# Graph Report - izohradec  (2026-11-13)

## Corpus Check
- 85 files · ~105,102 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .jsonc 1)

## Summary
- 604 nodes · 1055 edges · 52 communities (26 shown, 26 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.85)
- Token cost: 600,189 input · 0 output

## Community Hubs (Navigation)
- Overlay a geodata
- MHD podle GTFS
- Grafová navigace silnic
- Testy čekání MHD
- Testy komínů
- Testy sousedních měst
- DeepZoom dlaždice (dzi)
- Testy letadel
- Testy obcí
- Generování webu (build_html)
- Dominanty a stromy
- Seskupení budov
- Záloha custom modelů
- Intenzita dopravy
- Výbava střech
- Kreslení čar a ploch
- Mosty a tunely
- Stíny na střechách
- Vzorkování terénu DMR
- Rozklad půdorysu střech
- Komíny a potrubí
- Overture hodnoty a jednosměrky
- Panelové domy
- Custom modely dominant
- Node závislosti a render.mjs
- Nájezdy na mosty
- Mostovky nad terénem
- Hustota zástavby
- Poloha věží a komínů
- Řady garáží
- Výšky skupin budov
- Šířka silnic
- Stahování dat (fetch_data)
- Příprava scény (prep.py)
- Cloudflare worker a lety
- Projekt Hradec – dokumentace
- Shell skripty renderu
- Build celého města
- Nahrání na R2
- Three.js render scény
- Webový prohlížeč app.html
- Ukázka Chrastava
- Ukázka Liberec
- Postup pro nové město
- Hlášení nepřesností
- Věže dominant v renderu
- Kamera a obrysy
- Admin API hlášení
- Hučák – reference fotek

## God Nodes (most connected - your core abstractions)
1. `draw() / frame() animation loop` - 20 edges
2. `initLayers()` - 16 edges
3. `Hučák` - 16 edges
4. `postav.sh script` - 14 edges
5. `to_local()` - 11 edges
6. `og_obrazek()` - 8 edges
7. `build()` - 8 edges
8. `loadChunk() / loadVisible() lazy overlay chunks` - 8 edges
9. `KominyTest` - 7 edges
10. `dopln_mezicasy()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Bílá věž v pozadí (z fotky Hučáku)` --references--> `Bílá věž`  [INFERRED]
  podklady/hučák/hucak.jpg → CLAUDE.md
- `Nasvícená Bílá věž v pozadí (noční foto)` --references--> `Bílá věž`  [INFERRED]
  podklady/hučák/nocni-hucak.jpg → CLAUDE.md
- `Stavebnice dílů místo kódu na míru` --references--> `assets/custom_models.js`  [EXTRACTED]
  NAVRH_procedury_budov.md → izomapa/CLAUDE.md
- `skripty/budova.py – jeden příkaz pro novou budovu` --references--> `assets/dominanty.json (spec dominant)`  [EXTRACTED]
  NAVRH_procedury_budov.md → izomapa/CLAUDE.md
- `skripty/oprav_misto.sh – částečné překreslení` --conceptually_related_to--> `Renderuje se celý čtverec (odstíny GPU)`  [INFERRED]
  NAVRH_procedury_budov.md → izomapa/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Build pipeline izomapy (prep -> render -> dzi -> overlay -> build_html)** — izomapa_prep, izomapa_claude_render_html, izomapa_dzi, izomapa_overlay, izomapa_build_html [EXTRACTED 1.00]
- **Geometry primitive stack** — izomapa_render_pushtri, izomapa_render_pushquad, izomapa_render_pushbox, izomapa_render_frameat, izomapa_render_ring [EXTRACTED 1.00]
- **GTFS timetable transit simulation** — izomapa_web_app_mhd, izomapa_web_app_mhdactive, izomapa_web_app_mhdpos, izomapa_web_app_drawtrain, izomapa_web_app_showstop, izomapa_web_app_xings [EXTRACTED 1.00]
- **Vehicle sprite render and occlusion pipeline** — izomapa_web_app_drawvehicle, izomapa_web_app_vehiclesprite, izomapa_web_app_drawbehindtrees, izomapa_web_app_stromy, izomapa_web_app_flushlights [EXTRACTED 1.00]
- **Návrh procedurálních úprav budov A–E** — navrh_procedury_budov_stavebnice_dílů, navrh_procedury_budov_budova_py, navrh_procedury_budov_editor_vzhledu, navrh_procedury_budov_pravidla_ai, navrh_procedury_budov_oprav_misto [EXTRACTED 1.00]
- **Tile render pipeline: shadow, scene, post, export** — izomapa_render_shadowmap, izomapa_render_postprocess, izomapa_render_rendertile, izomapa_render_dimetric_camera [INFERRED 0.85]
- **Season / time-of-day / weather state controls** — izomapa_web_app_setseason, izomapa_web_app_setweather, izomapa_web_app_applytime, izomapa_web_app_sunalt, izomapa_web_app_loadwind [INFERRED 0.85]
- **Hučák hydro ensemble: building + weir + bridge + river** — hučák_landmark, podklady_hučák_hucak_weir, podklady_hučák_hucak_bridge, podklady_hučák_hucak_river_labe [INFERRED 0.85]
- **Noční světelná paleta Hučáku** — podklady_hučák_nocni_hucak_lit_clock_tower, podklady_hučák_nocni_hucak_warm_facade_floodlight, podklady_hučák_nocni_hucak_sodium_streetlamps, podklady_hučák_nocni_hucak_water_reflections, podklady_hučák_nocni_hucak_blue_hour_sky, night_mode [INFERRED 0.85]

## Communities (52 total, 26 thin omitted)

### Community 1 - "Overlay a geodata"
Cohesion: 0.05
Nodes (24): Image2D, krovak(), bbox_lonlat(), extent(), to_local(), view(), r2(), ridge() (+16 more)

### Community 11 - "MHD podle GTFS"
Cohesion: 0.17
Nodes (4): MezicasyTest, chunk_center(), cekani_na_konecne(), dopln_mezicasy()

### Community 3 - "DeepZoom dlaždice (dzi)"
Cohesion: 0.07
Nodes (15): TestStada, build(), build_alpha(), one(), palette_with_water(), quant_alpha(), save(), vyber() (+7 more)

### Community 0 - "Generování webu (build_html)"
Cohesion: 0.07
Nodes (20): ikony_a_manifest(), og_obrazek(), postav_stranku(), src(), chunk_dir(), chunk_of(), neighbours(), skirt_edges() (+12 more)

### Community 13 - "Dominanty a stromy"
Cohesion: 0.22
Nodes (6): free_v(), ihash(), polys(), scatter(), unhole(), zone_split()

### Community 16 - "Seskupení budov"
Cohesion: 0.22
Nodes (7): free(), group_key(), h01(), _ok(), pix(), wkey(), wrng()

### Community 17 - "Záloha custom modelů"
Cohesion: 0.31
Nodes (6): axis(), frame2(), frame2swap(), prism(), wall(), landmarks

### Community 18 - "Intenzita dopravy"
Cohesion: 0.29
Nodes (5): _along(), piece_intensity(), piece_limit(), piece_oneway(), _road()

### Community 20 - "Výbava střech"
Cohesion: 0.33
Nodes (5): load(), polys_lines(), roof_deco(), to_local(), _zpoly()

### Community 23 - "Kreslení čar a ploch"
Cohesion: 0.40
Nodes (5): sheet(), fill(), line(), lines(), P()

### Community 24 - "Mosty a tunely"
Cohesion: 0.40
Nodes (3): bridge_parts(), seg_flags(), tunnel_parts()

### Community 26 - "Vzorkování terénu DMR"
Cohesion: 0.67
Nodes (4): dem_sampler(), sample(), sample_dmr(), to_lonlat()

### Community 4 - "Node závislosti a render.mjs"
Cohesion: 0.06
Nodes (30): author, dependencies, openseadragon@^4.1.0, playwright@^1.56.1, three@^0.170.0, description, devDependencies, wrangler@^4.152.0 (+22 more)

### Community 5 - "Stahování dat (fetch_data)"
Cohesion: 0.09
Nodes (8): dem(), tile(), rows(), sections(), cas(), vlak(), api(), strip()

### Community 6 - "Příprava scény (prep.py)"
Cohesion: 0.08
Nodes (4): ground(), zline(), assets/custom_prep.py (HOOK terrain/cemetery/props), assets/upresneni.json

### Community 8 - "Cloudflare worker a lety"
Cohesion: 0.13
Nodes (17): onRequest(), adminDetail(), adminList(), adminSet(), fetch(), isAdmin(), json(), report() (+9 more)

### Community 9 - "Projekt Hradec – dokumentace"
Cohesion: 0.11
Nodes (14): match_doms(), Bílá věž, Cloudflare R2 (hosting dlaždic), GTFS CIS JŘ DPMHK (agency A194), Hučák, assets/custom_models.js, assets/dominanty.json (spec dominant), render.html + render.mjs (three.js renderer) (+6 more)

### Community 12 - "Shell skripty renderu"
Cohesion: 0.17
Nodes (5): render_all.sh script, render_chunk.sh script, render_ctverec.sh script, render_par.sh script, setup.sh script

### Community 10 - "Three.js render scény"
Cohesion: 0.11
Nodes (19): Bridge decks, embankments, piers, Building geometry (walls, roofs, landmarks: church, radnice, hq, chapel), covered() parallel deck test, frameAt() local frame, geom() buffer geometry builder, Seasonal herds (cows, horses, deer), inst() instanced props, mat() shader material factory (+11 more)

### Community 2 - "Webový prohlížeč app.html"
Cohesion: 0.06
Nodes (52): app.html (OpenSeadragon map viewer), addPreview(), applyTime(), applyVisibility(), Car traffic simulation (roads graph, stepCar, pickExit), Clouds (cloudBitmap), deckZ() bridge deck height, draw() / frame() animation loop (+44 more)

### Community 21 - "Ukázka Chrastava"
Cohesion: 0.33
Nodes (6): Isometric terrain block render of Chrastava (L-shaped multi-square extent, summer), Forest mask, meadows and yellow fields (orthophoto/ZABAGED landcover), Winding river (Lužická Nisa/Jeřice) and main road/railway corridor, DMR relief with brown soil cross-section base, Chrastava town center with red roofs and industrial halls in river valley, chrastava.webp (sample izomapa render)

### Community 22 - "Ukázka Liberec"
Cohesion: 0.40
Nodes (6): Landmark labels: Liberecka radnice, Kostel sv. Antonina Velikeho, Divadlo F. X. Saldy, Krajska vedecka knihovna, Minimap overview with scale (1 px = 37 cm), SimCity 2000-style isometric pixel-art city render, Summer (Leto) daytime season variant, Viewer control panel (search, season Jaro/Leto/Podzim/Zima, day-night slider, weather Jasno/Dest/Snih/Mlha, layers), liberec.webp - sample isometric map of Liberec (izomapa UI screenshot)

### Community 30 - "Postup pro nové město"
Cohesion: 0.67
Nodes (3): mesto.json, Postup pro nové město, AGENTS.md (odkaz na CLAUDE.md)

### Community 31 - "Hlášení nepřesností"
Cohesion: 0.67
Nodes (3): Administrace hlášení nepřesností, hlaseni/worker.js (Cloudflare Worker + D1), Hlášení nepřesností (SALT, limit 3/h)

### Community 36 - "Věže dominant v renderu"
Cohesion: 0.67
Nodes (3): Photo-based landmark towers/stacks/chimneys (tw, stk, chs, blk, cn), ring() frustum/cone primitive, assets/custom_models.js hooks (landmarks, buildProps)

### Community 7 - "Hučák – reference fotek"
Cohesion: 0.08
Nodes (25): Hučák, Noční režim izomapy, Bílá věž v pozadí (z fotky Hučáku), Low arched road/foot bridge with white balustrade across the weir, Clock tower with stepped/curved gable, clock faces, steep dark hipped roof and finial, Dark grey slate mansard roof with brick chimneys on main block, Red brick facade with cream/white plaster bands and window surrounds (Art Nouveau), River Labe (Elbe) with stone-paved embankment (+17 more)

## Knowledge Gaps
- **58 isolated node(s):** `web/app.html (OpenSeadragon prohlížeč)`, `frameAt() local frame`, `geom() buffer geometry builder`, `roofMat shader`, `solidMat shader` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 240 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `postav.sh script` connect `Generování webu (build_html)` to `Overlay a geodata`, `Node závislosti a render.mjs`, `Stahování dat (fetch_data)`, `MHD podle GTFS`, `Shell skripty renderu`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **What connects `web/app.html (OpenSeadragon prohlížeč)`, `frameAt() local frame`, `geom() buffer geometry builder` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Overlay a geodata` be split into smaller, more focused modules?**
  _Cohesion score 0.053763440860215055 - nodes in this community are weakly interconnected._
- **Why does `Bílá věž` connect `Projekt Hradec – dokumentace` to `Hučák – reference fotek`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Should `DeepZoom dlaždice (dzi)` be split into smaller, more focused modules?**
  _Cohesion score 0.0728744939271255 - nodes in this community are weakly interconnected._
- **Should `Generování webu (build_html)` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Should `Node závislosti a render.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.06006006006006006 - nodes in this community are weakly interconnected._