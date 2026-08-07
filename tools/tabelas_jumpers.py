# -*- coding: utf-8 -*-
"""Troca a legenda dos jumpers por tabelas, e aumenta o titulo da placa.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tools/tabelas_jumpers.py

Antes cada jumper tinha uma linha corrida no verso, do tipo
`JP2  aberto = ROM do TK | 1-2 = pelo GAL | 2-3 = +5V`. Com a placa na mao e um
shunt na pinca isso e ruim: nao da para achar a posicao de relance. Vira
tabela, no formato que o Leonardo desenhou.

Onde couberam: nos canais que os soquetes DIP deixam entre as duas fileiras de
pinos. Sao os unicos retangulos grandes da placa — o resto esta tomado por
ilhas passantes, que existem nas DUAS faces — e no verso nada os cobre.

O texto vai centralizado em cada celula de proposito: em B.Silk ele e
espelhado, e com justificacao a esquerda o espelhamento joga a caixa para o
lado errado. Centralizado, a ancora e o centro nas duas faces.

DUAS ARMADILHAS de medicao, as duas descobertas aqui:

  GetBoundingBox() de texto RECEM-CRIADO devolve caixa sem pe nem cabeca — 13 mm
  de altura para fonte de 2,2. So depois de gravar e reler o valor presta. Por
  isso este script grava, rele, confere, e DESFAZ (copia de seguranca) se algo
  nao couber.

  Mesmo relida, a caixa sobra ~0,27 mm em cima e embaixo do glifo: 1,50 mm para
  fonte de 0,80. Serve para dizer se a largura cabe (e conservadora), nao para
  julgar altura. A altura da tinta e tamanho + espessura, e essa da para
  calcular.
"""
import os
import shutil

import pcbnew

MM = 1e6
PCB = "hardware/tkmem128-ii.kicad_pcb"
FACE = pcbnew.B_SilkS

FONTE, ESP = 0.8, 0.16          # 0,2 x tamanho, a regra de negrito do projeto
LARG_LINHA = 0.15
COL1, COL2, ALT = 6.5, 10.5, 1.7
FOLGA_ILHA = 0.25

# ONDE. As tabelas moram nos vazios que os soquetes DIP deixam entre as duas
# fileiras de pinos — no verso nada os cobre, e sao os unicos retangulos
# grandes da placa. JP2 e JP3 vao no canal de U3 (y 29,0..42,64, 13,64 mm de
# altura), centrados nele; JP1 vai na faixa livre acima de U1 (x 54..77,
# y 17..27), entre os pontos de teste e a fileira de cima do soquete.
#
# ATENCAO A ORDEM. Isto e o VERSO, que se le espelhado: x maior aparece mais a
# ESQUERDA para quem olha a placa por tras. Entao, em coordenada de placa, a
# tabela do JP1 fica na direita e a coluna da POSICAO vem depois da coluna do
# efeito — o inverso do que se quer ver. Lido na mao sai JP1, JP2, JP3, cada um
# com a posicao a esquerda e o efeito a direita, como no desenho do Leonardo.
TABELAS = [
    (4.0, 33.27, "JP3", [("ABERTO", "128K"),
                         ("FECHADO", "512K")]),
    (23.5, 32.42, "JP2", [("ABERTO", "ROM INTERNA"),
                          ("1-2", "ROMCS GAL"),
                          ("2-3", "ROMCS HIGH")]),
    (57.0, 21.3, "JP1", [("1-2", "ROM TKMEM"),
                         ("2-3", "ROM INTERNA")]),
]

# Em UMA linha o titulo nao passa de 1,35 mm: a faixa livre da face de cima tem
# 37 mm (entre R4 e C2) e os 31 caracteres ja ocupam 30 deles a 1,10. Em DUAS
# linhas o nome da placa vai a 2,2 — o dobro do que era — e o credito fica
# menor, embaixo, que e onde credito fica.
TITULO = [("TKMEM-128 II", 26.5, 50.7, 2.2),
          ("LRRosa 2026 v1.0", 26.5, 53.8, 1.4)]
BLOCO_TITULO = (8.3, 48.6, 44.7, 55.0)     # vazio conferido no mapa da face


def p(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


BAK = PCB + ".bak"
shutil.copy(PCB, BAK)
b = pcbnew.LoadBoard(PCB)

ilhas = []
for fp in b.Footprints():
    for q in fp.Pads():
        sz = q.GetSize(pcbnew.F_Cu)
        x, y = q.GetPosition().x / MM, q.GetPosition().y / MM
        ilhas.append((x - sz.x / MM / 2, y - sz.y / MM / 2,
                      x + sz.x / MM / 2, y + sz.y / MM / 2))


def bate_em_ilha(x1, y1, x2, y2):
    for a, c, d, e in ilhas:
        if (x1 - FOLGA_ILHA <= d and x2 + FOLGA_ILHA >= a and
                y1 - FOLGA_ILHA <= e and y2 + FOLGA_ILHA >= c):
            return (a, c)
    return None


# ---- limpa a faixa antes de desenhar --------------------------------------
# Idempotente de proposito: apaga tanto as legendas de uma linha (a versao
# antiga) quanto tabelas de rodadas anteriores, onde quer que elas tenham
# ficado. A faixa e exclusiva nossa: conferido item a item, entre y 18 e 42,5
# o verso nao tem mais nada — a licenca fica em y 9..15 e a nota do R4 em 50.
FAIXA = (1.0, 18.0, 78.0, 42.5)
velhas = []
for d in b.GetDrawings():
    if d.GetLayer() != FACE:
        continue
    if d.GetClass() == "PCB_TEXT" and d.GetText().startswith(("JP1", "JP2", "JP3")):
        velhas.append(d)
        continue
    bb = d.GetBoundingBox()
    if (FAIXA[0] <= bb.GetLeft() / MM and bb.GetRight() / MM <= FAIXA[2]
            and FAIXA[1] <= bb.GetTop() / MM and bb.GetBottom() / MM <= FAIXA[3]):
        velhas.append(d)
if not velhas:
    raise SystemExit("nao achei nada para substituir na faixa dos jumpers")
for d in velhas:
    b.Remove(d)
print("removidos da faixa: %d itens" % len(velhas))

modelo = [d for d in b.GetDrawings()
          if d.GetClass() == "PCB_TEXT" and d.GetLayer() == FACE][0]
ESPELHADO = modelo.IsMirrored()


def linha(x1, y1, x2, y2):
    g = pcbnew.PCB_SHAPE(b)
    g.SetShape(pcbnew.SHAPE_T_SEGMENT)
    g.SetStart(p(x1, y1))
    g.SetEnd(p(x2, y2))
    g.SetWidth(int(round(LARG_LINHA * MM)))
    g.SetLayer(FACE)
    b.Add(g)


def texto(s, cx, cy, tam, camada, espelhado):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s)
    t.SetLayer(camada)
    t.SetMirrored(espelhado)
    t.SetTextSize(pcbnew.VECTOR2I(int(tam * MM), int(tam * MM)))
    t.SetTextThickness(int(round(tam * 0.2 * MM)))
    t.SetPosition(p(cx, cy))
    b.Add(t)


problemas = []
conferir = []       # (texto, cx, cy, largura util, tamanho da fonte)

for x0, y0, nome, linhas_tab in TABELAS:
    nlin = len(linhas_tab) + 1
    # coluna do EFEITO primeiro, coluna da POSICAO depois — ver a nota da ordem
    x1, x2 = x0 + COL2, x0 + COL2 + COL1
    y_fim = y0 + nlin * ALT
    for i in range(nlin + 1):
        linha(x0, y0 + i * ALT, x2, y0 + i * ALT)
    for xv in (x0, x1, x2):
        linha(xv, y0, xv, y_fim)
    for i, (esq, dir_) in enumerate([(nome, "")] + list(linhas_tab)):
        cy = y0 + (i + 0.5) * ALT
        for s, cx, larg in ((dir_, x0 + COL2 / 2, COL2),
                            (esq, x1 + COL1 / 2, COL1)):
            if not s:
                continue
            texto(s, cx, cy, FONTE, FACE, ESPELHADO)
            conferir.append((s, cx, cy, larg, FONTE))
    colisao = bate_em_ilha(x0, y0, x2, y_fim)
    if colisao:
        problemas.append("%s (x %.1f..%.1f y %.1f..%.1f) encosta na ilha em "
                         "(%.2f, %.2f)" % (nome, x0, x2, y0, y_fim,
                                           colisao[0], colisao[1]))
    print("%s: %d linhas, x %.1f..%.1f, y %.1f..%.1f"
          % (nome, nlin, x0, x2, y0, y_fim))

# ---- titulo ---------------------------------------------------------------
# Idempotente tambem aqui: apaga o titulo de uma linha (versao antiga) OU as
# duas linhas de uma rodada anterior. Casar so por "TKMEM-128 II" deixava a
# linha do credito para tras, e a rodada seguinte empilhava outra por cima.
tit = [d for d in b.GetDrawings()
       if d.GetClass() == "PCB_TEXT"
       and d.GetText().startswith(("TKMEM-128 II", "LRRosa"))]
if not tit:
    raise SystemExit("nao achei o titulo da placa")
FACE_TIT, ESP_TIT = tit[0].GetLayer(), tit[0].IsMirrored()
for d in tit:
    print("titulo antigo removido: %r em %.1f mm"
          % (d.GetText(), d.GetTextWidth() / MM))
    b.Remove(d)
for s, cx, cy, tam in TITULO:
    texto(s, cx, cy, tam, FACE_TIT, ESP_TIT)
    conferir.append((s, cx, cy, BLOCO_TITULO[2] - BLOCO_TITULO[0], tam))

b.Save(PCB)

# ---- rele do disco e mede -------------------------------------------------
b2 = pcbnew.LoadBoard(PCB)
achados = []
for d in b2.GetDrawings():
    if d.GetClass() == "PCB_TEXT":
        bb = d.GetBoundingBox()
        achados.append((d.GetText(), bb.GetLeft() / MM, bb.GetTop() / MM,
                        bb.GetRight() / MM, bb.GetBottom() / MM))
print("\nmedido no arquivo gravado:")
for s, cx, cy, larg, tam in conferir:
    # so o texto certo NA POSICAO certa: 'ABERTO' e '1-2' aparecem em mais de
    # uma tabela, entao casar por conteudo sozinho pega a instancia errada
    cand = [a for a in achados if a[0] == s
            and abs((a[1] + a[3]) / 2 - cx) < 0.6
            and abs((a[2] + a[4]) / 2 - cy) < 0.6]
    if not cand:
        problemas.append("%r nao apareceu em (%.1f, %.1f)" % (s, cx, cy))
        continue
    _, ax1, ay1, ax2, ay2 = cand[0]
    w = ax2 - ax1
    tinta = tam + tam * 0.2
    cabe = w <= larg - 0.4 and tinta <= (ALT if larg <= COL2 else 99) - 0.2
    print("   %-18s largura %5.2f de %5.2f   tinta %.2f   %s"
          % (s, w, larg, tinta, "cabe" if cabe else "NAO CABE"))
    if not cabe:
        problemas.append("%r mede %.2f e a celula tem %.2f" % (s, w, larg))
    colisao = bate_em_ilha(ax1, cy - tinta / 2, ax2, cy + tinta / 2)
    if colisao:
        problemas.append("%r encosta na ilha em (%.2f, %.2f)"
                         % (s, colisao[0], colisao[1]))
    if larg > COL2:      # titulo: tem que caber no bloco livre
        if not (BLOCO_TITULO[0] <= ax1 and ax2 <= BLOCO_TITULO[2]
                and BLOCO_TITULO[1] <= cy - tinta / 2
                and cy + tinta / 2 <= BLOCO_TITULO[3]):
            problemas.append("%r sai do bloco livre do titulo" % s)

if problemas:
    shutil.copy(BAK, PCB)
    os.remove(BAK)
    print()
    for x in problemas:
        print("  PROBLEMA: %s" % x)
    raise SystemExit("desfeito: a placa voltou ao que era")
os.remove(BAK)
print("\ngravado.")
