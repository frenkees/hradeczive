# Plán: vlaky podle jízdního řádu, nástupiště, přejezdy, nákladní vlaky, NAD

Rozsah: celá mapa (HK hl.n., HK zastávka, Slezské Předměstí, Předměřice n. L., Kukleny, odbočky). Stav k 2026-11-15; plán, ještě nic z toho není hotové.

## Co už generátor umí (nezačínat od nuly)
- `nastroje/vlaky_vyber.py` + `nastroje/vlaky.py`: osobní vlaky z celostátního JŘ (CZPTT XML, portal.cisjr.cz) -> `vlaky_mhd.json`, `mhd.py` je přidá k MHD (volba `"vlak"` a `"vlaky_stanice"` v `mesto.json`).
- `web/app.html`: katalog modelů `TRAINS` (regiopanter, regioshark, regionova, vuz810, cityelefant, rychlik), pohyb vlaků po tvarech tras.
- `nastroje/prejezdy.py`: přejezdy z OSM -> `assets/prejezdy.json`; web zavírá přejezd ~25 s před vlakem a auta čekají ve frontě, výstražníky blikají.
- Dnes je to všechno VYPNUTÉ (v `mesto.json` není `"vlak"`, `assets/prejezdy.json` neexistuje).

## Zdroje dat
| Co | Zdroj | Poznámka |
|---|---|---|
| Časy, směr, další stanice | GTFS CIS JŘ (už máme, `build/gtfs.zip`, 2 616 vlaků přes SC822) nebo CZPTT | GTFS nemá `shapes.txt` pro vlaky, trasu stavíme po kolejích |
| Čísla kolejí a topologie stanic | Staničář: `Desktop/stanicar-komplet/.../Stanice/HK_1-01.xml` (schéma HK hl.n. s čísly kolejí, vjezdy OPL, ONL, 51-59 Harfa, VSE, PNL = Předměřice n. L., HSP) + GVD 15/16 v téže XML (475 vlaků s typem, délkou, hmotností) | jen fakta o kolejích; GVD je z 2015/16, je to typické obsazení, ne dnešní |
| Skutečné polohy vlaků pro kontrolu | research agent (běží), výsledek viz níže | |
| Souprava (typ, počet vozů) | typ z druhu vlaku a dopravce (ČD Os = RegioShark/Regionova/RegioPanter, R/Ex = lokomotiva + vozy, LEO, RegioJet atd.), délka z GVD, kde existuje | skutečné sestavy v JŘ nejsou |
| NAD / dálkové autobusy za výluku Jaroměř | research agent (běží); GTFS z 2026-11 NAD přes SC822 nemá | |

## Fáze
1. **Zapnout existující pipeline a podívat se.** `"vlak"` + `vlaky_stanice`, JR zip nebo GTFS; zjistit, jak vlaky jezdí po grafu kolejí, kde to nesedí (výhybky, vjezdy z okraje mapy, odbočky).
2. **Kolejový graf stanic + čísla kolejí.** Z OSM/Overture koleje a hrany nástupišť; mapování na schéma Staničáře (kolej číslo -> hrana), tabulka `assets/vlaky_nastupiste.json` (linka/směr/typ -> kolej), kontrola kolizí obsazení kolejí.
3. **Směr příjezdu a odjezdu.** Vjezd z okraje mapy podle předchozí a následující stanice (Pardubice / Praha-Chlumec / Jaroměř-Trutnov / Letohrad-Choceň / Liberec-Turnov přes Všestary), otočky a průjezdy.
4. **Vzhled souprav.** Typ vlaku z druhu + dopravce + délky; nové modely do `TRAINS` (lokomotivy 163/362/380/1216, vozy Bmz/Bdmpee, jednotky 650/660/844, RegioJet, LEO). Počet vozů z GVD / druhu.
5. **Přejezdy.** Zapnout `prejezdy.json`, dokreslit vzhled podle skutečnosti (závory půlkové/celé, počet a poloha, výstražníky, štítky), ověřit, že auta nejedou přes zavřený přejezd ani v křižovatce za ním, a že se přejezd zavírá podle skutečného času vlaku.
6. **Nákladní vlaky (náhodné průjezdy).** Uhelné (vozy Eaos / Fals), kontejnerové, autovlaky Škoda (Laeks / Hbbills), cisternové, dřevo; lokomotivy 163/181/183/363/742/753; náhodně podle hustoty z GVD, ne podle skutečného JŘ.
7. **NAD / dálkové autobusy od nádražní budovy** podle nalezených odjezdů za výluku.
8. **Kontrola proti živým polohám**, pokud agent najde použitelný veřejný zdroj bez porušení podmínek.

Pořadí: 1 -> 5 (přejezdy jsou levné a jsou na viditelné cestě) -> 2, 3 -> 4 -> 6 -> 7 -> 8.
