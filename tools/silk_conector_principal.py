# -*- coding: utf-8 -*-
"""Leva a numeracao do conector da placa principal para o lado dos componentes.

Edicao cirurgica (padrao troca_j1.py): nao regera a placa.

J1 fica em B.Cu — e o unico componente do lado do cobre. Toda a serigrafia dele
estava so em B.Silkscreen, o lado onde o conector e soldado. Mas o lado dos
componentes e onde a TIRA DE EXPANSAO e soldada, nos terminais que atravessam a
placa: quem monta precisa da numeracao la tambem. O conector e THT, entao cada
pino existe nas duas faces, na mesma coluna — os mesmos rotulos, nas mesmas
coordenadas, valem para as duas.

De quebra, o contorno do corpo do conector descia ate y=67,23 numa placa de
66,04 mm: 1,19 mm de serigrafia fora da placa, mais dois tracos verticais
atravessando a aresta (3 avisos de silk_edge_clearance). Vira um U aberto para
a aresta, parando 0,3 mm antes — o mesmo tratamento que a tira levou.

  "C:/Program Files/KiCad/10.0/bin/python.exe" silk_conector_principal.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
FOLGA = 0.3                      # da aresta da placa
b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM
fp = [f for f in b.GetFootprints() if f.GetReference() == "J1"][0]
Y_LIM = PRINC.BOARD_H - FOLGA

# ---- fotografa a serigrafia atual antes de mexer na colecao ----------------
textos, tracos = [], []
for it in fp.GraphicalItems():
    camada = it.GetLayer()
    if camada not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
        continue
    if it.GetClass() == "PCB_TEXT":
        p = it.GetPosition()
        textos.append((it.GetText(), mm(p.x), mm(p.y), mm(it.GetTextWidth()),
                       mm(it.GetTextThickness())))
    elif it.GetClass() == "PCB_SHAPE":
        s, e = it.GetStart(), it.GetEnd()
        tracos.append((mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(it.GetWidth())))

velhos = [it for it in fp.GraphicalItems()
          if it.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
for it in velhos:
    fp.Remove(it)

# ---- contorno: recorta o que passa da aresta -------------------------------
# o traco totalmente fora da placa some; o que atravessa a aresta e encurtado.
# Sobra um U aberto para a aresta, que e onde o conector realmente esta.
recortados = []
for x1, y1, x2, y2, larg in tracos:
    if min(y1, y2) > Y_LIM:
        continue                                   # inteiro fora da placa
    recortados.append((x1, min(y1, Y_LIM), x2, min(y2, Y_LIM), larg))

# ---- reescreve nas duas faces ----------------------------------------------
for camada in (pcbnew.B_SilkS, pcbnew.F_SilkS):
    for x1, y1, x2, y2, larg in recortados:
        c = pcbnew.PCB_SHAPE(fp)
        c.SetShape(pcbnew.SHAPE_T_SEGMENT)
        c.SetStart(pcbnew.VECTOR2I(fmm(x1), fmm(y1)))
        c.SetEnd(pcbnew.VECTOR2I(fmm(x2), fmm(y2)))
        c.SetWidth(fmm(larg))
        c.SetLayer(camada)
        fp.Add(c)
    for s, x, y, tam, esp in textos:
        t = pcbnew.PCB_TEXT(fp)
        t.SetText(s)
        t.SetPosition(pcbnew.VECTOR2I(fmm(x), fmm(y)))
        t.SetLayer(camada)
        t.SetTextSize(pcbnew.VECTOR2I(fmm(tam), fmm(tam)))
        t.SetTextThickness(fmm(esp))
        t.SetMirrored(camada == pcbnew.B_SilkS)
        fp.Add(t)

pcbnew.SaveBoard(REAL, b)
print("J1: %d rotulos e %d tracos em cada face" % (len(textos),
                                                   len(recortados)))
print("   descartados %d tracos fora da placa (y > %.2f)"
      % (len(tracos) - len(recortados), Y_LIM))
print("   rotulos:", ", ".join('%s(%.2f,%.2f)' % (t[0], t[1], t[2])
                               for t in textos))
print("gravado:", REAL)
