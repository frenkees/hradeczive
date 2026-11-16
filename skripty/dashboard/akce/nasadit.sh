#!/bin/sh
# Nasazení hotového renderu: změněné dlaždice na R2, příprava složky pro Vercel, produkční nasazení.
set -e
cd "$(dirname "$0")/../../.."
echo "== 1/3 dlaždice na Cloudflare R2 (jen změněné)"
node skripty/nahrat_dlazdice_r2.mjs izohradec
echo "== 2/3 příprava složky pro Vercel"
node skripty/pripravit_vercel.mjs https://pub-55cbad9c2db745779e46b9eac5658b47.r2.dev
echo "== 3/3 nasazení na Vercel (produkce)"
cd nasazeni/vercel
vercel deploy --prod --yes
echo "Nasazeno."
