# -*- coding: utf-8 -*-
"""Recoloca a referencia de U4, aproxima o nome dele, e afasta C6 de J1.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/ajusta_u4_c6.py

REFERENCIA DE U4. Nas outras tres a referencia fica a ~0,7 mm da aresta
ESQUERDA do courtyard (U1 em 45,97 para courtyard em 46,67, e assim por
diante). Quando U4 recuou 1,5 mm para abrir o furo da torre, a dele foi junto e
caiu em x = -0,57: fora da placa, portanto fora do gerber, sem que nada
acusasse — DRC nao reclama de serigrafia que nao existe. A esquerda nao ha mais
espaco (o courtyard comeca em 0,17), entao ela passa para a direita, junto do
nome do componente.

NOME DO COMPONENTE. `27C256` estava a 3,05 mm do courtyard de U4, distancia
herdada de antes do recuo. Volta para ~0,7 mm, a mesma folga que as outras
referencias usam.

C6 x J1. O corpo de C6 (Ø5,10 no F.Fab) terminava em y=57,55, e a fileira de
cima de J1 esta em y=58,305 — terminal quadrado de ~0,64, ou seja borda em
57,99. Sobravam **0,44 mm**. Nao e problema eletrico (cobre a cobre sao 1,81
mm), e sim de bancada: esses terminais atravessam a placa e sobram 3,18 mm DO
LADO DOS COMPONENTES, que e onde a tira de expansao e soldada dos dois lados.
Soldar aquela fileira com uma lata de 5 mm a meio milimetro e ruim.

Subindo C6 0,70 mm a folga vai a 1,13 mm embaixo, e em cima sobra 1,11 mm ate o
corpo do soquete de U2 (F.Fab em 50,64). Fica equilibrado.

Por que subir so 0,70 e nao 0,80: a ilha 2 de C6 passa raspando numa diagonal
de `D3` a 45 graus, e subir aperta essa folga em 1/raiz(2) por milimetro. Com
0,80 dava 0,195 contra os 0,200 da regra — cinco microns. O laco de conferencia
no fim deste script mede isso antes de gravar.

E POR QUE TAMBEM 0,80 PARA A ESQUERDA. Mesmo depois de subir, a ilha 2 ficava a
0,234 mm de uma vertical de `D5` na face de trás — dentro da regra, mas e a
menor folga da placa inteira. Andar na horizontal ataca isso de frente, 1 mm
por milimetro, em vez de 1/raiz(2). Varrendo -0,1 a -2,5:

    -0,10  0,334   (sai de cima do D5)
    -0,80  0,806   <- maximo
    -1,50  0,302
    -1,80  0,002   (a ilha 1 encosta no D7, que vem pelo outro lado)

Ou seja, existe um otimo e ele nao esta na ponta: passar de 0,80 comeca a
piorar. A folga da pior trilha vai de 0,234 para 0,806 mm, 3,4 vezes.

Mover C6 NAO obriga a rerotear: as duas ilhas dele sao +5V e GND, e nesta placa
alimentacao nao usa trilha nenhuma — cada ilha toca o plano interno direto. So
e preciso repreencher as zonas, conferir as trilhas vizinhas e rodar o DRC.
"""
import math

import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"

C6_NOVO = (67.20, 54.30)
X_TEXTO = 37.70                 # coluna a direita de U4, ~0,7 mm do courtyard
Y_NOME, Y_REF = 12.50, 17.70   # 1,2 mm de vao: com 16,60 sobrava 0,13 e as
                               # duas linhas liam como uma so, 'U4 27C256'


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


b = pcbnew.LoadBoard(PCB)

# ---- referencia de U4 ------------------------------------------------------
U4 = [f for f in b.Footprints() if f.GetReference() == "U4"][0]
cy = U4.GetCourtyard(pcbnew.F_CrtYd).BBox()
ref = U4.Reference()
antes = (ref.GetPosition().x / MM, ref.GetPosition().y / MM)
ref.SetPosition(p(X_TEXTO, Y_REF))
ref.SetVisible(True)
ref.SetLayer(pcbnew.F_SilkS)
print("U4: courtyard x %.2f..%.2f" % (cy.GetLeft() / MM, cy.GetRight() / MM))
print("    referencia (%.2f,%.2f) -> (%.2f,%.2f)"
      % (antes[0], antes[1], X_TEXTO, Y_REF))
if antes[0] >= 0:
    print("    (atencao: a antiga ja estava dentro da placa)")

# ---- nome do componente ----------------------------------------------------
nome = [d for d in b.GetDrawings()
        if d.GetClass() == "PCB_TEXT" and d.GetText() == "27C256"]
if len(nome) != 1:
    raise SystemExit("achei %d textos '27C256'" % len(nome))
antes = nome[0].GetPosition().x / MM
nome[0].SetPosition(p(X_TEXTO, Y_NOME))
print("    nome '27C256' x %.2f -> %.2f  (%.2f mm do courtyard)"
      % (antes, X_TEXTO, X_TEXTO - cy.GetRight() / MM))

# ---- C6 --------------------------------------------------------------------
C6 = [f for f in b.Footprints() if f.GetReference() == "C6"][0]
dx = C6_NOVO[0] - C6.GetPosition().x / MM
dy = C6_NOVO[1] - C6.GetPosition().y / MM
C6.Move(pcbnew.VECTOR2I(int(round(dx * MM)), int(round(dy * MM))))

corpo = None
for g in C6.GraphicalItems():
    if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == pcbnew.F_Fab \
            and g.GetShapeStr() == "Circle":
        corpo = g.GetBoundingBox()
U2 = [f for f in b.Footprints() if f.GetReference() == "U2"][0]
u2_fab = max(g.GetBoundingBox().GetBottom() / MM for g in U2.GraphicalItems()
             if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == pcbnew.F_Fab)
J1 = [f for f in b.Footprints() if f.GetReference() == "J1"][0]
fileira = min(q.GetPosition().y / MM for q in J1.Pads())
terminal = fileira - 0.32          # meio terminal quadrado de 0,64

print("\nC6 subiu %.2f mm, corpo agora em y %.2f..%.2f"
      % (-dy, corpo.GetTop() / MM, corpo.GetBottom() / MM))
print("   ate o corpo do soquete de U2 (%.2f): %.2f mm"
      % (u2_fab, corpo.GetTop() / MM - u2_fab))
print("   ate o terminal de J1 (%.2f):        %.2f mm"
      % (terminal, terminal - corpo.GetBottom() / MM))
if corpo.GetTop() / MM - u2_fab < 0.5 or terminal - corpo.GetBottom() / MM < 0.5:
    raise SystemExit("folga insuficiente — nao gravei")

# ---- as trilhas vizinhas aguentaram? ---------------------------------------
# Subir C6 nao mexe em trilha nenhuma, mas aproxima as ilhas dele das trilhas
# que ja passavam ali — e uma diagonal a 45 graus se aproxima 1/raiz(2) por
# milimetro de subida. Foi assim que 0,80 mm de subida perdeu por 5 microns.
FOLGA = 0.20


def dist_seg(x1, y1, x2, y2, px, py):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx +
                                               (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


apertadas = []
for q in C6.Pads():
    px, py = q.GetPosition().x / MM, q.GetPosition().y / MM
    r = max(q.GetSize(pcbnew.F_Cu).x, q.GetSize(pcbnew.F_Cu).y) / MM / 2
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA" or t.GetNetCode() == q.GetNetCode():
            continue
        s_, e_ = t.GetStart(), t.GetEnd()
        d = dist_seg(s_.x / MM, s_.y / MM, e_.x / MM, e_.y / MM,
                     px, py) - r - t.GetWidth() / MM / 2
        if d < FOLGA:
            apertadas.append("ilha %s x %s em %s: %.3f mm"
                             % (q.GetPadName(), t.GetNetname(),
                                b.GetLayerName(t.GetLayer()), d))
if apertadas:
    for x in apertadas:
        print("  APERTOU: %s" % x)
    raise SystemExit("nao gravei nada")

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("\ngravado; trilhas vizinhas de C6 conferidas.")
