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
| `producao.sh` | Regenera gerbers, furação, BOM, posições e os `.zip` das duas placas |
| `confere_alinhamento.py` | **Verificação de regressão**: confere que as colunas, a guia, as faces e a numeração serigrafada batem entre a placa principal e a tira |

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
```

**Tira de expansão** — não usa autorouter: as 54 ligações são retas verticais.

```bash
"$KIPY" rota_tira.py
```

O Freerouting fecha as 74 nets da principal com isolação 0,215 no DSN. Ele é
determinístico por entrada: se sobrar ligação em aberto, repetir não muda nada —
tem que perturbar (isolação 0,20 a 0,215, largura, posicionamento). E antes de
mexer em posicionamento, **conferir o vão entre ilhas do conector**: foi ali que
o gargalo real estava.

> Os caminhos das ferramentas estão fixos no topo dos scripts — ajuste para a
> sua instalação.

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
