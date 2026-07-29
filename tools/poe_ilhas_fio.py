# -*- coding: utf-8 -*-
"""Coloca as ilhas dedicadas dos tres fios de ligacao da placa principal.

Fio soldado em cima da perna de outro componente parece conserto de erro. Cada
ligacao ganha um par de ilhas proprias, com serigrafia dizendo a qual rede
pertence — vira parte do projeto.

As posicoes vem de `busca_ilhas.py`, que procura, para cada ponta, o ponto livre
mais proximo onde cabe a ilha e um coto reto ate o cobre daquela rede. As duas
ilhas de um par caem sempre na MESMA face, senao o fio teria de contornar a
placa.

Ilha SMD, nao passante: junto do conector nao ha um milimetro livre nas duas
faces ao mesmo tempo (54 ilhas passantes a 2,54 mm). Numa face so, sobra.

  "C:/Program Files/KiCad/10.0/bin/python.exe" poe_ilhas_fio.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
LIB = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/lib/"
       "tkmem128.pretty")
LARG = 0.5

# rede -> (face, [(ancora_x, ancora_y, ilha_x, ilha_y), ...])
PLANO = [
    ("A4", "B", [(15.24, 64.655, 14.19, 63.45),
                 (21.08, 43.44, 21.46, 41.89)]),
    ("A2", "F", [(48.26, 64.655, 47.21, 63.45),
                 (26.16, 43.44, 26.54, 44.99)]),
    ("RESET_N", "B", [(25.40, 64.655, 25.48, 63.06),
                      (50.80, 49.32, 51.18, 50.87)]),
]

b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM
if any(f.GetFPIDAsString().endswith("WirePad_1.6mm") for f in b.GetFootprints()):
    raise SystemExit("as ilhas ja existem; reverta a placa antes de repetir")

n = 0
for net, face, pares in PLANO:
    code = b.GetNetcodeFromNetname(net)
    cu = pcbnew.B_Cu if face == "B" else pcbnew.F_Cu
    silk = pcbnew.B_SilkS if face == "B" else pcbnew.F_SilkS
    cantos = []
    for ax, ay, x, y in pares:
        n += 1
        fp = pcbnew.FootprintLoad(LIB, "WirePad_1.6mm")
        fp.SetReference("W%d" % n)
        fp.SetPosition(pcbnew.VECTOR2I(fmm(x), fmm(y)))
        b.Add(fp)
        if cu == pcbnew.B_Cu:
            fp.SetLayerAndFlip(pcbnew.B_Cu)
        for pd in fp.Pads():
            pd.SetNetCode(code)
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(fmm(ax), fmm(ay)))
        t.SetEnd(pcbnew.VECTOR2I(fmm(x), fmm(y)))
        t.SetWidth(fmm(LARG))
        t.SetLayer(cu)
        t.SetNetCode(code)
        b.Add(t)
        cantos.append((x, y, "W%d" % n))
    # tracejado ligando o par, para o fio ter um caminho desenhado
    (x1, y1, w1), (x2, y2, w2) = cantos
    for k in range(0, 14, 2):
        t0, t1 = k / 14.0, (k + 1) / 14.0
        ln = pcbnew.PCB_SHAPE(b)
        ln.SetShape(pcbnew.SHAPE_T_SEGMENT)
        ln.SetStart(pcbnew.VECTOR2I(fmm(x1 + (x2 - x1) * t0),
                                    fmm(y1 + (y2 - y1) * t0)))
        ln.SetEnd(pcbnew.VECTOR2I(fmm(x1 + (x2 - x1) * t1),
                                  fmm(y1 + (y2 - y1) * t1)))
        ln.SetWidth(fmm(0.12))
        ln.SetLayer(silk)
        b.Add(ln)
    tx = pcbnew.PCB_TEXT(b)
    tx.SetText("FIO %s" % net)
    tx.SetPosition(pcbnew.VECTOR2I(fmm((x1 + x2) / 2.0),
                                   fmm((y1 + y2) / 2.0 - 1.3)))
    tx.SetLayer(silk)
    tx.SetTextSize(pcbnew.VECTOR2I(fmm(0.9), fmm(0.9)))
    tx.SetTextThickness(fmm(0.18))
    tx.SetBold(True)
    tx.SetMirrored(silk == pcbnew.B_SilkS)
    b.Add(tx)
    print("  %-8s %s (%.2f,%.2f) <-> %s (%.2f,%.2f) na face %s.Cu"
          % (net, w1, x1, y1, w2, x2, y2, face))

pcbnew.SaveBoard(REAL, b)
print("gravado:", REAL)
