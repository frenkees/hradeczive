#!/bin/sh
# Přepínač „Plachta – kdyby se stavělo“: scéna čtverce 1,-1 se zástavbou podle urbanistické studie, render jen dlaždic v zóně, vrstvy plachta_<varianta>.
# Spouštět z izomapa/ (Git Bash):  sh ../skripty/plachta.sh      [--bez-prep = jen render a web]
set -e
cd "$(dirname "$0")/../izomapa"
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; else . .venv/Scripts/activate; fi
export PYTHONUTF8=1
C=1,-1; D=build/c1_-1; G="gx0=-1646.34559672906 gy1=988.7958500237901"
if [ "$1" != "--bez-prep" ]; then
  python ../skripty/plachta_studie.py
  IZO_PLACHTA=1 python prep.py data_c1_-1 $C > build/plachta_prep.log 2>&1 || { tail -20 build/plachta_prep.log; echo "PREP SELHAL"; exit 1; }
fi
TILES=$(python - <<'PY'
import json, geo
z = json.load(open('assets/plachta_studie.json', encoding='utf-8'))['zona']
info = json.load(open('build/c1_-1/tiles_summer/info.json')); T = info['tile']
cx, cy = geo.chunk_center((1, -1)); ts = set()
for la, lo in z:
    x, y = geo.to_local(lo, la)
    for h in (-5, 0, 40, 70):
        vx, vy, _ = geo.view(float(x), float(y), h); px, py = (vx - info['x0']) / info['mpp'], (info['y1'] - vy) / info['mpp']
        for ox in (-60, 60):
            for oy in (-60, 60): ts.add(f'{int((px + ox) // T)}_{int((py + oy) // T)}')
print(';'.join(sorted(ts)))
PY
)
echo "dlaždice: $TILES"
for s in summer autumn winter spring lights; do
  M=day; S=$s; [ $s = lights ] && { M=lights; S=autumn; }
  rm -rf $D/tiles_plachta_$s
  node render.mjs mpp=0.2 dir=${D}_plachta out=$D/tiles_plachta_$s season=$S mode=$M alpha=1 $G "tiles=$TILES" > $D/render_plachta_$s.log 2>&1 || { tail -5 $D/render_plachta_$s.log; echo "RENDER SELHAL $s"; exit 1; }
  echo "render $s"
done
python dzi.py --chunk $C plachta_summer plachta_autumn plachta_winter plachta_spring plachta_lights
python build_html.py > /dev/null
echo "Hotovo."
