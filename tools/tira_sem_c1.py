# -*- coding: utf-8 -*-
"""Remove C1 do esquematico da tira e poe a ligacao de GND no lugar dela.

POR QUE C1 SAI. Numa placa de passagem com ilhas presas a uma face (F.Cu leva
29..56, B.Cu leva 1..28), cada COLUNA carrega redes diferentes nas duas faces.
Logo **toda ilha passante fora da coluna da guia curto-circuita as duas faces**
— nao existe lugar para um componente THT. E mesmo com ilha SMD nao adianta:
+5V esta em x=68,58 e o GND mais proximo em x=60,96, com BUS_9V (x=66,04) entre
eles, e as duas faces ocupadas por verticais. Nao ha caminho de 2 camadas de um
ao outro. O desacoplamento fica na placa principal (5x100n + 10u) e no
periferico seguinte, que e onde ele serve para alguma coisa.

POR QUE ENTRA O LINK DE GND. Os pinos 6 e 14 sao os dois GND do barramento.
Cada um atravessa reto, mas amarra-los entre si exigiria cruzar 7 colunas — e
as duas faces estao cheias. Duas ilhas SMD em B.Cu e um fio isolado por cima
resolvem: e o retorno de terra de tudo que for ligado em cascata.

  "C:/Program Files/KiCad/10.0/bin/python.exe" tira_sem_c1.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist_exp as TIRA

SCH = "%s/%s.kicad_sch" % (TIRA.PROJ_DIR, TIRA.PROJ_NAME)


def bloco(s, ini):
    """Extensao do s-expression que comeca em ini, balanceando parenteses."""
    d = 0
    for i in range(ini, len(s)):
        if s[i] == "(":
            d += 1
        elif s[i] == ")":
            d -= 1
            if d == 0:
                return i + 1
    raise ValueError("parenteses nao fecham")


def remove_blocos(s, achador, quantos=None):
    fora = 0
    while True:
        m = achador(s)
        if not m or (quantos is not None and fora >= quantos):
            return s, fora
        ini = s.rindex("(", 0, m.start() + 1)
        fim = bloco(s, ini)
        # come tambem a indentacao e a quebra de linha da frente
        while ini > 0 and s[ini - 1] in "\t ":
            ini -= 1
        if ini > 0 and s[ini - 1] == "\n":
            ini -= 1
        s = s[:ini] + s[fim:]
        fora += 1


s = io.open(SCH, encoding="utf-8").read()
orig = len(s)

# 1) o simbolo C1 (bloco (symbol ... lib_id "Device:C" ...))
while True:
    m = re.search(r'\(lib_id "Device:C"\)', s)
    if not m:
        break
    ini = s.rindex("(symbol", 0, m.start())
    fim = bloco(s, ini)
    while ini > 0 and s[ini - 1] in "\t ":
        ini -= 1
    if ini > 0 and s[ini - 1] == "\n":
        ini -= 1
    s = s[:ini] + s[fim:]
    print("removido o simbolo C1")

# 2) rotulos, fios e juncoes na coluna de C1 (x = 377.19)
for tipo, padrao in (("global_label", r'\(global_label "[^"]+"\s*\n\s*\(shape \w+\)\s*\n\s*\(at 377\.19 '),
                     ("junction", r'\(junction\s*\n\s*\(at 377\.19 '),
                     ("wire", r'\(wire\s*\n\s*\(pts\s*\n\s*\(xy 377\.19 ')):
    n = 0
    while True:
        m = re.search(padrao, s)
        if not m:
            break
        ini = m.start()
        fim = bloco(s, ini)
        while ini > 0 and s[ini - 1] in "\t ":
            ini -= 1
        if ini > 0 and s[ini - 1] == "\n":
            ini -= 1
        s = s[:ini] + s[fim:]
        n += 1
    print("removidos %d %s em x=377.19" % (n, tipo))

io.open(SCH, "w", encoding="utf-8", newline="\n").write(s)
print("esquematico: %d -> %d bytes" % (orig, len(s)))
