import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data.banks import get_banks_with_rates
from data.scrapers import fetch_bnb_reference_rate
from data.watchlist_db import (
    save_mortgage_scenario, get_mortgage_scenarios, delete_mortgage_scenario
)
from utils.mortgage_calc import (
    calculate_monthly_payment, calculate_max_loan,
    calculate_total_cost, calculate_amortization_schedule, eur_to_bgn,
)
from utils.pdf_report import generate_mortgage_pdf

L = {
    "title":      {"bg": "Ипотечен Калкулатор", "en": "Mortgage Calculator"},
    "sub":        {"bg": "Изчислете вноски, сравнете всички банки и изтеглете доклад",
                   "en": "Calculate payments, compare all banks & download your report"},
    "bnb_rate":   {"bg": "БНБ референтен лихвен процент", "en": "BNB Base Interest Rate"},
    "bnb_src":    {"bg": "Източник", "en": "Source"},
    "params":     {"bg": "Параметри на кредита", "en": "Loan parameters"},
    "currency":   {"bg": "Валута", "en": "Currency"},
    "prop_price": {"bg": "Цена на имота", "en": "Property price"},
    "down":       {"bg": "Самоучастие (%)", "en": "Down payment (%)"},
    "loan_lbl":   {"bg": "Размер на кредита", "en": "Loan amount"},
    "rate":       {"bg": "Лихвен процент (%)", "en": "Annual interest rate (%)"},
    "rate_hint":  {"bg": "Съвет: ползвайте БНБ + марж ≈ 2.5%", "en": "Tip: use BNB rate + margin ≈ 2.5%"},
    "term":       {"bg": "Срок (години)", "en": "Term (years)"},
    "income":     {"bg": "Месечен нетен доход (лв.)", "en": "Monthly net income (BGN)"},
    "results":    {"bg": "Резултати", "en": "Results"},
    "monthly":    {"bg": "Месечна вноска", "en": "Monthly payment"},
    "total":      {"bg": "Общо изплатено", "en": "Total paid"},
    "max_loan":   {"bg": "Макс. кредит (40% DTI)", "en": "Max. loan (40% DTI)"},
    "afford":     {"bg": "Достъпност", "en": "Affordability"},
    "ok":         {"bg": "✅ Достъпно", "en": "✅ Affordable"},
    "warn":       {"bg": "⚠️ Напрегнато", "en": "⚠️ Stretched"},
    "over":       {"bg": "❌ Над лимита", "en": "❌ Over limit"},
    "breakdown":  {"bg": "Структура на разходите", "en": "Cost breakdown"},
    "principal":  {"bg": "Главница", "en": "Principal"},
    "interest":   {"bg": "Лихви", "en": "Interest"},
    "fees":       {"bg": "Такси", "en": "Fees"},
    "amort":      {"bg": "📈 График на погасяване", "en": "📈 Amortization chart"},
    "bal":        {"bg": "Остатък главница", "en": "Remaining principal"},
    "int_paid":   {"bg": "Платени лихви", "en": "Interest paid"},
    "banks_hdr":  {"bg": "Всички банки в България", "en": "All Banks in Bulgaria"},
    "scrape_btn": {"bg": "🔄 Актуализирай лихвите", "en": "🔄 Refresh live rates"},
    "scraping":   {"bg": "Зареждам актуални данни…", "en": "Fetching live data…"},
    "live_badge": {"bg": "🟢 live", "en": "🟢 live"},
    "cache_badge":{"bg": "🟡 cached", "en": "🟡 cached"},
    "compare":    {"bg": "Сравнение на месечни вноски", "en": "Monthly payment comparison"},
    "disclaimer": {"bg": "⚠️ Лихвите са приблизителни — проверете условията директно в банката.",
                   "en": "⚠️ Rates are approximate — always verify directly with the bank."},
    "visit":      {"bg": "🌐 Посети", "en": "🌐 Visit"},
    "from_rate":  {"bg": "от", "en": "from"},
    "max_ltv":    {"bg": "Макс. LTV", "en": "Max. LTV"},
    "max_term":   {"bg": "Макс. срок", "en": "Max. term"},
    "fee_lbl":    {"bg": "Такса", "en": "Fee"},
    "pmt_est":    {"bg": "Вноска ~", "en": "Payment ~"},
    "tier1":      {"bg": "🏆 Топ банки", "en": "🏆 Major banks"},
    "tier2":      {"bg": "🏦 Средни банки", "en": "🏦 Tier-2 banks"},
    "group":      {"bg": "Група", "en": "Group"},
    "free_val":   {"bg": "✅ Безплатна оценка", "en": "✅ Free valuation"},
    "life_ins":   {"bg": "Застр. живот", "en": "Life insurance"},
    "prop_ins":   {"bg": "Застр. имот", "en": "Property ins."},
    "req":        {"bg": "задлж.", "en": "required"},
    "opt":        {"bg": "незадлж.", "en": "optional"},
    # Scenarios
    "scen_hdr":   {"bg": "💾 Запази сценарий", "en": "💾 Save scenario"},
    "scen_name":  {"bg": "Име на сценария", "en": "Scenario name"},
    "scen_save":  {"bg": "Запази", "en": "Save"},
    "scen_saved": {"bg": "✅ Сценарият е запазен!", "en": "✅ Scenario saved!"},
    "scen_list":  {"bg": "📋 Запазени сценарии", "en": "📋 Saved scenarios"},
    "scen_del":   {"bg": "Изтрий", "en": "Delete"},
    "scen_empty": {"bg": "Няма запазени сценарии.", "en": "No saved scenarios yet."},
    # PDF
    "pdf_btn":    {"bg": "📄 Изтегли PDF доклад", "en": "📄 Download PDF report"},
    "pdf_name":   {"bg": "ipoteka_doklad.pdf", "en": "mortgage_report.pdf"},
    "pdf_gen":    {"bg": "Генерирам PDF…", "en": "Generating PDF…"},
}

def tr(k, l): return L[k][l]


def render(lang: str = "bg"):
    st.markdown(f"### 🏦 {tr('title', lang)}")
    st.caption(tr("sub", lang))

    default_amount = st.session_state.get("mortgage_amount", 80000)

    # ── BNB reference rate banner ─────────────────────────────────────────────
    bnb = fetch_bnb_reference_rate()
    bnb_col1, bnb_col2, bnb_col3 = st.columns([2, 2, 3])
    with bnb_col1:
        st.metric(tr("bnb_rate", lang), f"{bnb['rate']:.2f}%",
                  delta="BNB BIR", delta_color="off")
    with bnb_col2:
        src_icon = "🟢" if bnb["ok"] else "🟡"
        st.caption(f"{src_icon} {tr('bnb_src', lang)}: {bnb['source']}\n\n{bnb['fetched_at']}")
    with bnb_col3:
        st.info(f"💡 {'Типичната ипотечна лихва = БНБ референтен процент + марж на банката (~1.5-2%)' if lang=='bg' else 'Typical mortgage rate = BNB reference rate + bank margin (~1.5–2%)'}")

    # ── Refresh + scrape row ──────────────────────────────────────────────────
    rc1, rc2 = st.columns([2, 4])
    with rc1:
        do_refresh = st.button(tr("scrape_btn", lang), type="secondary")
    with rc2:
        st.caption("ℹ️ " + ("Данните се кешират за 1 час" if lang=="bg" else "Rates cached for 1 hour"))

    if do_refresh:
        with st.spinner(tr("scraping", lang)):
            banks = get_banks_with_rates(force_refresh=True)
    else:
        banks = get_banks_with_rates(force_refresh=False)

    st.markdown("---")
    col_calc, col_banks = st.columns([2, 1.4])

    # ── LEFT: Calculator ──────────────────────────────────────────────────────
    with col_calc:
        st.markdown(f"#### 📋 {tr('params', lang)}")

        currency = st.radio(tr("currency", lang), ["EUR (€)", "BGN (лв.)"], horizontal=True)
        is_eur = currency.startswith("EUR")

        if is_eur:
            property_price = st.number_input(
                f"{tr('prop_price', lang)} (€)", min_value=10000, max_value=3000000,
                value=int(default_amount / 0.8), step=5000, format="%d"
            )
            down_pct = st.slider(tr("down", lang), 10, 50, 20)
            loan_eur = property_price * (1 - down_pct / 100)
            st.info(f"💳 {tr('loan_lbl', lang)}: **€ {loan_eur:,.0f}** ({eur_to_bgn(loan_eur):,.0f} лв.)")
        else:
            property_price_bgn = st.number_input(
                f"{tr('prop_price', lang)} (лв.)", min_value=20000, max_value=6000000,
                value=int(default_amount / 0.8 * 1.9558), step=10000, format="%d"
            )
            down_pct = st.slider(tr("down", lang), 10, 50, 20)
            loan_eur = (property_price_bgn / 1.9558) * (1 - down_pct / 100)
            property_price = property_price_bgn / 1.9558
            st.info(f"💳 {tr('loan_lbl', lang)}: **{eur_to_bgn(loan_eur):,.0f} лв.** (€ {loan_eur:,.0f})")

        cr, ct = st.columns(2)
        with cr:
            interest_rate = st.number_input(
                tr("rate", lang), min_value=1.0, max_value=12.0,
                value=round(bnb["rate"] + 1.5, 2), step=0.05, format="%.2f",
                help=tr("rate_hint", lang)
            )
        with ct:
            term_years = st.slider(tr("term", lang), 5, 35, 25)

        monthly_income_bgn = st.number_input(
            tr("income", lang), min_value=500, max_value=100000, value=3500, step=100
        )
        monthly_income_eur = monthly_income_bgn / 1.9558

        costs = calculate_total_cost(loan_eur, interest_rate, term_years)
        max_loan = calculate_max_loan(monthly_income_eur, interest_rate, term_years)
        afford_pct = min(130, loan_eur / max_loan * 100) if max_loan > 0 else 130

        st.markdown(f"---\n#### 📊 {tr('results', lang)}")
        r1, r2, r3 = st.columns(3)
        r1.metric(tr("monthly", lang), f"€ {costs['monthly_payment']:,.0f}",
                  f"{eur_to_bgn(costs['monthly_payment']):,.0f} лв.")
        r2.metric(tr("total", lang), f"€ {costs['total_payments']:,.0f}",
                  f"{'лихви' if lang=='bg' else 'interest'}: €{costs['total_interest']:,.0f}")
        r3.metric(tr("max_loan", lang), f"€ {max_loan:,.0f}")

        # Gauge
        g_color = "#0f7a6e" if afford_pct <= 80 else "#e07020" if afford_pct <= 100 else "#c0392b"
        g_label = tr("ok" if afford_pct<=80 else "warn" if afford_pct<=100 else "over", lang)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=afford_pct,
            title={"text": f"{tr('afford', lang)} — {g_label}", "font": {"size": 12}},
            number={"suffix": "%", "font": {"size": 19}},
            gauge={"axis": {"range": [0, 130]}, "bar": {"color": g_color},
                   "steps": [{"range":[0,80],"color":"#e6f9f5"},
                              {"range":[80,100],"color":"#fff3e0"},
                              {"range":[100,130],"color":"#fde8e8"}],
                   "threshold":{"line":{"color":"red","width":2},"thickness":0.75,"value":100}}
        ))
        fig_g.update_layout(height=185, margin=dict(t=28,b=0,l=20,r=20),
                             paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)

        # Cost pie
        fig_pie = px.pie(
            values=[loan_eur, costs["total_interest"], costs["processing_fee"]+costs["notary_fee"]],
            names=[tr("principal",lang), tr("interest",lang), tr("fees",lang)],
            color_discrete_sequence=["#1a5a8a","#e07020","#0f7a6e"],
            title=tr("breakdown", lang)
        )
        fig_pie.update_layout(height=250, margin=dict(t=40,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander(f"📈 {tr('amort', lang)}"):
            sched = pd.DataFrame(calculate_amortization_schedule(loan_eur, interest_rate, term_years))
            fig_a = go.Figure()
            fig_a.add_trace(go.Scatter(x=sched["year"], y=sched["balance"],
                name=tr("bal",lang), fill="tozeroy",
                line=dict(color="#1a5a8a"), fillcolor="rgba(26,90,138,0.15)"))
            fig_a.add_trace(go.Scatter(x=sched["year"], y=sched["total_interest_paid"],
                name=tr("int_paid",lang), line=dict(color="#e07020", dash="dash")))
            fig_a.update_layout(height=280, margin=dict(t=10,b=20),
                                 paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                 legend=dict(orientation="h", y=-0.3),
                                 xaxis_title="Year" if lang=="en" else "Година",
                                 yaxis_title="EUR")
            st.plotly_chart(fig_a, use_container_width=True)

        # ── Save scenario ──────────────────────────────────────────────────────
        st.markdown(f"---\n#### {tr('scen_hdr', lang)}")
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            sc_name = st.text_input(tr("scen_name", lang),
                                    value=f"€{loan_eur:,.0f} @ {interest_rate}% × {term_years}yr")
        with sc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(tr("scen_save", lang), type="primary"):
                save_mortgage_scenario(
                    name=sc_name, loan_eur=loan_eur, rate_pct=interest_rate,
                    term_years=term_years, bank_id="custom",
                    monthly_pmt=costs["monthly_payment"],
                    total_paid=costs["total_payments"]
                )
                st.success(tr("scen_saved", lang))

        # ── PDF export ─────────────────────────────────────────────────────────
        st.markdown("---")
        bank_comparison_data = [{
            "name": (b["bank_bg"] if lang=="bg" else b["bank_en"]),
            "rate": b["live_min_rate"],
            "monthly": calculate_monthly_payment(loan_eur, b["live_min_rate"], term_years),
            "total": calculate_monthly_payment(loan_eur, b["live_min_rate"], term_years) * term_years * 12,
            "max_ltv": b["max_ltv"],
            "fee": b["processing_fee_pct"],
        } for b in banks]

        saved_sc = get_mortgage_scenarios()

        if st.button(f"📄 {tr('pdf_btn', lang)}", type="primary"):
            with st.spinner(tr("pdf_gen", lang)):
                pdf_bytes = generate_mortgage_pdf(
                    lang=lang,
                    loan_eur=loan_eur,
                    rate_pct=interest_rate,
                    term_years=term_years,
                    monthly_pmt=costs["monthly_payment"],
                    total_paid=costs["total_payments"],
                    total_interest=costs["total_interest"],
                    max_loan=max_loan,
                    property_price=property_price,
                    down_pct=down_pct,
                    income_bgn=monthly_income_bgn,
                    bank_comparison=bank_comparison_data,
                    scenarios=saved_sc if saved_sc else None,
                )
            st.download_button(
                label=f"⬇️ {tr('pdf_btn', lang)}",
                data=pdf_bytes,
                file_name=tr("pdf_name", lang),
                mime="application/pdf",
            )

    # ── RIGHT: Bank cards ──────────────────────────────────────────────────────
    with col_banks:
        st.markdown(f"#### 🏦 {tr('banks_hdr', lang)}")

        for tier_key, tier_banks in [("tier1",[b for b in banks if b["tier"]==1]),
                                      ("tier2",[b for b in banks if b["tier"]==2])]:
            st.markdown(f"**{tr(tier_key, lang)}**")
            for b in tier_banks:
                live_rate = b["live_min_rate"]
                monthly   = calculate_monthly_payment(loan_eur, live_rate, term_years)
                src_cls   = "bank-live" if b["data_source"]=="live" else "bank-cached"
                src_badge = tr("live_badge",lang) if b["data_source"]=="live" else tr("cache_badge",lang)
                bank_name = b["bank_bg"] if lang=="bg" else b["bank_en"]
                note      = b["promo_note_bg"] if lang=="bg" else b["promo_note_en"]
                web       = b["website_bg"] if lang=="bg" else b["website_en"]
                ins_life  = tr("req",lang) if b["life_insurance"] else tr("opt",lang)
                ins_prop  = tr("req",lang) if b["property_insurance"] else tr("opt",lang)
                free_val  = f'<div style="color:#0a6658;font-size:0.68rem;">{tr("free_val",lang)}</div>' if b["free_valuation"] else ""
                mshare    = f'<span style="font-size:0.68rem;color:#888;">({b["market_share_pct"]}% market share)</span>' if b["tier"]==1 else ""

                st.markdown(f"""
                <div class="bank-card">
                  <div class="bank-name">{bank_name} {mshare}</div>
                  <div class="bank-group">{tr('group',lang)}: {b['group']}</div>
                  <div class="bank-rate">{tr("from_rate",lang)} {live_rate}%
                    <span class="{src_cls}">{src_badge}</span>
                  </div>
                  <div style="font-size:0.77rem;color:#333;margin-top:0.3rem;line-height:1.75;">
                    💰 {tr("pmt_est",lang)} <strong>€ {monthly:,.0f}</strong> / {"мес" if lang=="bg" else "mo"}<br>
                    📅 {tr("max_term",lang)}: {b['max_term_years']} {"г." if lang=="bg" else "yr"} &nbsp;|&nbsp;
                    🏠 {tr("max_ltv",lang)}: {b['max_ltv']}%<br>
                    📋 {tr("fee_lbl",lang)}: {b['processing_fee_pct']}% &nbsp;|&nbsp;
                    🏥 {tr("life_ins",lang)}: {ins_life}<br>
                    🏡 {tr("prop_ins",lang)}: {ins_prop} &nbsp;&nbsp; {free_val}
                  </div>
                  <div style="font-size:0.71rem;color:#0f7a6e;margin-top:0.25rem;">ℹ️ {note}</div>
                  <div style="margin-top:0.3rem;">
                    <a href="{web}" target="_blank" style="font-size:0.72rem;color:#1a5a8a;text-decoration:none;">
                      🌐 {tr("visit",lang)} →
                    </a>
                    &nbsp; 📞 <span style="font-size:0.71rem;color:#555;">{b['phone']}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Bar chart comparison
        st.markdown(f"**{tr('compare', lang)}**")
        bar_names = [(b["bank_bg"] if lang=="bg" else b["bank_en"]).split(" ")[0]
                     + (f" ({b['market_share_pct']}%)" if b["tier"]==1 else "")
                     for b in banks]
        bar_pmts  = [calculate_monthly_payment(loan_eur, b["live_min_rate"], term_years) for b in banks]
        min_pmt   = min(bar_pmts)
        fig_bar   = go.Figure(go.Bar(
            x=bar_pmts, y=bar_names, orientation="h",
            marker_color=["#0f7a6e" if p==min_pmt else "#a8c5e0" for p in bar_pmts],
            text=[f"€{p:,.0f}" for p in bar_pmts], textposition="outside"
        ))
        fig_bar.update_layout(
            height=340, margin=dict(t=5,b=5,l=5,r=65),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="EUR / " + ("месец" if lang=="bg" else "month")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption(tr("disclaimer", lang))

        # ── Saved scenarios panel ──────────────────────────────────────────────
        st.markdown(f"---\n**{tr('scen_list', lang)}**")
        scenarios = get_mortgage_scenarios()
        if not scenarios:
            st.caption(tr("scen_empty", lang))
        else:
            for sc in scenarios:
                sc_col1, sc_col2 = st.columns([4, 1])
                with sc_col1:
                    st.markdown(f"""
                    <div style="background:#f4f7fb;border-radius:8px;padding:0.5rem 0.7rem;margin-bottom:0.4rem;font-size:0.8rem;">
                      <strong>{sc['name']}</strong><br>
                      €{sc['loan_eur']:,.0f} @ {sc['rate_pct']}% × {sc['term_years']}{"г." if lang=="bg" else "yr"}
                      → €{sc['monthly_pmt']:,.0f}/{"мес" if lang=="bg" else "mo"}<br>
                      <span style="color:#888;font-size:0.7rem;">{sc['created_at']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with sc_col2:
                    if st.button("🗑️", key=f"del_sc_{sc['id']}"):
                        delete_mortgage_scenario(sc["id"])
                        st.rerun()
