# Návrh: procedurální úpravy vzhledu budov (méně tokenů, méně ruční práce)

Stav k 13. 11. 2026. Zatím jen návrh, nic z toho není implementované.

## Kde se teď spotřebovávají tokeny (od nejdražšího)

1. **Obrázky:** fotky, ortofoto, rendery a srovnání; při ladění jedné budovy 5–10 obrázků.
2. **Psaní JS na míru:** každá dominanta má vlastní funkci v `izomapa/assets/custom_models.js` (30–80 řádků) a opravy, když nesedí.
3. **Průzkum kódu a dat:** opakované hledání, jak `prep.py` a `render.html` něco kreslí, výpisy dat budov.
4. **Ukecané výpisy:** logy, varování knihoven, dlouhé výstupy skriptů.

## A. Stavebnice dílů místo kódu na míru (největší úspora)

Z modelů, které už jsou v `custom_models.js` (Bílá věž, Hučák, terminál, zimní stadion, ČSOB, knihovna…), vytáhnout obecné díly ovládané jen ze `spec` v `assets/dominanty.json`:

- římsy a pásy (`bands`)
- mřížka oken, rozházená okna (knihovna), půlkruhová okna (strojovna Hučáku)
- střechy: mansarda, valená klenba (`vault`), membrány (terminál)
- hodinová věž: dřík s lizénami, bílé patro, ciferníky (v noci svítí), zaoblený štít, mansardová báň, hrot
- lucerny na hřebeni
- most s oblouky a balustrádou, pilíře, domek na pilíři (jez Hučák)
- skleněná mozaika (zimní stadion), pásy podlaží (ČSOB)

Nová budova by pak byla pár řádků JSON, bez nového JS:

```json
"spec": {"wc": "cihla", "pasy": [0.9, 4.6, "okap"],
         "vez": {"roh": "jz", "h": 30, "hodiny": 1, "stit": "zaobleny", "strecha": "mansarda"}}
```

Úpravu typu „věž o 3 m výš“ zvládne kdokoli bez AI.

## B. Jeden příkaz pro novou budovu

`skripty/budova.py "Název" lat lon [foto.jpg]`:

1. stáhne ortofoto ČÚZK (`skripty/pruzkum_mista.py`),
2. najde půdorys, výšku z laseru a barvu střechy z ortofota,
3. založí výchozí `spec` v `dominanty.json`,
4. připraví scénu a vyrenderuje výřez (`skripty/nahled_mista.py`),
5. složí **jeden** srovnávací obrázek (render, noc a referenční fotka; šířka do 800 px).

Pro jednu budovu se pak čtou 1–2 malé obrázky místo deseti.

## C. Editor vzhledu pro uživatele

Malá místní stránka: vybrat dominantu, měnit barvy, výšky a díly stavebnice posuvníky, hned vidět výřez (render.html s parametry) a uložit do `dominanty.json`. Drobné doladění („tmavší střecha“) pak nejde přes AI vůbec.

## D. Pravidla práce s AI

- Skripty vypisují jen souhrn, zbytek jde do logu v `build/`.
- Obrázky zmenšovat a ořezávat, na jedno kolo jedno srovnání.
- Od uživatele 1–2 nejlepší fotky na budovu, ne všechny.
- Úpravy posílat v dávkách (seznam budov s poznámkami), výsledek jedno souhrnné srovnání.
- Konvence projektu držet v `CLAUDE.md` a v paměti, ať se kód nemusí procházet znovu.

## E. Částečné překreslení (šetří čas, ne tokeny)

`skripty/oprav_misto.sh <lat> <lon>`: příprava scény čtverce, render jen dlaždic kolem budovy, aktualizace pyramidy se zamčenou paletou, a u budovy do 80 m od hranice i soused. Ověřeno: na RTX 5060 Ti / Direct3D dává opakovaný render bajtově stejné dlaždice, takže částečný render švy nerozbije. Čas na čtverec: příprava scény ~85 s, render ~1 min, `dzi.py` ~1,7 min.

## Doporučené pořadí

1. **A + B** (stavebnice z hotových modelů a příkaz pro novou budovu),
2. **C** podle potřeby,
3. **E** jako zrychlení.
