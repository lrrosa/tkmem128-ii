# -*- coding: utf-8 -*-
"""Verifica se a placa continua compativel com TK90X/TK95 E ZX Spectrum 48K.

A compatibilidade nao e uma promessa de texto: ela se resume a uma regra
mecanica, que este script confere.

  O barramento do TK e o do ZX Spectrum 48K sao o mesmo conector, mas nove
  contatos NAO carregam a mesma coisa nas duas maquinas. Enquanto a placa nao
  tocar nenhum deles, ela serve nas duas.

Os nove estao marcados em `busdef.py` com uma ressalva no comentario ("Spectrum",
"difere", "NAO conectar"). O script cruza essa marca com os pinos que a netlist
realmente liga a algum componente e falha alto se algum deles aparecer.

Rodar depois de qualquer mexida em `busdef.py` ou em `netlist.py` — e antes de
repetir em qualquer lugar que a placa serve nas duas maquinas.

  python confere_compatibilidade.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from busdef import BUS
import netlist as PRINC

RESSALVA = ("Spectrum", "difere", "NAO conectar")
# O pino 29 tem "Spectrum" no comentario, mas a ressalva dele e o contrario:
# diz que ele e N.C. NAS DUAS. E o unico caso e esta aqui de proposito.
EXCECAO = {29}

usados = set()
for ref, pinos in PRINC.CONN.items():
    if ref != "J1":                    # J1 mapeia o barramento inteiro
        usados |= set(pinos.values())

toca, divergentes, erros = [], [], []
for p in sorted(BUS):
    rede, _alias, com = BUS[p]
    tem_ressalva = any(k in com for k in RESSALVA) and p not in EXCECAO
    if tem_ressalva:
        divergentes.append((p, rede, com))
    if rede in usados:
        toca.append(p)
        if tem_ressalva:
            erros.append("pino %d (%s) difere entre TK e Spectrum: %s"
                         % (p, rede, com))

print("a placa liga %d dos %d contatos do barramento" % (len(toca), len(BUS)))
print("contatos que diferem entre TK e ZX Spectrum 48K: %d"
      % len(divergentes))
for p, rede, com in divergentes:
    print("   %2d  %-11s %s" % (p, rede, com))
print()
if erros:
    for e in erros:
        print("FALHA:", e)
    raise SystemExit(1)
print("OK: nenhum contato divergente e usado — serve em TK90X/TK95 e "
      "ZX Spectrum 48K.")
print()
print("Lembrete: isto cobre so o barramento. A desativacao da RAM interna de")
print("32K e especifica de cada maquina, e a que esta documentada e a do TK.")
