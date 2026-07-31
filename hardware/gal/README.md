# GAL20V8B — decodificador da TKMEM-128 II

O GAL faz toda a decodificação de endereços da placa: seleciona ROM e SRAM,
gera o clock do latch da porta `0x7FFD` e produz os bits altos de endereço da
SRAM a partir do banco selecionado.

## Pinagem

Nome do pino = **função programada** (o símbolo no esquemático usa esses nomes).

```
                       ._____    _____.
                       |     \__/     |
                  MREQ |  1        24 | VCC
                 ZX512 |  2        23 | IORQ
                    A1 |  3        22 | SA14
                    WR |  4        21 | SA15
                DIS128 |  5        20 | SA16
                 BANK2 |  6        19 | /RAMCS
                    A5 |  7        18 | /SA17
                 BANK0 |  8        17 | SA18
                 BANK4 |  9        16 | CLK7FFD
                 BANK3 | 10        15 | /ROMCS
                 BANK1 | 11        14 | A14
                   GND | 12        13 | A15
                       |______________|
```

Entradas: 14 pinos dedicados. Saídas: 8, todas combinatórias com habilitação
permanente. Uso de termos-produto: 18 de 64 (28%) — sobra folga para
modificações.

## As equações

```
/ROMCS  = /MREQ * /A14 * /A15
/RAMCS  = /MREQ *  A15
CLK7FFD = /IORQ * /WR * /A15 * A5 * /A1
        + DIS128
SA14    =  A14 * A15 * BANK0
SA15    =  A14 * A15 * BANK1
        + /A14 * A15
SA16    =  A14 * A15 * BANK2
/SA17   =  A14 * A15 * BANK3 * /ZX512
SA18    =  A14 * A15 * BANK4 * /ZX512
```

Três detalhes que não são óbvios:

1. **`+ DIS128` no clock é a trava de paginação.** Quando o bit 5 da porta
   `0x7FFD` é setado, `CLK7FFD` fica preso em nível alto, o latch nunca mais é
   clocado e a paginação trava até o reset — exatamente o comportamento do
   Spectrum 128.
2. **O termo `/A14 * A15` de `SA15`** fixa o banco 2 na janela `0x8000-0xBFFF`,
   independente do que estiver no latch. Só `0xC000-0xFFFF` é paginado.
3. **`SA17` acumula duas funções.** No modo 512K é o bit A17 da SRAM. No modo
   128K (`ZX512` em nível alto, JP3 aberto) a saída fica permanentemente em
   nível alto e serve de `CE2` da `AS6C1008` — que é ativo alto no pino 30.

## Gravando

**Já vai pronto: [`tkmem128.jed`](tkmem128.jed).** Abra no programador, escolha o
dispositivo e grave. Não precisa montar nada.

| | |
| --- | --- |
| Arquivo | `tkmem128.jed` |
| Dispositivo | `GAL20V8B` (Lattice) ou `ATF20V8B` (Microchip) |
| Fusíveis | 2706 |
| **Checksum de fusíveis** | **`C5752`** |
| Programador | XGecu T48/T56 (Xgpro) ou equivalente |

Confira o checksum que o software do programador mostra ao abrir o arquivo: tem
que dar `C5752`. Se der outro valor, o arquivo foi corrompido no download.

### De onde vem esse arquivo

O `.jed` **não foi copiado de lugar nenhum** — é gerado por
[`tools/galgen.py`](../../tools/galgen.py) a partir das equações deste projeto:

1. O script monta o mapa de fusíveis do GAL20V8 diretamente das equações
   (matriz AND, polaridade das saídas, habilitação dos termos e bits de modo).
2. O mapa de colunas da matriz AND é **deduzido das próprias equações**, não
   chutado — e depois conferido por consistência entre as oito saídas.
3. O resultado é comparado, fusível a fusível, com o mapa de referência do
   projeto do Velesoft.

O resultado dessa comparação:

```
fusiveis divergentes: 0 de 2706
checksum de referencia: 5752
checksum reconstruido : 5752
```

Ou seja: está provado que o arquivo distribuído implementa **exatamente** as
equações documentadas aqui, e que essas equações são as mesmas do projeto
original. Para reproduzir a verificação você só precisa de um `.jed` de
referência e do Python:

```bash
python tools/galgen.py caminho/para/referencia.jed
```

### Montando a partir do fonte, se preferir

O [`tkmem128.pld`](tkmem128.pld) está em sintaxe **GALasm** (compatível com
`galasm`, derivado do GALer):

```bash
galasm tkmem128.pld
```

Vale lembrar que montadores diferentes podem escolher modos diferentes do GAL
(*simple* × *complex*) e produzir mapas distintos, ainda que funcionalmente
equivalentes. O `.jed` distribuído usa o modo **complex** (SYN=1, AC0=1), que é
o do projeto original.

### Peças que servem

| Peça | Situação |
| --- | --- |
| **GAL20V8B-15LP** (Lattice) | Descontinuada; ainda comum como estoque antigo |
| **ATF20V8B-15PC** (Microchip) | Substituta pino a pino, ainda distribuída |

Ambas são DIP-24 de 300 mil e gravam com o mesmo mapa de fusíveis.

## Mapa de colunas da matriz AND

Deduzido do mapa de fusíveis e confirmado pelas oito equações:

| Coluna | Sinal | | Coluna | Sinal |
| --- | --- | --- | --- | --- |
| 1 | `/ZX512` | | 24 | `BANK0` |
| 3 | `/MREQ` | | 28 | `BANK4` |
| 5 | `/A1` | | 32 | `BANK3` |
| 7 | `/WR` | | 34 / 35 | `A14` / `/A14` |
| 9 | `A5` | | 36 | `BANK1` |
| 12 | `DIS128` | | 38 / 39 | `A15` / `/A15` |
| 16 | `BANK2` | | 20 | `/IORQ` |

Quatro literais (`/IORQ`, `/WR`, `A5`, `/A1`) só aparecem juntos num mesmo termo
produto, então a atribuição entre eles é intercambiável — como AND é comutativo,
qualquer permutação dentro desse grupo dá o mesmo mapa de fusíveis.

## Modificando

Se for alterar as equações, lembre que:

- `SA14..SA18` precisam continuar sendo uma permutação bijetora sobre os bits de
  endereço alto da SRAM — qualquer embaralhamento entre eles é inofensivo, desde
  que consistente, porque nada mais acessa essa memória.
- O mesmo **não vale** para a EPROM: o conteúdo dela é fixo, então endereços e
  dados têm que ser 1:1 com o barramento.
- Sobram 46 termos-produto livres, mas apenas 8 saídas físicas.
