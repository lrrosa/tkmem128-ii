# -*- coding: utf-8 -*-
"""Troca o footprint de J1 na placa principal PRESERVANDO o resto.

O esquematico e o posicionamento/serigrafia ajustados a mao continuam
intactos: so o footprint de J1 muda (header 2x28 -> soquete de borda) e o
cobre e apagado para ser reroteado.

  fase 1: python troca_j1.py limpar     remove cobre, zonas e o J1 antigo
  fase 2: python troca_j1.py colocar    insere o novo J1 com as nets
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from netlist import PROJ_DIR, PROJ_NAME, CONN, PLACE_PCB

REAL = "%s/%s.kicad_pcb" % (PROJ_DIR, PROJ_NAME)
LOCALFP = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/"
           "lib/tkmem128.pretty")
NOVO = "ZX_TK_Bus_Socket_56"
FASE = sys.argv[1]

b = pcbnew.LoadBoard(REAL)

if FASE == "limpar":
    pos = None
    for fp in b.GetFootprints():
        if fp.GetReference() == "J1":
            pos = (pcbnew.ToMM(fp.GetPosition().x),
                   pcbnew.ToMM(fp.GetPosition().y),
                   fp.GetOrientationDegrees())
    if pos is None:
        raise SystemExit("J1 nao encontrado")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "j1_pos.txt"), "w") as f:
        f.write("%.4f %.4f %.1f\n" % pos)
    print("J1 estava em (%.2f, %.2f) rot %.0f" % pos)

    alvos = list(b.GetTracks()) + list(b.Zones())
    for t in alvos:
        b.Remove(t)
    for fp in list(b.GetFootprints()):
        if fp.GetReference() == "J1":
            b.Remove(fp)
    pcbnew.SaveBoard(REAL, b)
    print("removidos: %d segmentos/zonas + o J1 antigo" % len(alvos))

elif FASE == "colocar":
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "j1_pos.txt")) as f:
        x, y, rot = [float(v) for v in f.read().split()]
    fp = pcbnew.FootprintLoad(LOCALFP, NOVO)
    if fp is None:
        raise SystemExit("footprint %s nao carregou" % NOVO)
    fp.SetReference("J1")
    fp.SetValue("Barramento TK")
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    if rot:
        fp.SetOrientationDegrees(rot)
    b.Add(fp)
    fp.SetLayerAndFlip(pcbnew.B_Cu)   # corpo do conector do lado do cobre
    nets = CONN["J1"]
    n = 0
    for pad in fp.Pads():
        nn = nets.get(pad.GetNumber())
        if not nn:
            continue
        item = b.FindNet(nn)
        if item is None:          # net ficou sem nenhuma ilha ao tirar o J1
            item = pcbnew.NETINFO_ITEM(b, nn)
            b.Add(item)
        pad.SetNet(item)
        n += 1
    pcbnew.SaveBoard(REAL, b)
    print("J1 recolocado em (%.2f, %.2f): %d ilhas com net" % (x, y, n))
