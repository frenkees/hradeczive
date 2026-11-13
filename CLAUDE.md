# Projekt: Izometrický Hradec Králové

## Cíl
Adaptovat open-source generátor `adamklatovsky/izomapa` (původně vytvořený pro Liberec) pro město **Hradec Králové**.

## Geografické vymezení (WGS84)
- **Bílá věž:** `50.20898, 15.83083` (Overture places; dřívější `50.2093, 15.8358` bylo ~350 m vedle)
- **Velké náměstí (těžiště pěší plochy, vánoční strom):** `50.20932, 15.83300`
- **Katedrála sv. Ducha:** `50.20877, 15.83051` · **Hučák:** `50.20741, 15.82576` · **Gymnázium J. K. Tyla:** `50.20869, 15.82572`
- **Soutok Labe a Orlice:** `50.20416, 15.82496` · **Ulrichovo náměstí:** `50.21053, 15.82211`
- **Pilotní výřez (historické centrum + soutok Labe a Orlice):**
  - `min_lat: 50.2030, max_lat: 50.2150`
  - `min_lon: 15.8180, max_lon: 15.8430` (rozšířeno na západ, aby obsahoval soutok i Ulrichovo náměstí)
  - V izomapě se renderuje celý čtverec (0,0) o straně 2,3 km se středem `50.20539, 15.83009`, který výřez pokrývá.
- **Celé město (pro finální render):**
  - `min_lat: 50.1750, max_lat: 50.2450`
  - `min_lon: 15.7850, max_lon: 15.8850`
  - Mřížka izomapy: 16 čtverců i, j ∈ −1…2 kolem středu `50.20539, 15.83009` (lat, lon); `href` 233,3 m, `dno` −40 m. Střed ani `href` neměnit, jinak nesedí už vyrenderované čtverce.

## Umístění
- Repo izomapa: `./izomapa/` (Python vždy `.venv/Scripts/python`, `PYTHONUTF8=1`, skripty v Git Bash).
- Náhledy: `./izomapa/preview/`, referenční fotky dominant: `./izomapa/landmarks_ref/<dominanta>/` (obojí v `.gitignore`).
- MHD: GTFS CIS JŘ `https://www.spojenka.cz/jrdata/jizdnirady-gtfs.zip`, DPMHK = agency `A194` (bez shapes.txt, trolejbusy route_type 11, číslo linky je v `route_long_name` „linka: N“).

## Architektura a pravidla
- **Vstupní data:** OpenStreetMap, Overture Maps (budovy/výšky) a DMR (digitální model reliéfu) z ČÚZK.
- **Výstup:** Víceúrovňová DeepZoom dlaždicová pyramida ve formátu `.webp` pro prohlížeč OpenSeadragon (roční období: jaro/léto, podzim, zima + noční režim).
- **Hardware:** Lokální stroj má RTX 5060 Ti 16GB – kdykoli je to možné, využij paralelní zpracování / GPU akceleraci.
- **Reference dominant:** Složka `./landmarks_ref/` obsahuje reálné fotografie klíčových budov Hradce Králové. Při jejich modelování vždy vyrenderuj kontrolní výřez a vizuálně ho porovnej s fotkou.
- **Oddělení dat:** Vygenerované dlaždice neukládej do Gitu (přidej výstupní složky do `.gitignore`), počítá se s jejich nahráním na Cloudflare R2.
## Plány
- Návrh procedurálních úprav budov (stavebnice dílů, příkaz pro novou budovu, editor vzhledu): `./NAVRH_procedury_budov.md`

## Stav projektu
Aktuální stav, postup stavby a nasazení a otevřené úkoly: `./STAV_PROJEKTU.md` (na začátku session přečíst, po větších změnách aktualizovat).
