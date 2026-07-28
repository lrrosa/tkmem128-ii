# -*- coding: utf-8 -*-
"""Poe toda a serigrafia em negrito, do mesmo jeito que o KiCad faz na mao.

Serigrafia de PCB e impressa com tinta que espalha um pouco e depois e lida a
olho nu, muitas vezes com o CI ja soquetado por cima. Negrito ajuda de verdade.

O KiCad, ao marcar negrito, engrossa o traco para 0,2 x o tamanho da fonte
(contra 0,15 no normal) — e essa proporcao, nao uma espessura fixa, que mantem
texto grande e pequeno com o mesmo peso visual. O script reproduz isso.

Pega texto de nivel de placa, campos visiveis de footprint (referencias) e
texto grafico de footprint, so em F.SilkS/B.SilkS.

  "C:/Program Files/KiCad/10.0/bin/python.exe" silk_negrito.py [netlist ...]
"""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

RAZAO = 0.2                      # espessura / tamanho, a mesma do KiCad
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM


def silk(b):
    for d in b.GetDrawings():
        if d.GetClass() == "PCB_TEXT" and d.GetLayer() in SILK:
            yield d
    for fp in b.GetFootprints():
        for f in fp.GetFields():
            if f.GetLayer() in SILK and f.IsVisible():
                yield f
        for it in fp.GraphicalItems():
            if it.GetClass() == "PCB_TEXT" and it.GetLayer() in SILK:
                yield it


for nome in (sys.argv[1:] or ["netlist", "netlist_exp"]):
    BOARD = importlib.import_module(nome)
    caminho = "%s/%s.kicad_pcb" % (BOARD.PROJ_DIR, BOARD.PROJ_NAME)
    b = pcbnew.LoadBoard(caminho)
    mudados = []
    for t in silk(b):
        alvo = round(mm(t.GetTextWidth()) * RAZAO, 3)
        if t.IsBold() and abs(mm(t.GetTextThickness()) - alvo) < 0.001:
            continue
        mudados.append(t.GetText().splitlines()[0][:22])
        t.SetBold(True)
        t.SetTextThickness(fmm(alvo))
    pcbnew.SaveBoard(caminho, b)
    print("%-22s %d de %d textos ajustados" % (BOARD.PROJ_NAME, len(mudados),
                                               sum(1 for _ in silk(b))))
    if mudados:
        print("   ", ", ".join(sorted(mudados)))
