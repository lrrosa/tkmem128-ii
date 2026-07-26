# -*- coding: utf-8 -*-
"""Adiciona plano de GND nas duas faces, preenche e salva.

  python add_zones.py <modulo>
"""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1])
REAL = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
W, H = BOARD.BOARD_W, BOARD.BOARD_H
INSET = 0.3


def mm(v):
    return pcbnew.FromMM(float(v))


b = pcbnew.LoadBoard(REAL)

for z in list(b.Zones()):
    b.Remove(z)

# a area dos dedos de borda fica fora do plano
if BOARD.KEYSLOT_COL is None:
    y1, y2 = INSET, H - INSET
else:
    y1, y2 = INSET, H - 9.0

pts = [(INSET, y1), (W - INSET, y1), (W - INSET, y2), (INSET, y2)]
gnd = b.GetNetcodeFromNetname("GND")

for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNetCode(gnd)
    z.SetAssignedPriority(0)
    z.SetLocalClearance(mm(0.3))
    z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.4))
    z.SetThermalReliefSpokeWidth(mm(0.5))
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(x), mm(y))
    b.Add(z)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(REAL, b)
print("%s: %d zonas de GND preenchidas (y %.1f..%.1f)"
      % (BOARD.PROJ_NAME, len(list(b.Zones())), y1, y2))
