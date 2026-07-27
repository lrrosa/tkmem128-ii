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
    return ('\t(fp_text user "%s"\n\t\t(at %s %s 0)\n\t\t(layer "%s")\n'
            '\t\t(effects (font (size %s %s) (thickness 0.15)))\n\t)\n'
            % (s, x, y, layer, size, size))


# ---------------------------------------------------------------- J1 socket
def gen_socket():
    """Terminais THT: fileira frontal = pinos 1..28, traseira = 29..56.

    y negativo = borda frontal da placa (lado do TK).
    """
    # TE/AMP 5645235 "Standard Edge II", 2,54 mm: terminais em duas fileiras
    # a 4,85 mm [.191], furo recomendado 1,02 +-0,08 mm [.040].
    yf, yr = -2.425, 2.425
    s = HDR % ("ZX_TK_Bus_Socket_56",
               "Soquete de borda femea 56 vias (28x2) passo 2,54mm, fileiras "
               "de terminais a 4,85mm, furo 1,02mm. TE/AMP 5645235 Standard "
               "Edge II. ATENCAO: e conector de entrada VERTICAL - a placa "
               "que o recebe fica PERPENDICULAR ao cartao do TK.",
               "conector borda edge socket 56 ZX Spectrum TK90X TK95",
               -6.5, "ZX_TK_Bus_Socket_56", 6.5)
    for c in range(1, NCOL + 1):
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
    s += line(xk, -5.0, xk, 5.0, "F.SilkS")
    s += text("GUIA 5/52", xk + 5.0, 0, "F.SilkS", 0.8)
    s += text("1", col_x(1), -6.2, "F.SilkS", 1.0)
    s += text("28", col_x(NCOL), -6.2, "F.SilkS", 1.0)
    s += text("56", col_x(1), 6.2, "F.SilkS", 1.0)
    s += text("29", col_x(NCOL), 6.2, "F.SilkS", 1.0)
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
    s += text("56", col_x(1), -5.4, "F.SilkS", 1.0)
    s += text("29", col_x(NCOL), -5.4, "F.SilkS", 1.0)
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

    Os terminais do TE 5645235 atravessam a placa principal e sobram 3,18 mm
    do outro lado. A tira encosta neles de chapa e e soldada. Mesma grade do
    conector: 2,54 mm entre colunas, 4,85 mm entre fileiras.
    """
    s = HDR % ("ZX_TK_Bus_SolderPads_56",
               "Ilhas de solda 2x28 (2,54 x 4,85mm) para a tira de expansao "
               "soldar nos terminais do conector TE 5645235 que atravessam a "
               "placa principal. Sem furos - so ilhas.",
               "tira expansao ilhas solda TK90X TK95 barramento",
               -6.0, "ZX_TK_Bus_SolderPads_56", 6.0)
    for c in range(1, NCOL + 1):
        x = col_x(c)
        for y, num in ((2.425, bottom_pin(c)), (-2.425, top_pin(c))):
            s += ('\t(pad "%d" smd roundrect\n\t\t(at %s %s)\n'
                  '\t\t(size 1.6 2.2)\n'
                  '\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n'
                  '\t\t(roundrect_rratio 0.2)\n\t)\n'
                  % (num, x, y))
    x1, x2 = X0 - 2.0, col_x(NCOL) + 2.0
    for ly, w in (("F.SilkS", 0.15), ("F.CrtYd", 0.05)):
        s += line(x1, -4.2, x2, -4.2, ly, w)
        s += line(x2, -4.2, x2, 4.2, ly, w)
        s += line(x2, 4.2, x1, 4.2, ly, w)
        s += line(x1, 4.2, x1, -4.2, ly, w)
    s += text("1", col_x(1), 5.2, "F.SilkS", 0.9)
    s += text("28", col_x(NCOL), 5.2, "F.SilkS", 0.9)
    s += text("56", col_x(1), -5.2, "F.SilkS", 0.9)
    s += text("29", col_x(NCOL), -5.2, "F.SilkS", 0.9)
    s += text("SOLDAR NOS TERMINAIS DO CONECTOR", 0, -5.2, "F.Fab", 1.0)
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
