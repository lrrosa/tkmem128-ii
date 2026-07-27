# Montagem

Antes de começar, leia [ANTES-DE-FABRICAR.md](ANTES-DE-FABRICAR.md) — há três
itens que, se estiverem errados, podem danificar o micro.

---

## Antes de tudo: a orientação

A placa principal fica **em pé** e o conector de borda é soldado nela. O corpo
do conector sai por **um** lado e os terminais atravessam para o **outro**, onde
a tira de expansão é soldada.

> ⚠️ **Os componentes vão do mesmo lado da tira de expansão.** O conector de
> borda é **o único componente do lado do cobre**: você o encaixa por baixo e
> solda por cima, pelo lado dos componentes. Montada ao contrário, a placa
> esbarra no micro dentro da caixa.

---

## Ordem de montagem

### Placa principal

1. **Resistores** R2, R4, R5 (e R3 se for usar o LED).
2. **Soquetes torneados** dos CIs — U1 (DIP-24), U2 (DIP-20), U3 (DIP-32),
   U4 (DIP-28). Use soquetes: a SRAM e o GAL são peças caras e o GAL você vai
   querer regravar.
3. **Capacitores** C1–C5 (100 nF) e C6 (10 µF, atenção à polaridade).
4. **Headers de jumper** JP1–JP4.
5. **LED D1** (opcional, atenção à polaridade).
6. **Conector de borda `J1`** — por último. Ele entra pelo **lado do cobre** e
   é soldado pelo lado dos componentes. Solde dois terminais das pontas,
   confira o esquadro, e só então o resto.
   A **guia**: encaixe um pedacinho de PCB de ~1,6 mm na posição **5/52** do
   conector (a placa não tem furos ali, justamente porque não há terminal),
   casando com o rasgo entre os dedos do TK.
7. Só então **encaixe os CIs** nos soquetes.

### Tira de expansão

Ela não tem componente nenhum: de um lado ilhas de solda, do outro dedos de
borda.

1. Enfie a tira **entre as duas fileiras** de terminais do conector, que são
   retos: uma fileira fica por cima da tira e a outra por baixo. Ela sai
   perpendicular à placa principal, no plano do cartão do TK.
2. **Solde dos dois lados** — por cima e por baixo. Comece pelas duas pontas
   de cada face para travar o alinhamento, depois preencha o resto.
   As ilhas chegam até a aresta da tira, então não importa se o seu conector
   tem o terminal mais curto: sempre há cobre embaixo dele.
3. Confira com multímetro alguns pontos contra os dedos da outra extremidade
   antes de energizar.

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

1. TK **desligado**. Encaixe o conector da placa principal nos dedos do TK,
   atenção à guia das posições 5 e 52.
2. Confira que os componentes estão virados para o lado da tira de expansão.
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

A tira de expansão tem **45 mm** e atravessa a caixa pelo eixo de 32 mm, saindo
pela traseira com os dedos de passagem. O conector do TK fica na frente, do lado
oposto da placa principal.

### Adaptando a caixa

1. Abra duas fendas: uma **na frente**, para o corpo do conector de borda sair
   e receber os dedos do TK, e uma **atrás**, para a tira de expansão passar.
2. Uma das torres de fixação (a de `y = 62,02 mm`, sob o conector `J1`) cai dentro
   da fenda maior e precisa ser desgastada com micro-retífica.
3. Fixe as placas com **pedaços de EVA** colados no fundo e nas laterais — é como
   a montagem original resolve, e funciona bem porque a caixa fecha com trava.

> A placa **não tem furos de fixação** de propósito: as duas torres da caixa caem
> em posições inutilizáveis. Veja o porquê em
> [ANTES-DE-FABRICAR.md](ANTES-DE-FABRICAR.md#7-caixa-patola-pb-0853).

O resultado fica com a placa em pé dentro da caixa, o conector saindo pela
frente e a tira de expansão pela traseira — exatamente como a TKMEM-128
original e os demais periféricos do TK.
