# -*- coding: utf-8 -*-
"""Cria os dois planos internos da placa principal de 4 camadas.

  F.Cu    sinal
  In1.Cu  plano de GND inteiro
  In2.Cu  plano de +5V inteiro
  B.Cu    sinal

Todos os componentes sao passantes, entao cada ilha de +5V e de GND toca o seu
plano diretamente — nao e preciso rotear alimentacao nenhuma nas camadas de
sinal, nem por via. E o ganho real das 4 camadas: as duas faces de sinal ficam
so para sinal.

Roda depois de apagar as trilhas, antes de exportar o DSN — o roteador precisa
ver os planos para saber que +5V e GND ja estao ligados.

  "C:/Program Files/KiCad/10.0/bin/python.exe" planos_4camadas.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
RECUO = 0.3                      # do contorno da placa
PLANOS = ((pcbnew.In1_Cu, "GND"), (pcbnew.In2_Cu, "+5V"))

b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM

if len(list(b.Zones())):
    raise SystemExit("ja ha zonas na placa; apague antes de recriar")

x1, y1 = RECUO, RECUO
x2, y2 = PRINC.BOARD_W - RECUO, PRINC.BOARD_H - RECUO

for camada, rede in PLANOS:
    z = pcbnew.ZONE(b)
    z.SetLayer(camada)
    z.SetNetCode(b.GetNetcodeFromNetname(rede))
    z.SetIsFilled(True)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetLocalClearance(fmm(0.3))
    z.SetMinThickness(fmm(0.25))
    pts = z.Outline()
    pts.NewOutline()
    for px, py in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        pts.Append(fmm(px), fmm(py))
    b.Add(z)
    print("plano de %-4s em %s" % (rede, b.GetLayerName(camada)))

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(REAL, b)
print("preenchidos %d planos, %.1f x %.1f mm"
      % (len(list(b.Zones())), x2 - x1, y2 - y1))
