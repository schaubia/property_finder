"""
Live property data scrapers:
  - imot.bg listing scraper
  - imoti.net listing scraper  
  - Bulgarian National Bank (BNB) reference interest rate
"""
import requests
from bs4 import BeautifulSoup
import re
import datetime
import streamlit as st

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "bg,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── BNB Reference Interest Rate ───────────────────────────────────────────────

@st.cache_data(ttl=86400)  # cache 24h
def fetch_bnb_reference_rate() -> dict:
    """
    Fetch the current BNB Base Interest Rate (BIR).
    Source: Bulgarian National Bank statistics page.
    Falls back to a known recent value if scraping fails.
    """
    try:
        url = "https://www.bnb.bg/Statistics/StInterestRates/StIRInterestRatesMbBase/index.htm"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            # BNB table has the rate in a structured table
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    text = " ".join(c.get_text(strip=True) for c in cells)
                    match = re.search(r'(\d+[.,]\d+)\s*%', text)
                    if match:
                        rate_val = float(match.group(1).replace(",", "."))
                        if 0.0 <= rate_val <= 5.0:
                            return {
                                "rate": rate_val,
                                "source": "BNB (live)",
                                "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "url": url,
                                "ok": True,
                            }
    except Exception:
        pass

    # Fallback: BNB BIR as of early 2026 (ECB-linked)
    return {
        "rate": 1.81,
        "source": "BNB (fallback – verify at bnb.bg)",
        "fetched_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "url": "https://www.bnb.bg/Statistics/StInterestRates/StIRInterestRatesMbBase/",
        "ok": False,
    }


# ── imot.bg scraper ───────────────────────────────────────────────────────────

IMOTBG_TYPE_MAP = {
    "Апартамент": "1-stаен,2-стаен,3-стаен,4-стаен,многостаен,ателие,мезонет",
    "Къща":       "house",
    "Вила":       "villa",
    "Студио":     "studio",
}

IMOTBG_CITY_CODES = {
    "София":          1,
    "Пловдив":        2,
    "Варна":          3,
    "Бургас":         4,
    "Стара Загора":   6,
    "Русе":           5,
    "Велико Търново": 7,
    "Банско":         48,
}


def _parse_price(text: str) -> int | None:
    """Extract integer price from strings like '120 000 EUR' or '85000 лв.'"""
    text = text.replace(" ", "").replace("\xa0", "")
    m = re.search(r'(\d+)', text.replace(",", "").replace(".", ""))
    if m:
        val = int(m.group(1))
        if 1000 < val < 5_000_000:
            return val
    return None


def _parse_area(text: str) -> float | None:
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:кв\.?м|m²|sq)', text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


@st.cache_data(ttl=1800)  # cache 30min
def scrape_imotbg(city: str = "София", prop_type: str = "Апартамент",
                  max_price_eur: int = 300000, pages: int = 2) -> list[dict]:
    """
    Scrape listings from imot.bg for a given city and type.
    Returns a list of property dicts compatible with the app's data format.
    """
    results = []
    city_code = IMOTBG_CITY_CODES.get(city, 1)
    base_url = "https://www.imot.bg/pcgi/imot.cgi"

    # imot.bg search params (act=3 = search)
    params = {
        "act": "3",
        "slink": "",
        "f1": city_code,
        "f2": "0",   # all neighborhoods
        "f3": "1" if "Апартамент" in prop_type else "2",  # 1=apt, 2=house
        "f4": "",
        "f5": "",
        "f6": str(max_price_eur),
        "f7": "EUR",
    }

    import random
    seen_titles = set()

    for page in range(1, pages + 1):
        params["f0"] = str(page)
        try:
            resp = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                break
            resp.encoding = "windows-1251"
            soup = BeautifulSoup(resp.text, "lxml")

            # imot.bg listing containers
            listings = soup.find_all("table", class_="listItem")
            if not listings:
                # Try alternative selectors
                listings = soup.find_all("div", class_=re.compile(r"listItem|result|listing", re.I))

            for item in listings:
                try:
                    text_all = item.get_text(separator=" ", strip=True)

                    # Title / description
                    title_el = item.find(["a", "h3", "b"])
                    title = title_el.get_text(strip=True) if title_el else text_all[:80]
                    if title in seen_titles or len(title) < 5:
                        continue
                    seen_titles.add(title)

                    # Price
                    price_el = item.find(text=re.compile(r'\d+\s*(?:EUR|лв)', re.I))
                    price_raw = price_el if price_el else ""
                    price_eur = _parse_price(str(price_raw))
                    if not price_eur:
                        price_match = re.search(r'(\d[\d\s]{3,})\s*(EUR|лв)', text_all)
                        if price_match:
                            price_eur = _parse_price(price_match.group(1))
                            if price_match.group(2) == "лв":
                                price_eur = int(price_eur / 1.9558) if price_eur else None

                    # Area
                    area = _parse_area(text_all)

                    # Link
                    link_el = item.find("a", href=True)
                    link = ""
                    if link_el:
                        href = link_el["href"]
                        link = href if href.startswith("http") else "https://www.imot.bg" + href

                    if price_eur and area:
                        results.append({
                            "id": 10000 + len(results),
                            "title": title[:120],
                            "type_bg": prop_type,
                            "type_en": "Apartment" if "Апартамент" in prop_type else prop_type,
                            "city": city,
                            "neighborhood": "",
                            "price_eur": price_eur,
                            "price_bgn": int(price_eur * 1.9558),
                            "area_sqm": area,
                            "price_per_sqm": round(price_eur / area) if area else 0,
                            "floor": 0,
                            "floors_total": 0,
                            "rooms": max(1, int(area // 35)),
                            "construction_type": "Неизвестна",
                            "features": [],
                            "description": text_all[:500],
                            "listing_date": datetime.date.today().strftime("%Y-%m-%d"),
                            "days_listed": 0,
                            "is_new": True,
                            "agency": "imot.bg",
                            "contact": "",
                            "source_url": link,
                            "source": "imot.bg",
                        })
                except Exception:
                    continue
        except Exception:
            break

    return results


@st.cache_data(ttl=1800)
def scrape_imotinet(city: str = "София", prop_type: str = "Апартамент",
                    max_price_eur: int = 300000) -> list[dict]:
    """
    Scrape listings from imoti.net as a secondary source.
    """
    results = []
    city_slug = {
        "София": "sofia", "Пловдив": "plovdiv", "Варна": "varna",
        "Бургас": "burgas", "Банско": "bansko",
    }.get(city, "sofia")

    type_slug = "apartments" if "Апартамент" in prop_type else "houses"
    url = f"https://www.imoti.net/bg/obiavi/r/{city_slug}/{type_slug}/s/forsale/"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return results
        soup = BeautifulSoup(resp.text, "lxml")

        items = soup.find_all("div", class_=re.compile(r"listing|property|offer", re.I))
        for item in items[:20]:
            try:
                text = item.get_text(separator=" ", strip=True)
                price_m = re.search(r'(\d[\d\s,]{2,})\s*(EUR|лв|€)', text)
                area_m  = _parse_area(text)
                title_el = item.find(["h2", "h3", "a"])
                title = title_el.get_text(strip=True) if title_el else text[:80]

                if price_m and area_m:
                    raw_price = _parse_price(price_m.group(1))
                    price_eur = raw_price
                    if price_m.group(2) in ("лв",):
                        price_eur = int(raw_price / 1.9558) if raw_price else None

                    if price_eur and price_eur <= max_price_eur:
                        results.append({
                            "id": 20000 + len(results),
                            "title": title[:120],
                            "type_bg": prop_type,
                            "type_en": "Apartment",
                            "city": city,
                            "neighborhood": "",
                            "price_eur": price_eur,
                            "price_bgn": int(price_eur * 1.9558),
                            "area_sqm": area_m,
                            "price_per_sqm": round(price_eur / area_m),
                            "floor": 0, "floors_total": 0,
                            "rooms": max(1, int(area_m // 35)),
                            "construction_type": "Неизвестна",
                            "features": [], "description": text[:400],
                            "listing_date": datetime.date.today().strftime("%Y-%m-%d"),
                            "days_listed": 0, "is_new": True,
                            "agency": "imoti.net", "contact": "",
                            "source_url": url, "source": "imoti.net",
                        })
            except Exception:
                continue
    except Exception:
        pass

    return results


def get_live_listings(city: str, prop_type: str, max_price: int,
                      force: bool = False) -> tuple[list[dict], str]:
    """
    Fetch live listings from imot.bg + imoti.net, deduplicate by price+area.
    Returns (listings, status_message).
    """
    if force:
        scrape_imotbg.clear()
        scrape_imotinet.clear()

    listings = []
    status_parts = []

    bg = scrape_imotbg(city, prop_type, max_price)
    listings.extend(bg)
    status_parts.append(f"imot.bg: {len(bg)}")

    inet = scrape_imotinet(city, prop_type, max_price)
    listings.extend(inet)
    status_parts.append(f"imoti.net: {len(inet)}")

    # Deduplicate by (price_eur, area_sqm)
    seen = set()
    unique = []
    for l in listings:
        key = (l["price_eur"], round(l.get("area_sqm", 0)))
        if key not in seen:
            seen.add(key)
            unique.append(l)

    status = " | ".join(status_parts) + f" → {len(unique)} unique"
    return unique, status
