#!/bin/sh
# Plné překreslení všech čtverců: scény, render, dlaždice, klikací vrstva, jízdní řády, web (to samé jako `sh ./postav.sh render`).
cd "$(dirname "$0")/../../../izomapa" || exit 1
sh ./postav.sh render
