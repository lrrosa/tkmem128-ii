# -*- coding: utf-8 -*-
"""Importa o .ses na placa real.

  python import_ses.py <modulo> <subdir>
"""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1])
SES = "C:/Users/Leonardo/AppData/Local/Temp/fr_work/%s/route.ses" % sys.argv[2]
REAL = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)

b = pcbnew.LoadBoard(REAL)
ok = pcbnew.ImportSpecctraSES(b, SES)
if not ok:
    raise SystemExit("ImportSpecctraSES falhou")
pcbnew.SaveBoard(REAL, b)

b2 = pcbnew.LoadBoard(REAL)
tracks = len([t for t in b2.GetTracks()])
print("%s: SES importado, %d segmentos/vias" % (sys.argv[2], tracks))
