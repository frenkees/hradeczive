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

## Čeká na překreslení (vizuální změny, zatím jen uložené)

Celá mapa se překreslí až po nasbírání víc změn (`sh ./postav.sh render`, pak nahrát dlaždice a nasadit).
Ověřuje se jen výřez dotčeného místa (`prep.py` čtverce + `skripty/nahled_mista.py`, náhledy v `izomapa/preview/`).
- Silnice pod mostovkami (viz Most níže) – ověřeno na mostě 50.21954, 15.81119 a Pražském mostě (`preview/mosty/`).
  Scény čtverců 0,0 a −1,1 už jsou přepočítané.

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

## Nápady a požadavky do budoucna (zadání uživatele 2026-11-13)

Odkazy jsou na živou mapu (`#leto@lat,lon,zoom`); hradeczive.vercel.app funguje stejně.

### Střední priorita
- [ ] **Zastávky MHD**: stáhnout zastávky (GTFS DPMHK `stops.txt`), možnost je na mapě zvýraznit; po kliknutí pop-up
      s odjezdy na příští hodinu (linka, směr, čas).
- [ ] **Trasa linky po kliknutí na vozidlo MHD**: překreslit barevnou čáru po celé trase linky. Trasy **důkladně ověřit**
      (kterými ulicemi linka opravdu jede); kde k další zastávce vede víc možných ulic, trasu **nepočítat automaticky**
      (GTFS nemá `shapes.txt`) – ruční/ověřené trasy (např. z pasportu, jízdních řádů DPMHK, OSM relací route=bus/trolleybus).
- [x] **Most** https://izohradec.vercel.app/#leto@50.21954,15.81119,0.33 – silnice nakreslená i pod mostovkou (2026-11-13):
      byla to plocha vozovky/chodníku z pasportu magistrátu; `custom_prep.py` (krok 5b) pod mostovkou výš než 1 m nad terénem
      vrací povrch z OSM (koleje, voda, tráva, silnice pod mostem). Platí pro všechny mosty. **Čeká na překreslení.**
- [ ] **Podjezd** https://izohradec.vercel.app/#leto@50.21093,15.80850,0.23 – silnice (auta + trolejbusy) vede podjezdem,
      železnice nad ní po mostě v úrovni okolního terénu (teď je to obráceně / špatně).
- [ ] **Model mostu** https://izohradec.vercel.app/#leto@50.21550,15.90725,0.33 – velký obloukový most v modrobílém
      provedení; najít volně licencované foto (Wikimedia Commons) a udělat vlastní model (`custom_models.js`).

### Nízká priorita
- [x] **Směr provozu na víceproudých silnicích** (2026-11-13): auta jednosměrky dodržovala už dřív; nově počet pruhů
      z OSM (`nastroje/pruhy.py` → `assets/pruhy.json`, 589 cest / 56 km), na 2–4pruhovém pásu jedou auta vedle sebe
      (nákladní vpravo) a plynule mění pruh. Trasy MHD (`road_route.py`) dřív jednosměrky ignorovaly – na rozděleném
      okruhu jezdily autobusy po obou pásech oběma směry (~48 % vzorků proti směru); teď dodržují jednosměrky
      i kruhové objezdy (zbývá ~1 % = pár metrů u křižovatek). Po změně dopravy stačí `prep.py` (nebo jen graf silnic),
      `overlay.py`, `mhd.py`, `build_html.py` – bez renderu.
- [ ] **Zákaz parkování** aut na kruhových objezdech, u křižovatek a na městském okruhu (zákazy stání v datech jsou,
      ale nejspíš zbytečná složitost – stačí jednoduchá pravidla).
- [ ] **Autobusový terminál MHD**: před terminálem parkují autobusy vedle sebe v desítkách řad (linkové i dálkové) – vykreslit.
- [ ] **Malšovická aréna** https://izohradec.vercel.app/#leto@50.20609,15.84415,0.57 – malý text „další zápas: datum a čas“;
      při probíhajícím zápase svítí „lízátka“, na hřišti běhají hráči a na tribunách fandí lidé; po kliknutí pop-up s rozpisem zápasů.
- [ ] **Zimní stadion**: po kliknutí pop-up s dalšími zápasy (datum, čas, kdo s kým).

### Větší projekt: fotografie budov od lidí
- Klik na budovu → výzva „Pomoz vylepšit tuto budovu“; nahrávání jen po registraci e-mailem.
- Limity: fotka max. 25 MB, max. 4 fotky na budovu, fotky hned v prohlížeči zmenšit/komprimovat;
  ochrana proti spamu max. 20 fotek denně na uživatele + celkový denní limit pro všechny.
- Kontaktní e-mail autora mapy; autor může aktivním uživatelům udělit práva bez limitu.
- Nahráním uživatel potvrzuje, že je autorem fotek, a souhlasí s jejich bezplatným použitím k vylepšení projektu (jasné upozornění).
- Potřebuje server (např. Cloudflare Worker + R2 + D1 jako u hlášení nepřesností v `izomapa/hlaseni/`), ověření e-mailu,
  moderaci a zásady zpracování osobních údajů (GDPR).

## Git

- `izohradec/` – projektový repozitář (skripty, dokumentace, konfigurace nasazení; bez tajemství, dlaždic a stažených dat),
  soukromá záloha na GitHubu **frenkees/hradeczive** (remote `origin`, větev `main`).
- `izomapa/` – klon `adamklatovsky/izomapa`; vlastní úpravy na lokální větvi **`hradec`** (sdílený kód i městské soubory,
  které upstream `.gitignore` vynechává – přidané přes `git add -f`). Soukromá záloha **frenkees/hradeczive-izomapa**
  (remote `zaloha`, větev `hradec`; `git push` jde tam). Remote `origin` = upstream autora – tam nepushovat.
- Mimo git (vyrobí se znovu): `izomapa/build`, `data*`, `site`, `assets/mmhk.json`, `assets/mmhk_znaceni/`, `nasazeni/vercel`.
- Tajemství jen lokálně: `nasazeni/tajne.env`, `nasazeni/wedos_kontakt.json`, `.vercel/`.
