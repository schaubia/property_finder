"""
Geo-Risk Assessment page for BG Property Finder.
Covers: seismic, flood, radon, landslide risk for any Bulgarian location.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
from data.geo_hazards import (
    get_all_hazards, get_all_hazards_full, get_seismic_risk, get_flood_risk,
    get_radon_risk, get_landslide_risk, get_uranium_mine_risk,
    fetch_recent_earthquakes_bg,
    CITY_HAZARD_SUMMARY, SEISMIC_ZONES, FLOOD_ZONES, RADON_ZONES, LANDSLIDE_ZONES,
    URANIUM_MINES, CONTAMINATION_COLORS,
)
from data.sample_data import BULGARIAN_CITIES, CITY_COORDS

L = {
    "title":      {"bg": "Геоопасности & Рискове", "en": "Geo-Hazard Risk Assessment"},
    "sub":        {"bg": "Сеизмичен риск · Наводнения · Радон · Свлачища — за всяко местоположение в България",
                   "en": "Seismic risk · Floods · Radon · Landslides — for any location in Bulgaria"},
    "tab_city":   {"bg": "🏙️ Сравнение по градове", "en": "🏙️ City comparison"},
    "tab_point":  {"bg": "📍 Провери адрес", "en": "📍 Check a location"},
    "tab_quakes": {"bg": "🌍 Последни земетресения", "en": "🌍 Recent earthquakes"},
    "tab_map":    {"bg": "🗺️ Рискова карта", "en": "🗺️ Risk map"},
    "select_city":{"bg": "Избери град", "en": "Select city"},
    "overall":    {"bg": "Общ риск", "en": "Overall risk"},
    "seismic":    {"bg": "🏚️ Сеизмичен", "en": "🏚️ Seismic"},
    "flood":      {"bg": "💧 Наводнения", "en": "💧 Flood"},
    "radon":      {"bg": "☢️ Радон", "en": "☢️ Radon"},
    "landslide":  {"bg": "⛰️ Свлачища", "en": "⛰️ Landslide"},
    "pga":        {"bg": "Пикова земна ускорение (PGA)", "en": "Peak Ground Acceleration (PGA)"},
    "radon_bq":   {"bg": "Ср. концентрация радон", "en": "Avg. radon concentration"},
    "eu_ref":     {"bg": "EU референтно ниво: 300 Bq/m³", "en": "EU reference level: 300 Bq/m³"},
    "zone":       {"bg": "Зона", "en": "Zone"},
    "desc":       {"bg": "Описание", "en": "Description"},
    "source":     {"bg": "Източник", "en": "Source"},
    "composite":  {"bg": "Композитен риск индекс", "en": "Composite risk index"},
    "lat_lbl":    {"bg": "Ширина (latitude)", "en": "Latitude"},
    "lon_lbl":    {"bg": "Дължина (longitude)", "en": "Longitude"},
    "check_btn":  {"bg": "🔍 Провери рисковете", "en": "🔍 Check risks"},
    "or_pick":    {"bg": "...или избери от картата по-горе", "en": "...or pick from the map above"},
    "quake_hdr":  {"bg": "Последни земетресения в България и района (M≥2.5)", "en": "Recent earthquakes in Bulgaria area (M≥2.5)"},
    "quake_load": {"bg": "Зареждам данни от USGS…", "en": "Loading USGS data…"},
    "quake_none": {"bg": "Няма данни за последни земетресения.", "en": "No recent earthquake data available."},
    "mag":        {"bg": "Магнитуд", "en": "Magnitude"},
    "depth":      {"bg": "Дълбочина (км)", "en": "Depth (km)"},
    "time":       {"bg": "Дата/час", "en": "Date/time"},
    "place":      {"bg": "Местоположение", "en": "Location"},
    "risk_map_hdr":{"bg": "Рискова карта — избери слой", "en": "Risk map — select layer"},
    "layer_sel":  {"bg": "Слой", "en": "Layer"},
    "uranium":    {"bg": "☢️ Уранови мини", "en": "☢️ Uranium mines"},
    "tab_uranium":{"bg": "☢️ Уранови мини", "en": "☢️ Uranium mines"},
    "u_title":    {"bg": "Закрити уранови мини и радиоактивно наследство",
                   "en": "Closed uranium mines & radioactive legacy sites"},
    "u_sub":      {"bg": "48 мини, 2 преработвателни завода (1944–1992). Общо ~16 720 т U. "
                          "Рекултивацията продължава по Постановление 74/1998.",
                   "en": "48 mines, 2 processing plants (1944–1992). Total ~16,720 t U. "
                          "Remediation ongoing under Decree 74/1998."},
    "u_type":     {"bg": "Тип", "en": "Type"},
    "u_period":   {"bg": "Период", "en": "Period"},
    "u_status":   {"bg": "Статус", "en": "Status"},
    "u_cont":     {"bg": "Замърсяване", "en": "Contamination"},
    "u_nearest":  {"bg": "Най-близка мина", "en": "Nearest mine"},
    "u_dist":     {"bg": "км от избраната точка", "en": "km from selected point"},
    "u_warn":     {"bg": "⚠️ Намирате се в рамките на радиус на замърсяване от затворена уранова мина.",
                   "en": "⚠️ You are within the contamination radius of a closed uranium mine."},
    "u_safe":     {"bg": "✅ Не са установени уранови мини наблизо (>28 км).",
                   "en": "✅ No uranium legacy sites found nearby (>28 km)."},
    "legend":     {"bg": "Легенда", "en": "Legend"},
    "disclaimer": {"bg": "⚠️ Данните са с образователна цел. Базирани на публично достъпни EU/BAS данни. Не замества официална строителна/геоложка оценка.",
                   "en": "⚠️ Data is for informational purposes. Based on publicly available EU/BAS data. Does not replace an official structural/geological assessment."},
    "what_means": {"bg": "💡 Какво означава всеки риск?", "en": "💡 What does each risk mean?"},
    "radar_lbl":  {"bg": "Радарна диаграма на рисковете", "en": "Risk radar chart"},
    "city_cmp":   {"bg": "Сравнение на градовете", "en": "City comparison"},
}

def tr(k, lang): return L[k][lang]


def _score_bar(score: float, width: int = 200) -> str:
    """Return an HTML progress bar for a 0-1 score."""
    pct = int(score * 100)
    color = "#c0392b" if score >= 0.55 else "#e07020" if score >= 0.35 else "#f0b429" if score >= 0.20 else "#0f7a6e"
    return (f'<div style="background:#eee;border-radius:4px;width:{width}px;height:10px;display:inline-block;">'
            f'<div style="background:{color};width:{pct}%;height:100%;border-radius:4px;"></div></div> '
            f'<span style="font-size:0.75rem;color:{color};">{pct}%</span>')


def _hazard_card(title: str, data: dict, lang: str):
    """Render a single hazard info card."""
    score = data["score"]
    color = "#fde8e8" if score >= 0.55 else "#fff3e0" if score >= 0.35 else "#fffde7" if score >= 0.20 else "#e8f8f5"
    border = "#c0392b" if score >= 0.55 else "#e07020" if score >= 0.35 else "#f0b429" if score >= 0.20 else "#0f7a6e"

    extras = ""
    if "pga_g" in data:
        extras += f'<br><span style="font-size:0.78rem;">PGA: <strong>{data["pga_g"]}g</strong></span>'
    if "bq_m3" in data:
        extras += f'<br><span style="font-size:0.78rem;">Radon: <strong>{data["bq_m3"]} Bq/m³</strong> (EU ref: 300)</span>'

    st.markdown(f"""
    <div style="background:{color};border-left:4px solid {border};border-radius:10px;
                padding:0.9rem 1rem;margin-bottom:0.7rem;">
        <div style="font-weight:700;font-size:0.95rem;color:#1a1a1a;">{title}</div>
        <div style="font-size:0.88rem;margin:0.2rem 0;">{data['level']}</div>
        {_score_bar(score)}
        {extras}
        <div style="font-size:0.78rem;color:#444;margin-top:0.4rem;">
            <strong>{tr('zone',lang)}:</strong> {data['zone']}<br>
            {data['description']}
        </div>
        <div style="font-size:0.68rem;color:#888;margin-top:0.3rem;">
            📚 {tr('source',lang)}: {data['source']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render(lang: str = "bg"):
    st.markdown(f"### ⚠️ {tr('title', lang)}")
    st.caption(tr("sub", lang))

    tab_city, tab_point, tab_quakes, tab_map, tab_uranium = st.tabs([
        tr("tab_city", lang), tr("tab_point", lang),
        tr("tab_quakes", lang), tr("tab_map", lang), tr("tab_uranium", lang)
    ])

    # ── TAB 1: City comparison ─────────────────────────────────────────────────
    with tab_city:
        st.markdown(f"#### 🏙️ {tr('city_cmp', lang)}")

        cities = list(CITY_HAZARD_SUMMARY.keys())
        records = []
        for city, h in CITY_HAZARD_SUMMARY.items():
            records.append({
                "city": city,
                tr("overall", lang):    round(h["composite_score"] * 100),
                tr("seismic", lang):    round(h["seismic"]["score"] * 100),
                tr("flood", lang):      round(h["flood"]["score"] * 100),
                tr("radon", lang):      round(h["radon"]["score"] * 100),
                tr("landslide", lang):  round(h["landslide"]["score"] * 100),
            })
        df = pd.DataFrame(records).set_index("city")

        # Heatmap-style table
        st.dataframe(
            df.style.background_gradient(cmap="RdYlGn_r", vmin=0, vmax=100),
            use_container_width=True, height=370
        )

        # Radar chart for selected city
        st.markdown("---")
        selected_city = st.selectbox(tr("select_city", lang), cities, key="city_radar")
        h = CITY_HAZARD_SUMMARY[selected_city]

        categories = [tr("seismic",lang), tr("flood",lang), tr("radon",lang), tr("landslide",lang)]
        values = [
            h["seismic"]["score"] * 100,
            h["flood"]["score"] * 100,
            h["radon"]["score"] * 100,
            h["landslide"]["score"] * 100,
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(224,112,32,0.25)",
            line=dict(color="#e07020", width=2),
            name=selected_city
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False, height=340,
            title=f"{tr('radar_lbl',lang)} — {selected_city}",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Detail cards for selected city
        c1, c2 = st.columns(2)
        with c1:
            _hazard_card(tr("seismic", lang), h["seismic"], lang)
            _hazard_card(tr("flood", lang),   h["flood"],   lang)
        with c2:
            _hazard_card(tr("radon", lang),     h["radon"],     lang)
            _hazard_card(tr("landslide", lang), h["landslide"], lang)

        st.caption(tr("disclaimer", lang))

    # ── TAB 2: Point lookup ────────────────────────────────────────────────────
    with tab_point:
        st.markdown(f"#### 📍 {tr('tab_point', lang)}")

        col_coords, col_or = st.columns([2, 1])
        with col_coords:
            lat = st.number_input(tr("lat_lbl", lang), min_value=41.0, max_value=44.5,
                                  value=42.697, step=0.001, format="%.4f")
            lon = st.number_input(tr("lon_lbl", lang), min_value=22.0, max_value=29.0,
                                  value=23.322, step=0.001, format="%.4f")
        with col_or:
            st.markdown(f"<br>{tr('or_pick', lang)}", unsafe_allow_html=True)
            preset = st.selectbox("", list(CITY_COORDS.keys()), key="preset_city")
            if st.button("📌 " + ("Зареди" if lang=="bg" else "Load"), key="load_preset"):
                plat, plon = CITY_COORDS[preset]
                st.session_state["geo_lat"] = plat
                st.session_state["geo_lon"] = plon
                st.rerun()

        if "geo_lat" in st.session_state:
            lat = st.session_state["geo_lat"]
            lon = st.session_state["geo_lon"]

        if st.button(tr("check_btn", lang), type="primary"):
            with st.spinner("Analyzing..."):
                h = get_all_hazards(lat, lon)

            # Composite score gauge
            score_pct = int(h["composite_score"] * 100)
            g_color = "#c0392b" if score_pct >= 55 else "#e07020" if score_pct >= 35 else "#f0b429" if score_pct >= 20 else "#0f7a6e"
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score_pct,
                title={"text": f"{tr('composite',lang)} — {h['overall']}", "font":{"size":13}},
                number={"suffix": "/100", "font":{"size":22}},
                gauge={
                    "axis": {"range":[0,100]},
                    "bar": {"color": g_color},
                    "steps": [
                        {"range":[0,20],  "color":"#e8f8f5"},
                        {"range":[20,35], "color":"#fffde7"},
                        {"range":[35,55], "color":"#fff3e0"},
                        {"range":[55,100],"color":"#fde8e8"},
                    ],
                }
            ))
            fig_g.update_layout(height=200, margin=dict(t=35,b=0,l=20,r=20),
                                 paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_g, use_container_width=True)

            # Four hazard cards
            c1, c2 = st.columns(2)
            with c1:
                _hazard_card(tr("seismic", lang), h["seismic"], lang)
                _hazard_card(tr("flood", lang),   h["flood"],   lang)
            with c2:
                _hazard_card(tr("radon", lang),     h["radon"],     lang)
                _hazard_card(tr("landslide", lang), h["landslide"], lang)

            # Explainer
            with st.expander(tr("what_means", lang)):
                st.markdown("""
**🏚️ Сеизмичен риск / Seismic risk**  
Измерва се чрез Пикова Земна Ускорение (PGA) за 475-годишен период на повторяемост (Eurocode 8).  
*PGA ≥ 0.20g = висок риск. Зони: Кресна, Пловдив, Шабла, София.*

**💧 Риск от наводнения / Flood risk**  
Базиран на EU Директива за Наводненията (2007/60/EC), цикъл 2023.  
*Най-засегнати: поречията на Дунав, Искър, Марица.*

**☢️ Радон / Radon**  
Радонът е естествен радиоактивен газ от почвата — основна причина за рак на белия дроб след тютюнопушенето.  
*EU референтно ниво: 300 Bq/m³. Повишен в гранитни зони (Родопи, Пирин, Витоша).*

**⛰️ Свлачища / Landslides**  
Склонност към свлачища по наклонен терен при обилни валежи.  
*Най-висока — Рила, Родопи и Пиринско. Ниска — Дунавска равнина.*
                """)

            st.caption(tr("disclaimer", lang))

    # ── TAB 3: Recent earthquakes ──────────────────────────────────────────────
    with tab_quakes:
        st.markdown(f"#### 🌍 {tr('quake_hdr', lang)}")
        st.caption("Source: USGS Earthquake Hazards Program — real-time feed")

        with st.spinner(tr("quake_load", lang)):
            quakes = fetch_recent_earthquakes_bg()

        if not quakes:
            st.info(tr("quake_none", lang))
        else:
            df_q = pd.DataFrame(quakes)

            # Map of recent quakes
            df_q["color"] = df_q["mag"].apply(lambda m:
                [192, 57, 43] if m >= 4.5 else
                [224, 112, 32] if m >= 3.5 else
                [240, 180, 41] if m >= 2.5 else [100, 180, 100]
            )
            df_q["radius"] = df_q["mag"].apply(lambda m: int(m ** 2.5 * 1000))

            layer_q = pdk.Layer("ScatterplotLayer",
                data=df_q[["lat","lon","color","radius","mag","place","time"]],
                get_position="[lon,lat]", get_color="color",
                get_radius="radius", pickable=True,
                radius_min_pixels=4, radius_max_pixels=30)

            st.pydeck_chart(pdk.Deck(
                layers=[layer_q],
                initial_view_state=pdk.ViewState(latitude=42.7, longitude=25.5, zoom=6, pitch=20),
                tooltip={"text": "M{mag} — {place}\n{time}"},
                map_style="mapbox://styles/mapbox/light-v10",
            ))

            # Legend
            st.markdown("""
            <span style="display:inline-block;width:12px;height:12px;background:#c0392b;border-radius:50%;margin-right:4px;"></span>M≥4.5 &nbsp;
            <span style="display:inline-block;width:12px;height:12px;background:#e07020;border-radius:50%;margin-right:4px;"></span>M3.5–4.5 &nbsp;
            <span style="display:inline-block;width:12px;height:12px;background:#f0b429;border-radius:50%;margin-right:4px;"></span>M2.5–3.5
            """, unsafe_allow_html=True)

            # Table
            st.dataframe(
                df_q[["time","mag","depth","place"]].rename(columns={
                    "time": tr("time",lang), "mag": tr("mag",lang),
                    "depth": tr("depth",lang), "place": tr("place",lang)
                }),
                use_container_width=True, height=300
            )

            # Magnitude histogram
            fig_hist = px.histogram(df_q, x="mag", nbins=15,
                title="Magnitude distribution" if lang=="en" else "Разпределение по магнитуд",
                color_discrete_sequence=["#1a5a8a"],
                labels={"mag": tr("mag",lang), "count": "Count"})
            fig_hist.update_layout(height=250, margin=dict(t=40,b=10),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_hist, use_container_width=True)

    # ── TAB 4: Risk map ────────────────────────────────────────────────────────
    with tab_map:
        st.markdown(f"#### 🗺️ {tr('risk_map_hdr', lang)}")

        layer_choice = st.selectbox(tr("layer_sel", lang), [
            tr("seismic", lang), tr("flood", lang),
            tr("radon", lang), tr("landslide", lang)
        ])

        # Build polygon data from zone lists
        if layer_choice == tr("seismic", lang):
            zones, score_idx, label_idx = SEISMIC_ZONES, 4, 5
            score_max, cmap = 0.30, "seismic"
        elif layer_choice == tr("flood", lang):
            zones, score_idx, label_idx = FLOOD_ZONES, 4, 5
            score_max, cmap = 3, "flood"
        elif layer_choice == tr("radon", lang):
            zones, score_idx, label_idx = RADON_ZONES, 4, 5
            score_max, cmap = 300, "radon"
        else:
            zones, score_idx, label_idx = LANDSLIDE_ZONES, 4, 5
            score_max, cmap = 4, "landslide"

        map_records = []
        for z in zones:
            val = z[score_idx]
            norm = min(1.0, val / score_max)
            r = int(192 * norm + 26 * (1 - norm))
            g = int(57  * norm + 138 * (1 - norm))
            b = int(43  * norm + 90 * (1 - norm))
            clat = (z[0] + z[1]) / 2
            clon = (z[2] + z[3]) / 2
            map_records.append({
                "lat": clat, "lon": clon,
                "color": [r, g, b, 140],
                "radius": int(((z[1]-z[0]) + (z[3]-z[2])) / 2 * 55000),
                "label": z[label_idx],
                "value": str(val),
                "description": z[6],
            })

        df_map = pd.DataFrame(map_records)
        risk_layer = pdk.Layer("ScatterplotLayer",
            data=df_map,
            get_position="[lon,lat]", get_color="color",
            get_radius="radius", pickable=True,
            opacity=0.55, stroked=True,
            get_line_color=[80,80,80], line_width_min_pixels=1)

        st.pydeck_chart(pdk.Deck(
            layers=[risk_layer],
            initial_view_state=pdk.ViewState(latitude=42.8, longitude=25.2, zoom=6, pitch=0),
            tooltip={"text": "{label}\nValue: {value}\n{description}"},
            map_style="mapbox://styles/mapbox/light-v10",
        ))

        st.markdown("""
        <div style="display:flex;gap:8px;align-items:center;margin-top:0.5rem;">
            <div style="background:linear-gradient(to right,#1a8a5a,#f0b429,#c0392b);
                        width:200px;height:12px;border-radius:4px;"></div>
            <span style="font-size:0.78rem;">Low → High risk</span>
        </div>
        """, unsafe_allow_html=True)

        st.caption(tr("disclaimer", lang))
    # ── TAB 5: Uranium mines ──────────────────────────────────────────────────
    with tab_uranium:
        st.markdown(f"#### ☢️ {tr('u_title', lang)}")
        st.caption(tr("u_sub", lang))

        # Overview metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Затворени мини / Closed mines", "48")
        m2.metric("Общо добит уран / Total U mined", "~16 720 t")
        m3.metric("Отвали / Waste heaps", "298 heaps, 84.5 ha")
        m4.metric("Хвостохранилища / Tailings", "132 ha, 16 Mt")

        st.markdown("---")

        # Map of uranium mines
        import pandas as pd
        import pydeck as pdk
        mine_records = []
        for m in URANIUM_MINES:
            c = CONTAMINATION_COLORS.get(m["contamination_level"], [150,150,150])
            mine_records.append({
                "lat": m["lat"], "lon": m["lon"],
                "color": c + [180],
                "radius": int(m["risk_score"] * 12000),
                "name": m["name"] if lang=="en" else m["name_bg"],
                "type": m["type"],
                "period": m["active_period"],
                "status": m["status"],
                "contamination": m["contamination_level"],
            })
        df_mines = pd.DataFrame(mine_records)

        mine_layer = pdk.Layer("ScatterplotLayer",
            data=df_mines,
            get_position="[lon,lat]", get_color="color",
            get_radius="radius", pickable=True,
            radius_min_pixels=8, radius_max_pixels=35,
            stroked=True, get_line_color=[80,0,0], line_width_min_pixels=1)

        st.pydeck_chart(pdk.Deck(
            layers=[mine_layer],
            initial_view_state=pdk.ViewState(latitude=42.5, longitude=24.5, zoom=7, pitch=20),
            tooltip={"text": "{name}\n{type}\n{period}\n{status}\nContamination: {contamination}"},
            map_style="mapbox://styles/mapbox/light-v10",
        ))

        # Legend
        st.markdown("""
        <span style="display:inline-block;width:12px;height:12px;background:#c0392b;border-radius:50%;margin-right:4px;"></span>High &nbsp;
        <span style="display:inline-block;width:12px;height:12px;background:#962064;border-radius:50%;margin-right:4px;"></span>High (groundwater) &nbsp;
        <span style="display:inline-block;width:12px;height:12px;background:#e07020;border-radius:50%;margin-right:4px;"></span>Moderate-High &nbsp;
        <span style="display:inline-block;width:12px;height:12px;background:#f0b429;border-radius:50%;margin-right:4px;"></span>Moderate
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed cards per mine
        for m in sorted(URANIUM_MINES, key=lambda x: x["risk_score"], reverse=True):
            c = CONTAMINATION_COLORS.get(m["contamination_level"], [150,150,150])
            hex_c = f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
            name_disp = m["name_bg"] if lang=="bg" else m["name"]
            notes_disp = m["notes_bg"] if lang=="bg" else m["notes_en"]

            with st.expander(f"{'☢️' if m['risk_score']>=0.7 else '⚠️'} {name_disp} — {m['contamination_level']}"):
                c1, c2 = st.columns([2,1])
                with c1:
                    st.markdown(f"""
**{tr('u_type',lang)}:** {m['type']}  
**{tr('u_period',lang)}:** {m['active_period']}  
**{tr('u_status',lang)}:** {m['status']}  
**{tr('u_cont',lang)}:** <span style="color:{hex_c};font-weight:700;">{m['contamination_level']}</span>  
**{tr('source',lang)}:** {m['source']}
                    """, unsafe_allow_html=True)
                    st.caption(notes_disp)
                with c2:
                    score_pct = int(m['risk_score']*100)
                    fig_mini = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score_pct,
                        number={"suffix":"/100","font":{"size":18}},
                        title={"text":"Risk","font":{"size":11}},
                        gauge={"axis":{"range":[0,100]},
                               "bar":{"color":hex_c},
                               "steps":[{"range":[0,40],"color":"#e8f8f5"},
                                        {"range":[40,70],"color":"#fff3e0"},
                                        {"range":[70,100],"color":"#fde8e8"}]}
                    ))
                    fig_mini.update_layout(height=160, margin=dict(t=25,b=0,l=10,r=10),
                                          paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_mini, use_container_width=True)

        st.markdown("---")
        # Check a specific point
        st.markdown(f"#### 📍 {'Провери конкретна точка' if lang=='bg' else 'Check a specific point'}")
        uc1, uc2 = st.columns(2)
        with uc1:
            u_lat = st.number_input("Lat", 41.0, 44.5, 42.697, 0.001, format="%.4f", key="u_lat")
            u_lon = st.number_input("Lon", 22.0, 29.0, 23.322, 0.001, format="%.4f", key="u_lon")
        if st.button("☢️ " + ("Провери" if lang=="bg" else "Check"), key="u_check"):
            result = get_uranium_mine_risk(u_lat, u_lon)
            if result["found"]:
                st.error(tr("u_warn", lang))
                for site in result["sites"]:
                    name_d = site["name_bg"] if lang=="bg" else site["name"]
                    notes_d = site["notes_bg"] if lang=="bg" else site["notes_en"]
                    st.markdown(f"""
                    <div style="background:#fde8e8;border-left:4px solid #c0392b;border-radius:8px;padding:0.8rem;margin:0.4rem 0;">
                    <strong>{name_d}</strong> — {site['distance_km']} {tr('u_dist',lang)}<br>
                    <span style="font-size:0.82rem;">{notes_d}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success(tr("u_safe", lang))
                st.caption(f"{tr('u_nearest',lang)}: {result['nearest_site']} ({result['nearest_km']} km)")

        st.caption(tr("disclaimer", lang))
