# -*- coding: utf-8 -*-
"""Move a auto-desativacao da RAM do pino 17 para o pino 29 e remove JP4.

POR QUE. O pino 17 e livre no TK, mas no ZX Spectrum e o **V do video
componente**. Por isso a placa precisava de JP4 e de um aviso em toda a
documentacao: fechar o jumper num Spectrum joga 5 V na saida do codificador de
video. Um jumper cuja posicao errada estraga o micro e um projeto ruim.

O pino 29 (28A na nomenclatura do Spectrum) e **N.C. nas duas maquinas**:
- no TK, confirmado na pinagem oficial arquivada e nas fotos do cartao, onde o
  dedo 17 e o 29 nao tem trilha nenhuma;
- no Spectrum, levantado por pesquisa do Leonardo (jul/2026).

Com isso o pull-up pode ser PERMANENTE: num Spectrum nao ha nada ligado ali, e
num TK ele faz o que tem que fazer. JP4 deixa de existir, e com ele o aviso
"nunca feche em Spectrum" — nao ha mais o que fechar errado.

R4 fica: e o limite de corrente, e nao monta-lo desliga o recurso. 1k e mais
firme que o pull-up de 10k da placa Luccas original, que ja bastava, o que
confirma que o pino 10 do IC27 e entrada livre.

  "C:/Program Files/KiCad/10.0/bin/python.exe" move_ramdis.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as PRINC

SCH = "%s/%s.kicad_sch" % (PRINC.PROJ_DIR, PRINC.PROJ_NAME)

# (nome atual, x, y) -> nome novo.  As coordenadas identificam qual das
# instancias do rotulo e qual: uma esta no pino do conector, outra no jumper.
RENOMEIA = [
    ("RAMDIS", "46.99", "196.85", "BUS_P17"),    # pino 17 volta a ser sem uso
    ("BUS_P29", "105.41", "224.79", "RAMDIS"),   # pino 29 recebe o sinal
    ("RAMDIS_DRV", "521.97", "96.52", "RAMDIS"),  # saida de R4
]
# rotulos que existiam so para os dois lados de JP4
APAGA = [("RAMDIS", "492.76", "279.4"), ("RAMDIS_DRV", "492.76", "276.86")]


def fim(s, i):
    d = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            d += 1
        elif s[j] == ")":
            d -= 1
            if d == 0:
                return j + 1
    raise ValueError("parenteses nao fecham")


def acha(s, nome, x, y):
    pad = (r'\(global_label "%s"\s*\n\s*\(shape \w+\)\s*\n\s*\(at %s %s '
           % (re.escape(nome), re.escape(x), re.escape(y)))
    return re.search(pad, s)


s = io.open(SCH, encoding="utf-8").read()
orig = len(s)

# 1) o simbolo JP4 e os dois rotulos que so serviam a ele
m = re.search(r'\(property "Reference" "JP4"', s)
if m:
    ini = s.rindex("(symbol", 0, m.start())
    f = fim(s, ini)
    while ini > 0 and s[ini - 1] in "\t ":
        ini -= 1
    if ini > 0 and s[ini - 1] == "\n":
        ini -= 1
    s = s[:ini] + s[f:]
    print("removido o simbolo JP4")

for nome, x, y in APAGA:
    m = acha(s, nome, x, y)
    if m:
        i, f = m.start(), fim(s, m.start())
        while i > 0 and s[i - 1] in "\t ":
            i -= 1
        if i > 0 and s[i - 1] == "\n":
            i -= 1
        s = s[:i] + s[f:]
        print("removido o rotulo %s em (%s, %s)" % (nome, x, y))

# 2) troca de nome nos rotulos que ficam
for nome, x, y, novo in RENOMEIA:
    m = acha(s, nome, x, y)
    if not m:
        raise SystemExit("nao achei %s em (%s, %s)" % (nome, x, y))
    ini, f = m.start(), fim(s, m.start())
    bloco = s[ini:f].replace('"%s"' % nome, '"%s"' % novo, 1)
    s = s[:ini] + bloco + s[f:]
    print("%-11s em (%-7s %-7s) -> %s" % (nome, x, y, novo))

io.open(SCH, "w", encoding="utf-8", newline="\n").write(s)
print("esquematico: %d -> %d bytes" % (orig, len(s)))
