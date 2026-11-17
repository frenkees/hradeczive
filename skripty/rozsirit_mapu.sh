#!/bin/sh
# Rozšíření mapy o nové čtverce (po úpravě "ctverce" v izomapa/mesto.json): doplní vstupní data pro celou novou plochu a vyrenderuje jen čtverce,
# kterým se změnila scéna (otisk v nastroje/otisk.py), ostatní přeskočí. Spouští se z kořene repa v Git Bash:  sh skripty/rozsirit_mapu.sh
# Záloha původních dat je v izomapa/build/zaloha_rozsireni/. Log: izomapa/build/rozsireni.log
set -e
cd "$(dirname "$0")/../izomapa"
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; else . .venv/Scripts/activate; fi
export PYTHONUTF8=1
krok() { echo "=== $(date +%H:%M:%S) $*"; }
krok "Overture (vrstvy se stahují znovu pro celou novou plochu, místa a části obcí)"
for l in building segment land_use water land_cover infrastructure land address; do rm -f data_all/$l.parquet; done
rm -f data_all/division_area.parquet data/places.parquet
python fetch_data.py --vse
krok "laser ČÚZK (výšky budov) a terén DMR 5G"; python dmp_fetch.py && python dmp_vysky.py && python nastroje/teren_dmr.py
krok "les, pole"; python nastroje/les.py; python nastroje/zabaged.py && python nastroje/pole.py
krok "hřiště, typy budov, barvy střech, zeleň na zpevněných plochách, hřebeny, komíny, pruhy, přejezdy"
python nastroje/hriste.py || true; python nastroje/ruian.py || true; python nastroje/strechy.py || true; python nastroje/povrchy.py || true
python nastroje/hrebeny.py || true; python nastroje/kominy.py || true; python nastroje/pruhy.py || true
python nastroje/prejezdy_z_dat.py || true
krok "data magistrátu (pasporty, značení, značky); mimo území města zůstanou prázdná"
python ../skripty/mmhk_pasport.py || true
python ../skripty/mmhk_znacky.py || true
krok "scény, render změněných čtverců, dlaždice, web"
sh ./postav.sh render
krok "hotovo"
