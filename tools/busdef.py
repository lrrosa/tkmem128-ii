# -*- coding: utf-8 -*-
"""Definicao unica do barramento TK90X/TK95 e da netlist da TKMEM-128.

Numeracao 1..56 conforme a pinagem oficial do expansor do TK (Luccas Eletronica),
confirmada contra o esquematico Velesoft zx48_to_128-EASY_3 (A/B do ZX Spectrum).
Pinos 5 e 52 sao a guia mecanica (nao existem como contato).
"""

KEY_PINS = (5, 52)

# pino -> (nome do sinal na net, rotulo impresso, observacao)
# nome None => pino sem net propria alem do passthrough
BUS = {
    1:  ("A14",      "A14",      ""),
    2:  ("A12",      "A12",      ""),
    3:  ("+5V",      "+5V",      "alimentacao principal"),
    4:  ("BUS_9V",   "+9V",      "nao usado (USS no Spectrum)"),
    6:  ("GND",      "GND",      ""),
    7:  ("BUS_P07",  "NC/GND",   "GND no ZX Spectrum, NC no TK -> SJ1"),
    8:  ("BUS_CLK",  "CLOCK",    "nao usado"),
    9:  ("A0",       "A0",       ""),
    10: ("A1",       "A1",       ""),
    11: ("A2",       "A2",       ""),
    12: ("A3",       "A3",       ""),
    13: ("BUS_IORQGE", "IORQGE", "nao usado"),
    14: ("GND",      "GND",      ""),
    15: ("BUS_P15",  "GND/NC",   "GND no TK, sinal no Spectrum -> SJ2"),
    16: ("BUS_P16",  "NC/Y",     "livre no TK; Y do video componente no ZX Spectrum"),
    17: ("RAMDIS",   "RAMDIS",   "auto-desativa 32K do TK; V do video componente no ZX Spectrum"),
    18: ("BUS_P18",  "NC/U",     "livre no TK; U do video componente no ZX Spectrum"),
    19: ("BUS_BUSREQ", "BUSREQ", "nao usado"),
    20: ("RESET_N",  "/RESET",   ""),
    21: ("A7",       "A7",       ""),
    22: ("A6",       "A6",       ""),
    23: ("A5",       "A5",       ""),
    24: ("A4",       "A4",       ""),
    25: ("ROMCS_BUS", "ROMCS",   "ativo ALTO desabilita ROM interna"),
    26: ("BUS_BUSACK", "BUSACK", "nao usado"),
    27: ("A9",       "A9",       ""),
    28: ("A11",      "A11",      ""),
    29: ("BUS_P29",  "NC",       "nao usado"),
    30: ("A10",      "A10",      ""),
    31: ("A8",       "A8",       ""),
    32: ("BUS_RFSH", "/RFSH",    "nao usado"),
    33: ("BUS_M1",   "/M1",      "nao usado"),
    34: ("BUS_P34",  "12V",      "difere TK x Spectrum - NAO conectar"),
    35: ("BUS_P35",  "12V",      "difere TK x Spectrum - NAO conectar"),
    36: ("BUS_WAIT", "/WAIT",    "nao usado"),
    37: ("BUS_P37",  "+5V/-5V",  "+5V no TK, -5V no Spectrum - NAO conectar"),
    38: ("WR_N",     "/WR",      ""),
    39: ("RD_N",     "/RD",      ""),
    40: ("IORQ_N",   "/IORQ",    ""),
    41: ("MREQ_N",   "/MREQ",    ""),
    42: ("BUS_HALT", "/HALT",    "nao usado"),
    43: ("BUS_NMI",  "/NMI",     "nao usado"),
    44: ("BUS_INT",  "/INT",     "nao usado"),
    45: ("D4",       "D4",       ""),
    46: ("D3",       "D3",       ""),
    47: ("D5",       "D5",       ""),
    48: ("D6",       "D6",       ""),
    49: ("D2",       "D2",       ""),
    50: ("D1",       "D1",       ""),
    51: ("D0",       "D0",       ""),
    53: ("BUS_SOUNDIN", "SOUND IN", "nao usado"),
    54: ("D7",       "D7",       ""),
    55: ("A13",      "A13",      ""),
    56: ("A15",      "A15",      ""),
}

BOTTOM = [p for p in range(1, 29) if p not in KEY_PINS]   # 1..28
TOP = [p for p in range(29, 57) if p not in KEY_PINS]     # 29..56

assert len(BOTTOM) == 27 and len(TOP) == 27, (len(BOTTOM), len(TOP))
assert len(BUS) == 54, len(BUS)

# --------------------------------------------------------------------------
# Pinagem dos CIs (nome do pino no simbolo -> numero fisico)
# --------------------------------------------------------------------------

GAL20V8B = [
    # (num, nome, tipo eletrico, lado)
    (1,  "MREQ",    "input",  "L"),
    (2,  "ZX512",   "input",  "L"),
    (3,  "A1",      "input",  "L"),
    (4,  "WR",      "input",  "L"),
    (5,  "DIS128",  "input",  "L"),
    (6,  "BANK2",   "input",  "L"),
    (7,  "A5",      "input",  "L"),
    (8,  "BANK0",   "input",  "L"),
    (9,  "BANK4",   "input",  "L"),
    (10, "BANK3",   "input",  "L"),
    (11, "BANK1",   "input",  "L"),
    (13, "A15",     "input",  "L"),
    (14, "A14",     "input",  "L"),
    (23, "IORQ",    "input",  "L"),
    (15, "~{ROMCS}", "output", "R"),
    (16, "CLK7FFD", "output", "R"),
    (17, "SA18",    "output", "R"),
    (18, "~{SA17}", "output", "R"),
    (19, "~{RAMCS}", "output", "R"),
    (20, "SA16",    "output", "R"),
    (21, "SA15",    "output", "R"),
    (22, "SA14",    "output", "R"),
    (12, "GND",     "power_in", "B"),
    (24, "VCC",     "power_in", "T"),
]

# SRAM 32-pin DIP JEDEC (AS6C1008 128Kx8 / AS6C4008 512Kx8)
SRAM = [
    (1,  "A18/NC",  "input", "L"),
    (2,  "A16",     "input", "L"),
    (3,  "A14",     "input", "L"),
    (4,  "A12",     "input", "L"),
    (5,  "A7",      "input", "L"),
    (6,  "A6",      "input", "L"),
    (7,  "A5",      "input", "L"),
    (8,  "A4",      "input", "L"),
    (9,  "A3",      "input", "L"),
    (10, "A2",      "input", "L"),
    (11, "A1",      "input", "L"),
    (12, "A0",      "input", "L"),
    (23, "A10",     "input", "L"),
    (25, "A11",     "input", "L"),
    (26, "A9",      "input", "L"),
    (27, "A8",      "input", "L"),
    (28, "A13",     "input", "L"),
    (31, "A15",     "input", "L"),
    (13, "DQ0",     "bidirectional", "R"),
    (14, "DQ1",     "bidirectional", "R"),
    (15, "DQ2",     "bidirectional", "R"),
    (17, "DQ3",     "bidirectional", "R"),
    (18, "DQ4",     "bidirectional", "R"),
    (19, "DQ5",     "bidirectional", "R"),
    (20, "DQ6",     "bidirectional", "R"),
    (21, "DQ7",     "bidirectional", "R"),
    (22, "~{CE1}",  "input", "R"),
    (30, "A17/CE2", "input", "R"),
    (24, "~{OE}",   "input", "R"),
    (29, "~{WE}",   "input", "R"),
    (16, "GND",     "power_in", "B"),
    (32, "VCC",     "power_in", "T"),
]

# 74HCT273 - octal D flip-flop com master reset (latch da porta 0x7FFD)
HCT273 = [
    (1,  "~{MR}", "input",  "L"),
    (11, "CP",    "input",  "L"),
    (3,  "D0",    "input",  "L"),
    (4,  "D1",    "input",  "L"),
    (7,  "D2",    "input",  "L"),
    (8,  "D3",    "input",  "L"),
    (13, "D4",    "input",  "L"),
    (14, "D5",    "input",  "L"),
    (17, "D6",    "input",  "L"),
    (18, "D7",    "input",  "L"),
    (2,  "Q0",    "output", "R"),
    (5,  "Q1",    "output", "R"),
    (6,  "Q2",    "output", "R"),
    (9,  "Q3",    "output", "R"),
    (12, "Q4",    "output", "R"),
    (15, "Q5",    "output", "R"),
    (16, "Q6",    "output", "R"),
    (19, "Q7",    "output", "R"),
    (10, "GND",   "power_in", "B"),
    (20, "VCC",   "power_in", "T"),
]

# 27C256 - EPROM 32Kx8 DIP-28
M27C256 = [
    (10, "A0",  "input", "L"), (9,  "A1",  "input", "L"),
    (8,  "A2",  "input", "L"), (7,  "A3",  "input", "L"),
    (6,  "A4",  "input", "L"), (5,  "A5",  "input", "L"),
    (4,  "A6",  "input", "L"), (3,  "A7",  "input", "L"),
    (25, "A8",  "input", "L"), (24, "A9",  "input", "L"),
    (21, "A10", "input", "L"), (23, "A11", "input", "L"),
    (2,  "A12", "input", "L"), (26, "A13", "input", "L"),
    (27, "A14", "input", "L"),
    (11, "D0", "tri_state", "R"), (12, "D1", "tri_state", "R"),
    (13, "D2", "tri_state", "R"), (15, "D3", "tri_state", "R"),
    (16, "D4", "tri_state", "R"), (17, "D5", "tri_state", "R"),
    (18, "D6", "tri_state", "R"), (19, "D7", "tri_state", "R"),
    (20, "~{CE}", "input", "R"), (22, "~{OE}", "input", "R"),
    (1,  "VPP", "input", "R"),
    (14, "GND", "power_in", "B"),
    (28, "VCC", "power_in", "T"),
]

# --------------------------------------------------------------------------
# Header 2x28 entre a placa principal (em pe) e a placa expansora (deitada).
# Mesma geometria de colunas do barramento: coluna c leva o pino c numa
# fileira e o pino 57-c na outra. As posicoes 5 e 52 (guia no conector de
# borda) nao existem no barramento e viram GND adicional entre as placas.
# --------------------------------------------------------------------------
HEADER_NETS = {}
for _p, _v in BUS.items():
    HEADER_NETS[_p] = _v[0]
HEADER_NETS[5] = "GND"
HEADER_NETS[52] = "GND"

assert len(HEADER_NETS) == 56, len(HEADER_NETS)
