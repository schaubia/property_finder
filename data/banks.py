"""
All Bulgarian banks and lending institutions offering mortgages.
Includes live scraping helpers and cached fallback data.
"""
import requests
from bs4 import BeautifulSoup
import datetime
import streamlit as st

# ── Static / fallback data ────────────────────────────────────────────────────
# Rates verified from public bank websites, March 2025.
# Reference: BNB average mortgage rate Dec-2025 = 2.69%

ALL_BANKS = [
    {
        "id": "dsk",
        "bank_en": "DSK Bank",
        "bank_bg": "ДСК Банк",
        "group": "OTP Group (Hungary)",
        "tier": 1,
        "market_share_pct": 27.0,
        "min_rate": 2.25,
        "max_rate": 3.45,
        "promo_rate": 2.25,
        "promo_note_bg": "Плаваща лихва – от 2.25% до 3.45% (DSK Уют Плюс)",
        "promo_note_en": "Variable rate 2.25%–3.45% (DSK Uyut Plus programme)",
        "max_ltv": 85,
        "max_term_years": 35,
        "min_income_bgn": 1200,
        "processing_fee_pct": 1.0,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://dskbank.bg/en/individual-clients/loans/mortgages-loans",
        "website_bg": "https://dskbank.bg/bg/individualni-klienti/krediti/ipotechni-krediti",
        "website_en": "https://dskbank.bg/en/individual-clients/loans/mortgages-loans",
        "phone": "0700 33 944",
        "color": "#005b9a",
    },
    {
        "id": "ubb",
        "bank_en": "United Bulgarian Bank (UBB)",
        "bank_bg": "ОББ (Обединена Българска Банка)",
        "group": "KBC Group (Belgium)",
        "tier": 1,
        "market_share_pct": 22.4,
        "min_rate": 2.41,
        "max_rate": 3.90,
        "promo_rate": 2.41,
        "promo_note_bg": "Фиксирана лихва за първите 3 или 5 години; RIR + марж след това",
        "promo_note_en": "Fixed rate for first 3 or 5 years; RIR + margin thereafter",
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1500,
        "processing_fee_pct": 1.0,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.ubb.bg/en/individual-clients/credits/mortgage-loans",
        "website_bg": "https://www.ubb.bg/bg/individualni-klienti/krediti/ipotechni-krediti",
        "website_en": "https://www.ubb.bg/en/individual-clients/credits/mortgage-loans",
        "phone": "0800 11 822",
        "color": "#00843d",
    },
    {
        "id": "ucb",
        "bank_en": "UniCredit Bulbank",
        "bank_bg": "УниКредит Булбанк",
        "group": "UniCredit (Italy)",
        "tier": 1,
        "market_share_pct": 18.5,
        "min_rate": 2.55,
        "max_rate": 4.10,
        "promo_rate": 2.55,
        "promo_note_bg": "Фиксиран период 3г./5г., след това плаваща лихва",
        "promo_note_en": "Fixed 3yr/5yr period, then floating rate",
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1500,
        "processing_fee_pct": 1.5,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.unicreditbulbank.bg/bg/za-individualni-klienti/krediti/zhilishchni-krediti/",
        "website_bg": "https://www.unicreditbulbank.bg/bg/za-individualni-klienti/krediti/zhilishchni-krediti/",
        "website_en": "https://www.unicreditbulbank.bg/en/for-individual-clients/loans/housing-loans/",
        "phone": "0700 1 84 84",
        "color": "#dd1d21",
    },
    {
        "id": "eurobank",
        "bank_en": "Postbank (Eurobank Bulgaria)",
        "bank_bg": "Пощенска Банка (Eurobank България)",
        "group": "Eurobank Ergasias (Greece)",
        "tier": 1,
        "market_share_pct": 16.5,
        "min_rate": 2.45,
        "max_rate": 3.80,
        "promo_rate": 2.45,
        "promo_note_bg": "Без такса за управление; salary account задължителен",
        "promo_note_en": "No management fee; salary account required",
        "max_ltv": 85,
        "max_term_years": 35,
        "min_income_bgn": 1000,
        "processing_fee_pct": 0.5,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.postbank.bg/bg/individuals/loans/home-loans",
        "website_bg": "https://www.postbank.bg/bg/individuals/loans/home-loans",
        "website_en": "https://www.postbank.bg/en/individuals/loans/home-loans",
        "phone": "0700 18 555",
        "color": "#e8440a",
    },
    {
        "id": "fib",
        "bank_en": "First Investment Bank (Fibank)",
        "bank_bg": "Първа Инвестиционна Банка (Фибанк)",
        "group": "Bulgarian private",
        "tier": 1,
        "market_share_pct": 5.4,
        "min_rate": 2.60,
        "max_rate": 4.20,
        "promo_rate": 2.60,
        "promo_note_bg": "Без нотариална такса при избрани нотариуси",
        "promo_note_en": "No notary fee with selected notaries",
        "max_ltv": 85,
        "max_term_years": 30,
        "min_income_bgn": 1000,
        "processing_fee_pct": 0.8,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.fibank.bg/bg/individuals/credits/home-credits",
        "website_bg": "https://www.fibank.bg/bg/individuals/credits/home-credits",
        "website_en": "https://www.fibank.bg/en/individuals/credits/home-credits",
        "phone": "0800 11 011",
        "color": "#0055a5",
    },
    {
        "id": "ccb",
        "bank_en": "Central Cooperative Bank (CCB)",
        "bank_bg": "Централна Кооперативна Банка (ЦКБ)",
        "group": "Chimimport (Bulgarian)",
        "tier": 2,
        "market_share_pct": 4.2,
        "min_rate": 2.50,
        "max_rate": 3.90,
        "promo_rate": 2.50,
        "promo_note_bg": "Без нотариална такса; до 85% LTV; безплатна имуществена застраховка",
        "promo_note_en": "No notary fee; up to 85% LTV; free property insurance",
        "max_ltv": 85,
        "max_term_years": 30,
        "min_income_bgn": 900,
        "processing_fee_pct": 0.0,
        "free_valuation": True,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.ccbank.bg/en/fl-tes-t/mortgage-loans/mortgage-loan-home-for-you",
        "website_bg": "https://www.ccbank.bg/bg/fizicheski-litsa/krediti/ipotechni-krediti/kredit-dom-za-teb",
        "website_en": "https://www.ccbank.bg/en/fl-tes-t/mortgage-loans/mortgage-loan-home-for-you",
        "phone": "0800 11 100",
        "color": "#006daf",
    },
    {
        "id": "allianz",
        "bank_en": "Allianz Bank Bulgaria",
        "bank_bg": "Алианц Банк България",
        "group": "Allianz SE (Germany)",
        "tier": 2,
        "market_share_pct": 3.5,
        "min_rate": 2.65,
        "max_rate": 4.00,
        "promo_rate": 2.65,
        "promo_note_bg": "Комплексна застраховка живот и имущество включена",
        "promo_note_en": "Bundled life & property insurance included",
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1200,
        "processing_fee_pct": 1.0,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://bank.allianz.bg/bg/individual/credits/mortgage/",
        "website_bg": "https://bank.allianz.bg/bg/individual/credits/mortgage/",
        "website_en": "https://bank.allianz.bg/en/individual/credits/mortgage/",
        "phone": "0700 10 010",
        "color": "#003781",
    },
    {
        "id": "raiffeisen",
        "bank_en": "Raiffeisenbank Bulgaria",
        "bank_bg": "Райфайзенбанк България",
        "group": "Raiffeisen Bank International (Austria)",
        "tier": 2,
        "market_share_pct": 3.0,
        "min_rate": 2.75,
        "max_rate": 4.30,
        "promo_rate": 2.75,
        "promo_note_bg": "Безплатна оценка на имота",
        "promo_note_en": "Free property valuation",
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1500,
        "processing_fee_pct": 1.2,
        "free_valuation": True,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.raiffeisenbank.bg/individuals/loans/mortgage/",
        "website_bg": "https://www.raiffeisenbank.bg/individuals/loans/mortgage/",
        "website_en": "https://www.raiffeisenbank.bg/en/individuals/loans/mortgage/",
        "phone": "0700 10 000",
        "color": "#ffed00",
    },
    {
        "id": "investbank",
        "bank_en": "Investbank",
        "bank_bg": "Инвестбанк",
        "group": "Festa Holding (Bulgarian)",
        "tier": 2,
        "market_share_pct": 1.8,
        "min_rate": 2.80,
        "max_rate": 4.50,
        "promo_rate": 2.80,
        "promo_note_bg": "Гъвкав погасителен план; refinancing опция",
        "promo_note_en": "Flexible repayment; refinancing option available",
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1000,
        "processing_fee_pct": 1.0,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.ibank.bg/krediti/ipotechni-krediti/",
        "website_bg": "https://www.ibank.bg/krediti/ipotechni-krediti/",
        "website_en": "https://www.ibank.bg/krediti/ipotechni-krediti/",
        "phone": "0700 44 555",
        "color": "#1b5ea0",
    },
    {
        "id": "municipal",
        "bank_en": "Municipal Bank",
        "bank_bg": "Общинска Банка",
        "group": "Novito Opportunities Fund (Liechtenstein)",
        "tier": 2,
        "market_share_pct": 0.8,
        "min_rate": 3.00,
        "max_rate": 4.60,
        "promo_rate": 3.00,
        "promo_note_bg": "Специални условия за служители на общини и държавни институции",
        "promo_note_en": "Special terms for municipal and government employees",
        "max_ltv": 80,
        "max_term_years": 25,
        "min_income_bgn": 1000,
        "processing_fee_pct": 1.0,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://www.municipalbank.bg/bg/individuals/credits/mortgage",
        "website_bg": "https://www.municipalbank.bg/bg/individuals/credits/mortgage",
        "website_en": "https://www.municipalbank.bg/en/individuals/credits/mortgage",
        "phone": "02/930 01 01",
        "color": "#8b2131",
    },
    {
        "id": "bacb",
        "bank_en": "Bulgarian-American Credit Bank (BACB)",
        "bank_bg": "Българо-Американска Кредитна Банка (БАКБ)",
        "group": "BACB Group (Bulgarian)",
        "tier": 2,
        "market_share_pct": 0.7,
        "min_rate": 3.20,
        "max_rate": 5.00,
        "promo_rate": 3.20,
        "promo_note_bg": "Включва и Токуда Банк след сливане",
        "promo_note_en": "Includes Tokuda Bank after merger",
        "max_ltv": 75,
        "max_term_years": 25,
        "min_income_bgn": 1200,
        "processing_fee_pct": 1.5,
        "free_valuation": False,
        "life_insurance": True,
        "property_insurance": True,
        "scrape_url": "https://bacb.bg/individuals/loans/mortgage-loans/",
        "website_bg": "https://bacb.bg/individuals/loans/mortgage-loans/",
        "website_en": "https://bacb.bg/individuals/loans/mortgage-loans/",
        "phone": "0700 111 33",
        "color": "#2b5b9c",
    },
    {
        "id": "dbank",
        "bank_en": "D Commerce Bank",
        "bank_bg": "Д Комерс Банк",
        "group": "Bulgarian private",
        "tier": 2,
        "market_share_pct": 0.5,
        "min_rate": 3.50,
        "max_rate": 5.50,
        "promo_rate": 3.50,
        "promo_note_bg": "Специализирани ипотечни продукти за малък бизнес",
        "promo_note_en": "Specialised mortgage products for small businesses",
        "max_ltv": 70,
        "max_term_years": 20,
        "min_income_bgn": 1500,
        "processing_fee_pct": 2.0,
        "free_valuation": False,
        "life_insurance": False,
        "property_insurance": True,
        "scrape_url": "https://www.dcommerce.bg/individuals/credits/",
        "website_bg": "https://www.dcommerce.bg/individuals/credits/",
        "website_en": "https://www.dcommerce.bg/individuals/credits/",
        "phone": "02/9105 100",
        "color": "#4a4a4a",
    },
]


def _try_scrape_rate(bank: dict, timeout: int = 8) -> dict | None:
    """
    Attempt a lightweight scrape of a bank's mortgage page.
    Looks for percentage strings near keywords like 'лихв', 'rate', '%'.
    Returns a dict with scraped fields if found, else None.
    """
    import re
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "bg,en;q=0.9",
    }
    try:
        resp = requests.get(bank["scrape_url"], headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        # Look for percentage patterns near lending keywords
        patterns = [
            r'(\d+[.,]\d+)\s*%',          # 2.75%
            r'от\s+(\d+[.,]\d+)\s*%',     # от 2.75%
            r'from\s+(\d+[.,]\d+)\s*%',   # from 2.75%
        ]
        found_rates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                try:
                    val = float(m.replace(",", "."))
                    if 1.0 <= val <= 12.0:  # sane mortgage rate range
                        found_rates.append(val)
                except ValueError:
                    pass

        if found_rates:
            found_rates.sort()
            return {
                "scraped_min_rate": found_rates[0],
                "scraped_max_rate": found_rates[-1],
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scrape_ok": True,
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600)  # cache for 1 hour
def fetch_live_rates() -> list[dict]:
    """
    Attempt scraping for each bank. Returns merged list with live data
    where available, fallback data otherwise.
    """
    results = []
    for bank in ALL_BANKS:
        b = bank.copy()
        scraped = _try_scrape_rate(bank)
        if scraped and scraped["scrape_ok"]:
            b["live_min_rate"] = scraped["scraped_min_rate"]
            b["live_max_rate"] = scraped["scraped_max_rate"]
            b["scraped_at"] = scraped["scraped_at"]
            b["data_source"] = "live"
        else:
            b["live_min_rate"] = b["min_rate"]
            b["live_max_rate"] = b["max_rate"]
            b["scraped_at"] = "fallback"
            b["data_source"] = "cached"
        results.append(b)
    return results


def get_banks_with_rates(force_refresh: bool = False) -> list[dict]:
    """Return bank list. Uses cached data unless force_refresh=True."""
    if force_refresh:
        fetch_live_rates.clear()
    return fetch_live_rates()
