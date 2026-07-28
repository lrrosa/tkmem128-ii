# -*- coding: utf-8 -*-
"""Footprints proprios da TKMEM-128 KiCad.

J1  soquete de borda femea 56 vias (grade 0,100" x 0,200" = 2,54 x 5,08 mm)
J2  dedos de borda para passagem do barramento (1,524 x 7,62 mm, passo 2,54)

Coluna fisica c (1..28) da esquerda para a direita, vista pelo lado dos
componentes:  fileira inferior = pino c   |   fileira superior = pino 57-c
Coluna 5 = guia mecanica (sem contato nas duas fileiras).
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS

OUTDIR = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/"
          "lib/tkmem128.pretty")

PITCH = 2.54
NCOL = 28
KEYCOL = 5
SPAN = (NCOL - 1) * PITCH          # 68.58 mm centro a centro
X0 = -SPAN / 2.0                   # coluna 1 a esquerda


def col_x(c):
    return round(X0 + (c - 1) * PITCH, 4)


def bottom_pin(c):
    return c


def top_pin(c):
    return 57 - c


HDR = ('(footprint "%s"\n\t(version 20260206)\n\t(generator "tkmem128-gen")\n'
       '\t(generator_version "10.0")\n\t(layer "F.Cu")\n\t(descr "%s")\n'
       '\t(tags "%s")\n'
       '\t(property "Reference" "J**"\n\t\t(at 0 %s 0)\n\t\t(layer "F.SilkS")\n'
       '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
       '\t(property "Value" "%s"\n\t\t(at 0 %s 0)\n\t\t(layer "F.Fab")\n'
       '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
       '\t(attr through_hole)\n')


def line(x1, y1, x2, y2, layer, w=0.15):
    return ('\t(fp_line\n\t\t(start %s %s)\n\t\t(end %s %s)\n'
            '\t\t(stroke (width %s) (type solid))\n\t\t(layer "%s")\n\t)\n'
            % (x1, y1, x2, y2, w, layer))


def text(s, x, y, layer, size=1.0):
    # texto em camada de tras precisa de (justify mirror), senao sai espelhado
    # e ilegivel para quem olha a placa por tras
    esp = " (justify mirror)" if layer.startswith("B.") else ""
    return ('\t(fp_text user "%s"\n\t\t(at %s %s 0)\n\t\t(layer "%s")\n'
            '\t\t(effects (font (size %s %s) (thickness 0.15))%s)\n\t)\n'
            % (s, x, y, layer, size, size, esp))


# ---------------------------------------------------------------- J1 socket
def gen_socket():
    """Terminais THT do conector de borda.

    A placa principal fica EM PE e o conector vai na borda de baixo. Os pinos
    1..28 sao a fileira DE BAIXO do TK, entao ficam do lado da borda (y
    positivo, mais perto da aresta inferior da placa); 29..56 sao a fileira de
    cima e ficam do lado de dentro.

    TE/AMP 5645235 "Standard Edge II", 2,54 mm: terminais em duas fileiras a
    4,85 mm [.191], furo recomendado 1,02 +-0,08 mm [.040].

    O contorno desenha o corpo do conector, que de fato avanca alem da aresta
    da placa — e um conector DE BORDA. Serigrafia fora da placa nao imprime, e
    o fabricante recorta; na placa principal quem apara e
    `silk_conector_principal.py`, que deixa um U aberto para a aresta.
    """
    yf, yr = 2.425, -2.425
    s = HDR % ("ZX_TK_Bus_Socket_56",
               "Soquete de borda femea 56 vias (28x2) passo 2,54mm, fileiras "
               "de terminais a 4,85mm, furo 1,02mm. TE/AMP 5645235 Standard "
               "Edge II. ATENCAO: e conector de entrada VERTICAL - a placa "
               "que o recebe fica PERPENDICULAR ao cartao do TK.",
               "conector borda edge socket 56 ZX Spectrum TK90X TK95",
               -6.5, "ZX_TK_Bus_Socket_56", 6.5)
    for c in range(1, NCOL + 1):
        if c == KEYCOL:
            continue          # a guia ocupa esta posicao: sem terminal, sem furo
        x = col_x(c)
        for y, num in ((yf, bottom_pin(c)), (yr, top_pin(c))):
            shape = "rect" if num == 1 else "circle"
            s += ('\t(pad "%d" thru_hole %s\n\t\t(at %s %s)\n'
                  '\t\t(size 1.75 1.75)\n\t\t(drill 1.02)\n'
                  '\t\t(layers "*.Cu" "*.Mask")\n\t)\n' % (num, shape, x, y))
    # contorno do corpo do conector
    x1, x2 = X0 - 2.2, col_x(NCOL) + 2.2
    for ly in ("F.SilkS", "F.CrtYd"):
        w = 0.15 if ly == "F.SilkS" else 0.05
        s += line(x1, -5.0, x2, -5.0, ly, w)
        s += line(x2, -5.0, x2, 5.0, ly, w)
        s += line(x2, 5.0, x1, 5.0, ly, w)
        s += line(x1, 5.0, x1, -5.0, ly, w)
    # marcacao da guia e do pino 1
    xk = col_x(KEYCOL)
    # Terminais THT: cada pino existe nas DUAS faces, na mesma coluna. A
    # numeracao vai nas duas porque as duas sao usadas — de um lado solda-se o
    # conector, do outro solda-se a tira de expansao nos terminais que
    # atravessam a placa.
    for ly in ("F.SilkS", "B.SilkS"):
        s += line(xk, -5.0, xk, 5.0, ly)
        s += text("GUIA 5/52", xk + 5.0, 0, ly, 0.8)
        s += text("1", col_x(1), 6.2, ly, 1.0)
        s += text("28", col_x(NCOL), 6.2, ly, 1.0)
        s += text("56", col_x(1), -6.2, ly, 1.0)
        s += text("29", col_x(NCOL), -6.2, ly, 1.0)
    s += text("TK90X/TK95", 0, -6.2, "F.Fab", 1.0)
    return s + ')\n'


# --------------------------------------------------------------- J2 fingers
def gen_fingers():
    """Dedos de borda: fileira superior (F.Cu) = 29..56, inferior (B.Cu)=1..28.

    Espelha a placa-mae do TK: o dedo do lado dos componentes carrega os
    pinos 29..56, exatamente como o TK visto por tras.
    """
    L = 7.62      # comprimento do dedo
    W = 1.524     # largura do dedo
    s = HDR % ("ZX_TK_Bus_Fingers_56",
               "Dedos de borda 56 vias (28x2) passo 2,54mm para passagem do "
               "barramento TK90X/TK95. Requer chanfro 45 graus e ouro ENIG. "
               "Coluna 5 = guia (rasgo no contorno da placa).",
               "conector borda edge fingers 56 ZX Spectrum TK90X TK95 passthrough",
               -6.5, "ZX_TK_Bus_Fingers_56", 6.5)
    for c in range(1, NCOL + 1):
        if c == KEYCOL:
            continue
        x = col_x(c)
        s += ('\t(pad "%d" smd rect\n\t\t(at %s 0)\n\t\t(size %s %s)\n'
              '\t\t(layers "F.Cu" "F.Mask")\n\t)\n' % (top_pin(c), x, W, L))
        s += ('\t(pad "%d" smd rect\n\t\t(at %s 0)\n\t\t(size %s %s)\n'
              '\t\t(layers "B.Cu" "B.Mask")\n\t)\n' % (bottom_pin(c), x, W, L))
    x1, x2 = X0 - 2.2, col_x(NCOL) + 2.2
    for ly in ("F.CrtYd",):
        s += line(x1, -L / 2, x2, -L / 2, ly, 0.05)
        s += line(x2, -L / 2, x2, L / 2, ly, 0.05)
        s += line(x2, L / 2, x1, L / 2, ly, 0.05)
        s += line(x1, L / 2, x1, -L / 2, ly, 0.05)
    # cada face leva a numeracao dos SEUS dedos: F.Cu = 29..56, B.Cu = 1..28
    s += text("56", col_x(1), -5.4, "F.SilkS", 1.0)
    s += text("29", col_x(NCOL), -5.4, "F.SilkS", 1.0)
    s += text("1", col_x(1), -5.4, "B.SilkS", 1.0)
    s += text("28", col_x(NCOL), -5.4, "B.SilkS", 1.0)
    s += text("PASSAGEM DO BARRAMENTO", 0, -5.4, "F.Fab", 1.0)
    return s + ')\n'


# ---------------------------------------------------------------- J header
def gen_header():
    """Header 2x28 entre a placa principal e a expansora.

    Fileira y=+1.27 -> pinos 1..28   |   fileira y=-1.27 -> pinos 29..56
    Posicoes 5 e 52 existem fisicamente e sao GND adicional entre as placas.
    """
    s = HDR % ("ZX_TK_Bus_Header_2x28",
               "Header 2x28 passo 2,54mm ligando a placa principal (soquete "
               "femea angular) a placa expansora (pino macho vertical). "
               "Numeracao 1..56 do TK; posicoes 5 e 52 = GND adicional.",
               "header 2x28 TK90X TK95 interligacao placas",
               -5.0, "ZX_TK_Bus_Header_2x28", 5.0)
    for c in range(1, NCOL + 1):
        x = col_x(c)
        for y, num in ((1.27, bottom_pin(c)), (-1.27, top_pin(c))):
            shape = "rect" if num == 1 else "circle"
            s += ('\t(pad "%d" thru_hole %s\n\t\t(at %s %s)\n'
                  '\t\t(size 1.7 1.7)\n\t\t(drill 1.0)\n'
                  '\t\t(layers "*.Cu" "*.Mask")\n\t)\n' % (num, shape, x, y))
    x1, x2 = X0 - 1.9, col_x(NCOL) + 1.9
    for ly, w in (("F.SilkS", 0.15), ("F.CrtYd", 0.05)):
        s += line(x1, -3.2, x2, -3.2, ly, w)
        s += line(x2, -3.2, x2, 3.2, ly, w)
        s += line(x2, 3.2, x1, 3.2, ly, w)
        s += line(x1, 3.2, x1, -3.2, ly, w)
    s += text("1", col_x(1), -4.2, "F.SilkS", 0.9)
    s += text("56", col_x(3), -4.2, "F.SilkS", 0.9)
    s += text("28", col_x(NCOL), -4.2, "F.SilkS", 0.9)
    s += text("29", col_x(NCOL - 2), -4.2, "F.SilkS", 0.9)
    return s + ')\n'


# ------------------------------------------------- ilhas de solda da tira
def gen_solderpads():
    """Tira de expansao: ilhas que recebem os terminais do conector.

    Os terminais do TE 5645235 sao RETOS e ficam em duas fileiras a 4,85 mm.
    A tira entra ENTRE elas: uma fileira passa por cima da tira e a outra por
    baixo. Por isso ha ilhas nas DUAS faces, na mesma posicao, e a solda e
    feita dos dois lados.

    Mesma convencao de face dos dedos de J2: F.Cu leva 29..56 (a fileira de
    cima do TK) e B.Cu leva 1..28.

    Convencao de orientacao (igual a de ZX_TK_Bus_Fingers_56): a aresta livre
    da placa fica no +y local e o corpo da placa no -y. Toda a serigrafia mora
    no -y. Na tira desta interface os dois conectores entram girados 180 graus,
    entao a serigrafia foi reposicionada a mao no .kicad_pcb.
    """
    # A ilha comeca NA BORDA da tira e entra 5 mm. Os terminais do conector
    # so avancam 3,18 mm (+-0,51), e ha modelos com terminal mais curto — com
    # a ilha chegando na borda, o terminal sempre encontra cobre.
    L = 5.0
    W = 1.7
    s = HDR % ("ZX_TK_Bus_SolderPads_56",
               "Ilhas de solda nas duas faces (54 vias, passo 2,54mm) para a "
               "tira de expansao ser soldada entre os terminais retos do "
               "conector TE 5645235. As ilhas chegam ate a borda da tira, para "
               "acomodar conectores com terminal mais curto. "
               "F.Cu = 29..56, B.Cu = 1..28. Sem furos.",
               "tira expansao ilhas solda TK90X TK95 barramento",
               -5.5, "ZX_TK_Bus_SolderPads_56", 5.5)
    for c in range(1, NCOL + 1):
        if c == KEYCOL:
            continue          # a guia ocupa esta posicao
        x = col_x(c)
        s += ('\t(pad "%d" smd rect\n\t\t(at %s 0)\n\t\t(size %s %s)\n'
              '\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n\t)\n'
              % (top_pin(c), x, W, L))
        s += ('\t(pad "%d" smd rect\n\t\t(at %s 0)\n\t\t(size %s %s)\n'
              '\t\t(layers "B.Cu" "B.Mask" "B.Paste")\n\t)\n'
              % (bottom_pin(c), x, W, L))
    x1, x2 = X0 - 2.0, col_x(NCOL) + 2.0
    # contorno em U aberto, nao retangulo: do lado das ilhas fica a ARESTA da
    # placa, e fechar o retangulo poria serigrafia fora da placa (e um traco
    # atravessado sobre todas as ilhas). Os tracos param 0,3 mm antes da borda.
    yb, yf_ = -L / 2 - 0.3, L / 2 - 0.3
    s += line(x1, yb, x2, yb, "F.CrtYd", 0.05)
    s += line(x2, yb, x2, L / 2 + 0.4, "F.CrtYd", 0.05)
    s += line(x2, L / 2 + 0.4, x1, L / 2 + 0.4, "F.CrtYd", 0.05)
    s += line(x1, L / 2 + 0.4, x1, yb, "F.CrtYd", 0.05)
    xk = col_x(KEYCOL)
    for ly in ("F.SilkS", "B.SilkS"):
        s += line(x1, yb, x2, yb, ly)
        s += line(x1, yb, x1, yf_, ly)
        s += line(x2, yb, x2, yf_, ly)
        s += line(xk, yb, xk, yf_, ly)      # coluna da guia
    # a serigrafia de cada face nomeia os pads DAQUELA face: as ilhas sao SMD,
    # entao a coluna de x=col_x(1) e o pino 56 em F.Cu e o pino 1 em B.Cu.
    # Rotular a frente com "1" seria nomear o pad de tras.
    yt = -L / 2 - 1.4          # do lado do corpo da placa, nunca o da aresta
    s += text("56", col_x(1), yt, "F.SilkS", 0.9)
    s += text("29", col_x(NCOL), yt, "F.SilkS", 0.9)
    s += text("1", col_x(1), yt, "B.SilkS", 0.9)
    s += text("28", col_x(NCOL), yt, "B.SilkS", 0.9)
    s += text("SOLDAR DOS DOIS LADOS", 0, yt, "F.SilkS", 0.9)
    s += text("SOLDAR DOS DOIS LADOS", 0, yt, "B.SilkS", 0.9)
    return s + ')\n'


if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)

for name, body in (("ZX_TK_Bus_Socket_56", gen_socket()),
                   ("ZX_TK_Bus_Fingers_56", gen_fingers()),
                   ("ZX_TK_Bus_Header_2x28", gen_header()),
                   ("ZX_TK_Bus_SolderPads_56", gen_solderpads())):
    path = os.path.join(OUTDIR, name + ".kicad_mod")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print("escrito:", path)

print("span dos contatos: %.2f mm  (coluna 1 em x=%.2f)" % (SPAN, X0))
