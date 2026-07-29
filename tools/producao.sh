#!/usr/bin/env bash
# Regenera tudo que e DERIVADO das placas: gerbers, furacao, BOM, posicoes,
# esquematico em PDF, os .zip da fabrica e os renders da documentacao.
#
# Rodar SEMPRE que a placa mudar — ate ajuste de serigrafia. Os .zip sao o que
# a fabrica pede no formulario de pedido; os arquivos soltos ficam ao lado para
# quem quiser inspecionar sem descompactar.
#
#   bash tools/producao.sh
set -e
cd "$(dirname "$0")/.."
KC="${KICAD_CLI:-C:/Program Files/KiCad/10.0/bin/kicad-cli.exe}"

# placa principal: 4 camadas (F.Cu / In1.Cu=GND / In2.Cu=+5V / B.Cu)
# tira de expansao: 2 camadas
gera() {
  local pcb="$1" sch="$2" dir="$3" camadas="$4" img="$5"
  echo "== $dir"
  rm -rf "$dir/gerbers"
  "$KC" pcb export gerbers --no-protel-ext --layers "$camadas" \
      -o "$dir/gerbers" "$pcb" >/dev/null
  "$KC" pcb export drill --format excellon --generate-map --map-format gerberx2 \
      -o "$dir/gerbers/" "$pcb" >/dev/null
  "$KC" pcb export pos --format csv --units mm -o "$dir/posicoes.csv" "$pcb" >/dev/null
  "$KC" sch export pdf -o "$dir/esquematico.pdf" "$sch" >/dev/null
  "$KC" sch export bom --fields 'Reference,Value,Footprint,Description' \
      --group-by Value -o "$dir/bom.csv" "$sch" >/dev/null
  # Renders da documentacao: sao derivados da placa como qualquer outro, entao
  # saem daqui. Fora do pipeline eles envelhecem sem ninguem notar — foi o que
  # aconteceu com o JP4, que ficou na imagem do README depois de ser removido.
  "$KC" pcb render --side top --quality high --width 1300 --height 1100 \
      -o "docs/img/$img.png" "$pcb" >/dev/null
  "$KC" pcb render --side bottom --quality high --width 1300 --height 1100 \
      -o "docs/img/$img-verso.png" "$pcb" >/dev/null
  # zip via Python: o Git Bash do Windows nao traz o utilitario `zip`
  python -c "import glob,os,zipfile,sys
d=sys.argv[1]
z=os.path.join(d,'gerbers.zip')
if os.path.exists(z): os.remove(z)
f=sorted(glob.glob(os.path.join(d,'gerbers','*')))
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
    for p in f: a.write(p, os.path.basename(p))
print('   %d arquivos -> %s (%.0f kB)' % (len(f), os.path.basename(z), os.path.getsize(z)/1024.0))" "$dir"
}

gera hardware/tkmem128.kicad_pcb hardware/tkmem128.kicad_sch \
     production/placa-principal \
     "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"      placa-principal

gera hardware/expansor/tkmem128-expansor.kicad_pcb \
     hardware/expansor/tkmem128-expansor.kicad_sch \
     production/tira-expansao \
     "F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"      placa-expansora

# registra o hash das fontes: e assim que confere_saidas.py sabe depois se as
# saidas correspondem a estas placas (data e conteudo nao servem — ver o script)
python tools/confere_saidas.py --grava

echo "pronto."
