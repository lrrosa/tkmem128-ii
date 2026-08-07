# -*- coding: utf-8 -*-
"""Desfaz desvios que o Freerouting deixou e que nao eram necessarios.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/endireita_trilhas.py
  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/endireita_trilhas.py --grava

O Freerouting roteia e depois otimiza, mas o otimizador dele nao desfaz
escadinha: sobra caminho de uma iteracao anterior, de quando outra rede ainda
ocupava o espaco e foi rerroteada depois. O caso que motivou isto foi o
`ROMA14`, que subia por cima de uma ilha do R5, atravessava, e descia pelo vao
de 1,27 mm ENTRE as duas ilhas do R5 — com 0,22 mm de folga de cada lado — so
para voltar a mesma altura de onde tinha saido. Reto por baixo cabia, e com
mais folga (0,25).

COMO FUNCIONA. Cada rede vira cadeias de trechos entre nos fixos (ilha, via ou
bifurcacao). Dentro de uma cadeia, tenta-se trocar o pedaco entre dois vertices
por um caminho mais curto no estilo da placa: um trecho reto, ou dois trechos em
"L" com canto de 45 graus, nas duas orientacoes. Cada candidato e medido ponto a
ponto contra TODO o cobre daquela face que nao seja da mesma rede, mais a
margem da placa e a area de exclusao do furo. So entra se couber e se encurtar.

O que ele NAO faz: mudar de camada, mexer em via, ou reconsiderar a topologia.
E poda local, nao rerroteamento.
"""
import collections
import math
import sys

import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"
GRAVA = "--grava" in sys.argv

FOLGA = 0.20            # isolacao do projeto
FOLGA_BORDA = 0.30
W, H = 78.74, 66.04
FURO = (39.37, 4.02, 3.00)      # centro e raio da area de exclusao de H1
GANHO_MIN = 0.05                # chanfro de canto de 90 vale mesmo pequeno

b = pcbnew.LoadBoard(PCB)


def dseg(x1, y1, x2, y2, px, py):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


# ---- obstaculos por camada, indexados por rede -----------------------------
discos = collections.defaultdict(list)      # camada -> [(x,y,r,netcode)]
segs = collections.defaultdict(list)        # camada -> [(x1,y1,x2,y2,hw,netcode)]
for fp in b.Footprints():
    for q in fp.Pads():
        p = q.GetPosition()
        r = max(q.GetSize(pcbnew.F_Cu).x, q.GetSize(pcbnew.F_Cu).y) / MM / 2
        for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
            if q.IsOnLayer(lay):
                discos[lay].append((p.x / MM, p.y / MM, r, q.GetNetCode()))
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        r = t.GetWidth(pcbnew.F_Cu) / MM / 2
        for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
            discos[lay].append((p.x / MM, p.y / MM, r, t.GetNetCode()))
    else:
        s, e = t.GetStart(), t.GetEnd()
        segs[t.GetLayer()].append((s.x / MM, s.y / MM, e.x / MM, e.y / MM,
                                   t.GetWidth() / MM / 2, t.GetNetCode()))


def livre(x1, y1, x2, y2, lay, nc, larg):
    """O trecho cabe? Devolve None se sim, ou o motivo."""
    meia = larg / 2.0
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.02))
    for i in range(n + 1):
        t = i / float(n)
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        if not (FOLGA_BORDA + meia <= px <= W - FOLGA_BORDA - meia):
            return "fora da margem"
        if not (FOLGA_BORDA + meia <= py <= H - FOLGA_BORDA - meia):
            return "fora da margem"
        if math.hypot(px - FURO[0], py - FURO[1]) < FURO[2] + meia:
            return "area de exclusao do furo"
        for cx, cy, cr, cnc in discos[lay]:
            if cnc == nc:
                continue
            if math.hypot(px - cx, py - cy) < meia + cr + FOLGA:
                return "ilha em (%.2f,%.2f)" % (cx, cy)
        for ax, ay, bx, by, hw, cnc in segs[lay]:
            if cnc == nc:
                continue
            if dseg(ax, ay, bx, by, px, py) < meia + hw + FOLGA:
                return "trilha em (%.2f,%.2f)" % (ax, ay)
    return None


def candidatos(a, z):
    """Caminhos no estilo da placa entre dois pontos: reto, ou L com 45."""
    (x1, y1), (x2, y2) = a, z
    dx, dy = x2 - x1, y2 - y1
    saida = []
    if abs(dx) < 1e-6 or abs(dy) < 1e-6 or abs(abs(dx) - abs(dy)) < 1e-6:
        saida.append([a, z])
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    if abs(dx) > abs(dy):          # diagonal + reta horizontal, nas duas ordens
        saida.append([a, (x1 + sx * abs(dy), y2), z])
        saida.append([a, (x2 - sx * abs(dy), y1), z])
    elif abs(dy) > abs(dx):
        saida.append([a, (x2, y1 + sy * abs(dx)), z])
        saida.append([a, (x1, y2 - sy * abs(dx)), z])
    return saida


def comprimento(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
               for i in range(len(pts) - 1))


# ---- cadeias ---------------------------------------------------------------
fixos = set()
for fp in b.Footprints():
    for q in fp.Pads():
        fixos.add((round(q.GetPosition().x / MM, 3), round(q.GetPosition().y / MM, 3)))
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        fixos.add((round(t.GetPosition().x / MM, 3), round(t.GetPosition().y / MM, 3)))

por = collections.defaultdict(list)
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        continue
    s, e = t.GetStart(), t.GetEnd()
    por[(t.GetNetCode(), t.GetLayer())].append(
        ((round(s.x / MM, 3), round(s.y / MM, 3)),
         (round(e.x / MM, 3), round(e.y / MM, 3)), t.GetWidth(), t))

cadeias = []
for (nc, lay), lista in por.items():
    grau = collections.Counter()
    for a, z, _, _ in lista:
        grau[a] += 1
        grau[z] += 1
    adj = collections.defaultdict(list)
    for i, (a, z, w, t) in enumerate(lista):
        adj[a].append((z, i))
        adj[z].append((a, i))
    usados = set()
    for no in list(adj):
        if grau[no] == 2 and no not in fixos:
            continue
        for viz, i in adj[no]:
            if i in usados:
                continue
            pts = [no]
            atual, ii, prox = no, i, viz
            objs = []
            while True:
                usados.add(ii)
                objs.append(lista[ii][3])
                pts.append(prox)
                if grau[prox] != 2 or prox in fixos:
                    break
                seg = [(v, j) for v, j in adj[prox] if j != ii]
                if not seg:
                    break
                atual = prox
                prox, ii = seg[0]
            if len(pts) > 2:
                cadeias.append((nc, lay, pts, objs, lista[i][2],
                                b.GetNetInfo().GetNetItem(nc).GetNetname()))

print("%d cadeias com mais de um trecho\n" % len(cadeias))

trocas = []
for nc, lay, pts, objs, w, nome in cadeias:
    larg = w / MM
    atual = list(pts)
    ganho_total = 0.0
    melhorou = True
    while melhorou and len(atual) > 2:
        melhorou = False
        melhor = None
        for i in range(len(atual) - 2):
            for j in range(len(atual) - 1, i + 1, -1):
                trecho = comprimento(atual[i:j + 1])
                for cand in candidatos(atual[i], atual[j]):
                    novo = comprimento(cand)
                    if trecho - novo < GANHO_MIN:
                        continue
                    ruim = None
                    for k in range(len(cand) - 1):
                        ruim = livre(cand[k][0], cand[k][1], cand[k + 1][0],
                                     cand[k + 1][1], lay, nc, larg)
                        if ruim:
                            break
                    if ruim:
                        continue
                    if melhor is None or trecho - novo > melhor[0]:
                        melhor = (trecho - novo, i, j, cand)
        if melhor:
            g, i, j, cand = melhor
            atual = atual[:i] + cand + atual[j + 1:]
            ganho_total += g
            melhorou = True
    if ganho_total >= GANHO_MIN:
        trocas.append((ganho_total, nome, b.GetLayerName(lay), pts, atual, objs,
                       nc, lay, w))

print("cadeias que dava para encurtar sem sair da face nem mudar as pontas:\n")
if not trocas:
    print("   nenhuma")
for g, nome, lay, velho, novo, objs, nc, lc, w in sorted(trocas, reverse=True):
    print("  -%5.2f mm  %-9s %-5s  %d trechos -> %d   (%.2f,%.2f)->(%.2f,%.2f)"
          % (g, nome, lay, len(velho) - 1, len(novo) - 1,
             velho[0][0], velho[0][1], velho[-1][0], velho[-1][1]))
print("\ntotal: %d cadeias, %.2f mm" % (len(trocas), sum(t[0] for t in trocas)))

if "--detalhe" in sys.argv:
    print()
    for g, nome, lay, velho, novo, objs, nc, lc, w in sorted(trocas, reverse=True):
        print("=== %s em %s  (-%.2f mm)" % (nome, lay, g))
        print("   antes: " + " ".join("(%.2f,%.2f)" % v for v in velho))
        print("   agora: " + " ".join("(%.2f,%.2f)" % v for v in novo))

if not GRAVA:
    print("\n(simulacao; rode com --grava para aplicar)")
    raise SystemExit(0)

for g, nome, lay, velho, novo, objs, nc, lc, w in trocas:
    for t in objs:
        b.Remove(t)
    for k in range(len(novo) - 1):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(int(round(novo[k][0] * MM)),
                                   int(round(novo[k][1] * MM))))
        t.SetEnd(pcbnew.VECTOR2I(int(round(novo[k + 1][0] * MM)),
                                 int(round(novo[k + 1][1] * MM))))
        t.SetWidth(w)
        t.SetLayer(lc)
        t.SetNetCode(nc)
        b.Add(t)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("\ngravado. rodar o DRC: as trocas foram conferidas uma a uma, mas o DRC"
      " e quem tem a ultima palavra.")
