# -*- coding: utf-8 -*-
"""Confere o alinhamento fisico entre a placa principal e a tira de expansao.

A tira e soldada nos terminais do conector da placa principal. Os dois layouts
correm no MESMO sentido de X do mundo (a principal fica em pe com os
componentes virados para tras; a tira fica deitada com F.Cu para cima e sai
para tras). Logo, vistas nos respectivos layouts:

  - a coluna de cada pino tem que cair no mesmo x nas duas placas;
  - a guia (coluna sem contato) tem que cair no mesmo x nas duas;
  - a face de cada fileira tem que bater: 29..56 em cima, 1..28 embaixo.

Este script falha alto se algum desses invariantes quebrar. Rodar depois de
qualquer mexida em footprint, rotacao ou posicionamento dos conectores.

  "C:/Program Files/KiCad/10.0/bin/python.exe" confere_alinhamento.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC
import netlist_exp as TIRA


def ilhas(modulo, ref):
    caminho = "%s/%s.kicad_pcb" % (modulo.PROJ_DIR, modulo.PROJ_NAME)
    b = pcbnew.LoadBoard(caminho)
    for fp in b.GetFootprints():
        if fp.GetReference() != ref:
            continue
        out = {}
        for p in fp.Pads():
            pos = p.GetPosition()
            out[int(p.GetNumber())] = (round(pcbnew.ToMM(pos.x), 2),
                                       round(pcbnew.ToMM(pos.y), 2),
                                       p.IsOnLayer(pcbnew.F_Cu),
                                       p.IsOnLayer(pcbnew.B_Cu))
        return out
    raise SystemExit("%s nao tem %s" % (modulo.PROJ_NAME, ref))


def vao_da_guia(xs):
    xs = sorted(set(xs))
    todos = [round(xs[0] + 2.54 * k, 2) for k in range(28)]
    faltando = [x for x in todos if x not in xs]
    return faltando


erros = []
conector = ilhas(PRINC, "J1")      # conector de borda na placa principal
tira_j1 = ilhas(TIRA, "J1")        # ilhas de solda da tira
tira_j2 = ilhas(TIRA, "J2")        # dedos de passagem

# 1) coluna de cada pino
divergentes = [n for n in sorted(conector)
               if n in tira_j1 and conector[n][0] != tira_j1[n][0]]
if divergentes:
    erros.append("colunas divergentes entre o conector e as ilhas da tira: %d "
                 "pinos (ex.: pino %d em x=%.2f na principal e x=%.2f na tira)"
                 % (len(divergentes), divergentes[0],
                    conector[divergentes[0]][0], tira_j1[divergentes[0]][0]))

# 2) guia
g_con = vao_da_guia([v[0] for v in conector.values()])
g_tira = vao_da_guia([v[0] for v in tira_j1.values()])
g_ded = vao_da_guia([v[0] for v in tira_j2.values()])
if not (g_con == g_tira == g_ded):
    erros.append("guia em x diferente: conector %s, ilhas %s, dedos %s"
                 % (g_con, g_tira, g_ded))

# 3) faces das fileiras na tira: 29..56 em F.Cu, 1..28 em B.Cu
for nome, mapa in (("ilhas J1", tira_j1), ("dedos J2", tira_j2)):
    for n, (x, y, f, b_) in mapa.items():
        esperado_f = n >= 29
        if f != esperado_f or b_ == esperado_f:
            erros.append("%s: pino %d na face errada (F.Cu=%s, B.Cu=%s)"
                         % (nome, n, f, b_))
            break

# 4) fileira do conector: 1..28 junto a aresta de baixo da placa principal
y1 = conector[1][1]
y56 = conector[56][1]
if not y1 > y56:
    erros.append("no conector, a fileira 1..28 deveria estar mais proxima da "
                 "aresta inferior (y maior): pino 1 em y=%.2f, pino 56 em "
                 "y=%.2f" % (y1, y56))


# 5) a serigrafia de cada face so pode nomear pads DAQUELA face
#
# Nas ilhas e nos dedos cada pino existe em uma face so: na coluna x=73,66 o
# cobre de F.Cu e o pino 56 e o de B.Cu e o pino 1. Escrever "1" na frente
# nomeia o pad de tras — foi exatamente o erro que J1 da tira tinha.
def confere_rotulos(modulo, refs):
    caminho = "%s/%s.kicad_pcb" % (modulo.PROJ_DIR, modulo.PROJ_NAME)
    b = pcbnew.LoadBoard(caminho)
    mm = pcbnew.ToMM
    for fp in b.GetFootprints():
        if fp.GetReference() not in refs:
            continue
        pads = [(int(p.GetNumber()), mm(p.GetPosition().x),
                 mm(p.GetPosition().y), p.IsOnLayer(pcbnew.F_Cu),
                 p.IsOnLayer(pcbnew.B_Cu)) for p in fp.Pads()]
        for it in fp.GraphicalItems():
            if it.GetClass() != "PCB_TEXT":
                continue
            camada = it.GetLayer()
            if camada not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                continue
            s = it.GetText()
            if not s.isdigit():
                continue
            frente = camada == pcbnew.F_SilkS
            p = it.GetPosition()
            tx, ty = mm(p.x), mm(p.y)
            perto = min((q for q in pads if (q[3] if frente else q[4])),
                        key=lambda q: (q[1] - tx) ** 2 + (q[2] - ty) ** 2)
            if perto[0] != int(s):
                erros.append('%s %s: rotulo "%s" em %s (x=%.2f y=%.2f) esta '
                             'sobre o pino %d daquela face'
                             % (modulo.PROJ_NAME, fp.GetReference(), s,
                                b.GetLayerName(camada), tx, ty, perto[0]))


confere_rotulos(TIRA, ("J1", "J2"))
confere_rotulos(PRINC, ("J1",))

print("conector (principal): pino 1 em x=%.2f, pino 28 em x=%.2f, guia em %s"
      % (conector[1][0], conector[28][0], g_con))
print("ilhas    (tira)     : pino 1 em x=%.2f, pino 28 em x=%.2f, guia em %s"
      % (tira_j1[1][0], tira_j1[28][0], g_tira))
print("dedos    (tira)     : pino 1 em x=%.2f, pino 28 em x=%.2f, guia em %s"
      % (tira_j2[1][0], tira_j2[28][0], g_ded))
print()
if erros:
    for e in erros:
        print("FALHA:", e)
    raise SystemExit(1)
print("OK: colunas, guia, faces e fileiras alinhadas entre as duas placas.")
