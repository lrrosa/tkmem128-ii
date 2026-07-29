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
    "hardware/tkmem128.kicad_pcb",
    "hardware/tkmem128.kicad_sch",
    "hardware/expansor/tkmem128-expansor.kicad_pcb",
    "hardware/expansor/tkmem128-expansor.kicad_sch",
)


def md5(caminho):
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for pedaco in iter(lambda: f.read(1 << 16), b""):
            h.update(pedaco)
    return h.hexdigest()


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
