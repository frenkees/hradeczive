#!/bin/sh
# Denní aktualizace grafu kódu (AST, bez LLM) – i pro vnořený repozitář izomapa, na který se hook v kořenu nevztahuje
cd "$(dirname "$0")/../.." && graphify update . >> graphify-out/denni_update.log 2>&1
