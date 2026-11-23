# Report: nevyřízená hlášení z mapy (stav k 2026-11-19)

Zdroj: GitHub issues `frenkees/hradeczive` (otevřená). Odkaz „Pozice“ otevře mapu na místě hlášení (`https://hradeczive.cz/#@lat,lon,zoom`).
Stav: ✅ opraveno · 🟡 opraveno částečně · 🔧 opraveno lokálně, čeká na nasazení · ⏳ čeká na data/rozhodnutí · 🆕 nové, netříděno

## ✅ Nasazeno 2026-11-19 a issues smazány (#13, #49, #25, #44)

| # | Hlášení | Pozice | Co je hotovo |
|---|---|---|---|
| 13 | „Chybí jez“ | [50.21073, 15.86065](https://hradeczive.cz/#@50.21073,15.86065,0.11) | Malšovický jez z OSM (way 36887106), betonový pás přes řeku, 1,3 m |
| 49 | „Vůbec tady není zobrazený jez“ (MVE HK III) | [50.21100, 15.86047](https://hradeczive.cz/#@50.21100,15.86047,0.28) | Duplicita #13 – řeší stejná oprava |
| 25 | „Před muzeem chybí fontána“ | [50.21169, 15.83047](https://hradeczive.cz/#@50.21169,15.83047,0.27) | Bazének + sloupek na místě; neodpovídá tvarem Kotěrově kašně |
| 44 | „Silnice v Meruňkové“ | [50.22192, 15.80224](https://hradeczive.cz/#@50.22192,15.80224,0.15) | Nová čtvrť: 47 cest z aktuálního OSM (Meruňková, Jabloňová, Drtinova, Ovocnářská) |

## 🟡 Částečně opraveno (nasazeno), zbytek čeká

| # | Hlášení | Pozice | Hotovo | Čeká na |
|---|---|---|---|---|
| 5 | Bezručova 555: stromy před domem | [50.20053, 15.81229](https://hradeczive.cz/#@50.20053,15.81229,0.22) | ❌ Zahozeno (bez podkladů); dřívější odhad stromů odstraněn z `oblasti.json`, projeví se při příštím překreslení čtverce -1,0; issue lze zavřít |
| 6 | „je tu zahrádkářská kolonie“ | [50.22477, 15.84482](https://hradeczive.cz/#@50.22477,15.84482,0.38) | 🔧 Kolonie je dlouhý pás podél kanálu (ortofoto): obrys zvětšen na 2 části, 40 chatek a 40 stromů; čeká na překreslení čtverce 0,1 |
| 8 | „Barák v Orlické kotlině max. 4 patra, Švendova 3“ | [50.21224, 15.84407](https://hradeczive.cz/#@50.21224,15.84407,0.06) | Orlická kotlina 4 podlaží, Švendova 3 podlaží (11 m) | Střechy/tvary jednotlivých domů – bez podkladů |
| 36 | „Muzeum nemá vypadat jako panelák“ | [50.21128, 15.82860](https://hradeczive.cz/#@50.21128,15.82860,0.30) | Barvy | Skutečný tvar (Kotěrovo muzeum): fotky/výkresy nebo ruční model |
| 43 | „domy nemají normální barvy“ (Meruňková 817) | [50.22198, 15.80221](https://hradeczive.cz/#@50.22198,15.80221,0.15) | 🔧 Podle panoramatu Mapy.com: pískově žluté dvoupodlažní řadové domky, ploché střechy, šedé garáže (dřív bílé); čeká na překreslení čtverce -1,1 |

## ⏳ Čeká na data nebo rozhodnutí

| # | Hlášení | Pozice | Problém | Co potřebuji |
|---|---|---|---|---|
| 14 | „Chybí Burgerking“ | [50.21790, 15.82970](https://hradeczive.cz/#@50.21790,15.82970,0.06) | OSM má BK na Brněnské, hlášení ukazuje jinam | Přesná adresa; zda jde o stavbu, nebo jen o značku/pin |
| 28 | „nízké“ (Smetanovo nábř. 1186) | [50.21824, 15.82572](https://hradeczive.cz/#@50.21824,15.82572,0.17) | OSM i laser dávají 9 pater | Skutečný počet pater |
| 29 | „nízké“ (1187) | [50.21790, 15.82578](https://hradeczive.cz/#@50.21790,15.82578,0.17) | totéž | totéž |
| 30 | „nízké“ (1188) | [50.21773, 15.82581](https://hradeczive.cz/#@50.21798,15.82587,0.17) | totéž | totéž |
| 31 | „nízké“ (1189) | [50.21756, 15.82583](https://hradeczive.cz/#@50.21798,15.82587,0.17) | totéž | totéž |
| 32 | „plochá střecha“ (1190) | [50.21742, 15.82585](https://hradeczive.cz/#@50.21776,15.82600,0.17) | střecha vs. data | Potvrdit plochou střechu + počet pater |
| 37 | „Zastávky nejsou na správném místě“ | [50.20787, 15.83275](https://hradeczive.cz/#@50.20787,15.83275,0.05) | GTFS má jednu souřadnici na název; OSM jen 3 stojany „Zimní stadion“ | Které zastávky a kde skutečně jsou |
| 42 | „futrum“ (Sklad, Na Brně 1955) | [50.19968, 15.83046](https://hradeczive.cz/#@50.19968,15.83046,0.50) | Nejasné; pozice hlášení a pohledu se liší | Upřesnění, co je špatně |

## ✅ Opraveno a nasazeno 2026-11-19 (překresleny čtverce 1,-1, 1,0, -1,0, 0,0, 0,-1) – issues zatím ponechány k ověření

| # | Hlášení | Pozice | Co je uděláno | Co zbývá |
|---|---|---|---|---|
| 45 | „Nová přístavba hotelu AWAM“ | [50.19211, 15.84974](https://hradeczive.cz/#@50.19211,15.84974,0.16) | Plochá bílá budova u bodu (ortofoto) pojmenována „Hotel AWAM (nová přístavba)“, druh hotel | Skutečná výška/barva (foto) |
| 46 | Sklad, Brněnská 207 | [50.19211, 15.84974](https://hradeczive.cz/#@50.19211,15.84974,0.16) | 2 podlaží, světlá fasáda | Zkomplexovaný areál (kombinace střech), potřebuje foto |
| 47 | Průmyslová budova (víc pater) | [50.19211, 15.84974](https://hradeczive.cz/#@50.19211,15.84974,0.16) | Čtvercový dům: 4 podlaží, valbová střecha, světlá fasáda i střecha podle ortofota | Počet pater odhad |
| 48 | Brněnská 300 | [50.19126, 15.84964](https://hradeczive.cz/#@50.19126,15.84964,0.20) | Valbová břidlicová střecha (v datech byla sedlová) | Barva fasády (foto) |
| 50 | Kanceláře – dvě budovy v sobě | [50.21126, 15.85166](https://hradeczive.cz/#@50.21126,15.85166,0.24) | Skryt drobný objekt (29 m²) uvnitř zástavby; obrysy se jinak nepřekrývají | Zbytek je těsné sousedství otočených budov (70° vs 25°) – ověřit v mapě |
| 53 | Parkovací dům Aupark vyšší | [50.21172, 15.81029](https://hradeczive.cz/#@50.21172,15.81029,0.50) | 7 podlaží, 22 m (laser měřil jen palubu 3,6 m) | – |

Pozn.: v `prep.py` má ruční výška `h` z `upresneni.json` teď přednost před laserem (dřív ji laser přepsal) – ovlivní i dřívější opravy s `h` (#8 Švendova, #22, #26).

## ⏳ #51 Malšovický most
Ve scéně je jediná mostovka (tertiary 12,8 m, vedou po ní i dva chodníky z OSM jako samostatné úseky), dvojitost jsem nereprodukoval; pilíře stojí na zelených pásech a v ose pod mostem. Potřebuji upřesnit, který most (snímek pohledu) – jinak by to byl zásah naslepo.

## 🆕 Nová hlášení
| # | Hlášení | Pozice | Odhad |
|---|---|---|---|
| 52 | „Kostel Božské srdce Páně – dominanta, chtělo by věrné zobrazení“ | [50.21300, 15.81550](https://hradeczive.cz/#@50.21300,15.81550,0.17) | Nový model dominanty: potřeba referenční fotky do `landmarks_ref/` |
| 43 | „domy nemají normální barvy“ (Meruňková 817) | [50.22198, 15.80221](https://hradeczive.cz/#@50.22198,15.80221,0.15) | 🔧 Podle panoramatu Mapy.com: pískově žluté dvoupodlažní řadové domky, ploché střechy, šedé garáže (dřív bílé); čeká na překreslení čtverce -1,1 |
| 6 | „je tu zahrádkářská kolonie“ | [50.22477, 15.84482](https://hradeczive.cz/#@50.22477,15.84482,0.38) | 🔧 Kolonie je dlouhý pás podél kanálu (ortofoto): obrys zvětšen na 2 části, 40 chatek a 40 stromů; čeká na překreslení čtverce 0,1 |
| 5 | Bezručova 555: stromy před domem | [50.20053, 15.81229](https://hradeczive.cz/#@50.20053,15.81229,0.22) | ❌ Zahozeno (bez podkladů); dřívější odhad stromů odstraněn z `oblasti.json`, projeví se při příštím překreslení čtverce -1,0; issue lze zavřít |

## Doporučený další postup
1. (hotovo) Dávka #13/#49/#25/#44 nasazena a issues smazány.
2. Brněnská (#45–#48) a #50, #51, #53 – technicky řešitelné bez dalších podkladů (duplicity, výšky); pustit v jedné dávce.
3. #52 (kostel) a #36 (muzeum) – potřebují fotky/podklady, pak model dominanty.
4. #14, #28–#32, #37, #42 – dotaz na reportéry/vás (viz sloupec „Co potřebuji“).

## ✅ #54, #55 Kyjevská 333 (nasazeno 2026-11-22, issues zavřeny, autorům odeslán e-mail)
Duplicitní hlášení s fotkou: broskvová fasáda, 4 podlaží, ploché střechy u domu a sousedních čtyř domů téhož typu. Chybí vstupní dveře a balkony (generátor neumí).
