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

Poslední celé překreslení a nasazení 2026-11-14 (mosty, Mileta, aréna, trasy MHD, funkce /api/zapasy). Od té doby:

- **Cesty na hladině pod mosty** (2026-11-14, `assets/custom_prep.py` kroky 5a2 a 5c, platí pro celé město):
  - chodník a cyklostezka silničního mostu jsou v pasportu plocha nad vodou vedle mostovky; mostovka z dat měla jen
    šířku vozovky, takže chodník zůstal namalovaný na hladině (most U Soutoku na Sokolské u nemocnice). Mostovka se teď
    o chodník z pasportu rozšíří a osa se posune k němu (čtverec 0,0: 6 mostů, 0,1: 2);
  - vozovka, chodník nebo dlažba namalovaná do řeky (víc než 1,5 m od břehu) se vrací na vodu – most je vždy 3D mostovka
    nebo vlastní model (pás na hladině před jezem Hučák).
- **Lávka u Aldisu a náplavka** (`lavka_aldis` v `assets/custom_models.js`, záznam v `dominanty.json`, mostovka z dat
  skrytá v `upresneni.json` → `skryt_mosty`): bílá UHPC lávka 112 m s hrbem, žebra po 2,5 m (pod mostovkou k lanům,
  nad ní sloupky zábradlí prohnuté ven, LED v madle svítí v noci), pilíř do V na východním břehu, vějířové schody
  na západním konci. Náplavka pod ní na východním břehu: 9 dřevěných sedacích stupňů podél stezky (~34 m) a plovoucí molo
  na místě mola z OSM. Výšky z DMR přes `probe`. Předlohy: `izomapa/landmarks_ref/lavka_aldis/` (33 fotek z Commons,
  ZDROJE.md), poloha schodů podle fotky z 08/2024 (ortofoto je starší) – **ověřit délku a polohu schodů na místě**.
  Nový obecný klíč `spec.bez_stromu` v `dominanty.json` skryje stromy v pásu vlastního mostu.
- **Malá Mileta** (u záchranky, 50.1990, 15.8343; 2026-11-14): nové ulice k obytné výstavbě jsou v OSM ještě
  `highway=construction` (otevření 06/2027), pasport magistrátu je už má. Za hranicí zóny přestavby se kreslily z pasportu,
  v zóně se cesty ve výstavbě přeskakovaly → na hranici zóny pruh trávy přes silnici. Teď se v zóně kreslí i silnice ve
  výstavbě (`construction=` silniční třída). Náhled `izomapa/preview/mileta/mala_mileta_pred_po.jpg`.
  Bypassy na Miletě: podle města jsou tři (SZ, JZ, JV) a všechny tři v mapě jsou – žádný nechybí.
- **Estakáda I/31 a skleněný protihlukový tunel** (Okružní, 50.2150, 15.8434; 2026-11-14): dominanta „Estakáda I/31 a skleněný tunel“
  (`dominanty.json`, model `estakada_i31` v `custom_models.js`): 180 m, zakřivená skleněná stěna přecházející do střechy, žebra
  po ~2,9 m, hlavní táhla po 23 m s bílými stožáry a táhly k nosníku ve střeše, v noci svítí pásy pod střechou. Osa z OSM
  (`spec.os`), výška mostovky z dat (`prep.py` → `b['os']`, vyhlazená). Předlohy `izomapa/landmarks_ref/estakada_i31/` (5 fotek z Commons),
  rozměry (šířka ~19 m, výška ~9 m, stožáry ~13 m) jsou odhad z fotek a ortofota, **ověřit**. Sklo je kvůli renderu neprůhledné.
  Obecná oprava mostů v `prep.py` (platí pro celé město, **překreslit všechny čtverce**): konec mostu, který leží na jiné silniční
  mostovce (rozdělená estakáda, sjezd), už nezačíná na terénu, ale ve výšce té mostovky (dlouhé mostovky se zpracují první) –
  sjezd na Pospíšilovu třídu teď klesá plynule z úrovně estakády. Náhledy `izomapa/preview/estakada_pred.png` / `estakada_po*.png`.
- Náhledy před/po: `izomapa/preview/mosty/` (pred_/po_ soutok, hucak, aldis). Scény čtverců 0,0 a 0,1 jsou už připravené,
  překreslit je potřeba všechny čtverce (oprava mostů platí pro celé město).

## Noční katalog kandidátů na dominanty

`skripty/noc/noc_hlidac.py` (z `izohradec/`) spustí a hlídá `noc_katalog.py`: kandidáti z Wikidat v území mapy (1 406),
volně licencované fotky z Commons, ortofoto, koncepty „příběhů míst“ z cs Wikipedie (Ollama qwen3:14b, každé číslo
a citace se ověří proti zdroji, jinak se zahodí), třídění fotek (qwen3-vl:8b). Výstup `izomapa/build/noc/index.html`,
`katalog.json`, `mista_koncepty.json` (jen KONCEPTY – před použitím ověřit). Pokračuje po pádu (`stav.json`).
Hlídač: pád / 20 min bez tepu / 40 min na jedné položce -> restart a karanténa položky; víc než 6 restartů za hodinu nebo
4 bez postupu -> `build/noc/POMOC.txt` (čeká na něj Claude v otevřené session).

## Přestavby, které pasport magistrátu ještě nemá

`assets/prestavby.json` = zóny (`zona` [[lat, lon]…]) s aktuálním OSM (`skripty/prestavby_osm.py`, z `izomapa/`, bere API OSM).
V zóně hook `custom_prep.py` nepoužije pasport komunikací, zeleně, značení, stání, zábradlí ani lamp a nakreslí vozovky
podle OSM (šířka z pruhů, dělicí čáry pruhů, ostrůvky z `area:highway`, zebry z uzlů `crossing`); podchody (tunely) vynechá.
- **Křižovatka Mileta** (ŘSD 2024 – 10/2026, provoz od konce dubna 2026): bypassy, přímá třída E. Beneše, malá Mileta,
  oblouk k nemocnici. 4 podchody jako model `mileta_podchody` (dominanta „Křižovatka Mileta“): portály se světlem,
  rampy se zídkami a zábradlím podle OSM („Podchod 1–4“, v OSM `fixme: resurvey after construction`).
  Terén má krok 5 m, rampa se do něj zahloubit nedá – zářez naznačuje tmavnoucí podlaha. **Ověřit proti skutečnosti / fotkám.**
- Další kandidát: kruhový objezd Komenského (50.2078, 15.8325) – přidat zónu do `prestavby.json` a pustit `prestavby_osm.py`.

## Malšovická aréna (FINEP Arena) a zápasy FC Hradec Králové

- Model v dlaždicích: zaoblené tribuny 140 × 100 m, lamelová fasáda, membránová střecha s příhradovinami, budova hlavní tribuny
  s nápisem, obrazovka u severní tribuny, 4 lízátka se vzpěrou a terčem 11 m (podle ortofota a fotek z Commons).
- Animovaná vrstva `assets/custom_web.js` (obecný háček `window.IZOMAPA_PLUGINS` ve `web/app.html`, `build_html.py`
  ho kopíruje do `site/`): v noci RGB LED pás po obvodu fasády, při domácím zápase (75 min před výkopem do konce) svítí
  lízátka a hřiště, na obrazovce skóre / příští zápas, nad arénou popisek, v kartě arény rozpis domácích zápasů a výsledky.
- Data: Vercel funkce `/api/zapasy` (`skripty/vercel_api/zapasy.js` – rozpis z fchk.cz/matches/MUZ, při zápase skóre
  a fáze z onlajny.com; cache 30 s při zápase, jinak 10 min), záloha statický `zapasy.json` (`node skripty/zapasy.mjs`,
  `pripravit_vercel.mjs` ho vyrobí i s funkcí). Parser závisí na HTML fchk.cz – když se web klubu změní, rozpis zmizí.
- Podmínky užití dat fchk.cz / onlajny.com nejsou známé – zeptat se klubu, případně uvést zdroj v patičce.
- Ještě není: hráči na hřišti a fanoušci na tribunách, zimní stadion.

## Trasy MHD

GTFS DPMHK nemá tvary tras, `mhd.py` je počítá po silnicích (`road_route.py`), ale vede je přednostně po referenčních trasách:
`assets/mhd_trasy_ref.json` (`skripty/mhd_trasy_ref.py`, z `izomapa/`): relace linek DPMHK z OSM (43, všechny linky kromě nočních),
mapa linek magistrátu (ArcGIS `thematic/mhd_linky`, zjednodušená, bez linek 4 a 21 a bez variant Š/R – jen kontrola a rozhodčí)
a polohy zastávek z OSM (CIS JŘ má jednu souřadnici na název – vybere se stejnojmenná zastávka na trase linky).
Hrany na koridoru OSM jsou 0,3× levnější, podél městské čáry 0,65×; ruční průjezdní čáry `assets/mhd_trasy_rucne.json`
(`[{"linka": "12", "pres": [[lat, lon], …]}]`) 0,1×. Do grafu patří i pěší zóna s povoleným vjezdem bus/trolejbus (Riegrovo nám.).
Kvalita každého úseku mezi zastávkami (`kvalita` v mhd.json): jistý / jen OSM / jen město / rozpor / nejistý / mimo mapu.
Stav 2026-11-13 (úseky v mapě): 3 265 jistých, 265 jen město (hlavně noční linky), 62 jen OSM, 9 rozporů, 135 nejistých –
nejvíc linky 15, 10, 19, 27, 9 a školní/zkrácené varianty (Š, R), které v OSM nejsou.
Kontrola: `python ../skripty/mhd_trasy_kontrola.py` -> `izomapa/preview/mhd_trasy/index.html` (obrázek na linku).
Po změně tras stačí `mhd.py`, `build_html.py` a nasazení (bez renderu).

## Návrhy na zrychlení a úklid (analýza 2026-11-14, zatím nic z toho není udělané)

Vychází z grafu graphify, kódu a logů celého překreslení 14. 11. Čtverec 1,1 (339 s; celé město 23 min, 4 čtverce souběžně),
časy fází odvozené z časů souborů, začátek `prep.py` dopočítaný:

| fáze | čas | podíl |
|---|---|---|
| `prep.py` (z toho 4 textury terénu ~26 s) | ~155 s | 46 % |
| render 5 variant (`render.mjs`) | 43 s | 13 % |
| `dzi.py` | 135 s | 40 % |

Samotné kreslení dlaždic je ~5 s na variantu (0,03 s na dlaždici), zbytek renderu je start Chromia a stavba scény.
Úzké hrdlo je Python na CPU, ne GPU – další GPU akcelerace renderu nic nepřinese.

### Zrychlení (podle přínosu)
- [ ] **Nahrávání na R2**: manifest porovnává velikost a čas změny, ale `dzi.py` vždy smaže a přepíše celý čtverec → po každém
      překreslení se nahraje všech 1,4 GB (~1 MB/s), i když se bajty nezměnily. Hash obsahu v manifestu
      (`skripty/nahrat_dlazdice_r2.mjs`) a S3 API (rclone / SDK) místo jednoho procesu `wrangler` na soubor.
- [ ] **Přírůstkové `dzi`**: porovnat hash zdrojových PNG s minulým během a překódovat jen dotčené dlaždice pyramidy.
      S předchozím bodem zlevní opravu jedné dominanty z desítek minut na minuty.
- [ ] **Přetížení vláken v `dzi`**: 4 procesy × 8 vláken na 12 jádrech, zatímco jiné čtverce běží v `prep`. Jeden sdílený pool
      pro kódování, nebo `IZO_DZI_VLAKNA=3`.
- [ ] **`prep.py`**: `load()` převádí souřadnice po jedné geometrii Python lambdou → vektorový `shapely.transform` nad poli;
      39× `iterrows`/`apply`; sousední čtverce a velké JSONy (`mmhk.json` – předpoklad, ověřit) se čtou znovu pro každý čtverec →
      předpočítat po čtvercích; 4 textury ukládat souběžně a s nižší kompresí PNG.
- [ ] **Cache kroků podle hashe vstupů**: rozdělit `prep` na scénu, textury a graf dopravy; změna dopravy nepřepočítá geometrii,
      nezměněný čtverec se přeskočí celý.
- [ ] **Render**: jeden start Chromia na čtverec a přepínání variant uvnitř místo 5 startů (odhad 43 s → 15–20 s).
- [ ] **Měření předem**: do `build/render_par.log` zapisovat čas každé fáze (prep / render / dzi) a pustit `cProfile` na jeden
      `prep`. Bez toho jsou body o vláknech a `prep.py` jen odhad z kódu.

### Kód a workflow
- [ ] **Háček přes `exec` do globálů**: `assets/custom_prep.py` závisí na interních názvech proměnných `prep.py`, rozbije ho
      každý merge z upstreamu → explicitní rozhraní (kontextový objekt se zdokumentovanými poli).
- [ ] **Regresní test obrazem**: pevné výřezy dominant (den, noc) přes `skripty/nahled_mista.py` porovnat s uloženým vzorem.
      Dnešních 12 testů pokrývá jen nástroje, `prep` a render nic.
- [ ] **Stavba do pracovní složky**: `postav.sh` hned na začátku maže `site/tiles`, při pádu není web → stavět vedle a na konci prohodit.
- [ ] Drobnosti: `render_all.sh` má natvrdo `.venv/bin/python` (na Windows neběží); `python mhd.py || true` spolkne chybu;
      konstanty `gx0`/`gy1` zkopírované v `render_chunk.sh` i `nahled_mista.py`; chybí `requirements.txt` / `pyproject.toml`
      (verze Pythonu nejsou zamčené).
- [ ] Rozdělit `web/app.html` (195 kB) a `render.html` (97 kB) na ES moduly (importmap už tam je, build krok není potřeba).

### Git a upstream
- [ ] **Kořenové repo bylo 2026-11-14 v odpojeném HEAD** (ne na `main`) – ověřit a vrátit na větev, jinak se commity mohou ztratit.
- [ ] **Větev `hradec`** (7 commitů, +16 110 řádků proti upstreamu) míchá obecné opravy a městská data → rozdělit na obecné
      commity (rebase na upstream, vhodné pro PR) a městské soubory.
- [ ] **Městské soubory mimo klon**: přesunout do kořenového repa, cestu předat proměnnou prostředí (odpadne `git add -f` proti
      upstream `.gitignore`); `izomapa` připojit jako submodul, aby byla dvojice commitů svázaná.
- [ ] **PR autorovi po malých kusech**: `dalsi_zdroje`, jednosměrky v `road_route.py`, opravy mostů, silnice ve výstavbě,
      háček `IZOMAPA_PLUGINS`, opravy pro Windows.
- [ ] **Licence AGPL-3.0**: upravená izomapa běží veřejně, fork je v soukromém repu. AGPL nejspíš vyžaduje nabídnout návštěvníkům
      zdrojový kód úprav – ověřit; fork zveřejnit nebo přidat odkaz na zdroj.
- [ ] Generovaná data v gitu (`assets/prestavby.json`, 12 454 řádků) oddělit od ručně psaných, ať jsou diffy čitelné.

Doporučené pořadí: nahrávání na R2, přírůstkové `dzi`, měření fází.

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
- [x] **Trasa linky po kliknutí na vozidlo MHD** (2026-11-13): klik nakreslí trasu spoje (projetá část tlumená, zastávky
      s časy, nejisté úseky čárkovaně), zůstane i při oddálení, tlačítko „Celá trasa“, × ji skryje. Trasy viz „Trasy MHD“ níže.
      **Zbývá projít nejisté úseky** (`izomapa/preview/mhd_trasy/index.html`) a opravit je ručně.
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
- [x] **Malšovická aréna** – popisek s dalším zápasem, lízátka při zápase, pop-up s rozpisem (2026-11-13, viz výše).
- [ ] Aréna: na hřišti běhají hráči a na tribunách fandí lidé (při zápase).
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
