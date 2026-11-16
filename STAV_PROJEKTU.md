# Izometrický Hradec Králové – stav projektu

Aktualizováno 2026-11-16 (večer). Veřejně: **https://hradeczive.vercel.app** (staré izohradec.vercel.app je alias).
Cíl a souřadnice jsou v [CLAUDE.md](CLAUDE.md), návod nástroje v [izomapa/CLAUDE.md](izomapa/CLAUDE.md).

## Překreslení a nasazení 2026-11-16 večer
Celé překreslení všech 16 čtverců (20 min) a nasazení na hradeczive.cz (R2 + Vercel, včetně `/api/doprava`, HERE klíč už je ve Vercelu).
Zahrnuje vše dosud „uložené“: obchody a značky, nákupní centra, 3. dávka dominant, sloučení upstreamu (semafory, hřiště), mosty/podjezdy,
Futurum (issue #2), Kaufland ve výstavbě se nekreslí (#3), knihovna zpět s modelem `knihovna` (#4; 3. dávka dominant ji přepsala obecným popisem),
přístřešky zastávek otočené k silnici, svislé značky (~18,8 tis.). Nezbývá nic „čekajícího na překreslení“ kromě vánoc (viz níže).
- **Zrychlení prepu** (čtverec ~160 s → 73–110 s): `MaxFilter` přes scipy (25 s), převod do S-JTSK interpolací (40 s), vektorové `load()`, `compress_level=1` u mezisouborů, vlákna `dzi` podle počtu souběžných čtverců (`IZO_DZI_VLAKNA`).
  Přírůstkové `dzi` záměrně NEdělat: paleta se počítá z celého obrazu, takže po každé změně by se stejně změnila všem dlaždicím.
- **HERE doprava**: ověřit podmínky (hledání: starší podmínky HERE Platform omezují ukládání výstupu na 30 dní a vyžadují uvedení HERE; Advanced Traffic má podle ceníku 2 500 bezplatných dotazů měsíčně, náš provoz je až ~4 300/měs. při stálé návštěvnosti). Sběr ukládá jen agregovaný histogram, ne surové snímky.
- **Vánoční náměstí** (později): stavět podle webu vanocevhradci a vlastních fotek uživatele (`assets/vanoce.json`, `vanoce.sh`).
- **Dashboard** (`skripty/dashboard/server.py`): volání git/vercel/gh blikala okny konzole; opraveno `CREATE_NO_WINDOW`, tray je třeba po změně restartovat.

## Rozšíření mapy 2026-11-16 (jižní řádek j = −2, západní sloupec i = −2)
`skripty/rozsirit_mapu.sh` (z kořene repa): stáhne Overture, laser, les/pole, hřiště, RÚIAN, střechy, komíny, pruhy, přejezdy a data magistrátu pro celou novou plochu a pustí
`postav.sh render` (renderuje jen čtverce se změněným otiskem scény). Záloha původních dat je v `izomapa/build/zaloha_rozsireni/`.
Pozor: obnova vstupů přepsala i data ve starých čtvercích (OSM hřiště, komíny, střechy z ortofota…), proto se při tomto běhu překreslily skoro všechny;
další běh už přeskakuje (`beze změny`). Render spadl jednou na přechodném `ERR_CONNECTION_RESET` lokálního serveru, stačí pustit znovu.
Nové čtverce nemají živou dopravu (HERE a TomTom `BBOX` jsou pořád jen původní město) ani semafory; MHD trasy a vlaky jedou i po nové ploše, jen kde jsou silnice.

## Co je hotové

- **Celé město**: 25 čtverců 2,3 × 2,3 km (i, j ∈ −2…2 kolem 50.20539, 15.83009; jižní řádek a západní sloupec přidány 2026-11-16, skript `skripty/rozsirit_mapu.sh`), 4 roční období + noc, MHD DPMHK podle jízdních řádů.
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

Poslední celé překreslení a nasazení 2026-11-14 večer (mosty, podjezdy, zářezy, Šrámkův most, 38 dominant z katalogu, zastávky MHD) (mosty, Mileta, aréna, trasy MHD, /api/zapasy). Celé překreslení všech 16 čtverců s následujícími změnami proběhlo
2026-11-14 (+ zóna kruhový objezd Komenského), (vše níže je od 2026-11-14 večer nasazené na živém webu; dlaždice R2 + Vercel):

- **Obecná oprava mostů** (2026-11-14, izomapa commit `16710e5`, `prep.py`, `assets/custom_prep.py`): opěry v úrovni silnice, mostovka v rovině a jen po
  břeh, lampy a zábradlí na mostě (nad vodou se zahazují), nájezd nepokračuje přes křižovatku. Náhledy `izomapa/preview/mosty2/` (m1–m8 před/po).
  Zbývá: u mostu v násypu je terén po zářezu zjednodušený (krok mřížky 5 m).
- **Podjezdy** (50.21093, 15.80850 – nádraží): kratší silniční „tunel“ pod tratí = podjezd; `prep.py` vyřízne terén podél osy (`TUNNEL_PASSES`),
  trať nad ním dostane syntetický `is_bridge`, portály mají všechny silniční třídy (5. prvek = poloviční šířka), pasport magistrátu nekreslí vozovku
  nad dlouhým tunelem (`TUNNEL_ZONES`). Obecný zářez pod každým mostem nad silnicí/tratí/pěšinou (terén pod mostovkou klesne na úroveň cesty).
- **Nový most plk. Šrámka ve Svinarech** (obloukový ocelový, 50.2158, 15.9081, přes Orlici): model `most_sramek` (dva modré oblouky, závěsy),
  rozpětí 62 m a vzepětí 10 m jsou odhad z fotek. Předlohy `izomapa/landmarks_ref/sramek_most/` (CC BY-SA 4.0, ZDROJE.md).
- **Zastávky MHD**: v panelu Vrstvy volba „Zastávky MHD“ (značky + jména při přiblížení), kliknutí a hledání ukazují odjezdy (už dřív), vybraná zastávka pulzuje.
  Jen web, render není potřeba.
- **Dominanty z nočního katalogu, 1. dávka** (2026-11-14, `assets/dominanty.json`, jen popis budov `spec` – barvy, střechy, věže, bez vlastních modelů):
  kostel Nanebevzetí P. Marie, Radnice, Klicperovo divadlo, Galerie moderního umění, Evangelický kostel, Sbor kněze Ambrože, kostel Božského srdce,
  kostel sv. Antonína, Adalbertinum, Aldis, Hvězdárna, Pedagogická fakulta, Rudolfinum, hotely Grand a Labská, Kněžský seminář, Pivovar,
  Lékařská a Farmaceutická fakulta, Gymnázium B. Němcové, Wiplerova vila, vila Tesařových. Barvy a výšky jsou odhad z fotek (`build/noc/katalog/`),
  poloha podle Wikidat; **zkontrolovat napárování na správnou budovu a vzhled** po celém překreslení (ověřeno jen kostel, radnice, Adalbertinum, seminář).
  **2. dávka** (stejně, jen `spec`): Zbrojnice, Žižkova kasárna, Archa, Divadlo Drak, Odborná škola uměleckého zámečnictví, SPŠ stavební, vily (Fuchsových,
  Honzákova, Nepasických, Píšova), Klicperova 4, Dům U Špuláků, Dům U Švagerků, Dělnický dům, škola v Kuklenách, škola koželužská, Novákovy garáže,
  Aupark, OC Futurum, OC Atrium. Ve výřezu zkontrolováno jen centrum, východ a západ čtverce 0,0; Dělnický dům, Futurum a kostel sv. Antonína jsou v jiných čtvercích.
  **3. dávka** (2026-11-15, jen `spec`, zatím NEvyrenderováno – čeká na další překreslení): Magistrát, ředitelství státních drah, Steinského palác, Weinhengstův dům,
  Rejchlův dům, Jihlavcův dům, Knihovna města, Studijní a vědecká knihovna, Střední zdravotnická škola, Anglobanka, Hotel U Královny Elišky, plynárna Kukleny, Prior,
  Pražskopředměstská radnice, Městské lázně, Dům U skleněné věže, vila Charváta, kostel sv. Pavla (Pouchov), Vojenská nemocnice (celkem 88 dominant).
  Ve výřezu 0,0 ověřeno napárování Magistrátu, ředitelství drah a ČSA 27/29. Katalog už nemá další vhodné budovy bez vlastního modelu.
  Zbývá z katalogu (vlastní modely): lávky (Hradubická cyklostezka, Na Podhůrkách, Jiráskovy sady), Moravský jez, Kamenný most, most Klapák, Archa,
  Hlavní nádraží, Magistrát, Kulturní dům Střelnice, Žižkova kasárna, Zbrojnice; a další vily/činžáky.
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

- **Obchody, rychlé občerstvení, čerpací stanice a nákupní centra** (2026-11-16, zatím NEvyrenderováno – čeká na celé překreslení):
  - `izomapa/assets/znacky.json` = tabulka 47 značek (regulární výraz na název, barvy zdí/pásu/proužku, nápis písmem 3×5, logo, tvar vstupu, pylon).
    Hook v `assets/custom_prep.py` (fáze `props`, vypnout `IZO_ZNACKY=0`) přiřadí místa z Overture places + názvy budov z OSM k budovám:
    jediná značka = celá budova (zdi, plochá střecha, pás pod střechou, nápis/cedule na průčelí – když průčelí není z JZ vidět, i na viditelné stěně –,
    vstup lidl/kaufland/sklo/stres/mcd/kfc, pylon u nejbližší silnice), víc značek v budově = pás a nápis jen na úseku stěny, v paneláku výloha v parteru,
    hypermarket s pasáží = kotva celá + nájemci v parteru. Pumpy: největší stříška do 35 m (bílá, barevné čelo, ostrůvky se stojany), prodejna, pylon s cenami.
    Nákupní centra (místo shopping_mall) a dominanty se nemění. Model `znacka` v `custom_models.js`; v noci cedule, M a čela stříšek svítí vlastní barvou
    (`render.html`, solidMat: `aw.w = 1`).
  - Nákupní centra jako dominanty s modelem `oc` (obecný: části/ovály, obklady fasád, cedule s nápisem, světlíky, plochy na střeše; `nahradit` srovná budovy
    z dat uvnitř části): **Aupark** (skleněná rotunda, červenooranžový obklad, šedá fasáda s bílými lomenými čarami, nápisy AUPARK, kosočtverečné světlíky),
    **Futurum** (cihlový parter, prosklený blok kina, nápis FUTURUM na modrobílém pásu, TESCO, CINESTAR, tmavá střecha Tesca, parkovací dům),
    **Atrium** (terakotový kvádr s bílými pruhy a úzkými okny, svislé ATRIUM, parkoviště na střeše), **Orlice Park** (nový záznam: dřevěný parter, stříbrná patra,
    vstupní kostka s nápisem, fotovoltaika). Předlohy `izomapa/landmarks_ref/oc_*` (Commons, ZDROJE.md), tvar z ortofota ČÚZK; výšky a barvy jsou odhad.
  - Náhledy `izomapa/preview/znacky/` (po_s1c, po_brezhrad*, po_futurum, po_aupark, po_atrium, po_orlicepark, po_pumpy, noc_s1). Ověřit: Kaufland v budově
    pojmenované Kaufland u 50.1993, 15.8357 (z OSM), bauMax u Orlice parku (zavřený, nekreslí se), Lidl/Tesco v OD Prior (dominanta, nekreslí se).

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
- [x] **Nahrávání na R2** (2026-11-14): manifest teď porovnává sha256 obsahu, po překreslení se nahraje jen změněné (900 z 6 400 souborů, 325 MB
      místo 1,4 GB). S3 API zatím ne (chybí R2 klíče v `tajne.env`; ~1 MB/s je nejspíš limit uploadu).
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
- [x] **Měření předem** (časy fází jsou v `build/render_par.log`; celé překreslení 2026-11-14: prep 150–240 s, render 40–70 s, dzi 150–175 s na čtverec, 26 min celkem; cProfile `prep` zbývá):
- [ ] (původní zadání) do `build/render_par.log` zapisovat čas každé fáze (prep / render / dzi) a pustit `cProfile` na jeden
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
- [x] Kořenové repo je na `main` (ověřeno 2026-11-14, odpojený HEAD nebyl), vše pushnuto.
- [ ] **Větev `hradec`** (7 commitů, +16 110 řádků proti upstreamu) míchá obecné opravy a městská data → rozdělit na obecné
      commity (rebase na upstream, vhodné pro PR) a městské soubory.
- [ ] **Městské soubory mimo klon**: přesunout do kořenového repa, cestu předat proměnnou prostředí (odpadne `git add -f` proti
      upstream `.gitignore`); `izomapa` připojit jako submodul, aby byla dvojice commitů svázaná.
- [ ] **PR autorovi po malých kusech**: `dalsi_zdroje`, jednosměrky v `road_route.py`, opravy mostů, silnice ve výstavbě,
      háček `IZOMAPA_PLUGINS`, opravy pro Windows.
- [x] **Licence AGPL-3.0** (fork `frenkees/hradeczive-izomapa` veřejný od 2026-11-14, odkaz na zdroj v patičce mapy po dalším nasazení; původně:): upravená izomapa běží veřejně, fork je v soukromém repu. AGPL nejspíš vyžaduje nabídnout návštěvníkům
      zdrojový kód úprav – ověřit; fork zveřejnit nebo přidat odkaz na zdroj.
- [ ] Generovaná data v gitu (`assets/prestavby.json`, 12 454 řádků) oddělit od ručně psaných, ať jsou diffy čitelné.

Doporučené pořadí: nahrávání na R2, přírůstkové `dzi`, měření fází.

## Otevřené úkoly

- [x] **Licence dat magistrátu**: uživatel potvrdil 2026-11-16, že je v pořádku (zdroj zůstává v patičce).
- [ ] **Doména hradeczive.eu**: registrace u WEDOS přes WAPI (`skripty/domena.mjs`), DNS v Cloudflare. Čeká na účet WEDOS
      (kredit, WAPI heslo, povolená IP), Cloudflare API token a vyplnění `nasazeni/tajne.env` + `nasazeni/wedos_kontakt.json`
      (obojí mimo git). Ostrý nákup jen po výslovném potvrzení. Pak: Vercel doména, R2 doména `tiles.hradeczive.eu`,
      `mesto.json` url, `build_html.py`, redeploy.
- [ ] **Nábřežní zdi**: podle laseru 2,5–3 m nad hladinou (hladina je v DMR dopočítaná); uživatel odhaduje ~4 m – případně
      snížit hladinu v centru.
- [ ] **Pasport místy zastaralý** (např. kruhový objezd Komenského 50.2078, 15.8325 v pasportu chybí) – projít mapu proti ortofotu.
- [x] **Svislé dopravní značky** (2026-11-16): `skripty/mmhk_znacky.py` (z `izomapa/`) stáhne WFS `pk-dzs-z` do `mmhk.json` (klíč `znacky`, ~18,8 tis.), hook `custom_prep.py` (6b, vypnout `IZO_ZNACKY_DZ=0`) postaví sloupek s tabulí kolmo k ose silnice (`props.sg_*`), model v `render.html` (barva podle druhu: výstražné, stůj/dej přednost, zákazové, příkazové, přednostní, informativní, dodatkové). Tabule jsou jednobarevné bez piktogramů (3–5 px).
- [ ] **Pull request autorovi izomapy**: obecná volba `dalsi_zdroje` (build_html.py, web/app.html) a další obecné úpravy
      na větvi `hradec` v `izomapa/`.
- [ ] Letadla (`functions/`) na Vercelu nefungují (vypnuto).
- [x] **Zastávky MHD na Riegrově náměstí** (2026-11-16): přístřešek měl otevřenou stranu podle směru čáry silnice bez ohledu na stranu; `prep.py` ji teď otáčí k nejbližší silnici (všechny přístřešky ve městě).
- [ ] **Hotel Černigov v noci**: skrz budovu prosvítají okna budov v pozadí – v noci i ve dne jsem v náhledu (`preview/cern_noc.png`) nic takového nenašel (okna vlevo a vpravo patří sousedním budovám za věží); chce ověřit na živé mapě podle konkrétního místa (odkaz/screenshot od uživatele).
- [x] **Delší vlaky na nástupištích** (2026-11-16, `mhdPos` ve `web/app.html`): zastávka je střed nástupiště; na konci trasy vlak přesahuje o půl délky (rovně za konec), takže stojí celý středem u nástupiště.
- [x] **Klikací pole na hlavním nádraží** (2026-11-16): klik na budovu Hlavního nádraží ukáže odjezdy vlaků na 60 min (`showStation`), číslo koleje je odhad.
- [x] **Pop-up zastávky MHD** (2026-11-16): odjezdy mají vlastní rozložení (`dl.dep`, časy `.tm` nowrap).
- [x] **Mobil** (2026-11-16): karta s odjezdy je kompaktní (písmo .78 rem, výška max. 38 %).
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

## Poznámky z překreslení 2026-11-14
- `render.mjs` vybíral náhodný port a Chromium odmítl 5060 (ERR_UNSAFE_PORT) → čtverec 0,-1 spadl; opraveno (porty 20000–49999 s opakováním).
- GTFS: agency DPMHK se přečíslovala (A194 → A193); `mesto.json` `mhd.dopravce` je teď název „Dopravní podnik města Hradce Králové“ (mhd.py hledá i podle části názvu).
- Při chybě jednoho čtverce `postav.sh` skončí před kroky po renderu (stromy, preview, overlay, mhd, build_html): pustit je ručně, nebo celý `postav.sh render` znovu.

## Vlaky, přejezdy, NAD (2026-11-15, jen web, bez překreslení)
Podrobný plán a postup: `PLAN_vlaky.md`.
- **Vlaky z GTFS:** `nastroje/vlaky_z_gtfs.py` (osobní vlaky přes oblast mapy, 75 dní dopředu) -> `nastroje/vlaky.py` (trasy po kolejích, graf spojuje jen konce kolejí) -> `mhd.py`; v `mesto.json` je `"vlak"`.
  Pořadí po změně JŘ: `vlaky_z_gtfs.py`, `vlaky.py`, `mhd.py`, `build_html.py`, nasazení webu (stačí `pripravit_vercel.mjs` a `vercel deploy`, bez renderu).
- **Koleje HK hl.n.:** `nastroje/vlaky_koleje.py` -> `assets/vlaky_koleje.json`: E1–E12 od budovy na západ = 3a, 3, 5, 1, 2, 6, 8, 10, 12, 14, 16, 18 (potvrzeno uživatelem podle schématu Staničáře);
  pravidla (směr příjezdu > odjezdu -> četnosti kolejí) z GVD 15/16 ve hře Staničář (`Desktop/stanicar-komplet/.../HK_1-01.xml`). Směry: ONL Pardubice, OPL Praha/Chlumec, PNL Jaroměř, HSP Slezské Předměstí, VSE Všestary/Jičín.
  Jízda po levé koleji (ve stanicích mimo HK hl.n. `uzel_levy`). Číslo koleje je odhad ze staré tabulky, ne skutečné přidělení.
- **Soupravy:** model v 5. položce trasy (`routes[i][4]`) z `vlaky_z_gtfs.py` (dopravce, druh, směr, hash čísla vlaku); katalog `TRAINS` ve `web/app.html` (+ FLIRT, 163+vozy, dvojité jednotky, rychlík 5 vozů, nákladní `f_*`).
- **Nákladní vlaky:** 22 náhodných průjezdů v ~45 % dnů (`vlaky.py`, služby N0…): uhlí, kontejnery, auta Škoda, cisterny, dřevo; jedou po trasách přes hlavní koleje HK hl.n.
- **Přejezdy:** `nastroje/prejezdy_z_dat.py` (Overpass nefunguje) -> `assets/prejezdy.json` (v `.gitignore`); `prep.py` je přiřadí silnicím (34 ve městě); web: výstražník, červenobílá půlzávora (6 s po začátku výstrahy), auta čekají.
- **Výluka HK – Jaroměř (1. 11. – 12. 12. 2026):** `nastroje/vyluka_nad.py` z `assets/vyluka_odjezdy.json` (přepsané z PDF ČD, 66 spojů ze stání F, dny z obrázkových značek = odhad) -> `build/gtfs_extra/`, `mhd.py` je čte; autobusy J, R, Z jedou jen do Plotiště (okraj mapy).
- **Zbývá:** vlaky vzniklé v HK se objeví až při odjezdu; vlaky na Jaroměř jedou i za výluky (v JŘ jsou); živá poloha vlaků není (GRAPP a ČD nemají povolený strojový přístup); NAD příjezdy na stání J nejsou.

## Sloučení upstreamu (2026-11-16, větev `hradec` v `izomapa`, zatím nepřerenderováno)
Z `adamklatovsky/izomapa` main (34 commitů od základu `d37658b`) sloučeno výběrově, jen přidaná funkčnost:
- **Převzato:** semafory (auta stojí na červenou; `nastroje/semafory.py` -> `assets/semafory.json`, spojeno s naším zastavováním u přejezdů), dětská a workoutová hřiště (`nastroje/hriste.py`), vánoční vrstva (`vanoce.sh`, `assets/vanoce.json` podle `priklady/vanoce.json`), popisky okolních obcí, oprava `povrchy.py`, odkaz na sousední mapu bez „tady jsi“, render jen změněných čtverců (`nastroje/otisk.py`, v `render_ctverec.sh` spojeno s našimi časy fází).
- **Záměrně vynecháno:** chodci a cyklisté (chodci chodí po silnici; nasadit později), památky #127 (kolize s našimi modely dominant, `pam_vrsek`), přejezdy přes sousední koleje #117 (máme vlastní `XC`/`xGeo`), „opravy pro nová města“ #128 (mění zdroj dat Overture), systém doplňků #132 (jen infrastruktura).
- **Čeká:** nový `prep.py` + render dotčených čtverců (hřiště, vánoce, semafory v scéně), `assets/vanoce.json` pro vánoční strom a stánky na Velkém náměstí. Nasazení až po sebrání dalších vizuálních oprav.
- Postup přenosu: `git cherry-pick -x` po jednom commitu upstreamu v dočasném worktree; další sloučení stejně, ne `git merge origin/main` (konflikty v `web/app.html`, `prep.py`, `render_ctverec.sh`).

## Doprava z HERE (2026-11-16, kód hotový a vyzkoušený místně, nenasazeno)
- Klíč HERE je v `api_here.txt` (v `.gitignore`), jen Traffic API v7 `/flow`; kvóta Traffic ~5 000 dotazů/měsíc zdarma (ověřit v účtu HERE).
- Kód: `izomapa/nastroje/here_doprava.py`, `nahled_doprava.py`, `skripty/vercel_api/doprava.js`, `overlay.py` (přiřazení `h`), `web/app.html` (hustota, rychlost, vrstva „Zácpy“), příznak `doprava_here` v `mesto.json`. Pokyny v `izomapa/CLAUDE.md`.
- **Čeká:** (1) sběr snímků `python nastroje/here_doprava.py snimek` každých 10–15 min (plánovač úloh), po ~2 týdnech `typicka` a nasazení `site/doprava_typicka.json` = typické špičky; (2) ve Vercelu nastavit `HERE_API_KEY` (`vercel env add`) a nasadit; (3) ověřit podmínky užití dat HERE pro veřejný web (ukládání a zobrazování odvozených dat).
- Pozn.: HERE nedává počty aut; hustotu řídí `jamFactor` nad základem ze sčítání ŘSD. Jednorázové stažení neukáže, které ulice se ucpávají ve špičkách.
