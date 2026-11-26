# Izometrický Hradec Králové – stav projektu

Aktualizováno 2026-11-19. Veřejně: **https://hradeczive.vercel.app** (doména už běží jinde, neřešit).
Cíl a souřadnice jsou v [CLAUDE.md](CLAUDE.md), návod nástroje v [izomapa/CLAUDE.md](izomapa/CLAUDE.md).
Historie hotových změn a stará analýza zrychlení: [STAV_ARCHIV.md](STAV_ARCHIV.md) (nečíst, jen když je to třeba).

## Co je hotové
- **Celé město**: 25 čtverců 2,3 × 2,3 km (i, j ∈ −2…2 kolem 50.20539, 15.83009), 4 roční období + noc, MHD DPMHK podle jízdních řádů, vlaky.
- Poslední celé překreslení a nasazení 2026-11-16 večer (R2 + Vercel včetně `/api/doprava`). Nic dalšího „čekajícího na překreslení“ není kromě vánoc.
- **Dominanty** (`izomapa/assets/dominanty.json` + `custom_models.js`): 88 záznamů, z toho vlastní modely (Bílá věž, katedrála, Gymnázium Tyla, Hučák, Ulrichovo nám.,
  aréna, lávka u Aldisu, most Šrámkův, estakáda I/31, Mileta, nákupní centra `oc`) a ostatní jen popisem `spec`.
- **Obchody a značky** (`assets/znacky.json`, 47 značek), pumpy, svislé dopravní značky (z WFS magistrátu), semafory, hřiště.
- **Data magistrátu** (tabulka níže), **Graphify** znalostní graf v `graphify-out/`.
- **Nasazení**: Vercel `frenkees-projects/hradeczive`, dlaždice v R2 (bucket `izohradec`, veřejně `https://pub-55cbad9c2db745779e46b9eac5658b47.r2.dev`).
- **Doprava**: sběr TomTom každých 10 min, HERE střídavě (20 min), sloučený `live.json`.
- **Rozšíření 2026-11-16** (j = −2, i = −2): `skripty/rozsirit_mapu.sh`, záloha původních dat `izomapa/build/zaloha_rozsireni/`.
  Nové čtverce nemají živou dopravu (HERE a TomTom `BBOX` jsou jen původní město) ani semafory.
  Render občas spadne na přechodném `ERR_CONNECTION_RESET`, stačí pustit znovu.

## Opravy hlášení #45–#53 a systém doplňků (2026-11-19)
- Hlášení #45–#48, #50, #53 opravena v `skripty/opravy_hlaseni.py` (podrobně `REPORT_hlaseni.md`); #51 (most) nereprodukováno, čeká na upřesnění.
  V `izomapa/prep.py` má ruční výška `h` z `upresneni.json` přednost před laserem. Čtverce 1,-1, 1,0, -1,0 (a 0,0, 0,-1) **překresleny a nasazeny 2026-11-19**.
- **Systém doplňků** přenesen z upstreamu bez merge: `izomapa/plugins.py`, volání v `overlay.py` (`overlay.json["doplnky"]`), API `window.Izomapa` ve `web/app.html`
  (vrstvy `world`/`sky`/`top`, `onMapClick`, `getUiSlot`…, navíc `isOccluded`). Formát doplňku podle upstream `doplnky/letiste`.

## Jak mapu postavit a nasadit
Vše z `izomapa/` v Git Bash, Python `.venv/Scripts/python` s `PYTHONUTF8=1`.
1. (volitelně) nová data magistrátu: `.venv/Scripts/python ../skripty/mmhk_pasport.py`
2. scény, render, dlaždice, web: `sh ./postav.sh render` (celé město ~35 min; přeskakuje čtverce beze změny)
3. rychlý náhled místa: `.venv/Scripts/python ../skripty/nahled_mista.py <lat> <lon> out.png [season=lights]`
4. nasazení (z `izohradec/`):
   - `node skripty/nahrat_dlazdice_r2.mjs izohradec` (jen změněné dlaždice, ~1 MB/s)
   - `node skripty/pripravit_vercel.mjs https://pub-55cbad9c2db745779e46b9eac5658b47.r2.dev`
   - `cd nasazeni/vercel && vercel deploy --prod --yes`
- Při chybě jednoho čtverce `postav.sh` skončí před kroky po renderu (stromy, preview, overlay, mhd, build_html): pustit ručně, nebo celé znovu.
- Jen web (vlaky, MHD, doprava) nepotřebuje render: `mhd.py`, `build_html.py`, nasazení.
- Přírůstkové `dzi` záměrně NEdělat: paleta se počítá z celého obrazu, po každé změně by se stejně změnila všem dlaždicím.

## Data Magistrátu města HK
`skripty/mmhk_pasport.py` (z `izomapa/`) stáhne do `izomapa/assets/mmhk.json` a `mmhk_znaceni/`:

| co | zdroj | použití v mapě |
|---|---|---|
| plochy vozovek, chodníků, parkoviště | pasport komunikací (WFS `pakom`) | skutečné tvary ulic, obrubníky |
| vodorovné značení | WMS `pakom` | přechody, čáry, stání |
| řady parkovacích stání | pasport komunikací | auta na stáních |
| stromy, zeleň, parky | pasport zeleně (WFS `pazel-sec`) | 50 tis. stromů, trávníky, záhony |
| výška stromů | DMP 1G (`izomapa/build/dmp/*.laz`) | výška u ~50 % stromů |
| lampy | WFS `pvohk` | 13 tis. lamp |
| opěrné zdi, zábradlí | DTMM (ArcGIS REST) | nábřežní zdi, zábradlí |

Hook `izomapa/assets/custom_prep.py` (vypnout `IZO_MMHK=0`). Zdroj je v patičce (`dalsi_zdroje` v `izomapa/mesto.json`).
Geoportál po ~1 500 rychlých dotazech odmítá spojení, stažené části jsou v cache `izomapa/build/mmhk_cache/` (`--bez-site` = jen přepočet).
Otevřená data města: https://web.mmhk.cz/opendata/

## Přestavby, které pasport magistrátu ještě nemá
`assets/prestavby.json` = zóny s aktuálním OSM (`skripty/prestavby_osm.py`). V zóně se místo pasportu kreslí vozovky podle OSM.
- **Křižovatka Mileta** (model `mileta_podchody`, 4 podchody): ověřit proti skutečnosti / fotkám.
- Kandidát: kruhový objezd Komenského (50.2078, 15.8325) – přidat zónu do `prestavby.json`.

## Malšovická aréna a zápasy FC Hradec Králové
- Model v dlaždicích + animovaná vrstva `assets/custom_web.js` (noční LED pás, lízátka při zápase, skóre, rozpis).
- Data: Vercel funkce `/api/zapasy` (`skripty/vercel_api/zapasy.js`, rozpis z fchk.cz, skóre z onlajny.com), záloha `zapasy.json` (`node skripty/zapasy.mjs`).
  Parser závisí na HTML fchk.cz. Podmínky užití dat nejsou známé – zeptat se klubu, případně uvést zdroj v patičce.
- Ještě není: hráči na hřišti, fanoušci na tribunách, zimní stadion.

## Trasy MHD
`mhd.py` počítá trasy po silnicích (`road_route.py`) přednostně po referenčních trasách `assets/mhd_trasy_ref.json` (`skripty/mhd_trasy_ref.py`), ruční čáry
`assets/mhd_trasy_rucne.json`. Kvalita úseků (`kvalita` v mhd.json): jistý / jen OSM / jen město / rozpor / nejistý / mimo mapu.
Kontrola: `python ../skripty/mhd_trasy_kontrola.py` -> `izomapa/preview/mhd_trasy/index.html`. Zbývá projít nejisté úseky (nejvíc linky 15, 10, 19, 27, 9 a varianty Š, R).
GTFS agency DPMHK se přečíslovala (A194 → A193), `mhd.dopravce` v `mesto.json` je název.

## Vlaky, přejezdy, NAD
Podrobně `PLAN_vlaky.md`. Pořadí po změně JŘ: `nastroje/vlaky_z_gtfs.py`, `vlaky.py`, `mhd.py`, `build_html.py`, nasazení webu (bez renderu).
- Koleje HK hl.n. `nastroje/vlaky_koleje.py` -> `assets/vlaky_koleje.json`; číslo koleje je odhad, ne skutečné přidělení.
- Soupravy: katalog `TRAINS` ve `web/app.html`; nákladní vlaky náhodně (`vlaky.py`).
- Přejezdy `nastroje/prejezdy_z_dat.py` -> `assets/prejezdy.json` (v `.gitignore`).
- Výluka HK – Jaroměř (1. 11. – 12. 12. 2026): `nastroje/vyluka_nad.py` z `assets/vyluka_odjezdy.json`.
- Zbývá: vlaky vzniklé v HK se objeví až při odjezdu; živá poloha vlaků není; NAD příjezdy na stání J nejsou.

## Příběhy míst a Wikipedie (rozpracováno)
Noční katalog: `skripty/noc/noc_hlidac.py` -> `izomapa/build/noc/` (`katalog.json`, `index.html`, **`mista_koncepty.json` = 177 konceptů, `KONCEPT: true`**,
každý má `zdroj` na cs Wikipedii). Koncepty vznikly přes qwen3:14b s ověřením čísel a citací proti zdroji. Formát cíle: `izomapa/mista.json`
`[{"nazev","lat","lon","text"}]` (viz `izomapa/priklady/mista.json`), jen ověřená fakta.
- [ ] Doplnit informace z Wikipedie ke všem dominantám a koncepty zrevidovat. Dohodnuto: lokální Ollama; k dispozici `qwen3-coder:30b`, `qwen2.5-coder:14b`,
      `qwen3:14b` (psaní prózy v češtině zvládá lépe než coder modely – při revizi porovnat na vzorku). Každý text ověřit proti zdroji, jinak zahodit.

## Plachta: sídliště podle nerealizované studie (přepínač ve Vrstvách, nasazeno 2026-11-17, označeno „experimentální“)
- Podklady (kořen repa, nejsou v gitu): `studie.jpg` (maketa, 19 000 obyv., konec 70.–80. let), `studie2.jpg` (výkres Stavoprojekt IX/1987, ing. arch. J. Bahník,
  1:1000, „UPJ-Z1 návrh“, 1. etapa ~4 600 obyv., domy A11–A32 s počty B.J./OB), `studie3.jpg` (řez: dům A22 8 podlaží, A14 7). Zdroj snímku makety: web naplachte.cz/historie
  (poděkování PhDr. L. Jacksonovi); autor makety neznámý. Uvést zdroj v patičce před zveřejněním.
- `skripty/plachta_studie.py` (z `izomapa/`): z `studie4.jpg` (maketa s červeně obkreslenými domy a modře silnicemi od uživatele, 2026-11-17) vyřízne obrysy domů (bloky tvaru C) a silnice -> `izomapa/assets/plachta_studie.json`.
  Od 2026-11-17 večer i `studie_colored.png` (barevná maketa, oříznutá o ~37 px výš než maketa: registrace `SX,SY,DX,DY` v skriptu): tvary domů = šedé střechy v okolí červených tahů,
  voda, kurty vedle oválu; měřítko 1,25 m/px, ~18 tis. obyv. Vynecháno (leží na dnešní zástavbě): západní parkoviště, jižní blok, škola. Nasazeno 2026-11-17.
  Okolí (`skripty/plachta_okoli.py`, ze kostry modrých silnic): chodníky, čárkovaná osa, přechody, čáry stání, ~400 lamp (v noci svítí), lavičky, koše, 2 zastávky, značky Dej přednost / Děti / Parkoviště,
  auta na parkovištích; `prep.py` v zóně vypouští dnešní lesní cesty (`IZO_PLACHTA`). Nasazeno 2026-11-17.
  Domyšleno: parkoviště u bloků, 4 parkovací domy, pískoviště + dětské hřiště ve dvoře každého bloku, uliční stromořadí, ovál. Obytných domů 22, ~15 tis. obyvatel (28 m²/os.).
  Zakotvení na rybník u silnice (50.18750, 15.85276), měřítko 1,3 m/px, natočení 11° (odhad, ověřit proti přesnému skenu). Podlaží max. 8 (podle řezu).
- `skripty/plachta.sh` (z `izomapa/`): `IZO_PLACHTA=1 prep.py` čtverce 1,-1 -> `build/c1_-1_plachta`, render jen ~14 dlaždic v zóně, vrstvy `plachta_summer/autumn/winter/spring/lights` (dzi.py je bere jako řídké),
  `build_html.py`. Trvá ~2 min. Web: checkbox „Plachta: sídliště podle studie“ (`web/app.html`, `applyExtras`), noční světla zvlášť.
- **Čeká:** (verze s domy C, silnicemi a hřišti nasazena 2026-11-17) až bude sken výkresu 1:1000, přesně obkreslit etapu Z1 (skutečné půdorysy, počty podlaží) a opravit zakotvení;
  doplnit uliční síť a jezero z makety; zdroj do patičky.

## Hlášení z mapy (GitHub issues frenkees/hradeczive, zpracováno 2026-11-18, lokálně vyrenderováno, NEnasazeno)
- `skripty/opravy_hlaseni.py` (z `izomapa/`) zapisuje opravy budov do `assets/upresneni.json` klíč `b` (nové klíče v `prep.py`: `name`, `cls_cz`, `cls`, `fl`, `skryt`, `sachta`), kolonii #6 a stromy #5 (`oblasti.json`).
  Přístřešky zastávek ve vozovce se v `prep.py` posouvají na chodník (#33). Názvy podle návštěvníků jsou neověřené.
- Hotovo: #7 #9 #10 #11 #15–#20 #34 #38 #39 #41 (názvy), #8 (patra Orlická kotlina), #12 (šachty), #21 #22, #23 #24 (zbořené), #26 #27 #35 (13 pater), #36 (cihla, měděná střecha), #40, #43 (bílé novostavby), #5, #6, #33.
  #2–#4 byly opraveny dřív. Otevřené: #13 jez, #14 Burger King, #25 fontána, #28–#32 (výška nejasná), #37 zastávky Riegrovo nám., #42 („futrum“), #44 (chybí silnice v Meruňkové, v OSM není).

## Doprava (TomTom + HERE)
Kód `izomapa/nastroje/here_doprava.py`, `skripty/vercel_api/doprava.js`, příznak `doprava_here` v `mesto.json`; klíče v `api_here.txt` / `tomtomapi.txt` (v `.gitignore`).
HERE nedává počty aut, hustotu řídí `jamFactor` nad základem ze sčítání ŘSD. Po ~2 týdnech sběru `typicka` a nasazení `site/doprava_typicka.json`.
Ověřit podmínky HERE (veřejný web, ukládání odvozených dat, uvedení zdroje; kvóta ~2 500 dotazů měsíčně).

## Otevřené úkoly
- [ ] **Nové čtverce**: rozšířit `BBOX` dopravy (HERE, TomTom) a semafory na celou mapu 25 čtverců.
- [ ] **Pasport místy zastaralý** (např. chybí kruhový objezd Komenského) – projít mapu proti ortofotu.
- [ ] **Pull request autorovi izomapy**: `dalsi_zdroje`, jednosměrky v `road_route.py`, opravy mostů, silnice ve výstavbě, `IZOMAPA_PLUGINS`, opravy pro Windows.
      Větev `hradec` míchá obecné opravy s městskými daty – rozdělit.
- [ ] **Před zveřejněním** projít mapu a příběhy míst proti skutečnosti.
- [ ] Ověřit na místě: délku a polohu schodů u lávky Aldis, rozměry estakády I/31, napárování dominant `spec` na správné budovy.
- [ ] Vánoční náměstí (později): `assets/vanoce.json`, `vanoce.sh`, podle webu vanocevhradci a fotek uživatele.
- Zrychlení (otevřené, podle přínosu): jeden Chromium na čtverec místo 5 startů; cache kroků `prep` podle hashe vstupů; `prep.py` vektorizace; měření fází `cProfile`.
  Kód: explicitní rozhraní místo `exec` do globálů v `custom_prep.py`; regresní test obrazem; stavba do pracovní složky; `render_all.sh` má `.venv/bin/python`; `requirements.txt`.

## Nápady do budoucna
- Zákaz parkování aut na kruhových objezdech a křižovatkách (nejspíš zbytečná složitost).
- Autobusový terminál MHD: autobusy v řadách před terminálem.
- Chodci a cyklisté (z upstreamu záměrně vynecháno, chodí po silnici).
- Zimní stadion: pop-up s dalšími zápasy.
- **Vrstva „Události“** (výjezdy HZS KHK, nehody, výstrahy): plán a ověřené rozhraní v [PLAN_udalosti.md](PLAN_udalosti.md).
- Přehled otevřených hlášení z mapy: [REPORT_hlaseni.md](REPORT_hlaseni.md) (#51 čeká na upřesnění, #52 na fotky). Doplněk „Doprava“ (generická auta) byl zkoušen a 2026-11-19 zrušen, mapa má původní auta.
- **Fotografie budov od lidí**: klik na budovu -> nahrání fotek po registraci e-mailem; limity 25 MB, 4 fotky na budovu, 20 fotek denně na uživatele;
  souhlas s bezplatným použitím; potřebuje Cloudflare Worker + R2 + D1 (jako `izomapa/hlaseni/`), moderaci a GDPR.

## Git
- `izohradec/` – projektový repozitář (skripty, dokumentace; bez tajemství, dlaždic a stažených dat), záloha **frenkees/hradeczive** (remote `origin`, větev `main`).
- `izomapa/` – klon `adamklatovsky/izomapa`; vlastní úpravy na větvi **`hradec`** (městské soubory přidané přes `git add -f`). Záloha **frenkees/hradeczive-izomapa**
  (remote `zaloha`; `git push` jde tam). Remote `origin` = upstream autora, tam nepushovat. Fork je veřejný (AGPL).
- Další sloučení upstreamu: `git cherry-pick -x` po jednom commitu v dočasném worktree, ne `git merge origin/main`.
- Mimo git: `izomapa/build`, `data*`, `site`, `assets/mmhk.json`, `assets/mmhk_znaceni/`, `nasazeni/vercel`. Tajemství jen lokálně: `nasazeni/tajne.env`, `.vercel/`.

## Hlášení s fotkou a e-mailem (2026-11-20, nasazeno)
- Formulář (`izomapa/web/app.html`) umí přiložit fotku (zmenšení v prohlížeči na 1600 px) a po odeslání vybídne k fotce a e-mailu pro poděkování a zprávu o stavu.
- `skripty/vercel_api/report.js`: fotky a e-maily jdou SOUKROMĚ do Vercel Blob (privátní store, `BLOB_READ_WRITE_TOKEN`), do veřejného issue jen věta „fotka přiložena / kontakt uložen“. Doplnění po odeslání ověřuje podpis (HMAC čísla issue). E-mail s poděkováním posílá Resend (`RESEND_API_KEY`, `MAIL_FROM`), bez nich se e-mail jen uloží.
- `skripty/hlaseni_soukrome.mjs`: seznam / stažení fotek (do `landmarks_ref/`, mimo git) / zpráva o stavu autorovi.
- Blob store `hradeczive-hlaseni-2` je propojen s projektem (BLOB_READ_WRITE_TOKEN); prázdný duplicitní `hradeczive-hlaseni` lze smazat v dashboardu. Volitelně nastavit Resend; `pripravit_vercel.mjs` už přidává závislost `@vercel/blob`.
- Čtverce 0,1 (#6), -1,1 (#43), -1,0 (#5) překresleny a nasazeny 2026-11-20.
- Čtverec 0,1 znovu 2026-11-22 (#54, #55 Kyjevská). Fotky z hlášení: `node skripty/hlaseni_soukrome.mjs foto <č>` (potřebuje `@vercel/blob` a token z `vercel env pull`).

## Sync s upstreamem a doplňky (2026-11-24, nasazeno na ostro)
- `izomapa/` je fork `frenkees/izomapa` (větev `hradec`, remote `fork`; `origin` = autor `adamklatovsky/izomapa`, `zaloha` = záloha). Aktuální verze je v `IZOMAPA_VERZE`.
- Upstream se sleduje pravidelným `git merge origin/main` (už ne cherry-pick). Naše věci jsou doplňky v `izomapa/doplnky/<id>/` (hlaseni, hk_zapasy, odjezdova_tabule, doprava_here, letiste), konfigurace v `assets/doplnky/<id>.json` (gitignorováno, `git add -f`), HK specifika v `assets/custom_prep.py`. Web se skládá z `web/app.html` + `web/css` + `web/js/NN-*.js` (`web/sestav.py`).
- Přijato od autora: chodci a cyklisté (zapnuti), pole, parkoviště, letiště (ilustrační provoz, uvedeno v patičce). Celá mapa (25 čtverců) přerenderována.
- Dlaždice jsou v R2 pod prefixem `test/` (produkce na ně míří: `pripravit_vercel.mjs <r2 url>/test`); původní `tiles/` zůstaly pro rollback. Upload: `nahrat_dlazdice_r2.mjs <bucket> --prefix test`.
- Podrobnosti: `PLAN_upstream_sync.md`. Pozor: preview deploye jsou za přihlášením a na nich mapa trhala, ostrá je plynulá.
- Čeká: PR autorovi (jen se souhlasem uživatele, malé, po tématech), smazat prázdný Blob store `hradeczive-hlaseni`, rotovat Resend klíč.

## MHD živě a oprava mostů (2026-11-24, hotovo lokálně, čeká na večerní přerender a nasazení)
- Doplněk `izomapa/doplnky/mhd_live/` + Vercel funkce `skripty/vercel_api/mhd_live.js` (zdroj `dpmhk.qrbus.me/index/getAllRtdVehicles`, záloha `mapa.fcen.cz/api/vehicle_data`; jména řidičů a ostatní údaje se zahazují na serveru). Klient páruje vozidlo se spojem jízdního řádu (linka + poloha + směr při hlášeném zpoždění, doladění ±90 s) a spoj vykreslí na trase o zpoždění zpět (`Izomapa.setMhdDelayHook`, změna max 15 s/s). Přepínač „Všechny spoje MHD“ ve Vrstvách: pixelové špendlíky s číslem linky na odzoomované mapě (zelený včas, žlutý 1 min, oranžový 2 min, červený 3+ min, šedý bez živých dat). Konfigurace `assets/doplnky/mhd_live.json` (`git add -f`). Zdroj uveden v patičce.
- **Oprava skákání autobusů (2026-11-24, lokálně, nenasazeno):** příčiny: skokově se měnící zpoždění (limit 15 s/s je v praxi skok stovek m), duplicitní záznamy téhož vozu ve zdroji (starý „duch“), pole `l` je pražský čas s příponou „Z“ (server stáří nefiltroval) a úseky s nulovým časem v profilu spojů (`mhd.py`, 19 % spojů). Nově doháněcí model: cíl = průmět GPS na trasu spoje + dojetí o stáří záznamu, zobrazená poloha se plynule blíží a nikdy necouvá (háček jádra `setMhdElHook`, poloha každý snímek); server posílá `ag` (stáří) a `sp` (rychlost) a dedupuje; poll 15 s. Zbývá: nasadit Vercel funkci i web (`build_html.py`), ověřit na mapě; známé drobnosti z revize (karta spoje vs. barva špendlíku, extrapolace přes zastávky, výpadek obou zdrojů).
- Mosty: pilíře se nestaví nad cestou pod mostovkou (`prep.py` `no_pier`, `render.html`; hlášení #51).
- Noc: `skripty/noc/noc_objekt.py` (podklady k jedné dominantě přes Ollamu), úloha Plánovače `izohradec_kostel_qwen` (kostel Božského Srdce Páně, #52, výstup `landmarks_ref/bozske_srdce_pane/info.md`) a `izohradec_rerender` (19:00, `build/rerender_all.sh`). Po přerenderu: prohlédnout, nasadit (testovací deploy, pak ostrý).

## Letadla: model, světla, linka, databáze typů (2026-11-24, nasazeno)
- `izomapa/web/js/87-letadla.js` (+ `87-letadla-typy.js`): model letadel 1,5× (vrtulník LZS 1,9×), poziční světla podle směru pohledu kamery (červené levé křídlo, zelené pravé, bílé zadní; strany ověřeno revizí), bílý strobo (dvojitý záblesk 1,2 s) a červený maják i ve dne, tenká svislá linka od letadla k šedému kruhu (14 m) na terénu.
- Typ letadla z ICAO Doc 8643: `nastroje/letadla_typy.py` (obnova seznamu, výstup `web/js/87-letadla-typy.js`); ruční tabulka `AC_TABLE` má přednost, neznámý typ se odhadne podle kategorie ADS-B. Známá drobnost: u `EC35` vybere název „HE-26“.
- `skripty/vercel_api/flights.js`: záloha adsb.fi, když adsb.lol selže (adsb.lol blokuje domácí IP uživatele, produkční Vercel funguje; airplanes.live a adsb.one vrací 403).
- Web je nasazen (hradeczive.cz), `IZOMAPA_VERZE` = `3a983a3`.
- **PR autorovi (adamklatovsky/izomapa), všechny otevřené, nikdo je zatím neposoudil:** #162 render a blokované porty, #163 `novy_mesto.py --bbox/--stred` (nálezy Codexu opraveny), #164 `render_par.sh` vlákna (nálezy opraveny), #165 databáze typů ICAO, #166 světla podle směru, #167 linka s kruhem (větve `pr/letadla-*` ve forku). Revize Opusem proběhla u #165–167. Pomocné worktrees ve scratchpadu smazat, až budou PR přijaty/zavřeny.
- PR se špendlíky MHD (doplněk bez našeho API) se nedělá, uživatel zamítl.

## Světlo lamp a údržba silnic (2026-11-24, nasazeno)
- **Lampy bez přerenderu:** doplněk `izomapa/doplnky/lampy_svetla` (hook z `build/**/info_src.json` → `site/doplnky/lampy_svetla/lampy.json`, 12 719 lamp, typ 0 sodík = vedlejší ulice, 1 LED = třída silnice motorway…tertiary). Klient v noci kreslí záři (světelný kruh na zemi + svítidlo, aditivně), jen při přiblížení a v záběru, za budovou nesvítí. Ladění: `TYPY` v `lampy_svetla.js` (barvy, poloměr, intenzita), seznam tříd `hlavni` v `assets/doplnky/lampy_svetla.json`. Zapečené světlo lamp v dlaždicích `lights` zůstává (obě se sčítají).
- **Údržba silnic:** doplněk `udrzba_khk` + `skripty/vercel_api/udrzba_khk.js` (zdroj: veřejné rozhraní SÚS KHK `protank-dynamics.cz/SUSHK-AP`, 4 pásma stáří: do 30 min, 30–60 min, 1–3 h, 3–12 h; cache 5 min, výřez HK). Přepínač „Údržba silnic“ ve Vrstvách, plovoucí legenda, „Ztlumit mapu“ (schematický režim). Mimo zimu bývá prázdná. Zdroj uveden v patičce (`mesto.json` `dalsi_zdroje`). Písemný souhlas SÚS KHK nemáme (uživatel zvolil nasadit rovnou s rozumnou frekvencí).
- **Pozor:** produkční dlaždice jsou v R2 pod prefixem `test/` (`pripravit_vercel.mjs <r2 url>/test`). Dnešní první nasazení letadel proběhla omylem s adresou bez `/test`, tj. na starý rollback prefix; od nasazení lamp je to opraveno. Nový render celé mapy (25 čtverců, `-2,-2` dorenderován zvlášť) nahrán do R2.

## Sync s upstreamem 2026-11-26 (nasazeno)
- Autor přijal PR #162–#167 a přidal #168 (zrychlení kreslení, cache čísel linek, autobusy na silnici z GTFS; v HK bez účinku, GTFS DPMHK nemá `shapes.txt`) a větev `dotazy-za-sebe` (User-Agent, pravidlo v CLAUDE.md). Vše sloučeno do `hradec` (`0b50692`), `IZOMAPA_VERZE` = `0b50692`.
- Při sloučení ponechán náš `87-letadla.js` (LZS, historie, karta); cache štítků `cisloLinky` doplněna o barvu trolejbusu (typ 11). Test `test_plugins_core` (node suite) selhává už před sloučením.
- Web nasazen s `mhd.json` z čerstvého GTFS, dlaždice beze změny (R2 prefix `test/`).

