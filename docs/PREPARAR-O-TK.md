# Preparando o TK90X / TK95

A TKMEM-128 II mapeia a SRAM externa em `0x8000-0xFFFF`. Como o banco superior de
32 KB do TK ocupa exatamente essa faixa, **os dois brigariam pelo barramento**.
Desativar essa RAM interna é a **única alteração necessária dentro do micro**.

> **TK90X de 16 KB não precisa de nada** — esse modelo não tem o banco de 32 KB.

Há três caminhos, do mais bruto ao mais elegante.

---

## 1. Remover os CIs de RAM

O jeito mais direto: arrancar os **quatro chips 4416**. Só é prático se estiverem
soquetados na sua unidade.

Definitivo enquanto os chips estiverem fora, e trivial de reverter (é só
recolocá-los).

---

## 2. Desabilitar por lógica — um fio

Se os chips estiverem soldados direto na placa e você não quiser dessoldá-los:

Solde um fio ligando o **pino 10 ao pino 14 do IC27** (um 74LS32, que fica no
canto da placa, perto dos CIs de RAM).

Pronto — 32 KB desabilitados. A desvantagem é que o TK fica permanentemente com
16 KB quando a interface não está conectada.

---

## 3. Auto-desativação — o método recomendado

Faz o TK voltar a ser 48 KB sozinho quando você desconecta a interface.

1. Solde um fio do **pino 29 do conector de expansão** até o **pino 10 do IC27**
   (74LS32).
2. Confirme a ligação com multímetro no teste de continuidade **antes de ligar o
   micro**.
3. Nada a fazer na TKMEM-128 II: `R4` já mantém o pino 29 em nível 1
   permanentemente.

Ao remover a interface o pino fica flutuando e o TK volta a operar como 48 KB.
Transparente, e **sem jumper nenhum para configurar**.

> **Atenção ao lado da placa.** O pino 29 está na **fileira de cima** (29..56),
> ou seja, na face da placa do TK oposta à dos pinos 1..28. Se você já viu as
> fotos da modificação original — que usava o pino 17 —, o ponto de solda agora é
> do outro lado da placa-mãe.

### Por que o pino 29

Porque ele é **não-conectado nas duas máquinas**, TK e ZX Spectrum:

```
    fileira de cima (vista da interface, esquerda -> direita)
    [29] 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 ... [52=guia] ... 56
    ^^^^
    N.C. no TK e no Spectrum (onde é chamado de 28A)

    fileira de baixo
     1  2  3  4 [ 5=guia]  6  7  8  9 10 11 12 13 14 15 16 [17] 18 19 20 ...
                                                            ^^^^
                                              N.C. no TK, mas V do vídeo
                                              componente no ZX Spectrum
```

No TK isso está confirmado na pinagem oficial arquivada em [`docs/`](.), que
marca o 29 como `N.C.`, e nas fotos da placa, onde o dedo não tem trilha
nenhuma. No Spectrum, o 28A também é livre.

**Consequência prática:** o pull-up de `R4` pode ficar permanente. Num Spectrum
não há nada ligado nesse contato, então nada acontece; num TK ele faz exatamente
o que tem que fazer. Foi por isso que **o jumper JP4 deixou de existir** neste
projeto.

> A placa original da Luccas usava o **pino 17**, que é livre no TK mas é o
> **V do vídeo componente no ZX Spectrum** — e por isso precisava de um jumper e
> de um aviso. Um jumper cuja posição errada estraga o micro é um risco que não
> precisa existir. Se você tem uma placa antiga com JP4, o aviso continua
> valendo: **nunca feche JP4 num Spectrum**.

Se algum dia quiser liberar o pino 29 — por exemplo para um periférico que o use
—, basta **não montar R4**.

--- | --- | --- |
| 16, 17, 18 | N.C. | Y, V, U do vídeo componente |
| 34, 35 | 12 V | +12 V / −12 V |
| 37 | **+5 V** | **−5 V** |
| 7 | N.C. | GND |
| 15 | GND | sinal |

Escolher a posição "Spectrum" num TK mandaria o sinal de desativação — que é
nível 1 injetado sem resistor de série na placa original — para um pino que no TK
é trilho de alimentação. Curto entre fontes explica bem um aviso em letras
garrafais.

**Aqui esse risco não existe**, e por dois motivos: não há jumper para pôr na
posição errada, e o sinal vai para o pino 29, que é N.C. nas duas máquinas.
`R4` de 1 kΩ em série continua limitando corrente — é mais firme que o pull-up de
10 kΩ da placa original, que já bastava.

---

## E num ZX Spectrum 48K?

A placa serve — o barramento é compatível contato a contato, ver
[Compatibilidade](../README.md#compatibilidade) — mas **esta página não serve**.
Ela descreve o interior do TK.

O que vale igual: os 32 KB superiores de RAM interna também têm que sair de
`0x8000-0xFFFF`, senão colidem com a SRAM da placa. O que muda é **o ponto
interno onde se faz isso**, e ele depende da revisão da placa-mãe:

| Issue | Componente | Fio |
| --- | --- | --- |
| 2, 3 e 4 | `IC23`, um **74LS32** | do **pino 5** ao **pino 14** (+5 V) |
| 5 e 6 | `IC27`, o **ZX8401** | do **pino 35** ao **pino 40** (+5 V) |

O efeito é o mesmo nos dois casos e é o mesmo do TK: segurar `CAS`/`RAS` em
nível alto para que não chegue aos chips de RAM de cima. Repare que a versão
Issue 2/3/4 é literalmente o mesmo tipo de intervenção que a do TK — forçar a
entrada de uma porta do 74LS32 para +5 V —, só que noutra porta e noutro CI.

**Teste rápido de que o fio ficou certo:** com o mod feito e a interface
*desconectada*, o micro tem que se comportar como um **Spectrum de 16K**.

> ⚠️ **`IC27` não quer dizer a mesma coisa nas duas máquinas.** No TK90X/TK95 o
> `IC27` é o 74LS32 desta página; num Spectrum Issue 5/6 o `IC27` é o ZX8401 —
> outro chip, outro pino, 40 pinos em vez de 14. Lendo os dois procedimentos
> lado a lado é fácil trocar. Confira o que está escrito no encapsulamento
> antes de soldar.

**De onde veio isto:** do [goloskokovic/zx16to128upgrade](https://github.com/goloskokovic/zx16to128upgrade),
que redistribui o mesmo projeto do Velesoft de onde este aqui deriva.
**Não verificamos em bancada** — não temos a máquina aqui. Se você fizer, uma
[issue](https://github.com/lrrosa/tkmem128-ii/issues) dizendo se funcionou é
bem-vinda.

A auto-desativação pelo contato 29 continua **inerte num Spectrum**: lá esse
contato é N.C., então o pull-up de `R4` não chega a lugar nenhum. Isso é de
propósito — é o que torna a placa segura nas duas máquinas —, mas significa que
num Spectrum a desativação é sempre por dentro, pelo fio da tabela acima.

---

## Conferindo

Com a interface conectada, ligue o TK. Ele deve iniciar
normalmente. Em BASIC:

```basic
PRINT PEEK 23732 + 256 * PEEK 23733
```

Isso mostra o topo da RAM (`RAMTOP`/P-RAMT). Num TK com os 32 KB desativados e a
interface ativa, você tem os 128 KB paginados disponíveis pela porta `0x7FFD` —
o teste real é carregar um jogo de 128 KB.

---

## Fontes

O procedimento vem do artigo **"Preparando o TK90X/TK95 para a TKMEM-128"**, de
Eduardo Luccas (Luccas Eletrônica), que documentou os três métodos com fotos da
placa do TK indicando o IC27 e o ponto do barramento.
