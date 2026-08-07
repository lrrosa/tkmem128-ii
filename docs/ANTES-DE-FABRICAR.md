# Antes de mandar fabricar

Este projeto foi validado em software: **ERC e DRC zerados, netlist conferida
item a item contra a intenção de projeto**. Mas nenhuma placa foi fabricada nem
testada num micro real.

Os itens abaixo dependem de medir peças físicas ou de decisões que não dá para
verificar de dentro do KiCad. Confira antes de gastar dinheiro com PCB.

> **Conferência em papel — julho de 2026.** As duas placas foram impressas em
> escala 1:1 e comparadas com as peças reais. **Todas as medidas e alinhamentos
> bateram**, com uma correção: o rasgo da guia da tira passou de 5,0 para
> **7,0 mm** de profundidade (item 3). Isso confirma as cotas do conector, o
> tamanho das placas e o encaixe na caixa — mas *não* substitui o teste de
> continuidade com a placa fabricada, antes de plugar no micro.

---

## 1. O conector de borda (cotas do datasheet)

**Onde:** placa principal, conector `J1`.

O conector é o **TE / AMP 5645235, "Standard Edge II", passo 2,54 mm**
(desenho de cliente arquivado em [`docs/`](.)). Cotas usadas no footprint:

| Dimensão | Valor |
| --- | --- |
| Passo entre contatos | 2,54 mm [.100] |
| **Distância entre as duas fileiras de terminais** | **4,85 mm [.191]** |
| **Furo recomendado na PCB** | **1,02 ± 0,08 mm [.040]** |
| Aceita placa de | 1,37 – 1,78 mm [.054–.070] |
| Altura do corpo acima da placa | 15,49 mm [.610] |
| Terminal abaixo da placa | 3,18 ± 0,51 mm [.125] |
| Largura do corpo | 9,35 mm [.368] |
| Chanfro da entrada | 1,52 × 45° [.060] |

A **guia** ocupa a posição das vias 5 e 52 — é um pedacinho de PCB que o
montador encaixa ali, casando com o rasgo entre os dedos do micro. Como não há
terminal nessa posição, o footprint tem **54 furos**, não 56.

**Onde a furação cai em relação à aresta.** A fileira de baixo (pinos 1–28) fica
a **2,885 mm** da aresta inferior — 2,135 mm de cobre até a borda. Não é sobra
gratuita: o corpo do conector tem 10 mm de fundo, e nessa posição ele termina
**0,31 mm dentro** do contorno da placa. Numa versão anterior a furação estava
1,5 mm mais para baixo, e o corpo sobrava 1,19 mm para fora — o contorno da PCB
cortava o conector, restavam 0,635 mm de cobre até a aresta e a serigrafia dele
tinha que ser um "U" aberto. A medida de 1,5 mm veio de conferir interfaces reais
de TK90X.

**Conferido em papel (jul/2026)** contra o conector real: as duas fileiras
(4,85 mm) e o furo (1,02 mm) batem. Ainda assim, **confira com paquímetro o
conector que você comprou** — modelos de outros fabricantes variam, e é aqui que
uma divergência de décimos custa a placa inteira.

---

## 1b. Orientação: componentes virados para a tira (CRÍTICO)

O conector é de **entrada vertical** — a placa que entra fica perpendicular
àquela em que ele está soldado. Por isso ele vai na placa **em pé**, e a fenda cai no
plano horizontal para receber a placa do micro.

O corpo do conector fica de **um** lado da placa e os terminais atravessam para
o **outro**, onde a tira de expansão é soldada.

> ⚠️ **O lado dos componentes tem que ficar virado para a tira de expansão.**
> Se a placa for montada ao contrário, com os componentes do lado do conector,
> ela esbarra no micro dentro da caixa e não encaixa direito.

Consequência prática: o conector é **o único componente do lado do cobre** da
placa principal. Você o encaixa por baixo e solda por cima, pelo lado dos
componentes. No projeto ele está atribuído à camada `B.Cu`, e é assim que
aparece na serigrafia do verso.

---

## 2. Qual fileira do conector é qual (CRÍTICO)

**Onde:** placa principal, conector `J1`.

O projeto assume, com a placa **em pé** e o conector na borda de baixo:

| Fileira de terminais | Pinos | Corresponde a |
| --- | --- | --- |
| a **de baixo**, junto à aresta inferior da placa | **1..28** | fileira de baixo do micro (fileira B no ZX Spectrum) |
| a **de cima**, do lado de dentro da placa | **29..56** | fileira de cima do micro (fileira A no ZX Spectrum) |

Ou seja: o pino 1 (`A14`) fica embaixo, junto da borda. É a mesma orientação
física da placa do micro, onde 1..28 é a fileira inferior.

Trocar as duas inverte a placa inteira e **pode danificar o micro** (alimentação
onde deveriam estar sinais).

Repare que o conector é montado **pelo lado do cobre**: no projeto ele está na
camada `B.Cu`, o que espelha o footprint — inserir a peça pelo outro lado
inverte a ordem das colunas *e* troca as duas fileiras. É a consequência física
de enfiar o conector por baixo, e é justamente por isso que este teste existe.

**O que fazer:** antes de soldar qualquer CI, monte só o conector `J1` na placa
principal e faça um teste de continuidade com o micro **desligado e desconectado**:

1. Encaixe a placa nos dedos do micro.
2. Meça continuidade entre o contato **3** do soquete (+5 V nas duas máquinas) e
   o ponto de +5 V do micro.
3. Meça o contato **6** (GND) contra o terra do micro.

Se +5 V e GND aparecerem trocados ou em contatos inesperados, a fileira está
invertida: gire o footprint 180° no eixo Y (troque as fileiras) e regenere.

---

## 3. A guia do conector

O conector de 56 vias vem **sem guia**. Onde ficariam os contatos **5 e 52**
você precisa encaixar um pedacinho de PCB (ou material equivalente, ~1,6 mm) que
sirva de guia, casando com o rasgo entre os dedos da placa do micro.

Sem isso, é fácil plugar deslocado por uma posição — e aí sinais e alimentação
vão para os lugares errados.

Do outro lado da corrente, a **tira** tem o rasgo correspondente entre os dedos
de `J2`: 1,8 mm de largura por **7,0 mm de profundidade**, centrado em
x = 63,50. A profundidade foi conferida contra a placa real em julho de 2026
(impressão em papel 1:1) — os 5,0 mm iniciais não chegavam ao fundo da guia.

Se algum dia precisar de mais profundidade, saiba que **restam só 0,62 mm**: os
dedos começam em y = 37,38 e o rasgo já vai até y = 38,00. Passar disso obriga a
encurtar os dedos também. A folga lateral para o cobre mais próximo (pinos 4, 6,
51 e 53) é de 0,88 mm.

O valor mora em `KEYSLOT_DEPTH`, em `tools/netlist_exp.py`; para aplicar numa
placa já roteada use `tools/ajusta_guia.py`, que refaz o contorno e repreenche
as zonas.

---

## 3b. A placa principal é de 4 camadas (CRÍTICO no pedido)

**Onde:** `production/placa-principal/gerbers.zip`.

Peça **4 camadas**, empilhamento padrão de 1,6 mm:

| Gerber | Papel |
| --- | --- |
| `tkmem128-ii-F_Cu.gbr` | sinal, lado dos componentes |
| `tkmem128-ii-In1_Cu.gbr` | **plano de GND** |
| `tkmem128-ii-In2_Cu.gbr` | **plano de +5V** |
| `tkmem128-ii-B_Cu.gbr` | sinal, lado do cobre |

Se pedir 2 camadas por engano, a fábrica descarta os dois planos e a placa sai
sem alimentação nenhuma — e isso não aparece na inspeção visual. Confira no
formulário antes de fechar.

A **tira de expansão continua de 2 camadas** e é pedida separadamente
(`production/tira-expansao/gerbers.zip`).

---

## 4. Acabamento dos dedos de borda

**Onde:** tira de expansão, `J2`.

Peça explicitamente à fábrica:

- **ENIG (ouro)** nos dedos — HASL descasca com a inserção repetida
- **chanfro de 45°** na borda dos dedos (às vezes chamado *gold finger
  beveling*); costuma ser item separado no pedido

O ENIG vale para a tira inteira: as ilhas de solda do outro extremo (`J1`)
também chegam à borda e ficam melhor sem HASL.

Sem chanfro, a placa entra forçando e arranha os contatos do conector do micro.

---

## 5. Polaridade do ROMCS

**Onde:** placa principal, `JP2`.

O sinal `ROMCS` do barramento (pino 25) é **ativo em nível alto** para desligar a
ROM interna, enquanto a saída do GAL (`/ROMCS`) é ativa em nível baixo. JP2
oferece as duas estratégias, mas **qual funciona no seu micro só o teste dirá**:

| JP2 | Comportamento |
| --- | --- |
| aberto | ROM interna do micro (comece por aqui) |
| 1-2 | Aciona `ROMCS` pela saída do GAL — comportamento da placa original |
| 2-3 | Fixa `ROMCS` em nível alto, estilo cartucho da Interface 2 |

`R5` fica em série. Comece com 0 Ω (fio). Se houver disputa de barramento
(imagem instável, travamentos ao usar a ROM 128), troque por 100–470 Ω.

Se você não vai usar a EPROM — e ela é dispensável, ver o README — deixe JP1 em
2-3 e JP2 aberto e nada disso importa.

---

## 5b. Alinhamento entre as duas placas (CRÍTICO)

Os dois layouts correm no **mesmo sentido de X**: a principal fica em pé com os
componentes virados para trás, a tira fica deitada com o cobre de cima virado
para cima e sai para trás. Logo, vistos nos respectivos layouts do KiCad:

| | Coluna do pino 1 | Guia (coluna sem contato) |
| --- | --- | --- |
| Conector `J1` da principal | x = 73,66 mm | x = 63,50 mm |
| Ilhas `J1` da tira | x = 73,66 mm | x = 63,50 mm |
| Dedos `J2` da tira | x = 73,66 mm | x = 63,50 mm |

Se a tira for desenhada espelhada, tudo continua com ERC e DRC zerados — os
dois projetos são válidos isoladamente — e a placa só falha na bancada, com o
barramento invertido ponta a ponta.

**Verificação automática:** rode
[`tools/confere_alinhamento.py`](../tools/confere_alinhamento.py) depois de
qualquer mexida em footprint, rotação ou posicionamento de conector. Ele
confere as colunas, a guia, as faces das fileiras e qual fileira fica junto à
aresta, e falha alto se algum invariante quebrar.

---

## 6. A tira de expansão é soldada, não encaixada

**Onde:** tira de expansão, `J1`.

A tira **não tem conector**. Os terminais do conector são **retos** e ficam em
duas fileiras a 4,85 mm; a tira entra **entre elas**, com uma fileira passando
por cima e a outra por baixo.

Por isso ela tem ilhas de solda nas **duas faces**, nas mesmas posições
(`J1`, 54 vias, passo 2,54 mm, sem furos), e **a solda é feita dos dois lados**:
por cima e por baixo. Do outro extremo ficam os dedos de borda (`J2`) para o
próximo periférico.

As ilhas **chegam até a aresta da tira** e entram 5 mm. Os terminais do TE
5645235 avançam 3,18 ± 0,51 mm, mas há conectores com terminal mais curto — com
a ilha começando na borda, o terminal encontra cobre em qualquer caso, e a
solda fica fácil independentemente de quanto a tira entra.

Isso é o que mantém tudo coplanar. Não substitua por um header: qualquer
conector empilhado reintroduz o degrau.

---

## 7. Caixa Patola PB 085/3

Conferido contra os desenhos técnicos da Patola (`PB 085/3_CX` e `PB 085/3_TP`).

| Medida | Valor |
| --- | --- |
| Caixa fechada (externo) | 32 × 73 × 85 mm |
| Tampa: área interna onde a placa assenta | **81 × 69 mm** |
| Tampa: profundidade interna | 6 mm |
| Caixa (metade funda): interna | 83 × 71 × 25 mm |
| Torres de fixação | Ø5 externo, furo Ø2,5, **58 mm entre centros**, centradas |

### A placa principal cabe

| | Disponível | Usado | Folga |
| --- | --- | --- | --- |
| Largura | 81 mm | 78,74 mm | 1,13 mm por lado |
| Altura | 69 mm | 66,04 mm | 1,48 mm por lado |
| Altura de componentes | ~25 mm | ~10 mm (soquete torneado + DIP) | ~15 mm |

### O furo de fixação `H1` — e por que só existe um

As torres ficam em **x = 39,37 mm** (centro) e **y = 4,02 e 62,02 mm** nas
coordenadas da placa, medidas conferidas contra a caixa real em impressão 1:1.
Só uma das duas serve:

- A de **y = 62,02** cai exatamente sobre o conector `J1`. É a que se desgasta
  com micro-retífica ao abrir a fenda — não tem como ser furo.
- A de **y = 4,02** virou `H1`, um furo **Ø2,7 não metalizado**. Enquanto a placa
  era de 2 camadas ele custava duas ligações que o roteador não fechava; com as
  faces de sinal livres de alimentação ele passou a caber, e o leque de trilhas
  que passava por ali desviou para o vão entre o furo e a aresta de cima.

Três coisas a saber antes de usar o parafuso:

1. **Ø2,7 é o teto.** Acima disso o furo entra no *courtyard* do soquete de U4,
   que termina a 1,42 mm do centro. O cobre não é o limite — sobra 0,72 mm até a
   ilha `U4.15`; o soquete é.
2. **A folga da cabeça do parafuso não está garantida.** É justamente por isso
   que `H1` não tem courtyard: declarar um seria mentir. Com o soquete de U4 a
   1,42 mm, cabeça de parafuso comum encosta nele. Meça no seu conjunto antes de
   contar com o parafuso; a fixação por **EVA** continua valendo sozinha.
3. **Use parafuso de náilon, ou uma arruela isolante.** A placa tem plano de GND
   em `In1.Cu` e plano de +5 V em `In2.Cu`. O furo mantém os dois 0,5 mm longe da
   parede (área de exclusão desenhada na placa, não é só a folga da regra), mas
   parafuso metálico raspando a parede de uma placa de 4 camadas pode arrastar
   cobre de um plano ao outro — e isso é +5 V em curto com o terra.

Com uma torre só, o que segura a placa é o parafuso numa ponta e a fenda frontal
na outra, onde o corpo do conector atravessa. Continua valendo colar **EVA** no
fundo e nas laterais, como na montagem original.

> Na furação, `H1` sai no mesmo `.drl` dos outros furos, declarado como
> `NonPlated,NPTH` (o arquivo é `MixedPlating`). Se a sua fábrica ignorar o
> atributo e metalizar tudo, não há curto: nenhum cobre chega à parede do furo em
> nenhuma das quatro camadas. Só avise, porque metalizado ele fica com a parede
> mais estreita.

### O conjunto montado também cabe — mas só com a fenda aberta

O corpo do conector (15,49 mm) e a tira de expansão ficam **fora** do contorno
da tampa, na fenda cortada na base. Isso é inerente ao formato e é o que a
montagem original faz.

### Comprimento da tira de expansão

A tira sai da placa principal e atravessa a caixa pelo eixo de **32 mm**, indo
até fora para os dedos de passagem. Com **45 mm** ela cobre a travessia e ainda
sobra o suficiente do lado de fora. O conector do micro fica na frente, do lado
oposto — a tira não precisa alcançá-lo.

### Adaptação da caixa

Conforme documentado por Eduardo Luccas: abra duas fendas na base — uma maior
para o soquete de borda e uma menor para a passagem —, desgaste com
micro-retífica a torre que cair dentro da fenda, e fixe com **pedaços de EVA**
colados no fundo e nas laterais. A caixa fecha com trava, então o EVA segura bem.

---

## 8. Regras de fabricação

| Parâmetro | Placa principal | Tira de expansão |
| --- | --- | --- |
| Camadas | **4** | 2 |
| Espessura | 1,6 mm | 1,6 mm |
| Trilha | 0,5 mm | 1,5 mm |
| Isolação | 0,2 mm | 0,25 mm |
| Furo mínimo | 0,3 mm | sem furos |
| Via | 0,8 mm / furo 0,4 mm | nenhuma |
| Ilha do conector | 1,50 mm / furo 1,02 mm | — |

Nada disso é apertado: 0,2 mm de isolação e 0,5 mm de trilha estão muito acima do
mínimo de qualquer fábrica barata (JLCPCB e PCBWay especificam 0,127 mm). Uma
versão anterior deste projeto usava 0,25 mm de trilha com 0,14 de isolação para
caber em 2 camadas — foi abandonada justamente por ser apertada demais para
inspeção e retrabalho.

A **ilha de 1,50 mm no conector** não é arbitrária: com os 1,75 mm iniciais
sobravam 0,79 mm entre ilhas vizinhas, e nenhum sinal conseguia sair da fileira
de baixo (a fuga passa entre duas ilhas da fileira de cima, e uma trilha de
0,5/0,2 precisa de 0,90 mm). Se for mexer no footprint do conector, **não reduza
o vão abaixo de 0,90 mm**.

---

## Resumo

| Item | Risco se errar |
| --- | --- |
| 1. Cotas do conector | Conector não entra na placa |
| 1b. Orientação invertida | A placa esbarra no micro e não encaixa |
| 2. Fileira invertida | **Pode danificar o micro** |
| 3. Chaveta | **Pode danificar o micro** |
| 3b. Pedir 2 camadas em vez de 4 | **Placa sem alimentação** — não aparece na inspeção visual |
| 4. Acabamento dos dedos | Contato ruim, desgaste rápido |
| 5. ROMCS | ROM 128 instável (só afeta quem usa a EPROM) |
| 5b. Alinhamento das placas | **Barramento invertido ponta a ponta** — ERC/DRC não pegam |
| 6. Tira soldada | Empilhar conector reintroduz o degrau |
| 7. Caixa | Não fecha |
| 8. Regras de fabricação | Nenhuma folga é apertada; conferir só se a fábrica for muito básica |
