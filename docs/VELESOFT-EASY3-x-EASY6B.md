# As duas variantes do Velesoft: `EASY_3` e `EASY_6b`

Este projeto deriva da **`zx48_to_128-EASY_3`** do Velesoft (Pavel Cimbal, 2009).
Existe uma variante posterior, **`EASY_6b`**, que circula nos mesmos pacotes —
por exemplo em [goloskokovic/zx16to128upgrade](https://github.com/goloskokovic/zx16to128upgrade),
que credita o Velesoft e aponta para
[a página original](https://velesoft.speccy.cz/zx/external_128kb_upgrade/index.htm).

Esta página registra o que foi comparado, para ninguém precisar refazer.

## O `EASY_3` de terceiros é o mesmo que o nosso

Os cinco arquivos do `EASY_3` naquele repositório têm **exatamente o mesmo
tamanho** dos que estão preservados aqui, e as nossas cópias são as do pacote
original de 2009:

| Arquivo | Bytes |
| --- | --- |
| `zx48_to_128-EASY_3.sch` | 109 065 |
| `zx48_to_128-EASY_3.brd` | 23 427 |
| `zx48_to_128-easy_3.eqn` | 545 |
| `zx48_to_128-easy_3.jed` | 3 432 |
| `zx48_to_128-easy_3.log` | 3 318 |

O `.jed` daqui tem `QF2706` e checksum **`5752`**, e o `tools/galgen.py`
reconstrói esse mapa de fusíveis a partir das equações deste projeto com **zero
divergências**. Ou seja: o GAL que gravamos é o do Velesoft, bit a bit.

## O `EASY_6b` é outra arquitetura de memória

Comparando as equações lado a lado (`.eqn` de 545 contra 605 bytes):

| Saída | `EASY_3` — o nosso | `EASY_6b` |
| --- | --- | --- |
| `/ROMCS` | `/MREQ*/A14*/A15` | igual |
| `/RAMCS` | `/MREQ*A15` | **`+ /MREQ*A14`** |
| `CLK7FFD` | `/IORQ*/WR*/A15*A5*/A1 + DIS128` | **`+ DIS128*ZX512`** no lugar de `+ DIS128` |
| `SA14` | `A14*A15*BANK0` | **`+ A14*/A15`** |
| `SA15` | `A14*A15*BANK1 + /A14*A15` | igual |
| `SA16` | `A14*A15*BANK2` | **`+ A14*/A15`** |
| `/SA17` | `A14*A15*BANK3*/ZX512` | igual |
| `SA18` | `A14*A15*BANK4*/ZX512` | igual |

Duas mudanças de fundo:

**1. A janela `0x4000-0x7FFF` passa a ser decodificada.** No `EASY_3`, `RAMCS`
só responde com `A15=1`, então a SRAM externa cobre `0x8000-0xFFFF` e a faixa de
baixo continua sendo a RAM interna que a ULA lê. No `EASY_6b`, `RAMCS` também
responde com `A14=1`; e como `SA14` e `SA16` ganham o termo `A14*/A15`, nessa
janela o endereço de banco vira `SA = 0b101` — **banco 5**, que é justamente o
banco de tela do Spectrum 128.

**2. A trava de paginação fica condicionada ao modo.** No `EASY_3`, setar o bit 5
(`DIS128`) prende o clock do latch em nível alto e a paginação trava até o reset,
em qualquer modo. No `EASY_6b` isso só acontece com `ZX512` ativo — o que faz
sentido, porque no modo 512K os bits 6 e 7 da porta continuam sendo necessários.

## O que NÃO foi verificado

**Como o `EASY_6b` convive com a ULA.** Mapear banco 5 em `0x4000-0x7FFF` é o que
o Spectrum 128 faz, mas ali a ULA lê a mesma RAM que a CPU escreve. Numa
interface externa a ULA continua lendo a DRAM de dentro do micro, e as equações
sozinhas não dizem como isso é resolvido — se é resolvido. Responder exigiria ler
o esquemático, e o `.sch` é **binário do Eagle**, não dá para diffar como texto.
Sinal de que há mais coisa lá: o `.sch` do `EASY_6b` tem 266 KB contra 109 KB do
`EASY_3`, e o repositório traz uma pasta `AY/`.

Enquanto isso não for verificado, a limitação que este projeto documenta continua
valendo: **não há shadow video aqui**, e os poucos jogos de 128K que dependem
dele não funcionam.

## Por que ficamos no `EASY_3`

Não é conservadorismo: é que a placa de 2012 do Luccas, da qual herdamos a
adaptação ao TK, os jumpers e a divisão em duas placas, é construída sobre o
`EASY_3`. Trocar as equações mudaria o que precisa ser desativado dentro do
micro — e é justamente essa a parte que já é específica de cada máquina e a que
mais tem chance de danificar alguma coisa se estiver errada.
