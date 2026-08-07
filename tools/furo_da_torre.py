# -*- coding: utf-8 -*-
"""Abre o furo para a TORRE da caixa passar, e recua U4 para caber.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/furo_da_torre.py

O QUE ESTAVA ERRADO. `H1` nasceu Ø2,7, dimensionado como furo de PARAFUSO. Mas
a torre da Patola PB 085/3 tem **Ø5 externo** (o Ø2,5 do desenho e o furo-piloto
dentro dela), e a placa assenta no fundo da tampa, de onde a torre nasce. Com
Ø2,7 a placa nao desce: ela para em cima da torre.

O furo tem que deixar a TORRE passar, nao o parafuso. Ø5,4 da 0,2 mm de folga
radial — a conicidade de desmoldagem pede isso, porque a base da torre e mais
larga que o topo, e e a base que encontra a placa.

O QUE ISSO MELHORA. O parafuso da caixa passa a correr dentro da torre e nunca
toca a placa. Somem as duas ressalvas do furo pequeno: folga para a cabeca do
parafuso, e parafuso metalico raspando a parede e encostando o plano de GND no
de +5V. O furo virou pino de localizacao.

O QUE ISSO CUSTA. U4 tem que recuar 1,5 mm para a esquerda, senao o furo entra
no courtyard do soquete dele — e recuar U4 obriga a rerotear. Depois do recuo
sobram 0,60 mm entre o cobre de U4 e a aresta esquerda (regra: 0,30).

E o canal acima do furo praticamente fecha: entre a aresta de cima e a area de
exclusao sobra uma janela de 0,22 mm para o centro de uma trilha de 0,5, contra
1,37 mm quando o furo era Ø2,7. Quem passava por ali tem que dar a volta.
"""
import math
import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"
LIBDIR = "hardware/lib/tkmem128.pretty"
FURO_D, FURO_X, FURO_Y = 5.4, 39.37, 4.02
RECUO_PLANO = 0.30              # GND e +5V longe da parede do furo
RAIO_LIVRE = FURO_D / 2 + RECUO_PLANO
DX_U4 = -1.50                   # U4 para a esquerda


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


b = pcbnew.LoadBoard(PCB)

# ------------------------------------------------------------------ 1. U4
U4 = [f for f in b.Footprints() if f.GetReference() == "U4"][0]
U4.Move(pcbnew.VECTOR2I(int(round(DX_U4 * MM)), 0))
cy = U4.GetCourtyard(pcbnew.F_CrtYd).BBox()
xs = []
for q in U4.Pads():
    sz = q.GetSize(pcbnew.F_Cu)
    xs += [(q.GetPosition().x - sz.x / 2) / MM, (q.GetPosition().x + sz.x / 2) / MM]
print("U4 recuou %.2f mm: courtyard x %.2f..%.2f, cobre x %.2f..%.2f"
      % (-DX_U4, cy.GetLeft() / MM, cy.GetRight() / MM, min(xs), max(xs)))
folgas = [("cobre de U4 ate a aresta esquerda", min(xs), 0.30),
          ("courtyard de U4 ate o furo", FURO_X - cy.GetRight() / MM, FURO_D / 2),
          ("cobre de U4 ate a exclusao", FURO_X - max(xs), RAIO_LIVRE)]
for nome, tem, precisa in folgas:
    print("   %-36s %5.2f >= %4.2f  %s" % (nome, tem, precisa,
                                           "OK" if tem >= precisa else "NAO CABE"))
if any(t < r for _, t, r in folgas):
    raise SystemExit("nao gravei nada")

# ------------------------------------------- 2. furo novo no lugar do antigo
velho = [f for f in b.Footprints() if f.GetReference() == "H1"]
for f in velho:
    print("furo antigo removido: %s" % f.GetValue())
    b.Remove(f)
for z in list(b.Zones()):
    if z.GetIsRuleArea():
        b.Remove(z)
        print("area de exclusao antiga removida")

fp = pcbnew.FootprintLoad(LIBDIR, "MountingHole_%.1fmm" % FURO_D)
fp.SetFPID(pcbnew.LIB_ID("tkmem128", "MountingHole_%.1fmm" % FURO_D))
fp.SetReference("H1")
fp.SetPosition(p(FURO_X, FURO_Y))
b.Add(fp)

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
r = RAIO_LIVRE / math.cos(math.pi / 8.0)            # octogono circunscrito
for i in range(8):
    a = math.pi * (2 * i + 1) / 8.0
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

b.Save(PCB)
print("\nsalvo. agora: mk_decoy -> freerouting -> import_ses -> limpa_cotocos"
      " -> repreencher zonas -> fecha_a14")
