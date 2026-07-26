# -*- coding: utf-8 -*-
"""Placa-isca + export do DSN para o Freerouting.

  "C:/Program Files/KiCad/10.0/bin/python.exe" mk_decoy.py <modulo> <subdir>

Recua o contorno 0,35mm; na placa que tem dedos de borda a aresta inferior
fica no lugar, senao os dedos ficariam fora do contorno.
"""
import importlib, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1])
WORK = "C:/Users/Leonardo/AppData/Local/Temp/fr_work/" + sys.argv[2]
INSET = 0.35
W, H = BOARD.BOARD_W, BOARD.BOARD_H
SRC = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
PRO = "%s/%s.kicad_pro" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)

if not os.path.isdir(WORK):
    os.makedirs(WORK)
shutil.copy(SRC, WORK + "/route.kicad_pcb")
shutil.copy(PRO, WORK + "/route.kicad_pro")

b = pcbnew.LoadBoard(WORK + "/route.kicad_pcb")
for z in list(b.Zones()):
    b.Remove(z)

tol = pcbnew.FromMM(0.01)
has_fingers = BOARD.KEYSLOT_COL is not None


def adj(x, y):
    if abs(x) < tol:
        x = pcbnew.FromMM(INSET)
    elif abs(x - pcbnew.FromMM(W)) < tol:
        x = pcbnew.FromMM(W - INSET)
    if abs(y) < tol:
        y = pcbnew.FromMM(INSET)
    elif abs(y - pcbnew.FromMM(H)) < tol and not has_fingers:
        y = pcbnew.FromMM(H - INSET)
    return x, y


for d in b.GetDrawings():
    if d.GetLayer() != pcbnew.Edge_Cuts:
        continue
    for get, set_ in ((d.GetStart, d.SetStart), (d.GetEnd, d.SetEnd)):
        p = get()
        x, y = adj(p.x, p.y)
        set_(pcbnew.VECTOR2I(x, y))

pcbnew.SaveBoard(WORK + "/route.kicad_pcb", b)
b2 = pcbnew.LoadBoard(WORK + "/route.kicad_pcb")
ok = pcbnew.ExportSpecctraDSN(b2, WORK + "/route.dsn")
print("%s: camadas=%d  DSN=%s  %d bytes" % (
    sys.argv[2], b2.GetCopperLayerCount(), ok,
    os.path.getsize(WORK + "/route.dsn")))
