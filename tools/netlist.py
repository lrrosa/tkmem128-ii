# -*- coding: utf-8 -*-
"""Netlist completa da TKMEM-128 KiCad (fonte unica da verdade)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS, HEADER_NETS

# (ref, lib_id, valor, footprint, descricao)
PARTS = [
    ("J1", "tkmem128:ZX_TK_Bus_Header_56", "Barramento TK",
     "tkmem128:ZX_TK_Bus_Socket_56",
     "Conector de borda TE 5645235 soldado nesta placa. O corpo fica do lado "
     "OPOSTO aos componentes; os terminais atravessam e recebem a tira de "
     "expansao pelo lado dos componentes."),
    ("U1", "tkmem128:GAL20V8B_TKMEM", "GAL20V8B",
     "Package_DIP:DIP-24_W7.62mm_Socket_LongPads",
     "Decodificador de enderecos (GAL20V8B ou ATF20V8B)"),
    ("U2", "tkmem128:74HCT273", "74HCT273",
     "Package_DIP:DIP-20_W7.62mm_Socket_LongPads",
     "Latch da porta 0x7FFD"),
    ("U3", "tkmem128:SRAM_DIP32_1M_4M", "AS6C1008-55PCN",
     "Package_DIP:DIP-32_W15.24mm_Socket_LongPads",
     "SRAM 128Kx8 (ou AS6C4008 512Kx8 no modo ZX512)"),
    ("U4", "tkmem128:M27C256", "27C256",
     "Package_DIP:DIP-28_W15.24mm_Socket_LongPads",
     "EPROM opcional com o par de ROMs do Spectrum 128"),
]

# ligacoes: ref -> {numero_do_pino: net}
CONN = {}

# ------------------------------------- J1: header para a placa expansora
CONN["J1"] = {str(p): HEADER_NETS[p] for p in HEADER_NETS}

# ------------------------------------------------------------------ U1 GAL
CONN["U1"] = {
    "1": "MREQ_N", "2": "ZX512", "3": "A1", "4": "WR_N", "5": "DIS128",
    "6": "BANK2", "7": "A5", "8": "BANK0", "9": "BANK4", "10": "BANK3",
    "11": "BANK1", "12": "GND", "13": "A15", "14": "A14",
    "15": "ROMCS_N", "16": "CLK7FFD", "17": "SA18", "18": "SA17_CE2",
    "19": "RAMCS_N", "20": "SA16", "21": "SA15", "22": "SA14",
    "23": "IORQ_N", "24": "+5V",
}

# ------------------------------------------------- U2 74HCT273 (porta 7FFD)
# bit N do 7FFD -> flip-flop N (ordem natural, ao contrario do original)
CONN["U2"] = {
    "1": "RESET_N", "11": "CLK7FFD", "10": "GND", "20": "+5V",
    "3": "D0", "2": "BANK0",     # bit 0
    "4": "D1", "5": "BANK1",     # bit 1
    "7": "D2", "6": "BANK2",     # bit 2
    "8": "D3", "9": "VRAM",      # bit 3  (shadow screen - nao usado)
    "13": "D4", "12": "ROMA14",  # bit 4  (selecao de ROM)
    "14": "D5", "15": "DIS128",  # bit 5  (trava de paginacao)
    "17": "D6", "16": "BANK3",   # bit 6  (extensao 512K)
    "18": "D7", "19": "BANK4",   # bit 7  (extensao 512K)
}

# ----------------------------------------------------------------- U3 SRAM
CONN["U3"] = {
    "12": "A0", "11": "A1", "10": "A2", "9": "A3", "8": "A4", "7": "A5",
    "6": "A6", "5": "A7", "27": "A8", "26": "A9", "23": "A10", "25": "A11",
    "4": "A12", "28": "A13",
    "3": "SA14", "31": "SA15", "2": "SA16", "30": "SA17_CE2", "1": "SA18",
    "13": "D0", "14": "D1", "15": "D2", "17": "D3", "18": "D4", "19": "D5",
    "20": "D6", "21": "D7",
    "22": "RAMCS_N", "24": "RD_N", "29": "WR_N",
    "16": "GND", "32": "+5V",
}

# ---------------------------------------------------------------- U4 EPROM
# Enderecos e dados OBRIGATORIAMENTE 1:1 (o conteudo da ROM e fixo).
CONN["U4"] = {
    "10": "A0", "9": "A1", "8": "A2", "7": "A3", "6": "A4", "5": "A5",
    "4": "A6", "3": "A7", "25": "A8", "24": "A9", "21": "A10", "23": "A11",
    "2": "A12", "26": "A13", "27": "ROMA14",
    "11": "D0", "12": "D1", "13": "D2", "15": "D3", "16": "D4", "17": "D5",
    "18": "D6", "19": "D7",
    "20": "ROMCE_N", "22": "RD_N",
    "1": "+5V", "14": "GND", "28": "+5V",
}

# ------------------------------------------------- passivos, jumpers, LED
DISCRETE = [
    # (ref, lib_id, valor, footprint, {pino: net}, descricao)
    ("R2", "Device:R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical",
     {"1": "+5V", "2": "ZX512"}, "Pull-up do modo ZX128/ZX512"),
    ("R3", "Device:R", "2k2", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical",
     {"1": "+5V", "2": "LED_A"}, "Limitador do LED de energia (opcional)"),
    ("R4", "Device:R", "1k", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical",
     {"1": "+5V", "2": "RAMDIS"}, "Pull-up de auto-desativacao da RAM interna do TK, no pino 29"),
    ("R5", "Device:R", "0R", "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical",
     {"1": "ROMCS_DRV", "2": "ROMCS_BUS"}, "Serie do ROMCS (0R; 100-470R se houver disputa)"),
    ("C1", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     {"1": "+5V", "2": "GND"}, "Desacoplamento U1"),
    ("C2", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     {"1": "+5V", "2": "GND"}, "Desacoplamento U2"),
    ("C3", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     {"1": "+5V", "2": "GND"}, "Desacoplamento U3"),
    ("C4", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     {"1": "+5V", "2": "GND"}, "Desacoplamento U4"),
    ("C5", "Device:C", "100n", "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
     {"1": "+5V", "2": "GND"}, "Desacoplamento do conector"),
    ("C6", "Device:C_Polarized", "10u",
     "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
     {"1": "+5V", "2": "GND"}, "Reservatorio de entrada"),
    ("D1", "Device:LED", "LED", "LED_THT:LED_D3.0mm",
     {"2": "LED_A", "1": "GND"}, "LED de energia (opcional)"),
    ("JP1", "Connector_Generic:Conn_01x03", "SELECIONA ROM",
     "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     {"1": "ROMCS_N", "2": "ROMCE_N", "3": "+5V"},
     "1-2 = ROM 128 (EPROM ativa) | 2-3 = ROM TK (EPROM desligada)"),
    ("JP2", "Connector_Generic:Conn_01x03", "ROMCS BARRAMENTO",
     "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     {"1": "ROMCS_N", "2": "ROMCS_DRV", "3": "+5V"},
     "Aberto = ROM do TK | 1-2 = aciona ROMCS pelo GAL | 2-3 = ROMCS fixo em 1"),
    ("JP3", "Connector_Generic:Conn_01x02", "ZX128/ZX512",
     "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
     {"1": "ZX512", "2": "GND"},
     "Aberto = 128K (AS6C1008) | Fechado = 512K (AS6C4008)"),
    ("TP1", "Connector_Generic:Conn_01x01", "VRAM",
     "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm",
     {"1": "VRAM"}, "Bit 3 do 7FFD (shadow screen), sem uso nesta arquitetura"),
    ("TP2", "Connector_Generic:Conn_01x01", "CLK7FFD",
     "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm",
     {"1": "CLK7FFD"}, "Clock do latch - trava em 1 quando DIS128 e setado"),
]



for ref, lib, val, fp, conns, descr in DISCRETE:
    PARTS.append((ref, lib, val, fp, descr))
    CONN[ref] = conns


PROJ_NAME = "tkmem128"
PROJ_DIR = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware")
BOARD_W, BOARD_H = 78.74, 66.04
# As ilhas de J1 chegam a 0,51 mm da aresta de baixo — de proposito, e o conector
# de borda. A placa-isca do roteador nao pode recuar essa aresta: recuando 0,35
# ela passa a 0,16 mm das ilhas e o Freerouting acusa 54 violacoes (uma por
# ilha) antes mesmo de rotear o primeiro fio.
EDGE_PADS_BOTTOM = True
KEYSLOT_COL = None          # placa principal nao tem dedos, logo nao tem guia
SHEET = "A2"
TITLE = "TKMEM-128 KiCad - placa principal (128K/512K para TK90X/TK95)"

# posicionamento no esquematico
PLACE_SCH = {
    "J1": (58, 200), "U1": (200, 108), "U2": (200, 262),
    "U3": (330, 112), "U4": (330, 292),
}
SCH_DISC_ORIGIN = (470, 40)

# posicionamento na PCB (pino 1 nos DIP, centro nos conectores)
PLACE_PCB = {
    "J1": (39.37, 62.23, 0),
    "U3": (6.35, 5.08, 0),
    "U4": (26.67, 7.62, 0),
    "U1": (46.99, 10.16, 0),
    "U2": (59.69, 12.70, 0),
    "C3": (4.0, 47.2, 0),
    "C4": (12.0, 47.2, 0),
    "C1": (20.0, 47.2, 0),
    "C2": (28.0, 47.2, 0),
    "C5": (36.0, 47.2, 0),
    "C6": (44.0, 47.2, 0),
    "D1": (52.0, 47.2, 0),
    "TP1": (60.0, 47.2, 0),
    "TP2": (64.0, 47.2, 0),
    "R2": (5.0, 53.3, 0),
    "R4": (11.0, 53.3, 0),
    "R5": (17.0, 53.3, 0),
    "R3": (23.0, 53.3, 0),
    "JP1": (71.5, 8.0, 0),
    "JP2": (71.5, 17.0, 0),
    "JP3": (71.5, 26.0, 0),
}

REF_OFFSET = {}

SILK = [
    ("5 e 52 = GND", 60.0, 58.5, 0.9, "F"),
    ("TKMEM-128", 52.0, 51.0, 1.6, "F"),
    ("KiCad v1.0", 52.0, 53.5, 1.1, "F"),
    ("JP1  1-2 = ROM 128   |   2-3 = ROM do TK", 39.37, 8.0, 1.0, "B"),
    ("JP2  aberto = ROM do TK  |  1-2 = pelo GAL  |  2-3 = +5V", 39.37, 11.0, 1.0, "B"),
    ("JP3  fechado = 512K (AS6C4008)", 39.37, 14.0, 1.0, "B"),
    ("JP4  fechado = auto-desativa a RAM de 32K do TK", 39.37, 17.0, 1.0, "B"),
    ("     NAO feche JP4 em ZX Spectrum: o pino 17 la e o V do video", 39.37, 19.5, 0.85, "B"),
    ("SJ1 e SJ2 sao terra extra, opcionais - podem ficar abertos", 39.37, 22.5, 0.9, "B"),
    ("SJ1  fechar SO em ZX Spectrum (pino 7 = GND la)", 39.37, 25.0, 0.9, "B"),
    ("SJ2  fechar SO em TK90X/TK95 (pino 15 = GND la)", 39.37, 27.5, 0.9, "B"),
    ("CERN-OHL-S v2", 39.37, 32.0, 1.3, "B"),
    ("github.com/lrrosa/tkmem128-kicad", 39.37, 35.0, 1.0, "B"),
    ("Derivado de Velesoft 2009 e Luccas Eletronica 2012", 39.37, 38.0, 0.9, "B"),
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
    solo = [n for n, v in nets.items() if len(v) < 2]
    print("nets com menos de 2 pinos:", solo)
    for n in sorted(nets):
        print("  %-12s %s" % (n, " ".join("%s.%s" % x for x in sorted(nets[n]))))
