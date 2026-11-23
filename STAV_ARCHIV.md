# Archiv stavu projektu (historie, nečte se automaticky)

Přesunuto ze STAV_PROJEKTU.md 2026-11-17. Vše tu je už hotové a nasazené, nebo je to analýza z doby, kdy se plánovalo.

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


## Poznámky z překreslení 2026-11-14
- `render.mjs` vybíral náhodný port a Chromium odmítl 5060 (ERR_UNSAFE_PORT) → čtverec 0,-1 spadl; opraveno (porty 20000–49999 s opakováním).
- GTFS: agency DPMHK se přečíslovala (A194 → A193); `mesto.json` `mhd.dopravce` je teď název „Dopravní podnik města Hradce Králové“ (mhd.py hledá i podle části názvu).
- Při chybě jednoho čtverce `postav.sh` skončí před kroky po renderu (stromy, preview, overlay, mhd, build_html): pustit je ručně, nebo celý `postav.sh render` znovu.


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
