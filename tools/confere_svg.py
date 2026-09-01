# -*- coding: utf-8 -*-
"""Procura sobreposicao entre texto e desenho no SVG da vista de lado.

Nao substitui olhar a imagem, mas pega o caso que mais escapa: texto pousado em
cima de trilha, ilha, parede ou de outro texto. A largura do glifo e estimada
(0,55 x tamanho da fonte), o que basta para acusar colisao real.
"""
import os, re, sys, xml.etree.ElementTree as ET

# Caminho derivado do proprio script, nao absoluto: com "F:/downloads/..."
# embutido isto rodava so na maquina de origem, e foi assim que o script
# derrubou o CI na primeira execucao.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    RAIZ, "docs", "img", "vista-de-lado.svg")
NS = "{http://www.w3.org/2000/svg}"
raiz = ET.parse(SVG).getroot()
LARG_TELA, ALT_TELA = [float(v) for v in raiz.get("viewBox").split()[2:]]


def num(el, chave, padrao=0.0):
    try:
        return float(el.get(chave, padrao))
    except (TypeError, ValueError):
        return padrao


def texto_de(el):
    return "".join(el.itertext()).strip()


caixas, tracos, rects = [], [], []
for el in raiz.iter():
    t = el.tag
    if t == NS + "text":
        s = texto_de(el)
        if not s:
            continue
        tam = num(el, "font-size", 13.0)
        larg = len(s) * tam * 0.55
        x, y = num(el, "x"), num(el, "y")
        anc = el.get("text-anchor", "start")
        if anc == "middle":
            x -= larg / 2.0
        elif anc == "end":
            x -= larg
        # texto branco e rotulo DENTRO de uma forma preenchida (o J1 no corpo do
        # conector): sobrepor e o objetivo, nao o defeito
        if el.get("fill", "").lower() in ("#fff", "#ffffff", "white"):
            continue
        caixas.append((s[:34], x, y - tam * 0.78, x + larg, y + tam * 0.22))
    elif t == NS + "line":
        tracos.append((num(el, "x1"), num(el, "y1"), num(el, "x2"), num(el, "y2"),
                       num(el, "stroke-width", 1.0)))
    elif t == NS + "rect":
        w, h = num(el, "width"), num(el, "height")
        if num(el, "x") == 0 and num(el, "y") == 0 and w >= LARG_TELA:
            continue                       # o fundo
        rects.append((num(el, "x"), num(el, "y"), num(el, "x") + w,
                      num(el, "y") + h))


def cruza(cx, seg):
    x1, y1, x2, y2 = cx[1], cx[2], cx[3], cx[4]
    ax, ay, bx, by, w = seg
    m = w / 2.0 + 1.0
    if abs(ay - by) < 0.5:                # horizontal
        return (min(ax, bx) - m < x2 and max(ax, bx) + m > x1
                and y1 < ay + m and y2 > ay - m)
    if abs(ax - bx) < 0.5:                # vertical
        return (min(ay, by) - m < y2 and max(ay, by) + m > y1
                and x1 < ax + m and x2 > ax - m)
    return False                          # diagonais: leader, ignora


def sobrepoe(a, b):
    return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]


achados = []
for cx in caixas:
    for seg in tracos:
        if cruza(cx, seg):
            achados.append("texto %-34r cortado por traco (%.0f,%.0f)-(%.0f,%.0f)"
                           % (cx[0], seg[0], seg[1], seg[2], seg[3]))
    for r in rects:
        if sobrepoe(cx, ("", r[0], r[1], r[2], r[3])):
            achados.append("texto %-34r sobre retangulo (%.0f,%.0f)-(%.0f,%.0f)"
                           % (cx[0], r[0], r[1], r[2], r[3]))
for i in range(len(caixas)):
    for j in range(i + 1, len(caixas)):
        if sobrepoe(caixas[i], caixas[j]):
            achados.append("texto %-34r sobre texto %r"
                           % (caixas[i][0], caixas[j][0]))

print("%d textos, %d tracos, %d retangulos" % (len(caixas), len(tracos), len(rects)))
fora = [c for c in caixas if c[1] < 0 or c[2] < 0 or c[3] > LARG_TELA or c[4] > ALT_TELA]
print("texto fora do quadro:", [c[0] for c in fora] or "nenhum")
print()
if achados:
    for a in achados:
        print("  ", a)
    raise SystemExit(1)
print("nenhuma sobreposicao de texto encontrada")
