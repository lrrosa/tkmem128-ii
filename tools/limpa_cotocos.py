# -*- coding: utf-8 -*-
"""Remove cotocos de trilha (fragmentos minusculos) deixados pela importacao.

O Freerouting as vezes gera segmentos de decimos de milimetro que, ao serem
importados, viram ilhas soltas e o DRC do KiCad reclama de ligacao faltando.
Sao eletricamente irrelevantes.

  python limpa_cotocos.py <modulo>
"""
import importlib, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1])
REAL = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
LIMITE = 0.15      # mm

b = pcbnew.LoadBoard(REAL)
mortos = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        continue
    s, e = t.GetStart(), t.GetEnd()
    L = math.hypot(pcbnew.ToMM(e.x - s.x), pcbnew.ToMM(e.y - s.y))
    if L < LIMITE:
        mortos.append((t, round(L, 4), pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)))

for t, L, x, y in mortos:
    b.Remove(t)

pcbnew.SaveBoard(REAL, b)
print("cotocos removidos: %d" % len(mortos))
for _, L, x, y in mortos[:10]:
    print("   %.4f mm em (%.2f, %.2f)" % (L, x, y))
