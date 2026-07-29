# -*- coding: utf-8 -*-
"""Da ilhas proprias aos tres fios de ligacao da placa principal.

Fio soldado em cima da perna de outro componente parece conserto de erro. Aqui
cada ligacao ganha um par de ilhas dedicadas, com serigrafia dizendo de onde
para onde ela vai — vira parte do projeto, nao remendo.

Cada ilha e procurada perto da ponta que ela atende, num ponto onde as DUAS
faces estao livres (a ilha e passante) e onde cabe um coto reto ate o cobre
daquela rede. O fio voa de uma ilha a outra.

  "C:/Program Files/KiCad/10.0/bin/python.exe" ilhas_jumper.py
"""
import math, os, sys
import functools
print = functools.partial(print, flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
LIB = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/lib/"
       "tkmem128.pretty")
RAIO_ILHA = 0.8            # ilha de 1,6 mm
FOLGA = 0.20
LARG = 0.5                 # coto de ligacao
BUSCA = 9.0                # ate onde procurar um lugar livre

b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM

# Sem limpeza de execucao anterior: carregar duas BOARD no mesmo processo, ou
# remover e inserir no mesmo passe, derruba o SWIG. Se ja rodou, reverta a placa
# (git checkout) antes de rodar de novo.
if any(f.GetFPIDAsString().endswith("WirePad_1.6mm") for f in b.GetFootprints()):
    raise SystemExit("as ilhas de fio ja existem; reverta a placa antes")

# ---- geometria ocupada, por face -------------------------------------------
segs = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
discos = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}   # (x, y, raio)
furos = []                                     # (x, y, raio) - vale nas duas


def guarda_pad(p):
    pos = p.GetPosition()
    sz = p.GetSize()
    r = max(mm(sz.x), mm(sz.y)) / 2.0
    for ly in (pcbnew.F_Cu, pcbnew.B_Cu):
        if p.IsOnLayer(ly):
            discos[ly].append((mm(pos.x), mm(pos.y), r, p.GetNetCode()))
    if p.GetDrillSize().x > 0:
        furos.append((mm(pos.x), mm(pos.y), mm(p.GetDrillSize().x) / 2.0))


for fp in b.GetFootprints():
    for p in fp.Pads():
        guarda_pad(p)
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        pos = t.GetPosition()
        # via: GetWidth() SEM camada dispara assert no KiCad 10 (e derruba o
        # processo). O diametro tem que ser pedido para uma camada.
        r = mm(t.GetWidth(pcbnew.F_Cu)) / 2.0
        for ly in (pcbnew.F_Cu, pcbnew.B_Cu):
            discos[ly].append((mm(pos.x), mm(pos.y), r, t.GetNetCode()))
        furos.append((mm(pos.x), mm(pos.y), r * 0.5))
    else:
        s, e = t.GetStart(), t.GetEnd()
        if t.GetLayer() in segs:
            segs[t.GetLayer()].append((mm(s.x), mm(s.y), mm(e.x), mm(e.y),
                                       mm(t.GetWidth()) / 2.0, t.GetNetCode()))


def d_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx +
                                               (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def livre_ponto(x, y, code, camada):
    """A ilha SMD cabe em (x,y) daquela face, sem encostar em rede alheia?

    SMD e nao passante de proposito: junto do conector nao existe um milimetro
    livre nas duas faces ao mesmo tempo — sao 54 ilhas passantes a 2,54 mm. Numa
    face so, sobra espaco. O fio solda em cima da ilha, que e o que se quer.
    """
    if x < 2.0 or y < 2.0 or x > PRINC.BOARD_W - 2.0 or y > PRINC.BOARD_H - 2.0:
        return False
    for fx, fy, fr in furos:
        if math.hypot(x - fx, y - fy) < RAIO_ILHA + fr + FOLGA:
            return False
    for ly in (camada,):
        for cx, cy, cr, cn in discos[ly]:
            if cn == code:
                continue
            if math.hypot(x - cx, y - cy) < RAIO_ILHA + cr + FOLGA:
                return False
        for x1, y1, x2, y2, hw, cn in segs[ly]:
            if cn == code:
                continue
            if d_pt_seg(x, y, x1, y1, x2, y2) < RAIO_ILHA + hw + FOLGA:
                return False
    return True


def livre_coto(x1, y1, x2, y2, camada, code):
    """O coto reto de (x1,y1) a (x2,y2) passa sem encostar em rede alheia?"""
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.1))
    meia = LARG / 2.0
    for i in range(n + 1):
        t = i / float(n)
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        for cx, cy, cr, cn in discos[camada]:
            if cn != code and math.hypot(px - cx, py - cy) < meia + cr + FOLGA:
                return False
        for ax, ay, bx, by, hw, cn in segs[camada]:
            if cn != code and d_pt_seg(px, py, ax, ay, bx, by) < meia + hw + FOLGA:
                return False
    return True


def acha_ilha(ax, ay, code, camada):
    """Ponto livre mais proximo da ancora, com coto reto ate ela."""
    melhor = None
    r = 1.6
    while r <= BUSCA:
        passo = max(12, int(2 * math.pi * r / 0.3))
        for k in range(passo):
            a = 2 * math.pi * k / passo
            x, y = round(ax + r * math.cos(a), 2), round(ay + r * math.sin(a), 2)
            if livre_ponto(x, y, code, camada) and livre_coto(ax, ay, x, y, camada, code):
                d = math.hypot(x - ax, y - ay)
                if melhor is None or d < melhor[2]:
                    melhor = (x, y, d)
        if melhor:
            return melhor[:2]
        r += 0.4
    return None


# ---- as tres ligacoes -------------------------------------------------------
LIGACOES = [
    ("A4", ("J1", "24"), ("U3", "8")),
    ("A2", ("J1", "11"), ("U3", "10")),
    ("RESET_N", ("J1", "20"), ("U2", "1")),
]

pads = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        pads[(fp.GetReference(), p.GetNumber())] = p

# Os dois lados de uma ligacao tem que cair na MESMA face, senao o fio teria de
# contornar a placa. Procura uma face que sirva para as duas pontas.

for net, a, c in LIGACOES:
    code = b.GetNetcodeFromNetname(net)
    for camada in (pcbnew.F_Cu, pcbnew.B_Cu):
        r = []
        for ref in (a, c):
            pd = pads[ref]
            ax, ay = mm(pd.GetPosition().x), mm(pd.GetPosition().y)
            achou = acha_ilha(ax, ay, code, camada)
            r.append((ref, ax, ay, achou))
        ok = all(x[3] for x in r)
        print("%-8s %-5s %s" % (net, b.GetLayerName(camada),
              "  ".join("%s.%s->%s" % (x[0][0], x[0][1], x[3]) for x in r)),
              "OK" if ok else "")
