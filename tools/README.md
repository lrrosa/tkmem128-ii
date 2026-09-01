# Geradores

Todo o projeto KiCad deste repositório é **gerado por script** a partir de uma
descrição única da netlist. Isso mantém esquemático, PCB, símbolos e footprints
sempre coerentes entre si — não existe a possibilidade de o esquemático dizer
uma coisa e a placa outra.

Você **não precisa destes arquivos** para fabricar ou modificar a placa: abra o
projeto no KiCad normalmente. Eles estão aqui porque documentam como o desenho
nasceu, e porque a CERN-OHL-S pede a fonte completa.

> ⚠️ **Os geradores são ferramenta de bootstrap, não a fonte corrente.**
> O esquemático e o posicionamento foram refinados à mão no KiCad depois de
> gerados. Rodar `gen_schematic.py` ou `gen_pcb.py` de novo **sobrescreve esse
> trabalho**. A fonte corrente são os arquivos em `hardware/`.
>
> O que continua seguro rodar a qualquer momento: `gen_symbols.py` e
> `gen_footprints.py` (bibliotecas), `galgen.py` (o `.jed` do GAL), e o trio de
> roteamento `mk_decoy.py` / `import_ses.py` / `add_zones.py` quando você
> quiser reroteá-las de propósito.

## Arquivos

| Arquivo | Papel |
| --- | --- |
| `busdef.py` | Pinagem 1..56 do barramento do TK e mapa do header entre as placas |
| `netlist.py` | Netlist, posicionamento e serigrafia da **placa principal** |
| `netlist_exp.py` | Idem para a **placa expansora** |
| `gen_symbols.py` | Gera `hardware/lib/tkmem128.kicad_sym` |
| `gen_footprints.py` | Gera `hardware/lib/tkmem128.pretty/` |
| `gen_schematic.py` | Gera o `.kicad_sch` (estilo netlist: rótulo global em cada pino) |
| `gen_pcb.py` | Gera o `.kicad_pcb` com contorno, footprints posicionados e nets |
| `mk_decoy.py` | Placa-isca + export do DSN para o Freerouting |
| `import_ses.py` | Importa o `.ses` roteado de volta |
| `add_zones.py` | Planos de GND nas duas faces (usado só na tira, que é de 2 camadas) |
| `limpa_cotocos.py` | Remove fragmentos de trilha de décimos de mm deixados pela importação do SES |
| `maze.py` | Roteador de labirinto A* de duas camadas com via, para fechar a última ligação quando o autorouter desiste. **Não é mais necessário** — fica como ferramenta |
| `galgen.py` | Monta o mapa de fusíveis do GAL20V8 das equações e confere contra um `.jed` de referência |
| `troca_j1.py` | Troca o footprint de `J1` na placa principal preservando esquemático e serigrafia |
| `corrige_silk_tira.py` | Acerta a serigrafia da tira (numeração por face, contorno em U, texto da passagem) sem regerar a placa |
| `silk_conector_principal.py` | Leva a numeração de `J1` para o lado dos componentes e apara o contorno que passava da aresta |
| `ajusta_guia.py` | Refaz o rasgo da guia da tira com a profundidade de `KEYSLOT_DEPTH` e repreenche as zonas |
| `silk_negrito.py` | Poe toda a serigrafia em negrito (espessura = 0,2 x tamanho, como o KiCad faz) |
| `rota_tira.py` | Roteia a tira a mao: 54 retas verticais de 1,5 mm, zero via, zero plano |
| `tira_sem_c1.py` | Removeu C1 do esquematico da tira (ilha passante e curto numa placa de passagem) |
| `repoe_principal.py` | Reposicionamento da principal para roteamento: CIs horizontais, desacoplamento junto aos CIs, corredor livre, regras 0,5/0,20 |
| `silk_principal.py` | Reposiciona a serigrafia de nível de placa depois do rearranjo |
| `tira_sj.py` | Removeu SJ1/SJ2 do esquemático — histórico, já aplicado |
| `planos_4camadas.py` | Cria os planos internos de GND e +5V da placa principal |
| `move_ramdis.py` | Moveu a auto-desativação do pino 17 para o 29 e removeu JP4 — histórico, já aplicado |
| `sobe_j1.py` | Subiu `J1` 1,5 mm: o corpo do conector deixa de sair pela aresta. Apaga o roteamento de propósito |
| `furo_da_torre.py` | Abriu `H1` em Ø5,4 — passagem da **torre** Ø5 da caixa, não do parafuso — e recuou `U4` 1,5 mm para caber. Apaga o roteamento |
| `tabelas_jumpers.py` | Serigrafia dos jumpers em tabela no verso e título da placa em duas linhas. Idempotente: limpa a faixa antes de desenhar |
| `endireita_trilhas.py` | Poda os desvios que o Freerouting deixa e chanfra cantos de 90°. Simula por padrão; `--grava` aplica. Rodar até dar zero |
| `silk_r4.py` | Quebra a nota do `R4` em duas linhas (era uma só de 43,4 mm) e troca "do TK" por "do micro" |
| `ajusta_u4_c6.py` | Traz a referência de `U4` de volta para dentro da placa (o recuo dele a jogou para x = −0,57), aproxima o `27C256`, e move `C6` 0,70 mm para cima e 0,80 para a esquerda — longe dos terminais de `J1` e da vertical de `D5`. Confere as trilhas vizinhas antes de gravar |
| `fecha_silk_conector.py` | Fecha o contorno de `J1` na serigrafia agora que o corpo cabe dentro da placa, tira as linhas duplicadas, e afasta o rótulo `GUIA 5/52` de qualquer ilha vizinha |
| `fecha_a14.py` | Fecha `A14` à mão pela margem direita: o Freerouting deixa essa uma em aberto |
| `producao.sh` | Regenera **tudo que é derivado** das placas — gerbers, furação, BOM, posições, esquemático em PDF, os `.zip`, os renders de `docs/img/` e o manifesto `production/fontes.json` — e no fim roda as verificações de regressão. Qualquer uma falhando derruba a geração |
| `confere_svg.py` | Procura texto pousado sobre trilha, ilha, parede ou outro texto no `docs/img/vista-de-lado.svg` |
| `confere_saidas.py` | **Verificação de regressão**: diz se as saídas correspondem às placas atuais, comparando o hash das fontes contra o manifesto |
| `confere_compatibilidade.py` | **Verificação de regressão**: confere que a placa não liga nenhum contato que difere entre TK e ZX Spectrum 48K |
| `confere_pinos.py` | **Verificação de regressão**: confere que os rótulos de pino do conector nos dois esquemáticos e na biblioteca de símbolos batem com `busdef.py` |
| `confere_alinhamento.py` | **Verificação de regressão**: confere que as colunas, a guia, as faces e a numeração serigrafada batem entre a placa principal e a tira |
| `confere_links.py` | **Verificação de regressão**: confere que os links entre os documentos e as âncoras de seção ainda resolvem |

## Refazendo tudo do zero (destrói os ajustes manuais)

Símbolos e footprints usam o Python comum; o resto usa o Python embutido do
KiCad (que traz o módulo `pcbnew`).

```bash
python gen_symbols.py
python gen_footprints.py
python gen_schematic.py netlist
python gen_schematic.py netlist_exp
```

```bash
KIPY="C:/Program Files/KiCad/10.0/bin/python.exe"
"$KIPY" gen_pcb.py netlist
"$KIPY" gen_pcb.py netlist_exp
```

Roteamento (Freerouting), para cada placa:

**Placa principal** (4 camadas). Os planos internos entram *antes* do roteamento:
o DSN precisa declará-los para o Freerouting saber que `+5V` e `GND` já estão
ligados e não tentar roteá-los nas faces de sinal.

```bash
"$KIPY" planos_4camadas.py                   # GND em In1.Cu, +5V em In2.Cu
"$KIPY" mk_decoy.py netlist main
sed -i "s/(clearance 200)/(clearance 215)/g" route.dsn
freerouting -de route.dsn -do route.ses -mp 900
"$KIPY" import_ses.py netlist main
"$KIPY" limpa_cotocos.py netlist
"$KIPY" fecha_a14.py                         # a unica que o autorouter nao fecha
```

Depois de importar, **repreencher as zonas**: o SES traz só as trilhas, e um DRC
com os planos desatualizados acusa centenas de violações que não existem.

**Tira de expansão** — não usa autorouter: as 54 ligações são retas verticais.

```bash
"$KIPY" rota_tira.py
```

O Freerouting fecha 73 das 74 nets da principal com isolação **0,215** no DSN; a
que sobra é sempre `A14`, fechada à mão por `fecha_a14.py`. Ele é determinístico
por entrada: se sobrar ligação em aberto, repetir não muda nada — tem que
perturbar a isolação. E a resposta **não é monotônica**: uma varredura deu, numa
mesma placa,

| isolação no DSN | 200 | 205 | 211 | 213 | 214 | 216 | 220 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nets em aberto | 14 | 2 | 1 | 1 | **17** | 2 | 13 |

— ou seja, 1 mícron a mais que o ótimo faz saltar de 1 para 17. Não adianta
"afrouxar até funcionar"; varra a faixa 200–220 e escolha o melhor. E **varra de
novo a cada mudança de placa**: com `U4` recuado e o furo em Ø5,4 o ótimo saiu de
0,213 para **0,215**, e 0,213 passou a deixar 2 nets.

Antes de mexer em posicionamento por causa de net em aberto, **conferir o vão
entre ilhas do conector**: foi ali que o gargalo real estava.

E depois de importar o SES, rodar `endireita_trilhas.py`. O otimizador do
Freerouting não desfaz escadinha: sobra caminho de iterações anteriores, de
quando outra rede ainda ocupava o espaço. Na rodada em que isto foi escrito ele
tirou **54,7 mm em 41 cadeias** e reduziu os cantos de 90° de 23 para zero, sem
mudar nenhuma ponta, sem trocar de camada e sem mexer em via. Rodar repetido
até dar `total: 0` — cada passada muda a decomposição em cadeias e abre a
seguinte.

> Os caminhos das ferramentas estão fixos no topo dos scripts — ajuste para a
> sua instalação.

## Uma regra de DRC que vale a pena estar ligada

Os dois projetos trazem `silk_over_copper` em **`warning`**, e não no `ignore`
que é o padrão do KiCad. É a regra que acusa serigrafia por cima da abertura de
máscara de uma ilha — texto que na placa pronta sai cortado, ou pior, tinta
sobre a área a soldar.

Ela ficou desligada por um tempo e no meio disso um capacitor andou 0,8 mm, o
rótulo `GUIA 5/52` passou a cobrir uma ilha dele, e **nada acusou**: DRC zerado,
os quatro conferidores passando, e o defeito só apareceu quando alguém olhou o
render. Ligada, ela acusa exatamente esse caso e nenhum falso positivo nas duas
placas.

## Refazendo o `.jed` do GAL

`galgen.py` monta o mapa de fusíveis do GAL20V8 a partir das equações (matriz
AND, polaridade das saídas, habilitação dos termos e bits de modo), **deduzindo o
mapa de colunas das próprias equações** em vez de assumi-lo, e compara o
resultado com um `.jed` de referência:

```bash
python tools/galgen.py caminho/para/referencia.jed
```

Saída esperada:

```
fusiveis divergentes: 0 de 2706
checksum de referencia: 5752
checksum reconstruido : 5752
```

É essa comparação que autoriza distribuir `hardware/gal/tkmem128.jed` pronto: o
arquivo é gerado das equações deste projeto, e bate fusível a fusível com o mapa
do projeto original.

## Uma geração que também confere

`producao.sh` termina rodando `confere_pinos`, `confere_links`,
`confere_compatibilidade`, `confere_svg` e `confere_alinhamento`. Com
`set -eo pipefail`, qualquer uma falhando derruba a geração antes do
`pronto.` — conferido com teste negativo.

Não é zelo: regerar sem conferir já deixou passar coisa demais aqui. A
biblioteca ficou com ilha de 1,75 mm enquanto a placa usava 1,50; o bloco de
legenda ficou com o nome antigo do projeto; e o símbolo do conector continuou
rotulando *pino 17 = RAMDIS* depois de a auto-desativação ter ido para o 29 —
esse último saindo no PDF entregue. **Nenhum aparecia no ERC nem no DRC**, que
não leem `busdef.py` nem o esquemático um do outro.

O `pipefail` não é decoração: a saída do `confere_alinhamento` passa por um
`grep` para tirar o ruído do wxWidgets, e sem ele o status seria o do `grep`.

### E no CI

[`.github/workflows/conferidores.yml`](../.github/workflows/conferidores.yml)
roda **as seis** verificações a cada push e pull request, em dois jobs
paralelos porque os custos são diferentes:

| Job | O que roda | Como |
| --- | --- | --- |
| `rapidos` | os cinco conferidores em Python puro | ~15 s, sem dependência nenhuma |
| `alinhamento` | `confere_alinhamento.py` | dentro de `kicad/kicad:10.0.4`, porque precisa do `pcbnew` |

A versão da imagem é a mesma da bancada de propósito: as placas estão no
formato do KiCad 10 (`version 20260206`) e não abrem em 8 nem 9. O job usa
`docker run` em vez de `container:` para o checkout rodar no host como
usuário normal — a imagem do KiCad não roda como root, e o conferidor só
precisa **ler** o workspace montado.

Isso cobre o furo que o `producao.sh` não cobre: ele só confere quando alguém
lembra de rodá-lo. As duas que mais ganham com isso são o `confere_saidas`,
que pega o caso de editar uma placa e commitar sem regerar — aí gerbers, BOM,
PDF e renders passam a descrever uma placa que não existe mais —, e o
`confere_alinhamento`, que é o único a enxergar a relação **entre** as duas
placas. Uma tira espelhada passa em ERC e em DRC, porque cada placa é válida
sozinha; o que não existe é o casamento entre elas.

O job do KiCad só se tornou possível depois que os caminhos absolutos saíram
do `netlist.py` e do `netlist_exp.py`: dentro do container eles resolviam
para `F:/downloads/...`, o disco da máquina de origem.

## Como saber se as saídas estão atualizadas

```bash
python tools/confere_saidas.py
```

As duas maneiras óbvias de responder isso **não funcionam** neste projeto, e vale
saber por quê antes de tentar:

| Tentativa | Por que falha |
| --- | --- |
| comparar **data** dos arquivos | O `kicad-cli` reescreve a `.kicad_pcb` byte a byte idêntica ao rodar `export` e `render`. A placa fica sempre "mais nova" que os derivados dela, e a comparação acusa defasagem que não existe |
| comparar **conteúdo** | Gerber, `.drl`, `.gbrjob` e PDF carregam a data de geração embutida. E o **raytracer dos renders não é determinístico**: duas rodadas seguidas dão PNGs diferentes com a placa intacta |

Então `producao.sh` registra o hash das **fontes** em `production/fontes.json`, e
`confere_saidas.py` compara. Se bate, as saídas foram geradas desta versão das
placas. Sai com código 1 se não bate, então serve em hook ou CI.

## A outra verificação de regressão

```bash
python tools/confere_compatibilidade.py
```

A placa serve em TK90X/TK95 **e** em ZX Spectrum 48K, e isso se resume a uma
regra: dos 54 contatos do barramento, **nove não carregam a mesma coisa nas duas
máquinas** (4, 7, 15, 16, 17, 18, 34, 35, 37), e a placa não pode tocar nenhum.
O script cruza as ressalvas de `busdef.py` com os contatos que a netlist usa e
falha se algum aparecer. Rodar depois de qualquer mexida em `busdef.py` ou
`netlist.py` — e antes de repetir a afirmação de compatibilidade em qualquer
lugar.

## A verificação que vale rodar sempre

```bash
"$KIPY" confere_alinhamento.py
```

As duas placas se encaixam por solda, não por conector — nada no KiCad amarra
uma à outra. Cada uma passa em ERC e DRC isoladamente mesmo se a tira estiver
espelhada; o erro só apareceria na bancada, com o barramento invertido ponta a
ponta. Esse script fecha essa lacuna: confere que a coluna de cada pino, a
guia, as faces das fileiras e a fileira junto à aresta batem entre as duas.

Ele também confere a **numeração serigrafada**. As ilhas e os dedos são SMD —
cada pino existe em uma face só —, então a serigrafia de uma face não pode
nomear o pad da outra: na coluna x=73,66 o cobre de `F.Cu` é o pino 56 e o de
`B.Cu` é o pino 1. O script acha, para cada rótulo numérico, o pad mais próximo
*naquela face* e exige que o número bata.

## Por que gerado

O barramento do TK tem 56 posições e a numeração dele (1..56) não bate com a
convenção A/B do ZX Spectrum. Descrever isso uma vez em `busdef.py` e derivar
símbolo, footprint, esquemático e placa a partir dali elimina a classe de erro
mais provável neste tipo de projeto: um pino trocado entre o desenho e a placa.
