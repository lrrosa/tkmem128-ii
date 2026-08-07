# -*- coding: utf-8 -*-
"""Fecha a rede A14 a mao, pela margem direita da placa.

O Freerouting deixa essa uma em aberto e o roteador de labirinto produziu um
caminho de 136 segmentos que nem conectava. Ela e simples de fazer a mao:

  J1 pino 1  (73,66; 64,66)  fileira de BAIXO do conector, coluna 1
  U1 pino 14 (73,70; 28,20)  fileira de cima do GAL

Subir reto nao da: em x=73,66 a fileira de cima do conector tem o pino 56. E
chegar em U1.14 pela direita cruzaria os pinos vizinhos da mesma fileira. O
caminho e sair para a margem, subir por ela e entrar em U1.14 POR CIMA:

  direita ao longo da aresta de baixo -> sobe pela margem -> esquerda acima de U1
  -> desce direto na ilha do pino 14

Cada trecho e conferido contra todo o cobre da face antes de ser criado; se algum
nao couber, o script para sem gravar.

  "C:/Program Files/KiCad/10.0/bin/python.exe" fecha_a14.py
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
NET = "A14"
LARG, FOLGA = 0.5, 0.20
CAMADA = pcbnew.F_Cu

b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM
code = b.GetNetcodeFromNetname(NET)

# ---- apaga o que o labirinto deixou nesta rede ------------------------------
lixo = [t for t in b.GetTracks() if t.GetNetCode() == code]
for t in lixo:
    b.Remove(t)
print("removidos %d tracos da tentativa anterior" % len(lixo))
pcbnew.SaveBoard(REAL, b)

# ---- recarrega e monta o mapa de cobre da face ------------------------------
b = pcbnew.LoadBoard(REAL)
code = b.GetNetcodeFromNetname(NET)
discos, segs = [], []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if not p.IsOnLayer(CAMADA) or p.GetNetCode() == code:
            continue
        pos, sz = p.GetPosition(), p.GetSize()
        discos.append((mm(pos.x), mm(pos.y),
                       max(mm(sz.x), mm(sz.y)) / 2.0))
for t in b.GetTracks():
    if t.GetNetCode() == code:
        continue
    if t.GetClass() == "PCB_VIA":
        pos = t.GetPosition()
        discos.append((mm(pos.x), mm(pos.y), mm(t.GetWidth(CAMADA)) / 2.0))
    elif t.GetLayer() == CAMADA:
        s, e = t.GetStart(), t.GetEnd()
        segs.append((mm(s.x), mm(s.y), mm(e.x), mm(e.y),
                     mm(t.GetWidth()) / 2.0))


def d_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx +
                                               (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def livre(x1, y1, x2, y2):
    meia = LARG / 2.0
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05))
    for i in range(n + 1):
        t = i / float(n)
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        if not (0.3 + meia <= px <= PRINC.BOARD_W - 0.3 - meia):
            return "fora da margem em x=%.2f" % px
        for cx, cy, cr in discos:
            if math.hypot(px - cx, py - cy) < meia + cr + FOLGA:
                return "ilha em (%.2f, %.2f)" % (cx, cy)
        for ax, ay, bx, by, hw in segs:
            if d_pt_seg(px, py, ax, ay, bx, by) < meia + hw + FOLGA:
                return "trilha em (%.2f,%.2f)-(%.2f,%.2f)" % (ax, ay, bx, by)
    return None


# As duas pontas saem da placa, nao de constante: J1 ja subiu 1,5 mm uma vez
# (tools/sobe_j1.py) e o caminho tem que acompanhar sozinho da proxima.
pontas = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode() == code:
            pontas[fp.GetReference()] = (mm(p.GetPosition().x), mm(p.GetPosition().y))
(XJ, YJ), (XU, YU) = pontas["J1"], pontas["U1"]

X_MARGEM, Y_ACIMA = 78.04, 24.00
CAMINHO = [(XJ, YJ), (X_MARGEM, YJ), (X_MARGEM, Y_ACIMA),
           (XU, Y_ACIMA), (XU, YU)]

for i in range(len(CAMINHO) - 1):
    (x1, y1), (x2, y2) = CAMINHO[i], CAMINHO[i + 1]
    erro = livre(x1, y1, x2, y2)
    print("  trecho %d (%.2f,%.2f)->(%.2f,%.2f): %s"
          % (i + 1, x1, y1, x2, y2, erro or "livre"))
    if erro:
        raise SystemExit("nao gravei nada")

for i in range(len(CAMINHO) - 1):
    (x1, y1), (x2, y2) = CAMINHO[i], CAMINHO[i + 1]
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(fmm(x1), fmm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(fmm(x2), fmm(y2)))
    t.SetWidth(fmm(LARG))
    t.SetLayer(CAMADA)
    t.SetNetCode(code)
    b.Add(t)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(REAL, b)
total = sum(math.hypot(CAMINHO[i+1][0]-CAMINHO[i][0], CAMINHO[i+1][1]-CAMINHO[i][1])
            for i in range(len(CAMINHO)-1))
print("A14 fechada em %d trechos, %.1f mm, sem via" % (len(CAMINHO) - 1, total))
