# -*- coding: utf-8 -*-
"""Recorta a placa do fundo nas fotos das placas fabricadas.

  python tools/corta_fotos.py                 # so mostra o que faria
  python tools/corta_fotos.py --grava

POR QUE ISTO EXISTE. As fotos saem do celular com 4080x1884 e a placa ocupando
um terco do quadro, o resto sendo a mesa. No README isso vira uma imagem pesada
onde a placa aparece pequena. O recorte e mecanico, mas fazer a mao a cada nova
foto -- e vao vir mais, quando as placas forem montadas -- da retrabalho e
resultado inconsistente.

ONDE FICAM AS FOTOS. As ORIGINAIS nao sao versionadas: sao ~2,3 MB cada, sao
insumo e nao projeto, e estao no `.gitignore`. Ficam soltas em `docs/img/` na
maquina de quem fotografou. O que o repositorio guarda sao os RECORTES, com
sufixo `-fabricada`. Quem clonar o repositorio nao consegue rodar este script
sem ter as fotos -- e nao precisa, do mesmo jeito que nao precisa rodar os
geradores de footprint.

COMO ACHA A PLACA. Nao por cor fixa: a cor do fundo muda com a mesa e a luz. O
fundo e estimado a partir das BORDAS da propria imagem: a moldura de 3% em
volta, que e mesa em qualquer foto util.

A comparacao e feita em CROMATICIDADE -- r=R/(R+G+B), g=G/(R+G+B) -- e nao em
RGB cru. Isso nao e refinamento: com distancia RGB o primeiro recorte saiu 47%
mais largo que a placa, porque a luz caia mais forte numa faixa do fundo, a
mancha clara passou o limiar e o fechamento morfologico a colou na placa.
Normalizar por brilho apaga exatamente esse artefato -- fundo claro e fundo
escuro tem a mesma cromaticidade.

Tres armadilhas que o caminho ingenuo nao trata:

1. **Iluminacao desigual**, acima.
2. **Buracos.** A serigrafia branca e os dedos dourados ENIG sao muito
   diferentes do roxo. Sem `binary_fill_holes` eles viram furos na mascara e o
   recorte pode cortar por dentro da placa.
3. **Mais de uma placa no quadro.** A foto da tira tem a placa principal
   entrando pela direita. Bounding box global pegaria as duas -- por isso o
   corte sai da MAIOR COMPONENTE CONEXA, nao do conjunto todo.

A deteccao roda numa versao reduzida (rapido e imune a ruido de JPEG) e a caixa
e reescalada para cortar no original.

CONFERENCIA. Cada foto declara a razao largura/altura da placa que aparece
nela, e o script compara com a razao do recorte. Um recorte que pegou fundo
demais, ou que cortou a placa, erra essa razao -- foi o que denunciou o
primeiro resultado errado, antes de qualquer arquivo ser gravado. Tolerancia de
5%, que acomoda a leve rotacao da placa sobre a mesa.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
IMG = RAIZ + "/docs/img"

PRINCIPAL = 78.74 / 66.04
TIRA = 78.74 / 45.00

# (origem, destino, razao largura/altura da placa que aparece na foto)
# Os nomes de destino seguem o padrao dos renders (minusculas, hifen), para as
# duas familias ficarem lado a lado na pasta.
FOTOS = [
    ("placa principal fabricada - lado componentes.jpg",
     "placa-principal-fabricada.jpg", PRINCIPAL),
    ("placa principal fabricada - lado solda.jpg",
     "placa-principal-fabricada-verso.jpg", PRINCIPAL),
    ("placa expansora fabricada.jpg",
     "placa-expansora-fabricada.jpg", TIRA),
]

ESCALA = 8          # reducao usada na deteccao
MARGEM = 12         # px do original deixados em volta da placa
LARGURA_MAX = 1500  # redimensiona a saida para caber no README
QUALIDADE = 88
TOLERANCIA = 0.05


def acha_placa(im):
    """Caixa (x1, y1, x2, y2) da maior peca que nao e fundo, no original."""
    p = im.resize((im.width // ESCALA, im.height // ESCALA), Image.BILINEAR)
    a = np.asarray(p, dtype=np.float32)

    # cromaticidade: descarta o brilho e guarda so a cor
    soma = a.sum(axis=2, keepdims=True)
    soma[soma < 1] = 1
    crom = a[:, :, :2] / soma

    # cor do fundo = mediana da moldura externa (3% da menor dimensao)
    b = max(2, int(min(a.shape[:2]) * 0.03))
    moldura = np.concatenate([crom[:b].reshape(-1, 2), crom[-b:].reshape(-1, 2),
                              crom[:, :b].reshape(-1, 2),
                              crom[:, -b:].reshape(-1, 2)])
    fundo = np.median(moldura, axis=0)

    dist = np.sqrt(((crom - fundo) ** 2).sum(axis=2))
    # limiar proporcional ao contraste da propria foto, em vez de constante
    mask = dist > max(0.05, np.percentile(dist, 99) * 0.35)

    mask = ndimage.binary_closing(mask, np.ones((5, 5)))
    mask = ndimage.binary_fill_holes(mask)                 # silk e dedos ENIG
    mask = ndimage.binary_opening(mask, np.ones((3, 3)))   # tira poeira

    rotulos, n = ndimage.label(mask)
    if n == 0:
        raise SystemExit("nao achei placa nenhuma")
    areas = ndimage.sum(mask, rotulos, range(1, n + 1))
    maior = int(np.argmax(areas)) + 1
    ys, xs = np.where(rotulos == maior)

    x1 = int(max(0, xs.min() * ESCALA - MARGEM))
    y1 = int(max(0, ys.min() * ESCALA - MARGEM))
    x2 = int(min(im.width, (xs.max() + 1) * ESCALA + MARGEM))
    y2 = int(min(im.height, (ys.max() + 1) * ESCALA + MARGEM))
    return (x1, y1, x2, y2), n, areas[maior - 1] / mask.size


def main():
    grava = "--grava" in sys.argv
    problemas = []
    for origem, destino, razao_ok in FOTOS:
        po = os.path.join(IMG, origem)
        if not os.path.exists(po):
            print("  ausente: %s" % origem)
            continue
        im = Image.open(po)
        caixa, n, frac = acha_placa(im)
        w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
        razao = w / float(h)
        erro = abs(razao - razao_ok) / razao_ok

        print("%s" % origem)
        print("   %dx%d -> corte %dx%d   (%d peca(s) no quadro, maior ocupa %.0f%%)"
              % (im.width, im.height, w, h, n, frac * 100))
        print("   razao %.3f contra %.3f da placa real: %.1f%% de erro -> %s"
              % (razao, razao_ok, erro * 100,
                 "ok" if erro <= TOLERANCIA else "FORA DA TOLERANCIA"))
        if erro > TOLERANCIA:
            problemas.append(origem)
            continue

        corte = im.crop(caixa)
        if corte.width > LARGURA_MAX:
            nh = round(corte.height * LARGURA_MAX / corte.width)
            corte = corte.resize((LARGURA_MAX, nh), Image.LANCZOS)
        if grava:
            pd = os.path.join(IMG, destino)
            corte.save(pd, quality=QUALIDADE, optimize=True, progressive=True)
            print("   gravado: docs/img/%s  %dx%d  %.0f kB"
                  % (destino, corte.width, corte.height,
                     os.path.getsize(pd) / 1024.0))

    if problemas:
        print("\nrecorte fora da tolerancia em:\n   " + "\n   ".join(problemas))
        raise SystemExit(1)
    if not grava:
        print("\nSimulacao. Repita com --grava para escrever os recortes.")


if __name__ == "__main__":
    main()
