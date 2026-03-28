import streamlit as st
import pandas as pd
from data.sample_data import generate_sample_properties, BULGARIAN_CITIES, PROPERTY_TYPES, FEATURES, CONSTRUCTION_TYPES
from data.scrapers import get_live_listings
from data.watchlist_db import (
    add_to_watchlist, remove_from_watchlist, get_watchlist,
    is_in_watchlist, update_notes, watchlist_count
)

L = {
    "title":      {"bg": "Търсене на имоти", "en": "Property Search"},
    "tab_sample": {"bg": "🏘️ Примерни обяви", "en": "🏘️ Sample listings"},
    "tab_live":   {"bg": "🌐 Живи обяви (imot.bg)", "en": "🌐 Live listings (imot.bg)"},
    "tab_watch":  {"bg": "❤️ Моят списък", "en": "❤️ My Watchlist"},
    "city":       {"bg": "Град", "en": "City"},
    "city_all":   {"bg": "Всички градове", "en": "All cities"},
    "type":       {"bg": "Тип имот", "en": "Property type"},
    "type_all":   {"bg": "Всички типове", "en": "All types"},
    "price":      {"bg": "Цена (EUR)", "en": "Price (EUR)"},
    "area":       {"bg": "Площ (кв.м)", "en": "Area (sqm)"},
    "const":      {"bg": "Конструкция", "en": "Construction"},
    "features":   {"bg": "Специфики (трябва да включва)", "en": "Features (must include)"},
    "new_only":   {"bg": "🆕 Само нови обяви (≤7 дни)", "en": "🆕 New listings only (≤7 days)"},
    "sort":       {"bg": "Сортирай по", "en": "Sort by"},
    "s_pa":       {"bg": "Цена ↑", "en": "Price ↑"},
    "s_pd":       {"bg": "Цена ↓", "en": "Price ↓"},
    "s_aa":       {"bg": "Площ ↑", "en": "Area ↑"},
    "s_ad":       {"bg": "Площ ↓", "en": "Area ↓"},
    "s_sqm":      {"bg": "Цена/м² ↑", "en": "Price/m² ↑"},
    "s_new":      {"bg": "Най-нови", "en": "Newest"},
    "found":      {"bg": "Намерени имоти", "en": "Properties found"},
    "avg_p":      {"bg": "Средна цена", "en": "Avg. price"},
    "avg_a":      {"bg": "Средна площ", "en": "Avg. area"},
    "avg_s":      {"bg": "Ср. цена/м²", "en": "Avg. price/m²"},
    "no_res":     {"bg": "Няма намерени имоти. Разширете търсенето.", "en": "No properties found. Widen your search."},
    "desc":       {"bg": "Описание", "en": "Description"},
    "agency":     {"bg": "Агенция", "en": "Agency"},
    "mort_btn":   {"bg": "📊 Изчисли ипотека", "en": "📊 Mortgage calc"},
    "watch_add":  {"bg": "❤️ Запази", "en": "❤️ Save"},
    "watch_rm":   {"bg": "💔 Премахни", "en": "💔 Remove"},
    "watch_ok":   {"bg": "✅ Добавено в списъка!", "en": "✅ Added to watchlist!"},
    "watch_dup":  {"bg": "ℹ️ Вече е в списъка.", "en": "ℹ️ Already in watchlist."},
    "watch_rm_ok":{"bg": "🗑️ Премахнато.", "en": "🗑️ Removed."},
    "fl":         {"bg": "ет.", "en": "fl."},
    "rooms":      {"bg": "стаи", "en": "rooms"},
    # live tab
    "live_city":  {"bg": "Град за търсене", "en": "Search city"},
    "live_type":  {"bg": "Тип имот", "en": "Property type"},
    "live_price": {"bg": "Макс. цена (€)", "en": "Max price (€)"},
    "live_btn":   {"bg": "🔍 Търси в imot.bg + imoti.net", "en": "🔍 Search imot.bg + imoti.net"},
    "live_spin":  {"bg": "Изтеглям живи обяви…", "en": "Fetching live listings…"},
    "live_none":  {"bg": "Не бяха намерени обяви. Опитайте с различни параметри.",
                   "en": "No listings found. Try different parameters."},
    "live_src":   {"bg": "Източник", "en": "Source"},
    "live_note":  {"bg": "⚠️ Реалният скрейпинг зависи от структурата на сайта. Резултатите могат да варират.",
                   "en": "⚠️ Live scraping depends on the site structure. Results may vary."},
    # watchlist tab
    "wl_empty":   {"bg": "Списъкът е празен. Добавете имоти с бутона ❤️.",
                   "en": "Your watchlist is empty. Add properties with the ❤️ button."},
    "wl_notes":   {"bg": "Бележки", "en": "Notes"},
    "wl_save_n":  {"bg": "Запази бележката", "en": "Save note"},
    "wl_remove":  {"bg": "🗑️ Премахни", "en": "🗑️ Remove"},
    "wl_count":   {"bg": "имота в списъка", "en": "properties in watchlist"},
    "wl_export":  {"bg": "⬇️ Изтегли списъка (CSV)", "en": "⬇️ Download watchlist (CSV)"},
    "source_lnk": {"bg": "🔗 Обява", "en": "🔗 Listing"},
}

def _(k, l): return L[k][l]


@st.cache_data
def load_data():
    return generate_sample_properties(100)


def _property_card(row, lang, prefix="s", show_source=False):
    """Render a single property card. Works for both sample and live data."""
    with st.container():
        col_info, col_price = st.columns([3, 1])
        with col_info:
            badges = ""
            if row.get("is_new"):
                badges += '<span class="prop-badge badge-new">🆕 ' + ("Нова" if lang=="bg" else "New") + '</span>'
            if row.get("days_listed", 99) <= 3:
                badges += '<span class="prop-badge badge-hot">🔥</span>'
            type_label = row.get("type_bg","") if lang=="bg" else row.get("type_en","")
            badges += f'<span class="prop-badge badge-type">{type_label}</span>'
            if show_source:
                badges += f'<span class="prop-badge badge-const">{row.get("source","")}</span>'
            else:
                badges += f'<span class="prop-badge badge-const">{row.get("construction_type","")}</span>'

            st.markdown(f"**{row['title']}**")
            st.markdown(badges, unsafe_allow_html=True)

            s1, s2, s3, s4 = st.columns(4)
            s1.markdown(f"📐 **{row['area_sqm']} м²**")
            s2.markdown(f"🏢 **{row.get('floor',0)}/{row.get('floors_total',0)} {_('fl',lang)}**" if row.get("floors_total") else "🏢 —")
            s3.markdown(f"🛏️ **{row.get('rooms',0)} {_('rooms',lang)}**")
            s4.markdown(f"📅 {row.get('listing_date','')}")

            feats = row.get("features", [])[:6]
            if feats:
                st.caption("✅ " + " · ".join(feats))

            with st.expander(f"📄 {_('desc', lang)}"):
                st.write(row.get("description","")[:600])
                agency = row.get("agency","")
                contact = row.get("contact","")
                if contact:
                    st.caption(f"📞 {contact} · {_('agency',lang)}: {agency}")
                src_url = row.get("source_url","")
                if src_url:
                    st.markdown(f"[{_('source_lnk',lang)}]({src_url})")

        with col_price:
            st.markdown(f"""
            <div style="text-align:right;padding:0.4rem 0;">
                <div style="font-size:1.5rem;font-weight:700;color:#0d2d4e;font-family:'Playfair Display',serif;">
                    € {row['price_eur']:,}
                </div>
                <div style="color:#555;font-size:0.8rem;">{row.get('price_bgn',int(row['price_eur']*1.9558)):,} лв.</div>
                <div style="color:#888;font-size:0.73rem;">€ {row.get('price_per_sqm',0):,} / м²</div>
                <div style="color:#1a5a8a;font-size:0.73rem;margin-top:0.35rem;">
                    📍 {row.get('city','')}{', ' + row['neighborhood'] if row.get('neighborhood') else ''}
                </div>
            </div>""", unsafe_allow_html=True)

            prop_id = row.get("id", 0)
            in_wl   = is_in_watchlist(prop_id)
            btn_lbl = _("watch_rm", lang) if in_wl else _("watch_add", lang)
            if st.button(btn_lbl, key=f"{prefix}_wl_{prop_id}"):
                if in_wl:
                    remove_from_watchlist(prop_id)
                    st.toast(_("watch_rm_ok", lang))
                else:
                    ok = add_to_watchlist(dict(row), notes="")
                    st.toast(_("watch_ok", lang) if ok else _("watch_dup", lang))
                st.rerun()

            if st.button(_("mort_btn", lang), key=f"{prefix}_m_{prop_id}"):
                st.session_state["mortgage_amount"] = int(row["price_eur"] * 0.8)
                st.info("→ Mortgage ✓")
    st.divider()


def render(lang: str = "bg"):
    wl_count = watchlist_count()
    wl_label = f"❤️ {'Моят списък' if lang=='bg' else 'My Watchlist'} ({wl_count})"
    tab1, tab2, tab3 = st.tabs([
        _("tab_sample", lang),
        _("tab_live", lang),
        wl_label,
    ])

    # ── Shared sidebar filters (for sample tab) ────────────────────────────────
    df = load_data()

    with st.sidebar:
        st.markdown(f'<div class="sidebar-box"><h4>📍 {_("city", lang)}</h4>', unsafe_allow_html=True)
        selected_cities = st.multiselect(
            _("city", lang), options=sorted(df["city"].unique()),
            default=[], placeholder=_("city_all", lang), label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-box"><h4>🏠 {_("type", lang)}</h4>', unsafe_allow_html=True)
        type_opts = [(f"{k} / {v}" if lang=="en" else k) for k,v in PROPERTY_TYPES.items()]
        type_sel_d = st.multiselect(_("type", lang), options=type_opts, default=[], label_visibility="collapsed")
        selected_types = [t.split(" / ")[0] for t in type_sel_d]
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-box"><h4>💶 {_("price", lang)}</h4>', unsafe_allow_html=True)
        price_min, price_max = st.slider(_("price", lang),
            int(df["price_eur"].min()), int(df["price_eur"].max()),
            (int(df["price_eur"].min()), int(df["price_eur"].max())),
            step=5000, format="€%d", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-box"><h4>📐 {_("area", lang)}</h4>', unsafe_allow_html=True)
        area_min, area_max = st.slider(_("area", lang),
            int(df["area_sqm"].min()), int(df["area_sqm"].max()),
            (int(df["area_sqm"].min()), int(df["area_sqm"].max())),
            step=5, format="%d m²", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-box"><h4>🏗️ {_("const", lang)}</h4>', unsafe_allow_html=True)
        sel_const = st.multiselect(_("const", lang), CONSTRUCTION_TYPES, default=[], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sidebar-box"><h4>⭐ {_("features", lang)}</h4>', unsafe_allow_html=True)
        req_feats = st.multiselect(_("features", lang), FEATURES, default=[], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        only_new = st.checkbox(_("new_only", lang), value=False)
        st.markdown("---")
        sort_opts = [_("s_pa",lang),_("s_pd",lang),_("s_aa",lang),_("s_ad",lang),_("s_sqm",lang),_("s_new",lang)]
        sort_by = st.selectbox(_("sort", lang), sort_opts)

    # ── TAB 1: Sample listings ─────────────────────────────────────────────────
    with tab1:
        st.markdown(f"### 🔍 {_('title', lang)}")

        filtered = df.copy()
        if selected_cities: filtered = filtered[filtered["city"].isin(selected_cities)]
        if selected_types:  filtered = filtered[filtered["type_bg"].isin(selected_types)]
        filtered = filtered[(filtered["price_eur"]>=price_min)&(filtered["price_eur"]<=price_max)]
        filtered = filtered[(filtered["area_sqm"]>=area_min)&(filtered["area_sqm"]<=area_max)]
        if sel_const:  filtered = filtered[filtered["construction_type"].isin(sel_const)]
        if req_feats:  filtered = filtered[filtered["features"].apply(lambda f: all(ft in f for ft in req_feats))]
        if only_new:   filtered = filtered[filtered["is_new"]==True]

        sk_map = {_("s_pa",lang):("price_eur",True), _("s_pd",lang):("price_eur",False),
                  _("s_aa",lang):("area_sqm",True),  _("s_ad",lang):("area_sqm",False),
                  _("s_sqm",lang):("price_per_sqm",True), _("s_new",lang):("days_listed",True)}
        sc, asc = sk_map.get(sort_by, ("price_eur", True))
        filtered = filtered.sort_values(sc, ascending=asc)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric(_("found",lang), len(filtered))
        if len(filtered):
            c2.metric(_("avg_p",lang), f"€ {filtered['price_eur'].mean():,.0f}")
            c3.metric(_("avg_a",lang), f"{filtered['area_sqm'].mean():.0f} м²")
            c4.metric(_("avg_s",lang), f"€ {filtered['price_per_sqm'].mean():.0f}")
        st.markdown("---")

        if len(filtered)==0:
            st.warning(_("no_res", lang))
        else:
            for _, row in filtered.iterrows():
                _property_card(row, lang, prefix="s")

    # ── TAB 2: Live scraping ───────────────────────────────────────────────────
    with tab2:
        st.markdown(f"### 🌐 {_('tab_live', lang)}")
        st.caption(_("live_note", lang))

        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            live_city = st.selectbox(_("live_city", lang), list(BULGARIAN_CITIES.keys()), index=0)
        with lc2:
            live_type_opts = list(PROPERTY_TYPES.keys()) if lang=="bg" else [f"{k} / {v}" for k,v in PROPERTY_TYPES.items()]
            live_type_disp = st.selectbox(_("live_type", lang), live_type_opts)
            live_type = live_type_disp.split(" / ")[0]
        with lc3:
            live_price = st.number_input(_("live_price", lang), min_value=20000, max_value=2000000,
                                          value=300000, step=10000)

        force_live = st.button(_("live_btn", lang), type="primary")

        if force_live or st.session_state.get("live_results"):
            with st.spinner(_("live_spin", lang)):
                listings, status_msg = get_live_listings(live_city, live_type, live_price,
                                                          force=force_live)
            st.session_state["live_results"] = listings

            st.info(f"📡 {status_msg}")

            if not listings:
                st.warning(_("live_none", lang))
            else:
                c1,c2,c3 = st.columns(3)
                c1.metric(_("found",lang), len(listings))
                if listings:
                    prices = [l["price_eur"] for l in listings if l.get("price_eur")]
                    areas  = [l["area_sqm"] for l in listings if l.get("area_sqm")]
                    if prices: c2.metric(_("avg_p",lang), f"€ {sum(prices)/len(prices):,.0f}")
                    if areas:  c3.metric(_("avg_a",lang), f"{sum(areas)/len(areas):.0f} м²")
                st.markdown("---")
                for listing in listings:
                    _property_card(listing, lang, prefix="l", show_source=True)
        else:
            st.info("👆 " + ("Натиснете бутона за да заредите реални обяви от imot.bg и imoti.net"
                             if lang=="bg" else
                             "Click the button above to fetch real listings from imot.bg and imoti.net"))

    # ── TAB 3: Watchlist ───────────────────────────────────────────────────────
    with tab3:
        st.markdown(f"### ❤️ {'Моят списък с имоти' if lang=='bg' else 'My Property Watchlist'}")
        wl = get_watchlist()

        if not wl:
            st.info(_("wl_empty", lang))
        else:
            st.metric(_("wl_count" if lang=="bg" else "wl_count", lang),
                      f"{len(wl)} " + _("wl_count", lang))
            st.markdown("---")

            for item in wl:
                with st.container():
                    wcol1, wcol2 = st.columns([3, 1])
                    with wcol1:
                        st.markdown(f"**{item['title']}**")
                        s1,s2,s3 = st.columns(3)
                        s1.markdown(f"📐 {item['area_sqm']} м²")
                        s2.markdown(f"📅 {_('wl_notes',lang) if False else item['listing_date']}")
                        s3.markdown(f"🕐 {('Добавено' if lang=='bg' else 'Added')}: {item['added_at']}")

                        notes_val = st.text_input(
                            _("wl_notes", lang), value=item.get("notes",""),
                            key=f"wl_notes_{item['id']}"
                        )
                        if st.button(_("wl_save_n", lang), key=f"wl_sn_{item['id']}"):
                            update_notes(item["prop_id"], notes_val)
                            st.toast("✅ " + ("Запазено" if lang=="bg" else "Saved"))

                    with wcol2:
                        st.markdown(f"""
                        <div style="text-align:right;">
                            <div style="font-size:1.4rem;font-weight:700;color:#0d2d4e;">€ {item['price_eur']:,}</div>
                            <div style="color:#555;font-size:0.8rem;">{item['price_bgn']:,} лв.</div>
                            <div style="color:#1a5a8a;font-size:0.73rem;">📍 {item['city']}, {item['neighborhood']}</div>
                        </div>""", unsafe_allow_html=True)
                        if st.button(_("wl_remove", lang), key=f"wl_rm_{item['id']}"):
                            remove_from_watchlist(item["prop_id"])
                            st.rerun()
                st.divider()

            # Export watchlist
            wl_df = pd.DataFrame(wl).drop(columns=["features","description"], errors="ignore")
            csv = wl_df.to_csv(index=False).encode("utf-8")
            st.download_button(_("wl_export", lang), csv, "watchlist.csv", "text/csv")
