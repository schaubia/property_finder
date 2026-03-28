"""
Bilingual strings for the BG Property Finder app.
Usage: from utils.i18n import t, set_lang
"""

TRANSLATIONS = {
    # ── App-wide ──────────────────────────────────────────────────────────
    "app_title":        {"bg": "БГ Имоти", "en": "BG Property Finder"},
    "app_subtitle":     {"bg": "Намерете мечтания си дом в България",
                         "en": "Find your dream home in Bulgaria"},
    "lang_toggle":      {"bg": "🇬🇧 English", "en": "🇧🇬 Български"},

    # ── Tabs ──────────────────────────────────────────────────────────────
    "tab_search":       {"bg": "🔍 Търсене", "en": "🔍 Search"},
    "tab_mortgage":     {"bg": "🏦 Ипотека", "en": "🏦 Mortgage"},
    "tab_map":          {"bg": "🗺️ Карта", "en": "🗺️ Map"},
    "tab_analytics":    {"bg": "📊 Анализи", "en": "📊 Analytics"},

    # ── Search ────────────────────────────────────────────────────────────
    "search_title":     {"bg": "Търсене на имоти", "en": "Property Search"},
    "filter_city":      {"bg": "Град", "en": "City"},
    "filter_city_all":  {"bg": "Всички градове", "en": "All cities"},
    "filter_type":      {"bg": "Тип имот", "en": "Property type"},
    "filter_type_all":  {"bg": "Всички типове", "en": "All types"},
    "filter_price":     {"bg": "Цена (EUR)", "en": "Price (EUR)"},
    "filter_area":      {"bg": "Площ (кв.м)", "en": "Area (sqm)"},
    "filter_rooms":     {"bg": "Стаи", "en": "Rooms"},
    "filter_const":     {"bg": "Конструкция", "en": "Construction"},
    "filter_features":  {"bg": "Специфики", "en": "Features"},
    "filter_new_only":  {"bg": "🆕 Само нови обяви (≤7 дни)", "en": "🆕 New listings only (≤7 days)"},
    "sort_by":          {"bg": "Сортирай по", "en": "Sort by"},
    "sort_price_asc":   {"bg": "Цена ↑", "en": "Price ↑"},
    "sort_price_desc":  {"bg": "Цена ↓", "en": "Price ↓"},
    "sort_area_asc":    {"bg": "Площ ↑", "en": "Area ↑"},
    "sort_area_desc":   {"bg": "Площ ↓", "en": "Area ↓"},
    "sort_sqm":         {"bg": "Цена/м² ↑", "en": "Price/m² ↑"},
    "sort_newest":      {"bg": "Най-нови", "en": "Newest"},
    "results_found":    {"bg": "Намерени имоти", "en": "Properties found"},
    "avg_price":        {"bg": "Средна цена", "en": "Avg. price"},
    "avg_area":         {"bg": "Средна площ", "en": "Avg. area"},
    "avg_sqm":          {"bg": "Ср. цена/м²", "en": "Avg. price/m²"},
    "no_results":       {"bg": "Няма намерени имоти с тези критерии. Разширете търсенето.", "en": "No properties match your filters. Please widen your search."},
    "description":      {"bg": "Описание", "en": "Description"},
    "agency":           {"bg": "Агенция", "en": "Agency"},
    "calc_mortgage":    {"bg": "📊 Изчисли ипотека", "en": "📊 Calculate mortgage"},
    "floors":           {"bg": "ет.", "en": "fl."},
    "rooms_lbl":        {"bg": "стаи", "en": "rooms"},

    # ── Mortgage ──────────────────────────────────────────────────────────
    "mortgage_title":   {"bg": "Ипотечен Калкулатор", "en": "Mortgage Calculator"},
    "mortgage_sub":     {"bg": "Изчислете вноски и сравнете всички банки в България",
                         "en": "Calculate payments and compare all banks in Bulgaria"},
    "currency":         {"bg": "Валута", "en": "Currency"},
    "prop_price":       {"bg": "Цена на имота", "en": "Property price"},
    "down_pmt":         {"bg": "Самоучастие (%)", "en": "Down payment (%)"},
    "loan_amount":      {"bg": "Размер на кредита", "en": "Loan amount"},
    "annual_rate":      {"bg": "Лихвен процент (%)", "en": "Annual interest rate (%)"},
    "term_years":       {"bg": "Срок (години)", "en": "Term (years)"},
    "net_income":       {"bg": "Месечен нетен доход (лв.)", "en": "Monthly net income (BGN)"},
    "monthly_pmt":      {"bg": "Месечна вноска", "en": "Monthly payment"},
    "total_paid":       {"bg": "Общо изплатено", "en": "Total paid"},
    "max_loan":         {"bg": "Макс. кредит", "en": "Max. loan"},
    "affordability":    {"bg": "Достъпност", "en": "Affordability"},
    "affordable":       {"bg": "✅ Достъпно", "en": "✅ Affordable"},
    "stretched":        {"bg": "⚠️ Напрегнато", "en": "⚠️ Stretched"},
    "over_limit":       {"bg": "❌ Над лимита", "en": "❌ Over limit"},
    "cost_breakdown":   {"bg": "Структура на разходите", "en": "Cost breakdown"},
    "principal":        {"bg": "Главница", "en": "Principal"},
    "interest":         {"bg": "Лихви", "en": "Interest"},
    "fees":             {"bg": "Такси", "en": "Fees"},
    "amort_chart":      {"bg": "📈 График на погасяване", "en": "📈 Amortization chart"},
    "bank_offers":      {"bg": "Банкови оферти", "en": "Bank offers"},
    "bank_compare":     {"bg": "Сравнение на месечни вноски", "en": "Monthly payment comparison"},
    "scrape_now":       {"bg": "🔄 Актуализирай лихвите", "en": "🔄 Refresh rates"},
    "scraping":         {"bg": "Зареждам актуални данни…", "en": "Fetching live data…"},
    "scraped_at":       {"bg": "Актуализирано", "en": "Last updated"},
    "disclaimer":       {"bg": "⚠️ Лихвите са приблизителни — проверете актуалните условия директно в банката.",
                         "en": "⚠️ Rates are approximate — always verify current terms directly with your bank."},
    "min_rate":         {"bg": "от", "en": "from"},
    "max_ltv":          {"bg": "Макс. LTV", "en": "Max. LTV"},
    "max_term":         {"bg": "Макс. срок", "en": "Max. term"},
    "proc_fee":         {"bg": "Такса", "en": "Fee"},
    "monthly_est":      {"bg": "Вноска ~", "en": "Payment ~"},
    "visit_bank":       {"bg": "🌐 Посети банката", "en": "🌐 Visit bank"},

    # ── Map ───────────────────────────────────────────────────────────────
    "map_title":        {"bg": "Карта на имотите", "en": "Property Map"},
    "map_browse":       {"bg": "🗺️ Разгледай на карта", "en": "🗺️ Browse map"},
    "map_geocode":      {"bg": "📝 Геокодиране от текст", "en": "📝 Geocode from text"},
    "geocode_title":    {"bg": "Извличане на местоположение от текст", "en": "Extract location from listing text"},
    "geocode_sub":      {"bg": "Поставете текст на обява и системата открива адреса автоматично.",
                         "en": "Paste any listing text and the system pinpoints the location automatically."},
    "geocode_example":  {"bg": "Примерен текст", "en": "Example text"},
    "geocode_own":      {"bg": "Въведи свой текст", "en": "Enter your own text"},
    "geocode_btn":      {"bg": "📍 Намери местоположение", "en": "📍 Find location"},
    "geocode_found":    {"bg": "✅ Намерено местоположение!", "en": "✅ Location found!"},
    "geocode_city":     {"bg": "Град", "en": "City"},
    "geocode_nbh":      {"bg": "Квартал", "en": "Neighborhood"},
    "geocode_coords":   {"bg": "Координати", "en": "Coordinates"},
    "geocode_conf":     {"bg": "Увереност", "en": "Confidence"},
    "geocode_fail":     {"bg": "❌ Не беше намерено местоположение. Опитайте с по-конкретен текст.",
                         "en": "❌ No location found. Try more specific text including city/neighborhood names."},

    # ── Analytics ─────────────────────────────────────────────────────────
    "analytics_title":  {"bg": "Пазарни Анализи", "en": "Market Analytics"},
    "analytics_sub":    {"bg": "Статистики и тенденции на имотния пазар в България",
                         "en": "Statistics and trends on the Bulgarian property market"},
    "total_listings":   {"bg": "Общо обяви", "en": "Total listings"},
    "median_price":     {"bg": "Медианна цена", "en": "Median price"},
    "chart_city":       {"bg": "Средна цена по град (€)", "en": "Avg. price by city (€)"},
    "chart_type":       {"bg": "Разпределение по тип имот", "en": "Distribution by property type"},
    "chart_scatter":    {"bg": "Цена vs Площ по градове", "en": "Price vs Area by city"},
    "chart_box":        {"bg": "Цена/м² по конструкция", "en": "Price/m² by construction"},
    "chart_hist":       {"bg": "Разпределение на цените", "en": "Price distribution"},
    "chart_features":   {"bg": "Най-чести характеристики", "en": "Most common features"},
    "download_csv":     {"bg": "⬇️ Свали данните (CSV)", "en": "⬇️ Download data (CSV)"},
    "all_listings":     {"bg": "Таблица с всички обяви", "en": "All listings table"},
}


def t(key: str, lang: str = "bg") -> str:
    """Translate a key to the given language ('bg' or 'en')."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key  # fallback: return the key itself
    return entry.get(lang, entry.get("en", key))
