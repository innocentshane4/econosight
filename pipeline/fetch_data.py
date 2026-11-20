# =============================================================================
# EconoSight — Data Pipeline
# Fetches World Bank indicators and currency rates → stores in Supabase
# =============================================================================

import httpx
import sys, os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import WORLD_BANK_BASE, EXCHANGE_RATE_BASE, ALL_COUNTRIES, INDICATORS
from database import supabase_upsert


def fetch_world_bank_indicator(country_code, indicator_code, indicator_name):
    """Fetches historical data for one indicator and one country."""

    url = f"{WORLD_BANK_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {
        "format":   "json",
        "per_page": "20",
        "mrv":      "20"   # most recent 20 years
    }

    try:
        r = httpx.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        if not data or len(data) < 2:
            return []

        records = []
        for entry in data[1] or []:
            if entry.get("value") is None:
                continue
            records.append({
                "country_code":   country_code,
                "country_name":   ALL_COUNTRIES.get(country_code, country_code),
                "indicator_code": indicator_code,
                "indicator_name": indicator_name,
                "year":           int(entry["date"]),
                "value":          float(entry["value"])
            })

        return records

    except Exception as e:
        print(f"  [Pipeline] WB error {country_code}/{indicator_code}: {e}")
        return []


def run_indicators_pipeline():
    """Fetches all indicators for all countries and upserts into Supabase."""

    print("  [Pipeline] Starting World Bank fetch...")
    total = 0

    for code, name in ALL_COUNTRIES.items():
        for ind_code, ind_name in INDICATORS.items():
            records = fetch_world_bank_indicator(code, ind_code, ind_name)
            if records:
                try:
                    supabase_upsert("indicators", records,
                                    on_conflict="country_code,indicator_code,year")
                    total += len(records)
                    print(f"  [Pipeline] {name} / {ind_name} — {len(records)} rows")
                except Exception as e:
                    print(f"  [Pipeline] Upsert failed {code}/{ind_code}: {e}")

    print(f"  [Pipeline] World Bank done. Total rows: {total}")


def run_currency_pipeline():
    """Fetches live exchange rates and stores in Supabase."""

    print("  [Pipeline] Fetching exchange rates...")
    targets = ["ZAR", "NGN", "KES", "GHS", "EGP", "ETB",
               "EUR", "GBP", "JPY", "CNY", "INR", "BRL"]

    try:
        r = httpx.get(f"{EXCHANGE_RATE_BASE}/latest/USD", timeout=10)
        r.raise_for_status()
        data = r.json()

        if data.get("result") != "success":
            print("  [Pipeline] Exchange rate API error.")
            return

        rates = data["conversion_rates"]
        records = []
        fetched_at = datetime.utcnow().isoformat()

        for target in targets:
            if target in rates:
                records.append({
                    "base":       "USD",
                    "target":     target,
                    "rate":       rates[target],
                    "fetched_at": fetched_at
                })

        supabase_upsert("currency_rates", records, on_conflict="")
        print(f"  [Pipeline] Currency rates done. {len(records)} rates stored.")

    except Exception as e:
        print(f"  [Pipeline] Currency error: {e}")


def run_full_pipeline():
    print("=" * 60)
    print("  EconoSight — Data Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    run_indicators_pipeline()
    run_currency_pipeline()
    print("=" * 60)
    print("  Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_full_pipeline()
