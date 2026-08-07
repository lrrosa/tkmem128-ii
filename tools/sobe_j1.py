# -*- coding: utf-8 -*-
"""Sobe J1 1,5 mm e abre o furo de fixacao da torre superior.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/sobe_j1.py

POR QUE SUBIR J1. A fileira de baixo estava a 1,385 mm da aresta — 0,635 mm de
cobre ate a borda, e o furo de 1,02 a 0,875 mm dela. Passa na regra (0,3), mas
e uma tira fina de FR4 justo onde a interface e alavancada ao plugar e onde a
tira de expansao esta soldada nos terminais do outro lado. Pior: o corpo do
conector tem 10 mm de fundo e sobrava 1,19 mm PARA FORA da placa — o contorno
cortava o conector ao meio, e foi por isso que a serigrafia dele virou um "U"
aberto. Subindo 1,5 mm (a medida que o Leonardo conferiu nas interfaces reais
que tem) o cobre fica a 2,135 mm da borda e o corpo termina 0,31 mm DENTRO da
placa.

POR QUE ISTO OBRIGA A REROTEAR. Das 33 pontas de trilha que pousam em ilhas de
J1, 26 saem a 45 graus costurando entre as proprias ilhas. Subir a fileira joga
as ilhas para dentro do leque que elas alimentam. Nao da para remendar as
pontas: o leque tem que ser refeito. Por isso este script tambem apaga o
roteamento — rodar mk_decoy/freerouting/import_ses depois dele.

O FURO. Torre superior da caixa Patola em (39,37 ; 4,02), conferida contra a
peca real em impressao 1:1. Ø2,7 e o teto pratico: acima disso o furo invade o
courtyard do soquete de U4, que termina em x=37,95. O cobre nao e o limite —
sobra 0,72 mm ate a ilha U4.15.

A area de exclusao de 1,85 mm de raio existe por causa das camadas internas:
com furo passante nao metalizado os planos so recuariam os 0,25 mm da regra, e
parafuso metalico raspando a parede de uma placa de 4 camadas pode arrastar
cobre e encostar +5V em GND. 1,85 = 1,35 do furo + 0,5 de recuo. Ela tambem e
o que o Freerouting enxerga: sem ela, o autorotedor passaria trilha por cima do
furo.
"""
import math
import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"
LIBDIR = "hardware/lib/tkmem128.pretty"
DY = -1.50                      # sobe (y cresce para baixo)
FURO_D, FURO_X, FURO_Y = 2.7, 39.37, 4.02
RAIO_LIVRE = 1.85               # 1,35 do furo + 0,5 de recuo dos planos


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


b = pcbnew.LoadBoard(PCB)

# ------------------------------------------------------------------ 1. J1
J1 = [f for f in b.Footprints() if f.GetReference() == "J1"][0]
antes = J1.GetPosition().y / MM
J1.Move(pcbnew.VECTOR2I(0, int(round(DY * MM))))
fileiras = sorted({round(q.GetPosition().y / MM, 3) for q in J1.Pads()})
print("J1: y %.2f -> %.2f   fileiras em %s" % (antes, J1.GetPosition().y / MM,
                                               ", ".join("%.3f" % y for y in fileiras)))
borda = b.GetBoardEdgesBoundingBox().GetBottom() / MM - 0.05
print("    fileira de baixo a %.3f mm da aresta (cobre a %.3f)"
      % (borda - fileiras[-1], borda - fileiras[-1] - 0.75))

# ------------------------------------------------------------ 2. o furo
# O furo vem da biblioteca DO PROJETO, nao montado a mao aqui, por dois
# motivos. Um: footprint sem FPID sai do exportador Specctra como
# (component "") e o KiCad se recusa a reimportar o .ses do Freerouting.
# Dois: montado a mao ele nunca fica identico a nenhuma biblioteca, e o DRC
# acusa lib_footprint_mismatch para sempre. Vindo de la, placa e biblioteca
# sao o mesmo objeto por construcao. Ver gen_mountinghole() em
# tools/gen_footprints.py para por que este footprint nao tem courtyard.
fp = pcbnew.FootprintLoad(LIBDIR, "MountingHole_2.7mm")
fp.SetFPID(pcbnew.LIB_ID("tkmem128", "MountingHole_2.7mm"))
fp.SetReference("H1")
fp.SetPosition(p(FURO_X, FURO_Y))
b.Add(fp)

# area de exclusao em TODAS as camadas de cobre (octogono; o Freerouting le
# isto como keepout no DSN)
ko = pcbnew.ZONE(b)
ko.SetIsRuleArea(True)
ko.SetDoNotAllowTracks(True)
ko.SetDoNotAllowVias(True)
ko.SetDoNotAllowZoneFills(True)
ko.SetDoNotAllowPads(False)
ko.SetDoNotAllowFootprints(False)
camadas = pcbnew.LSET()
for lay in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
    camadas.addLayer(lay)
ko.SetLayerSet(camadas)
pts = pcbnew.SHAPE_LINE_CHAIN()
for i in range(8):
    a = math.pi * (2 * i + 1) / 8.0
    r = RAIO_LIVRE / math.cos(math.pi / 8.0)          # circunscrito
    pts.Append(p(FURO_X + r * math.cos(a), FURO_Y + r * math.sin(a)))
pts.SetClosed(True)
poly = pcbnew.SHAPE_POLY_SET()
poly.AddOutline(pts)
ko.SetOutline(poly)
b.Add(ko)
print("furo Ø%.1f em (%.2f ; %.2f) + exclusao de raio %.2f nas 4 camadas"
      % (FURO_D, FURO_X, FURO_Y, RAIO_LIVRE))

# --------------------------------------------------- 3. apaga o roteamento
trilhas = list(b.GetTracks())
vias = sum(1 for t in trilhas if t.GetClass() == "PCB_VIA")
for t in trilhas:
    b.Remove(t)
print("roteamento apagado: %d trechos (%d vias)" % (len(trilhas) - vias, vias))

# planos: ficam, o DSN precisa deles para saber que +5V e GND ja estao ligados
zonas = [z for z in b.Zones() if not z.GetIsRuleArea()]
print("zonas mantidas: %s" % ", ".join(
    "%s/%s" % (b.GetLayerName(z.GetLayer()), z.GetNetname()) for z in zonas))

b.Save(PCB)
print("\nsalvo. agora: mk_decoy -> freerouting -> import_ses -> limpa_cotocos")
