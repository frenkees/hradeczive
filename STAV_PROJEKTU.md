# Izometrický Hradec Králové – stav projektu

Aktualizováno 2026-11-13. Veřejně: **https://hradeczive.vercel.app** (staré izohradec.vercel.app je alias).
Cíl a souřadnice jsou v [CLAUDE.md](CLAUDE.md), návod nástroje v [izomapa/CLAUDE.md](izomapa/CLAUDE.md).

## Co je hotové

- **Celé město**: 16 čtverců 2,3 × 2,3 km (i, j ∈ −1…2 kolem 50.20539, 15.83009), 4 roční období + noc, MHD DPMHK podle jízdních řádů.
- **Dominanty** (`izomapa/assets/dominanty.json` + `custom_models.js`): Bílá věž, katedrála sv. Ducha, Gymnázium J. K. Tyla,
  jez Hučák, Ulrichovo náměstí, Malšovická aréna.
- **Data magistrátu** (geoportal.mmhk.cz) v celé mapě – viz níže.
- **Nasazení**: web na Vercelu (projekt `frenkees-projects/hradeczive`), dlaždice v Cloudflare R2 (bucket `izohradec`,
  veřejně `https://pub-55cbad9c2db745779e46b9eac5658b47.r2.dev`).
- **Graphify**: znalostní graf repa v `graphify-out/` (`graphify query "…"`).

## Data Magistrátu města HK

`skripty/mmhk_pasport.py` (spouštět z `izomapa/`) stáhne pro celou mapu do `izomapa/assets/mmhk.json` a `izomapa/assets/mmhk_znaceni/`:

| co | zdroj | použití v mapě |
|---|---|---|
| plochy vozovek, chodníků, materiál; parkoviště | pasport komunikací (WFS `pakom`) | skutečné tvary ulic místo čar z OSM, obrubníky |
| vodorovné značení | WMS `pakom` (městská symbologie, maska 0,1 m) | přechody, čáry, stání |
| řady parkovacích stání (značky 486/487/488) | pasport komunikací | auta na skutečných stáních, natočená podle čar |
| stromy (druh, taxon), plochy zeleně, parky | pasport zeleně (WFS `pazel-sec`) | 50 tis. stromů na skutečných místech, trávníky/záhony/keře |
| výška stromů | DMP 1G (laser ČÚZK, `izomapa/build/dmp/*.laz`) | výška u ~50 % stromů |
| lampy veřejného osvětlení | WFS `pvohk` | 13 tis. lamp, noční osvětlení |
| opěrné zdi, zábradlí | DTMM (ArcGIS REST) | nábřežní zdi Labe a Orlice (svislá stěna, hladina dole), zábradlí |

Kreslí to hook `izomapa/assets/custom_prep.py` (fáze `cliffs`, `cemetery`, `props`); vypnout `IZO_MMHK=0`.
Zdroj je v patičce mapy (`dalsi_zdroje` v `izomapa/mesto.json`).
Geoportál po ~1 500 rychlých dotazech na čas odmítá spojení – stahuje se šetrně, stažené části jsou v cache
(`izomapa/build/mmhk_cache/`, `--bez-site` = jen přepočet bez sítě).
Otevřená data města (ortofota 2014–2023, pasporty, DTMM, 3D budovy): https://web.mmhk.cz/opendata/

## Jak mapu postavit a nasadit

Vše z `izomapa/` v Git Bash, Python `.venv/Scripts/python` s `PYTHONUTF8=1`.

1. (volitelně) nová data magistrátu: `.venv/Scripts/python ../skripty/mmhk_pasport.py`
2. scény, render, dlaždice, web: `sh ./postav.sh render` (~25 min, 16 čtverců)
3. rychlý náhled místa: `.venv/Scripts/python ../skripty/nahled_mista.py <lat> <lon> out.png [season=lights]`
4. nasazení (z `izohradec/`):
   - `node skripty/nahrat_dlazdice_r2.mjs izohradec` (jen změněné dlaždice, ~1 MB/s)
   - `node skripty/pripravit_vercel.mjs https://pub-55cbad9c2db745779e46b9eac5658b47.r2.dev`
   - `cd nasazeni/vercel && vercel deploy --prod --yes`

## Otevřené úkoly

- [ ] **Licence dat magistrátu**: nikde výslovně uvedená; zdroj je v patičce, ale je dobré poslat magistrátu dotaz / žádost o souhlas.
- [ ] **Doména hradeczive.eu**: registrace u WEDOS přes WAPI (`skripty/domena.mjs`), DNS v Cloudflare. Čeká na účet WEDOS
      (kredit, WAPI heslo, povolená IP), Cloudflare API token a vyplnění `nasazeni/tajne.env` + `nasazeni/wedos_kontakt.json`
      (obojí mimo git). Ostrý nákup jen po výslovném potvrzení. Pak: Vercel doména, R2 doména `tiles.hradeczive.eu`,
      `mesto.json` url, `build_html.py`, redeploy.
- [ ] **Nábřežní zdi**: podle laseru 2,5–3 m nad hladinou (hladina je v DMR dopočítaná); uživatel odhaduje ~4 m – případně
      snížit hladinu v centru.
- [ ] **Pasport místy zastaralý** (např. kruhový objezd Komenského 50.2078, 15.8325 v pasportu chybí) – projít mapu proti ortofotu.
- [ ] **Svislé dopravní značky** (WFS `pk-dzs-*`, 13,7 tis.) zatím nekreslené – potřebují vlastní 3D model.
- [ ] **Pull request autorovi izomapy**: obecná volba `dalsi_zdroje` (build_html.py, web/app.html) a další obecné úpravy
      na větvi `hradec` v `izomapa/`.
- [ ] Letadla (`functions/`) na Vercelu nefungují (vypnuto).
- [ ] Před zveřejněním fakt projít mapu a příběhy míst proti skutečnosti.

## Git

- `izohradec/` – projektový repozitář (skripty, dokumentace, konfigurace nasazení; bez tajemství, dlaždic a stažených dat).
- `izomapa/` – klon `adamklatovsky/izomapa`; vlastní úpravy na lokální větvi **`hradec`** (sdílený kód i městské soubory,
  které upstream `.gitignore` vynechává – přidané přes `git add -f`). Na upstream nepushovat.
- Mimo git (vyrobí se znovu): `izomapa/build`, `data*`, `site`, `assets/mmhk.json`, `assets/mmhk_znaceni/`, `nasazeni/vercel`.
- Tajemství jen lokálně: `nasazeni/tajne.env`, `nasazeni/wedos_kontakt.json`, `.vercel/`.
