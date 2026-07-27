# Antes de mandar fabricar

Este projeto foi validado em software: **ERC e DRC zerados, netlist conferida
item a item contra a intenção de projeto**. Mas nenhuma placa foi fabricada nem
testada num TK real.

Os itens abaixo dependem de medir peças físicas ou de decisões que não dá para
verificar de dentro do KiCad. Confira antes de gastar dinheiro com PCB.

---

## 1. O padrão de furação do soquete de borda (CRÍTICO)

**Onde:** placa expansora, conector `J1`.

O footprint usa a grade industrial de conectores de borda de passo 0,1":

| Dimensão | Valor adotado |
| --- | --- |
| Passo entre contatos | 2,54 mm (0,100") |
| Distância entre as duas fileiras de terminais | **5,08 mm (0,200")** |
| Furo | 1,0 mm (terminal típico é 0,635 mm quadrado) |

Essa é a grade padrão da família (EDAC, Sullins e similares especificam
"0.100 C-C × 0.200 grid, solder tail 0.025 square"), mas **modelos variam**.

**O que fazer:** com o conector em mãos, meça a distância entre as duas fileiras
de terminais. Se não for 5,08 mm, ajuste `hardware/lib/tkmem128.pretty/ZX_TK_Bus_Socket_56.kicad_mod`
(a variável `yf`/`yr` no gerador, ou os pads diretamente) antes de gerar os
gerbers.

---

## 2. Qual fileira do soquete é qual (CRÍTICO)

**Onde:** placa expansora, conector `J1`.

O projeto assume:

- fileira de terminais **mais próxima da borda frontal** → pinos **1..28**
  (fileira de baixo do TK)
- fileira **mais afastada** → pinos **29..56** (fileira de cima do TK)

Trocar as duas inverte a placa inteira e **pode danificar o micro** (alimentação
onde deveriam estar sinais).

**O que fazer:** antes de soldar qualquer CI, monte só o soquete `J1` na
expansora e faça um teste de continuidade com o TK **desligado e desconectado**:

1. Encaixe a expansora nos dedos do TK.
2. Meça continuidade entre o contato **3** do soquete (que deve ser +5 V) e o
   ponto de +5 V do TK.
3. Meça o contato **6** (GND) contra o terra do TK.

Se +5 V e GND aparecerem trocados ou em contatos inesperados, a fileira está
invertida: gire o footprint 180° no eixo Y (troque as fileiras) e regenere.

---

## 3. A chaveta do soquete

O soquete de 56 vias vem **sem chaveta**. Onde ficariam os contatos **5 e 52**
você precisa encaixar um pedacinho de PCB (ou material equivalente, ~1,6 mm) que
sirva de guia, casando com o rasgo entre os dedos da placa do TK.

Sem isso, é fácil plugar deslocado por uma posição — e aí sinais e alimentação
vão para os lugares errados.

---

## 4. Acabamento dos dedos de borda

**Onde:** placa expansora, `J2`.

Peça explicitamente à fábrica:

- **ENIG (ouro)** nos dedos — HASL descasca com a inserção repetida
- **chanfro de 45°** na borda dos dedos (às vezes chamado *gold finger
  beveling*); costuma ser item separado no pedido

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

## 6. Conector angular na placa principal

**Onde:** placa principal, `J1`.

A placa principal fica **em pé** e a expansora **deitada**. Para isso, `J1` tem
que ser um **soquete fêmea 2×28 angular** (*right angle*), não um vertical — o
land pattern é o mesmo, mas o corpo precisa sair perpendicular à placa.

Na expansora, `J3` é um **header macho 2×28 vertical** comum.

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

O `J1` angular e a placa expansora ficam **abaixo** da linha da tampa, dentro da
fenda cortada na base. Isso é inerente ao formato e é o que a montagem original
faz.

### A expansora precisa ser mais comprida que a caixa

O comprimento da expansora corre ao longo do eixo de **32 mm** da caixa. Para o
soquete de borda alcançar o TK e os dedos de passagem ficarem acessíveis, ela tem
que sobrar dos dois lados:

| Comprimento | Sobra total | Por lado |
| --- | --- | --- |
| 45 mm (primeira versão) | 13 mm | 6,5 mm — **insuficiente** |
| **70 mm (adotado)** | 38 mm | **19 mm** — folgado |

Precisa de ≥12 mm do lado do TK (corpo do soquete ~10 mm) e ≥11 mm do lado da
passagem (dedos de 7,62 mm).

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
| 1. Grade do soquete | Conector não entra na placa |
| 2. Fileira invertida | **Pode danificar o TK** |
| 3. Chaveta | **Pode danificar o TK** |
| 4. Acabamento dos dedos | Contato ruim, desgaste rápido |
| 5. ROMCS | ROM 128 instável (só afeta quem usa a EPROM) |
| 6. Conector angular | Placa não fica em pé |
| 7. Caixa | Não fecha |
| 8. Regras de fabricação | Curto ou trilha aberta se a fábrica não atender 0,14 mm |
