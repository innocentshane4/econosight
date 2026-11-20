# EconoSight — African Economic Intelligence Platform

> A full-stack data platform for exploring, analysing, and predicting economic trends across Africa and the world.

**Live Demo:** https://econosight.onrender.com *(deploy to activate)*  
**API Docs:** https://econosight.onrender.com/api/docs  
**Built with:** Python · FastAPI · Supabase · Plotly · World Bank API

---

## What Is EconoSight?

EconoSight is a production-grade economic intelligence platform built entirely in Python. It pulls real economic data from the World Bank and ExchangeRate-API, stores it in a cloud PostgreSQL database, exposes it through a REST API, and presents it through an interactive web dashboard — with a built-in prediction and anomaly detection engine.

It was built to demonstrate end-to-end data engineering, analytics, and data science skills in a single cohesive product — not a tutorial, not a toy project, but something a real company could ship.

---

## What It Does

### Public Dashboard
Anyone can visit the site and explore:
- GDP, inflation, unemployment, trade, and population data for 16 countries
- 20 years of historical data per indicator
- Live USD exchange rates for African currencies
- Interactive charts powered by Plotly

### Data Explorer
- Select any country and any indicator
- Compare two countries side by side on the same chart
- Export the data as a CSV file with one click
- Year-on-year change calculated automatically

### Insights & Prediction Engine
The core data science layer. For any country and indicator:
- **Trend analysis** — determines whether the indicator is growing, declining, or stable
- **Linear regression forecasting** — projects values up to 10 years into the future
- **Confidence scoring** — rates how reliable the prediction is based on R² value
- **Volatility measurement** — classifies how stable or erratic the data is
- **Year-on-year change chart** — bar chart showing growth or decline each year
- **Anomaly detection** — flags years where the value deviated significantly from the long-term average using Z-score analysis (useful for spotting economic crises or booms)
- **Country comparison** — compares total percentage change across multiple African countries for the same indicator
- **Plain-English summary** — auto-generated sentence describing what the numbers actually mean

### User Accounts
- Register and log in securely via Supabase Auth
- Each user gets a personal API key on signup
- Save indicators to your personal dashboard for quick access

### Developer REST API
Authenticated JSON endpoints for developers:
- `GET /api/v1/indicators` — fetch indicator data for a country
- `GET /api/v1/compare` — compare an indicator across countries
- `GET /api/v1/predict` — get trend forecasts and projections
- `GET /api/v1/currency` — live exchange rates
- `GET /api/v1/countries` — all supported country codes
- Full auto-generated documentation at `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc)

---

## Countries Covered

| Region | Countries |
|---|---|
| Africa | South Africa, Nigeria, Kenya, Ghana, Egypt, Ethiopia, Tanzania, Morocco, Rwanda, Uganda |
| Global (comparison) | United States, United Kingdom, China, Germany, Brazil, India |

---

## Indicators Tracked

| Code | Indicator |
|---|---|
| `NY.GDP.MKTP.CD` | GDP (Current USD) |
| `NY.GDP.PCAP.CD` | GDP Per Capita (USD) |
| `FP.CPI.TOTL.ZG` | Inflation Rate (%) |
| `SL.UEM.TOTL.ZS` | Unemployment Rate (%) |
| `NE.TRD.GNFS.ZS` | Trade (% of GDP) |
| `GC.DOD.TOTL.GD.ZS` | Government Debt (% of GDP) |
| `SP.POP.TOTL` | Population |
| `NY.GDP.MKTP.KD.ZG` | GDP Growth Rate (%) |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core language |
| Backend | FastAPI | REST API and web server |
| Database | Supabase (PostgreSQL) | Cloud database with auth |
| Auth | Supabase Auth | User registration and login |
| Frontend | HTML + CSS + JavaScript | Web interface |
| Charts | Plotly.js | Interactive visualisations |
| Data Science | NumPy + SciPy | Regression, anomaly detection |
| Data Sources | World Bank API, ExchangeRate-API | Live economic data |
| Hosting | Render (free tier) | Live deployment |
| HTTP Client | httpx | Async API calls |

---

## Project Structure

```
econosight/
├── api/
│   ├── __init__.py
│   └── main.py              — FastAPI app: all routes, auth, prediction engine
├── pipeline/
│   ├── __init__.py
│   └── fetch_data.py        — Data pipeline: World Bank + currency fetcher
├── frontend/
│   ├── static/
│   │   ├── css/main.css     — Full design system: layout, components, theme
│   │   └── js/main.js       — Auth helpers, API calls, chart utilities
│   └── templates/
│       ├── base.html        — Base layout with nav and footer
│       ├── index.html       — Public landing page
│       ├── explorer.html    — Data explorer with compare and export
│       ├── insights.html    — Prediction and anomaly detection engine
│       ├── dashboard.html   — Logged-in user dashboard
│       ├── developers.html  — API documentation page
│       ├── register.html    — Account registration
│       └── login.html       — Login page
├── config.py                — Environment variable loader
├── database.py              — Supabase REST client and schema
├── schema.sql               — Database schema (run once in Supabase SQL Editor)
├── requirements.txt         — Python dependencies
├── render.yaml              — Render deployment config
├── .env                     — API keys (never committed to Git)
├── .gitignore
└── README.md
```

---

## Setup — Run It Locally

### Prerequisites
- Python 3.10 or higher
- A free [Supabase](https://supabase.com) account
- A free [ExchangeRate-API](https://exchangerate-api.com) key

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/econosight.git
cd econosight
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file
Create a file named `.env` in the root of the project and add:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SECRET_KEY=sb_secret_...
EXCHANGE_RATE_API_KEY=your_exchangerate_api_key
APP_SECRET_KEY=any_random_string_here
```

### 4. Set up the database
Go to your Supabase project → **SQL Editor** → click **New Query** → paste the full contents of `schema.sql` → click **Run**.

This creates all tables, row-level security policies, and permissions in one step.

### 5. Run the data pipeline
This fetches 20 years of World Bank data for all 16 countries and stores it in Supabase. Run it once — it takes 3 to 5 minutes.
```bash
python -m pipeline.fetch_data
```

### 6. Start the server
```bash
python -m uvicorn api.main:app --reload --port 8000
```

### 7. Open in your browser
```
http://localhost:8000
```

---

## Setup — Deploy to Production (Render)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit — EconoSight v1.0"
git remote add origin https://github.com/YOUR_USERNAME/econosight.git
git push -u origin main
```

### 2. Create a Render Web Service
1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **New** → **Web Service**
3. Connect your `econosight` repository
4. Render detects `render.yaml` automatically

### 3. Add environment variables in Render
Under your service → **Environment**, add:

| Key | Value |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Your Supabase publishable key |
| `SUPABASE_SECRET_KEY` | Your Supabase secret key |
| `EXCHANGE_RATE_API_KEY` | Your ExchangeRate-API key |
| `APP_SECRET_KEY` | Any random string |

### 4. Deploy
Click **Deploy**. Render builds and hosts the app. You get a live URL like:
```
https://econosight.onrender.com
```

### 5. Run the pipeline on the live server
In Render → your service → **Shell** tab:
```bash
python -m pipeline.fetch_data
```

---

## Using the API

### Get your API key
Register at `/register`. Your API key is shown immediately on signup and available in your dashboard.

### Authenticate
Include your key in every request header:
```
X-API-Key: es_your_api_key_here
```

### Example requests

**Fetch South Africa's GDP data:**
```bash
curl -X GET "https://econosight.onrender.com/api/v1/indicators?country=ZA&indicator=NY.GDP.MKTP.CD" \
  -H "X-API-Key: es_your_key"
```

**Compare inflation across Nigeria, Kenya, and Ghana:**
```bash
curl -X GET "https://econosight.onrender.com/api/v1/compare?countries=NG,KE,GH&indicator=FP.CPI.TOTL.ZG" \
  -H "X-API-Key: es_your_key"
```

**Get a 5-year GDP forecast for South Africa:**
```bash
curl -X GET "https://econosight.onrender.com/api/v1/predict?country=ZA&indicator=NY.GDP.MKTP.CD&years_ahead=5" \
  -H "X-API-Key: es_your_key"
```

**Get live currency rates:**
```bash
curl -X GET "https://econosight.onrender.com/api/v1/currency" \
  -H "X-API-Key: es_your_key"
```

### Interactive documentation
Visit `/api/docs` for Swagger UI — you can test every endpoint directly in the browser with no extra tools.

---

## Data Sources

| Source | What It Provides | Key Required |
|---|---|---|
| [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) | GDP, inflation, unemployment, trade, population | No |
| [ExchangeRate-API](https://exchangerate-api.com) | Live USD exchange rates | Yes (free) |
| [Supabase](https://supabase.com) | Database and authentication | Yes (free) |

---

## API Plans

| Plan | Requests/Month | Price |
|---|---|---|
| Free | 1,000 | $0 |
| Pro | 50,000 | Coming soon |

---

## Skills Demonstrated

This project was built to demonstrate competency across the full data stack:

- **Data Engineering** — automated pipeline fetching, cleaning, and storing data from external APIs into a cloud database
- **Data Analytics** — indicator comparison, year-on-year analysis, country benchmarking, CSV export
- **Data Science** — linear regression forecasting, Z-score anomaly detection, volatility measurement, confidence scoring
- **Backend Development** — RESTful API design with FastAPI, JWT-based auth via Supabase, rate limiting, usage logging
- **Frontend Development** — responsive web interface, interactive Plotly charts, client-side auth flow
- **Database Design** — normalised PostgreSQL schema, row-level security policies, upsert pipelines
- **Cloud Deployment** — Supabase for managed database and auth, Render for app hosting, environment-based config

---

## Author

Built by **Shane** — data analytics and data engineering portfolio project.  
GitHub: [github.com/innocentshane4](https://github.com/innocentshane4)

---

*Data sourced from the World Bank Open Data platform and ExchangeRate-API. All data is publicly available.*
