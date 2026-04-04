import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.sample_data import generate_sample_properties, PROPERTY_TYPES

L = {
    "title":   {"bg": "Пазарни Анализи", "en": "Market Analytics"},
    "sub":     {"bg": "Статистики и тенденции на имотния пазар в България",
                "en": "Statistics and trends on the Bulgarian property market"},
    "total":   {"bg": "Общо обяви", "en": "Total listings"},
    "avg_p":   {"bg": "Средна цена", "en": "Avg. price"},
    "med_p":   {"bg": "Медианна цена", "en": "Median price"},
    "avg_a":   {"bg": "Средна площ", "en": "Avg. area"},
    "avg_s":   {"bg": "Ср. цена/м²", "en": "Avg. €/m²"},
    "c_city":  {"bg": "Средна цена по град (€)", "en": "Avg. price by city (€)"},
    "c_type":  {"bg": "Разпределение по тип имот", "en": "Distribution by property type"},
    "c_scat":  {"bg": "Цена vs Площ по градове", "en": "Price vs Area by city"},
    "c_box":   {"bg": "Цена/м² по конструкция", "en": "€/m² by construction type"},
    "c_hist":  {"bg": "Разпределение на цените", "en": "Price distribution"},
    "c_feat":  {"bg": "Най-чести характеристики", "en": "Most common features"},
    "dl":      {"bg": "⬇️ Свали данните (CSV)", "en": "⬇️ Download data (CSV)"},
    "tbl":     {"bg": "Таблица с всички обяви", "en": "All listings table"},
    "city_l":  {"bg": "Град", "en": "City"},
    "nbh_l":   {"bg": "Квартал", "en": "Neighborhood"},
    "type_l":  {"bg": "Тип", "en": "Type"},
    "area_l":  {"bg": "м²", "en": "m²"},
    "price_l": {"bg": "€", "en": "€"},
    "sqm_l":   {"bg": "€/м²", "en": "€/m²"},
    "fl_l":    {"bg": "Ет.", "en": "Floor"},
    "rm_l":    {"bg": "Стаи", "en": "Rooms"},
    "cn_l":    {"bg": "Конструкция", "en": "Construction"},
    "dy_l":    {"bg": "Дни", "en": "Days"},
    "nr_l":    {"bg": "Брой обяви", "en": "No. listings"},
    "ch_l":    {"bg": "Характеристика", "en": "Feature"},
}

def tr(k, l): return L[k][l]


@st.cache_data
def load_data():
    return generate_sample_properties(100)


def render(lang: str = "bg"):
    df = load_data()
    st.markdown(f"### 📊 {tr('title', lang)}")
    st.caption(tr("sub", lang))

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(tr("total", lang), len(df))
    k2.metric(tr("avg_p", lang), f"€ {df['price_eur'].mean():,.0f}")
    k3.metric(tr("med_p", lang), f"€ {df['price_eur'].median():,.0f}")
    k4.metric(tr("avg_a", lang), f"{df['area_sqm'].mean():.0f} м²")
    k5.metric(tr("avg_s", lang), f"€ {df['price_per_sqm'].mean():.0f}")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        city_avg = df.groupby("city").agg(
            avg_price=("price_eur","mean"), count=("id","count"), avg_sqm=("price_per_sqm","mean")
        ).reset_index().sort_values("avg_price", ascending=False)
        fig = px.bar(city_avg, x="avg_price", y="city", orientation="h",
                     title=tr("c_city", lang),
                     color="avg_sqm", color_continuous_scale="Blues",
                     labels={"avg_price":"€","city":"","avg_sqm":"€/m²"},
                     text=city_avg["avg_price"].apply(lambda x:f"€{x:,.0f}"))
        fig.update_layout(height=350, margin=dict(t=40,b=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    with c2:
        if lang == "en":
            df["type_label"] = df["type_bg"].map(PROPERTY_TYPES)
        else:
            df["type_label"] = df["type_bg"]
        tc = df["type_label"].value_counts().reset_index()
        tc.columns = ["type","count"]
        fig2 = px.pie(tc, values="count", names="type",
                      title=tr("c_type", lang),
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=350, margin=dict(t=40,b=0),
                           paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.scatter(df, x="area_sqm", y="price_eur", color="city",
                          size="price_per_sqm", opacity=0.7,
                          hover_data=["type_bg","neighborhood","construction_type"],
                          title=tr("c_scat", lang),
                          labels={"area_sqm":"m²","price_eur":"€","city":""})
        fig3.update_layout(height=350, margin=dict(t=40,b=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, width="stretch")

    with c4:
        fig4 = px.box(df, x="construction_type", y="price_per_sqm",
                      color="construction_type",
                      title=tr("c_box", lang),
                      labels={"construction_type":"","price_per_sqm":"€/m²"},
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig4.update_layout(height=350, margin=dict(t=40,b=10), showlegend=False,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, width="stretch")

    c5, c6 = st.columns(2)
    with c5:
        fig5 = px.histogram(df, x="price_eur", nbins=30, title=tr("c_hist", lang),
                            labels={"price_eur":"€","count":tr("nr_l",lang)},
                            color_discrete_sequence=["#1a5a8a"])
        fig5.update_layout(height=300, margin=dict(t=40,b=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig5, width="stretch")

    with c6:
        all_f = []
        for feats in df["features"]: all_f.extend(feats)
        fs = pd.Series(all_f).value_counts().head(12).reset_index()
        fs.columns = ["feature","count"]
        fig6 = px.bar(fs, x="count", y="feature", orientation="h",
                      title=tr("c_feat", lang), color="count",
                      color_continuous_scale="Teal",
                      labels={"count":tr("nr_l",lang),"feature":tr("ch_l",lang)})
        fig6.update_layout(height=300, margin=dict(t=40,b=10), showlegend=False,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig6, width="stretch")

    st.markdown("---")
    st.markdown(f"#### 📋 {tr('tbl', lang)}")
    show = ["city","neighborhood","type_bg","area_sqm","price_eur","price_per_sqm",
            "floor","rooms","construction_type","days_listed"]
    ren = {
        "city": tr("city_l",lang), "neighborhood": tr("nbh_l",lang),
        "type_bg": tr("type_l",lang), "area_sqm": tr("area_l",lang),
        "price_eur": tr("price_l",lang), "price_per_sqm": tr("sqm_l",lang),
        "floor": tr("fl_l",lang), "rooms": tr("rm_l",lang),
        "construction_type": tr("cn_l",lang), "days_listed": tr("dy_l",lang)
    }
    st.dataframe(df[show].rename(columns=ren), width="stretch", height=380)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(tr("dl", lang), csv, "bg_properties.csv", "text/csv")
