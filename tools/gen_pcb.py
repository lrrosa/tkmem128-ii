# -*- coding: utf-8 -*-
"""Cria a .kicad_pcb de uma das placas: contorno, footprints e nets.

  "C:/Program Files/KiCad/10.0/bin/python.exe" gen_pcb.py [netlist|netlist_exp]
"""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

BOARD = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "netlist")

KIFP = "C:/Program Files/KiCad/10.0/share/kicad/footprints"
LOCALFP = ("F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/"
           "lib/tkmem128.pretty")
OUT = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
W, H = BOARD.BOARD_W, BOARD.BOARD_H
CX = W / 2.0


def mm(v):
    return pcbnew.FromMM(float(v))


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def fp_path(lib):
    return LOCALFP if lib == "tkmem128" else "%s/%s.pretty" % (KIFP, lib)


def main():
    if not os.path.isdir(BOARD.PROJ_DIR):
        os.makedirs(BOARD.PROJ_DIR)
    board = pcbnew.NewBoard(OUT)
    board.SetCopperLayerCount(2)

    netmap = {}
    for name in sorted(BOARD.all_nets()):
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        netmap[name] = n

    for ref, lib_id, val, fp_full, descr in BOARD.PARTS:
        lib, fpname = fp_full.split(":")
        fp = pcbnew.FootprintLoad(fp_path(lib), fpname)
        if fp is None:
            raise RuntimeError("footprint nao carregou: %s" % fp_full)
        fp.SetReference(ref)
        fp.SetValue(val)
        x, y, rot = BOARD.PLACE_PCB[ref]
        fp.SetPosition(pt(x, y))
        if rot:
            fp.SetOrientationDegrees(rot)
        off = getattr(BOARD, "REF_OFFSET", {}).get(ref)
        if off:
            r = fp.Reference()
            r.SetPosition(pcbnew.VECTOR2I(mm(x + off[0]), mm(y + off[1])))
        board.Add(fp)
        pins = BOARD.CONN.get(ref, {})
        for pad in fp.Pads():
            nn = pins.get(pad.GetNumber())
            if nn:
                pad.SetNet(netmap[nn])

    # ----------------------------------------------------------- Edge.Cuts
    def edge(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(x1, y1))
        s.SetEnd(pt(x2, y2))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)

    edge(0, 0, W, 0)
    edge(W, 0, W, H)
    edge(0, 0, 0, H)
    if BOARD.KEYSLOT_COL is None:
        edge(0, H, W, H)
    else:
        kx = CX + (BOARD.KEYSLOT_COL - 14.5) * 2.54
        kw, kd = 0.9, 5.0
        edge(0, H, kx - kw, H)
        edge(kx - kw, H, kx - kw, H - kd)
        edge(kx - kw, H - kd, kx + kw, H - kd)
        edge(kx + kw, H - kd, kx + kw, H)
        edge(kx + kw, H, W, H)

    # ---------------------------------------------------------- serigrafia
    for s_, x, y, size, where in BOARD.SILK:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s_)
        t.SetPosition(pt(x, y))
        t.SetLayer(pcbnew.B_SilkS if where.startswith("B") else pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(0.15))
        if where.startswith("B"):
            t.SetMirrored(True)
        if where.endswith("90"):
            t.SetTextAngleDegrees(90)
        board.Add(t)

    # linhas de serigrafia opcionais: (x1, y1, x2, y2, camada)
    for x1, y1, x2, y2, where in getattr(BOARD, "LINES", []):
        ln = pcbnew.PCB_SHAPE(board)
        ln.SetShape(pcbnew.SHAPE_T_SEGMENT)
        ln.SetStart(pt(x1, y1))
        ln.SetEnd(pt(x2, y2))
        ln.SetLayer(pcbnew.B_SilkS if where == "B" else pcbnew.F_SilkS)
        ln.SetWidth(mm(0.2))
        board.Add(ln)

    pcbnew.SaveBoard(OUT, board)
    print("escrito:", OUT)
    print("footprints:", len(BOARD.PARTS), " nets:", len(netmap),
          " placa: %.2f x %.2f mm" % (W, H))


if __name__ == "__main__":
    main()
