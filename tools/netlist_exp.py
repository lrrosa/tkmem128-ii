# -*- coding: utf-8 -*-
"""Tira de expansao da TKMEM-128.

Arquitetura confirmada em fotos de perifericos reais do TK:

  - o conector de borda (TE 5645235) e soldado DIRETAMENTE na placa principal,
    que fica EM PE. Como o conector e de entrada vertical, a fenda dele cai no
    plano horizontal e recebe o cartao do TK;
  - os terminais do conector atravessam a placa principal e sobram ~3,18 mm do
    outro lado;
  - esta tira encosta nesses terminais e e soldada neles. Ela tem apenas
    ilhas de solda de um lado e dedos de borda do outro. Nenhum conector.

Resultado: a tira fica coplanar com o cartao do TK e com a fenda do conector —
degrau zero na corrente de perifericos.

O lado dos componentes da placa principal fica virado para ESTA tira, nunca
para o lado do conector: senao a placa dentro da caixa esbarra no micro.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS

PROJ_NAME = "tkmem128-expansor"
PROJ_DIR = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/"
            "expansor")
BOARD_W, BOARD_H = 78.74, 45.0
KEYSLOT_COL = 5             # rasgo da guia nos dedos de J2
EDGE_PADS_TOP = True        # as ilhas de J1 chegam ate a aresta y=0
SHEET = "A3"
TITLE = "TKMEM-128 KiCad - tira de expansao do barramento TK90X/TK95"

PARTS = [
    ("J1", "tkmem128:ZX_TK_Bus_56", "Terminais do conector",
     "tkmem128:ZX_TK_Bus_SolderPads_56",
     "Ilhas de solda nos terminais do conector de borda que atravessam a "
     "placa principal"),
    ("J2", "tkmem128:ZX_TK_Bus_56", "Passagem",
     "tkmem128:ZX_TK_Bus_Fingers_56",
     "Dedos de borda 56 vias - passagem do barramento a outros perifericos"),
    ("C1", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     "Desacoplamento junto ao ponto de alimentacao"),
]

CONN = {
    "J1": {str(p): BUS[p][0] for p in BUS},
    "J2": {str(p): BUS[p][0] for p in BUS},
    "C1": {"1": "+5V", "2": "GND"},
}

PLACE_SCH = {"J1": (70, 190), "J2": (250, 190)}
SCH_DISC_ORIGIN = (360, 60)

PLACE_PCB = {
    "J1": (39.37, 2.5, 0),        # ilhas comecam na borda (y=0) e entram 5 mm
    "J2": (39.37, 41.19, 0),      # dedos: passagem a outros perifericos
    "C1": (6.0, 20.0, 0),
}

REF_OFFSET = {"C1": (2.5, 3.0)}

LINES = [
    # parede de tras da caixa Patola PB-085/3, com a placa principal rente
    # a face interna da frente
    (3.0, 30.0, 75.7, 30.0, "F"),
]

SILK = [
    ("TKMEM-128  TIRA DE EXPANSAO DO BARRAMENTO", 39.37, 15.0, 1.1, "F"),
    ("TK90X / TK95", 39.37, 17.5, 1.0, "F"),
    ("ilhas ate a borda: servem para terminal curto ou longo",
     39.37, 10.0, 0.8, "F"),
    ("parede de tras da caixa", 20.0, 28.6, 0.85, "F"),
    ("PASSAGEM ->", 60.0, 34.0, 1.2, "F"),
    ("CERN-OHL-S v2  |  github.com/lrrosa/tkmem128-kicad", 39.37, 22.0, 0.9, "B"),
    ("Derivado de Velesoft 2009 e Luccas Eletronica 2012", 39.37, 25.0, 0.9, "B"),
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
