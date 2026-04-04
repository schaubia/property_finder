"""
Geo-Risk Assessment page for BG Property Finder.
Covers: seismic, flood, radon, landslide, uranium mine legacy risk.
"""
# ── ALL imports at module top — no inline imports inside render() ─────────────
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk

from data.geo_hazards import (
    get_all_hazards, get_all_hazards_full,
    get_seismic_risk, get_flood_risk, get_radon_risk, get_landslide_risk,
    get_uranium_mine_risk, fetch_recent_earthquakes_bg,
    CITY_HAZARD_SUMMARY, SEISMIC_ZONES, FLOOD_ZONES, RADON_ZONES, LANDSLIDE_ZONES,
    URANIUM_MINES, CONTAMINATION_COLORS,
)
from data.sample_data import CITY_COORDS

# ── Translations ──────────────────────────────────────────────────────────────
L = {
    "title":       {"bg": "Геоопасности & Рискове",     "en": "Geo-Hazard Risk Assessment"},
    "sub":         {"bg": "Сеизмичен риск · Наводнения · Радон · Свлачища · Уранови мини",
                    "en": "Seismic · Floods · Radon · Landslides · Uranium mine legacy"},
    "tab_city":    {"bg": "🏙️ Сравнение по градове",    "en": "🏙️ City comparison"},
    "tab_point":   {"bg": "📍 Провери адрес",            "en": "📍 Check a location"},
    "tab_quakes":  {"bg": "🌍 Земетресения",             "en": "🌍 Earthquakes"},
    "tab_map":     {"bg": "🗺️ Рискова карта",            "en": "🗺️ Risk map"},
    "tab_uranium": {"bg": "☢️ Уранови мини",             "en": "☢️ Uranium mines"},
    "select_city": {"bg": "Избери град",                 "en": "Select city"},
    "overall":     {"bg": "Общ риск",                   "en": "Overall"},
    "seismic":     {"bg": "Сеизмичен",                  "en": "Seismic"},
    "flood":       {"bg": "Наводнения",                 "en": "Flood"},
    "radon":       {"bg": "Радон",                      "en": "Radon"},
    "landslide":   {"bg": "Свлачища",                   "en": "Landslide"},
    "uranium":     {"bg": "Уранови мини",               "en": "Uranium"},
    "composite":   {"bg": "Композитен риск индекс",     "en": "Composite risk index"},
    "radar_lbl":   {"bg": "Радарна диаграма",           "en": "Risk radar chart"},
    "city_cmp":    {"bg": "Сравнение на градовете",     "en": "City comparison"},
    "lat_lbl":     {"bg": "Ширина (latitude)",          "en": "Latitude"},
    "lon_lbl":     {"bg": "Дължина (longitude)",        "en": "Longitude"},
    "check_btn":   {"bg": "🔍 Провери рисковете",       "en": "🔍 Check risks"},
    "or_pick":     {"bg": "...или избери град",         "en": "...or pick a city"},
    "load_btn":    {"bg": "📌 Зареди",                  "en": "📌 Load"},
    "quake_hdr":   {"bg": "Последни земетресения (M≥2.5)", "en": "Recent earthquakes (M≥2.5)"},
    "quake_load":  {"bg": "Зареждам от USGS…",         "en": "Loading from USGS…"},
    "quake_none":  {"bg": "Няма данни.",                "en": "No data available."},
    "mag":         {"bg": "Магнитуд",                   "en": "Magnitude"},
    "depth":       {"bg": "Дълбочина (км)",             "en": "Depth (km)"},
    "time":        {"bg": "Дата/час",                   "en": "Date/time"},
    "place":       {"bg": "Местоположение",             "en": "Location"},
    "risk_map_hdr":{"bg": "Рискова карта — избери слой","en": "Risk map — select layer"},
    "layer_sel":   {"bg": "Слой",                       "en": "Layer"},
    "zone":        {"bg": "Зона",                       "en": "Zone"},
    "source":      {"bg": "Източник",                   "en": "Source"},
    "disclaimer":  {"bg": "⚠️ Данните са с образователна цел. Не замества официална геоложка оценка.",
                    "en": "⚠️ Data is for informational purposes only. Does not replace an official assessment."},
    "what_means":  {"bg": "💡 Какво означава всеки риск?", "en": "💡 What does each risk mean?"},
    # Uranium
    "u_title":     {"bg": "Закрити уранови мини и радиоактивно наследство",
                    "en": "Closed uranium mines & radioactive legacy sites"},
    "u_sub":       {"bg": "48 мини, 2 завода (1944–1992). Общо ~16 720 т U. Рекултивацията продължава.",
                    "en": "48 mines, 2 plants (1944–1992). Total ~16,720 t U. Remediation ongoing."},
    "u_type":      {"bg": "Тип",                        "en": "Type"},
    "u_period":    {"bg": "Период",                     "en": "Period"},
    "u_status":    {"bg": "Статус",                     "en": "Status"},
    "u_cont":      {"bg": "Замърсяване",                "en": "Contamination"},
    "u_nearest":   {"bg": "Най-близка мина",            "en": "Nearest mine"},
    "u_dist":      {"bg": "км от точката",              "en": "km from point"},
    "u_warn":      {"bg": "⚠️ В радиус на замърсяване от закрита уранова мина.",
                    "en": "⚠️ Within contamination radius of a closed uranium mine."},
    "u_safe":      {"bg": "✅ Няма уранови мини наблизо (>28 км).",
                    "en": "✅ No uranium legacy sites within 28 km."},
    "u_check_btn": {"bg": "☢️ Провери",                 "en": "☢️ Check"},
}


def tr(key: str, lang: str) -> str:
    return L.get(key, {}).get(lang, L.get(key, {}).get("en", key))


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _score_bar(score: float) -> str:
    pct = int(score * 100)
    color = ("#c0392b" if score >= 0.55 else
             "#e07020" if score >= 0.35 else
             "#f0b429" if score >= 0.20 else "#0f7a6e")
    return (f'<div style="background:#eee;border-radius:4px;width:180px;height:9px;'
            f'display:inline-block;vertical-align:middle;">'
            f'<div style="background:{color};width:{pct}%;height:100%;border-radius:4px;"></div>'
            f'</div> <span style="font-size:0.74rem;color:{color};">{pct}%</span>')


def _hazard_card(title: str, data: dict, lang: str):
    score = data["score"]
    bg    = ("#fde8e8" if score >= 0.55 else
             "#fff3e0" if score >= 0.35 else
             "#fffde7" if score >= 0.20 else "#e8f8f5")
    bdr   = ("#c0392b" if score >= 0.55 else
             "#e07020" if score >= 0.35 else
             "#f0b429" if score >= 0.20 else "#0f7a6e")
    extras = ""
    if "pga_g" in data:
        extras += f'<br><span style="font-size:0.77rem;">PGA: <strong>{data["pga_g"]}g</strong></span>'
    if "bq_m3" in data:
        extras += f'<br><span style="font-size:0.77rem;">Radon: <strong>{data["bq_m3"]} Bq/m³</strong></span>'
    st.markdown(f"""
    <div style="background:{bg};border-left:4px solid {bdr};border-radius:10px;
                padding:0.8rem 1rem;margin-bottom:0.6rem;">
      <div style="font-weight:700;font-size:0.93rem;">{title}</div>
      <div style="font-size:0.86rem;margin:0.15rem 0;">{data['level']}</div>
      {_score_bar(score)}
      {extras}
      <div style="font-size:0.76rem;color:#444;margin-top:0.35rem;">
        <strong>{tr('zone',lang)}:</strong> {data['zone']}<br>{data['description']}
      </div>
      <div style="font-size:0.67rem;color:#888;margin-top:0.2rem;">
        📚 {tr('source',lang)}: {data['source']}
      </div>
    </div>""", unsafe_allow_html=True)


# ── Main render ────────────────────────────────────────────────────────────────

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

        col_overall   = tr("overall",   lang)
        col_seismic   = tr("seismic",   lang)
        col_flood     = tr("flood",     lang)
        col_radon     = tr("radon",     lang)
        col_landslide = tr("landslide", lang)

        city_names, z_matrix = [], []
        for city, h in CITY_HAZARD_SUMMARY.items():
            city_names.append(city)
            z_matrix.append([
                round(h["composite_score"] * 100),
                round(h["seismic"]["score"] * 100),
                round(h["flood"]["score"] * 100),
                round(h["radon"]["score"] * 100),
                round(h["landslide"]["score"] * 100),
            ])

        col_labels = [col_overall, col_seismic, col_flood, col_radon, col_landslide]

        fig_heat = px.imshow(
            z_matrix,
            labels=dict(x="Risk type", y="City", color="Score (0-100)"),
            x=col_labels,
            y=city_names,
            color_continuous_scale="RdYlGn_r",
            zmin=0, zmax=100,
            text_auto=True,
            aspect="auto",
        )
        fig_heat.update_layout(
            height=370, margin=dict(t=20, b=20, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            font=dict(size=11),
        )
        st.plotly_chart(fig_heat, width="stretch")

        # Radar for selected city
        st.markdown("---")
        selected_city = st.selectbox(tr("select_city", lang), list(CITY_HAZARD_SUMMARY.keys()),
                                     key="city_radar")
        h_city = CITY_HAZARD_SUMMARY[selected_city]
        cats   = [tr("seismic",lang), tr("flood",lang), tr("radon",lang), tr("landslide",lang)]
        vals   = [round(h_city[k]["score"]*100) for k in ("seismic","flood","radon","landslide")]

        fig_radar = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", fillcolor="rgba(224,112,32,0.22)",
            line=dict(color="#e07020", width=2),
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=False, height=320,
            title=f"{tr('radar_lbl',lang)} — {selected_city}",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_radar, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            _hazard_card(f"🏚️ {tr('seismic',lang)}", h_city["seismic"], lang)
            _hazard_card(f"💧 {tr('flood',lang)}",   h_city["flood"],   lang)
        with c2:
            _hazard_card(f"☢️ {tr('radon',lang)}",     h_city["radon"],     lang)
            _hazard_card(f"⛰️ {tr('landslide',lang)}", h_city["landslide"], lang)
        st.caption(tr("disclaimer", lang))

    # ── TAB 2: Point lookup ────────────────────────────────────────────────────
    with tab_point:
        st.markdown(f"#### 📍 {tr('tab_point', lang)}")

        pc1, pc2 = st.columns([2, 1])
        with pc1:
            pt_lat = st.number_input(tr("lat_lbl", lang), 41.0, 44.5, 42.697,
                                     step=0.001, format="%.4f", key="pt_lat")
            pt_lon = st.number_input(tr("lon_lbl", lang), 22.0, 29.0, 23.322,
                                     step=0.001, format="%.4f", key="pt_lon")
        with pc2:
            st.markdown(f"<br>{tr('or_pick',lang)}", unsafe_allow_html=True)
            preset = st.selectbox("", list(CITY_COORDS.keys()), key="preset_city",
                                  label_visibility="collapsed")
            if st.button(tr("load_btn", lang), key="load_preset"):
                st.session_state["pt_lat"] = CITY_COORDS[preset][0]
                st.session_state["pt_lon"] = CITY_COORDS[preset][1]
                st.rerun()

        if st.button(tr("check_btn", lang), type="primary", key="check_point"):
            h_pt = get_all_hazards_full(pt_lat, pt_lon)
            score_pct = int(h_pt["composite_score"] * 100)
            g_color = ("#c0392b" if score_pct >= 55 else
                       "#e07020" if score_pct >= 35 else
                       "#f0b429" if score_pct >= 20 else "#0f7a6e")

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=score_pct,
                title={"text": f"{tr('composite',lang)} — {h_pt['overall']}", "font":{"size":12}},
                number={"suffix":"/100","font":{"size":20}},
                gauge={"axis":{"range":[0,100]}, "bar":{"color":g_color},
                       "steps":[{"range":[0,20],  "color":"#e8f8f5"},
                                 {"range":[20,35], "color":"#fffde7"},
                                 {"range":[35,55], "color":"#fff3e0"},
                                 {"range":[55,100],"color":"#fde8e8"}]}
            ))
            fig_g.update_layout(height=195, margin=dict(t=30,b=0,l=20,r=20),
                                 paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_g, width="stretch")

            cc1, cc2 = st.columns(2)
            with cc1:
                _hazard_card(f"🏚️ {tr('seismic',lang)}",   h_pt["seismic"],   lang)
                _hazard_card(f"💧 {tr('flood',lang)}",      h_pt["flood"],     lang)
            with cc2:
                _hazard_card(f"☢️ {tr('radon',lang)}",      h_pt["radon"],     lang)
                _hazard_card(f"⛰️ {tr('landslide',lang)}",  h_pt["landslide"], lang)

            u_result = h_pt.get("uranium", {})
            if u_result.get("found"):
                st.error(tr("u_warn", lang))
                primary = u_result.get("primary", {})
                name_d  = primary.get("name_bg" if lang=="bg" else "name", "")
                notes_d = primary.get("notes_bg" if lang=="bg" else "notes_en", "")
                st.markdown(f"""
                <div style="background:#fde8e8;border-left:4px solid #c0392b;
                            border-radius:8px;padding:0.8rem;margin:0.4rem 0;">
                  <strong>{name_d}</strong><br>
                  <span style="font-size:0.82rem;">{notes_d}</span>
                </div>""", unsafe_allow_html=True)

            with st.expander(tr("what_means", lang)):
                st.markdown("""
**🏚️ Seismic / Сеизмичен**  
PGA (Peak Ground Acceleration) за 475-год. период — Eurocode 8.
PGA ≥ 0.20g = висок риск. Главни зони: Кресна, Пловдив, Шабла, София.

**💧 Flood / Наводнения**  
EU Директива 2007/60/EC — цикъл 2023.
Най-засегнати: Дунав, Искър, Марица.

**☢️ Radon / Радон**  
Естествен радиоактивен газ. EU референтно ниво: 300 Bq/m³.
Повишен в гранитни зони (Родопи, Пирин, Витоша).

**⛰️ Landslide / Свлачища**  
EU JRC Global Landslide Susceptibility.
Най-висока — Рила, Родопи. Ниска — Дунавска равнина.

**☢️ Uranium / Уранови мини**  
48 закрити мини (1944–1992). Рекултивацията продължава.
Активни проблеми: Бухово, Елешница, ИСЛ находища в Пловдивско.
                """)
            st.caption(tr("disclaimer", lang))

    # ── TAB 3: Recent earthquakes ──────────────────────────────────────────────
    with tab_quakes:
        st.markdown(f"#### 🌍 {tr('quake_hdr', lang)}")
        st.caption("Source: USGS Earthquake Hazards Program")

        with st.spinner(tr("quake_load", lang)):
            quakes = fetch_recent_earthquakes_bg()

        if not quakes:
            st.info(tr("quake_none", lang))
        else:
            df_quakes = pd.DataFrame(quakes)
            df_quakes["color"] = df_quakes["mag"].apply(lambda m:
                [192,57,43]  if m >= 4.5 else
                [224,112,32] if m >= 3.5 else
                [240,180,41]
            )
            df_quakes["radius"] = df_quakes["mag"].apply(lambda m: int(m**2.5 * 1000))

            q_layer = pdk.Layer("ScatterplotLayer",
                data=df_quakes[["lat","lon","color","radius","mag","place","time"]],
                get_position="[lon,lat]", get_color="color", get_radius="radius",
                pickable=True, radius_min_pixels=4, radius_max_pixels=28)

            st.pydeck_chart(pdk.Deck(
                layers=[q_layer],
                initial_view_state=pdk.ViewState(latitude=42.7, longitude=25.5, zoom=6, pitch=20),
                tooltip={"text": "M{mag} — {place}\n{time}"},
                map_style="mapbox://styles/mapbox/light-v10",
            ))

            st.markdown("""
            <span style="display:inline-block;width:11px;height:11px;background:#c0392b;border-radius:50%;margin-right:4px;"></span>M≥4.5 &nbsp;
            <span style="display:inline-block;width:11px;height:11px;background:#e07020;border-radius:50%;margin-right:4px;"></span>M3.5–4.5 &nbsp;
            <span style="display:inline-block;width:11px;height:11px;background:#f0b429;border-radius:50%;margin-right:4px;"></span>M2.5–3.5
            """, unsafe_allow_html=True)

            st.dataframe(
                df_quakes[["time","mag","depth","place"]].rename(columns={
                    "time":  tr("time",lang),  "mag":   tr("mag",lang),
                    "depth": tr("depth",lang), "place": tr("place",lang)
                }),
                width="stretch", height=280
            )

            fig_qhist = px.histogram(df_quakes, x="mag", nbins=15,
                title="Magnitude distribution" if lang=="en" else "Разпределение по магнитуд",
                color_discrete_sequence=["#1a5a8a"],
                labels={"mag": tr("mag",lang)})
            fig_qhist.update_layout(height=230, margin=dict(t=40,b=10),
                                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_qhist, width="stretch")

    # ── TAB 4: Risk map ────────────────────────────────────────────────────────
    with tab_map:
        st.markdown(f"#### 🗺️ {tr('risk_map_hdr', lang)}")

        layer_opts = {
            tr("seismic",   lang): (SEISMIC_ZONES,   0.30),
            tr("flood",     lang): (FLOOD_ZONES,      3.0),
            tr("radon",     lang): (RADON_ZONES,    300.0),
            tr("landslide", lang): (LANDSLIDE_ZONES,  4.0),
        }
        layer_choice = st.selectbox(tr("layer_sel", lang), list(layer_opts.keys()), key="map_layer")
        zones, score_max = layer_opts[layer_choice]

        map_recs = []
        for z in zones:
            norm = min(1.0, z[4] / score_max)
            r = int(192 * norm + 26  * (1 - norm))
            g = int(57  * norm + 138 * (1 - norm))
            b = int(43  * norm + 90  * (1 - norm))
            map_recs.append({
                "lat":   (z[0] + z[1]) / 2,
                "lon":   (z[2] + z[3]) / 2,
                "color": [r, g, b, 140],
                "radius": int(((z[1]-z[0]) + (z[3]-z[2])) / 2 * 55000),
                "label":  z[5],
                "value":  str(z[4]),
                "desc":   z[6],
            })

        df_map = pd.DataFrame(map_recs)
        map_layer = pdk.Layer("ScatterplotLayer",
            data=df_map, get_position="[lon,lat]", get_color="color",
            get_radius="radius", pickable=True, opacity=0.55,
            stroked=True, get_line_color=[80,80,80], line_width_min_pixels=1)

        st.pydeck_chart(pdk.Deck(
            layers=[map_layer],
            initial_view_state=pdk.ViewState(latitude=42.8, longitude=25.2, zoom=6, pitch=0),
            tooltip={"text": "{label}\nValue: {value}\n{desc}"},
            map_style="mapbox://styles/mapbox/light-v10",
        ))
        st.markdown("""
        <div style="display:flex;gap:8px;align-items:center;margin-top:0.4rem;">
            <div style="background:linear-gradient(to right,#1a8a5a,#f0b429,#c0392b);
                        width:180px;height:10px;border-radius:4px;"></div>
            <span style="font-size:0.77rem;">Low → High risk</span>
        </div>""", unsafe_allow_html=True)
        st.caption(tr("disclaimer", lang))

    # ── TAB 5: Uranium mines ───────────────────────────────────────────────────
    with tab_uranium:
        st.markdown(f"#### ☢️ {tr('u_title', lang)}")
        st.caption(tr("u_sub", lang))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Мини / Mines",    "48")
        m2.metric("Добит U / Mined", "~16 720 t")
        m3.metric("Отвали / Heaps",  "298, 84.5 ha")
        m4.metric("Хвостохр. / Tailings", "132 ha, 16 Mt")

        st.markdown("---")

        # Map
        mine_recs = []
        for mine in URANIUM_MINES:
            col = CONTAMINATION_COLORS.get(mine["contamination_level"], [150,150,150])
            mine_recs.append({
                "lat":    mine["lat"],
                "lon":    mine["lon"],
                "color":  col + [180],
                "radius": int(mine["risk_score"] * 12000),
                "name":   mine["name_bg"] if lang=="bg" else mine["name"],
                "cont":   mine["contamination_level"],
                "period": mine["active_period"],
                "status": mine["status"],
            })
        df_mines = pd.DataFrame(mine_recs)

        mine_layer = pdk.Layer("ScatterplotLayer",
            data=df_mines, get_position="[lon,lat]", get_color="color",
            get_radius="radius", pickable=True,
            radius_min_pixels=8, radius_max_pixels=35,
            stroked=True, get_line_color=[80,0,0], line_width_min_pixels=1)

        st.pydeck_chart(pdk.Deck(
            layers=[mine_layer],
            initial_view_state=pdk.ViewState(latitude=42.5, longitude=24.5, zoom=7, pitch=20),
            tooltip={"text": "{name}\n{cont}\n{period}\n{status}"},
            map_style="mapbox://styles/mapbox/light-v10",
        ))
        st.markdown("""
        <span style="display:inline-block;width:11px;height:11px;background:#c0392b;border-radius:50%;margin-right:4px;"></span>High &nbsp;
        <span style="display:inline-block;width:11px;height:11px;background:#962064;border-radius:50%;margin-right:4px;"></span>High (groundwater) &nbsp;
        <span style="display:inline-block;width:11px;height:11px;background:#e07020;border-radius:50%;margin-right:4px;"></span>Moderate-High &nbsp;
        <span style="display:inline-block;width:11px;height:11px;background:#f0b429;border-radius:50%;margin-right:4px;"></span>Moderate
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Detail cards
        for mine in sorted(URANIUM_MINES, key=lambda x: x["risk_score"], reverse=True):
            col  = CONTAMINATION_COLORS.get(mine["contamination_level"], [150,150,150])
            hx   = f"#{col[0]:02x}{col[1]:02x}{col[2]:02x}"
            name = mine["name_bg"] if lang=="bg" else mine["name"]
            note = mine["notes_bg"] if lang=="bg" else mine["notes_en"]
            icon = "☢️" if mine["risk_score"] >= 0.7 else "⚠️"

            with st.expander(f"{icon} {name} — {mine['contamination_level']}"):
                ec1, ec2 = st.columns([2, 1])
                with ec1:
                    st.markdown(f"""
**{tr('u_type',lang)}:** {mine['type']}  
**{tr('u_period',lang)}:** {mine['active_period']}  
**{tr('u_status',lang)}:** {mine['status']}  
**{tr('u_cont',lang)}:** <span style="color:{hx};font-weight:700;">{mine['contamination_level']}</span>  
**{tr('source',lang)}:** {mine['source']}
                    """, unsafe_allow_html=True)
                    st.caption(note)
                with ec2:
                    score_pct = int(mine["risk_score"] * 100)
                    fig_mini = go.Figure(go.Indicator(
                        mode="gauge+number", value=score_pct,
                        number={"suffix":"/100","font":{"size":16}},
                        title={"text":"Risk","font":{"size":10}},
                        gauge={"axis":{"range":[0,100]}, "bar":{"color":hx},
                               "steps":[{"range":[0,40],  "color":"#e8f8f5"},
                                        {"range":[40,70],  "color":"#fff3e0"},
                                        {"range":[70,100], "color":"#fde8e8"}]}
                    ))
                    fig_mini.update_layout(height=155, margin=dict(t=22,b=0,l=8,r=8),
                                          paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_mini, width="stretch")

        st.markdown("---")
        st.markdown(f"#### 📍 {'Провери конкретна точка' if lang=='bg' else 'Check a specific point'}")
        uc1, uc2 = st.columns(2)
        with uc1:
            u_lat = st.number_input("Lat", 41.0, 44.5, 42.697, 0.001, format="%.4f", key="u_lat")
        with uc2:
            u_lon = st.number_input("Lon", 22.0, 29.0, 23.322, 0.001, format="%.4f", key="u_lon")

        if st.button(tr("u_check_btn", lang), key="u_check"):
            u_res = get_uranium_mine_risk(u_lat, u_lon)
            if u_res["found"]:
                st.error(tr("u_warn", lang))
                for site in u_res["sites"]:
                    sname = site["name_bg"] if lang=="bg" else site["name"]
                    snote = site["notes_bg"] if lang=="bg" else site["notes_en"]
                    st.markdown(f"""
                    <div style="background:#fde8e8;border-left:4px solid #c0392b;
                                border-radius:8px;padding:0.7rem;margin:0.3rem 0;">
                      <strong>{sname}</strong> — {site['distance_km']} {tr('u_dist',lang)}<br>
                      <span style="font-size:0.8rem;">{snote}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success(tr("u_safe", lang))
                st.caption(f"{tr('u_nearest',lang)}: {u_res['nearest_site']} ({u_res['nearest_km']} km)")

        st.caption(tr("disclaimer", lang))
