# =============================================================================
# EconoSight — Config Loader
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL            = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
SUPABASE_SECRET_KEY     = os.getenv("SUPABASE_SECRET_KEY")
EXCHANGE_RATE_API_KEY   = os.getenv("EXCHANGE_RATE_API_KEY")
APP_SECRET_KEY          = os.getenv("APP_SECRET_KEY", "changeme")
APP_ENV                 = os.getenv("APP_ENV", "development")
APP_PORT                = int(os.getenv("APP_PORT", 8000))

# World Bank API — no key needed
WORLD_BANK_BASE = "https://api.worldbank.org/v2"

# ExchangeRate API
EXCHANGE_RATE_BASE = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}"

# African countries we focus on
AFRICAN_COUNTRIES = {
    "ZA": "South Africa",
    "NG": "Nigeria",
    "KE": "Kenya",
    "GH": "Ghana",
    "EG": "Egypt",
    "ET": "Ethiopia",
    "TZ": "Tanzania",
    "MA": "Morocco",
    "RW": "Rwanda",
    "UG": "Uganda",
}

# Global comparison countries
GLOBAL_COUNTRIES = {
    "US": "United States",
    "GB": "United Kingdom",
    "CN": "China",
    "DE": "Germany",
    "BR": "Brazil",
    "IN": "India",
}

ALL_COUNTRIES = {**AFRICAN_COUNTRIES, **GLOBAL_COUNTRIES}

# World Bank indicators we track
INDICATORS = {
    "NY.GDP.MKTP.CD":     "GDP (Current USD)",
    "NY.GDP.PCAP.CD":     "GDP Per Capita (USD)",
    "FP.CPI.TOTL.ZG":     "Inflation Rate (%)",
    "SL.UEM.TOTL.ZS":     "Unemployment Rate (%)",
    "NE.TRD.GNFS.ZS":     "Trade (% of GDP)",
    "GC.DOD.TOTL.GD.ZS":  "Government Debt (% of GDP)",
    "SP.POP.TOTL":        "Population",
    "NY.GDP.MKTP.KD.ZG":  "GDP Growth Rate (%)",
}
