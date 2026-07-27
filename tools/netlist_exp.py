# -*- coding: utf-8 -*-
"""Placa expansora da TKMEM-128: soquete de borda + header + dedos de passagem.

Fica deitada, saindo pela base da caixa. Liga o TK90X/TK95 a placa principal
(que fica em pe dentro da caixa) e ainda oferece passagem para outros
perifericos. Tudo 1:1, sem logica.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS, HEADER_NETS

PROJ_NAME = "tkmem128-expansor"
PROJ_DIR = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/"
            "expansor")
BOARD_W, BOARD_H = 78.74, 70.0
KEYSLOT_COL = 5             # rasgo da guia nos dedos de J2
SHEET = "A2"
TITLE = "TKMEM-128 KiCad - placa expansora do barramento TK90X/TK95"

PARTS = [
    ("J1", "tkmem128:ZX_TK_Bus_56", "Barramento TK",
     "tkmem128:ZX_TK_Bus_Socket_56",
     "Soquete de borda femea 56 vias - encaixa nos dedos do TK90X/TK95"),
    ("J2", "tkmem128:ZX_TK_Bus_56", "Passagem",
     "tkmem128:ZX_TK_Bus_Fingers_56",
     "Dedos de borda 56 vias - passagem do barramento a outros perifericos"),
    ("J3", "tkmem128:ZX_TK_Bus_Header_56", "Para a placa principal",
     "tkmem128:ZX_TK_Bus_Header_2x28",
     "Header macho 2x28 vertical - recebe a placa principal em pe"),
    ("C1", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     "Desacoplamento na entrada de alimentacao"),
]

CONN = {
    "J1": {str(p): BUS[p][0] for p in BUS},
    "J2": {str(p): BUS[p][0] for p in BUS},
    "J3": {str(p): HEADER_NETS[p] for p in HEADER_NETS},
    "C1": {"1": "+5V", "2": "GND"},
}

PLACE_SCH = {"J1": (58, 200), "J2": (200, 200), "J3": (340, 200)}
SCH_DISC_ORIGIN = (450, 60)

PLACE_PCB = {
    # eixo Y = eixo de 32 mm da caixa. Soquete e dedos precisam sobrar para
    # fora da caixa; o header fica no meio, sob a placa principal.
    "J1": (39.37, 6.0, 0),        # soquete de borda -> lado do TK
    "J3": (39.37, 35.0, 0),       # header -> recebe a placa principal em pe
    "J2": (39.37, 66.19, 0),      # dedos -> passagem a outros perifericos
    "C1": (6.0, 45.0, 0),
}

# paredes da caixa Patola PB-085/3 (32 mm) centradas no header
LINES = [
    (3.0, 19.0, 75.7, 19.0, "F"),
    (3.0, 51.0, 75.7, 51.0, "F"),
]

REF_OFFSET = {"J3": (0.0, 5.0), "C1": (2.5, 3.0)}

SILK = [
    ("TKMEM-128  EXPANSOR DO BARRAMENTO", 39.37, 27.0, 1.1, "F"),
    ("TK90X / TK95", 39.37, 29.5, 1.0, "F"),
    ("<- TK", 8.0, 15.0, 1.2, "F"),
    ("PLACA PRINCIPAL AQUI", 39.37, 31.8, 0.9, "F"),
    ("J3: 5 e 52 = GND", 62.0, 39.0, 0.9, "F"),
    ("PASSAGEM ->", 60.0, 55.0, 1.2, "F"),
    ("parede da caixa", 20.0, 17.6, 0.85, "F"),
    ("parede da caixa", 20.0, 52.8, 0.85, "F"),
    ("CERN-OHL-S v2  |  github.com/lrrosa/tkmem128-kicad", 39.37, 44.0, 0.9, "B"),
    ("Derivado de Velesoft 2009 e Luccas Eletronica 2012", 39.37, 47.0, 0.9, "B"),
]


def all_nets():
    nets = {}
    for ref, pins in CONN.items():
        for pin, net in pins.items():
            nets.setdefault(net, []).append((ref, pin))
    return nets


if __name__ == "__main__":
    nets = all_nets()
    print("componentes: %d   nets: %d" % (len(PARTS), len(nets)))
    print("nets com 1 pino:", [n for n, v in nets.items() if len(v) < 2])
