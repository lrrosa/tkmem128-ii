# GAL20V8B — decodificador da TKMEM-128

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

O arquivo [`tkmem128.pld`](tkmem128.pld) está em sintaxe **GALasm**
(compatível com `galasm`, derivado do GALer):

```bash
galasm tkmem128.pld
```

Isso gera `tkmem128.jed`, que você grava com um programador **XGecu T48/T56**
(software Xgpro) ou equivalente. Selecione o dispositivo `GAL20V8B` (Lattice) ou
`ATF20V8B` (Microchip), conforme o CI que comprou.

### Peças que servem

| Peça | Situação |
| --- | --- |
| **GAL20V8B-15LP** (Lattice) | Descontinuada; ainda comum como estoque antigo |
| **ATF20V8B-15PC** (Microchip) | Substituta pino a pino, ainda distribuída |

Ambas são DIP-24 de 300 mil e gravam com o mesmo mapa de fusíveis.

## Conferindo o resultado

> O `tkmem128.pld` é uma **reescrita em sintaxe moderna** das equações do
> Velesoft. Ele não foi conferido contra hardware.

Antes de confiar nele, vale comparar com o mapa de fusíveis de referência —
o `.jed` original do Velesoft, distribuído no pacote
`zx48_to_128-easy_3-gal.zip` da página do projeto dele
(<https://velesoft.speccy.cz/>).

```bash
galasm tkmem128.pld
# compare o bloco de fusíveis do tkmem128.jed gerado com o .jed de referência
```

O `.jed` de referência tem **checksum de fusíveis `C5752`**. Se o seu arquivo
gerado fechar nesse valor, a reescrita está fiel bit a bit.

Se der diferença, quase certamente é o **modo do GAL**: o original foi montado
em modo *complex* (saídas tristate com OE fixo em VCC); dependendo de como o
montador decide o modo, o mapa muda mesmo sendo funcionalmente equivalente.
Nesse caso, prefira gravar o `.jed` de referência do Velesoft — ele é o que
está comprovadamente funcionando em campo desde 2009.

## Modificando

Se for alterar as equações, lembre que:

- `SA14..SA18` precisam continuar sendo uma permutação bijetora sobre os bits de
  endereço alto da SRAM — qualquer embaralhamento entre eles é inofensivo, desde
  que consistente, porque nada mais acessa essa memória.
- O mesmo **não vale** para a EPROM: o conteúdo dela é fixo, então endereços e
  dados têm que ser 1:1 com o barramento.
- Sobram 46 termos-produto livres, mas apenas 8 saídas físicas.
