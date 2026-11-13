"""Noční katalog kandidátů na dominanty Hradce Králové (spouští ho noc_hlidac.py, ne přímo).

Fáze (stav v izomapa/build/noc/stav.json, po pádu pokračuje, kde skončil):
  1 kandidati  Wikidata: objekty v území mapy s kategorií nebo obrázkem na Commons (budovy, památky, sochy, mosty…)
  2 fotky      Commons: jen soubory s volnou licencí (CC0, CC BY, CC BY-SA, public domain), náhled 960 px, autor a licence do ZDROJE.md
  3 orto       výřez ortofota ČÚZK 120 × 120 m kolem bodu
  4 texty      česká Wikipedie -> qwen3:14b napíše 2–3 věty pro "příběh místa"; skript ověří, že každé číslo a každá citace
               je doslova ve zdroji, jinak koncept zahodí (nic se nevymýšlí; výsledek je jen KONCEPT k ruční kontrole)
  5 trideni    qwen3-vl:8b roztřídí fotky (exteriér celé stavby / detail / interiér / jiné) – pro výběr podkladů k modelování
  6 report     build/noc/index.html a katalog.json
Výstup: izomapa/build/noc/ (mimo git). Do mapy, repa ani na web nic nezapisuje.
Srdeční tep: build/noc/tep.json (čas + právě zpracovávaná položka) – podle něj hlídač pozná zaseknutí.
"""
import base64, hashlib, html, json, os, re, subprocess, sys, time, traceback, urllib.parse, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'izomapa'))
OUT = os.path.join(ROOT, 'build', 'noc')
KAT = os.path.join(OUT, 'katalog')
os.makedirs(KAT, exist_ok=True)
STAV_F, TEP_F, LOG_F = os.path.join(OUT, 'stav.json'), os.path.join(OUT, 'tep.json'), os.path.join(OUT, 'noc.log')
UA = {'User-Agent': 'izomapa-hradec-noc/1.0 (local research script)'}
BBOX = (50.175, 15.785, 50.245, 15.885)                    # celé město (CLAUDE.md)
MODEL_TXT, MODEL_VL = 'qwen3:14b', 'qwen3-vl:8b'
OLLAMA = 'http://127.0.0.1:11434'
FREE = re.compile(r'^(cc0|cc[- ]by(-sa)?[- ]?\d|public domain|pd\b|cc by-sa|cc by\b)', re.I)


def log(*a):
    line = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a)
    print(line, flush=True)
    with open(LOG_F, 'a', encoding='utf-8') as f: f.write(line + '\n')


def tep(polozka):
    json.dump({'t': time.time(), 'polozka': polozka}, open(TEP_F, 'w', encoding='utf-8'), ensure_ascii=False)


def nacti_stav():
    if os.path.exists(STAV_F): return json.load(open(STAV_F, encoding='utf-8'))
    return {'faze': {}, 'hotovo': {}, 'karantena': {}}


def uloz_stav(s):
    tmp = STAV_F + '.tmp'
    json.dump(s, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); os.replace(tmp, STAV_F)


def http(url, data=None, timeout=90, tries=4, headers=None):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:
            err = e; time.sleep(5 * (i + 1) ** 2)
    raise err


def ollama_ok():
    try: http(OLLAMA + '/api/tags', timeout=5, tries=1); return True
    except Exception: return False


def zajisti_ollama():
    if ollama_ok(): return
    exe = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe')
    log('Ollama neběží, spouštím', exe)
    subprocess.Popen([exe, 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    for _ in range(30):
        time.sleep(2)
        if ollama_ok(): return
    raise RuntimeError('Ollama se nepodařilo spustit')


def llm(model, prompt, schema, images=None, timeout=300):
    zajisti_ollama()
    body = {'model': model, 'prompt': prompt, 'stream': False, 'format': schema, 'think': False,
            'options': {'temperature': 0.1, 'num_ctx': 8192}, 'keep_alive': '10m'}
    if images: body['images'] = images
    r = json.loads(http(OLLAMA + '/api/generate', json.dumps(body).encode(), timeout=timeout, tries=2, headers={'Content-Type': 'application/json'}))
    return json.loads(r['response'])


slug = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower().encode('ascii', 'ignore').decode()).strip('_')[:50] or 'x'


# ---------------- 1 kandidáti z Wikidat ----------------
def faze_kandidati(S):
    q = f'''SELECT ?item ?itemLabel ?coord ?cat ?img ?cswiki ?typeLabel WHERE {{
      SERVICE wikibase:box {{ ?item wdt:P625 ?coord .
        bd:serviceParam wikibase:cornerSouthWest "Point({BBOX[1]} {BBOX[0]})"^^geo:wktLiteral .
        bd:serviceParam wikibase:cornerNorthEast "Point({BBOX[3]} {BBOX[2]})"^^geo:wktLiteral . }}
      OPTIONAL {{ ?item wdt:P373 ?cat }} OPTIONAL {{ ?item wdt:P18 ?img }} OPTIONAL {{ ?item wdt:P31 ?type }}
      OPTIONAL {{ ?cswiki schema:about ?item ; schema:isPartOf <https://cs.wikipedia.org/> }}
      FILTER(BOUND(?cat) || BOUND(?img))
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "cs,en". }} }}'''
    raw = http('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q), timeout=120)
    items = {}
    for b in json.loads(raw)['results']['bindings']:
        qid = b['item']['value'].rsplit('/', 1)[1]
        m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', b['coord']['value'])
        it = items.setdefault(qid, {'qid': qid, 'nazev': b.get('itemLabel', {}).get('value', qid), 'lat': float(m.group(2)), 'lon': float(m.group(1)),
                                    'kategorie': None, 'obrazek': None, 'cswiki': None, 'typy': []})
        if 'cat' in b: it['kategorie'] = b['cat']['value']
        if 'img' in b: it['obrazek'] = urllib.parse.unquote(b['img']['value'].rsplit('/', 1)[1])
        if 'cswiki' in b: it['cswiki'] = b['cswiki']['value']
        t = b.get('typeLabel', {}).get('value')
        if t and t not in it['typy']: it['typy'].append(t)
    # nejdřív významné (článek na cs Wikipedii), pak s kategorií na Commons, pak zbytek
    S['kandidati'] = sorted(items.values(), key=lambda x: (not x['cswiki'], not x['kategorie'], x['qid']))
    log('kandidátů z Wikidat', len(S['kandidati']))


# ---------------- 2 fotky z Commons ----------------
def commons(**p):
    p.update(format='json'); time.sleep(0.6)
    return json.loads(http('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p)))


def fotky(it, d):
    soubory = []
    if it['kategorie']:
        r = commons(action='query', list='categorymembers', cmtitle='Category:' + it['kategorie'], cmtype='file', cmlimit=40)
        soubory = [m['title'] for m in r.get('query', {}).get('categorymembers', [])]
    if it['obrazek'] and 'File:' + it['obrazek'] not in soubory: soubory.insert(0, 'File:' + it['obrazek'])
    soubory = [s for s in soubory if re.search(r'\.(jpe?g|png)$', s, re.I)][:12]
    vys = []
    for i in range(0, len(soubory), 10):
        r = commons(action='query', titles='|'.join(soubory[i:i + 10]), prop='imageinfo', iiprop='url|extmetadata', iiurlwidth=960)
        for pg in r.get('query', {}).get('pages', {}).values():
            ii = (pg.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
            lic = md.get('LicenseShortName', {}).get('value', '')
            if not FREE.match(lic.strip()) or not ii.get('thumburl'): continue
            autor = re.sub(r'<[^>]+>', '', md.get('Artist', {}).get('value', '?')).strip()[:80]
            jm = slug(pg['title'][5:].rsplit('.', 1)[0]) + '.jpg'
            cil = os.path.join(d, jm)
            if not os.path.exists(cil):
                open(cil, 'wb').write(http(ii['thumburl'], timeout=120)); time.sleep(0.6)
            vys.append({'soubor': jm, 'titul': pg['title'], 'autor': autor, 'licence': lic, 'url': ii.get('descriptionurl', '')})
            if len(vys) >= 6: break
        if len(vys) >= 6: break
    with open(os.path.join(d, 'ZDROJE.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {it['nazev']} ({it['qid']})\n\nWikimedia Commons, jen volné licence. Použití jen jako předloha pro model.\n\n| soubor | autor | licence | zdroj |\n|---|---|---|---|\n")
        for v in vys: f.write(f"| {v['soubor']} | {v['autor']} | {v['licence']} | {v['url']} |\n")
    return vys


# ---------------- 3 ortofoto ----------------
def orto(it, d):
    cil = os.path.join(d, 'orto.jpg')
    if os.path.exists(cil): return
    R = 60.0; dla, dlo = R / 110574, R / 71400
    url = ('https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=0&STYLES='
           f"&CRS=EPSG:4326&BBOX={it['lat'] - dla},{it['lon'] - dlo},{it['lat'] + dla},{it['lon'] + dlo}&WIDTH=480&HEIGHT=480&FORMAT=image/jpeg")
    data = http(url, timeout=120)
    if data[:2] == b'\xff\xd8': open(cil, 'wb').write(data)


# ---------------- 4 texty (qwen3:14b + ověření) ----------------
SCHEMA_TXT = {'type': 'object', 'properties': {'text': {'type': 'string'}, 'citace': {'type': 'array', 'items': {'type': 'string'}}},
              'required': ['text', 'citace']}
norm = lambda s: re.sub(r'\s+', ' ', s.replace(' ', ' ')).strip().lower()


def overeni(navrh, zdroj):
    z = norm(zdroj); chyby = []
    for c in navrh.get('citace', []):
        if len(c) < 15 or norm(c) not in z: chyby.append(f'citace není ve zdroji: „{c[:60]}“')
    for n in re.findall(r'\d+', navrh.get('text', '')):
        if n not in zdroj: chyby.append(f'číslo {n} není ve zdroji')
    t = navrh.get('text', '')
    if not (60 <= len(t) <= 600): chyby.append('délka textu mimo 60–600 znaků')
    if not navrh.get('citace'): chyby.append('chybí citace')
    return chyby


def text(it):
    if not it.get('cswiki'): return {'stav': 'bez cs Wikipedie'}
    titul = urllib.parse.unquote(it['cswiki'].rsplit('/', 1)[1])
    r = json.loads(http('https://cs.wikipedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'exchars': 4000, 'titles': titul, 'format': 'json'})))
    zdroj = next(iter(r['query']['pages'].values())).get('extract', '')
    if len(zdroj) < 200: return {'stav': 'krátký zdroj'}
    prompt = (f"Zdrojový text z české Wikipedie o objektu „{it['nazev']}“:\n<<<\n{zdroj}\n>>>\n\n"
              "Napiš česky 2–3 věty pro turistickou mapu (co to je, kdy a kým vzniklo, čím je zajímavé). "
              "Používej VÝHRADNĚ fakta ze zdrojového textu, nic nedomýšlej. Do pole citace dej 1–3 doslovné úryvky "
              "ze zdroje (každý aspoň 15 znaků), ze kterých věty vycházejí. Vrať JSON.")
    for pokus in range(2):
        navrh = llm(MODEL_TXT, prompt, SCHEMA_TXT)
        chyby = overeni(navrh, zdroj)
        if not chyby: return {'stav': 'koncept', 'text': navrh['text'], 'citace': navrh['citace'], 'zdroj': it['cswiki']}
        prompt += '\n\nPředchozí odpověď neprošla kontrolou: ' + '; '.join(chyby) + '. Oprav to.'
    return {'stav': 'zamítnuto kontrolou', 'chyby': chyby, 'navrh': navrh.get('text', '')}


# ---------------- 5 třídění fotek (qwen3-vl:8b) ----------------
SCHEMA_VL = {'type': 'object', 'properties': {'druh': {'type': 'string', 'enum': ['exterier_cely', 'exterier_detail', 'interier', 'jine']},
                                              'popis': {'type': 'string'}}, 'required': ['druh', 'popis']}


def trideni(it, d, foto):
    for f in foto:
        if f.get('druh'): continue
        tep(f"{it['qid']} třídění {f['soubor']}")
        b64 = base64.b64encode(open(os.path.join(d, f['soubor']), 'rb').read()).decode()
        o = llm(MODEL_VL, f"Fotka objektu „{it['nazev']}“. Urči druh: exterier_cely (je vidět celá stavba zvenku), exterier_detail "
                          "(jen část fasády, portál, socha zblízka), interier, jine (mapa, plán, dokument, nesouvisí). "
                          "Do popisu napiš česky jednou větou, co je vidět a z jaké strany.", SCHEMA_VL, images=[b64], timeout=240)
        f['druh'] = o['druh'] if o.get('druh') in SCHEMA_VL['properties']['druh']['enum'] else 'jine'
        f['popis'] = str(o.get('popis', ''))[:200]


# ---------------- 6 report ----------------
def report(S):
    kat = [S['hotovo'][q] for q in sorted(S['hotovo'])]
    kat.sort(key=lambda k: (-sum(1 for f in k.get('foto', []) if f.get('druh') == 'exterier_cely'), -len(k.get('foto', []))))
    json.dump(kat, open(os.path.join(OUT, 'katalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    koncepty = [{'nazev': k['nazev'], 'lat': k['lat'], 'lon': k['lon'], 'text': k['text']['text'], 'zdroj': k['text']['zdroj'], 'KONCEPT': True}
                for k in kat if k.get('text', {}).get('stav') == 'koncept']
    json.dump(koncepty, open(os.path.join(OUT, 'mista_koncepty.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    h = ['<!doctype html><meta charset="utf-8"><title>Noční katalog dominant</title><style>body{font:14px system-ui;margin:16px;max-width:1200px}'
         '.k{border-top:1px solid #ccc;padding:10px 0}.f img{height:150px;margin:2px}.f span{font-size:11px;display:block}</style>',
         f'<h1>Kandidáti na dominanty ({len(kat)})</h1><p>Seřazeno podle počtu celkových fotek exteriéru. Texty jsou KONCEPTY – ověřit.</p>']
    for k in kat:
        d = slug(k['qid'] + '_' + k['nazev'])
        h.append(f"<div class=k><h2>{html.escape(k['nazev'])} <small>{k['qid']} · {', '.join(map(html.escape, k['typy'][:3]))} · "
                 f"{k['lat']:.5f}, {k['lon']:.5f}</small></h2>")
        t = k.get('text', {})
        if t.get('stav') == 'koncept': h.append(f"<p><b>Koncept:</b> {html.escape(t['text'])} <a href='{t['zdroj']}'>zdroj</a></p>")
        else: h.append(f"<p><i>text: {html.escape(t.get('stav', '-'))}</i></p>")
        h.append('<div class=f>' + (f"<img src='katalog/{d}/orto.jpg' title='ortofoto'>" if os.path.exists(os.path.join(KAT, d, 'orto.jpg')) else ''))
        for f in k.get('foto', []):
            h.append(f"<a href='{html.escape(f['url'])}'><img src='katalog/{d}/{f['soubor']}' title='{html.escape(f.get('popis', ''))}'></a>")
        h.append('</div><p class=f>' + ' · '.join(f"{html.escape(f.get('druh', '?'))}" for f in k.get('foto', [])) + '</p></div>')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write('\n'.join(h))
    log('report', len(kat), 'položek,', len(koncepty), 'konceptů textů')


def main():
    S = nacti_stav()
    tep('start')
    if not S.get('kandidati'):
        tep('kandidati'); faze_kandidati(S); uloz_stav(S)
    for i, it in enumerate(S['kandidati']):
        q = it['qid']
        if q in S['hotovo'] and S['hotovo'][q].get('kompletni'): continue
        if S['karantena'].get(q, 0) >= 2:                   # dvakrát shodil nebo zasekl zpracování -> přeskočit
            if q not in S['hotovo']: log('přeskakuji (karanténa)', q, it['nazev'])
            S['hotovo'].setdefault(q, {**it, 'chyba': 'karanténa'}); continue
        d = os.path.join(KAT, slug(q + '_' + it['nazev'])); os.makedirs(d, exist_ok=True)
        k = S['hotovo'].get(q) or dict(it)
        try:
            tep(f'{q} fotky')
            if 'foto' not in k: k['foto'] = fotky(it, d)
            tep(f'{q} orto'); orto(it, d)
            tep(f'{q} text')
            if 'text' not in k: k['text'] = text(it)
            S['hotovo'][q] = k; uloz_stav(S)
            if it.get('cswiki'): trideni(it, d, k['foto'][:4])   # třídění fotek jen u významných (čas GPU)
            k['kompletni'] = True
        except Exception as e:                              # chyba sítě apod.: zapsat a jít dál (pád celého skriptu řeší hlídač)
            k['chyba'] = f'{type(e).__name__}: {e}'[:300]; log('chyba', q, k['chyba'])
        S['hotovo'][q] = k; uloz_stav(S)
        if (i + 1) % 25 == 0: report(S)                      # průběžný report, ať je ráno co číst i když práce nedoběhne
        log(f"{i + 1}/{len(S['kandidati'])}", q, it['nazev'], 'fotek', len(k.get('foto', [])), 'text:', k.get('text', {}).get('stav'))
    tep('report'); report(S)
    open(os.path.join(OUT, 'HOTOVO.txt'), 'w', encoding='utf-8').write(time.strftime('%Y-%m-%d %H:%M') + '\n')
    tep('hotovo')


if __name__ == '__main__':
    try: main()
    except Exception:
        log('PÁD\n' + traceback.format_exc()); sys.exit(3)
