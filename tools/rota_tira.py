# -*- coding: utf-8 -*-
"""Roteia a tira de expansao a mao: 54 retas verticais, sem via nenhuma.

Por que nao usar o autorouter aqui: a tira nao tem problema de roteamento.
J1 e J2 estao nas MESMAS colunas e cada pino fica na MESMA face nos dois
(F.Cu = 29..56, B.Cu = 1..28). Entao cada rede e um segmento vertical de x
constante, e nao existe um unico cruzamento na placa. O Freerouting nao sabe
disso e produziu 53 vias, 82% do cobre numa face so e trilhas de 0,25 mm.

Trilha de 1,5 mm no passo de 2,54 deixa 1,04 mm de vao entre vizinhas — e a
largura maxima "limpa", porque os dedos de J2 tem 1,524 mm. Suporta ~3,5 A
(1 oz, 10 C de elevacao), o que importa numa placa que alimenta uma cascata de
perifericos.

Sem plano de terra: com as verticais ocupando as duas faces inteiras, um plano
so existiria em fiapos de 1 mm entre trilhas — inutil como retorno e util
apenas para criar acoplamento. Trilha grossa e direta vale mais.

  "C:/Program Files/KiCad/10.0/bin/python.exe" rota_tira.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist_exp as TIRA

LARG = 1.5
REAL = "%s/%s.kicad_pcb" % (TIRA.PROJ_DIR, TIRA.PROJ_NAME)
b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM

# ---- limpa o que o autorouter deixou ---------------------------------------
velhos = list(b.GetTracks())
for t in velhos:
    b.Remove(t)
zonas = list(b.Zones())
for z in zonas:
    b.Remove(z)

# ---- regras de projeto ------------------------------------------------------
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = fmm(0.5)
ds.m_MinClearance = fmm(0.25)

# ---- as 54 retas ------------------------------------------------------------
pads = {}
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in ("J1", "J2"):
        for p in fp.Pads():
            pads[(r, int(p.GetNumber()))] = p

feitos, torto = 0, []
for (r, n), p in sorted(pads.items()):
    if r != "J1":
        continue
    a, c = p, pads[("J2", n)]
    xa, ya = mm(a.GetPosition().x), mm(a.GetPosition().y)
    xc, yc = mm(c.GetPosition().x), mm(c.GetPosition().y)
    if abs(xa - xc) > 0.001:
        torto.append((n, xa, xc))
        continue
    camada = pcbnew.F_Cu if a.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    if not c.IsOnLayer(camada):
        torto.append((n, "faces diferentes"))
        continue
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(fmm(xa), fmm(ya)))
    t.SetEnd(pcbnew.VECTOR2I(fmm(xc), fmm(yc)))
    t.SetWidth(fmm(LARG))
    t.SetLayer(camada)
    t.SetNetCode(a.GetNetCode())
    b.Add(t)
    feitos += 1

if torto:
    raise SystemExit("nem toda rede e uma reta: %s" % torto[:5])

# ---- C1 sai; entra o link de fio do GND ------------------------------------
# Numa placa de passagem com ilhas presas a uma face, cada coluna carrega redes
# diferentes nas duas faces: ilha PASSANTE fora da coluna da guia e curto.
# C1 era THT. E mesmo em SMD nao caberia — BUS_9V (x=66,04) fica entre o +5V
# (68,58) e o GND mais proximo (60,96), com as duas faces ocupadas.
for fp in list(b.GetFootprints()):
    if fp.GetReference() == "C1":
        b.Remove(fp)
        print("C1 removida da placa")

lib, nome = TIRA.WIRELINK[0].split(":")
rede, lx, ly = TIRA.WIRELINK[1], TIRA.WIRELINK[2], TIRA.WIRELINK[3]
for fp in list(b.GetFootprints()):
    if fp.GetFPIDAsString().endswith(nome):
        b.Remove(fp)
link = pcbnew.FootprintLoad(
    "F:/downloads/_montagens - kits/TKMem128/tkmem128-kicad/hardware/lib/"
    "tkmem128.pretty", nome)
link.SetReference("W1")
link.SetPosition(pcbnew.VECTOR2I(fmm(lx), fmm(ly)))
b.Add(link)
codigo = b.GetNetcodeFromNetname(rede)
for p in link.Pads():
    p.SetNetCode(codigo)
alvo = (60.96, 40.64)          # colunas dos pinos 6 e 14, ambos GND
# as ilhas do link caem exatamente sobre as duas verticais de GND: sem coto
print("link de GND em x=%.2f e %.2f (pinos 6 e 14), fio isolado por cima"
      % alvo)

pcbnew.SaveBoard(REAL, b)

por_face = {}
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    d = ((mm(s.x) - mm(e.x)) ** 2 + (mm(s.y) - mm(e.y)) ** 2) ** .5
    por_face[b.GetLayerName(t.GetLayer())] = por_face.get(
        b.GetLayerName(t.GetLayer()), 0) + d
print("%d trilhas de %.1f mm, %d vias, %d zonas"
      % (feitos, LARG, sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA"),
         len(list(b.Zones()))))
print("cobre por face (mm):", {k: round(v, 1) for k, v in por_face.items()})
print("removidos: %d tracos e %d zonas do autorouter" % (len(velhos), len(zonas)))
print("gravado:", REAL)
