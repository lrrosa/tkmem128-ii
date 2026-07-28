# Antes de mandar fabricar

Este projeto foi validado em software: **ERC e DRC zerados, netlist conferida
item a item contra a intenção de projeto**. Mas nenhuma placa foi fabricada nem
testada num TK real.

Os itens abaixo dependem de medir peças físicas ou de decisões que não dá para
verificar de dentro do KiCad. Confira antes de gastar dinheiro com PCB.

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
montador encaixa ali, casando com o rasgo entre os dedos do TK. Como não há
terminal nessa posição, o footprint tem **54 furos**, não 56.

**Verifique antes de fabricar:** confira com paquímetro as duas fileiras
(4,85 mm) e o furo (1,02 mm) no conector que você comprou. Modelos de outros
fabricantes variam.

---

## 1b. Orientação: componentes virados para a tira (CRÍTICO)

O conector é de **entrada vertical** — o cartão entra perpendicular à placa em
que ele está soldado. Por isso ele vai na placa **em pé**, e a fenda cai no
plano horizontal para receber o cartão do TK.

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
| a **de baixo**, junto à aresta inferior da placa | **1..28** | fileira de baixo do TK |
| a **de cima**, do lado de dentro da placa | **29..56** | fileira de cima do TK |

Ou seja: o pino 1 (`A14`) fica embaixo, junto da borda. É a mesma orientação
física do cartão do TK, onde 1..28 é a fileira inferior.

Trocar as duas inverte a placa inteira e **pode danificar o micro** (alimentação
onde deveriam estar sinais).

Repare que o conector é montado **pelo lado do cobre**: no projeto ele está na
camada `B.Cu`, o que espelha o footprint — inserir a peça pelo outro lado
inverte a ordem das colunas *e* troca as duas fileiras. É a consequência física
de enfiar o conector por baixo, e é justamente por isso que este teste existe.

**O que fazer:** antes de soldar qualquer CI, monte só o conector `J1` na placa
principal e faça um teste de continuidade com o TK **desligado e desconectado**:

1. Encaixe a placa nos dedos do TK.
2. Meça continuidade entre o contato **3** do soquete (que deve ser +5 V) e o
   ponto de +5 V do TK.
3. Meça o contato **6** (GND) contra o terra do TK.

Se +5 V e GND aparecerem trocados ou em contatos inesperados, a fileira está
invertida: gire o footprint 180° no eixo Y (troque as fileiras) e regenere.

---

## 3. A guia do conector

O conector de 56 vias vem **sem guia**. Onde ficariam os contatos **5 e 52**
você precisa encaixar um pedacinho de PCB (ou material equivalente, ~1,6 mm) que
sirva de guia, casando com o rasgo entre os dedos da placa do TK.

Sem isso, é fácil plugar deslocado por uma posição — e aí sinais e alimentação
vão para os lugares errados.

---

## 4. Acabamento dos dedos de borda

**Onde:** tira de expansão, `J2`.

Peça explicitamente à fábrica:

- **ENIG (ouro)** nos dedos — HASL descasca com a inserção repetida
- **chanfro de 45°** na borda dos dedos (às vezes chamado *gold finger
  beveling*); costuma ser item separado no pedido

O ENIG vale para a tira inteira: as ilhas de solda do outro extremo (`J1`)
também chegam à borda e ficam melhor sem HASL.

Sem chanfro, a placa entra forçando e arranha os contatos do conector do TK.

---

## 5. Polaridade do ROMCS

**Onde:** placa principal, `JP2`.

O sinal `ROMCS` do barramento (pino 25) é **ativo em nível alto** para desligar a
ROM interna, enquanto a saída do GAL (`/ROMCS`) é ativa em nível baixo. JP2
oferece as duas estratégias, mas **qual funciona no seu TK só o teste dirá**:

| JP2 | Comportamento |
| --- | --- |
| aberto | ROM do TK (comece por aqui) |
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

### Por que a placa não tem furos de fixação

As torres ficam em **x = 39,37 mm** (centro) e **y = 4,02 e 62,02 mm** nas
coordenadas da placa. Nenhuma das duas dá para usar:

- A de **y = 62,02** cai exatamente sobre o conector `J1` — é a que se desgasta
  com micro-retífica ao abrir a fenda.
- A de **y = 4,02** cai numa área livre de componentes, mas bem no meio do leque
  de trilhas que sai do header para os CIs. Um furo Ø2,7 ali foi testado e custa
  duas ligações que o roteador não consegue fechar. A placa 100% roteada vale
  mais que um parafuso.

A fixação é por **EVA**, como na montagem original. Se você quiser mesmo o furo,
as coordenadas estão aí e os geradores estão em [`tools/`](../tools/) — é só
acrescentar e reproduzir o roteamento.

### O conjunto montado também cabe — mas só com a fenda aberta

O corpo do conector (15,49 mm) e a tira de expansão ficam **fora** do contorno
da tampa, na fenda cortada na base. Isso é inerente ao formato e é o que a
montagem original faz.

### Comprimento da tira de expansão

A tira sai da placa principal e atravessa a caixa pelo eixo de **32 mm**, indo
até fora para os dedos de passagem. Com **45 mm** ela cobre a travessia e ainda
sobra o suficiente do lado de fora. O conector do TK fica na frente, do lado
oposto — a tira não precisa alcançá-lo.

### Adaptação da caixa

Conforme documentado por Eduardo Luccas: abra duas fendas na base — uma maior
para o soquete de borda e uma menor para a passagem —, desgaste com
micro-retífica a torre que cair dentro da fenda, e fixe com **pedaços de EVA**
colados no fundo e nas laterais. A caixa fecha com trava, então o EVA segura bem.

---

## 8. Regras de fabricação

| Parâmetro | Valor |
| --- | --- |
| Camadas | 2 |
| Espessura | 1,6 mm |
| Trilha | 0,25 mm (0,6 mm em `+5V` e `GND`) |
| Isolação | **0,14 mm** |
| Furo mínimo | 0,3 mm |
| Via | 0,7 mm com furo de 0,35 mm |

A isolação de 0,14 mm é o que permitiu fechar as duas placas em 2 camadas. Está
dentro da capacidade **padrão** de fábrica barata (JLCPCB e PCBWay especificam
0,127 mm em 2 camadas), mas é apertado demais para corrosão caseira — se você for
fazer em casa, vai precisar redesenhar com folga maior.

---

## Resumo

| Item | Risco se errar |
| --- | --- |
| 1. Cotas do conector | Conector não entra na placa |
| 1b. Orientação invertida | A placa esbarra no micro e não encaixa |
| 2. Fileira invertida | **Pode danificar o TK** |
| 3. Chaveta | **Pode danificar o TK** |
| 4. Acabamento dos dedos | Contato ruim, desgaste rápido |
| 5. ROMCS | ROM 128 instável (só afeta quem usa a EPROM) |
| 5b. Alinhamento das placas | **Barramento invertido ponta a ponta** — ERC/DRC não pegam |
| 6. Tira soldada | Empilhar conector reintroduz o degrau |
| 7. Caixa | Não fecha |
| 8. Regras de fabricação | Curto ou trilha aberta se a fábrica não atender 0,14 mm |
