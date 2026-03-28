import streamlit as st
import pandas as pd
import pydeck as pdk
from data.sample_data import generate_sample_properties, PROPERTY_TYPES
from utils.geocoding import get_property_coords, extract_location_from_text

L = {
    "title":     {"bg": "Карта на имотите", "en": "Property Map"},
    "browse":    {"bg": "🗺️ Разгледай на карта", "en": "🗺️ Browse on map"},
    "geocode":   {"bg": "📝 Геокодиране от текст", "en": "📝 Geocode from text"},
    "city_f":    {"bg": "Град", "en": "City"},
    "type_f":    {"bg": "Тип", "en": "Type"},
    "max_p":     {"bg": "Макс. цена (€)", "en": "Max. price (€)"},
    "no_props":  {"bg": "Няма имоти за показване.", "en": "No properties to display."},
    "on_map":    {"bg": "имота на картата", "en": "properties on map"},
    "gc_title":  {"bg": "Извличане на местоположение от текст на обява",
                  "en": "Extract location from listing text"},
    "gc_sub":    {"bg": "Поставете текст и системата открива адреса автоматично.",
                  "en": "Paste any listing text and the system pinpoints the location."},
    "gc_ex":     {"bg": "Примерен текст", "en": "Example text"},
    "gc_own":    {"bg": "-- Въведи свой текст --", "en": "-- Enter your own text --"},
    "gc_area":   {"bg": "Текст на обява:", "en": "Listing text:"},
    "gc_ph":     {"bg": "Напр.: Продава се двустаен апартамент в кв. Младост, гр. София...",
                  "en": "E.g.: Apartment for sale in Mladost district, Sofia..."},
    "gc_btn":    {"bg": "📍 Намери местоположение", "en": "📍 Find location"},
    "gc_city":   {"bg": "Град", "en": "City"},
    "gc_nbh":    {"bg": "Квартал", "en": "Neighborhood"},
    "gc_coords": {"bg": "Координати", "en": "Coordinates"},
    "gc_conf":   {"bg": "Увереност", "en": "Confidence"},
    "gc_found":  {"bg": "✅ Намерено местоположение!", "en": "✅ Location found!"},
    "gc_fail":   {"bg": "❌ Не беше намерено местоположение. Опитайте с по-конкретен текст.",
                  "en": "❌ No location found. Try including city/neighborhood names."},
    "gc_warn":   {"bg": "Моля, въведете текст.", "en": "Please enter some text."},
    "how_it":    {"bg": "💡 Как работи геокодирането?", "en": "💡 How does geocoding work?"},
    "how_txt":   {
        "bg": "Системата търси: **Град** (гр. София), **Квартал** (кв. Лозенец), **Ключови думи** (Слънчев бряг, Банско…). Координатите се изчисляват по известни центрове + отместване за квартала.",
        "en": "The system looks for: **City** (гр. Sofia), **Neighborhood** (кв. Lozenets), **Keywords** (Sunny Beach, Bansko…). Coordinates are calculated from known city centres + neighborhood offsets."
    },
}

EXAMPLE_TEXTS = [
    "Продава се тристаен апартамент в кв. Лозенец, гр. София. Апартаментът е на 4 ет. от 8, площ 95 кв.м.",
    "Двустаен апартамент Пловдив, кв. Тракия, 62 кв.м, ново строителство 2022г.",
    "Луксозна вила в Банско, до ски писта. 280 кв.м, 4 спални, 3 бани.",
    "Студио Слънчев бряг, 32 кв.м, в комплекс с басейн.",
    "Четиристаен апартамент Варна Бриз, 85 кв.м, панорама море.",
]

TYPE_COLORS = {
    "Апартамент": [26, 90, 138], "Къща": [15, 122, 110], "Вила": [224, 112, 32],
    "Студио": [155, 89, 182], "Мезонет": [52, 152, 219], "Атeлие": [231, 76, 60],
    "Офис": [149, 165, 166], "Гараж": [127, 140, 141],
}

def tr(k, l): return L[k][l]


@st.cache_data
def load_map_data():
    df = generate_sample_properties(100)
    coords = df.apply(get_property_coords, axis=1)
    df["lat"] = coords.apply(lambda c: c[0])
    df["lon"] = coords.apply(lambda c: c[1])
    return df


def render(lang: str = "bg"):
    st.markdown(f"### 🗺️ {tr('title', lang)}")
    tab_browse, tab_geo = st.tabs([tr("browse", lang), tr("geocode", lang)])

    with tab_browse:
        df = load_map_data()
        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            city_f = st.multiselect(tr("city_f", lang), sorted(df["city"].unique()), default=[])
        with cf2:
            type_opts = [(k + " / " + v if lang == "en" else k) for k, v in PROPERTY_TYPES.items()]
            type_f_disp = st.multiselect(tr("type_f", lang), type_opts, default=[])
            type_f = [t.split(" / ")[0] for t in type_f_disp]
        with cf3:
            max_price = st.number_input(tr("max_p", lang), value=600000, step=10000)

        filt = df.copy()
        if city_f: filt = filt[filt["city"].isin(city_f)]
        if type_f: filt = filt[filt["type_bg"].isin(type_f)]
        filt = filt[filt["price_eur"] <= max_price]

        if len(filt) == 0:
            st.warning(tr("no_props", lang))
            return

        filt = filt.copy()
        filt["color"] = filt["type_bg"].map(lambda t: TYPE_COLORS.get(t, [100,100,200]))
        filt["tooltip"] = filt.apply(
            lambda r: f"{r['type_bg'] if lang=='bg' else r['type_en']} | {r['area_sqm']}m² | €{r['price_eur']:,} | {r['neighborhood']}, {r['city']}",
            axis=1
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filt[["lat","lon","color","tooltip"]],
            get_position="[lon, lat]",
            get_color="color",
            get_radius=300,
            pickable=True,
            auto_highlight=True,
            radius_min_pixels=6,
            radius_max_pixels=22,
        )
        view = pdk.ViewState(latitude=filt["lat"].mean(), longitude=filt["lon"].mean(), zoom=9, pitch=25)
        deck = pdk.Deck(layers=[layer], initial_view_state=view,
                        tooltip={"text": "{tooltip}"},
                        map_style="mapbox://styles/mapbox/light-v10")
        st.pydeck_chart(deck)

        # Legend
        leg_cols = st.columns(len(TYPE_COLORS))
        for i, (tp, c) in enumerate(TYPE_COLORS.items()):
            hex_c = f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
            label = tp if lang == "bg" else PROPERTY_TYPES.get(tp, tp)
            leg_cols[i].markdown(
                f'<span style="display:inline-block;width:11px;height:11px;background:{hex_c};border-radius:50%;margin-right:3px;"></span>{label}',
                unsafe_allow_html=True
            )

        st.markdown(f"**{len(filt)} {tr('on_map', lang)}**")
        show_cols = ["city","neighborhood","type_bg","area_sqm","price_eur","price_per_sqm"]
        renamed = {
            "city": "Град" if lang=="bg" else "City",
            "neighborhood": "Квартал" if lang=="bg" else "Neighborhood",
            "type_bg": "Тип" if lang=="bg" else "Type",
            "area_sqm": "м²",
            "price_eur": "€",
            "price_per_sqm": "€/м²"
        }
        st.dataframe(filt[show_cols].rename(columns=renamed), height=220, use_container_width=True)

    with tab_geo:
        st.markdown(f"#### {tr('gc_title', lang)}")
        st.caption(tr("gc_sub", lang))

        ex_opts = [tr("gc_own", lang)] + EXAMPLE_TEXTS
        sel_ex = st.selectbox(tr("gc_ex", lang), ex_opts)
        default_text = "" if sel_ex == tr("gc_own", lang) else sel_ex
        input_text = st.text_area(tr("gc_area", lang), value=default_text,
                                   height=130, placeholder=tr("gc_ph", lang))

        if st.button(tr("gc_btn", lang), type="primary"):
            if not input_text.strip():
                st.warning(tr("gc_warn", lang))
            else:
                res = extract_location_from_text(input_text)
                if res["found"]:
                    cr, cm = st.columns([1, 2])
                    with cr:
                        st.success(tr("gc_found", lang))
                        st.markdown(f"""
**{tr('gc_city', lang)}:** {res['city'] or 'N/A'}

**{tr('gc_nbh', lang)}:** {res['neighborhood'] or ('Неизвестен' if lang=='bg' else 'Unknown')}

**{tr('gc_coords', lang)}:** {res['lat']:.4f}, {res['lon']:.4f}

**{tr('gc_conf', lang)}:** {res['confidence_label']} ({res['confidence']*100:.0f}%)
""")
                    with cm:
                        pt = pd.DataFrame([{"lat": res["lat"], "lon": res["lon"]}])
                        mini = pdk.Deck(
                            layers=[pdk.Layer("ScatterplotLayer", data=pt,
                                get_position="[lon, lat]",
                                get_color=[224, 112, 32], get_radius=400,
                                radius_min_pixels=10)],
                            initial_view_state=pdk.ViewState(
                                latitude=res["lat"], longitude=res["lon"], zoom=13, pitch=20),
                            map_style="mapbox://styles/mapbox/streets-v11",
                            height=280,
                        )
                        st.pydeck_chart(mini)
                else:
                    st.error(tr("gc_fail", lang))

        with st.expander(tr("how_it", lang)):
            st.markdown(tr("how_txt", lang))
