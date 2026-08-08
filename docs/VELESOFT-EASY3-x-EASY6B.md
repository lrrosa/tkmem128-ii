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

## O esquemático do `EASY_6b` contradiz o `.eqn` dele

Os `.sch` são binário do Eagle, mas exportados em PDF e rasterizados dão para
ler. E aí aparece uma inconsistência **dentro do próprio pacote deles**:

**A folha do `EASY_6b` imprime, no quadro verde de equações, o conjunto do
`EASY_3`** — `/RAMCS = /MREQ*A15` sem o `+ /MREQ*A14`, `SA14 = A14*A15*BANK0`
sem o `+ A14*/A15`, e `CLK7FFD = ... + DIS128` sem o `*ZX512`. Ou seja, o
desenho diz uma coisa e o arquivo de equações ao lado diz outra.

**Quem ganha é o `.eqn`**, e quem decide é a tabela de uso de termos do relatório
do compilador (`zx48_to_128-EASY_6b.log`), porque ela é o que de fato foi
compilado:

| Saída | Termos no log do `6b` | `EASY_3` teria | `.eqn` do `6b` tem |
| --- | --- | --- | --- |
| `ROMCS`, `SA17`, `SA18` | 1 | 1 | 1 |
| `SA14`, `SA16`, `RAMCS` | **2** | 1 | **2** |

A comparação é interna à mesma tabela, mesma ferramenta, mesma contagem: as três
saídas de uma equação só ficam em 1 termo, e justamente `SA14`, `SA16` e `RAMCS`
— as três que o `.eqn` do `6b` engorda — aparecem com 2. **O quadro de texto da
folha é que ficou para trás.**

## O resto do `EASY_6b` é o `EASY_3`

Lado a lado, as duas folhas têm os mesmos quatro blocos e a mesma fiação: o
conector `ZX-EDGET`, o `GAL 20V8`, o `74HCT273N` e a `SRAM 128 KB`. O que o
`6b` acrescenta é **dois LEDs** junto do jumper `ZX128/512` e **desacoplamento
melhor** (100 µF + 100 nF em vez de dois cerâmicos). O `.sch` ser 2,4× maior é
bagagem do Eagle, não circuito.

**E isso deixa a pergunta da ULA sem resposta por hardware:** não há hardware
adicional nenhum no `6b` para arbitrar `0x4000-0x7FFF` com a ULA, que continua
lendo a DRAM de dentro do micro. Se as equações do `.eqn` forem mesmo as de
produção, essa variante depende de alguma intervenção interna diferente, que o
pacote não documenta. Não sabemos qual.

Enquanto isso, a limitação que este projeto documenta continua valendo: **não há
shadow video aqui**, e os poucos jogos de 128K que dependem dele não funcionam.

## A nossa placa confere com a do Velesoft

Com o esquemático legível deu para comparar o que antes só se comparava pelas
equações. Duas diferenças, as duas deliberadas e nenhuma funcional:

**O latch da porta `0x7FFD`.** O Velesoft usa os flip-flops do `74HCT273` fora de
ordem: `D3` entra no FF1, `D6` no FF2, `D1` no FF3, e assim por diante. Nós
ligamos bit *n* no flip-flop *n*. O que importa é o mapeamento lógico, e ele é
**idêntico nos dois**:

| Bit | Função | Velesoft (pino de entrada → saída) | Nosso |
| --- | --- | --- | --- |
| 0 | `BANK0` | 8 → 9 | 3 → 2 |
| 1 | `BANK1` | 7 → 6 | 4 → 5 |
| 2 | `BANK2` | 14 → 15 | 7 → 6 |
| 3 | `VRAM` | 3 → 2 | 8 → 9 |
| 4 | `ROMA14` | 18 → 19 | 13 → 12 |
| 5 | `DIS128` | 17 → 16 | 14 → 15 |
| 6 | `BANK3` | 4 → 5 | 17 → 16 |
| 7 | `BANK4` | 13 → 12 | 18 → 19 |

`RESET` no `/CLR` (pino 1) e `CLK7FFD` no `CLK` (pino 11) são iguais.

**O endereçamento da SRAM.** O Velesoft **embaralha** as linhas: `A3` do micro vai
no `A2` da SRAM, `A2` no `A3`, `A7` no `A4`, `SA15` no `A8`, `SA14` no `A9`,
`SA16` no `A13`… Nós ligamos 1:1, `A0`→`A0` até `A13`→`A13` e `SA14`→`A14` até
`SA18`→`A18`.

Embaralhar é legítimo e é truque velho de roteamento: a SRAM não liga para qual
bit vai onde, desde que a ligação seja consistente. Com os 14 bits da CPU e os 5
do banco em posições fixas, cada valor de banco continua selecionando um conjunto
de 16 KB disjunto dos outros — só que não contíguo no endereço físico. Como nada
mais acessa essa SRAM, é invisível.

Ficamos no 1:1 porque a placa é de 4 camadas e o roteamento não precisou do
favor, e porque um mapa contíguo é mais fácil de depurar com analisador.

O resto bate: pinagem do GAL idêntica, `/RAMCS` no `/CS1`, `/SA17` no `CS2`
(que no `AS6C1008` é habilitação ativa em alto, e é por isso que essa saída do
GAL é invertida), `WR` no `/WE`, `RD` no `/OE`.

## Por que ficamos no `EASY_3`

Não é conservadorismo: é que a placa de 2012 do Luccas, da qual herdamos a
adaptação ao TK, os jumpers e a divisão em duas placas, é construída sobre o
`EASY_3`. Trocar as equações mudaria o que precisa ser desativado dentro do
micro — e é justamente essa a parte que já é específica de cada máquina e a que
mais tem chance de danificar alguma coisa se estiver errada.
