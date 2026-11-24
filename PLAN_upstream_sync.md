# Plán: sladění s upstreamem izomapy a čistý fork

Stav k 2026-11-23. Jen analýza a plán, nic se zatím neměnilo. Zkušební merge proběhl v dočasném worktree a byl zrušen (`git merge --abort`, worktree smazán).

## 1. Výchozí stav (zjištěno)

| | |
|---|---|
| merge-base | `d37658b` (2026-11-12) |
| naše větev `hradec` | 63 commitů, `a3ab124` (= `zaloha/hradec`, tedy zálohováno), 60 souborů, +29 202 / −288 řádků |
| upstream `origin/main` | 72 commitů (PR #110–#160), 107 souborů, +11 006 / −45 |
| **nekomitováno v `izomapa/`** | 16 upravených souborů (`prep.py` plachta + `skryt`, `overlay.py`, `dzi.py`, `web/app.html` +212 ř. formulář s fotkou a doplňky, `mesto.json`, 11× `assets/*.json`) + nesledované `plugins.py`, `priklady/doplnky.sample.json`, `assets/plachta_studie.json` |
| nekomitováno v kořeni | `.gitignore`, `STAV_PROJEKTU.md`, `skripty/pripravit_vercel.mjs`, `skripty/vercel_api/report.js` + nové skripty (`hlaseni_soukrome.mjs`, `opravy_hlaseni.py`, `plachta*.py/sh`, `umami_id.txt`) |

Pozn.: část našich commitů jsou dřívější ruční převzetí z upstreamu (render jen změn, hřiště, soused bez značky, popisky obcí, povrchy, semafory, vánoce, revertnutí chodci/cyklisti). Při merge se buď sloučí samy, nebo dělají konflikty typu add/add.
Nesledovaný `plugins.py` by skutečný merge zablokoval (upstream ho přidává) – před merge komitnout nebo smazat (je to starší kopie upstreamu).

## 2. Zkušební merge `origin/main` → `hradec` (commit `a3ab124`, bez nekomitovaných změn)

**13 souborů v konfliktu, 29 bloků.** Ostatních 94 změněných souborů se sloučilo samo (nové `web/js/*`, `web/css/*`, `doplnky/`, `pamatky/`, `knihovny/`, testy).

| soubor | bloky / řádky | povaha | řešení |
|---|---|---|---|
| `web/app.html` | 4 / 3 318 | **zásadní**: upstream z něj udělal 160řádkovou šablonu (`<!-- @css -->`, `<!-- @js -->`), kód je v `web/js/00…90-*.js` | vzít upstream šablonu, naše změny (~1 170 ř.) přenést do `web/js`/`web/css` nebo do doplňků (viz 3.3) – **rozhodnutí + 1–2 dny práce** |
| `prep.py` | 2 / 12 | `top_` výška vozidel (naše `tw`/`top` vs. upstream `pam_vrsek`), `'koleje': KOLEJE` ve scéně | triviální: ponechat obojí |
| `overlay.py` | 1 / 11 | `json.dump` – upstream přidal `doplnky` | vzít upstream (naše ruční kopie plugin systému tím odpadne) |
| `build_html.py` | 4 / 43 | importy, `SOC_IKONY`+`odkaz_html` (FB/IG), `og_obrazek(dolu=)`, náhrady `DOPRAVA_HERE` vs `PLUHY/NASTUPISTE/MHD`, `DALSI_ZDROJE` vs `PLUHY_ZDROJ` | sjednotit obojí, `og_obrazek` vzít upstream (rozlišení) – střední |
| `mhd.py` | 2 / 36 | naše `KVAL` (kvalita úseků) + terminál vs. upstream `PRUJEZD` (průjezdné zastávky) | spojit obojí – střední, otestovat `mhd.py` |
| `novy_mesto.py` | 2 / 87 | naše `--bbox/--stred` vs. upstream `--detailni` | spojit (oba jsou obecné; `--bbox` → kandidát PR) |
| `nastroje/otisk.py` | 2 / 25 | add/add: upstream přidal `mpp` a památky do otisku | vzít upstream |
| `nastroje/semafory.py` | 1 / 5 | jen komentář | triviální |
| `render.html` | 1 / 20 | naše svislé značky `sg_*` vs. upstream přístřešky u památek | ponechat obojí |
| `render_chunk.sh` | 1 / 9 | upstream odstranil `mpp=0.2` (bere z `mesto.json` `rozliseni`) | vzít upstream (výchozí 0,2 m/px = beze změny) |
| `render_ctverec.sh` | 3 / 22 | naše časy fází prep/render/dzi | ponechat naše + upstream text |
| `postav.sh` | 2 / 10 | upstream `pole_cesty.py` | vzít upstream; **`pole_cesty` mění pole → nová `zabaged.json`?** ověřit |
| `CLAUDE.md` | 3 / 26 | dokumentace | sloučit ručně |

Triviální: 8 souborů (~15 min). Vyžaduje rozhodnutí: `web/app.html` (architektura), `build_html.py`, `mhd.py`, `novy_mesto.py`.
K tomu nekomitované změny v `overlay.py`/`dzi.py`/`web/app.html` (ruční port doplňků) – po merge zahodit ve prospěch upstreamu.

**Věcné kolize bez textového konfliktu (pozor):**
- `skryt` v `upresneni.json` `b` (naše) vs. `skryt_budovy` (upstream #152) – sjednotit na upstream klíč, `opravy_hlaseni.py` upravit.
- Chodci a cyklisté: upstream je má **výchozí zapnuté**; my jsme je revertovali („chodí po silnici“) → `"chodci": false` v `mesto.json`, nebo zkusit upstream verzi (#129 opravy, deštníky).
- `dzi.py` verze dlaždic po čtvercích (#160) mění `tiles.json` – ověřit `skripty/pripravit_vercel.mjs` a `nahrat_dlazdice_r2.mjs` (cache hlavičky, `?v=`).
- Upstream mění `render.html` (+297), `render.mjs`, `dzi.py` a otisk (mpp, památky) → **všech 25 čtverců se překreslí** (viz 5).
- Pole (`pole_cesty.py`, #149/#151), zatrubněné potoky, parkoviště podle OSM (#134), nástupiště, letiště mění vzhled – posoudit na náhledu.

## 3. Cílová architektura: „Hradec jako vrstva nad čistým upstreamem“

### 3.1 Co je čistě datové (žádný patch generátoru) – už dnes
`mesto.json`, `assets/upresneni.json` (`b`, `plochy`, `custom_bld`, `stada`, `sousedi`, `skryt_budovy`), `assets/oblasti.json`, `assets/dominanty.json`,
`assets/custom_models.js` (vlastní modely), `assets/custom_prep.py` (hook pasportu magistrátu, `IZO_MMHK`), `assets/znacky.json`, `assets/prestavby.json`,
`assets/mhd_trasy_*.json`, `assets/terminal_hd.json`, `assets/vanoce.json`, `mista.json`, `pamatky/<slug>.*` (upstream systém památek – kandidát pro naše dominanty `lm`).

### 3.2 Co může být doplněk (`doplnky/<id>/` + `assets/doplnky/<id>.json`)
API upstreamu: build hook `overlay_hook.py` (jen ve fázi `overlay.py`, ne `prep.py`), klient `registerPlugin`, `onFrame` (world/sky/top), `onMapClick`, `getUiSlot('sidebar-tabs')`, `getPluginLayer`, `private` volby.

| naše funkce | jako doplněk? | chybějící extension point |
|---|---|---|
| Zápasy FC + LED aréna (`assets/custom_web.js`, `/api/zapasy`) | **ano** `doplnky/hk_zapasy` (onFrame + onMapClick) | – (`custom_web.js`/`IZOMAPA_PLUGINS` je náš hook, odpadne) |
| Odjezdová tabule vlaků | ano (onMapClick na budovu, onFrame) | `onBuildingClick(id)` / slot v kartě budovy |
| Formulář hlášení s fotkou a e-mailem | **ano, obecný** `doplnky/hlaseni` (klient) + server `skripty/vercel_api/report.js` | slot „akce v kartě budovy“ (`getUiSlot('karta')`) – navrhnout upstreamu; upstream má i vlastní `izomapa/hlaseni/` (Cloudflare) → porovnat |
| Doprava TomTom/HERE (`api/doprava`, hustota aut podle `jamFactor`) | částečně: čáry vytížení ano (onFrame), **hustota aut ne** | hook do `70-animace.js` (`CAR_DENS` / `roadDensity(r)`), `doprava_here` v `overlay.py` je naše |
| Plachta (řídké vrstvy dlaždic + checkbox) | klient ano | API „přídavná vrstva dlaždic“ (`addTileLayer`); prep část → `custom_prep.py` (chybí hook pro silnice/budovy – nyní v `prep.py`) |
| Analytika (Umami, Vercel Analytics) | **ne** – vkládá se při nasazení (`pripravit_vercel.mjs`), tak to nechat | – |
| MHD DPMHK, vlaky z GTFS, NAD | data + `nastroje/*` (obecné) | – |
| Přejezdy/závory, semafory se světly, svislé značky, koleje 3D, modely souprav, terminál | **ne doplněk** – obecné vylepšení generátoru → PR | – |

### 3.3 Co zůstane patchem generátoru (cíl: < ~300 řádků, oddělené commity)
- `prep.py`: rozšíření `upresneni.b` (`h` před laserem DMP, `fl`, `cls`, `cls_cz`, `name`, `sachta`), přístřešky z vozovky na chodník, dálnice (křížení, pás), mosty/mostovky/zářezy/podjezdy, silnice ve výstavbě, `prestavby.json`, `KOLEJE`. **Vše kromě Plachty a pasportu je obecné → PR.**
- Plachta v `prep.py` (`IZO_PLACHTA`) → přesunout do `assets/custom_prep.py` (případně navrhnout hook fázi `roads`/`buildings`).
- `mhd.py` (kvalita úseků, terminál), `road_route.py` (jednosměrky), `geo.py`, `build_html.py` (`dalsi_zdroje`, soc. ikony), `novy_mesto.py --bbox`, `nastroje/teren_dmr.py` (DMR 5G), Windows opravy (`render.mjs` porty, `PYTHONUTF8`), časy fází.

### 3.4 Je cíl „update upstreamu nerozbije naši práci a mapa se sama zlepší“ reálný?
**Částečně ano.** Data, `custom_prep.py`, `custom_models.js` a doplňky přežijí upstream update bez zásahu. Reálné za podmínek:
1. patch set nad upstreamem je malý (ideálně jen to, co upstream nepřijal) a v samostatných commitech;
2. hlavní obecné funkce se dostanou do upstreamu (jinak každý merge = ruční konflikty v `prep.py`/`web/js`);
3. pravidelný `git merge origin/main` **každý týden** (ne cherry-pick po jednom – při 72 commitech za 11 dní je to neudržitelné; dosavadní pravidlo v STAV_PROJEKTU.md změnit);
4. upstream API doplňků je stabilní (je čerstvé, v2 od #132 – riziko změn); doplňky psát jen přes `window.Izomapa`, ne přes vnitřní proměnné `web/js`;
5. kontrola po merge: `pytest tests/`, `node tests/*.mjs`, náhled 2–3 míst `nahled_mista.py` (bílá věž, soutok, Mileta), porovnání s předchozím náhledem;
6. „sama se zlepší“ = nové funkce upstreamu se objeví po překreslení – každé překreslení ~35–50 min a vizuální kontrola, takže ne automaticky, ale levně.
Automatické nasazení bez lidské kontroly **nedoporučuji** (vzhled se mění, např. pole, chodci).

## 4. Správný fork a struktura repozitářů

**Doporučení: dva repozitáře, izomapa jako skutečný GitHub fork.**
- `frenkees/izomapa` = skutečný fork `adamklatovsky/izomapa` (`gh repo fork adamklatovsky/izomapa --clone=false`; uživatel smí mít jen jeden fork, jméno lze změnit).
  - `main` = zrcadlo upstreamu (jen fast-forward), větve `pr/<tema>` z `main` pro PR (GitHub fork umožní PR jedním klikem),
  - `hradec` = `main` + náš patch set + městská data (jako dnes, `git add -f`),
  - push současné `hradec` historie beze změny (historie se zachová; SHA zůstanou).
- `frenkees/hradeczive-izomapa` (dnešní `zaloha`): po ověření forku archivovat (read-only), nemazat.
- `frenkees/hradeczive` (kořen): skripty, nasazení, dokumentace, Vercel API. `izomapa/` dál v `.gitignore`, ale do kořene zapsat **pin**: soubor `IZOMAPA_VERZE` (SHA `hradec` použitý pro nasazení), nebo git **submodul** na fork (větev `hradec`).
- **Submodul vs. subtree vs. monorepo:** monorepo/subtree by vtáhlo kód generátoru do kořene a ztížilo merge upstreamu a PR → ne. Submodul je čistý, ale na Windows a s 30 MB `assets/` občas otravný; **stačí pin SHA** (jednodušší, stejný přínos). Rozhodne uživatel.
- Varianta B (pozdější): městská data přesunout z forku do kořene (`hradeczive/mesto/` → kopírovat/symlink do `izomapa/assets`) a `hradec` by obsahoval jen kód. Výhoda: fork čistší; nevýhoda: symlinky na Windows, víc kroků stavby. Teď nedělat.
- `.gitignore` (kořen i fork): `build/`, `site/`, `data*/`, `preview/`, `landmarks_ref/`, `assets/mmhk.json`, `assets/mmhk_znaceni/`, `nasazeni/vercel/`, `.env*`, `.vercel/`, `api_here.txt`, `tomtomapi.txt`, `restapikey.txt`, `nasazeni/tajne.env`, `nasazeni/wedos_kontakt.json`, `_wt_*/`, `*.pdf` a `studie*.jpg`/`studie_colored.png` v kořeni (zdroje s nejasnou licencí), `skripty/umami_id.txt` (není tajné, ale ID – rozhodnout).
- Před prvním pushem do veřejného forku: `git log -p --all | grep -iE "api[_-]?key|token|secret|re_[A-Za-z0-9]{10}"` (tajemství v historii); v kořeni nyní jsou `api_here.txt`, `tomtomapi.txt`, `restapikey.txt` – ignorované, ověřit, že nikdy nebyly v historii. Dlaždice zůstávají v R2, ne v gitu.
- Zbytky: v kořeni je složka `_wt_merge` (starý worktree?) – zjistit a uklidit (`git worktree prune`).

## 5. Rizika, zálohy, dopad na web

- **Zálohy před merge:** tag `pred-sync-2026-11` na `hradec` (lokálně i do forku), `git bundle create ../zaloha_izomapa.bundle --all`, kopie `assets/*.json` (jsou v gitu přes `-f`, ale nekomitované změny ne!). Kořen: commit nekomitovaných změn.
- **Rollback:** merge dělat ve větvi `sync/upstream-2026-11` ve worktree `../izomapa_sync`; `hradec` se posune až po schválení (`git merge --ff-only`). Web: Vercel `vercel rollback` / předchozí deployment; R2 dlaždice nahrávat do nové verze (verze po čtvercích) – staré zůstanou, dokud se nepřepíše `tiles.json`.
- **Překreslení:** změna `render.html`/`render.mjs`/`dzi.py` + nový otisk (`mpp`, památky) ⇒ všech 25 čtverců × 5 vrstev (+ vánoce). Odhad 25 × ~4 min / 2 souběžně ≈ **50 min** (STAV uvádí celé město ~35 min) + `dzi` + nahrání do R2: prakticky všechny dlaždice se změní → upload celé pyramidy (při ~1 MB/s hodiny; změřit velikost `site/tiles`). Lze zkrátit: nejdřív jen čtverec 0,0 jako kontrolní výřez.
- **Střed mřížky a `href` se nemění** – upstream na ně nesahá (ověřit `geo.py` po merge: `MPP` z `rozliseni`, výchozí 0,2 = beze změny).
- Plachta (`skripty/plachta.sh`) a vánoční vrstvy používají `dzi.py` řídké vrstvy – po změně `dzi.py` (verze, `VARIANTY`) přetestovat.
- **Co otestovat:** `pytest tests/` (+ `doplnky/najdi_to/tests`), `node tests/test-*.mjs`, naše `tests/test_here_doprava.py`, `tests/test-doprava-sber.mjs`; `nahled_mista.py` na Bílé věži, soutoku, Miletě, aréně, terminálu, Plachtě; v prohlížeči: MHD, vlaky + přejezdy, semafory, odjezdová tabule, zápasy, formulář hlášení (text, fotka, e-mail – na preview s testovacím issue), `/api/doprava`, `/api/zapasy`, analytika; mobil. Vše nejdřív **preview URL** (`vercel deploy` bez `--prod`), pak produkce.

## 6. Kroky

Značky: **[A]** lze svěřit podagentovi (levnější model u mechanické práce), **[U]** vyžaduje uživatele, **[A+U]** agent připraví, uživatel schválí.

| # | krok | odhad | hotovo, když | kdo |
|---|---|---|---|---|
| 1 | Komitnout rozpracované změny v kořeni i `izomapa/` (formulář s fotkou, Plachta, `skryt`, data); smazat/komitnout `plugins.py` | 30 min | `git status` čistý v obou | [A+U] |
| 2 | Zálohy: tag `pred-sync-2026-11`, bundle, push `hradec` do `zaloha` | 10 min | tag a bundle existují, `zaloha/hradec` = HEAD | [A] |
| 3 | **Rozhodnutí R1–R5** (níže) | – | odpovědi zapsané do tohoto souboru | [U] |
| 4 | Fork na GitHubu `frenkees/izomapa`, remote `fork`, push `main` (=upstream) a `hradec`; kontrola tajemství v historii | 30 min | fork viditelný jako fork, `hradec` tam | [U] (veřejný krok) + [A] |
| 5 | Roztřídit 63 commitů + nekomitované změny na: data HK / obecné → PR / HK kód → doplněk / zahodit (převzato z upstreamu) – tabulka v tomto souboru | 2 h | každý soubor z `git diff d37658b hradec --stat` má kategorii | [A] |
| 6 | Merge `origin/main` ve worktree `../izomapa_sync`, větev `sync/upstream-2026-11`: 8 triviálních konfliktů + `build_html.py`, `mhd.py`, `novy_mesto.py`; `skryt`→`skryt_budovy`; `"chodci"` podle R3 | 3 h | `python -c "import prep"`-úroveň: `prep.py` čtverce 0,0 projde, testy zelené | [A] |
| 7 | `web/app.html`: vzít upstream šablonu, naše UI (hlášení, plachta, doprava, přejezdy, semafory, tabule, FB/IG, vánoce-rozdíly) rozdělit do `web/js/*` / `web/css/*` (obecné) a doplňků (HK) podle R2 | 1–2 dny | `web/sestav.py` sestaví stránku, žádná chyba v konzoli, všechny funkce z kroku 5 fungují | [A] (Fable/silnější model – obecný návrh), [U] vizuální kontrola |
| 8 | Doplňky `doplnky/hk_zapasy`, `doplnky/hlaseni`, `doplnky/odjezdova_tabule`; `custom_web.js` zrušit; Plachta prep → `custom_prep.py` | 1 den | doplňky zapnuté přes `assets/doplnky.json`, `prep.py` bez `IZO_PLACHTA` | [A] |
| 9 | Kontrolní výřez: render čtverce 0,0 + `nahled_mista.py` 6 míst, porovnání se současnými dlaždicemi | 30 min | uživatel náhledy schválí | [A] + [U] |
| 10 | Celé překreslení 25 čtverců (`./postav.sh render`), plachta, vánoce, `dzi` | ~1 h strojově | `render_par.log` bez CHYBA | [A] |
| 11 | Ověřit `pripravit_vercel.mjs`/`nahrat_dlazdice_r2.mjs` s verzemi po čtvercích; nahrát do R2; deploy **preview**; test bodu 5 | 2 h + upload | vše z „Co otestovat“ OK na preview | [A] + [U] klikne formulář |
| 12 | Produkce (`vercel deploy --prod`), `hradec` ← `sync/…` (ff), push do forku, archivace `hradeczive-izomapa` | 20 min | hradeczive běží, fork aktuální | [U] potvrzení |
| 13 | PR do upstreamu (malé, viz 7) – připravit větve `pr/*` z `main` | průběžně | větve připravené, popis, test, ukázka | [A] příprava, **[U] odeslání** |
| 14 | Režim údržby: týdně `git fetch origin && merge origin/main` ve worktree, testy, náhled 0,0; zapsat do STAV_PROJEKTU.md, upravit pravidlo „cherry-pick po jednom“ | 1 h/týden | zapsaný postup, první týdenní merge proběhl | [A] |

Kroky 1–2 a 5 lze hned. 6–8 jsou na sobě závislé. 13 může běžet souběžně od kroku 5.

### Rozhodnutí pro uživatele
- **R1 Fork:** založit skutečný fork `frenkees/izomapa` a archivovat `hradeczive-izomapa`? Pin SHA, nebo submodul v kořeni?
- **R2 Hranice doplňků:** které funkce převést na doplňky (návrh: zápasy, odjezdová tabule, formulář hlášení, Plachta-klient) a které nabídnout upstreamu jako obecné (přejezdy, semafory, značky, mosty, doprava HERE/TomTom?).
- **R3 Upstream novinky se změnou vzhledu:** chodci (výchozí zapnuto), cyklisté, deštníky, pole podle cest, parkoviště podle OSM, nástupiště, sypače ŘSD (fungují jen na Cloudflare, my jsme na Vercelu → asi vypnout), letiště (HK má letiště! – zvážit doplněk `letiste`).
- **R4 Celé překreslení a upload** celé pyramidy do R2 (čas, případně provoz R2) – kdy.
- **R5 PR autorovi:** zda a které PR posílat (navenek viditelné, jménem `frenkees`); jak řešit `skryt` vs. `skryt_budovy` a duplicitní práci (upstream má vlastní hlášení přes Cloudflare `hlaseni/`).

## 7. Co nabídnout upstreamu (PR)

Styl upstreamu: PR z tematické větve (`kasparek-net/pr/…`, `MichalSkoula/…`), jeden námět na PR, název česky ve větě („Oprava: …“, „Zatrubněné potoky přerušovanou čarou“), malý diff, dokumentace v `CLAUDE.md` (odrážka „volitelné“ + klíč v `mesto.json`/`upresneni.json`), ukázka v `priklady/`, test v `tests/` (pytest `test_*.py`, node `test-*.mjs`), výchozí chování beze změny (nové věci vypnuté, nebo neovlivní jiná města). Kód pro město nepatří do `prep.py`/`render.html` (pravidlo upstream CLAUDE.md).

Návrh malých PR (pořadí podle snadnosti přijetí):
1. **Windows opravy** (`render.mjs` blokované porty, `PYTHONUTF8`, `.venv/Scripts`) – malé, jasné.
2. **`dalsi_zdroje` v `mesto.json`** (patička) – sloučit s upstream `*_ZDROJ` náhradami.
3. **`upresneni.json` `b`: ruční `h` přednost před laserem DMP, `fl`, `cls`, `name`** + test (`tests/test_upresneni_b.py`).
4. **`novy_mesto.py --bbox --stred`** (mapa z obdélníku).
5. **Jednosměrky a kruhové objezdy v `road_route.py`** (trasy MHD bez shapes.txt) + test.
6. **Přístřešky zastávek z vozovky na chodník** (prep.py, malé).
7. **Časy fází v `render_par.log`** (render_ctverec.sh).
8. **Terén DMR 5G** (`nastroje/teren_dmr.py`, volitelné, jen ČR) – větší, s dokumentací.
9. **Extension pointy doplňků:** `getUiSlot('karta')` / `onBuildingClick`, `addTileLayer`, hook hustoty aut – nejdřív jako issue/nápad, ne kód.
10. Větší (spíš nápad + ukázka): přejezdy se závorami a výstražníky, semafory se světly, svislé značky z dat, 3D koleje a modely souprav, mosty/zářezy/podjezdy, silnice ve výstavbě + `prestavby.json`, doprava HERE/TomTom jako doplněk, formulář hlášení s fotkou (Vercel Blob/Resend vs. jejich Cloudflare).

Ne posílat (HK specifické): pasport magistrátu (`custom_prep.py`), dominanty a modely, Plachta, zápasy FC, terminál HD, výluka/NAD, analytika.
**Odeslání PR i založení forku je navenek viditelný krok – jen po výslovném souhlasu uživatele.**

## Stav kroku 4 (fork)

- 2026-11-23: sken historie `hradec` i `--all` (názvy souborů + přidané řádky): žádné klíče/tokeny (`re_`, `ghp_`, `github_pat_`, `AKIA`, Blob), žádné soubory tomtomapi.txt/api_here.txt/restapikey.txt/*.env/wedos. Jen zmínky v kódu/dokumentaci a veřejný e-mail autora upstreamu.
- Fork: https://github.com/frenkees/izomapa (isFork, parent adamklatovsky/izomapa). Remote `fork` v `izomapa/`.
- `fork/main` = `origin/main` = 508b2a9 (zrcadlo upstreamu); `fork/hradec` = `hradec` = eab1675; tag `zaloha-pred-upstream-sync` nahrán.
- `frenkees/hradeczive-izomapa` archivován (read-only).
- Kořen: doplněn .gitignore, přidán `IZOMAPA_VERZE` (pin eab1675).


## 8. Krok 5: roztřídění změn `hradec` oproti `d37658b` (2026-11-23)

Kategorie: **D** data/úpravy specifické pro HK, **O** obecné vylepšení generátoru (kandidát PR), **K** HK kód (doplněk / `custom_*`), **Z** zahodit, upstream to už má (ruční převzetí). Podklad: `git diff d37658b hradec --stat` (63 souborů) a 64 commitů `git log d37658b..hradec`. U kategorie Z je po sloučení (krok 6) použita upstream verze.

### 8.1 Soubory

| soubor | kat. | proč |
|---|---|---|
| `mesto.json` | D | konfigurace města (střed, mřížka, zdroje, `doprava_here`…) |
| `assets/dominanty.json`, `custom_models.js`, `kominy.json`, `oblasti.json`, `znacky.json`, `prestavby.json`, `terminal_hd.json`, `vyluka_odjezdy.json`, `upresneni.json`, `mhd_trasy_ref.json`, `plachta_studie.json` | D | městská data (modely dominant, přestavby, terminál, výluka, ruční opravy) |
| `assets/dmp_vysky.json`, `hrebeny.json`, `potrubi.json`, `pruhy.json`, `ruian_budovy.json`, `strechy_orto.json`, `tomtom_segmenty.json`, `vlaky_koleje.json`, `zabaged.json` | D | vygenerované podklady města (v gitu přes `-f`) |
| `assets/custom_prep.py` | K | hook pasportu magistrátu (`IZO_MMHK`), jen HK |
| `assets/custom_web.js` | K | zápasy FC, LED aréna: má být doplněk `hk_zapasy` (krok 8); po merge se `{{CUSTOM_WEB}}` v upstream šabloně nenačítá |
| `priklady/vanoce.json`, `vanoce.sh` | Z | vánoce má upstream (ruční převzetí), při merge sloučeno |
| `plugins.py`, `priklady/doplnky.sample.json` | Z | naše ruční kopie systému doplňků, byly shodné s upstream (nahrazeno `git checkout origin/main`) |
| `overlay.py` | O + Z | doplňky a ulice vzaty z upstreamu; naše okluze `OKLUZE`, `ln` (pruhy), HERE `h`, semafory/přejezdy, trasy → PR po částech |
| `prep.py` (+853) | O + K | obecné: `upresneni.b` (`h` před laserem, `fl`, `cls`, `name`, `sachta`), mosty/zářezy/podjezdy, dálnice, silnice ve výstavbě, `prestavby.json`, `KOLEJE`, svislé značky `sg_*`, hřiště, pruhy, přístřešky na chodník → PR po částech. K: Plachta `IZO_PLACHTA` → `custom_prep.py`. Z: ruční převzetí (`skryt`, pole) |
| `render.html` (+340) | O | svislé značky `sg_*`, 3D koleje (lože, pražce, výhybky), modely souprav a nákladních vozů, přejezdy se závorami, hřiště → PR (větší, rozdělit); upstream přístřešky u památek zachovány |
| `render.mjs` | O | blokované porty Chromia (Windows) → PR č. 1 |
| `render_all.sh`, `render_par.sh` | O | drobnosti (Windows/časy), spojit s PR „časy fází“ |
| `render_chunk.sh` | Z | `mpp=0.2` upstream bere z `mesto.json` (merge: upstream verze) |
| `render_ctverec.sh` | O | časy fází prep/render/dzi v logu → PR |
| `postav.sh` | O + Z | HERE/TomTom `ids`, varování u mhd (naše), `pole_cesty` upstream |
| `dzi.py` | K | prázdné dlaždice vrstev `plachta*` (HK); obecně by to byl `addTileLayer` |
| `geo.py` | O | malá obecná úprava |
| `mhd.py` (+153) | O | kvalita úseků tras (`KVAL`), terminál s nástupišti, doplněk GTFS pro NAD; sloučeno s upstream `PRUJEZD` → PR (data terminálu jsou D) |
| `road_route.py` (+210) | O | jednosměrky a kruhové objezdy pro trasy MHD bez shapes.txt → PR č. 5 |
| `build_html.py` | O | `SOC_IKONY`/`odkaz_html` (FB/IG), `dalsi_zdroje`, `DOPRAVA_HERE` → PR č. 2; `CUSTOM_WEB` je K (odpadne) |
| `novy_mesto.py` | O | `--bbox/--stred` → PR č. 4 |
| `nastroje/otisk.py`, `nastroje/semafory.py`, `tests/test_sousedi.py` | Z | upstream verze je nadmnožina naší |
| `nastroje/hriste.py`, `nastroje/povrchy.py` | Z | hřiště a povrchy jsme ručně převzali z upstreamu; drobnou naši opravu `povrchy.py` ověřit, zda ji upstream má |
| `nastroje/prejezdy_z_dat.py`, `pruhy.py`, `vlaky.py`, `vlaky_koleje.py`, `vlaky_z_gtfs.py` | O | vlaky z GTFS, koleje, přejezdy z dat segmentů, pruhy z OSM → PR (větší) |
| `nastroje/vyluka_nad.py` | K | výluka Jaroměř (NAD), jen HK |
| `nastroje/here_doprava.py`, `tomtom_doprava.py`, `nahled_doprava.py`, `tests/test-doprava-sber.mjs`, `tests/test_here_doprava.py` | K | doprava HERE/TomTom: doplněk + serverový sběr; hustota aut by chtěla hook v upstreamu (nápad, ne PR) |
| `nastroje/teren_dmr.py` | O | DMR 5G (jen ČR, volitelné) → PR č. 8 |
| `web/app.html` (+1165) | K + O | po merge upstream šablona; naše UI změny jsou vypsány v 9.1 |
| `.gitignore`, `README.md`, `CLAUDE.md` | D | HK odstavce v CLAUDE.md zachovány |

### 8.2 Hlavní commity (64) po skupinách

| skupina | commity | kat. |
|---|---|---|
| Městská konfigurace a data | `04e6b83`, `2f614ae`, `ea32f1f`, `db232d2`, `6a090f5`, `762888d` (25 čtverců) | D |
| Dominanty, modely, Mileta, aréna, nádraží | `f99dd11`, `56c6a01`, `cfa1e4b`, `1c2c560`, `058040d`, `1d0490d`, `b7da0ec`, `5c041cf` | D (modely) + O (kit v `render.html`) |
| Mosty, podjezdy, estakáda, dálnice | `16710e5`, `0479eeb`, `8bb5ca3`, `3233ae3`, `5718a43`, `86bb655`, `a3ab124` | O |
| Vlaky, koleje, přejezdy | `8fcba39`, `a7d37fe`, `e8f03e7`, `1afd115`, `07cf950`, `28752fa`, `0652a24`, `fb7e36e`, `5b131e3`, `7614561` | O |
| Výluka Jaroměř | `f6433dd` | K |
| MHD trasy a zastávky | `0d30df7`, `b2f0747`, `c9d61e1`, `e0027f3`, `c102504` | O (data tras D) |
| Doprava HERE/TomTom | `5e302c9`, `b2815a3`, `184ff90`, `0e0896b` | K (doplněk + `/api/doprava`) |
| Odjezdová tabule vlaků | `6600ac5`, `e1cd1b2`, `0f46246` | K (doplněk) |
| Hlášení, FB/IG, opravy z issues | `74235b1`, `17cd9b5`, `1bf7afe`, `eab1675` | K (doplněk `hlaseni`) + O (FB/IG) |
| Ruční převzetí upstreamu | `0397262`, `0f150a2`, `953f1db`, `8e4c62a`, `02c35a7`, `aba66d9`, `72e9898`, `5a99db2`, `52fbc23` | Z |
| Revertované chodci/cyklisti | `46fe803`, `cc05bb7`, `452f34d` + 3× `Revert` (`230a7dd`, `60a8928`, `51b97ba`) | Z (`"chodci": false` do rozhodnutí) |
| Technické | `9c24980` časy fází | O |

## 9. Krok 6: merge ve worktree (2026-11-23)

Worktree `C:\Users\pavel\Desktop\izohradec\izomapa_sync`, větev `sync/upstream-2026-11` (z `hradec` = `eab1675`), merge commit `9d9b612` (`origin/main` = `508b2a9`). Větev `hradec` nepřesunuta, nic nepushnuto.

Konflikty (15 souborů): `prep.py`, `overlay.py`, `build_html.py`, `mhd.py`, `novy_mesto.py`, `dzi.py`, `render.html`, `render_chunk.sh`, `render_ctverec.sh`, `postav.sh`, `nastroje/otisk.py`, `nastroje/semafory.py`, `README.md`, `CLAUDE.md`, `web/app.html`. Nové proti sekci 2: `dzi.py` (ponechány obě předpony `xmas` + `plachta`) a `README.md` (upstream).

Testy: `pytest tests -q` 29 passed, 1 skipped; `node tests/test-*.mjs` všech 5 OK; `py_compile` všech `.py` OK; `prep.py data 0,0` ve worktree prošel (kopie `data/` a podkladů z `izomapa/`, bez `mmhk`). `doplnky/najdi_to` test PHP backendu selhal (prostředí, ne merge).

Otevřené po merge:
- `web/app.html` je čistá upstream šablona: **chybí** vše z 9.1; `{{CUSTOM_WEB}}` šablona nezná (`assets/custom_web.js` se nenačte, dokud ho nepřenese krok 7/8). Do té doby nespouštět `build_html.py` pro nasazení.
- `"chodci": false` v `mesto.json` (upstream výchozí zapnuto), rozhodnutí po náhledu.
- `skryt` -> `skryt_budovy` hotovo (3 budovy v `assets/upresneni.json`); `skripty/opravy_hlaseni.py` v kořenovém repu upraven (`nastav(..., skryt=True)` zapisuje do `skryt_budovy`), v kořeni nekomitováno.
- `pole_cesty.py` v `postav.sh` mění pole: při příštím plném `postav.sh` vznikne nová `zabaged.json`, posoudit na náhledu.
- `overlay.py`, `mhd.py`, `build_html.py` po merge nespuštěny (potřebují všechny čtverce a `site/`), jen `py_compile`. Nutný je i celý render (změna `render.html`, otisk).

### 9.1 Naše změny v `web/app.html` (`git diff d37658b hradec -- web/app.html`), které musí přenést krok 7
(Část byla ruční port upstreamu: ověřit proti `web/js/*` a přenést jen to, co upstream nemá.)
- **Doplňky (ruční port)**: `#pluginLayers`, `#pluginTabsSlot`, `runFrameLayer`, `window.IZOMAPA_PLUGINS`, `{{CUSTOM_WEB}}` -> nahradit upstream `web/js/45-doplnky-klik.js`, `90-doplnky-api.js`; HK kód přes `registerPlugin`.
- **Formulář hlášení**: `repWeb` (honeypot), `repFoto`/`repFotoBtn`/`repFotoNazev`, po odeslání `repAfter` (`repAfterFoto`, `repFoto2`, `repEmail`, `repAfterOk/No`), `zmensiFotku()`, `doplnit()`, POST `api/report`, `showCard({..., link, linkText, target, dep})`, `#cardExtra`, `issueUrl()`. Server `skripty/vercel_api/report.js`.
- **Doprava HERE/TomTom**: `l-jam-row`/`l-jam`/`jam-mode` (vrstva Zácpy), `praha()`, `hereVal/hereRoadVal/hereRoad/hereG/hereSp`, `JAM_COL`, `drawJam`, `nactiTyp` (`api/doprava`, `api/doprava_typicka`), `carActive` (`hereG`), `carSpeed` (`hereSp`).
- **Přejezdy a závory**: `blocked`, `xTyp`, `trackDir`, `xGeo`, `xStop`, `setClosed`, `xP`, `xFrame`, `xLine/xQuad/xLamp`, `xWarn`, `drawXPost/drawXArm/drawXDev` (výstražník, animované závory, fronta aut).
- **Semafory**: `addSignals`, `updateSignals`, `drawSigPost` (upstream má vlastní, porovnat).
- **Pruhy**: `laneOff`, `stepCarMove` (auta vedle sebe; upstream `ln` v overlay, ověřit duplicitu).
- **MHD**: `mhdFollow`, lišta `#follow`/`#followTxt`/`#routeFit`, `routeGeom`, `drawRoute`, `routeOff`, `MHD.kvalita` (nejisté úseky), přepínač Zastávky MHD (`l-stops`), `terminalPos` (autobusy na terminálu), `stopDepartures`.
- **Odjezdová tabule vlaků**: `#board`, `bdClock/bdRows/bdClose`, `bdSkrat/bdStr/bdIds/bdData/bdBuild/bdSync/bdStep/bdFlip/bdApply/bdTick/bdOpen/bdClose/bdWatch`, `showStation`, klik na budovu nádraží.
- **Vlaky**: `wagons`, `trainOf`, stání vlaků a přesah za konec trasy (`at`), modely souprav (`TRAINS`), nákladní vlaky.
- **Vánoce**: `l-xmas`, `inXmasDates`, `xmasOn/xmasShow`, `applyExtras`, `xmasTrees`, `rinks`, stánky, `lightOp` (část = port upstreamu).
- **Plachta (studie)**: přepínač `l-plachta`, vrstvy dlaždic `plachta_summer/_lights/…`, popisek studie.
- **Ostatní**: čtvercová tlačítka Facebook/Instagram v menu (ikony v `build_html.py`), `drawBehindTrees`, `DISTRICTS` (popisky obcí; upstream má), úpravy karty budovy.

## Stav: Plachta → custom_prep (2026-11-23, worktree `izomapa_sync`)

**Co a kde.** Veškerý kód Plachty (`IZO_PLACHTA=1`) je z `prep.py` v `izomapa_sync/assets/custom_prep.py` (sekce na konci souboru, běží jen s `IZO_PLACHTA=1` a existujícím `assets/plachta_studie.json`). Do `prep.py` přibyl **obecný hook bod**: 4 jednořádková volání `_hook('<fáze>')` (stejný mechanismus jako upstream `terrain/cliffs/cemetery/props`, bez `custom_prep.py` nic nedělají): `init` (po načtení `UP`/`OBL`, před jejich použitím; Plachta tu přidá `custom_bld`, `plochy`, `hriste`, oblast stromů a přesměruje `OUT` na `build/c<i>_<j>_plachta`), `roads` (po sestavení seznamu `roads`, před mosty), `props_extra` (před přesunem přístřešků, `props`/`cars` ještě v lokálních souřadnicích), `lamps` (po filtru pasportu, před světelnou mapou). Řádek s `OUT` je zpět v upstream podobě. Patch `prep.py` pro Plachtu: +5/−27 řádků. Návrh pro upstream PR: hooky `init/roads/props_extra/lamps` jako obecné rozšíření (jsou bezpečné, 4 řádky).
Skripty v kořeni (`skripty/plachta.sh`, `plachta_studie.py`, `plachta_okoli.py`) beze změny (volají `IZO_PLACHTA=1 python prep.py data_c1_-1 1,-1`, výstup stále `build/c1_-1_plachta`).

**Porovnání (čtverec 1,-1, `data_c1_-1` + `mmhk.json`, před/po):** `scene.json`, `lightmap.png`, `ground_{summer,autumn,winter,spring}.png` jsou **bajt po bajtu shodné** (cmp) před a po přesunu; `info_src.json` shodný také. Bez `IZO_PLACHTA` je výstup po změně shodný s výstupem před změnou (scene, lightmap, ground; `info_src.json` se lišil jen kódováním diakritiky, protože ten běh byl spuštěn bez `PYTHONUTF8=1`). Varianta Plachta se od běžné scény liší (scene.json 9,85 vs 9,64 MB), takže test skutečně Plachtu zahrnoval. Neověřeno: render dlaždic a web (nespuštěno; scéna je shodná, tak by měly být shodné i dlaždice).

**Zbylé HK/obecné zásahy v `prep.py` (nezměněno, `git diff origin/main -- prep.py`, ~740 řádků, 54 hunků):** žádný další zásah není čistě HK; téměř vše je obecné vylepšení → PR po částech, ne do hooku:
- podjezdy/tunely: `_tunnel_zones/_tunnel_passes`, zářez terénu pod tratí a pod mosty (PR; hook `terrain` už upstreamu nic z toho nepotřebuje);
- hradby a opěrné zdi jako útesy (`CLIFFS`, `lines_out['cliff']`) – obecné, ale v HK je plní i hook `cliffs` pasportu (PR spolu s `render.html`);
- uzly sítě `connectors`/`is_node`, dálnice bez křížení (`IZO_DALNICE_KRIZENI`; dá se vypnout env, k PR), trať nad podjezdem;
- mosty: společné výpočty mostovek (`_PP`, `_abut`, `_niveleta`), sloučené chodníky, `skryt_mosty`, `_back`, `AB_R/_junction` (největší blok, PR jako samostatný);
- `KOLEJE` (3D koleje, výhybky, zrušená trať) – PR spolu s `render.html`;
- `on_bridge`, `_WIN`, přístřešky zastávek z vozovky na chodník, `excl/_mx13`, `portals`, `teren_prevyseni` (volitelné v `mesto.json`) – drobné, PR;
- úpravy výšek/atributů budov (`upresneni.b` `h` před laserem, `fl`, `cls`, `name`, `sachta`, `custom_bld` zálohy) – PR;
- jediná věc z velké části HK-specifická: `UP['skryt_mosty']`/`prestavby.json` data (jsou už v `assets/`, kód je obecný). Do hooku nic dalšího nepřesouvat.

## Stav kroku 7 (web) (2026-11-23, worktree `izomapa_sync`, větev `sync/upstream-2026-11`)

Upstream šablona `web/app.html` + `web/css/*` + `web/js/*` zůstává základem; naše obecné funkce jsou přeneseny malými zásahy do upstream souborů, HK věci čekají na doplňky (krok 8) a dostaly k tomu extension pointy. Nic nepushnuto, `hradec` nepřesunut.

**Commity (každý samostatné téma, kandidát na PR):**

| commit | co | soubory |
|---|---|---|
| `3f71c9e` | odkazy města (FB/IG ikony, `{{ODKAZY}}`), v patičce `{{DOPRAVA_HERE_ZDROJ}}` a `{{DALSI_ZDROJE}}` | `app.html`, `css/00` |
| `2311348` | přejezdy podle ČR: výstražník ve světě natočený k řidičům, PZS se světly, animované půlzávory (`xTyp/trackDir/xGeo/xStop/xP/xFrame/drawXPost/drawXArm/drawXDev`), auta stojí před závorou; **navázáno na upstream skupiny přejezdů `z.g`** (stav závor a druh zabezpečení jsou na skupině). Pruhy `r.ln` (`laneOff`, `stepCar` → `stepCarMove`) | `js/70`, `js/89` |
| `004ef78` | modely vlaků z mhd.json (`MHD.tm`, `routes[4]`), nové řady + nákladní vlaky (`wagons`, `fr`), vlak stojí celý u nástupiště (přesah za konec trasy v `shapePos`), trolejbus (`route_type 11`, sběrače, barva, `MHD_DRUH`), barvy dopravce `{{MHD_BARVY}}` | `js/70`, `js/80`, `js/89` |
| `6f12aee` | trasa sledovaného spoje (`routeGeom/drawRoute/routeOff`, tlačítko `#routeFit` „Celá trasa“, `MHD.kvalita` čárkovaně), vrstva „Zastávky MHD“ (`#l-stops-row`, `state.selStop`), karta odjezdů `showCard({dep})` s poli časů | `app.html`, `css/10`, `css/40`, `js/40`, `js/70`, `js/89` |
| `39836ab` | extension pointy (níže); `build_html.py`: zrušeno `{{CUSTOM_WEB}}` + kopie `custom_web.js` (šablona ho nezná, nahradí doplněk) | `app.html` (`#cardExtra`), `js/10`, `js/40`, `js/70`, `js/89`, `js/90`, `build_html.py` |
| `1c50280` | `Izomapa.depth`, `Izomapa.isOccluded` (potřebuje doplněk zápasů) | `js/90` |
| `89a4035` | popis nového API v `priklady/doplnek_vzor/README.md` | README |

Rozsah: `web/js` + `web/css` **+379 / −64 řádků** (cíl ~300 překročen: přejezdy+pruhy ~150, vlaky/trolejbusy ~75, trasa/zastávky ~100, API ~55); `app.html` +8, `build_html.py` −4.

**Extension pointy (`window.Izomapa`, vše v `web/js/90-doplnky-api.js`; bez doplňku se nic nemění):**
- `getUiSlot('karta')` → `#cardExtra` v kartě pod údaji (vyprázdní se při každém otevření karty); `getUiSlot('vrstvy')` → `.layers` (přepínače v menu, doplněk si přidá `<label><input type=checkbox>…`). `'sidebar-tabs'` beze změny.
- `onCard(fn)` → odhlašovací funkce; `fn({ title, text, lon, lat, k, building, el })` po každém `showCard` (budova, místo, zastávka, sousední mapa); `building` = `state.sel` (záznam budovy nebo `null`).
- `onBuildingClick(fn, { priority })` → odhlášení; `fn(b)` při kliku na budovu i výběru budovy z hledání, `b` = záznam budovy (`id, oid, name, cls, addr, lon, lat, hull, k, …`); `return true` = karta se neotevře (odjezdová tabule nádraží).
- `getReportTarget()` → `{ target: 'b:<oid>' | 'pt:lat,lon', title, lon, lat }` otevřené karty (pro vlastní formulář hlášení).
- `addTileLayer(id, { variant(season, l), light })` → `{ refresh(), remove() }`: přídavná varianta dlaždic z `tiles.json` nad každým čtvercem (stejně jako vánoční výzdoba, `applyExtras`); `variant` vrací název varianty (např. `'plachta_' + season`) nebo `null` = vypnuto; `light: true` = noční světla (`compositeOperation: 'lighter'`, průhlednost podle noci). `hasTileVariant(name)` = je varianta v `tiles.json`.
- `setTrafficHook({ share(r, dir), speed(r, dir) })` / `setTrafficHook(null)`: násobek podílu jedoucích aut (0–1, aut nepřibude) a rychlosti na kusu silnice; volá se pro každé auto v každém snímku (kešovat!). `getRoads()` = kusy silnic načtených čtverců (`w` svět, `p` obrázek, `c` třída, `o` jednosměrka, `ln`, `k`, `L`, `h` čísla úseků HERE z overlay). Pozn.: dřívější „zdvojená zásoba aut na silnicích s HERE daty“ už není – maximum je hustota bez doplňku (J ≥ 6 = všechna auta, J 0 ≈ 35 %).
- `getMhd()` → objekt MHD (`routes, trips, names, stops, shapes, kvalita, terminal`) nebo `null`; `departures(stops, { trains = false, horizon = 3600 })` → `[[s do odjezdu, trip], …]`, `stops` = index zastávky nebo `Set` indexů (tabule: `Set` kolejí hlavního nádraží, `trains: true`, `horizon: 12*3600`).
- `onFrame(fn, { layer: 'ground' })` – nová vrstva na zemi pod vozidly (čáry zácp); dál `world/sky/top`.
- `depth(x, y, h)`, `isOccluded(x, y, h)`.
- Zavření karty z doplňku: `document.getElementById('cardClose').click()`.

**Pro doplňky v kroku 8 (vědomě NEpřeneseno do `web/js`, HK):**
- **Formulář hlášení s fotkou a e-mailem** (`doplnky/hlaseni`): upstream šablona má jen textový formulář (`#report` > `#reportForm` s `#repNote`, `#repMsg`, POST `api/report` `{target, title, lon, lat, note}`). Doplněk do `#reportForm` přidá (stejná ID jako dřív v `hradec:web/app.html`) `#repWeb` (honeypot, posílá se jako `hp`), `#repFoto`/`#repFotoBtn`/`#repFotoNazev`, po odeslání panel `#repAfter` (`#repAfterH`, `#repAfterFoto`, `#repFoto2`, `#repEmail`, `#repAfterOk`, `#repAfterNo`) a `zmensiFotku()` (delší strana ≤ 1600 px, JPEG, data URL < ~3,8 MB). Odeslání převezme (listener ve fázi capture + `stopImmediatePropagation`), cíl bere z `Izomapa.getReportTarget()`, při otevření karty resetuje přes `onCard`.
  **Rozhraní `/api/report` (`skripty/vercel_api/report.js`) zachovat beze změny:** hlášení `POST {target, title, lon, lat, note, hp, url, foto}` → `{ok, cislo, soukrome, podpis, foto, msg}`; doplnění `POST {doplnit: cislo, podpis, foto, email}` → `{ok, foto, email, msg}`. Panel „Chcete přidat fotku / e-mail“ jen když `d.soukrome && d.cislo`. Tlačítko GitHub issue (`issueUrl`, `frenkees/hradeczive`) jen bez `hlaseni` v mesto.json – v HK nepoužito, nepřeneseno.
- **Odjezdová tabule vlaků** (`doplnky/odjezdova_tabule`): CSS `.board/.fl/.bd-*` a `#board` vytvoří doplněk sám; data `Izomapa.getMhd()` + `departures(..., {trains: true})`; otevření `onBuildingClick` (název budovy `^Hradec Králové,? hlavní nádraží` / „Hlavní nádraží“) a přiblížení k `50.214528, 15.810767` (`onFrame` – `view.sx`, `latLonToImg`).
- **Zápasy FC + LED aréna** (`doplnky/hk_zapasy`, dnes `assets/custom_web.js`): `draw(d)` → `onFrame(..., {layer: 'world'})` (`view` má stejné `sx, ox, oy, night, vis, dt`), `card({title, el})` → `onCard`, `api.local` → `latLonToWorld`, `api.depth` → `depth`, `api.state.weather` → `getEnvironment().weather`. `custom_web.js` se po `39836ab` už nenačítá.
- **Doprava HERE/TomTom** (`doplnky/doprava_here`): přepínač Zácpy (`getUiSlot('vrstvy')`), čáry `onFrame(..., {layer: 'ground'})` přes `getRoads()` (`r.h`), hustota/rychlost `setTrafficHook`; data `doprava_id.json`, `api/doprava`, `api/doprava_typicka` (kód v `hradec:web/app.html`, `HERE`, `hereVal…drawJam`). `{{DOPRAVA_HERE}}` šablona už nepoužívá (build_html.py ho dál plní, neškodí).
- **Plachta – klient** (`doplnky/plachta`): přepínač do `getUiSlot('vrstvy')` (jen když `hasTileVariant('plachta_summer')`), `addTileLayer('plachta', {variant: s => on ? 'plachta_' + s : null})` + `addTileLayer('plachtal', {variant: () => on ? 'plachta_lights' : null, light: true})`, `refresh()` po přepnutí.

**Vědomě nepřeneseno (obecné, ale mimo rozpočet / upstream řeší jinak):**
- `terminalPos` (autobusy na terminálu s odstavnými místy, `MHD.terminal`, `noBld`): upstream má vlastní řešení front na konečné (`BUS_CEKA`, jedno vozidlo na stanovišti, fronta po `prijezdSh`); mhd.py dál zapisuje `terminal`, web ho nepoužívá. Kandidát na samostatný malý PR, pokud bude na náhledu terminálu chybět.
- Průhledná silueta vozidla za budovou (`drawBehindTrees` `[4, hull, gh]`, `GHOST_*`) – kosmetické, samostatný PR později.
- Vánoce, semafory, popisky obcí (`DISTRICTS` `k === 'obec'`), `neighborHref` – upstream už má (shodné nebo nadmnožina).
- `window.__izo`/`__izoX` ladicí rozšíření.

**Ověřeno:** `web/sestav.py` sestaví; `node --check` sestaveného skriptu OK; `node tests/test-*.mjs` 5/5 OK; `pytest tests` zelené. Headless Chromium (Playwright z `izomapa/node_modules`) nad kopií `izomapa/site` (dlaždice přes junction, `index.html` z `build_html.py` worktree, `api/*` → 404): **žádná chyba ani varování v konzoli**; API všech nových funkcí existuje, sloty `karta`/`vrstvy` vrací prvky, `onCard` se volá a vloží obsah do karty, `onBuildingClick` potlačí kartu, `getReportTarget` vrací cíl, `departures` vrací autobusy (24) i vlaky z hl. nádraží (21), `addTileLayer` s `plachta_*` i světly bez chyby, `setTrafficHook` bez chyby; FB/IG ikony a nové zdroje v patičce jsou vidět; „Zastávky MHD“ se objeví; klik na autobus → lišta „Autobus 11 → …“, „Celá trasa“ oddálí na trasu a ta se nakreslí; přejezd (13 v mapě) se kreslí bez chyby.
**Neověřeno:** spuštěná závora/výstraha při projíždějícím vlaku (záleží na čase, v testu nejel vlak), vzhled nákladních vlaků a trolejbusů, karta odjezdů na mobilu, pruhy na vícepruhových silnicích – jen kód, bez vizuální kontroly; `overlay.py`/`mhd.py` worktree nespuštěny (test běžel nad starším `site/` z `izomapa/`).

**Jak ověřit v prohlížeči:** ve worktree vytvořit `site/` (po `overlay.py` + `mhd.py`, nebo kopie/junction `izomapa/site` bez `index.html`), `python build_html.py`, `npm run nahled` (nebo libovolný statický server na `localhost`, kvůli `window.__izo`). Zkontrolovat: konzole bez chyb; panel – FB/IG, „Zastávky MHD“; patička nápovědy – HERE/TomTom a pasporty města; klik na autobus/trolejbus/vlak – lišta, trasa, „Celá trasa“; zastávka – karta s odjezdy po řádcích; přejezd u hl. nádraží při průjezdu vlaku (`#leto@50.2145,15.8107,0.3`) – blikání, sklopení závor, fronta aut; `window.Izomapa.getUiSlot('karta')`.

**Otevřené:** doplňky z kroku 8 (hlášení, tabule, zápasy, doprava, Plachta – klient); rozhodnout terminál a siluety; testy nových API do `tests/test-plugins.mjs` (pro PR); u PR do upstreamu rozdělit commit `39836ab` podle funkcí (karta / vrstvy dlaždic / doprava / MHD).

## Stav: doplněk hlaseni (2026-11-23, worktree `izomapa_sync`, větev `sync/upstream-2026-11`)

Krok 8, formulář hlášení s fotkou a e-mailem jako doplněk `doplnky/hlaseni/` (nic nepushnuto, bez renderu a nasazení).

- **Soubory:** `doplnky/hlaseni/{manifest.json, hlaseni.js, hlaseni.css, overlay_hook.py}`, `assets/doplnky/hlaseni.json` (`{"enabled": true, "api": "api/report"}`; `assets/doplnky/` je v `.gitignore`, soubor se do gitu přidává `git add -f`), testy `doplnky/hlaseni/tests/{test_hlaseni.py, test-hlaseni.mjs}`.
- **Napojení:** jen `window.Izomapa` (`registerPlugin`, `getPluginConfig`, `getReportTarget`, `onCard`). Do `#reportForm` vloží `#repWeb` (honeypot → `hp`), `#repFoto`/`#repFotoBtn`/`#repFotoNazev`, za formulář `#repAfter` (`#repAfterH`, `#repAfterFoto`, `#repFoto2`, `#repEmail`, `#repAfterOk`, `#repAfterNo`). Odeslání zachytí listenerem ve fázi capture na `#report` a `stopImmediatePropagation` (upstream textový handler neběží), cíl bere z `getReportTarget()`, reset formuláře přes `onCard`. Konfigurace: `api` (výchozí `api/report`), `max_strana` (1600). Hook vrací `{}`, bez `assets/doplnky/hlaseni.json` nebo s `enabled:false` se doplněk nezavede. Rozhraní `/api/report` beze změny (hlášení `{target,title,lon,lat,note,hp,url,foto}`, doplnění `{doplnit,podpis,foto,email}`).
- **Chování jako v `hradec`:** min. 3 znaky, zmenšení fotky na delší stranu 1600 px JPEG (data URL < ~3,8 MB), po odeslání panel fotky a e-mailu jen při `soukrome && cislo` (fotka se nenabízí, když už byla přiložena), „Ne, děkuji“, zprávy shodné s dřívějšími.
- **Ověřeno:** `node doplnky/hlaseni/tests/test-hlaseni.mjs` OK; `python -m unittest doplnky.hlaseni.tests.test_hlaseni` OK (4 testy, včetně `plugins.load_and_run_plugins`); `web/sestav.py` a `tests/test-plugins.mjs` OK. Headless Chromium (Playwright) nad kopií sestavené stránky s reálným výstupem `load_and_run_plugins` v `overlay.json` a **mockem** `/api/report` (route interception; nic se neposílalo ven): formulář v kartě, krátká poznámka bez požadavku, hlášení s honeypotem a fotkou 3000x2000 → JPEG 1600x1067, panel doplnění, doplnění e-mailu i fotky, reset při nové kartě, „Ne, děkuji“, režim bez `soukrome` (bez panelu); konzole bez chyb a varování.
- **Neověřeno:** reálný server `report.js` (zámerně), cíl `b:<oid>` při kliku na konkrétní budovu (test jen na „Vybrané místo“ `pt:`), mobilní vzhled, fotka z telefonu (EXIF/HEIC), `build_html.py` na úplném `site/` (test nad starším `site/` z kroku 7). Browser skript je jen v scratchpadu, v repu není.

## Stav: doplněk doprava_here (2026-11-23, worktree `izomapa_sync`, větev `sync/upstream-2026-11`)

**Co a kde.** `doplnky/doprava_here/` (`manifest.json`, `overlay_hook.py`, `doprava_here.js`, `tests/`, `priklady/doprava_here.sample.json`); zapíná ho `assets/doplnky/doprava_here.json` (v `.gitignore` jako ostatní městská data doplňků, ukázka je v `priklady/`; klíče `enabled`, `api`, `api_typicka`, `zive_s`, `min_podil`, `j_plny`).
- **Build (`overlay_hook.py`, jen `overlay.py`)**: po zápisu `site/overlay/*.json` projde čtverce, silnicím přidá `h` (`nastroje/here_doprava.py prirad`, HERE + TomTom, beze změny), vyrobí `site/doplnky/doprava_here/doprava_id.json` (klíč úseku -> číslo; nahrazuje ruční `here_doprava.py ids` + `tomtom_doprava.py ids` a `site/doprava_id.json`) a vrátí konfiguraci klienta (včetně `ids_v` pro cache). **Z `overlay.py` je odstraněn blok `if MESTO.get('doprava_here')`** (−7 řádků, patch generátoru je menší; v `overlay.py` zbývá jen komentář). Hook je idempotentní (starou `h` před přiřazením maže).
- **Klient (`doprava_here.js`)**: přepínač „Zácpy“ + výběr režimu ve `getUiSlot('vrstvy')` hned za „Doprava“, čáry vytížení `onFrame(..., {layer: 'ground'})` přes `getRoads()` (`r.h`), `setTrafficHook({share, speed})`, živá data `api/doprava` (každých `zive_s` s), typický průběh `api/doprava_typicka` (režimy se zablokují, dokud nejsou data). Jen `window.Izomapa`, na silnice si zapisuje `_dhv/_dhg/_dhs` (cache). `{{DOPRAVA_HERE}}` a `HERE.on` odpadly; `build_html.py` plní jen `{{DOPRAVA_HERE_ZDROJ}}` (patička, dál z `mesto.json` `doprava_here`; `{{DOPRAVA_HERE}}` šablona nezná, neškodí).
- **Rozdíl proti původní verzi (`hradec:web/app.html`)**: tam měly silnice s `h` **dvojnásobnou váhu při rozmisťování aut** (`weights × 2`) a podíl aktivních aut `hg` byl 0,35 + 0,65·min(1, J/6), bez dat 0,5. Tedy J ≥ 6 = všechna auta z dvojnásobné zásoby (2× hustota než bez HERE), J ≈ 3 = původní hustota, bez dat = původní hustota. Extension point `setTrafficHook` jen **násobí podíl ≤ 1**, zásobu aut nezvýší: nyní J ≥ 6 = původní hustota bez doplňku (max.), J 3 ≈ 67 %, J 0 = 35 %, bez dat nebo bez úseku = beze změny. Zácpy hustotu aut tedy jen snižují místo toho, aby ji proti klidu zvyšovaly (v zácpě je vizuálně míň aut než dřív, kolony se v mapě nevyplní). **Doplněk to nedokáže vyřešit** (zásoba se rozmisťuje v `70-animace.js` při načtení čtverců). Navrhované řešení (patch generátoru, ~3 řádky, obecně užitečné i pro upstream): rozšířit hook o `weight(r)` (násobek váhy silnice při rozmisťování, `weights = main.map(i => (roads[i].v||0) * roads[i].L * (trafficHook?.weight?.(roads[i]) ?? 1))`), jenže hook se nastavuje až po `onInit` (po načtení čtverců), takže by se musel nastavit dřív (např. `Izomapa.setTrafficHook` volaný synchronně před `layersReady`, nebo přepočet zásoby po nastavení hooku). Doplněk pak vrátí `weight = r.h ? 2 : 1` a `share` zůstane 0,5 + … (původní vzorec, bez dat 0,5). Dokud tohle není, je maximum hustoty stejné jako bez doplňku (rozhodnutí zadavatele).
- **Testy**: `doplnky/doprava_here/tests/test_hook.py` (syntetické registry: přiřazení `h`, směr HERE/TomTom, ids, idempotence, zavaděč `plugins`), `test-klient.mjs` (share/speed podle J, směry, bez dat = 1, nikdy > 1, UI, start/stop, kreslení). Beze změny zůstal `tests/test_here_doprava.py` (jádro `nastroje/here_doprava.py`: klíč, snímek). Spouštět: `python -m pytest tests doplnky/doprava_here/tests` (pytest je v systémovém Pythonu, ne v `.venv`), `node doplnky/doprava_here/tests/test-klient.mjs`.
- **Ověřeno**: 34 pytest + 24 podtestů zelených, `node tests/test-*.mjs` (5) a `test-klient.mjs` OK; hook nad skutečnými daty (`overlay/*.json` z `izomapa/site`, registry HERE 568 + TomTom 1131): 2 582 silnic s úseky; headless Chromium (Playwright) nad sestavenou stránkou s mockem `api/doprava` a `api/doprava_typicka`: bez chyb a varování v konzoli, přepínač Zácpy za „Doprava“ s 6 režimy, barevné čáry živě i pro 8 h, `getRoads()` 1 634 silnic s `h` z 5 001, `share` nabývá různých hodnot (1; 0,89; 0,78; 0,51 …) a `speed` 0,5–1, data se stahují po jednom (ids 1×, doprava 1×, typicka 1×).
- **Neověřeno**: skutečné API (`/api/doprava` na Vercelu, klíče HERE/TomTom se nepoužily), `overlay.py` celý neběžel (hook spuštěn přes `plugins.load_and_run_plugins` nad kopií `site/` s existujícím overlayem), vizuální dojem hustoty aut v čase (jen hodnoty), mobil, `api/doprava_typicka` v produkci (sběr snímků), nasazení `site/doplnky/` na R2/Vercel (`pripravit_vercel.mjs` musí kopírovat `site/doplnky/doprava_here/doprava_id.json`; zkontrolovat), odstranění `site/doprava_id.json` z nasazení.


## Stav: doplňky hk_zapasy a odjezdova_tabule (krok 8, 2026-11-23, worktree `izomapa_sync`)

Obě HK funkce z `hradec:assets/custom_web.js` a `hradec:web/app.html` přepsány na doplňky přes veřejné `window.Izomapa`; `web/js/*`, `prep.py` a jiné doplňky nedotčeny. Server `skripty/vercel_api/zapasy.js` beze změny (rozhraní `/api/zapasy` stejné, záloha `zapasy.json`).

- **`doplnky/hk_zapasy/`** (`manifest.json`, `overlay_hook.py`, `hk_zapasy.js`, `tests/`): lízátka, LED fasáda v noci, obrazovka se skóre/dalším zápasem, popisek nad arénou (`onFrame` vrstva `'world'`), karta „Malšovická aréna“ s rozpisem (`onCard`, výraz `karta_re`). Převody: `api.local` -> `latLonToWorld`, `api.state.weather` -> `getEnvironment().weather`, `depth` -> `Izomapa.depth`. Data v `assets/doplnky/hk_zapasy.json`: `arena` (lat, lon, azimut 110,4, stožáry, obvod, zeď budovy), `zdroje` (`api/zapasy`, `zapasy.json`), `odkaz`, `zkratky` klubů. Geometrie obrazovky (stínítko) je v JS napevno (rozměry modelu `malsovicka_arena`).
- **`doplnky/odjezdova_tabule/`** (`manifest.json`, `overlay_hook.py`, `.js`, `.css`, `tests/`): tabule s klapkami (stejné CSS a animace jako dřív), DOM si doplněk vytvoří sám (`#board`, `#bdRows`, `#bdClock`, `#bdClose`). Data `getMhd()` + `departures(Set kolejí, {trains: true, horizon})`, čas Prahy přes `Intl`. Otevření: `onBuildingClick` (budova `^Hradec Králové,? hlavní nádraží` nebo „Hlavní nádraží“, vrací `true` = karta se nesestaví; bez načtených jízdních řádů vrací `false`) a přiblížení (`onFrame` vrstva `'top'`, kontrola po ~400 ms přes `view.sx` a `getView()`, práh sx >= 0,3 a do 520 px od `latLonToImg(stanice)`). Data v `assets/doplnky/odjezdova_tabule.json` (`stanice`, `titulek`, `radku`, `sirky`, `horizont_h`, `zkratky`).
- **Aktivace:** `assets/doplnky/<id>.json` existují a `assets/doplnky.json` neexistuje = `plugins.py` je zapne sám. Po nasazení stačí `overlay.py` + `build_html.py`, render není potřeba.
- **Testy:** `node tests/test-hk-doplnky.mjs` (mock `Izomapa`, vm), `python -m unittest discover -s doplnky/hk_zapasy/tests -t .` a totéž pro `odjezdova_tabule` (hook, kopie assetů, klient obsahuje jen veřejné API); stávající `node tests/test-*.mjs` zůstaly zelené.
- **Ověřeno:** `web/sestav.py`/`build_html.py` sestaví; `node --check` obou skriptů; headless Chromium (Playwright z `izomapa/node_modules`) nad kopií `izomapa/site` v `izomapa_sync/site` (dlaždice přes junction, `overlay.json` doplněn výstupem `plugins.load_and_run_plugins`, `/api/zapasy` mockováno živým domácím zápasem): bez chyb v konzoli (jediná 404 je `preview/summer.json`, který jsem do kopie nekopíroval), arény: popisek „ŽIVĚ HKR 1:0 LIB - 1. poločas“ a lízátka vidět, karta „Malšovická aréna“ ukazuje „Právě se hraje“, rozpis a poslední výsledky; tabule se po přiblížení k nádraží otevře (7 řádků, 22 odjezdů v 12 h, klapky se doplní), tlačítko × ji zavře, klik na budovu nádraží ji otevře a kartu nesestaví.
- **Neověřeno:** skóre/obrazovka na LED stínítku zblízka a LED pás v noci (screenshot ve dne při `setEnvironment({night:true})` nepotvrzen vizuálně, nastaveno jen přes API), reálné API `/api/zapasy` a fchk.cz/onlajny.com (mock), mobilní vzhled tabule, pořadí vykreslení vůči doplňku `doprava_here`, `overlay.py` celý (jen hook), produkční nasazení. Kontrola rozdílu proti původnímu chování je z kódu a z jednoho běhu, ne porovnání obrazů.

## Stav: doplněk letiste

- Hotovo: `assets/doplnky/letiste.json` (v .gitignore, přidáno `git add -f`) na větvi sync/upstream-2026-11 v `izomapa_sync`. Doplněk se zapne sám (existuje data_file, `assets/doplnky.json` není).
- Dráhy z OSM/Overture (`data_all/infrastructure.parquet`), konce zkontrolovány proti ortofotu ČÚZK: 15L/33R beton 2400x60 m, 15R/33L tráva 800x25 m (prahové značky „L“ na ortofotu sedí s koncem b). Odstavná plocha = OSM „Apron GA“ (před hangáry aeroklubu, jih letiště).
- Aktivní okruh: dráha 15R/33L, vzlet od konce b (33L), levý okruh – podle VFR manuálu AIP ČR (15R pravý, 33L levý; ověřeno jen z výsledku webového vyhledávání, ne z plného textu). Odhad: volba 33L místo 15R.
- Odhad z ortofota: 4 stání (letadla před hangáry), počty a typy letadel, `vyska_okruhu` 110. Vynecháno: `dz` (existenci seskokové zóny jsem neověřil, An-2 se proto neobjeví), `pojizdeni` (OSM taxiwaye existují, hook ho stejně nepředává), hangáry (v Overture je jen jedna malá budova class hangar mimo hangáry aeroklubu, dominanty žádné).
- Letiště leží u severního okraje mapy (max lat ≈ 50.2574): severní konec dráh je mimo mapu.
- Dráhy a odstavná plocha se promítnou do dlaždic až po renderu čtverců (nespuštěno). Provoz letadel stačí overlay.
- Ověřeno: `plugins.load_and_run_plugins` nad kopií s letiste.json vrací data i kopíruje letiste.js, `tests.test_plugins_core` OK, `node tests/test-plugins.mjs` OK, `node --check letiste.js`. Headless Chromium nespuštěn (bez dlaždic bez přínosu).
- Pozor: doplněk popis mapy sám neoznačuje jako ilustrační (jen text v manifest.json, který se nikde nezobrazuje). Označení je potřeba dopsat ručně, např. do `dalsi_zdroje`/popisu v `mesto.json` (nesahal jsem).
