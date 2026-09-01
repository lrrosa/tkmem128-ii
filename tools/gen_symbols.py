# -*- coding: utf-8 -*-
"""Gera a biblioteca de simbolos local da TKMEM-128."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS, BOTTOM, TOP, GAL20V8B, SRAM, HCT273, M27C256

OUT = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/lib/"
       "tkmem128.kicad_sym")

FONT = '(effects (font (size 1.27 1.27)))'


def prop(name, value, x, y, hide=False, justify=None, size=1.27):
    eff = '(font (size %s %s))' % (size, size)
    if justify:
        eff += ' (justify %s)' % justify
    if hide:
        eff += ' (hide yes)'
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s 0)\n'
            '\t\t\t(effects %s)\n\t\t)\n' % (name, value, x, y, eff))


def pin(etype, x, y, rot, name, number, length=2.54):
    x, y = round(float(x), 2), round(float(y), 2)
    return ('\t\t\t(pin %s line\n\t\t\t\t(at %s %s %s)\n\t\t\t\t(length %s)\n'
            '\t\t\t\t(name "%s" %s)\n\t\t\t\t(number "%s" %s)\n\t\t\t)\n'
            % (etype, x, y, rot, length, name, FONT, number, FONT))


def rect(x1, y1, x2, y2):
    return ('\t\t\t(rectangle\n\t\t\t\t(start %s %s)\n\t\t\t\t(end %s %s)\n'
            '\t\t\t\t(stroke (width 0.254) (type default))\n'
            '\t\t\t\t(fill (type background))\n\t\t\t)\n' % (x1, y1, x2, y2))


def build(name, value, footprint, descr, keywords, left, right, top, bottom,
          half_w, half_h, ref="U"):
    """left/right/top/bottom: listas de (numero, nome, tipo)."""
    s = '\t(symbol "%s"\n' % name
    s += '\t\t(pin_names (offset 1.016))\n'
    s += '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n'
    s += prop("Reference", ref, -half_w, half_h + 3.81, justify="left")
    s += prop("Value", value, -half_w, half_h + 1.27, justify="left")
    s += prop("Footprint", footprint, 0, 0, hide=True)
    s += prop("Datasheet", "", 0, 0, hide=True)
    s += prop("Description", descr, 0, 0, hide=True)
    s += prop("ki_keywords", keywords, 0, 0, hide=True)
    s += '\t\t(symbol "%s_0_1"\n' % name
    s += rect(-half_w, half_h, half_w, -half_h)
    s += '\t\t)\n'
    s += '\t\t(symbol "%s_1_1"\n' % name

    for i, (num, pname, etype) in enumerate(left):
        s += pin(etype, -half_w - 2.54, half_h - 2.54 * (i + 1), 0, pname, num)
    for i, (num, pname, etype) in enumerate(right):
        s += pin(etype, half_w + 2.54, half_h - 2.54 * (i + 1), 180, pname, num)
    for num, pname, etype in top:
        s += pin(etype, 0, half_h + 2.54, 270, pname, num)
    for num, pname, etype in bottom:
        s += pin(etype, 0, -half_h - 2.54, 90, pname, num)
    s += '\t\t)\n\t)\n'
    return s


parts = []

# ---------------------------------------------------------------- GAL20V8B
L = [(str(n), nm, et) for n, nm, et, side in GAL20V8B if side == "L"]
R = [(str(n), nm, et) for n, nm, et, side in GAL20V8B if side == "R"]
T = [(str(n), nm, et) for n, nm, et, side in GAL20V8B if side == "T"]
B = [(str(n), nm, et) for n, nm, et, side in GAL20V8B if side == "B"]
parts.append(build(
    "GAL20V8B_TKMEM", "GAL20V8B",
    "Package_DIP:DIP-24_W7.62mm_Socket_LongPads",
    "GAL20V8B / ATF20V8B / PALCE20V8H programado com as equacoes da TKMEM-128 "
    "(nomes dos pinos = funcao programada)",
    "GAL PLD 20V8 decodificador",
    L, R, T, B, half_w=17.78, half_h=20.32))

# -------------------------------------------------------------------- SRAM
L = [(str(n), nm, et) for n, nm, et, side in SRAM if side == "L"]
R = [(str(n), nm, et) for n, nm, et, side in SRAM if side == "R"]
T = [(str(n), nm, et) for n, nm, et, side in SRAM if side == "T"]
B = [(str(n), nm, et) for n, nm, et, side in SRAM if side == "B"]
parts.append(build(
    "SRAM_DIP32_1M_4M", "AS6C1008-55PCN",
    "Package_DIP:DIP-32_W15.24mm_Socket_LongPads",
    "SRAM 128Kx8 (AS6C1008) ou 512Kx8 (AS6C4008), DIP-32 JEDEC. "
    "Pino 1 = NC/A18, pino 30 = CE2/A17 conforme a densidade.",
    "SRAM 128K 512K DIP32",
    L, R, T, B, half_w=20.32, half_h=27.94))

# --------------------------------------------------------------- 74HCT273
L = [(str(n), nm, et) for n, nm, et, side in HCT273 if side == "L"]
R = [(str(n), nm, et) for n, nm, et, side in HCT273 if side == "R"]
T = [(str(n), nm, et) for n, nm, et, side in HCT273 if side == "T"]
B = [(str(n), nm, et) for n, nm, et, side in HCT273 if side == "B"]
parts.append(build(
    "74HCT273", "74HCT273",
    "Package_DIP:DIP-20_W7.62mm_Socket_LongPads",
    "Octal D flip-flop com master reset - latch da porta 0x7FFD",
    "74HCT273 latch flip-flop octal 7FFD",
    L, R, T, B, half_w=15.24, half_h=15.24))

# ----------------------------------------------------------------- 27C256
L = [(str(n), nm, et) for n, nm, et, side in M27C256 if side == "L"]
R = [(str(n), nm, et) for n, nm, et, side in M27C256 if side == "R"]
T = [(str(n), nm, et) for n, nm, et, side in M27C256 if side == "T"]
B = [(str(n), nm, et) for n, nm, et, side in M27C256 if side == "B"]
parts.append(build(
    "M27C256", "27C256",
    "Package_DIP:DIP-28_W15.24mm_Socket_LongPads",
    "EPROM 32Kx8 DIP-28 (par de ROMs do Spectrum 128)",
    "27C256 EPROM 32K ROM",
    L, R, T, B, half_w=17.78, half_h=21.59))

# ------------------------------------------------------- Barramento TK 56p
L = [(str(p), "%s (%s)" % (BUS[p][1], p), "passive") for p in BOTTOM]
R = [(str(p), "%s (%s)" % (BUS[p][1], p), "passive") for p in reversed(TOP)]
parts.append(build(
    "ZX_TK_Bus_56", "ZX_TK_Bus_56", "",
    "Barramento de expansao do ZX Spectrum 48K e clones (TK90X/TK95), "
    "2x28 passo 2,54mm, pinos 5 e 52 = guia. Numeracao 1..56 do TK.",
    "conector barramento TK90X TK95 ZX Spectrum edge",
    L, R, [], [], half_w=22.86, half_h=36.83, ref="J"))

# ------------------------------------------------- Header 2x28 entre placas
HDRPINS = list(range(1, 29)) + list(range(29, 57))
L = [(str(p), "%s (%s)" % (BUS[p][1] if p in BUS else "GND", p), "passive")
     for p in range(1, 29)]
R = [(str(p), "%s (%s)" % (BUS[p][1] if p in BUS else "GND", p), "passive")
     for p in range(56, 28, -1)]
parts.append(build(
    "ZX_TK_Bus_Header_56", "ZX_TK_Bus_Header_56", "",
    "Conector de borda femea 56 vias (TE/AMP 5645235) que recebe os dedos "
    "do micro. Numeracao 1..56 do TK; posicoes 5 e 52 sao a guia. A tira de "
    "expansao e soldada entre as duas fileiras de terminais dele.",
    "conector borda edge socket 56 TK90X TK95 ZX Spectrum",
    L, R, [], [], half_w=22.86, half_h=38.10, ref="J"))

with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write('(kicad_symbol_lib\n\t(version 20251024)\n'
            '\t(generator "tkmem128-gen")\n\t(generator_version "10.0")\n')
    for p in parts:
        f.write(p)
    f.write(')\n')

print("escrito:", OUT)
print("simbolos:", len(parts))
