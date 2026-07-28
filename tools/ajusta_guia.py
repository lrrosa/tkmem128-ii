# -*- coding: utf-8 -*-
"""Refaz o rasgo da guia da tira com a profundidade de KEYSLOT_DEPTH.

Edicao cirurgica: mexe so no Edge.Cuts, nao regera a placa.

O rasgo e o vao entre os dedos que encaixa na guia do conector do periferico
seguinte. Largura e posicao vem do proprio footprint de J2 (a coluna sem
contato), como em gen_pcb.py — assim o rasgo acompanha se o footprint girar.

  "C:/Program Files/KiCad/10.0/bin/python.exe" ajusta_guia.py [netlist_exp]
"""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1] if len(sys.argv) > 1
                                else "netlist_exp")
REAL = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
W, H = BOARD.BOARD_W, BOARD.BOARD_H
KW = 0.9
KD = getattr(BOARD, "KEYSLOT_DEPTH", 5.0)

b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM

# centro do rasgo: a coluna que falta entre as ilhas de J2
xs = sorted({round(mm(p.GetPosition().x), 2) for fp in b.GetFootprints()
             if fp.GetReference() == "J2" for p in fp.Pads()})
todos = [round(xs[0] + 2.54 * k, 2) for k in range(28)]
kx = [x for x in todos if x not in xs][0]

# Refaz o contorno inteiro em vez de tentar achar so os tracos do rasgo: filtrar
# por posicao deixou para tras o fundo do rasgo antigo (um traco solto no meio
# da placa, que nenhum DRC acusa e o fabricante corta). O contorno e uma coisa
# so — retangulo com um entalhe —, entao vale reconstruir.
antigos = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
formas = {d.GetShapeStr() for d in antigos}
if formas - {"Line"}:
    raise SystemExit("contorno tem %s alem de retas; refazer a mao" % formas)
for d in antigos:
    b.Remove(d)

for x1, y1, x2, y2 in [(0, 0, W, 0), (W, 0, W, H), (0, 0, 0, H),
                       (0, H, kx - KW, H),
                       (kx - KW, H, kx - KW, H - KD),
                       (kx - KW, H - KD, kx + KW, H - KD),
                       (kx + KW, H - KD, kx + KW, H),
                       (kx + KW, H, W, H)]:
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(fmm(x1), fmm(y1)))
    s.SetEnd(pcbnew.VECTOR2I(fmm(x2), fmm(y2)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(fmm(0.1))
    b.Add(s)

# o contorno mudou: os planos de terra precisam ser refeitos
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(REAL, b)

topo = min(mm(p.GetBoundingBox().GetTop()) for fp in b.GetFootprints()
           if fp.GetReference() == "J2" for p in fp.Pads())
print("rasgo: x de %.2f a %.2f, %.2f mm de profundidade (ate y=%.2f)"
      % (kx - KW, kx + KW, KD, H - KD))
print("dedos de J2 comecam em y=%.2f -> sobra %.2f mm de material"
      % (topo, H - KD - topo))
print("contorno refeito: %d tracos -> 8; zonas repreenchidas" % len(antigos))
print("gravado:", REAL)
