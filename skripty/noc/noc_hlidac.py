"""Hlídač nočního katalogu: spustí noc_katalog.py a hlídá ho.

python skripty/noc/noc_hlidac.py        (z izohradec/, běží do konce práce)
- pád (nenulový kód) -> položka z tepu dostane bod do karantény (po 2 bodech se přeskočí) a skript se spustí znovu
- zaseknutí nebo zacyklení: tep.json se nezměnil 20 min, nebo tatáž položka běží přes 40 min -> zabít, bod do karantény, znovu
- víc než 6 restartů za hodinu, nebo 4 restarty po sobě bez postupu -> POMOC.txt (důvod, konec logu, tep) a konec;
  na POMOC.txt čeká Claude v otevřené session (Bash na pozadí) a přijde problém vyřešit
- hotovo -> HOTOVO.txt (zapisuje pracovní skript)
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'izomapa', 'build', 'noc'))
os.makedirs(OUT, exist_ok=True)
TEP, STAV, LOG = os.path.join(OUT, 'tep.json'), os.path.join(OUT, 'stav.json'), os.path.join(OUT, 'noc.log')
POMOC, HOTOVO = os.path.join(OUT, 'POMOC.txt'), os.path.join(OUT, 'HOTOVO.txt')
PY = os.path.abspath(os.path.join(HERE, '..', '..', 'izomapa', '.venv', 'Scripts', 'python.exe'))
TICHO, POLOZKA_MAX = 20 * 60, 40 * 60


def log(*a):
    line = time.strftime('%H:%M:%S ') + '[hlídač] ' + ' '.join(str(x) for x in a)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f: f.write(line + '\n')


def cti(f, default=None):
    try: return json.load(open(f, encoding='utf-8'))
    except Exception: return default


def karantena(polozka):
    q = (polozka or '').split(' ')[0]
    if not q.startswith('Q'): return
    s = cti(STAV)
    if not s: return
    s.setdefault('karantena', {})[q] = s['karantena'].get(q, 0) + 1
    json.dump(s, open(STAV + '.tmp', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); os.replace(STAV + '.tmp', STAV)
    log('karanténa', q, s['karantena'][q])


def pomoc(duvod):
    konec = open(LOG, encoding='utf-8').read().splitlines()[-60:] if os.path.exists(LOG) else []
    with open(POMOC, 'w', encoding='utf-8') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M")}\nDŮVOD: {duvod}\nTEP: {json.dumps(cti(TEP), ensure_ascii=False)}\n\n--- konec noc.log ---\n' + '\n'.join(konec) + '\n')
    log('POMOC:', duvod); sys.exit(2)


def hotovych():
    s = cti(STAV, {}) or {}
    return sum(1 for v in s.get('hotovo', {}).values() if v.get('kompletni'))


for f in (POMOC, HOTOVO):
    if os.path.exists(f): os.remove(f)
restarty, bez_postupu = [], 0
while True:
    pred = hotovych()
    log('spouštím pracovní skript, hotovo', pred)
    p = subprocess.Popen([PY, '-u', os.path.join(HERE, 'noc_katalog.py')], stdout=subprocess.DEVNULL, stderr=open(os.path.join(OUT, 'stderr.log'), 'a'),
                         env={**os.environ, 'PYTHONUTF8': '1'})
    posl, polozka, od = None, None, time.time()
    duvod = None
    while p.poll() is None:
        time.sleep(30)
        t = cti(TEP, {}) or {}
        if t.get('polozka') != polozka: polozka, od = t.get('polozka'), time.time()
        if t.get('t') != posl: posl = t.get('t')
        if t.get('t') and time.time() - t['t'] > TICHO: duvod = f'bez tepu {TICHO // 60} min (zaseknutí) u „{polozka}“'
        elif time.time() - od > POLOZKA_MAX: duvod = f'položka „{polozka}“ běží přes {POLOZKA_MAX // 60} min (zacyklení?)'
        if duvod:
            log(duvod, '-> ukončuji'); p.kill(); p.wait(); break
    if not duvod and p.returncode == 0 and os.path.exists(HOTOVO):
        log('hotovo'); break
    duvod = duvod or f'pád s kódem {p.returncode} u „{(cti(TEP, {}) or {}).get("polozka")}“'
    log(duvod)
    karantena((cti(TEP, {}) or {}).get('polozka'))
    bez_postupu = bez_postupu + 1 if hotovych() <= pred else 0
    restarty = [r for r in restarty if time.time() - r < 3600] + [time.time()]
    if len(restarty) > 6: pomoc(f'víc než 6 restartů za hodinu; poslední: {duvod}')
    if bez_postupu >= 4: pomoc(f'4 restarty po sobě bez postupu; poslední: {duvod}')
    time.sleep(20)
