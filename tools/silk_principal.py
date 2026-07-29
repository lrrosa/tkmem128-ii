# -*- coding: utf-8 -*-
"""Reposiciona a serigrafia de nivel de placa da principal depois do rearranjo.

Os textos ficaram onde estavam quando os CIs eram verticais. Aqui eles voltam
para areas livres: as legendas dos jumpers e a licenca no corredor entre a SRAM
e o conector (que tem cobre, mas serigrafia sobre trilha nao e problema — so
sobre ilha), e os nomes dos CIs junto de cada um.

Sai tambem a legenda de SJ1/SJ2, que nao existem mais.

  "C:/Program Files/KiCad/10.0/bin/python.exe" silk_principal.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM

FORA = ("SJ1  fechar", "SJ2  fechar", "SJ1 e SJ2")

# trecho do texto -> (x, y, tamanho, angulo)
POE = {
    "JP1": (23.0, 48.0, 0.9, 0),
    "JP2": (23.0, 50.0, 0.9, 0),
    "JP3": (23.0, 52.0, 0.9, 0),
    "JP4  fechado": (23.0, 54.0, 0.9, 0),
    "NUNCA feche": (23.0, 56.0, 0.9, 0),
    "CERN-OHL-S": (30.0, 23.5, 0.9, 0),
    "github.com": (30.0, 25.5, 0.9, 0),
    "Derivado de": (30.0, 46.0, 0.9, 0),
    "TKMEM-128": (30.0, 24.5, 1.1, 0),        # F.SilkS, titulo
}

mudou, tirou = [], []
for d in list(b.GetDrawings()):
    if d.GetClass() != "PCB_TEXT":
        continue
    t = d.GetText()
    if any(t.startswith(f) for f in FORA):
        b.Remove(d)
        tirou.append(t[:28])
        continue
    for chave, (x, y, tam, ang) in POE.items():
        if t.startswith(chave):
            d.SetPosition(pcbnew.VECTOR2I(fmm(x), fmm(y)))
            d.SetTextAngleDegrees(ang)
            d.SetTextSize(pcbnew.VECTOR2I(fmm(tam), fmm(tam)))
            d.SetTextThickness(fmm(round(tam * 0.2, 3)))
            mudou.append("%-28s -> (%.1f, %.1f)" % (t[:28], x, y))
            break

pcbnew.SaveBoard(REAL, b)
for t in tirou:
    print("  removido:", t)
for m in mudou:
    print("  ", m)
print("gravado:", REAL)
