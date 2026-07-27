# Montagem

Antes de começar, leia [ANTES-DE-FABRICAR.md](ANTES-DE-FABRICAR.md) — há três
itens que, se estiverem errados, podem danificar o micro.

---

## Ordem de montagem

### Placa expansora

1. **Soquete de borda `J1`** — solde primeiro, é a peça que define tudo.
2. **Teste de continuidade** (item 2 do ANTES-DE-FABRICAR) com o TK
   **desligado**. Só siga se +5 V e GND caírem nos contatos certos.
3. **Chaveta**: encaixe um pedacinho de PCB de ~1,6 mm nas posições **5 e 52**
   do soquete. Ele casa com o rasgo entre os dedos do TK e impede encaixe
   deslocado.
4. **Header macho `J3`** (2×28 vertical) — ele precisa ficar perfeitamente
   perpendicular. Solde um pino de cada extremidade, confira o esquadro, e só
   então solde o resto.
5. **C1** (100 nF).

> Os pinos **5 e 52** do header `J3` **não são barramento** — são terra
> adicional entre as placas. Está serigrafado na placa.

### Placa principal

1. **Resistores** R2, R4, R5 (e R3 se for usar o LED).
2. **Soquetes torneados** dos CIs — U1 (DIP-24), U2 (DIP-20), U3 (DIP-32),
   U4 (DIP-28). Use soquetes: a SRAM e o GAL são peças caras e o GAL você vai
   querer regravar.
3. **Capacitores** C1–C5 (100 nF) e C6 (10 µF, atenção à polaridade).
4. **Headers de jumper** JP1–JP4.
5. **LED D1** (opcional, atenção à polaridade).
6. **Soquete fêmea angular `J1`** (2×28) — é o que segura a placa em pé.
7. Só então **encaixe os CIs** nos soquetes.

---

## Configuração inicial dos jumpers

Comece na configuração mais conservadora — só RAM, sem mexer em ROM:

| Jumper | Posição inicial |
| --- | --- |
| JP1 (SELECIONA ROM) | **2-3** (EPROM desligada) |
| JP2 (ROMCS BARRAM.) | **aberto** |
| JP3 (ZX128/ZX512) | **aberto** (128 KB) |
| JP4 (AUTO-DESATIVA) | **fechado** em TK90X/TK95, se você fez a modificação do pino 17. **Sempre aberto em ZX Spectrum** |
| SJ1 | **aberto** |
| SJ2 | **aberto** |

Nessa configuração U4 (a EPROM) nem precisa estar montada.

> ⚠️ **JP4 em ZX Spectrum: nunca feche.** No Spectrum os pinos 16, 17 e 18 são
> **Y, V e U do vídeo componente**, não pinos livres como no TK. Lá a RAM tem que
> ser desativada por outro método.

**SJ1 e SJ2 são opcionais e podem ficar abertos em qualquer máquina** — é assim
que a placa foi validada. O terra já chega pelos pinos 6 e 14, que são GND nas
duas máquinas; os solder jumpers só acrescentam retorno usando pinos que são GND
em apenas uma delas (7 no Spectrum, 15 no TK). Feche **no máximo o da sua
máquina**, e só se quiser o terra extra.

---

## Primeiro teste

1. TK **desligado**. Encaixe a expansora nos dedos do TK, atenção à chaveta.
2. Encaixe a placa principal no header da expansora.
3. Ligue. O TK deve iniciar normalmente com a tela de sempre.
4. Carregue um jogo de 128 KB. Se rodar, a paginação está funcionando.

Se o micro não iniciar, desligue imediatamente e confira:

- a modificação do pino 17 (continuidade até o pino 10 do IC27)
- se a RAM interna de 32 KB foi mesmo desativada
- orientação dos CIs nos soquetes
- o teste de continuidade do soquete de borda

### Pontos de teste

| Ponto | Sinal |
| --- | --- |
| TP1 | `VRAM` — bit 3 da porta `0x7FFD` (shadow screen; latcheado mas sem uso) |
| TP2 | `CLK7FFD` — clock do latch. Deve pulsar a cada escrita em `0x7FFD` e **travar em nível alto** depois que o bit 5 (`DIS128`) for setado |

---

## Modo 512 KB

Troque U3 por uma **AS6C4008** (512K×8, mesmo encapsulamento DIP-32) e feche
**JP3**. O software precisa saber usar os bits 6 e 7 da porta `0x7FFD` — jogos
comuns de 128 KB não usam.

---

## A EPROM (opcional)

A ROM do Spectrum 128 **não vem neste repositório** (copyright da Amstrad/Sky) e
**não é necessária** para rodar jogos de 128 KB. Se quiser mesmo:

```bash
cat 128-0.rom 128-1.rom > rom_tkmem128_27c256.bin
```

Grave numa 27C256, encaixe em U4, e ponha **JP1 em 1-2** e **JP2 em 1-2**
(ou 2-3 — ver ANTES-DE-FABRICAR item 5). Use os dois juntos: JP1 sozinho deixa a
EPROM e a ROM interna disputando o barramento de dados.

---

## A caixa

Caixa **Patola PB 085/3** (32 × 73 × 85 mm fechada). A placa principal assenta na
**tampa**, cuja área interna é 81 × 69 mm — daí os 78,74 × 66,04 mm da placa.

| | Disponível | Usado |
| --- | --- | --- |
| Largura | 81 mm | 78,74 mm |
| Altura | 69 mm | 66,04 mm |
| Altura livre para componentes | ~25 mm | ~10 mm |

A expansora tem **70 mm** de comprimento e atravessa a caixa pelo eixo de 32 mm,
sobrando **19 mm de cada lado** — o suficiente para o soquete alcançar os dedos
do TK de um lado e os dedos de passagem ficarem acessíveis do outro.

### Adaptando a caixa

1. Abra duas fendas na base: uma **maior** para o soquete de borda da expansora
   passar, e uma **menor** para os dedos de passagem.
2. Uma das torres de fixação (a de `y = 62,02 mm`, sob o conector `J1`) cai dentro
   da fenda maior e precisa ser desgastada com micro-retífica.
3. Fixe as placas com **pedaços de EVA** colados no fundo e nas laterais — é como
   a montagem original resolve, e funciona bem porque a caixa fecha com trava.

> A placa **não tem furos de fixação** de propósito: as duas torres da caixa caem
> em posições inutilizáveis. Veja o porquê em
> [ANTES-DE-FABRICAR.md](ANTES-DE-FABRICAR.md#7-caixa-patola-pb-0853).

O resultado fica com a placa em pé dentro da caixa e a expansora saindo pela
base, exatamente como a TKMEM-128 original.
