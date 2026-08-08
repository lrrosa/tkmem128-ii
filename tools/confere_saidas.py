# -*- coding: utf-8 -*-
"""Diz se as saidas de `production/` e `docs/img/` estao em dia.

POR QUE ISTO EXISTE. As duas maneiras obvias de responder "esta atualizado?"
falham neste projeto:

  data de arquivo   O kicad-cli reescreve a .kicad_pcb byte a byte identica ao
                    rodar export e render. A placa fica sempre com data mais nova
                    que os derivados dela, e a comparacao acusa defasagem que nao
                    existe.

  comparar conteudo Gerber, .drl, .gbrjob e PDF carregam a data de geracao
                    embutida. E o raytracer dos renders NAO e deterministico:
                    duas rodadas seguidas dao PNGs diferentes, com a placa
                    intacta. Nada disso da para diffar.

Entao a geracao registra aqui o hash das FONTES, e este script compara. Se o
hash bate, as saidas foram geradas desta versao das placas. Simples e imune a
tudo acima.

  python confere_saidas.py           confere
  python confere_saidas.py --grava   registra (o producao.sh chama assim)
"""
import hashlib, io, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(RAIZ, "production", "fontes.json")
FONTES = (
    "hardware/tkmem128-ii.kicad_pcb",
    "hardware/tkmem128-ii.kicad_sch",
    "hardware/expansor/tkmem128-ii-expansor.kicad_pcb",
    "hardware/expansor/tkmem128-ii-expansor.kicad_sch",
)


CRLF = b"\x0d\x0a"
LF = b"\x0a"


def md5(caminho):
    """Hash do conteudo, com fim de linha NORMALIZADO.

    Sem normalizar, o hash passa a depender de quem escreveu o arquivo por
    ultimo: o `pcbnew` grava LF e o `git checkout` no Windows devolve CRLF.
    Trocar de um para o outro muda todos os bytes sem mudar nada da placa.

    Isso mordeu numa conferencia de vespera de fabricacao: rodar o DRC com
    `--save-board` regravou a placa em CRLF, ela cresceu exatamente 17627 bytes
    — um por linha —, o `git diff` reportou ZERO linhas alteradas, e mesmo
    assim este script acusou "as saidas nao correspondem a estas placas".

    Alarme falso e pior que nenhum alarme: ensina a ignorar o alarme, e no dia
    em que a diferenca for de verdade ninguem vai olhar.
    """
    with open(caminho, "rb") as f:
        dados = f.read()
    return hashlib.md5(dados.replace(CRLF, LF)).hexdigest()


agora = {f: md5(os.path.join(RAIZ, f)) for f in FONTES}

if "--grava" in sys.argv:
    io.open(MANIFESTO, "w", encoding="utf-8", newline="\n").write(
        json.dumps(agora, indent=2, sort_keys=True) + "\n")
    print("   fontes.json atualizado")
    raise SystemExit(0)

if not os.path.exists(MANIFESTO):
    raise SystemExit("nao ha production/fontes.json — rode tools/producao.sh")

antes = json.load(io.open(MANIFESTO, encoding="utf-8"))
velhas = [f for f in FONTES if antes.get(f) != agora[f]]
for f in FONTES:
    print("  %-46s %s" % (f, "MUDOU desde a geracao" if f in velhas else "em dia"))
print()
if velhas:
    print("FALHA: as saidas de production/ e docs/img/ nao correspondem a estas")
    print("       placas. Rode: bash tools/producao.sh")
    raise SystemExit(1)
print("OK: gerbers, PDF, BOM, posicoes e renders foram gerados destas placas.")
