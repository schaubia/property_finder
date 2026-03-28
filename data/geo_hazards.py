"""
Geo-hazard data for Bulgaria.
Sources:
  - Seismic: NIGGG-BAS (Bulgarian Academy of Sciences) + SHARE/ESHM20 European Seismic Hazard Model
  - Flood:   EU Floods Directive WMS (INSPIRE Geoportal Bulgaria)
  - Radon:   EU JRC Atlas of Natural Radiation + National radon survey 2015-16 (NCRRP Bulgaria)
  - Landslide: EU JRC Global Landslide Susceptibility + Bulgarian Geological Survey data

All data is polygon/point-based and stored as structured dicts with lat/lon bounds.
The GeoRiskLayer class returns a risk_score (0-1) and metadata for any given coordinate.
"""
import math
import requests
import datetime
import streamlit as st

# ── Seismic hazard zones (PGA in g, 475-year return period, Eurocode 8) ────────
# Source: Simeonova et al. 2006, NHESS; updated with ESHM20
# Zones defined as (lat_min, lat_max, lon_min, lon_max, PGA_g, zone_name, description)
SEISMIC_ZONES = [
    # High hazard zones (PGA ≥ 0.20g)
    (41.8, 42.5, 23.0, 24.0, 0.27, "Kresna-Strymon",
     "High seismic zone — Kresna fault system. Historical M6.8+ earthquakes."),
    (42.4, 42.9, 23.0, 23.8, 0.24, "Sofia Basin",
     "High seismic zone — Sofia graben. Active faults beneath the city."),
    (41.7, 42.2, 25.2, 26.2, 0.22, "Plovdiv-Maritsa",
     "High seismic zone — Maritsa fault zone. Significant historical seismicity."),
    (43.4, 43.9, 28.3, 28.7, 0.20, "Shabla (Black Sea coast)",
     "High seismic zone — offshore faults. 1901 M7.2 Shabla earthquake."),
    (43.0, 43.6, 25.5, 26.5, 0.20, "Gorna Oryahovitsa",
     "Moderate-high zone — Sub-Balkan graben system."),
    # Moderate hazard zones (PGA 0.10–0.20g)
    (42.5, 43.2, 27.0, 28.5, 0.15, "Varna region",
     "Moderate seismic zone — influenced by Vrancea deep earthquakes (Romania)."),
    (43.5, 44.2, 22.5, 26.0, 0.14, "Danube Plain (north)",
     "Moderate zone — influenced by Vrancea seismic source."),
    (42.0, 42.8, 26.0, 28.0, 0.13, "Eastern Rhodopes / Stara Zagora",
     "Moderate zone — local faults and Vrancea influence."),
    (41.9, 42.6, 22.5, 23.2, 0.15, "Blagoevgrad-Struma valley",
     "Moderate-high zone — active Struma fault corridor."),
    (42.6, 43.5, 23.8, 25.5, 0.12, "Central Balkan / Gabrovo",
     "Moderate zone — Balkan Range fault system."),
    # Lower hazard zones (PGA < 0.10g)
    (43.3, 44.2, 26.0, 28.5, 0.08, "Dobrudzha / Northeast Bulgaria",
     "Lower seismic zone — stable platform region."),
    (41.8, 42.3, 27.5, 28.5, 0.09, "Southeast Bulgaria / Burgas hinterland",
     "Lower-moderate zone."),
]

# ── Flood risk zones (EU Floods Directive, 2023 cycle) ───────────────────────
# Risk levels: 0=none, 1=low, 2=medium, 3=high
# Source: INSPIRE Geoportal Bulgaria WMS + basin shapefile data
FLOOD_ZONES = [
    # Danube / Iskar floodplain
    (43.6, 44.2, 23.5, 26.5, 3, "Danube floodplain",
     "High flood risk — Danube river and major tributaries. Frequent inundation events."),
    (43.0, 43.7, 23.5, 24.3, 3, "Iskar River valley",
     "High flood risk — Iskar River corridor, Sofia to Danube."),
    # Maritsa basin
    (41.9, 42.5, 24.5, 26.5, 3, "Maritsa / Upper Thracian Plain",
     "High flood risk — Maritsa River and Plovdiv region. Major 2022 flood event."),
    (41.6, 42.2, 26.0, 26.8, 2, "Maritsa lower reach",
     "Medium flood risk — lower Maritsa towards Turkey."),
    # Black Sea coastal rivers
    (42.8, 43.5, 27.5, 28.5, 2, "Kamchiya / Black Sea rivers",
     "Medium flood risk — coastal river systems."),
    (42.3, 42.8, 27.2, 27.9, 2, "Tundzha River",
     "Medium flood risk — Tundzha basin (tributary of Maritsa)."),
    # Mountain rivers
    (41.8, 42.2, 23.0, 24.5, 2, "Struma / Rila foothills",
     "Medium flood risk — rapid mountain runoff after heavy rain."),
    (43.0, 43.6, 24.8, 26.0, 1, "Yantra River valley",
     "Low-medium flood risk."),
    # Low risk
    (42.5, 43.5, 25.0, 27.0, 1, "Central Bulgaria plateau",
     "Generally low flood risk — plateau terrain."),
    (41.8, 42.3, 24.0, 25.5, 1, "Plovdiv uplands",
     "Low flood risk away from river channels."),
]

# ── Radon risk zones (Bq/m³ annual average) ──────────────────────────────────
# Source: National Radon Survey Bulgaria 2015-16 (NCRRP/BNRA)
#         + EU JRC Atlas of Natural Radiation (remon.jrc.ec.europa.eu)
# EU reference level: 300 Bq/m³. Bulgarian national average: 111 Bq/m³.
RADON_ZONES = [
    # High radon — granite/gneiss geology
    (41.7, 42.3, 23.0, 24.2, 220, "Rila-Rhodope granites",
     "Elevated radon — granite and gneiss basement. Rhodope massif known for higher radon."),
    (41.8, 42.2, 22.9, 23.5, 200, "Pirin Mountains",
     "Elevated radon — Pirin granite massif."),
    (42.0, 42.6, 23.5, 24.0, 175, "Southwest Sofia environs",
     "Moderately elevated radon — Vitosha granites and metamorphics."),
    (42.5, 43.1, 24.5, 25.5, 160, "Sredna Gora / Koprivshtitsa",
     "Moderately elevated — volcanic and metamorphic rocks."),
    # Medium radon
    (42.4, 43.0, 23.2, 24.5, 120, "Sofia City / Sofia Plain",
     "Average radon levels — alluvial plain with varied geology."),
    (42.1, 42.6, 24.5, 25.5, 115, "Plovdiv region",
     "Near-average radon — Thracian Plain sediments."),
    (43.1, 43.7, 27.5, 28.5, 100, "Varna coastal zone",
     "Below-average radon — Black Sea coastal sediments."),
    (42.3, 43.0, 27.0, 28.0, 95, "Burgas region",
     "Below-average radon — coastal sedimentary geology."),
    # Low radon — sedimentary basins
    (43.5, 44.2, 23.0, 28.5, 75, "Danubian Plain",
     "Low radon — thick Neogene sediment cover, dilutes radon emanation."),
    (41.8, 42.5, 26.0, 28.0, 90, "Eastern Thrace / Stara Zagora",
     "Low-moderate radon — sedimentary basin."),
]

# ── Landslide susceptibility ──────────────────────────────────────────────────
# Source: EU JRC Global Landslide Susceptibility Map + Bulgarian Geological Survey
# Levels: 0=very low, 1=low, 2=medium, 3=high, 4=very high
LANDSLIDE_ZONES = [
    (41.8, 42.5, 23.0, 24.5, 4, "Rila / Rhodope slopes",
     "Very high landslide susceptibility — steep terrain, frequent landslides after rain."),
    (41.8, 42.4, 22.8, 23.5, 4, "Pirin slopes",
     "Very high susceptibility — steep mountain slopes, active mass movements."),
    (42.4, 43.2, 24.5, 26.0, 3, "Balkan Range southern slopes",
     "High susceptibility — Stara Planina steep inclines."),
    (43.2, 43.8, 24.0, 26.0, 3, "Pre-Balkan hills",
     "High susceptibility — hilly terrain with clay-rich soils."),
    (42.5, 43.3, 22.8, 24.0, 2, "Vitosha / Plana foothills",
     "Moderate susceptibility — periurban Sofia area."),
    (43.0, 43.7, 27.5, 28.5, 1, "Black Sea coastal cliffs",
     "Low-moderate — coastal erosion and minor slides on sea cliffs."),
    (43.5, 44.2, 23.0, 28.5, 0, "Danubian Plain",
     "Very low susceptibility — flat plain."),
    (42.0, 42.8, 25.0, 27.5, 1, "Eastern Rhodope foothills",
     "Low-moderate susceptibility."),
]


# ── Lookup helpers ────────────────────────────────────────────────────────────

def _point_in_zone(lat, lon, zone):
    lat_min, lat_max, lon_min, lon_max = zone[0], zone[1], zone[2], zone[3]
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def _closest_zone(lat, lon, zones):
    """Find the zone whose centre is closest to the point."""
    best, best_dist = None, float("inf")
    for z in zones:
        clat = (z[0] + z[1]) / 2
        clon = (z[2] + z[3]) / 2
        d = math.sqrt((lat - clat) ** 2 + (lon - clon) ** 2)
        if d < best_dist:
            best_dist, best = d, z
    return best


def get_seismic_risk(lat: float, lon: float) -> dict:
    for z in SEISMIC_ZONES:
        if _point_in_zone(lat, lon, z):
            pga = z[4]
            score = min(1.0, pga / 0.30)
            level = "🔴 High" if pga >= 0.20 else "🟠 Moderate" if pga >= 0.12 else "🟡 Low-moderate"
            return {"score": round(score, 2), "pga_g": pga, "level": level,
                    "zone": z[5], "description": z[6], "source": "ESHM20 / NIGGG-BAS"}
    z = _closest_zone(lat, lon, SEISMIC_ZONES)
    pga = z[4] * 0.7
    return {"score": round(min(1.0, pga / 0.30), 2), "pga_g": round(pga, 3),
            "level": "🟢 Low", "zone": "Outside mapped zone (estimate)",
            "description": "No specific seismic zone data. Estimated from nearest zone.",
            "source": "ESHM20 estimate"}


def get_flood_risk(lat: float, lon: float) -> dict:
    for z in FLOOD_ZONES:
        if _point_in_zone(lat, lon, z):
            lvl = z[4]
            labels = {0: "🟢 None", 1: "🟡 Low", 2: "🟠 Medium", 3: "🔴 High"}
            return {"score": round(lvl / 3, 2), "level_num": lvl,
                    "level": labels[lvl], "zone": z[5], "description": z[6],
                    "source": "EU Floods Directive 2007/60/EC — Bulgaria 2023 cycle"}
    return {"score": 0.05, "level_num": 0, "level": "🟢 Very low",
            "zone": "No flood zone mapped", "description": "Area not identified in EU flood hazard mapping.",
            "source": "EU Floods Directive"}


def get_radon_risk(lat: float, lon: float) -> dict:
    for z in RADON_ZONES:
        if _point_in_zone(lat, lon, z):
            bq = z[4]
            score = min(1.0, bq / 300)
            level = ("🔴 Elevated (>200 Bq/m³)" if bq > 200
                     else "🟠 Moderate (150-200)" if bq > 150
                     else "🟡 Average (100-150)" if bq > 100
                     else "🟢 Low (<100 Bq/m³)")
            return {"score": round(score, 2), "bq_m3": bq, "level": level,
                    "zone": z[5], "description": z[6],
                    "eu_reference": 300,
                    "source": "NCRRP Bulgaria National Radon Survey 2015-16 + EU JRC REMON Atlas"}
    z = _closest_zone(lat, lon, RADON_ZONES)
    bq = int(z[4] * 0.9)
    return {"score": round(min(1.0, bq / 300), 2), "bq_m3": bq,
            "level": "🟡 Average", "zone": "Estimated from nearest zone",
            "description": "No direct measurement data. Estimated from nearest survey zone.",
            "eu_reference": 300, "source": "EU JRC REMON Atlas (estimate)"}


def get_landslide_risk(lat: float, lon: float) -> dict:
    for z in LANDSLIDE_ZONES:
        if _point_in_zone(lat, lon, z):
            lvl = z[4]
            labels = {0: "🟢 Very low", 1: "🟡 Low", 2: "🟠 Moderate",
                      3: "🔴 High", 4: "🔴 Very high"}
            return {"score": round(lvl / 4, 2), "level_num": lvl,
                    "level": labels[lvl], "zone": z[5], "description": z[6],
                    "source": "EU JRC Global Landslide Susceptibility + Bulgarian Geological Survey"}
    return {"score": 0.1, "level_num": 1, "level": "🟡 Low",
            "zone": "No specific data", "description": "Low susceptibility based on terrain type.",
            "source": "EU JRC estimate"}


def get_all_hazards(lat: float, lon: float) -> dict:
    """Return all hazard scores for a coordinate."""
    seismic   = get_seismic_risk(lat, lon)
    flood     = get_flood_risk(lat, lon)
    radon     = get_radon_risk(lat, lon)
    landslide = get_landslide_risk(lat, lon)
    # uranium: evaluated lazily to avoid circular dependency at module load
    # (URANIUM_MINES defined later in file)
    uranium = {"score": 0.0, "level": "🟢 Not evaluated", "found": False}

    # Composite risk score (weighted — uranium adds up to 0.15 if nearby)
    uranium_score = uranium.get("score", 0)
    composite = round(
        seismic["score"]   * 0.30 +
        flood["score"]     * 0.25 +
        radon["score"]     * 0.20 +
        landslide["score"] * 0.15 +
        uranium_score      * 0.10,
        2
    )
    overall = ("🔴 High risk" if composite >= 0.55
               else "🟠 Moderate risk" if composite >= 0.35
               else "🟡 Low-moderate" if composite >= 0.20
               else "🟢 Low risk")

    return {
        "lat": lat, "lon": lon,
        "composite_score": composite,
        "overall": overall,
        "seismic":   seismic,
        "flood":     flood,
        "radon":     radon,
        "landslide": landslide,
        "uranium":   uranium,
        "assessed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def get_all_hazards_full(lat: float, lon: float) -> dict:
    """Like get_all_hazards but also evaluates uranium mines (call after module fully loaded)."""
    h = get_all_hazards(lat, lon)
    uranium = get_uranium_mine_risk(lat, lon)
    uranium_score = uranium["score"]
    h["uranium"] = uranium
    h["composite_score"] = round(
        h["seismic"]["score"]   * 0.30 +
        h["flood"]["score"]     * 0.25 +
        h["radon"]["score"]     * 0.20 +
        h["landslide"]["score"] * 0.15 +
        uranium_score           * 0.10,
        2
    )
    overall = ("🔴 High risk" if h["composite_score"] >= 0.55
               else "🟠 Moderate risk" if h["composite_score"] >= 0.35
               else "🟡 Low-moderate" if h["composite_score"] >= 0.20
               else "🟢 Low risk")
    h["overall"] = overall
    return h


@st.cache_data(ttl=86400)
def fetch_recent_earthquakes_bg() -> list[dict]:
    """
    Fetch recent earthquakes in Bulgaria from USGS Earthquake API.
    Free, no key required. Covers M2.5+ in Bulgaria bounding box.
    """
    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "minlatitude": 41.2, "maxlatitude": 44.3,
            "minlongitude": 22.3, "maxlongitude": 28.8,
            "minmagnitude": 2.5,
            "orderby": "time",
            "limit": 50,
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            quakes = []
            for feat in data.get("features", []):
                p = feat["properties"]
                c = feat["geometry"]["coordinates"]
                quakes.append({
                    "mag":   round(p.get("mag", 0), 1),
                    "place": p.get("place", ""),
                    "time":  datetime.datetime.fromtimestamp(p["time"] / 1000).strftime("%Y-%m-%d %H:%M"),
                    "depth": round(c[2], 1),
                    "lon":   round(c[0], 3),
                    "lat":   round(c[1], 3),
                    "url":   p.get("url", ""),
                })
            return quakes
    except Exception:
        pass
    return []


# City-level hazard summary (pre-computed for the main Bulgarian cities)
CITY_HAZARD_SUMMARY = {
    "София":          get_all_hazards(42.697, 23.322),
    "Пловдив":        get_all_hazards(42.135, 24.745),
    "Варна":          get_all_hazards(43.214, 27.915),
    "Бургас":         get_all_hazards(42.505, 27.463),
    "Стара Загора":   get_all_hazards(42.426, 25.634),
    "Русе":           get_all_hazards(43.856, 25.975),
    "Велико Търново": get_all_hazards(43.076, 25.617),
    "Банско":         get_all_hazards(41.839, 23.486),
    "Несебър":        get_all_hazards(42.659, 27.735),
    "Пазарджик":      get_all_hazards(42.197, 24.338),
}


# ── Uranium mines & legacy sites ─────────────────────────────────────────────
# Sources:
#   - WISE Uranium Project decommissioning data (wise-uranium.org/uddbg.html)
#   - IAEA-TECDOC-865 / IAEA-TECDOC-982
#   - Dolchinkov et al. 2025 "Uranium Mines in Bulgaria — 30 Years After Closure"
#   - PubMed 26505204: surface water uranium 3x above background near mine sites
#
# Bulgaria total production: ~16,720 t U (1944–1992). 48 mines, 2 processing plants.
# State company Ecoengineering RM handles liquidation under Decree No.74/1998.

URANIUM_MINES = [
    {
        "name": "Buhovo / Seslavtsi",
        "name_bg": "Бухово / Сеславци",
        "lat": 42.773, "lon": 23.548,
        "region": "Sofia Province",
        "type": "Underground mine + Waste heaps + Mill tailings",
        "operator": "Podzemno stroitelstvo / Metalurg",
        "active_period": "1938–1992",
        "status": "Partially reclaimed — tailings 'conserved'",
        "contamination_level": "High",
        "risk_score": 0.85,
        "notes_en": "Largest waste rock deposit in Bulgaria: 200 heaps, 47.5 ha, 7.9 Mt. "
                    "Mill tailings (Metalurg Buhovo): 90 ha, 8.32 Mt — status 'conserved', not fully remediated. "
                    "Ore used to produce first Soviet atomic bomb. Ongoing groundwater contamination.",
        "notes_bg": "Най-голямото отвалище за скална маса в България: 200 купища, 47.5 ха, 7.9 Мт. "
                    "Хвостохранилище 'Металург Бухово': 90 ха — статус 'консервиран', не напълно рекултивиран. "
                    "Продължаващо замърсяване на подземни води.",
        "source": "WISE Uranium / IAEA-TECDOC-865",
    },
    {
        "name": "Eleshnitsa (Zvezda plant)",
        "name_bg": "Елешница (завод 'Звезда')",
        "lat": 41.887, "lon": 23.576,
        "region": "Blagoevgrad Province (~10 km NW of Bansko)",
        "type": "Underground + Processing plant + Mill tailings + ISL",
        "operator": "Redki Metali Ltd.",
        "active_period": "1945–1992 (plant closed 2005)",
        "status": "Partially reclaimed — liquid radwaste pond reclaimed, soils remain contaminated",
        "contamination_level": "High",
        "risk_score": 0.90,
        "notes_en": "Largest uranium processing plant in Bulgaria. 43 waste rock heaps (15.3 ha, 2.9 Mt). "
                    "Mill tailings: 42 ha, 7.68 Mt. Liquid radwaste pond reclaimed (now pine forest). "
                    "Surrounding soils and mine drainage remain contaminated.",
        "notes_bg": "Най-голямото преработвателно предприятие за уран. 43 отвала (15.3 ха). "
                    "Хвостохранилище: 42 ха, 7.68 Мт. Течното хвостохранилище е рекултивирано. "
                    "Почвите и дренажът от мините остават замърсени.",
        "source": "WISE Uranium / Dolchinkov et al. 2025",
    },
    {
        "name": "Smolyan (Shafts 7 & 8)",
        "name_bg": "Смолян (шахти 7 и 8)",
        "lat": 41.577, "lon": 24.703,
        "region": "Smolyan / Central Rhodopes",
        "type": "Underground + Stope leach",
        "operator": "Redki Metali Ltd.",
        "active_period": "1955–1992",
        "status": "Closed — partial reclamation",
        "contamination_level": "Moderate-High",
        "risk_score": 0.65,
        "notes_en": "12 waste rock heaps (7.1 ha, 1.24 Mt). Rhodope granite geology amplifies radon emanation. "
                    "Surface water uranium elevated downstream from mine drainage.",
        "notes_bg": "12 купища скална маса (7.1 ха). Гранитната геология усилва радоновото отделяне. "
                    "Повишен уран в повърхностни води надолу по течението.",
        "source": "WISE Uranium / IAEA-TECDOC-865",
    },
    {
        "name": "Barutin / Borino / Dospat",
        "name_bg": "Барутин / Борино / Доспат",
        "lat": 41.680, "lon": 24.190,
        "region": "Rhodopes (Devin-Dospat area)",
        "type": "Underground",
        "operator": "Redki Metali Ltd.",
        "active_period": "1960s–1992",
        "status": "Closed — monitoring required",
        "contamination_level": "Moderate",
        "risk_score": 0.55,
        "notes_en": "13 waste rock heaps at Barutin (1.4 ha, 0.2 Mt). Deep Rhodope region. "
                    "Dolchinkov 2025 identifies Borino, Dospat and Satovcha as sites still requiring environmental monitoring.",
        "notes_bg": "13 купища при Барутин. Долчинков 2025 идентифицира Борино, Доспат и Сатовча "
                    "като обекти, изискващи продължаващ екологичен мониторинг.",
        "source": "Dolchinkov et al. 2025 / WISE Uranium",
    },
    {
        "name": "Kostenets / Dolna Banya",
        "name_bg": "Костенец / Долна Баня",
        "lat": 42.303, "lon": 23.862,
        "region": "Sofia Province (Kostenets area)",
        "type": "Underground",
        "operator": "Various",
        "active_period": "1950s–1992",
        "status": "Closed — waste heaps remain",
        "contamination_level": "Moderate",
        "risk_score": 0.50,
        "notes_en": "3 waste rock heaps at Dolna Banya (1.2 ha, 0.22 Mt). "
                    "Proposal to use closed mine as landfill was rejected.",
        "notes_bg": "3 купища при Долна Баня. Предложение за превръщане на закритата мина "
                    "в депо за отпадъци беше отхвърлено.",
        "source": "Dolchinkov et al. 2025",
    },
    {
        "name": "Narechen (Rhodopes)",
        "name_bg": "Наречен (Родопи)",
        "lat": 41.868, "lon": 24.618,
        "region": "Plovdiv Province / Western Rhodopes",
        "type": "Open pit + Underground",
        "operator": "Georedmet Ltd.",
        "active_period": "1960s–1992",
        "status": "Closed",
        "contamination_level": "Moderate",
        "risk_score": 0.50,
        "notes_en": "Near Narechen spa resort. Rhodope granite basement. Radon in thermal mineral "
                    "springs actively used in balneotherapy — naturally elevated radiation in area.",
        "notes_bg": "Близо до курорт Наречен. Радонът в минералните извори се използва в балнеологията. "
                    "Естествено повишена радиация в района.",
        "source": "WISE Uranium",
    },
    {
        "name": "Smolyanovtsi (Vidin area)",
        "name_bg": "Смоляновци (Видинско)",
        "lat": 43.755, "lon": 22.905,
        "region": "Montana / Vidin",
        "type": "Underground + Heap leach",
        "operator": "Redki Metali Ltd.",
        "active_period": "1970s–1992",
        "status": "Closed — waste heap present",
        "contamination_level": "Moderate",
        "risk_score": 0.48,
        "notes_en": "1 waste rock heap (3.9 ha, 0.48 Mt). Northern Bulgaria sandstone-type deposit. "
                    "Lower contamination than Rhodope sites.",
        "notes_bg": "1 купище скална маса (3.9 ха). По-ниско замърсяване в сравнение с Родопските обекти.",
        "source": "WISE Uranium / IAEA-TECDOC-865",
    },
    {
        "name": "Sliven",
        "name_bg": "Сливен",
        "lat": 42.683, "lon": 26.320,
        "region": "Sliven",
        "type": "Underground",
        "operator": "Geostroikompekt Ltd.",
        "active_period": "1960s–1992",
        "status": "Closed",
        "contamination_level": "Moderate",
        "risk_score": 0.42,
        "notes_en": "18 waste rock heaps (2.7 ha, 0.14 Mt). Mostly exploratory mining.",
        "notes_bg": "18 купища скална маса. Предимно проучвателен добив.",
        "source": "WISE Uranium / IAEA-TECDOC-865",
    },
    # ISL (In-Situ Leach) sites — primary risk is groundwater contamination
    {
        "name": "Selishte ISL (Plovdiv Plain)",
        "name_bg": "Селище ИСЛ (Пловдивско)",
        "lat": 42.310, "lon": 24.620,
        "region": "Plovdiv Province",
        "type": "In-Situ Leach — groundwater contamination",
        "operator": "Trakia RM Ltd.",
        "active_period": "1975–1992",
        "status": "Closed — groundwater monitoring required",
        "contamination_level": "High (groundwater)",
        "risk_score": 0.75,
        "notes_en": "385 ha — largest single ISL site in Bulgaria. Acid/alkali injection left "
                    "contaminated groundwater plumes. Uranium in nearby monitoring wells 2–3× background. "
                    "WHO drinking water limit: 0.03 mg/L; mine drainage up to 6.8 mg/L recorded.",
        "notes_bg": "385 ха — най-голямото ИСЛ находище. Замърсени подземни води с уран "
                    "2–3 пъти над фоновите стойности. В минните води уран до 6.8 мг/л (СЗО лимит: 0.03 мг/л).",
        "source": "WISE Uranium / PubMed 26505204",
    },
    {
        "name": "Momino / Rakovski ISL cluster",
        "name_bg": "Момино / Раковски ИСЛ клъстер",
        "lat": 42.268, "lon": 24.963,
        "region": "Plovdiv Province (Thracian Plain)",
        "type": "In-Situ Leach cluster",
        "operator": "Trakia RM Ltd.",
        "active_period": "1975–1992",
        "status": "Closed — known groundwater contamination",
        "contamination_level": "High (groundwater)",
        "risk_score": 0.80,
        "notes_en": "Momino (215.5 ha) + Rakovski (271.1 ha). Major ISL cluster in Thracian Plain. "
                    "WISE Uranium flags known ongoing groundwater contamination issues.",
        "notes_bg": "Момино (215.5 ха) + Раковски (271.1 ха). WISE отбелязва продължаващи "
                    "проблеми с подземните води.",
        "source": "WISE Uranium / PubMed 26505204",
    },
    {
        "name": "Orlov Dol ISL (Stara Zagora area)",
        "name_bg": "Орлов Дол ИСЛ (Старозагорско)",
        "lat": 42.390, "lon": 25.810,
        "region": "Stara Zagora",
        "type": "In-Situ Leach + adjacent cluster",
        "operator": "Trakia RM Ltd.",
        "active_period": "1975–1992",
        "status": "Closed — issues flagged",
        "contamination_level": "Moderate-High",
        "risk_score": 0.65,
        "notes_en": "242 ha ISL. Stara Zagora region has several ISL sites "
                    "(Vladimirovo, Cheshmata, Belozem, Trilistnik, Navusen, Debar). "
                    "WISE Uranium flags known issues at Orlov Dol.",
        "notes_bg": "242 ха ИСЛ. Старозагорският район включва множество ИСЛ обекти. "
                    "WISE отбелязва проблеми при Орлов Дол.",
        "source": "WISE Uranium",
    },
]

CONTAMINATION_COLORS = {
    "High":               [192, 57, 43],
    "High (groundwater)": [150, 30, 100],
    "Moderate-High":      [224, 112, 32],
    "Moderate":           [240, 180, 41],
    "Low":                [26, 138, 90],
}


def get_uranium_mine_risk(lat: float, lon: float, radius_deg: float = 0.25) -> dict:
    """
    Check if a coordinate is within ~28 km of any known uranium mine / legacy site.
    Returns the nearest site(s) and risk info.
    """
    nearby = []
    for m in URANIUM_MINES:
        dist = math.sqrt((lat - m["lat"]) ** 2 + (lon - m["lon"]) ** 2)
        if dist <= radius_deg:
            nearby.append({**m, "distance_km": round(dist * 111, 1)})

    if not nearby:
        nearest = min(URANIUM_MINES,
                      key=lambda m: math.sqrt((lat-m["lat"])**2 + (lon-m["lon"])**2))
        dist_km = math.sqrt((lat-nearest["lat"])**2 + (lon-nearest["lon"])**2) * 111
        return {
            "found": False,
            "score": 0.03,
            "level": "🟢 No uranium legacy sites within 28 km",
            "nearest_site": nearest["name"],
            "nearest_km": round(dist_km, 1),
            "sites": [],
        }

    nearby.sort(key=lambda x: x["distance_km"])
    worst = max(nearby, key=lambda x: x["risk_score"])
    return {
        "found": True,
        "score": worst["risk_score"],
        "level": ("🔴 Within uranium legacy contamination zone" if worst["risk_score"] >= 0.7
                  else "🟠 Near uranium legacy site"),
        "sites": nearby,
        "primary": worst,
    }
