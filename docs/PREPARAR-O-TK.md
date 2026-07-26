# Preparando o TK90X / TK95

A TKMEM-128 mapeia a SRAM externa em `0x8000-0xFFFF`. Como o banco superior de
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

1. Solde um fio do **pino 17 do conector de expansão** até o **pino 10 do IC27**
   (74LS32). Pode passar por baixo da placa.
2. Confirme a ligação com multímetro no teste de continuidade **antes de ligar o
   micro**.
3. Na placa principal da TKMEM-128, **feche o jumper JP4**.

Com JP4 fechado, a placa injeta nível 1 no pino 17 através de R4 (1 kΩ),
desabilitando a RAM interna. Ao remover a interface o pino fica flutuando e o TK
volta a operar como 48 KB. Transparente.

### Por que o pino 17

O pino 17 é **não-conectado** tanto no TK90X/TK95 quanto no ZX Spectrum, o que o
torna seguro para esse uso. Confira na pinagem do expansor do TK:

```
    fileira de cima (vista da interface, esquerda -> direita)
    56 55 54 53 [52=guia] 51 50 49 48 47 46 45 44 43 42 41 40 39 38 37 ...
    fileira de baixo
     1  2  3  4 [ 5=guia]  6  7  8  9 10 11 12 13 14 15 16 [17] 18 19 20 ...
                                                            ^^^^
                                                            N.C.
```

### A diferença em relação à placa original

Na TKMEM-128 original esse jumper tinha **duas posições**, `TK` e `Spectrum`, e a
documentação avisava em letras garrafais que usar a posição errada num TK
**danificava o computador**.

Aqui esse risco não existe: JP4 é simplesmente aberto ou fechado, e o resistor
R4 de 1 kΩ em série limita a corrente caso o pino 17 não esteja livre no seu
micro.

---

## Conferindo

Com a interface conectada e JP4 fechado, ligue o TK. Ele deve iniciar
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
Edu Luccas (Luccas Eletrônica), que documentou os três métodos com fotos da
placa do TK indicando o IC27 e o ponto do barramento.
