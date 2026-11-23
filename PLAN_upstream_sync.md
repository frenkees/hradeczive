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
