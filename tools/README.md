# Geradores

Todo o projeto KiCad deste repositório é **gerado por script** a partir de uma
descrição única da netlist. Isso mantém esquemático, PCB, símbolos e footprints
sempre coerentes entre si — não existe a possibilidade de o esquemático dizer
uma coisa e a placa outra.

Você **não precisa destes arquivos** para fabricar ou modificar a placa: abra o
projeto no KiCad normalmente. Eles estão aqui porque são a fonte real do
desenho, e porque a CERN-OHL-S pede a fonte completa.

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
| `add_zones.py` | Planos de GND nas duas faces + preenchimento |

## Refazendo tudo do zero

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

```bash
"$KIPY" mk_decoy.py netlist main
freerouting -de route.dsn -do route.ses -mp 300
"$KIPY" import_ses.py netlist main
"$KIPY" add_zones.py netlist
```

> Os caminhos das ferramentas estão fixos no topo dos scripts — ajuste para a
> sua instalação.

## Por que gerado

O barramento do TK tem 56 posições e a numeração dele (1..56) não bate com a
convenção A/B do ZX Spectrum. Descrever isso uma vez em `busdef.py` e derivar
símbolo, footprint, esquemático e placa a partir dali elimina a classe de erro
mais provável neste tipo de projeto: um pino trocado entre o desenho e a placa.
