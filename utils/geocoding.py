import re
from data.sample_data import CITY_COORDS, NEIGHBORHOOD_OFFSETS, BULGARIAN_CITIES
import random


# Extended location keywords
LOCATION_KEYWORDS = {
    # Cities
    "sofia": "София", "софия": "София", "sofiya": "София",
    "plovdiv": "Пловдив", "пловдив": "Пловдив",
    "varna": "Варна", "варна": "Варна",
    "burgas": "Бургас", "бургас": "Бургас",
    "stara zagora": "Стара Zagora", "стара загора": "Стара Zagora",
    "ruse": "Русе", "русе": "Русе",
    "veliko tarnovo": "Велико Търново", "велико търново": "Велико Търново",
    "bansko": "Банско", "банско": "Банско",
    "nessebar": "Несебър", "несебър": "Несебър", "nessebur": "Несебър",
    "sunny beach": "Несебър", "слънчев бряг": "Несебър",
    "pazardzhik": "Пазарджик", "пазарджик": "Пазарджик",
    # Common neighborhoods Sofia
    "лозенец": "София", "lozenets": "София",
    "витоша": "София", "vitosha": "София",
    "младост": "София", "mladost": "София",
    "люлин": "София", "lyulin": "София",
    "надежда": "София", "nadezhda": "София",
    "студентски": "София", "studentski": "София",
    "борово": "София", "borovo": "София",
    "изток": "София", "iztok": "София",
    "гео милев": "София",
    "дружба": "София",
    "банишора": "София",
    # Varna neighborhoods
    "левски": "Варна", "бриз": "Варна", "чайка": "Варна", "владиславово": "Варна",
    # Plovdiv neighborhoods
    "тракия": "Пловдив", "кършияка": "Пловдив", "смирненски": "Пловдив",
    # Burgas
    "меден рудник": "Бургас", "лазур": "Бургас", "сарафово": "Бургас",
}


def extract_location_from_text(text: str) -> dict:
    """
    Parse a property listing description and extract location information.
    Returns a dict with city, neighborhood, and approximate coordinates.
    """
    if not text or not text.strip():
        return {"found": False, "city": None, "neighborhood": None, "lat": None, "lon": None, "confidence": 0}

    text_lower = text.lower()
    found_city = None
    found_neighborhood = None
    confidence = 0

    # Try matching known location keywords
    for keyword, city in LOCATION_KEYWORDS.items():
        if keyword in text_lower:
            found_city = city
            confidence = max(confidence, 0.7)
            # Check if keyword is a neighborhood
            for city_name, neighborhoods in BULGARIAN_CITIES.items():
                for nbh in neighborhoods:
                    if nbh.lower() in text_lower:
                        found_neighborhood = nbh
                        if city_name == found_city:
                            confidence = 0.95
                        break

    # Try regex for "кв. <name>" pattern (кв. = квартал = neighborhood)
    kv_match = re.search(r'кв\.?\s+([А-Яа-я\s]+?)[\s,\.]', text)
    if kv_match:
        nbh_candidate = kv_match.group(1).strip()
        found_neighborhood = nbh_candidate
        confidence = max(confidence, 0.8)

    # Try regex for "гр. <name>" pattern (гр. = город = city)
    gr_match = re.search(r'гр\.?\s+([А-Яа-я]+)', text)
    if gr_match:
        city_candidate = gr_match.group(1).strip()
        # Try to match to known cities
        for city_name in CITY_COORDS.keys():
            if city_candidate.lower() in city_name.lower() or city_name.lower() in city_candidate.lower():
                found_city = city_name
                confidence = max(confidence, 0.9)
                break

    # Resolve coordinates
    lat, lon = None, None
    if found_city and found_city in CITY_COORDS:
        base_lat, base_lon = CITY_COORDS[found_city]

        if found_neighborhood and found_neighborhood in NEIGHBORHOOD_OFFSETS:
            dlat, dlon = NEIGHBORHOOD_OFFSETS[found_neighborhood]
        else:
            # Small random offset within city bounds
            dlat = random.uniform(-0.025, 0.025)
            dlon = random.uniform(-0.025, 0.025)

        lat = base_lat + dlat
        lon = base_lon + dlon

    return {
        "found": found_city is not None,
        "city": found_city,
        "neighborhood": found_neighborhood,
        "lat": lat,
        "lon": lon,
        "confidence": confidence,
        "confidence_label": (
            "Висока" if confidence >= 0.85 else
            "Средна" if confidence >= 0.65 else
            "Ниска"
        )
    }


def get_property_coords(row) -> tuple:
    """Get coordinates for a property DataFrame row."""
    city = row.get("city", "")
    neighborhood = row.get("neighborhood", "")

    if city in CITY_COORDS:
        base_lat, base_lon = CITY_COORDS[city]
        if neighborhood in NEIGHBORHOOD_OFFSETS:
            dlat, dlon = NEIGHBORHOOD_OFFSETS[neighborhood]
        else:
            # Deterministic offset based on property id
            seed = hash(f"{city}{neighborhood}{row.get('id', 0)}") % 1000
            random.seed(seed)
            dlat = random.uniform(-0.02, 0.02)
            dlon = random.uniform(-0.02, 0.02)
        return (base_lat + dlat, base_lon + dlon)
    return (42.6977, 23.3219)  # Default to Sofia
