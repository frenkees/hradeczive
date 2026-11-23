# Plán: vrstva „Události“ (hasiči, nehody, výstrahy)

Stav: jen nápad do budoucna (2026-11-17), nic z toho není implementované. Jen web, bez překreslení dlaždic.

## Zdroj 1: Události HZS Královéhradeckého kraje (ověřeno 2026-11-17)
Webová aplikace https://udalostikhk.hzscr.cz/ (Angular + ArcGIS) čte nedokumentované veřejné JSON rozhraní bez klíče:
```
GET https://udalostikhk.hzscr.cz/api/?casOd=<ISO>&casDo=<ISO>&stavIndex=&stavIds=210&stavIds=400&...
```
- Povinné parametry: `casOd`, `casDo`, `stavIndex` (prázdný), `stavIds` (opakovaně). Bez nich vrací 400 s názvem chybějícího parametru.
- Stavy: otevřené 210, 400, 410, 420, 430, 440, 500; uzavřené 510, 520, 600, 610, 620, 700, 710, 750, 760, 780, 800.
- Zkouška: za 7 dní 156 událostí pro celý kraj, ~62 kB.
- Pole události: `id`, `casOhlaseni`, `casVzniku`, `stavId`, `typId`, `podtypId`, `poznamkaProMedia`, `kraj`, `okres`, `obec`, `castObce`, `ORP`, `ulice`, `gis1`, `gis2`, `zoc`, `silnice`.
- Souřadnice `gis1`, `gis2` = S-JTSK (aplikace je používá se záporným znaménkem); převést do WGS84.
- `typId` jsou číselné kódy (3100 požár, 3200, 3400, 3500, 3550, 3800 …). Popisky typů a podtypů zatím neznáme, najít v kódu aplikace (`main.*.js`) nebo dalším volání.
- Aplikace je načtená přes `curl` (systémový úložiště certifikátů), WebFetch odmítl certifikační řetězec. Ve Vercel funkci (Node) vyzkoušet.

## Další zdroje (z paměti, neověřeno)
- TomTom Traffic Incidents a HERE Traffic Incidents: klíče už máme, nehody, uzavírky, kolony (vykřičníky nad silnicí).
- NDIC (dopravniinfo.cz, DATEX II): uzavírky a události na silnicích ČR, vyžaduje registraci.
- ČHMÚ výstrahy (CAP/XML): otevřená data, zobrazit jako pruh nebo ikonu v panelu.

## Postup
1. Napsat HZS KHK: souhlas s použitím rozhraní a uvedení zdroje (nedokumentované API, může se změnit).
2. Vercel funkce `/api/udalosti` s cache (30–60 s), jako `/api/doprava`; převod S-JTSK -> WGS84, jen poslední hodiny.
3. Ochrana soukromí: zobrazovat typ, obec a čas, ne ulici ani poznámku; události po několika hodinách mizí.
4. Vrstva ve `web/app.html`: ikony nad místem (vykřičník u nehod na silnici), popisek, vypínač v panelu Vrstvy.
5. Doplnit TomTom/HERE nehody, potom výstrahy ČHMÚ.
