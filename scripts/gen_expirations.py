from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import os, json

# ⛭ Échéances dans la variable d'env EXPIRATIONS (repo variables/secrets)
# Format: "PEREMPTION=2025-09-25;CLE=YYYY-MM-DD"
RAW = os.getenv("EXPIRATIONS", "ONE=2028-09-07;TWO=2030-04-29";THREE=2025-09-30")

# ⛭ Coupe à 0 si on ne veux pas de valeurs négatives après expiration
CLAMP_NON_NEGATIVE = os.getenv("CLAMP_NON_NEGATIVE", "true").lower() in ("1","true","yes")

# Fuseau, pour que le "jour" bascule correctement
TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Paris"))
today = datetime.now(TZ).date()

expirations = {}
for pair in [p.strip() for p in RAW.split(";") if p.strip()]:
    key, iso = pair.split("=", 1)
    end = datetime.fromisoformat(iso).date()
    days_left = (end - today).days
    if CLAMP_NON_NEGATIVE and days_left < 0:
        days_left = 0
    expirations[key] = days_left

Path("docs").mkdir(parents=True, exist_ok=True)
out_path = Path("docs/expirations.json")
out_path.write_text(json.dumps(expirations, ensure_ascii=False), encoding="utf-8")
print(f"Écrit {out_path} → {expirations}")
