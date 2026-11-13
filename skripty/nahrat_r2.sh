#!/bin/sh
# Nahraje hotovou mapu (izomapa/site/) do Cloudflare R2 přes rclone (S3 API). Spouští uživatel sám, s vlastními klíči.
#
# Jednorázově:
#   1. Cloudflare → R2 → vytvoř bucket (např. izohradec) a API token „Object Read & Write“ jen pro tento bucket.
#   2. Nainstaluj rclone (https://rclone.org/downloads/) a nastav proměnné (do gitu je nikdy neukládej):
#        export R2_ACCOUNT_ID=...  R2_ACCESS_KEY_ID=...  R2_SECRET_ACCESS_KEY=...  R2_BUCKET=izohradec
#   3. V bucketu zapni veřejný přístup přes vlastní doménu (Settings → Custom Domains). index.html a dlaždice pak běží
#      z jedné domény, takže OpenSeadragon nepotřebuje CORS. Na samotném R2 neběží functions/ (letadla, hlášení) –
#      na ty je potřeba Cloudflare Pages nebo Worker (viz README izomapy).
#
# Použití:  sh skripty/nahrat_r2.sh            (jen změněné soubory; poprvé nahraje všechno)
#           sh skripty/nahrat_r2.sh --dry-run  (jen vypíše, co by se nahrálo)
set -e
cd "$(dirname "$0")/../izomapa"
: "${R2_ACCOUNT_ID:?chybí R2_ACCOUNT_ID}" "${R2_ACCESS_KEY_ID:?chybí R2_ACCESS_KEY_ID}" "${R2_SECRET_ACCESS_KEY:?chybí R2_SECRET_ACCESS_KEY}" "${R2_BUCKET:?chybí R2_BUCKET}"
[ -f site/index.html ] && [ -f site/tiles.json ] || { echo "site/ není hotová (spusť nejdřív stavbu)"; exit 1; }
R=":s3,provider=Cloudflare,access_key_id=$R2_ACCESS_KEY_ID,secret_access_key=$R2_SECRET_ACCESS_KEY,endpoint=https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com:$R2_BUCKET"
# dlaždice se nemění (nová verze = nový render a nové tiles.json s 'ver'), smí se cachovat dlouho; ostatní krátce
rclone sync site/tiles "$R/tiles" --transfers 32 --checkers 64 --fast-list --checksum \
  --header-upload "Cache-Control: public, max-age=2592000" "$@"
rclone sync site "$R" --exclude "tiles/**" --transfers 16 --fast-list \
  --header-upload "Cache-Control: public, max-age=300" "$@"
echo "Hotovo: $(find site -type f | wc -l) souborů, $(du -sh site | cut -f1)"
