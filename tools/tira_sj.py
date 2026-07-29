# -*- coding: utf-8 -*-
"""Remove SJ1 e SJ2 do esquematico da placa principal.

Eram terra extra OPCIONAL, em pinos que so sao GND numa das maquinas: pino 7 no
ZX Spectrum, pino 15 no TK90X/TK95. A propria documentacao ja mandava deixar os
dois abertos — foi assim que a placa foi validada. Em compensacao cada um puxava
uma rede do conector ate o outro extremo da placa, atravessando o corredor por
onde passam A0..A13 e D0..D7.

Sai o que era opcional e atrapalhava. Quem quiser o terra extra solda um fio do
pino do conector ao plano de terra, que agora cobre as duas faces.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tira_sj.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as PRINC

SCH = "%s/%s.kicad_sch" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)
FORA = ("SJ1", "SJ2")
# rotulos que so existiam para alimentar os solder jumpers
ROTULOS = {"BUS_P07": 171.45, "BUS_P15": 191.77}


def fim_do_bloco(s, ini):
    d = 0
    for i in range(ini, len(s)):
        if s[i] == "(":
            d += 1
        elif s[i] == ")":
            d -= 1
            if d == 0:
                return i + 1
    raise ValueError("parenteses nao fecham")


def corta(s, ini, fim):
    while ini > 0 and s[ini - 1] in "\t ":
        ini -= 1
    if ini > 0 and s[ini - 1] == "\n":
        ini -= 1
    return s[:ini] + s[fim:]


s = io.open(SCH, encoding="utf-8").read()
orig = len(s)

for ref in FORA:
    m = re.search(r'\(property "Reference" "%s"' % ref, s)
    if not m:
        print("%s: ja nao estava la" % ref)
        continue
    ini = s.rindex("(symbol", 0, m.start())
    s = corta(s, ini, fim_do_bloco(s, ini))
    print("removido o simbolo", ref)

# os rotulos globais do lado dos SJ (o outro par, no conector, fica)
for nome, y in ROTULOS.items():
    pad = r'\(global_label "%s"\s*\n\s*\(shape \w+\)\s*\n\s*\(at 46\.99 %s' % (
        nome, re.escape(str(y)))
    m = re.search(pad, s)
    if m:
        s = corta(s, m.start(), fim_do_bloco(s, m.start()))
        print("removido o rotulo %s em (46.99, %s)" % (nome, y))

io.open(SCH, "w", encoding="utf-8", newline="\n").write(s)
print("esquematico: %d -> %d bytes" % (orig, len(s)))
