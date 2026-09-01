# -*- coding: utf-8 -*-
"""Verificacao de regressao: os links entre os documentos ainda resolvem?

  python tools/confere_links.py

POR QUE ISTO EXISTE. A documentacao deste projeto e cruzada de proposito: o
README manda para secoes especificas de PREPARAR-O-TK.md, o MONTAGEM.md manda
para o item da caixa em ANTES-DE-FABRICAR.md, e o ANTES-DE-FABRICAR.md manda
para os proprios itens. Nada disso e verificado por ninguem — um link para
ancora inexistente nao da erro, nao muda a renderizacao, e so aparece quando
alguem clica e cai no topo da pagina.

E ancora quebra facil, porque ela e DERIVADA do titulo: basta reescrever um
cabecalho para todos os links que apontavam para ele morrerem em silencio. Ja
mexemos em titulo varias vezes aqui (o item 3b nasceu quando a placa virou de
4 camadas, o item 0 saiu de dentro dos itens 3b e 4).

Confere tambem a existencia do arquivo de destino, o que pega link para
arquivo renomeado ou apagado — como o footprint do header 2x28, removido
quando a arquitetura do prototipo foi abandonada.
"""
import glob
import io
import os
import re
import sys

# Aceita uma raiz por argumento para conferir tambem o pacote de release
# montado por tools/monta_pacote.py, que tem outra arvore de diretorios.
RAIZ = (os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Varredura recursiva em vez de lista fixa de pastas: assim serve para as duas
# arvores. Fora ficam os diretorios ocultos (.git, .history) e production/,
# que so tem saida gerada.
IGNORA = (".", "production")

# O Git Bash e o Python nativo do Windows discordam do separador: glob devolve
# "docs\X.md" e os links trazem "docs/X.md". Sem normalizar os dois lados, o
# indice nunca encontra o destino e TODO link entre documentos vira falso
# positivo.
def norm(p):
    return p.replace("\\", "/")


def ancora(titulo):
    """Ancora no estilo GitHub.

    Minusculas, marcacao (`code`, *enfase*) fora, pontuacao fora, espacos
    viram hifen. Acentos FICAM: o GitHub trata letra acentuada como letra,
    entao `#8-regras-de-fabricacao` nao resolve para "Regras de fabricacao"
    com cedilha — tem que ser escrito com o acento mesmo.
    """
    s = re.sub(r'[`*]', '', titulo.strip().lower())
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    return re.sub(r'\s+', '-', s.strip())


def indexa(caminho):
    """Ancoras de um documento, com o sufixo que o GitHub da a repetidas."""
    txt = io.open(os.path.join(RAIZ, caminho), encoding="utf-8").read()
    vistas, saida = {}, set()
    for titulo in re.findall(r'^#{1,6}\s+(.*)$', txt, re.M):
        a = ancora(titulo)
        n = vistas.get(a, 0)
        vistas[a] = n + 1
        saida.add(a if n == 0 else "%s-%d" % (a, n))
    return saida


docs = []
for base, dirs, arqs in os.walk(RAIZ):
    dirs[:] = [d for d in dirs
               if not d.startswith(".") and d not in IGNORA]
    for a in arqs:
        if a.endswith(".md"):
            docs.append(norm(os.path.relpath(os.path.join(base, a), RAIZ)))
docs.sort()
ancoras = {d: indexa(d) for d in docs}

ruins = []
for d in docs:
    base = os.path.dirname(d)
    txt = io.open(os.path.join(RAIZ, d), encoding="utf-8").read()
    for alvo in re.findall(r'\]\(([^)\s]+)\)', txt):
        if alvo.startswith(("http://", "https://", "mailto:")):
            continue
        arq, _, anc = alvo.partition("#")
        destino = norm(os.path.normpath(os.path.join(base, arq))) if arq else d
        if arq and not os.path.exists(os.path.join(RAIZ, destino)):
            ruins.append("%s -> %s (arquivo nao existe)" % (d, alvo))
            continue
        if anc:
            if destino not in ancoras:
                ruins.append("%s -> %s (destino nao e .md indexado)" % (d, alvo))
            elif anc not in ancoras[destino]:
                ruins.append("%s -> %s (ancora inexistente)" % (d, alvo))

print("%d documentos, %d ancoras" % (len(docs), sum(len(a) for a in ancoras.values())))
if ruins:
    print("\nLINKS QUEBRADOS:")
    for r in sorted(set(ruins)):
        print("   " + r)
    sys.exit(1)
print("OK: todos os links entre documentos resolvem.")
