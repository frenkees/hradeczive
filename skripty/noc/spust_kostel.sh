#!/bin/sh
# noční běh: podklady ke kostelu Božského Srdce Páně (hlášení #52); počká na dokončení přerenderu
cd "$(dirname "$0")/../.."
mkdir -p izomapa/build/noc
PYTHONUTF8=1 izomapa/.venv/Scripts/python.exe skripty/noc/noc_objekt.py "Kostel Božského Srdce Páně" 50.21309 15.81507 --slug bozske_srdce_pane --wiki "Kostel Božského srdce Páně (Hradec Králové)" --ceka >> izomapa/build/noc/objekt.log 2>&1
