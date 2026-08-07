# -*- coding: utf-8 -*-
"""Fecha o contorno de J1 na serigrafia das duas faces.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/fecha_silk_conector.py

O corpo do conector tem 10 mm de fundo. Enquanto J1 estava 1,5 mm mais para
baixo ele terminava em y=67,23, ou seja 1,19 mm FORA da placa: o contorno da
PCB cortava o conector, e a serigrafia dele teve que virar um "U" aberto,
com as verticais paradas 0,3 mm antes da aresta. Depois de tools/sobe_j1.py o
corpo termina em 65,73, dentro da placa — o retangulo pode fechar.

De quebra, TODA linha estava em duplicata exata, das sucessivas reconstrucoes
da serigrafia — o script anterior redesenhava sem apagar.

A face de cima nao ter a linha de cima do retangulo, essa NAO era falha: ela
esbarra na serigrafia de C2, C5 e C6, que ficam logo acima. Descobri tentando
fechar o retangulo nas duas faces e colhendo 16 silk_overlap.

Confere antes de gravar que nenhuma linha nova passa por cima de ilha.
"""
import math
import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"
LARG = 0.15
FOLGA_ARESTA = 0.2        # serigrafia ate a aresta da placa


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


b = pcbnew.LoadBoard(PCB)
J1 = [f for f in b.Footprints() if f.GetReference() == "J1"][0]
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)

# ---- de onde sai a geometria: do proprio corpo, nao de constante -----------
# Os vertices vem das linhas do courtyard, nao do BBox delas: o BBox inclui
# metade da largura do traco e devolveria o retangulo 0,025 mm maior.
cantos = []
for g in J1.GraphicalItems():
    if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == pcbnew.B_CrtYd:
        for q in (g.GetStart(), g.GetEnd()):
            cantos.append((q.x / MM, q.y / MM))
if not cantos:
    raise SystemExit("J1 sem courtyard — nao da para deduzir o corpo")
x1, x2 = min(c[0] for c in cantos), max(c[0] for c in cantos)
y1, y2 = min(c[1] for c in cantos), max(c[1] for c in cantos)
xg = 63.50                # coluna da guia 5/52
borda = b.GetBoardEdgesBoundingBox().GetBottom() / MM - 0.05
print("corpo do conector: x %.2f..%.2f  y %.2f..%.2f" % (x1, x2, y1, y2))
print("aresta de baixo em %.2f -> sobra %.3f mm para a serigrafia"
      % (borda, borda - y2 - LARG / 2))
if borda - y2 - LARG / 2 < FOLGA_ARESTA:
    raise SystemExit("o retangulo nao cabe: falta folga ate a aresta")

# ---- apaga a serigrafia de contorno atual (inclusive as duplicatas) --------
velhas = [g for g in J1.GraphicalItems()
          if g.GetClass() == "PCB_SHAPE" and g.GetLayer() in SILK]
for g in velhas:
    J1.Remove(g)
print("linhas antigas removidas: %d" % len(velhas))

# ---- as ilhas, para conferir que nada novo pousa em cima -------------------
ilhas = [(q.GetPosition().x / MM, q.GetPosition().y / MM,
          max(q.GetSize(pcbnew.F_Cu).x, q.GetSize(pcbnew.F_Cu).y) / MM / 2)
         for q in J1.Pads()]


def d_pt_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


# A linha de CIMA so vai na face de baixo. Do lado dos componentes ela corre a
# 55,73, e ali em cima estao C2, C5 e C6 com a serigrafia deles — dava 16
# silk_overlap. Nao era esquecimento a face de cima nao ter essa linha; e por
# isso que ela nao tinha. O contorno fica em "U" invertido na face dos
# componentes (fechado embaixo, aberto em cima) e retangulo fechado no verso,
# que e onde o conector realmente encosta.
COMUNS = [(x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1),
          (xg, y1, xg, y2)]                        # laterais, base e guia
TOPO = (x1, y1, x2, y1)
POR_FACE = {pcbnew.F_SilkS: COMUNS, pcbnew.B_SilkS: COMUNS + [TOPO]}

for ax, ay, bx, by in COMUNS + [TOPO]:
    for cx, cyy, cr in ilhas:
        if d_pt_seg(cx, cyy, ax, ay, bx, by) < cr + LARG / 2:
            raise SystemExit("linha (%.2f,%.2f)-(%.2f,%.2f) pousa na ilha "
                             "(%.2f,%.2f)" % (ax, ay, bx, by, cx, cyy))

for lay in SILK:
    for ax, ay, bx, by in POR_FACE[lay]:
        g = pcbnew.PCB_SHAPE(J1)
        g.SetShape(pcbnew.SHAPE_T_SEGMENT)
        g.SetStart(p(ax, ay))
        g.SetEnd(p(bx, by))
        g.SetWidth(int(round(LARG * MM)))
        g.SetLayer(lay)
        J1.Add(g)
print("linhas novas: %d na face de cima, %d no verso"
      % (len(POR_FACE[pcbnew.F_SilkS]), len(POR_FACE[pcbnew.B_SilkS])))

b.Save(PCB)

# ---- reconfere lendo do disco ---------------------------------------------
b2 = pcbnew.LoadBoard(PCB)
J2 = [f for f in b2.Footprints() if f.GetReference() == "J1"][0]
vistas = {}
for g in J2.GraphicalItems():
    if g.GetClass() != "PCB_SHAPE" or g.GetLayer() not in SILK:
        continue
    s, e = g.GetStart(), g.GetEnd()
    k = (b2.GetLayerName(g.GetLayer()), round(s.x / MM, 3), round(s.y / MM, 3),
         round(e.x / MM, 3), round(e.y / MM, 3))
    vistas[k] = vistas.get(k, 0) + 1
print("\nconferencia no arquivo gravado:")
for k in sorted(vistas):
    print("   n=%d  %-14s (%7.3f,%7.3f)->(%7.3f,%7.3f)"
          % (vistas[k], k[0], k[1], k[2], k[3], k[4]))
if any(n > 1 for n in vistas.values()):
    raise SystemExit("ainda ha linha duplicada")
