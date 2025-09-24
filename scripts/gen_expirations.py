#!/usr/bin/env python3
"""
Génère docs/expirations.json à partir d'une liste de paires CLE=YYYY-MM-DD
fournie via la variable d'environnement EXPIRATIONS.

Ex.:
  EXPIRATIONS="CERTIF=2025-12-31;CONTRAT=2026-03-01"

Variables optionnelles :
  - TIMEZONE="Europe/Paris"     (par défaut)
  - CLAMP_NON_NEGATIVE="true"   (true/false : coupe les valeurs négatives à 0)
  - OUT_PATH="docs/expirations.json"
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from datetime import datetime, date

# --- Fuseau horaire (zoneinfo standard lib, Python 3.9+) ---------------------
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # Gère un fallback

# ------------------------- Paramètres / Env -----------------------------------
RAW = os.getenv(
    "EXPIRATIONS",
    # Valeurs par défaut d'exemple (à remplacer côté workflow si besoin)
    "ONE=2028-09-07;TWO=2030-04-29;THREE=2025-09-30"
)

TIMEZONE = os.getenv("TIMEZONE", "Europe/Paris")
CLAMP_NON_NEGATIVE = os.getenv("CLAMP_NON_NEGATIVE", "true").lower() in ("1", "true", "yes")
OUT_PATH = os.getenv("OUT_PATH", "docs/expirations.json")

# ------------------------- Utilitaires ---------------------------------------
def warn(msg: str) -> None:
    print(f"[gen_expirations] WARN: {msg}", file=sys.stderr)

def info(msg: str) -> None:
    print(f"[gen_expirations] {msg}")

def get_today(tz_name: str) -> date:
    if ZoneInfo is None:
        warn("zoneinfo indisponible, fallback UTC.")
        return datetime.utcnow().date()
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        warn(f"Fuseau invalide '{tz_name}', fallback UTC.")
        tz = ZoneInfo("UTC")
    return datetime.now(tz).date()

def parse_pairs(raw: str) -> list[tuple[str, date]]:
    pairs: list[tuple[str, date]] = []
    for chunk in (c.strip() for c in raw.split(";")):
        if not chunk:
            continue
        if "=" not in chunk:
            warn(f"Ignoré (pas de '='): {chunk!r}")
            continue
        key, iso = (x.strip() for x in chunk.split("=", 1))
        if not key:
            warn(f"Ignoré (clé vide): {chunk!r}")
            continue
        try:
            d = datetime.fromisoformat(iso).date()  # attend YYYY-MM-DD
        except Exception:
            warn(f"Ignoré (date invalide): {chunk!r}")
            continue
        pairs.append((key, d))
    return pairs

# ----------------------------- Main ------------------------------------------
def main() -> int:
    today = get_today(TIMEZONE)
    expirations = {}

    pairs = parse_pairs(RAW)
    if not pairs:
        warn("Aucune paire valide trouvée dans EXPIRATIONS.")
    else:
        info(f"{len(pairs)} échéance(s) lue(s) → calcul des jours restants (au {today.isoformat()}).")

    for key, end in pairs:
        days_left = (end - today).days
        if CLAMP_NON_NEGATIVE and days_left < 0:
            days_left = 0
        expirations[key] = days_left

    out_path = Path(OUT_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(expirations, ensure_ascii=False), encoding="utf-8")

    info(f"Écrit {out_path} → {expirations}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
