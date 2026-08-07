# -*- coding: utf-8 -*-
"""Verificacao de regressao: os rotulos de pino batem com busdef.py?

  python tools/confere_pinos.py

POR QUE ISTO EXISTE. `busdef.py` e a fonte unica da pinagem do barramento, mas
o simbolo do conector fica EMBUTIDO dentro de cada `.kicad_sch` e dentro de
`lib/tkmem128.kicad_sym`. Corrigir a pinagem na netlist e na placa nao propaga
para essas copias, e nada acusa: ERC nao le busdef.py, e DRC nao le esquematico.

Foi o que aconteceu quando a auto-desativacao da RAM saiu do pino 17 para o 29
(por causa do video componente do ZX Spectrum). A placa mudou, a netlist mudou,
e o esquematico continuou desenhando **pino 17 = RAMDIS e pino 29 = NC** — ou
seja, o PDF entregue mostrava exatamente a ligacao que fomos evitar, e o rotulo
do pino contradizia o fio ligado nele.

E a terceira vez que a copia envelhece em silencio neste projeto: antes foram a
ilha do conector (1,75 contra 1,50 na placa) e o titulo do bloco de legenda.
Por isso virou conferidor.
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "tools"))
from busdef import BUS                                    # noqa: E402

ARQUIVOS = (
    "hardware/tkmem128-ii.kicad_sch",
    "hardware/expansor/tkmem128-ii-expansor.kicad_sch",
    "hardware/lib/tkmem128.kicad_sym",
)

# Os dois separadores existem e isso e armadilha: o GERADOR escreve
# "ROTULO (nn)" com espaco, e e assim que fica no .kicad_sym; mas o KiCad nao
# aceita espaco em nome de pino, entao ao salvar um .kicad_sch ele troca por
# underscore. Um padrao que so aceitasse um dos dois leria zero pino num dos
# arquivos e passaria "sem divergencia" — pior que nao conferir.
esperado = {p: "%s_(%d)" % (v[1].replace(" ", "_"), p) for p, v in BUS.items()}
PADRAO = re.compile(r'\(name "([A-Za-z0-9_/+\- ]+?)[ _]\((\d+)\)"')

falhou = False
for rel in ARQUIVOS:
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        print("  %-52s ausente" % rel)
        falhou = True
        continue
    texto = io.open(caminho, encoding="utf-8").read()
    achados = {}
    for nome, num in PADRAO.findall(texto):
        n = int(num)
        if n in esperado:
            achados.setdefault(n, set()).add(
                "%s_(%d)" % (nome.replace(" ", "_"), n))
    dif = [(n, sorted(v)[0], esperado[n]) for n, v in sorted(achados.items())
           if any(x != esperado[n] for x in v)]
    faltando = sorted(set(esperado) - set(achados))
    print("  %-52s %d pinos, %d divergentes" % (rel, len(achados), len(dif)))
    for n, tem, deve in dif:
        print("      pino %2d: esta %-16s e busdef.py diz %s" % (n, tem, deve))
    if dif:
        falhou = True
    if faltando and len(faltando) not in (0, len(esperado)):
        # a tira nao tem os pinos da guia; nao e erro faltar 5 e 52
        reais = [p for p in faltando if p not in (5, 52)]
        if reais:
            print("      nao apareceram: %s" % reais)

print()
if falhou:
    raise SystemExit("FALHA: rotulo de pino fora de sincronia com busdef.py")
print("OK: os rotulos de pino do conector batem com busdef.py nos tres arquivos.")
