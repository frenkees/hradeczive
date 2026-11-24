"""Podklady pro model JEDNÉ dominanty (noční skript, lokální Ollama; bez placených služeb).

python skripty/noc/noc_objekt.py "<název>" <lat> <lon> [--slug kostel_xyz] [--wiki "Titul článku cs Wikipedie"] [--ceka]
  z izohradec/, venv: izomapa/.venv/Scripts/python.exe, PYTHONUTF8=1

Co udělá (výstup izomapa/landmarks_ref/<slug>/, mimo git):
  1 Wikipedie  najde článek na cs Wikipedii (nebo --wiki) a stáhne text
  2 fotky      Wikimedia Commons: snímky do 150 m od bodu + hledání podle názvu, jen volné licence (CC0, CC BY, CC BY-SA, PD),
               až 14 fotek 1280 px; autor a licence do ZDROJE.md
  3 orto       výřez ortofota ČÚZK 120 × 120 m (půdorys, orientace střech)
  4 popis      qwen3-vl:8b: u každé fotky strana pohledu, druh (celek / detail / interiér / jiné) a tvary pro modelování
  5 fakta      qwen3:14b: fakta pro model (sloh, střecha, věž, materiály, barvy, rozměry, rok) ze Wikipedie; každé číslo a každá
               citace musí být doslova ve zdroji, jinak se zahodí (nic se nedomýšlí)
  info.md + info.json = souhrn pro modelování (označeno KONCEPT k ruční kontrole)
--ceka  počká, až doběhne noční přerender (build/rerender_all.log obsahuje KONEC), ať se nepere o GPU.

Nové dominanty příště: stačí zavolat tento skript s názvem a souřadnicemi, dohledání fotek a informací se pak nedělá ručně.
"""
import argparse, base64, json, os, re, sys, time, traceback, unicodedata, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noc_katalog as K

ROOT = K.ROOT
FREE = K.FREE
log, http, llm = K.log, K.http, K.llm
slug = lambda t: re.sub(r'[^a-z0-9]+', '_', unicodedata.normalize('NFKD', t.lower()).encode('ascii', 'ignore').decode()).strip('_')[:60] or 'x'


def najdi_wiki(nazev):
    r = json.loads(http('https://cs.wikipedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'list': 'search', 'srsearch': nazev + ' Hradec Králové', 'srlimit': 5, 'format': 'json'})))
    hits = r['query']['search']
    return hits[0]['title'] if hits else None


def wiki_text(titul):
    r = json.loads(http('https://cs.wikipedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'exchars': 12000, 'titles': titul, 'format': 'json', 'redirects': 1})))
    return next(iter(r['query']['pages'].values())).get('extract', '')


def stahni_fotky(nazev, lat, lon, d, kategorie=None):
    soubory = []
    r = K.commons(action='query', list='geosearch', gscoord=f'{lat}|{lon}', gsradius=150, gsnamespace=6, gslimit=40)
    soubory += [g['title'] for g in r.get('query', {}).get('geosearch', [])]
    r = K.commons(action='query', list='search', srsearch=nazev + ' Hradec Králové', srnamespace=6, srlimit=30)
    soubory += [g['title'] for g in r.get('query', {}).get('search', [])]
    if kategorie:
        r = K.commons(action='query', list='categorymembers', cmtitle='Category:' + kategorie, cmtype='file', cmlimit=40)
        soubory += [m['title'] for m in r.get('query', {}).get('categorymembers', [])]
    soubory = list(dict.fromkeys(s for s in soubory if re.search(r'\.(jpe?g|png)$', s, re.I)))
    vys = []
    for i in range(0, len(soubory), 10):
        r = K.commons(action='query', titles='|'.join(soubory[i:i + 10]), prop='imageinfo', iiprop='url|extmetadata', iiurlwidth=1280)
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
        if len(vys) >= 14: break
    with open(os.path.join(d, 'ZDROJE.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {nazev}\n\nWikimedia Commons, jen volné licence. Použito jen jako předloha pro model.\n\n| soubor | autor | licence | zdroj |\n|---|---|---|---|\n")
        for v in vys[:14]: f.write(f"| {v['soubor']} | {v['autor']} | {v['licence']} | {v['url']} |\n")
    return vys[:14]


SCHEMA_VL = {'type': 'object', 'properties': {
    'druh': {'type': 'string', 'enum': ['exterier_cely', 'exterier_detail', 'interier', 'jine']},
    'je_objekt': {'type': 'boolean'}, 'strana': {'type': 'string'}, 'tvary': {'type': 'string'}, 'barvy': {'type': 'string'}}, 'required': ['druh', 'je_objekt', 'strana', 'tvary', 'barvy']}


def popis_fotek(nazev, d, foto):
    for f in foto:
        if f.get('druh'): continue
        K.tep(f'objekt {f["soubor"]}')
        b64 = base64.b64encode(open(os.path.join(d, f['soubor']), 'rb').read()).decode()
        o = llm(K.MODEL_VL, f'Fotka objektu „{nazev}“. Vrať JSON: je_objekt (true jen když je na fotce právě tento objekt), druh (exterier_cely = celá stavba zvenku, exterier_detail, interier, jine), '
                            'strana (z které strany světa nebo od které ulice je pohled, pokud to jde poznat, jinak „neznámá“), '
                            'tvary (česky, 1–2 věty pro modeláře: půdorys, počet pater, tvar a sklon střechy, věž a její zakončení, okna, portál), '
                            'barvy (omítka, střecha, kamenné prvky). Nevymýšlej, co na fotce není vidět.', SCHEMA_VL, images=[b64], timeout=300)
        f.update({k: str(o.get(k, ''))[:300] for k in ('strana', 'tvary', 'barvy')})
        f['je_objekt'] = bool(o.get('je_objekt'))
        f['druh'] = o['druh'] if o.get('druh') in SCHEMA_VL['properties']['druh']['enum'] else 'jine'


SCHEMA_F = {'type': 'object', 'properties': {'fakta': {'type': 'array', 'items': {'type': 'object', 'properties': {
    'tema': {'type': 'string', 'enum': ['sloh', 'rok', 'architekt', 'strecha', 'vez', 'material', 'barva', 'rozmery', 'pudorys', 'okolí', 'jine']},
    'text': {'type': 'string'}, 'citace': {'type': 'string'}}, 'required': ['tema', 'text', 'citace']}}}, 'required': ['fakta']}


def fakta(nazev, zdroj):
    prompt = (f'Zdrojový text z české Wikipedie o objektu „{nazev}“:\n<<<\n{zdroj}\n>>>\n\n'
              'Vypiš fakta užitečná pro 3D model budovy: sloh, rok vzniku, architekt, tvar střechy, věž (výška, zakončení), materiály, barvy, '
              'rozměry, půdorys, okolí. Používej VÝHRADNĚ fakta ze zdroje, nic nedomýšlej. Ke každému faktu dej doslovnou citaci ze zdroje '
              '(aspoň 15 znaků). Vrať JSON.')
    for pokus in range(2):
        navrh = llm(K.MODEL_TXT, prompt, SCHEMA_F, timeout=600)
        z = K.norm(zdroj); ok, chyby = [], []
        for x in navrh.get('fakta', []):
            c = x.get('citace', '')
            if len(c) < 15 or K.norm(c) not in z: chyby.append(f'citace není ve zdroji: „{c[:50]}“'); continue
            if any(n not in zdroj for n in re.findall(r'\d+', x.get('text', ''))): chyby.append('číslo není ve zdroji: ' + x['text'][:50]); continue
            ok.append(x)
        if ok: return ok, chyby
        prompt += '\n\nPředchozí odpověď neprošla kontrolou: ' + '; '.join(chyby[:5]) + '. Oprav to.'
    return [], chyby


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nazev'); ap.add_argument('lat', type=float); ap.add_argument('lon', type=float)
    ap.add_argument('--slug'); ap.add_argument('--wiki'); ap.add_argument('--kategorie'); ap.add_argument('--ceka', action='store_true')
    a = ap.parse_args()
    if a.ceka:
        L = os.path.join(ROOT, 'build', 'rerender_all.log')
        for _ in range(6 * 60):                       # nejdéle 6 h
            if os.path.exists(L) and 'KONEC' in open(L, encoding='utf-8', errors='ignore').read(): break
            time.sleep(60)
    d = os.path.join(ROOT, 'landmarks_ref', a.slug or slug(a.nazev)); os.makedirs(d, exist_ok=True)
    K.tep('objekt ' + a.nazev); log('objekt', a.nazev, '->', d)
    titul = a.wiki or najdi_wiki(a.nazev); zdroj = wiki_text(titul) if titul else ''
    log('wikipedie:', titul, len(zdroj), 'znaků')
    foto = stahni_fotky(a.nazev, a.lat, a.lon, d, a.kategorie); log('fotek', len(foto))
    K.orto({'lat': a.lat, 'lon': a.lon}, d)
    popis_fotek(a.nazev, d, foto)
    f, chyby = fakta(a.nazev, zdroj) if len(zdroj) > 200 else ([], ['bez článku na cs Wikipedii'])
    info = {'KONCEPT': True, 'nazev': a.nazev, 'lat': a.lat, 'lon': a.lon, 'wikipedie': titul and 'https://cs.wikipedia.org/wiki/' + urllib.parse.quote(titul.replace(' ', '_')),
            'fakta': f, 'zamitnuto': chyby, 'foto': foto, 'vytvoreno': time.strftime('%Y-%m-%d %H:%M')}
    json.dump(info, open(os.path.join(d, 'info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(d, 'info.md'), 'w', encoding='utf-8') as o:
        o.write(f"# {a.nazev} – podklady pro model (KONCEPT, zkontrolovat)\n\nZdroj textu: {info['wikipedie']}\n\n## Fakta (ověřená proti zdroji)\n")
        for x in f: o.write(f"- **{x['tema']}**: {x['text']}  \n  _„{x['citace']}“_\n")
        o.write('\n## Fotky\n')
        for v in sorted(foto, key=lambda v: not v.get('je_objekt')): o.write(f"- `{v['soubor']}` ({'TENTO OBJEKT' if v.get('je_objekt') else 'jiný objekt'}, {v.get('druh')}, {v.get('strana')}): {v.get('tvary')} Barvy: {v.get('barvy')} – {v['autor']}, {v['licence']}\n")
        if chyby: o.write('\n## Zamítnuto kontrolou\n' + '\n'.join('- ' + c for c in chyby) + '\n')
    log('hotovo', d); K.tep('objekt hotovo')


if __name__ == '__main__':
    try: main()
    except Exception:
        log('PÁD\n' + traceback.format_exc()); sys.exit(3)
