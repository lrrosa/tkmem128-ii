# -*- coding: utf-8 -*-
"""Corrige a serigrafia da tira de expansao, preservando o arranjo manual.

Edicao cirurgica (padrao troca_j1.py): nao regera a placa, so mexe nos textos.

Tres coisas:

1. As ilhas de J1 sao SMD, uma face de cada pino. Na coluna de x=73,66 o cobre
   de F.Cu e o pino 56 e o de B.Cu e o pino 1 — a serigrafia da frente estava
   escrita "1", nomeando o pad de tras. Vira 56 / 29.
2. A tira e soldada dos dois lados, entao quem solda ve tanto a frente quanto o
   verso. Cada face ganha a numeracao dos seus proprios pads, em J1 e em J2.
3. "PASSAGEM ->" era ambiguo: a flecha aponta para +x, mas os dedos ficam para
   baixo. Vira um texto que diz o que e, junto dos dedos.

  "C:/Program Files/KiCad/10.0/bin/python.exe" corrige_silk_tira.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist_exp as TIRA

REAL = "%s/%s.kicad_pcb" % (TIRA.PROJ_DIR, TIRA.PROJ_NAME)
b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM


def texto_fp(fp, s, x, y, camada, tam, esp):
    t = pcbnew.PCB_TEXT(fp)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(fmm(x), fmm(y)))
    t.SetLayer(camada)
    t.SetTextSize(pcbnew.VECTOR2I(fmm(tam), fmm(tam)))
    t.SetTextThickness(fmm(esp))
    t.SetMirrored(camada in (pcbnew.B_SilkS, pcbnew.B_Fab))
    fp.Add(t)
    return t


fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
mudou = []

# --- 1) numeracao correta na frente de J1 -----------------------------------
# a coluna de cada pino ja foi validada por confere_alinhamento.py; aqui basta
# trocar o rotulo pelo pino que existe NAQUELA face
troca = {"1": "56", "28": "29"}
for it in fps["J1"].GraphicalItems():
    if it.GetClass() == "PCB_TEXT" and it.GetLayer() == pcbnew.F_SilkS:
        novo = troca.get(it.GetText())
        if novo:
            mudou.append("J1 F.SilkS  %-3s -> %s  (x=%.2f)"
                         % (it.GetText(), novo, mm(it.GetPosition().x)))
            it.SetText(novo)

# --- 2) numeracao no verso, nas duas conexoes -------------------------------
# espelha cada rotulo da frente para a face de tras com o pino de B.Cu
espelho = {"56": "1", "29": "28"}
for ref in ("J1", "J2"):
    fp = fps[ref]
    # copiar tudo para dados Python ANTES de remover: mexer na colecao invalida
    # o iterador do SWIG
    itens = [(it, it.GetClass(), it.GetLayer()) for it in fp.GraphicalItems()]
    novos = []
    for it, klass, camada in itens:
        if klass != "PCB_TEXT":
            continue
        if camada == pcbnew.B_SilkS:
            fp.Remove(it)        # rodar de novo nao pode duplicar serigrafia
            continue
        if camada != pcbnew.F_SilkS:
            continue
        p = it.GetPosition()
        alvo = espelho.get(it.GetText())
        if alvo:
            novos.append((alvo, mm(p.x), mm(p.y), mm(it.GetTextWidth()),
                          mm(it.GetTextThickness())))
        elif it.GetText() == "SOLDAR DOS DOIS LADOS":
            # instrucao dirigida a quem esta olhando o verso: repetir la
            novos.append((it.GetText(), mm(p.x), mm(p.y),
                          mm(it.GetTextWidth()), mm(it.GetTextThickness())))
    for s, x, y, tam, esp in novos:
        texto_fp(fp, s, x, y, pcbnew.B_SilkS, tam, esp)
        mudou.append("%s B.SilkS  + %-22s (x=%.2f y=%.2f)" % (ref, s, x, y))

# contorno e marca da guia nas duas faces, para orientar de que lado esta o
# pino 1 sem ter que virar a placa.
#
# O retangulo fechado que existia nao servia: do lado das ilhas fica a ARESTA
# da placa (y=0), entao um dos lados do retangulo caia FORA da placa e a marca
# da guia atravessava a borda. Vira um U aberto para a aresta, parando 0,3 mm
# antes dela.
fp = fps["J1"]
velhos = [it for it in fp.GraphicalItems()
          if it.GetClass() == "PCB_SHAPE" and it.GetLayer() in (pcbnew.F_SilkS,
                                                                pcbnew.B_SilkS)]
for it in velhos:
    fp.Remove(it)

Y_FUNDO, Y_ARESTA = 5.3, 0.3         # em coordenadas da placa
X_ESQ, X_DIR, X_GUIA = 3.08, 75.66, 63.50
tracos = [(X_ESQ, Y_FUNDO, X_DIR, Y_FUNDO),
          (X_ESQ, Y_FUNDO, X_ESQ, Y_ARESTA),
          (X_DIR, Y_FUNDO, X_DIR, Y_ARESTA),
          (X_GUIA, Y_FUNDO, X_GUIA, Y_ARESTA)]
for camada in (pcbnew.F_SilkS, pcbnew.B_SilkS):
    for x1, y1, x2, y2 in tracos:
        c = pcbnew.PCB_SHAPE(fp)
        c.SetShape(pcbnew.SHAPE_T_SEGMENT)
        c.SetStart(pcbnew.VECTOR2I(fmm(x1), fmm(y1)))
        c.SetEnd(pcbnew.VECTOR2I(fmm(x2), fmm(y2)))
        c.SetWidth(fmm(0.15))
        c.SetLayer(camada)
        fp.Add(c)
mudou.append("J1 silk    contorno refeito em U (4 tracos por face), "
             "nada fora da placa")

# --- 3) o texto ambiguo da passagem -----------------------------------------
# "PASSAGEM ->": a flecha apontava para +x, mas os dedos ficam para BAIXO.
# Basta dizer o que e e por perto de quem: os dedos comecam em y=37,38.
for d in b.GetDrawings():
    if d.GetClass() == "PCB_TEXT" and d.GetText() in ("PASSAGEM ->",
                                                      "PARA OUTROS PERIFERICOS"):
        d.SetText("PARA OUTROS PERIFERICOS")
        d.SetPosition(pcbnew.VECTOR2I(fmm(39.37), fmm(34.0)))
        mudou.append('placa      "PASSAGEM ->" -> "PARA OUTROS PERIFERICOS"')

pcbnew.SaveBoard(REAL, b)
for m in mudou:
    print(" ", m)
print("\ngravado:", REAL)
