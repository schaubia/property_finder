import pandas as pd
import random

# Bulgarian cities and neighborhoods
BULGARIAN_CITIES = {
    "София": ["Лозенец", "Витоша", "Младост", "Люлин", "Надежда", "Красна поляна",
              "Студентски град", "Борово", "Банишора", "Изток", "Гео Милев",
              "Дружба", "Кръстова вада", "Овча купел", "Слатина"],
    "Пловдив": ["Кършияка", "Тракия", "Столипиново", "Смирненски", "Централна",
                "Коматево", "Изток", "Западен"],
    "Варна": ["Левски", "Владиславово", "Младост", "Бриз", "Чайка", "Аспарухово",
              "Центъра", "Гръцка махала", "Галата"],
    "Бургас": ["Меден рудник", "Лазур", "Сарафово", "Центъра", "Братя Миладинови"],
    "Стара Загора": ["Центъра", "Три чучура", "Аязмото", "Казански"],
    "Русе": ["Центъра", "Чародейка", "Дружба", "Здравец"],
    "Велико Търново": ["Центъра", "Колю Фичето", "Картала", "Света гора"],
    "Пловдив - Пазарджик": ["Пазарджик", "Септември", "Ветрен"],
    "Банско": ["Центъра", "Баждар", "Грамадето"],
    "Несебър": ["Стар град", "Слънчев бряг", "Равда"],
}

PROPERTY_TYPES = {
    "Апартамент": "Apartment",
    "Къща": "House",
    "Вила": "Villa",
    "Студио": "Studio",
    "Мезонет": "Maisonette",
    "Атeлие": "Atelier/Loft",
    "Офис": "Office",
    "Гараж": "Garage",
}

CONSTRUCTION_TYPES = ["Тухла", "ЕПК", "Панел", "Гредоред", "Монолит"]

FEATURES = [
    "Паркинг", "Гараж", "Асансьор", "Балкон", "Тераса", "Мазе",
    "Таван", "Двор", "Басейн", "Охрана", "Климатик", "Интерком",
    "Ново строителство", "Обзаведен", "Необзаведен", "Панорама",
    "Близо до метро", "Близо до училище", "Тихо място", "Ъглов апартамент"
]

SAMPLE_DESCRIPTIONS = [
    "Продава се тристаен апартамент в кв. Лозенец, гр. София. Апартаментът е на 4 ет. от 8, с площ 95 кв.м. Разпределение: входно антре, дневна с кухненски бокс, 2 спални, 2 бани/тоалетни. Паркомясто в подземен гараж.",
    "Продавам двустаен апартамент в Младост 1А, близо до НДК метростанция. Панелна конструкция, 52 кв.м, 3 ет./9, голям балкон с гледка към парка. Отлично транспортно обслужване.",
    "Четиристаен апартамент, кв. Витоша. Тухлена сграда от 2019г., 130 кв.м РЗП. Просторен хол с трапезария, 3 спални, 2 бани. Подземен паркинг, охрана, видеонаблюдение. Близо до Природен парк Витоша.",
    "Луксозна вила в Банско, до ски писта. 280 кв.м, 4 спални, 3 бани, хамам, сауна. Напълно обзаведена. Идеална за инвестиция - приходи от наем.",
    "Студио в морски курорт Слънчев бряг, 32 кв.м, 2 ет., в комплекс с басейн и охрана. Напълно обзаведено. Инвестиционен имот.",
    "Двустаен апартамент в Пловдив, кв. Тракия. 62 кв.м, ново строителство 2022г., А-клас енергийна ефективност. Климатик, паркомясто.",
    "Тристаен апартамент Варна Бриз, 85 кв.м, 5/8 ет. Панорама море. Тухла, ново строителство. 2 балкона, климатизация, паркинг.",
]

def generate_sample_properties(n=50):
    """Generate realistic sample Bulgarian property listings."""
    random.seed(42)
    properties = []

    for i in range(n):
        city = random.choice(list(BULGARIAN_CITIES.keys()))
        neighborhood = random.choice(BULGARIAN_CITIES[city])
        prop_type_bg = random.choice(list(PROPERTY_TYPES.keys()))
        construction = random.choice(CONSTRUCTION_TYPES)

        # Realistic price ranges by type and city
        base_price = {
            "Апартамент": 80000, "Къща": 120000, "Вила": 200000,
            "Студио": 50000, "Мезонет": 150000, "Атeлие": 90000,
            "Офис": 100000, "Гараж": 15000
        }[prop_type_bg]

        city_multiplier = {
            "София": 2.2, "Варна": 1.5, "Пловдив": 1.2,
            "Бургас": 1.3, "Банско": 1.4, "Несебър": 1.6
        }.get(city, 1.0)

        price = int(base_price * city_multiplier * random.uniform(0.7, 1.8))
        price = round(price / 1000) * 1000  # round to thousands

        area = {
            "Апартамент": random.randint(45, 150),
            "Къща": random.randint(100, 350),
            "Вила": random.randint(150, 500),
            "Студио": random.randint(25, 50),
            "Мезонет": random.randint(80, 200),
            "Атeлие": random.randint(40, 100),
            "Офис": random.randint(50, 300),
            "Гараж": random.randint(16, 30),
        }[prop_type_bg]

        floors_total = random.randint(3, 15)
        floor = random.randint(1, floors_total)
        rooms = max(1, area // 35 + random.randint(-1, 1))

        num_features = random.randint(2, 8)
        property_features = random.sample(FEATURES, num_features)

        listing_date_days_ago = random.randint(0, 90)
        import datetime
        listing_date = datetime.date.today() - datetime.timedelta(days=listing_date_days_ago)

        desc = random.choice(SAMPLE_DESCRIPTIONS)

        properties.append({
            "id": i + 1,
            "title": f"{prop_type_bg} {area} кв.м, {neighborhood}, {city}",
            "type_bg": prop_type_bg,
            "type_en": PROPERTY_TYPES[prop_type_bg],
            "city": city,
            "neighborhood": neighborhood,
            "price_eur": price,
            "price_bgn": int(price * 1.9558),
            "area_sqm": area,
            "price_per_sqm": round(price / area),
            "floor": floor,
            "floors_total": floors_total,
            "rooms": rooms,
            "construction_type": construction,
            "features": property_features,
            "description": desc,
            "listing_date": listing_date.strftime("%Y-%m-%d"),
            "days_listed": listing_date_days_ago,
            "is_new": listing_date_days_ago <= 7,
            "agency": random.choice(["Arco Real Estate", "Address", "Имотека", "CМА", "Bulgarian Properties", "Nexus"]),
            "contact": f"+359 {random.randint(80,99)} {random.randint(100,999)} {random.randint(100,999)}",
        })

    return pd.DataFrame(properties)


# Bank mortgage data (based on publicly available rates - approximate)
BANK_MORTGAGE_DATA = [
    {
        "bank": "DSK Bank",
        "bank_bg": "ДСК Банк",
        "logo": "🏦",
        "min_rate": 2.45,
        "max_rate": 3.90,
        "promo_rate": 2.45,
        "max_ltv": 85,
        "max_term_years": 30,
        "min_income_bgn": 1200,
        "processing_fee_pct": 1.0,
        "life_insurance": True,
        "property_insurance": True,
        "url": "https://dskbank.bg/individuals/credits/mortgage-credits",
        "notes": "Промоционален лихвен процент за първите 24 месеца",
        "notes_en": "Promotional rate for first 24 months",
        "updated": "2024-01",
    },
    {
        "bank": "UniCredit Bulbank",
        "bank_bg": "УниКредит Булбанк",
        "logo": "🏦",
        "min_rate": 2.60,
        "max_rate": 4.10,
        "promo_rate": 2.60,
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1500,
        "processing_fee_pct": 1.5,
        "life_insurance": True,
        "property_insurance": True,
        "url": "https://www.unicreditbulbank.bg/bg/za-individualni-klienti/krediti/zhilishchni-krediti/",
        "notes": "Фиксирана лихва за 3 или 5 години",
        "notes_en": "Fixed rate for 3 or 5 years",
        "updated": "2024-01",
    },
    {
        "bank": "Postbank",
        "bank_bg": "Пощенска банка",
        "logo": "🏦",
        "min_rate": 2.55,
        "max_rate": 3.80,
        "promo_rate": 2.55,
        "max_ltv": 85,
        "max_term_years": 35,
        "min_income_bgn": 1000,
        "processing_fee_pct": 0.5,
        "life_insurance": True,
        "property_insurance": True,
        "url": "https://www.postbank.bg/bg/individuals/loans/home-loans",
        "notes": "Най-дълъг срок на кредита до 35 години",
        "notes_en": "Longest loan term up to 35 years",
        "updated": "2024-01",
    },
    {
        "bank": "OBB (United Bulgarian Bank)",
        "bank_bg": "ОББ",
        "logo": "🏦",
        "min_rate": 2.70,
        "max_rate": 4.20,
        "promo_rate": 2.70,
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1200,
        "processing_fee_pct": 1.0,
        "life_insurance": True,
        "property_insurance": False,
        "url": "https://www.ubb.bg/individuals/loans/home-loans",
        "notes": "Без такса за управление на кредита",
        "notes_en": "No loan management fee",
        "updated": "2024-01",
    },
    {
        "bank": "Fibank",
        "bank_bg": "Фибанк",
        "logo": "🏦",
        "min_rate": 2.80,
        "max_rate": 4.50,
        "promo_rate": 2.80,
        "max_ltv": 85,
        "max_term_years": 30,
        "min_income_bgn": 1000,
        "processing_fee_pct": 0.8,
        "life_insurance": True,
        "property_insurance": True,
        "url": "https://www.fibank.bg/bg/individuals/credits/home-credits",
        "notes": "Без нотариална такса при избрани нотариуси",
        "notes_en": "No notary fee with selected notaries",
        "updated": "2024-01",
    },
    {
        "bank": "Raiffeisenbank Bulgaria",
        "bank_bg": "Райфайзенбанк България",
        "logo": "🏦",
        "min_rate": 2.90,
        "max_rate": 4.30,
        "promo_rate": 2.90,
        "max_ltv": 80,
        "max_term_years": 30,
        "min_income_bgn": 1500,
        "processing_fee_pct": 1.2,
        "life_insurance": True,
        "property_insurance": True,
        "url": "https://www.raiffeisenbank.bg/individuals/loans/mortgage/",
        "notes": "Безплатна оценка на имота",
        "notes_en": "Free property valuation",
        "updated": "2024-01",
    },
]

# Geocoding lookup for Bulgarian cities (approximate lat/lon)
CITY_COORDS = {
    "София": (42.6977, 23.3219),
    "Пловдив": (42.1354, 24.7453),
    "Варна": (43.2141, 27.9147),
    "Бургас": (42.5048, 27.4626),
    "Стара Zagora": (42.4257, 25.6345),
    "Русе": (43.8564, 25.9745),
    "Велико Търново": (43.0757, 25.6172),
    "Банско": (41.8393, 23.4860),
    "Несебър": (42.6594, 27.7352),
    "Пазарджик": (42.1967, 24.3378),
}

NEIGHBORHOOD_OFFSETS = {
    "Лозенец": (0.005, 0.010),
    "Витоша": (-0.020, -0.005),
    "Младост": (0.015, 0.025),
    "Люлин": (-0.010, -0.030),
    "Надежда": (0.020, -0.015),
    "Студентски град": (0.010, 0.020),
    "Борово": (-0.008, -0.012),
    "Изток": (0.008, 0.018),
}
