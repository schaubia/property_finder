import sys
import os
# Ensure the project root is on the path (needed for Streamlit Cloud)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="БГ Имоти | BG Property Finder",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "lang" not in st.session_state:
    st.session_state["lang"] = "bg"

lang = st.session_state["lang"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
.main-header {
    background: linear-gradient(135deg, #0d2d4e 0%, #1a5a8a 55%, #0f7a6e 100%);
    padding: 1.6rem 2rem 1.4rem;
    border-radius: 18px;
    margin-bottom: 1.5rem;
    color: white;
    position: relative;
    overflow: hidden;
}
.main-header h1 { color: white !important; font-size: 2.2rem; margin: 0; letter-spacing: -0.5px; }
.main-header p  { color: rgba(255,255,255,0.78); margin: 0.35rem 0 0; font-size: 0.97rem; }
.nav-pill {
    display: inline-block;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.9);
    margin: 0.7rem 4px 0 0;
}
.sidebar-box { background:#f4f7fb; border-radius:12px; padding:1rem 1rem 0.8rem; margin-bottom:0.9rem; }
.sidebar-box h4 { color:#0d2d4e; margin:0 0 0.7rem; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.6px; font-family:'DM Sans',sans-serif !important; font-weight:600; }
.bank-card { background:white; border-radius:14px; padding:1rem 1.1rem; border:1.5px solid #e4eaf2; margin-bottom:0.75rem; transition:border-color 0.2s, box-shadow 0.2s; }
.bank-card:hover { border-color:#1a5a8a; box-shadow:0 4px 16px rgba(26,90,138,0.12); }
.bank-name  { font-weight:700; color:#0d2d4e; font-size:0.95rem; }
.bank-group { font-size:0.72rem; color:#888; margin-bottom:0.4rem; }
.bank-rate  { color:#0f7a6e; font-size:1.35rem; font-weight:700; font-family:'Playfair Display',serif; }
.bank-live  { display:inline-block; background:#e8f8f5; color:#0a6658; font-size:0.67rem; border-radius:10px; padding:1px 7px; margin-left:6px; }
.bank-cached{ display:inline-block; background:#fff8e8; color:#8a6200; font-size:0.67rem; border-radius:10px; padding:1px 7px; margin-left:6px; }
.prop-badge { display:inline-block; border-radius:20px; padding:2px 11px; font-size:0.72rem; font-weight:500; margin:0 4px 4px 0; }
.badge-type  { background:#e8f1fb; color:#1a5a8a; }
.badge-const { background:#f0f0f0; color:#555; }
.badge-new   { background:#e6f9f4; color:#0a7a68; }
.badge-hot   { background:#fff0e6; color:#c85000; }
.stTabs [data-baseweb="tab-list"] { gap:6px; }
.stTabs [data-baseweb="tab"] { border-radius:9px 9px 0 0; font-family:'DM Sans',sans-serif; font-size:0.88rem; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

col_head, col_lang = st.columns([6, 1])
with col_lang:
    toggle_label = "🇬🇧 EN" if lang == "bg" else "🇧🇬 БГ"
    if st.button(toggle_label, key="lang_btn", use_container_width=True):
        st.session_state["lang"] = "en" if lang == "bg" else "bg"
        st.rerun()

title    = "БГ Имоти" if lang == "bg" else "BG Property Finder"
subtitle = "Намерете мечтания си дом в България" if lang == "bg" else "Find your dream home in Bulgaria"

st.markdown(f"""
<div class="main-header">
    <h1>🏠 {title}</h1>
    <p>{subtitle}</p>
    <span class="nav-pill">🔍 {'Търсене' if lang=='bg' else 'Search'}</span>
    <span class="nav-pill">🏦 {'Ипотека' if lang=='bg' else 'Mortgage'}</span>
    <span class="nav-pill">🗺️ {'Карта' if lang=='bg' else 'Map'}</span>
    <span class="nav-pill">⚠️ {'Геориск' if lang=='bg' else 'Geo-Risk'}</span>
    <span class="nav-pill">📊 {'Анализи' if lang=='bg' else 'Analytics'}</span>
</div>
""", unsafe_allow_html=True)

tabs_bg = ["🔍 Търсене", "🏦 Ипотека", "🗺️ Карта", "📊 Анализи", "⚠️ Геориск"]
tabs_en = ["🔍 Search",  "🏦 Mortgage", "🗺️ Map",   "📊 Analytics", "⚠️ Geo-Risk"]
tab_labels = tabs_bg if lang == "bg" else tabs_en

tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

with tab1:
    from pages import search
    search.render(lang)

with tab2:
    from pages import mortgage
    mortgage.render(lang)

with tab3:
    from pages import map_view
    map_view.render(lang)

with tab4:
    from pages import analytics
    analytics.render(lang)


with tab5:
    from pages import geo_risk
    geo_risk.render(lang)
