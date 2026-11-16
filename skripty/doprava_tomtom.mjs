// TomTom Traffic Flow (vektorové dlaždice, styl relative) -> {t, s: {klíč: [jam×10, rychlost %]}}; klíče stejné jako v izomapa/nastroje/tomtom_doprava.py
// (t<z>/<x>/<y>/<px>,<py>,<počet bodů> z celočíselných souřadnic dlaždice). Balíčky pbf a @mapbox/vector-tile instaluje workflow (npm i).
// Podmínky TomTom: data se neukládají do historie (jen poslední snímek v live.json se přepisuje každých 10 min), typické špičky jen z HERE.
export const TZ = 14, BBOX = [15.785, 50.175, 15.885, 50.245];            // west, south, east, north (stejné jako v Pythonu)

export function dlazdice(bbox = BBOX, z = TZ) {
  const n = 2 ** z, tx = (lon) => Math.floor((lon + 180) / 360 * n), ty = (lat) => Math.floor((1 - Math.asinh(Math.tan(lat * Math.PI / 180)) / Math.PI) / 2 * n);
  const out = [];
  for (let x = tx(bbox[0]); x <= tx(bbox[2]); x++) for (let y = ty(bbox[3]); y <= ty(bbox[1]); y++) out.push([z, x, y]);
  return out;
}

export async function useky(z, x, y, buf) {
  const [{ default: Pbf }, { VectorTile }] = await Promise.all([import('pbf'), import('@mapbox/vector-tile')]);
  const layer = new VectorTile(new Pbf(buf)).layers['Traffic flow'], s = {};
  if (!layer) return s;
  for (let i = 0; i < layer.length; i++) {
    const f = layer.feature(i), p = f.properties;
    if (p.road_closure || typeof p.traffic_level !== 'number') continue;
    const lv = Math.max(0, Math.min(1, p.traffic_level));
    for (const ln of f.loadGeometry()) {
      if (ln.length < 2) continue;
      s[`t${z}/${x}/${y}/${ln[0].x},${ln[0].y},${ln.length}`] = [Math.round((1 - lv) * 100), Math.round(lv * 100)];
    }
  }
  return s;
}

export async function nactiTomTom(klic, fetchFn = fetch) {
  const s = {};
  for (const [z, x, y] of dlazdice()) {
    const r = await fetchFn(`https://api.tomtom.com/traffic/map/4/tile/flow/relative/${z}/${x}/${y}.pbf?key=${encodeURIComponent(klic)}`,
      { headers: { 'user-agent': 'hradeczive-doprava' }, signal: AbortSignal.timeout(20000) });
    if (!r.ok) throw new Error(`TomTom ${r.status}`);
    Object.assign(s, await useky(z, x, y, new Uint8Array(await r.arrayBuffer())));
  }
  return { t: new Date().toISOString(), s };
}
