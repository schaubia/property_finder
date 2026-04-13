# 🏠 БГ Имоти | BG Property Finder

Streamlit application for searching, analysing and financing real estate in Bulgaria. Built for both local buyers and foreign investors.

---

## ✨ Features

### 🔍 Property Search
- Browse **100 sample listings** across all major Bulgarian cities
- **Live scraping** from [imot.bg](https://www.imot.bg) and [imoti.net](https://www.imoti.net) — real listings, refreshed on demand
- Filter by city, property type, price range, area, construction type and specific features (parking, elevator, pool…)
- Sort by price, area, price per m², or newest first
- One-click **❤️ Watchlist** — save any property for later

### 🏦 Mortgage Calculator
- Calculate monthly payments, total cost and affordability (DTI gauge)
- Compare all **12 Bulgarian banks and lending institutions** side by side:

| Tier 1 | Tier 2 |
|--------|--------|
| DSK Bank (27% market share) | Central Cooperative Bank (CCB) |
| OBB / United Bulgarian Bank (22%) | Allianz Bank Bulgaria |
| UniCredit Bulbank (18.5%) | Raiffeisenbank Bulgaria |
| Postbank / Eurobank Bulgaria (16.5%) | Investbank |
| First Investment Bank / Fibank (5.4%) | Municipal Bank |
| | Bulgarian-American Credit Bank (BACB) |
| | D Commerce Bank |

- **🔄 Live rate scraping** — fetches current rates from each bank's website (cached 1 hour)
- **BNB Base Interest Rate** — fetched live from the Bulgarian National Bank; used as default rate anchor
- **💾 Save scenarios** — store multiple mortgage scenarios (loan amount, rate, term, bank) persistently
- **📄 PDF report** — download a branded A4 mortgage comparison report including all bank rates, your results, and saved scenarios

### 🗺️ Location Map
- Interactive **pydeck map** with colour-coded property pins by type
- Filter properties on the map by city, type and max price
- **📝 Geocoding from listing text** — paste any Bulgarian property description and the app extracts the city, neighbourhood and plots it on the map automatically

### 📊 Market Analytics
- Key market metrics: average price, median price, average area, price per m²
- Charts: price by city, distribution by type, price vs area scatter, price/m² by construction type, price histogram, most common features
- Full data table with CSV download

### 🌐 Bilingual
- Full **Bulgarian / English** toggle — switches all labels, filters, charts, bank notes and map tooltips instantly

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/schaubia/property_finder.git
cd property_finder
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📁 Project Structure

```
bg_property_finder/
├── app.py                        # Entry point — language toggle, tab routing
├── requirements.txt
│
├── pages/
│   ├── search.py                 # Search (sample + live scraping + watchlist)
│   ├── mortgage.py               # Mortgage calculator + bank comparison + PDF
│   ├── map_view.py               # Interactive map + geocoding from text
│   └── analytics.py             # Market statistics and charts
│
├── data/
│   ├── sample_data.py            # Generates 100 realistic Bulgarian listings
│   ├── banks.py                  # All 12 banks — rates, LTV, fees, URLs
│   ├── scrapers.py               # imot.bg / imoti.net scraper + BNB rate fetcher
│   └── watchlist_db.py          # SQLite: watchlist, saved searches, scenarios
│
└── utils/
    ├── mortgage_calc.py          # Amortization, DTI, total cost calculations
    ├── geocoding.py              # Location extraction from Bulgarian listing text
    ├── i18n.py                   # Bulgarian / English translation strings
    └── pdf_report.py             # ReportLab PDF mortgage report generator
```

---

## 🏦 Banks Covered

All institutions are sourced from the [EMF Hypostat 2025 Bulgaria report](https://hypo.org) and the ECB supervised institutions list (September 2025).

| Bank | Group | Max LTV | Max Term |
|------|-------|---------|----------|
| DSK Bank | OTP Group (Hungary) | 85% | 35 yr |
| OBB (United Bulgarian Bank) | KBC Group (Belgium) | 80% | 30 yr |
| UniCredit Bulbank | UniCredit (Italy) | 80% | 30 yr |
| Postbank (Eurobank Bulgaria) | Eurobank Ergasias (Greece) | 85% | 35 yr |
| Fibank (First Investment Bank) | Bulgarian private | 85% | 30 yr |
| CCB (Central Cooperative Bank) | Chimimport (Bulgarian) | 85% | 30 yr |
| Allianz Bank Bulgaria | Allianz SE (Germany) | 80% | 30 yr |
| Raiffeisenbank Bulgaria | RBI (Austria) | 80% | 30 yr |
| Investbank | Festa Holding (Bulgarian) | 80% | 30 yr |
| Municipal Bank | Novito Opportunities Fund | 80% | 25 yr |
| BACB | Bulgarian private | 75% | 25 yr |
| D Commerce Bank | Bulgarian private | 70% | 20 yr |

> ⚠️ Interest rates shown are approximate and scraped from public bank websites. Always verify current terms directly with your bank before making any financial decisions.

---

## 🔧 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web app framework |
| `pandas` | Data manipulation |
| `plotly` | Interactive charts |
| `pydeck` | Map visualisation |
| `requests` | HTTP scraping |
| `beautifulsoup4` + `lxml` | HTML parsing |
| `reportlab` | PDF generation |
| `sqlite3` | Watchlist persistence (built-in) |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🗺️ Supported Cities & Geocoding

The geocoding engine recognises listings mentioning:

**Cities:** София, Пловдив, Варна, Бургас, Стара Загора, Русе, Велико Търново, Банско, Несебър, Пазарджик and more.

**Neighbourhood patterns:** `кв. [Квартал]`, `гр. [Град]`, and a dictionary of 40+ known Sofia/Varna/Plovdiv neighbourhoods.

---

## 📋 Roadmap

- [ ] Email alerts for new matching listings
- [ ] Deploy to Streamlit Community Cloud
- [ ] Real-time imot.bg pagination (multiple pages)
- [ ] User authentication for multi-user watchlists
- [ ] Currency converter widget (BGN / EUR / USD / GBP)
- [ ] Neighbourhood price heatmap layer on the map
- [ ] Mobile-optimised layout

---
