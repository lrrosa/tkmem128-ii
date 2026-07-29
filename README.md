# TKMEM-128 KiCad

Expansão externa de **128 KB (ou 512 KB) de RAM paginada no padrão ZX Spectrum 128**
para os micros brasileiros **TK90X e TK95** (clones do ZX Spectrum 48K, da
Microdigital). Redesenho completo em **KiCad 10**, com arquivos de fabricação
prontos.

> **Estado: projeto validado em software, ainda não montado em hardware.**
> ERC e DRC estão zerados e a netlist foi conferida contra a intenção de projeto,
> mas nenhuma placa foi fabricada nem testada num TK. Antes de mandar fabricar,
> leia [`docs/ANTES-DE-FABRICAR.md`](docs/ANTES-DE-FABRICAR.md) — há itens que
> dependem de medir peças físicas.
>
> O conector de borda é o **TE/AMP 5645235**, de entrada vertical. As cotas do
> footprint saíram do desenho de cliente e estão no
> [datasheet arquivado](docs/), mas ninguém montou a peça ainda.

---

## Este projeto é uma derivação

Ele não inventa o circuito: junta e redesenha dois trabalhos anteriores.

| Origem | Autor | O que veio de lá |
| --- | --- | --- |
| **external 128kb upgrade** (`zx48_to_128-EASY_3`), 2009 | **Velesoft** (Pavel Cimbal, República Tcheca) | O circuito base: as equações do GAL20V8, o latch da porta `0x7FFD` e o esquema de paginação da SRAM, incluindo a extensão de 512K |
| **TKMEM-128**, 2012 | **Luccas Eletrônica** (Eduardo Luccas, Brasil) | A adaptação ao TK90X/TK95: soquete de EPROM com a ROM do Spectrum 128, jumpers de seleção de ROM, a auto-desativação da RAM interna de 32K pelo pino 17 do barramento, e a divisão em placa principal + expansor |

Créditos também a **Flávio Matsumoto**, que sugeriu o circuito do Velesoft para
os TKs e identificou a caixa Patola PB 085/3, e a **Daniel Jose Viana
(danjovic)**, cujo trabalho documentou as cotas da placa para essa caixa.

Este redesenho é distribuído sob **CERN-OHL-S v2** (ver [LICENSE.txt](LICENSE.txt)),
uma licença *fortemente recíproca*: quem fabricar, modificar ou distribuir
precisa disponibilizar as fontes das modificações sob a mesma licença.

---

## O que a placa faz

O ZX Spectrum 128 difere do 48K em três coisas: 128K de RAM em 8 bancos de 16K,
o chip de som AY-3-8912, e o espelhamento da memória de vídeo ("shadow video").
Esta placa entrega **a primeira**. O som AY exige interface separada; o shadow
video é inviável numa interface externa, porque exigiria interceptar a RAM baixa
da ULA dentro do micro.

Na prática a grande maioria dos jogos de 128K funciona — a exceção são os poucos
títulos que dependem do shadow video.

### Mapa de memória

| Faixa | Quem responde |
| --- | --- |
| `0x0000-0x3FFF` | ROM — interna do TK, ou a 27C256 da placa (jumper) |
| `0x4000-0x7FFF` | RAM baixa **interna do TK** (memória de vídeo da ULA). Não é decodificada aqui |
| `0x8000-0xBFFF` | SRAM externa, **banco 2 fixo** |
| `0xC000-0xFFFF` | SRAM externa, banco selecionado pela porta `0x7FFD` |

Como a SRAM externa cobre `0x8000-0xFFFF`, **a RAM interna de 32K do TK precisa
ser desativada** — é a única alteração necessária dentro do micro. Veja
[`docs/PREPARAR-O-TK.md`](docs/PREPARAR-O-TK.md).

### Porta 0x7FFD

Um `74HCT273` latcheia o barramento de dados quando o GAL detecta a escrita na
porta (`A15=0`, `A5=1`, `A1=0`, `/IORQ` e `/WR` ativos):

| Bit | Sinal | Função |
| --- | --- | --- |
| 0–2 | `BANK0..BANK2` | Banco de RAM em `0xC000` |
| 3 | `VRAM` | Shadow screen — latcheado, **sem uso** nesta arquitetura (disponível em TP1) |
| 4 | `ROMA14` | Seleciona a metade da 27C256 |
| 5 | `DIS128` | Trava a paginação até o reset |
| 6–7 | `BANK3..BANK4` | Extensão 512K (só no modo ZX512) |

A trava do bit 5 é elegante: `DIS128` entra na equação do clock do latch
(`CLK7FFD = ... + DIS128`), então ao ser setado o clock fica preso em nível alto
e o latch nunca mais é acionado.

---

## As duas placas

A placa de componentes fica **em pé** dentro da caixa. O conector de borda é
soldado **diretamente nela** — e como esse conector é de entrada vertical
(o cartão entra perpendicular à placa que o segura), a fenda dele cai no plano
horizontal e recebe o cartão do TK.

Os terminais do conector são **retos** e atravessam a placa, sobrando ~3,18 mm
do outro lado em duas fileiras a 4,85 mm. A **tira de expansão** entra **entre
essas fileiras** — uma passa por cima dela, a outra por baixo — e é soldada
**dos dois lados**. Ela não tem conector nenhum: ilhas de solda nas duas faces
de um extremo, dedos de borda no outro.

```
        vista de lado, com a caixa em corte

              ┌─────────────────────────┐
              │                         │
              │   placa principal       │  em pé, 78,74 × 66,04 mm
              │   (componentes deste    │
              │    lado ─────────────►  │
              │                         │
        ┌─────┴─────┐  ╤════════════════╡
   TK ──┤  conector │══╪═ tira ═════════╪══► periféricos
        └─────┬─────┘  ╧════════════════╡   78,74 × 45 mm
              │      terminais retos,    │
              └──────a tira entra entre──┘
                     eles e solda dos       tudo no mesmo plano:
                     dois lados             degrau zero na corrente
```

> No conector, **1..28 fica na fileira de baixo** (junto à aresta inferior da
> placa), igual à fileira inferior do cartão do TK; 29..56 fica do lado de
> dentro.
>
> ⚠️ **O lado dos componentes tem que ficar virado para a tira de expansão**,
> nunca para o lado do conector. Ao contrário, a placa dentro da caixa esbarra
> no micro e não encaixa direito. Na prática o conector de borda é **o único
> componente do lado do cobre**: entra por baixo e é soldado por cima.

| Placa | Arquivo | Conteúdo |
| --- | --- | --- |
| Principal | [`hardware/tkmem128.kicad_pro`](hardware/) | GAL20V8B, 74HCT273, SRAM DIP-32, EPROM 27C256, 4 jumpers, desacoplamento e o conector de borda |
| Tira de expansão | [`hardware/expansor/`](hardware/expansor/) | Ilhas de solda nas duas faces de um lado, dedos de borda do outro — nenhum componente ativo |

A **placa principal é de 4 camadas**; a tira de expansão, de 2.

| Camada | Placa principal | Tira |
| --- | --- | --- |
| F.Cu | sinal | 27 retas de 1,5 mm (pinos 29..56) |
| In1.Cu | **plano de GND** inteiro | — |
| In2.Cu | **plano de +5V** inteiro | — |
| B.Cu | sinal | 27 retas de 1,5 mm (pinos 1..28) |

Como todos os componentes são passantes, cada ilha de `+5V` e de `GND` toca o seu
plano direto: **não há uma única trilha de alimentação nas faces de sinal**, e
nenhuma via serve só para alimentação. Sinal de 0,5 mm, isolação de 0,2 mm,
39 vias, e nenhum fio de ligação.

![Placa principal](docs/img/placa-principal.png)

O conector é passante e é usado pelos dois lados — por baixo entra o conector,
por cima solda a tira —, então a numeração dele está serigrafada nas duas
faces.

![Placa principal, verso](docs/img/placa-principal-verso.png)

![Tira de expansão](docs/img/placa-expansora.png)

A tira é soldada dos dois lados, então cada face traz a numeração dos **seus**
pinos: 29..56 na frente, 1..28 no verso.

![Tira de expansão, verso](docs/img/placa-expansora-verso.png)

---

## O que mudou em relação ao original

| Melhoria | Motivo |
| --- | --- |
| **Passagem do barramento** (dedos de borda na expansora) | O original ocupava o barramento; agora dá para encadear outros periféricos |
| **Desacoplamento por CI** (100 nF em cada um) + 10 µF de reservatório | O original tinha desacoplamento mínimo |
| **4 camadas com planos de GND e +5V inteiros** | Alimentação sem uma única trilha nas faces de sinal, retorno de corrente curto e imunidade a ruído. O original era de 2 camadas |
| **Trilha de sinal de 0,5 mm** | O dobro da primeira tentativa deste redesenho, e no mesmo patamar da placa original. Menos sujeito a erro de fabricação, curto e defeito difícil de achar |
| **Jumper JP2 com duas estratégias de ROMCS** | O `ROMCS` do barramento é **ativo em nível alto** para desligar a ROM interna, o oposto da saída `/ROMCS` do GAL. É a explicação mais provável para a ROM 128 do original "funcionar num TK e não em outro". JP2 permite escolher entre acionar pelo GAL ou fixar em nível alto (como fazem os cartuchos da Interface 2), com R5 em série |
| **Jumper de auto-desativação sem posição perigosa** | Na placa original o jumper tinha uma posição "Spectrum" que, num TK, **danificava o micro**. Aqui JP4 é simplesmente aberto/fechado, sempre no pino 17, com R4 de 1 kΩ em série limitando corrente. Ver [a análise do porquê](docs/PREPARAR-O-TK.md#a-diferença-em-relação-à-placa-original) |
| **GAL com `.jed` pronto e verificado** | O usuário não precisa montar nada: o `.jed` distribuído é gerado das equações deste projeto e conferido fusível a fusível contra o mapa de referência (checksum `C5752`, zero divergências) |
| **Degrau zero na corrente de periféricos** | A tira de expansão solda nos terminais do próprio conector, ficando coplanar com o cartão do TK. O periférico seguinte entra no mesmo plano, sem escadinha |
| **Bit N da porta 7FFD no flip-flop N** | O original embaralhava as entradas do latch; aqui a ordem é natural e o esquemático se lê sozinho |
| **Endereços e dados da EPROM 1:1** | Obrigatório (o conteúdo da ROM é fixo) e documentado |
| **Pontos de teste** (`VRAM`, `CLK7FFD`) | Para depurar sem grampear em perna de CI |
| **LED de energia** (opcional) | Diagnóstico imediato |
| **Solder jumpers SJ1/SJ2** | Terra extra opcional nos pinos 7 (ZX Spectrum) ou 15 (TK), que diferem entre as máquinas |
| **Peças em produção na BOM** | AS6C1008 e ATF20V8B no lugar de peças só encontráveis como estoque antigo |

---

## Configuração dos jumpers

| Jumper | Posição | Efeito |
| --- | --- | --- |
| **JP1** SELECIONA ROM | 1-2 | ROM 128: a EPROM da placa responde em `0x0000-0x3FFF` |
| | 2-3 | ROM TK: EPROM desligada (padrão) |
| **JP2** ROMCS BARRAMENTO | aberto | Usa a ROM interna do TK (padrão) |
| | 1-2 | Aciona `ROMCS` pelo GAL (comportamento da placa original) |
| | 2-3 | Fixa `ROMCS` em nível alto (estilo Interface 2) |
| **JP3** ZX128/ZX512 | aberto | 128K — SRAM `AS6C1008` (padrão) |
| | fechado | 512K — SRAM `AS6C4008` |
| **JP4** AUTO-DESATIVA 32K | fechado | Injeta nível 1 no pino 17 e desliga a RAM interna do TK |
| | aberto | Não mexe no barramento (padrão) |
| **SJ1** | aberto | Padrão — funciona em qualquer máquina |
| | fechado | Terra extra pelo pino 7. **Só em ZX Spectrum** |
| **SJ2** | aberto | Padrão — funciona em qualquer máquina |
| | fechado | Terra extra pelo pino 15. **Só em TK90X/TK95** |

> ⚠️ **JP1 em 1-2 sem JP2** não faz nada útil: sem desligar a ROM interna, os dois
> chips disputam o barramento de dados. Use os dois juntos ou nenhum.

> ⚠️ **JP4 em ZX Spectrum: deixe aberto.** No Spectrum os pinos 16, 17 e 18 são
> **Y, V e U do vídeo componente** — não são livres como no TK. Fechar JP4 lá joga
> 5 V em cima da saída V do codificador de vídeo.

### Os solder jumpers SJ1 e SJ2 são opcionais

**Nenhum dos dois é obrigatório.** Podem ficar abertos em qualquer máquina, que é
como a placa sai de fábrica e como ela foi validada.

O terra já chega pelos **pinos 6 e 14**, que são GND tanto no TK90X/TK95 quanto no
ZX Spectrum. SJ1 e SJ2 apenas **acrescentam** caminho de retorno usando pinos que
são GND em só uma das máquinas:

| | Pino | TK90X/TK95 | ZX Spectrum |
| --- | --- | --- | --- |
| **SJ1** | 7 | N.C. — **não feche** | GND — pode fechar |
| **SJ2** | 15 | GND — pode fechar | sinal — **não feche** |

Na dúvida, deixe os dois abertos. Nada deixa de funcionar; você só não ganha os
dois pinos de terra a mais.

---

## Lista de material

### Placa principal

| Ref | Valor | Encapsulamento | Observação |
| --- | --- | --- | --- |
| U1 | GAL20V8B ou **ATF20V8B-15PC** | DIP-24 300 mil | Grave [`hardware/gal/tkmem128.jed`](hardware/gal/tkmem128.jed) |
| U2 | 74HCT273 | DIP-20 300 mil | Latch da porta 7FFD |
| U3 | **AS6C1008-55PCN** (128K×8) | DIP-32 600 mil | Ou `AS6C4008-55PCN` (512K×8) no modo ZX512 |
| U4 | 27C256 | DIP-28 600 mil | **Opcional** — ver seção da ROM |
| R2, R4 | 1 kΩ | axial, vertical | |
| R5 | 0 Ω | axial, vertical | Fio; 100–470 Ω se houver disputa no ROMCS |
| R3 | 2,2 kΩ | axial, vertical | Opcional (LED) |
| C1–C5 | 100 nF cerâmico | disco 5 mm, passo 5 mm | |
| C6 | 10 µF eletrolítico | radial 5 mm, passo 2 mm | |
| D1 | LED 3 mm | | Opcional |
| JP1, JP2 | header 1×3 | passo 2,54 mm | |
| JP3, JP4 | header 1×2 | passo 2,54 mm | |
| J1 | **TE/AMP 5645235** — conector de borda 56 vias, entrada vertical | passo 2,54 mm, fileiras a 4,85 mm | Único componente do lado do cobre; recebe os dedos do TK |
| — | soquetes torneados DIP-20/24/28/32 | | Recomendado |

### Tira de expansão

Não leva conector nenhum — os "conectores" são cobre da própria PCB:

| Ref | O que é | Observação |
| --- | --- | --- |
| J1 | Ilhas de solda nas duas faces, até a borda | Solda nos terminais retos do conector da placa principal, por cima e por baixo |
| J2 | Dedos de borda | Passagem do barramento ao próximo periférico |
| C1 | 100 nF cerâmico | Único componente montado |

---

## Montagem

Guias detalhados:

- [`docs/PREPARAR-O-TK.md`](docs/PREPARAR-O-TK.md) — desativar a RAM interna de 32K
- [`docs/MONTAGEM.md`](docs/MONTAGEM.md) — ordem de montagem, guia do conector, caixa
- [`docs/ANTES-DE-FABRICAR.md`](docs/ANTES-DE-FABRICAR.md) — conferências obrigatórias

Dois pontos que costumam pegar quem monta:

1. **A guia do conector de borda.** O conector de 56 vias vem sem guia. Na
   posição **5/52** você encaixa um pedacinho de PCB (ou material equivalente)
   casando com o rasgo entre os dedos do TK — a placa não tem furos ali,
   porque não há terminal nessa posição. Sem a guia é fácil plugar deslocado
   e danificar o micro.
2. **A tira de expansão é soldada dos dois lados.** Ela entra entre as duas
   fileiras de terminais retos do conector — uma fileira por cima, outra por
   baixo — e as ilhas chegam até a borda, então o terminal encontra cobre
   mesmo se for curto.

---

## Fabricação

Arquivos prontos em [`production/`](production/): Gerber X2, furação Excellon,
BOM e mapa de posições, para as duas placas.

Especificação: **2 camadas**, 1,6 mm, trilha 0,25 mm, isolação 0,14 mm, furo
mínimo 0,3 mm. Está dentro da capacidade padrão de qualquer fábrica barata
(JLCPCB e PCBWay fazem 0,127 mm em 2 camadas), na faixa de preço mais baixa.

**A tira de expansão precisa de acabamento em ouro (ENIG) na placa inteira e
chanfro de 45° na borda dos dedos.** Os dedos entram e saem do conector do
periférico seguinte muitos ciclos, e as ilhas de solda do outro extremo também
chegam à borda — HASL descasca nos dois casos. Peça o chanfro explicitamente,
é um item à parte no pedido.

---

## Gravando o GAL

**Já vai pronto**: grave [`hardware/gal/tkmem128.jed`](hardware/gal/tkmem128.jed)
direto no programador. Checksum de fusíveis **`C5752`** — confira no software do
gravador ao abrir o arquivo.

Esse `.jed` não foi copiado de lugar nenhum: é gerado por
[`tools/galgen.py`](tools/galgen.py) a partir das equações deste projeto, e
conferido **fusível a fusível** contra o mapa de referência do projeto do
Velesoft — *zero divergências em 2706 fusíveis*. O fonte em sintaxe GALasm está
em [`tkmem128.pld`](hardware/gal/tkmem128.pld) para quem quiser modificar.

Programadores XGecu (T48/T56) gravam tanto GAL20V8B quanto ATF20V8B.

---

## A ROM do Spectrum 128

**A imagem da ROM não está neste repositório** — ela é copyright da Amstrad/Sky.
O hardware (soquete U4 + jumpers) está lá; a imagem você monta com as suas
cópias de `128-0.rom` e `128-1.rom`:

```bash
cat 128-0.rom 128-1.rom > rom_tkmem128_27c256.bin
```

A ordem importa: `A14` da EPROM vem de `ROMA14` (bit 4 da porta 7FFD), então a
ROM 0 (editor do 128) tem que ficar na metade baixa.

Vale dizer que **a ROM é dispensável**: o autor da TKMEM-128 original deixou de
fornecê-la depois de constatar que os jogos de 128K não dependem dela, e que ela
causava incompatibilidades entre unidades diferentes de TK90X.

---

## Estrutura do repositório

```
hardware/
  tkmem128.kicad_pro/.kicad_sch/.kicad_pcb   placa principal
  expansor/                                   tira de expansão
  lib/                                        símbolos e footprints próprios
  gal/                                        fonte e documentação do GAL
production/
  placa-principal/                            gerbers, furação, BOM, posições, PDF
  tira-expansao/                            idem
docs/
  PREPARAR-O-TK.md   MONTAGEM.md   ANTES-DE-FABRICAR.md
  relatorios/                                 saídas de ERC e DRC
tools/                                        geradores do projeto KiCad
```

A biblioteca de símbolos e footprints é **local ao projeto** — nada depende da
versão das bibliotecas do seu KiCad.

O projeto KiCad **nasceu gerado por script** a partir de uma descrição única da
netlist ([`tools/`](tools/)) — é o que garante que esquemático e placa não
divergem — e depois foi refinado à mão no KiCad. A fonte corrente são os
arquivos em `hardware/`; os geradores ficam como registro e ferramenta de apoio.

### Estado da verificação

| Placa | ERC | DRC | Ligações |
| --- | --- | --- | --- |
| Principal | 0 | 0 erros (6 avisos cosméticos) | 0 pendentes |
| Tira de expansão | 0 | 0 erros (4 avisos cosméticos) | 0 pendentes |

A netlist exportada pelo KiCad foi comparada nó a nó com a intenção de projeto
nas duas placas: **74 nets na principal e 53 na tira, zero divergência**.

---

## Licença

Hardware sob **CERN-OHL-S v2** — ver [LICENSE.txt](LICENSE.txt).

```
Copyright Leonardo Rosa e contribuidores.
Derivado de: "external 128kb upgrade" (Velesoft, 2009)
             TKMEM-128 (Luccas Eletrônica, 2012)

Este código-fonte é licenciado sob CERN-OHL-S v2 ou posterior.
Você pode redistribuí-lo e modificá-lo nos termos dessa licença.
Distribuído SEM QUALQUER GARANTIA, incluindo as de COMERCIALIZAÇÃO,
ADEQUAÇÃO A UM FIM ESPECÍFICO E NÃO-VIOLAÇÃO.
Consulte a CERN-OHL-S v2 para os termos aplicáveis.
```
