# =============================================================================
# EconoSight — FastAPI Backend v2
# Fixed auth + prediction engine added
# =============================================================================

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx, secrets, sys, os, numpy as np
from datetime import datetime
from scipy import stats

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (SUPABASE_URL, SUPABASE_SECRET_KEY, SUPABASE_PUBLISHABLE_KEY,
                    ALL_COUNTRIES, AFRICAN_COUNTRIES, INDICATORS, APP_SECRET_KEY)
from database import supabase_get, supabase_post, supabase_upsert, supabase_delete

# =============================================================================
# App setup
# =============================================================================

app = FastAPI(
    title="EconoSight API",
    description="""
## EconoSight — African Economic Intelligence API

Access economic and financial data for African and global countries.

### Authentication
Include your API key in the request header:
```
X-API-Key: your_api_key_here
```
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend/templates"))

# =============================================================================
# Auth helpers
# =============================================================================

def generate_api_key():
    return "es_" + secrets.token_hex(24)


def get_supabase_auth_headers():
    """Returns correct headers for Supabase auth API calls."""
    return {
        "apikey":        SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {SUPABASE_PUBLISHABLE_KEY}",
        "Content-Type":  "application/json"
    }


async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required. Include X-API-Key header.")
    rows = supabase_get("profiles", {"api_key": f"eq.{x_api_key}", "select": "id,plan,api_calls"})
    if not rows:
        raise HTTPException(status_code=403, detail="Invalid API key.")
    return rows[0]


async def verify_supabase_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.replace("Bearer ", "")
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey":        SUPABASE_PUBLISHABLE_KEY,
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return r.json()

# =============================================================================
# Web pages
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/explorer", response_class=HTMLResponse)
async def explorer(request: Request):
    return templates.TemplateResponse(request=request, name="explorer.html")

@app.get("/developers", response_class=HTMLResponse)
async def developers(request: Request):
    return templates.TemplateResponse(request=request, name="developers.html")

@app.get("/insights", response_class=HTMLResponse)
async def insights(request: Request):
    return templates.TemplateResponse(request=request, name="insights.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# =============================================================================
# Auth endpoints — fixed for new Supabase key format
# =============================================================================

class AuthRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


@app.post("/auth/register")
async def register_user(body: AuthRequest):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=get_supabase_auth_headers(),
            json={"email": body.email, "password": body.password},
            timeout=15
        )

    data = r.json()

    if r.status_code not in [200, 201]:
        msg = data.get("msg") or data.get("message") or data.get("error_description") or "Registration failed."
        raise HTTPException(status_code=400, detail=msg)

    user = data.get("user") or data
    user_id = user.get("id")

    api_key = generate_api_key()

    if user_id:
        try:
            supabase_post("profiles", {
                "id":        user_id,
                "username":  body.email.split("@")[0],
                "full_name": body.full_name or "",
                "api_key":   api_key,
                "plan":      "free",
                "api_calls": 0
            })
        except Exception as e:
            print(f"Profile insert error: {e}")

    return {
        "message": "Account created successfully. You can now log in.",
        "api_key": api_key
    }


@app.post("/auth/login")
async def login_user(body: AuthRequest):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=get_supabase_auth_headers(),
            json={"email": body.email, "password": body.password},
            timeout=15
        )

    data = r.json()

    if r.status_code != 200:
        msg = data.get("error_description") or data.get("msg") or "Invalid email or password."
        raise HTTPException(status_code=401, detail=msg)

    return {
        "access_token":  data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "user":          data.get("user")
    }


@app.get("/auth/profile")
async def get_profile(user=Depends(verify_supabase_token)):
    rows = supabase_get("profiles", {"id": f"eq.{user['id']}", "select": "*"})
    if not rows:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return rows[0]

# =============================================================================
# Public data endpoints
# =============================================================================

@app.get("/data/countries")
async def get_countries():
    return {
        "african": AFRICAN_COUNTRIES,
        "global":  {k: v for k, v in ALL_COUNTRIES.items() if k not in AFRICAN_COUNTRIES},
        "all":     ALL_COUNTRIES
    }


@app.get("/data/indicators")
async def get_indicator_list():
    return INDICATORS


@app.get("/data/overview")
async def get_overview():
    rows = supabase_get("indicators", {
        "select":       "country_code,country_name,indicator_code,indicator_name,year,value",
        "country_code": "in.(" + ",".join(AFRICAN_COUNTRIES.keys()) + ")",
        "order":        "year.desc",
        "limit":        "500"
    })
    return {"data": rows, "count": len(rows)}


@app.get("/data/country/{country_code}")
async def get_country_data(country_code: str):
    code = country_code.upper()
    if code not in ALL_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country '{code}' not found.")
    rows = supabase_get("indicators", {
        "country_code": f"eq.{code}",
        "select":       "*",
        "order":        "year.desc"
    })
    return {"country_code": code, "country_name": ALL_COUNTRIES[code], "data": rows}


@app.get("/data/compare")
async def compare_countries(countries: str, indicator: str):
    codes = [c.strip().upper() for c in countries.split(",")]
    rows = supabase_get("indicators", {
        "country_code":   "in.(" + ",".join(codes) + ")",
        "indicator_code": f"eq.{indicator}",
        "select":         "*",
        "order":          "year.desc"
    })
    return {"countries": codes, "indicator": indicator, "data": rows}


@app.get("/data/currency")
async def get_currency_rates():
    rows = supabase_get("currency_rates", {
        "select": "base,target,rate,fetched_at",
        "order":  "fetched_at.desc",
        "limit":  "50"
    })
    return {"base": "USD", "rates": rows}


# =============================================================================
# Prediction & Insights Engine
# =============================================================================

@app.get("/insights/predict")
async def predict_indicator(country: str, indicator: str, years_ahead: int = 5):
    """
    Predicts future values for an economic indicator using linear regression.
    Returns historical data, trend analysis, and projections.
    """
    code = country.upper()
    rows = supabase_get("indicators", {
        "country_code":   f"eq.{code}",
        "indicator_code": f"eq.{indicator}",
        "select":         "year,value,country_name,indicator_name",
        "order":          "year.asc"
    })

    if len(rows) < 4:
        raise HTTPException(status_code=400,
            detail="Not enough data points for prediction. Need at least 4 years of data.")

    # Clean data
    clean = [(r["year"], r["value"]) for r in rows if r["value"] is not None]
    if len(clean) < 4:
        raise HTTPException(status_code=400, detail="Insufficient non-null data for prediction.")

    years  = np.array([c[0] for c in clean])
    values = np.array([c[1] for c in clean])

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)

    # Projections
    last_year = int(years[-1])
    future_years = list(range(last_year + 1, last_year + years_ahead + 1))
    projections = [{"year": y, "predicted_value": round(slope * y + intercept, 4)} for y in future_years]

    # Trend classification
    pct_change = ((values[-1] - values[0]) / abs(values[0])) * 100 if values[0] != 0 else 0
    if slope > 0:
        trend = "upward"
        trend_label = "Growing"
    elif slope < 0:
        trend = "downward"
        trend_label = "Declining"
    else:
        trend = "stable"
        trend_label = "Stable"

    # Volatility (coefficient of variation)
    volatility = (float(np.std(values)) / float(np.mean(values)) * 100) if np.mean(values) != 0 else 0
    volatility_label = "High" if volatility > 30 else "Medium" if volatility > 10 else "Low"

    # Year over year changes
    yoy = []
    for i in range(1, len(clean)):
        prev, curr = clean[i-1][1], clean[i][1]
        change = ((curr - prev) / abs(prev) * 100) if prev != 0 else 0
        yoy.append({"year": clean[i][0], "change_pct": round(change, 2)})

    return {
        "country":        ALL_COUNTRIES.get(code, code),
        "indicator":      rows[0]["indicator_name"],
        "historical":     [{"year": int(y), "value": float(v)} for y, v in clean],
        "projections":    projections,
        "trend": {
            "direction":    trend,
            "label":        trend_label,
            "slope":        round(float(slope), 6),
            "r_squared":    round(float(r_value ** 2), 4),
            "pct_change_total": round(float(pct_change), 2),
            "confidence":   "High" if r_value**2 > 0.8 else "Medium" if r_value**2 > 0.5 else "Low"
        },
        "volatility": {
            "value": round(float(volatility), 2),
            "label": volatility_label
        },
        "year_on_year":   yoy,
        "summary":        _build_summary(rows[0]["indicator_name"], ALL_COUNTRIES.get(code, code),
                                         trend_label, pct_change, projections, volatility_label)
    }


def _build_summary(indicator, country, trend, pct_change, projections, volatility):
    direction = "increased" if pct_change > 0 else "decreased"
    proj_val  = projections[-1]["predicted_value"] if projections else "N/A"
    proj_year = projections[-1]["year"] if projections else "N/A"
    return (
        f"{country}'s {indicator} has {direction} by {abs(pct_change):.1f}% over the tracked period. "
        f"The trend is {trend.lower()} with {volatility.lower()} volatility. "
        f"At the current trajectory, the projected value by {proj_year} is {proj_val:,.2f}." 
        if isinstance(proj_val, float) else
        f"{country}'s {indicator} trend is {trend.lower()}."
    )


@app.get("/insights/compare-trends")
async def compare_trends(countries: str, indicator: str):
    """
    Compares trends for an indicator across multiple countries.
    Returns who is growing fastest, slowest, most volatile.
    """
    codes = [c.strip().upper() for c in countries.split(",")]
    results = []

    for code in codes:
        rows = supabase_get("indicators", {
            "country_code":   f"eq.{code}",
            "indicator_code": f"eq.{indicator}",
            "select":         "year,value,country_name",
            "order":          "year.asc"
        })
        clean = [(r["year"], r["value"]) for r in rows if r["value"] is not None]
        if len(clean) < 3:
            continue

        years  = np.array([c[0] for c in clean])
        values = np.array([c[1] for c in clean])
        slope, _, r_value, _, _ = stats.linregress(years, values)
        pct_change = ((values[-1] - values[0]) / abs(values[0]) * 100) if values[0] != 0 else 0
        volatility = float(np.std(values) / np.mean(values) * 100) if np.mean(values) != 0 else 0

        results.append({
            "country_code":  code,
            "country_name":  ALL_COUNTRIES.get(code, code),
            "latest_value":  round(float(values[-1]), 4),
            "latest_year":   int(years[-1]),
            "trend_slope":   round(float(slope), 6),
            "pct_change":    round(float(pct_change), 2),
            "r_squared":     round(float(r_value**2), 4),
            "volatility":    round(float(volatility), 2),
            "trend_label":   "Growing" if slope > 0 else "Declining" if slope < 0 else "Stable"
        })

    if not results:
        raise HTTPException(status_code=400, detail="Insufficient data for comparison.")

    results.sort(key=lambda x: x["pct_change"], reverse=True)
    return {
        "indicator":    INDICATORS.get(indicator, indicator),
        "countries":    results,
        "fastest_growing": results[0]["country_name"] if results else None,
        "slowest":       results[-1]["country_name"] if results else None,
        "most_volatile": max(results, key=lambda x: x["volatility"])["country_name"] if results else None
    }


@app.get("/insights/anomalies")
async def detect_anomalies(country: str, indicator: str):
    """
    Detects anomalous years where the value deviated significantly from the trend.
    Useful for spotting economic crises or booms.
    """
    code = country.upper()
    rows = supabase_get("indicators", {
        "country_code":   f"eq.{code}",
        "indicator_code": f"eq.{indicator}",
        "select":         "year,value,country_name,indicator_name",
        "order":          "year.asc"
    })

    clean = [(r["year"], r["value"]) for r in rows if r["value"] is not None]
    if len(clean) < 5:
        raise HTTPException(status_code=400, detail="Not enough data to detect anomalies.")

    values = np.array([c[1] for c in clean])
    mean   = np.mean(values)
    std    = np.std(values)
    threshold = 1.5

    anomalies = []
    for year, val in clean:
        z_score = abs((val - mean) / std) if std > 0 else 0
        if z_score > threshold:
            anomalies.append({
                "year":      year,
                "value":     round(float(val), 4),
                "z_score":   round(float(z_score), 2),
                "deviation": "above" if val > mean else "below",
                "severity":  "Extreme" if z_score > 3 else "High" if z_score > 2 else "Moderate"
            })

    return {
        "country":    ALL_COUNTRIES.get(code, code),
        "indicator":  rows[0]["indicator_name"] if rows else indicator,
        "mean_value": round(float(mean), 4),
        "std_dev":    round(float(std), 4),
        "anomalies":  anomalies,
        "count":      len(anomalies)
    }


# =============================================================================
# Developer API (requires API key)
# =============================================================================

@app.get("/api/v1/indicators", tags=["Developer API"])
async def api_indicators(
    country: str,
    indicator: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    profile=Depends(verify_api_key)
):
    """Fetch economic indicators for a country."""
    params = {"country_code": f"eq.{country.upper()}", "select": "*", "order": "year.desc"}
    if indicator: params["indicator_code"] = f"eq.{indicator}"
    rows = supabase_get("indicators", params)
    if year_from: rows = [r for r in rows if r["year"] >= year_from]
    if year_to:   rows = [r for r in rows if r["year"] <= year_to]
    _log_api_call(profile, f"/api/v1/indicators")
    return {"country": country.upper(), "count": len(rows), "data": rows}


@app.get("/api/v1/compare", tags=["Developer API"])
async def api_compare(countries: str, indicator: str, profile=Depends(verify_api_key)):
    """Compare an indicator across multiple countries."""
    codes = [c.strip().upper() for c in countries.split(",")]
    rows = supabase_get("indicators", {
        "country_code":   "in.(" + ",".join(codes) + ")",
        "indicator_code": f"eq.{indicator}",
        "select":         "*",
        "order":          "year.desc"
    })
    _log_api_call(profile, "/api/v1/compare")
    return {"countries": codes, "indicator": indicator, "count": len(rows), "data": rows}


@app.get("/api/v1/predict", tags=["Developer API"])
async def api_predict(country: str, indicator: str, years_ahead: int = 5,
                      profile=Depends(verify_api_key)):
    """Predict future values for an economic indicator."""
    _log_api_call(profile, "/api/v1/predict")
    return await predict_indicator(country, indicator, years_ahead)


@app.get("/api/v1/currency", tags=["Developer API"])
async def api_currency(profile=Depends(verify_api_key)):
    """Latest USD exchange rates for African currencies."""
    rows = supabase_get("currency_rates", {"select": "*", "order": "fetched_at.desc", "limit": "20"})
    _log_api_call(profile, "/api/v1/currency")
    return {"base": "USD", "count": len(rows), "rates": rows}


@app.get("/api/v1/countries", tags=["Developer API"])
async def api_countries(profile=Depends(verify_api_key)):
    """All supported countries."""
    _log_api_call(profile, "/api/v1/countries")
    return {"african": AFRICAN_COUNTRIES, "global": {k: v for k, v in ALL_COUNTRIES.items() if k not in AFRICAN_COUNTRIES}}


def _log_api_call(profile, endpoint):
    try:
        supabase_post("api_usage_log", {"api_key": profile.get("api_key",""), "endpoint": endpoint, "called_at": datetime.utcnow().isoformat()})
    except Exception:
        pass


# =============================================================================
# User endpoints
# =============================================================================

class SaveIndicatorRequest(BaseModel):
    indicator_code: str
    country_code: str


@app.post("/user/save-indicator")
async def save_indicator(body: SaveIndicatorRequest, user=Depends(verify_supabase_token)):
    supabase_post("saved_indicators", {"user_id": user["id"], "indicator_code": body.indicator_code, "country_code": body.country_code})
    return {"message": "Saved."}


@app.get("/user/saved-indicators")
async def get_saved(user=Depends(verify_supabase_token)):
    rows = supabase_get("saved_indicators", {"user_id": f"eq.{user['id']}", "select": "*"})
    return {"data": rows}


@app.delete("/user/saved-indicator/{id}")
async def delete_saved(id: int, user=Depends(verify_supabase_token)):
    supabase_delete("saved_indicators", {"id": f"eq.{id}", "user_id": f"eq.{user['id']}"})
    return {"message": "Removed."}
