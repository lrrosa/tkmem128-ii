# -*- coding: utf-8 -*-
"""Reposiciona a placa principal para roteamento, nao para estetica.

O que estava errado no arranjo anterior:

  y  5..43   os quatro CIs, todos VERTICAIS, lado a lado
  y 47,2     C3 C4 C1 C2 C5 C6 D1 TP1 TP2   fileira de x=4 a x=64
  y 53,3     R2 R4 R5 R3 SJ1 SJ2            fileira de x=5 a x=37
  y 60..65   conector

Duas fileiras de passivos atravessando a placa de lado a lado, entre o conector
e os CIs — exatamente por onde passam A0..A13 e D0..D7. E os cinco capacitores
de desacoplamento a 40 mm dos pinos de alimentacao que deveriam desacoplar, o
que alem de atrapalhar o roteamento nao desacopla coisa nenhuma.

Com CI VERTICAL os 16 pinos de um lado ficam empilhados numa reta de 38 mm, e
todo sinal que vem do conector (embaixo) precisa subir por um canal estreito ao
lado do CI e depois virar. Com CI HORIZONTAL a fileira de pinos fica paralela ao
conector e cada sinal sobe quase reto — e o que a placa Luccas faz, e e por isso
que as trilhas dela podem ser gordas.

Arranjo novo:

  y  4..19   U4 EPROM (horizontal)      |  JP1..JP4, R*, SJ*, D1, TP*
  y 27..42   U3 SRAM  (horizontal)      |  U1 GAL (y 27..35) / U2 273 (y 40..48)
  y 48..57   corredor limpo de ponta a ponta ate o conector
  y 60..65   conector

Cada capacitor de desacoplamento vai colado no pino de +5V do seu CI.

  "C:/Program Files/KiCad/10.0/bin/python.exe" repoe_principal.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlist as PRINC

REAL = "%s/%s.kicad_pcb" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
b = pcbnew.LoadBoard(REAL)
mm, fmm = pcbnew.ToMM, pcbnew.FromMM
fps = {f.GetReference(): f for f in b.GetFootprints()}

# SJ1 e SJ2 saem do projeto. Eram terra extra OPCIONAL em pinos que so sao GND
# numa das maquinas (7 no ZX Spectrum, 15 no TK), a documentacao ja mandava
# deixar os dois abertos, e cada um puxava uma rede do conector ate o outro lado
# da placa. Quem quiser o terra extra solda um fio do pino do conector ao plano.
# JP4 tambem sai: a auto-desativacao passou do pino 17 (V do video componente no
# ZX Spectrum) para o pino 29, que e N.C. nas duas maquinas. Sem risco, o
# pull-up pode ser permanente e nao ha mais o que fechar errado.
REMOVER = ("SJ1", "SJ2", "JP4")

# ref -> (rotacao, canto superior esquerdo das ILHAS)
ANCORA = {
    # Memorias empurradas para a esquerda e logica para a direita: o canal
    # vertical entre elas era de 2,8 mm e e por onde passa tudo que vem do lado
    # direito do conector. Agora tem 5,3 mm.
    # Tentei tambem centrar a SRAM (o conector traz A0..A3 pela direita e
    # A4..A7 pela esquerda, mas na memoria sao pinos consecutivos, entao um
    # grupo sempre atravessa a placa). Centrar equilibra as distancias mas
    # empurra GAL e 273 para o alto e cria congestionamento novo: 6 nets em
    # aberto contra 4 deste arranjo. Ficou este.
    "U4": (90, 2.50, 4.00),      # EPROM 27C256    33,02 x 15,24
    "U3": (90, 2.50, 27.00),     # SRAM 128K x 8   38,10 x 15,24
    "U1": (90, 47.50, 27.00),    # GAL 20V8        27,94 x 7,62
    "U2": (90, 50.00, 40.50),    # 74HCT273        22,86 x 7,62
}
# ref -> (rotacao, posicao da origem) para o que e pequeno
SOLTOS = {
    "JP1": (0, 46.50, 4.00), "JP2": (0, 55.00, 4.00),
    "JP3": (0, 63.50, 4.00),
    "R2": (0, 46.50, 14.50),
    "R5": (0, 57.50, 14.50), "R3": (0, 63.00, 14.50),

    "D1": (0, 46.50, 19.50), "TP1": (0, 52.00, 19.50),
    "TP2": (0, 56.00, 19.50),
    "C5": (0, 60.00, 52.00),     # no corredor, junto do +5V do conector
    "C6": (0, 68.00, 52.00),     # reservatorio, idem
}
# Tentei por SJ1/SJ2/JP4/R4 na coluna do proprio pino de barramento, junto ao
# conector: a distancia caiu, mas eles viraram obstaculo no meio do corredor de
# leque e o roteador passou de 4 para 8 nets em aberto. Ficam no alto; as duas
# ligacoes longas se fecham a mao.
# R4 vai para o canto baixo ESQUERDO: o pino 29 fica na coluna x=5,08 (fileira
# de cima do conector, y=59,80). Deixar R4 no alto a direita fazia a rede RAMDIS
# atravessar a placa na diagonal inteira — com o pino 17 ela andava menos da
# metade disso.
SOLTOS.update({
    "R4":  (0, 4.00, 52.50),
})

# Desacoplamento colado no pino de +5V do CI. U4 (pino 1) e U3 (pino 32) tem o
# +5V na MESMA coluna x=4,80, um em y=20,44 e outro em y=28,20: C3 entre os dois
# atende os dois com trilha curta.
SOLTOS.update({
    "C3": (0, 3.30, 24.00),      # entre o +5V de U4 e o de U3
    "C4": (0, 12.00, 24.00),     # reforco na mesma faixa
    "C1": (0, 48.30, 23.50),     # 4,7 mm do +5V de U1 (GAL)
    "C2": (0, 47.30, 53.00),     # U2 + reservatorio no corredor
    "C5": (0, 58.00, 53.00),
    "C6": (0, 68.00, 55.00),
})


def ilhas_bbox(fp):
    xs, ys = [], []
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
        ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
    return min(xs), min(ys), max(xs), max(ys)


def poe_por_bbox(fp, rot, x0, y0):
    """Gira e depois translada ate o canto das ilhas cair em (x0, y0)."""
    fp.SetOrientationDegrees(rot)
    ax, ay, _, _ = ilhas_bbox(fp)
    o = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(fmm(mm(o.x) + x0 - ax),
                                   fmm(mm(o.y) + y0 - ay)))


for ref, (rot, x0, y0) in ANCORA.items():
    poe_por_bbox(fps[ref], rot, x0, y0)
for ref, (rot, x, y) in SOLTOS.items():
    fps[ref].SetOrientationDegrees(rot)
    fps[ref].SetPosition(pcbnew.VECTOR2I(fmm(x), fmm(y)))

# ---- serigrafia de nivel de placa acompanha o CI ---------------------------
SEGUE = {"27C256": "U4", "AS6C1008-55PCN / AS6C4008-55PCN": "U3",
         "ATF20V8B": "U1", "74HCT273": "U2"}
for d in b.GetDrawings():
    if d.GetClass() != "PCB_TEXT":
        continue
    t = d.GetText()
    if t in SEGUE:
        x1, y1, x2, y2 = ilhas_bbox(fps[SEGUE[t]])
        d.SetTextAngleDegrees(0)
        d.SetPosition(pcbnew.VECTOR2I(fmm((x1 + x2) / 2.0), fmm(y2 + 2.2)))

# ---- confere sobreposicao de corpos ----------------------------------------
caixas = []
for ref, fp in fps.items():
    if ref == "J1":
        continue
    caixas.append((ref,) + ilhas_bbox(fp))
choques = []
for i in range(len(caixas)):
    for j in range(i + 1, len(caixas)):
        a, b_ = caixas[i], caixas[j]
        if (a[1] < b_[3] and b_[1] < a[3] and a[2] < b_[4] and b_[2] < a[4]):
            choques.append("%s x %s" % (a[0], b_[0]))
print("posicionado. sobreposicoes:", choques if choques else "nenhuma")
for ref in ("U4", "U3", "U1", "U2"):
    x1, y1, x2, y2 = ilhas_bbox(fps[ref])
    print("  %-3s x %5.2f..%5.2f  y %5.2f..%5.2f" % (ref, x1, x2, y1, y2))
# ---- limpa o roteamento e sobe as regras -----------------------------------
for t in list(b.GetTracks()):
    b.Remove(t)
pcbnew.SaveBoard(REAL, b)

# Os planos de terra saem por edicao de texto: nesta versao do SWIG os objetos
# de Zones() vem como ponteiros crus, sem os metodos de remocao. add_zones.py
# recria os planos depois do roteamento.
import io
txt = io.open(REAL, encoding="utf-8").read()
n = 0
while True:
    i = txt.find("\n\t(zone")
    if i < 0:
        break
    d = 0
    for j in range(i + 1, len(txt)):
        if txt[j] == "(":
            d += 1
        elif txt[j] == ")":
            d -= 1
            if d == 0:
                break
    txt = txt[:i] + txt[j + 1:]
    n += 1
io.open(REAL, "w", encoding="utf-8", newline="\n").write(txt)
print("removidos %d planos de terra (add_zones.py recria depois)" % n)

for ref in REMOVER:
    marca = '(property "Reference" "%s"' % ref
    k = txt.find(marca)
    if k < 0:
        continue
    i = txt.rindex("\n\t(footprint", 0, k)
    d = 0
    for j in range(i + 1, len(txt)):
        if txt[j] == "(":
            d += 1
        elif txt[j] == ")":
            d -= 1
            if d == 0:
                break
    txt = txt[:i] + txt[j + 1:]
    print("removido do projeto:", ref)
io.open(REAL, "w", encoding="utf-8", newline="\n").write(txt)

# ---- regras de projeto no .kicad_pro (a fonte, o .kicad_pcb so cacheia) -----
import json
PRO = "%s/%s.kicad_pro" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
d = json.load(io.open(PRO, encoding="utf-8"))
d["board"]["design_settings"]["rules"].update(
    {"min_clearance": 0.20, "min_track_width": 0.50, "min_via_diameter": 0.8})
for c in d["net_settings"]["classes"]:
    c["clearance"] = 0.20
    if c["name"] == "Default":
        c["track_width"], c["via_diameter"], c["via_drill"] = 0.50, 0.80, 0.40
    else:                                   # Power
        c["track_width"], c["via_diameter"], c["via_drill"] = 1.00, 1.00, 0.50
io.open(PRO, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, indent=2) + "\n")
print("regras: sinal 0,50 / alimentacao 1,00 / isolacao 0,20 (antes 0,25/0,60/0,14)")
print("gravado:", REAL)
