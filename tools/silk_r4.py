# -*- coding: utf-8 -*-
"""Quebra a nota do R4 em duas linhas e troca "TK" por "micro".

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/silk_r4.py

Era uma linha so, de 57 caracteres e 43,4 mm — mais da metade da largura da
placa, atravessando o verso inteiro. Vira duas: a funcao em cima, o efeito
entre parenteses embaixo, com 28,1 mm na mais larga.

"do TK" virou "do micro" porque o pino 29 e N.C. nas duas maquinas e a placa
serve nas duas; o que e especifico do TK e o PONTO INTERNO onde o fio chega
(pino 10 do IC27), e isso esta em docs/PREPARAR-O-TK.md, nao cabe na
serigrafia.

Idempotente: reconhece tanto a linha unica antiga quanto as duas novas.
"""
import os
import shutil

import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"

# x=26,6 e nao 23,5: com a fonte em 1,2 mm a segunda linha passou a medir
# 37,7 mm, e centrada em 23,5 a ponta esquerda dela caia em cima das ilhas do
# proprio R4 (x 3,20..7,34). O vao livre nessa faixa vai de 7,34 a 46,50 —
# 39,2 mm — entao a linha so cabe centrada em 26,6.
LINHAS = [("R4: pull-up do pino 29", 26.60, 49.40),
          ("(auto-desativa a RAM de 32K do micro)", 26.60, 51.60)]
PREFIXOS = ("R4:", "(auto-desativa")
LIVRE = (7.6, 47.5, 46.2, 53.0)     # vazio do verso conferido no mapa


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


BAK = PCB + ".bak"
shutil.copy(PCB, BAK)
b = pcbnew.LoadBoard(PCB)

velhas = [d for d in b.GetDrawings()
          if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS
          and d.GetText().startswith(PREFIXOS)]
if not velhas:
    raise SystemExit("nao achei a nota do R4")
tam = velhas[0].GetTextWidth()
esp = velhas[0].GetTextThickness()
espelhado = velhas[0].IsMirrored()
for d in velhas:
    bb = d.GetBoundingBox()
    print("removido: %r  (%.1f mm de largura)"
          % (d.GetText(), (bb.GetRight() - bb.GetLeft()) / MM))
    b.Remove(d)

for s, cx, cy in LINHAS:
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s)
    t.SetLayer(pcbnew.B_SilkS)
    t.SetMirrored(espelhado)
    t.SetTextSize(pcbnew.VECTOR2I(tam, tam))
    t.SetTextThickness(esp)
    t.SetPosition(p(cx, cy))
    b.Add(t)

b.Save(PCB)

# a caixa de texto so vale depois de gravar e reler — ver tabelas_jumpers.py
b2 = pcbnew.LoadBoard(PCB)
problemas = []
print()
for d in b2.GetDrawings():
    if d.GetClass() != "PCB_TEXT" or not d.GetText().startswith(PREFIXOS):
        continue
    bb = d.GetBoundingBox()
    x1, y1 = bb.GetLeft() / MM, bb.GetTop() / MM
    x2, y2 = bb.GetRight() / MM, bb.GetBottom() / MM
    cabe = (LIVRE[0] <= x1 and x2 <= LIVRE[2]
            and LIVRE[1] <= y1 and y2 <= LIVRE[3])
    print("  %-38s x %5.2f..%5.2f  y %5.2f..%5.2f  %s"
          % (d.GetText(), x1, x2, y1, y2, "cabe" if cabe else "NAO CABE"))
    if not cabe:
        problemas.append(d.GetText())

if problemas:
    shutil.copy(BAK, PCB)
    os.remove(BAK)
    raise SystemExit("desfeito: %s nao cabe em x %.1f..%.1f y %.1f..%.1f"
                     % (problemas, LIVRE[0], LIVRE[2], LIVRE[1], LIVRE[3]))
os.remove(BAK)
print("\ngravado.")
