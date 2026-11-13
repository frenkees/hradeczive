#!/bin/sh
# Celý Hradec Králové (16 čtverců): data -> doladění z ČÚZK -> scény + render (5 variant) -> DeepZoom WebP -> web site/.
# Spouštět z izohradec/: sh skripty/postav_cele_mesto.sh   (log: izomapa/build/cele_mesto.log)
set -e
cd "$(dirname "$0")/../izomapa"
. .venv/Scripts/activate
export PYTHONUTF8=1
L=build/cele_mesto.log; mkdir -p build; : > $L
krok() { echo "$(date +%H:%M:%S) $*" | tee -a $L; }

krok "mesto.json: 16 čtverců"
python - <<'EOF'
import json
m = json.load(open('mesto.json', encoding='utf-8'))
m['ctverce'] = json.load(open('../ctverce_cele.json'))
open('mesto.json', 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=1) + '\n')
print(len(m['ctverce']), 'čtverců')
EOF

krok "mazání mezivýsledků vázaných na rozsah mapy"
rm -f data_all/*.parquet data/places.parquet
rm -rf build/orto build/orto04 build/ruian
rm -f build/les_maska.* build/orto_cele.jpg build/zelen_maska.*
rm -f assets/dmp_vysky.json assets/zabaged.json assets/strechy_orto.json assets/ruian_budovy.json assets/hrebeny.json

krok "Overture + terén";            python fetch_data.py --vse >> $L 2>&1
krok "laser DMP 1G";                python dmp_fetch.py >> $L 2>&1 && python dmp_vysky.py >> $L 2>&1
krok "les z ortofota";              python nastroje/les.py >> $L 2>&1
krok "ZABAGED pole a louky";        python nastroje/zabaged.py >> $L 2>&1 && python nastroje/pole.py >> $L 2>&1
krok "barvy střech a zeleň";        python nastroje/strechy.py >> $L 2>&1 && python nastroje/povrchy.py >> $L 2>&1
krok "RÚIAN";                       python nastroje/ruian.py >> $L 2>&1
krok "hřebeny";                     python nastroje/hrebeny.py >> $L 2>&1
krok "komíny a věže z OSM (Overpass, s opakováním)"
for i in 1 2 3 4; do python nastroje/kominy.py >> $L 2>&1 && break; echo "Overpass selhal, čekám" >> $L; sleep $((60 * i)); done || true

krok "scény, render a DeepZoom (render_par.sh)"
rm -rf site/tiles && mkdir -p site/tiles && rm -f site/tiles.json
./render_par.sh >> $L 2>&1
krok "kresby stromů"
for s in summer autumn winter spring; do node render.mjs mpp=0.2 dir=build season=$s alpha=1 stromy=site/stromy > /dev/null; done
krok "náhled, klikací vrstva, MHD, web"
python preview.py >> $L 2>&1
python overlay.py >> $L 2>&1
python mhd.py >> $L 2>&1 || true
python set_status.py hotovo >> $L 2>&1
python build_html.py >> $L 2>&1
krok "HOTOVO"
