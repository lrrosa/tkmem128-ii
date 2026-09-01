# -*- coding: utf-8 -*-
"""Monta o pacote de release: o suficiente para fabricar e montar a placa.

  python tools/monta_pacote.py v1.0 [--saida DIR]

POR QUE ISTO EXISTE. Quem quer so mandar fabricar nao precisa do projeto
inteiro -- precisa dos dois gerbers, da lista de material, do .jed do GAL e
dos documentos que dizem o que fazer antes de ligar no micro. Juntar isso a
mao a cada versao daria um zip que envelhece em relacao ao repositorio, que e
exatamente o que os conferidores existem para evitar. Aqui o pacote e
DERIVADO: sai do repositorio, e o CI so publica depois que as verificacoes
passam.

O QUE FICA DE FORA, de proposito:

- fontes do KiCad e tools/ -- quem quer modificar clona o repositorio;
- posicoes.csv -- e arquivo de pick-and-place, e aqui tudo e passante montado
  a mao; no pacote so confundiria;
- a ROM do Spectrum 128 -- copyright da Amstrad/Sky, nao esta no repositorio.

Os .md carregam links relativos. Os que apontam para arquivos que entram no
pacote continuam funcionando, porque a arvore de docs/ e gal/ e preservada;
os que apontam para fora viram URL do GitHub na tag. No fim o proprio
confere_links.py e chamado sobre o pacote montado, entao um link quebrado
derruba a geracao em vez de sair no zip.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
REPO = "https://github.com/lrrosa/tkmem128-ii"
PCB_PRINCIPAL = "hardware/tkmem128-ii.kicad_pcb"
PACOTE = None

# origem no repositorio -> destino dentro do pacote
ARQUIVOS = [
    ("production/placa-principal/gerbers.zip", "gerbers/placa-principal.zip"),
    ("production/tira-expansao/gerbers.zip",   "gerbers/tira-expansao.zip"),

    ("docs/ANTES-DE-FABRICAR.md", "docs/ANTES-DE-FABRICAR.md"),
    ("docs/MONTAGEM.md",          "docs/MONTAGEM.md"),
    ("docs/PREPARAR-O-TK.md",     "docs/PREPARAR-O-TK.md"),
    ("docs/img/placa-principal.png",       "docs/img/placa-principal.png"),
    ("docs/img/placa-principal-verso.png", "docs/img/placa-principal-verso.png"),
    ("docs/img/placa-expansora.png",       "docs/img/placa-expansora.png"),
    ("docs/img/placa-expansora-verso.png", "docs/img/placa-expansora-verso.png"),
    ("docs/img/vista-de-lado.svg",         "docs/img/vista-de-lado.svg"),

    ("production/placa-principal/bom.csv", "producao/placa-principal-bom.csv"),
    ("production/tira-expansao/bom.csv",   "producao/tira-expansao-bom.csv"),
    ("production/placa-principal/esquematico.pdf",
     "producao/esquematico-placa-principal.pdf"),
    ("production/tira-expansao/esquematico.pdf",
     "producao/esquematico-tira-expansao.pdf"),

    ("hardware/gal/tkmem128.jed", "gal/tkmem128.jed"),
    ("hardware/gal/tkmem128.pld", "gal/tkmem128.pld"),
    ("hardware/gal/README.md",    "gal/README.md"),

    ("LICENSE.txt", "LICENSE.txt"),
]


def versao_do_silk():
    """Le a versao gravada na serigrafia da placa principal.

    O cobre e a fonte da verdade da revisao: e o numero que fica na mao de
    quem monta. Se a tag divergir do silk, o download e a placa contam
    historias diferentes -- entao aqui isso e erro, nao aviso.
    """
    txt = io.open(os.path.join(RAIZ, PCB_PRINCIPAL), encoding="utf-8").read()
    achado = re.findall(r'"LRRosa \d{4} (v[\d.]+)"', txt)
    if not achado:
        raise SystemExit("nao achei a versao na serigrafia de " + PCB_PRINCIPAL)
    if len(set(achado)) > 1:
        raise SystemExit("silk com versoes divergentes: %s" % sorted(set(achado)))
    return achado[0]


def reescreve_links(origem_rel, destino_rel, destino_abs, tag):
    """Links para arquivos fora do pacote viram URL do GitHub na tag."""
    txt = io.open(destino_abs, encoding="utf-8", newline="").read()
    dir_repo = os.path.dirname(origem_rel)
    dir_pac = os.path.dirname(destino_rel)
    trocas = []

    def troca(m):
        alvo = m.group(1)
        if alvo.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        arq, sep, anc = alvo.partition("#")
        if arq:
            no_pacote = os.path.normpath(os.path.join(dir_pac, arq))
            if os.path.exists(os.path.join(PACOTE, no_pacote)):
                return m.group(0)               # resolve dentro do pacote
        else:
            return m.group(0)                   # ancora na mesma pagina
        no_repo = os.path.normpath(os.path.join(dir_repo, arq)).replace("\\", "/")
        trocas.append((alvo, no_repo))
        return "](%s/blob/%s/%s%s%s)" % (REPO, tag, no_repo, sep, anc)

    novo = re.sub(r'\]\(([^)\s]+)\)', troca, txt)
    if novo != txt:
        io.open(destino_abs, "w", encoding="utf-8", newline="").write(novo)
    return trocas


LEIAME = u"""# TKMEM-128 II {tag} — pacote de fabricação e montagem

Expansão externa de **128 KB (ou 512 KB) de RAM paginada no padrão ZX
Spectrum 128** para **TK90X, TK95 e ZX Spectrum 48K**.

> ## ⚠️ Nenhuma placa deste projeto foi fabricada ainda
>
> ERC e DRC estão zerados, a netlist foi conferida contra a intenção de
> projeto e as duas placas foram impressas em 1:1 e comparadas com as peças
> reais. Mas **nenhuma placa foi fabricada nem testada num micro real**.
>
> O `{tag}` numera a revisão do desenho — o mesmo número gravado na
> serigrafia da placa —, não uma validação em bancada. Se você for o
> primeiro a montar, comece por `docs/ANTES-DE-FABRICAR.md`: há itens ali
> que, se estiverem errados, **podem danificar o micro**.

## Por onde começar

| Momento | Leia |
| --- | --- |
| Antes de fechar o pedido na fábrica | `docs/ANTES-DE-FABRICAR.md` |
| Antes de ligar no micro | `docs/PREPARAR-O-TK.md` |
| Com as placas na mão | `docs/MONTAGEM.md` |

## O que tem aqui

```
gerbers/     os dois pedidos, um .zip cada — são placas diferentes,
             com número de camadas diferente
docs/        os três documentos acima, mais os renders das duas placas
producao/    lista de material das duas placas e os esquemáticos em PDF
gal/         o .jed pronto para gravar (checksum C5752) e o fonte
```

**Dois campos do formulário da fábrica não viajam nos gerbers:** o número de
camadas (a placa principal é de **4**, a tira é de 2) e o acabamento dos
dedos da tira (**ENIG + chanfro de 45°**). Errar qualquer um dos dois produz
uma placa que passa na inspeção visual. Está no item 0 do
`docs/ANTES-DE-FABRICAR.md`.

## O que não está aqui

- **Os fontes do KiCad** — estão no repositório: {repo}
- **A ROM do Spectrum 128** — copyright da Amstrad/Sky. Ela é *opcional*:
  jogos de 128 KB não dependem dela. Ver `docs/MONTAGEM.md`.

## Licença

CERN-OHL-S v2 — ver `LICENSE.txt`. Circuito original do **Velesoft** (2009);
adaptação ao TK da **Luccas Eletrônica** (2012). Detalhes e créditos em
{repo}
"""


def main():
    global PACOTE
    if len(sys.argv) < 2:
        raise SystemExit("uso: python tools/monta_pacote.py v1.0 [--saida DIR]")
    tag = sys.argv[1]
    saida = RAIZ + "/dist"
    if "--saida" in sys.argv:
        saida = sys.argv[sys.argv.index("--saida") + 1]

    silk = versao_do_silk()
    if tag.lstrip("v") != silk.lstrip("v"):
        raise SystemExit(
            "a tag (%s) nao bate com a serigrafia da placa (%s).\n"
            "O numero gravado no cobre e o que fica na mao de quem monta:\n"
            "ou corrija a tag, ou atualize o silk antes de publicar."
            % (tag, silk))
    print("versao: %s (confere com a serigrafia da placa)" % tag)

    nome = "tkmem128-ii-%s" % tag
    PACOTE = os.path.join(saida, nome)
    if os.path.isdir(PACOTE):
        shutil.rmtree(PACOTE)
    os.makedirs(PACOTE)

    # ---- copia ------------------------------------------------------------
    faltando = [o for o, _ in ARQUIVOS
                if not os.path.exists(os.path.join(RAIZ, o))]
    if faltando:
        raise SystemExit("nao existem no repositorio:\n  " + "\n  ".join(faltando))
    for origem, destino in ARQUIVOS:
        alvo = os.path.join(PACOTE, destino)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        shutil.copy2(os.path.join(RAIZ, origem), alvo)
    print("%d arquivos copiados" % len(ARQUIVOS))

    io.open(os.path.join(PACOTE, "LEIA-ME.md"), "w",
            encoding="utf-8", newline="\n").write(
                LEIAME.format(tag=tag, repo=REPO))

    # ---- links ------------------------------------------------------------
    for origem, destino in ARQUIVOS:
        if not destino.endswith(".md"):
            continue
        for alvo, no_repo in reescreve_links(
                origem, destino, os.path.join(PACOTE, destino), tag):
            print("   link para fora do pacote -> GitHub: %s" % alvo)

    # ---- confere o proprio pacote ----------------------------------------
    print("\nconferindo os links do pacote:")
    r = subprocess.run(
        [sys.executable, os.path.join(RAIZ, "tools/confere_links.py"), PACOTE],
        capture_output=True, text=True, encoding="utf-8")
    print("   " + (r.stdout or r.stderr).strip().replace("\n", "\n   "))
    if r.returncode != 0:
        raise SystemExit("pacote com link quebrado")

    # ---- zip --------------------------------------------------------------
    zf = os.path.join(saida, nome + ".zip")
    if os.path.exists(zf):
        os.remove(zf)
    with zipfile.ZipFile(zf, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, arqs in os.walk(PACOTE):
            for a in sorted(arqs):
                p = os.path.join(base, a)
                z.write(p, os.path.join(nome, os.path.relpath(p, PACOTE)))
    print("\n%s\n%.0f kB, %d arquivos"
          % (zf, os.path.getsize(zf) / 1024.0, len(ARQUIVOS) + 1))


if __name__ == "__main__":
    main()
