"""
Generate a mortgage comparison PDF report using reportlab.
"""
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Brand colours
DARK_BLUE  = colors.HexColor("#0d2d4e")
MID_BLUE   = colors.HexColor("#1a5a8a")
TEAL       = colors.HexColor("#0f7a6e")
LIGHT_GREY = colors.HexColor("#f4f7fb")
MID_GREY   = colors.HexColor("#888888")
ORANGE     = colors.HexColor("#e07020")
WHITE      = colors.white


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title", fontSize=22, textColor=WHITE,
                                fontName="Helvetica-Bold", alignment=TA_CENTER,
                                spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=11, textColor=WHITE,
                                   fontName="Helvetica", alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", fontSize=14, textColor=DARK_BLUE,
                              fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontSize=11, textColor=MID_BLUE,
                              fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=9, textColor=colors.black,
                               fontName="Helvetica", spaceAfter=3),
        "small": ParagraphStyle("small", fontSize=8, textColor=MID_GREY,
                                fontName="Helvetica", spaceAfter=2),
        "note": ParagraphStyle("note", fontSize=8, textColor=ORANGE,
                               fontName="Helvetica-Oblique", spaceAfter=6),
        "right": ParagraphStyle("right", fontSize=9, alignment=TA_RIGHT,
                                fontName="Helvetica"),
    }
    return styles


def _header_table(title_line1, title_line2, styles):
    """Coloured header block."""
    header_data = [[
        Paragraph(title_line1, styles["title"]),
    ], [
        Paragraph(title_line2, styles["subtitle"]),
    ]]
    t = Table(header_data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return t


def _kpi_table(kpis: list[tuple[str, str]], styles):
    """Row of KPI boxes: [(label, value), ...]"""
    n = len(kpis)
    col_w = 17 * cm / n
    labels_row = [Paragraph(f"<font color='#{MID_GREY.hexval()[2:]}'>{lab}</font>",
                            styles["small"]) for lab, _ in kpis]
    values_row = [Paragraph(f"<b>{val}</b>", ParagraphStyle(
        "kpi_val", fontSize=13, textColor=DARK_BLUE,
        fontName="Helvetica-Bold", alignment=TA_CENTER)) for _, val in kpis]

    t = Table([labels_row, values_row], colWidths=[col_w]*n)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GREY),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW",     (0,0), (-1,0), 0.5, colors.HexColor("#dde3ea")),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#dde3ea")),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


def generate_mortgage_pdf(
    lang: str,
    loan_eur: float,
    rate_pct: float,
    term_years: int,
    monthly_pmt: float,
    total_paid: float,
    total_interest: float,
    max_loan: float,
    property_price: float,
    down_pct: float,
    income_bgn: float,
    bank_comparison: list[dict],   # [{"name", "rate", "monthly", "total"}]
    scenarios: list[dict] | None = None,
) -> bytes:
    """
    Generate a styled PDF mortgage report.
    Returns PDF as bytes (suitable for st.download_button).
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.8*cm, bottomMargin=2*cm)
    styles = _styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    title1 = "Ипотечен Доклад" if lang == "bg" else "Mortgage Report"
    title2 = f"БГ Имоти | BG Property Finder · {datetime.date.today().strftime('%d.%m.%Y')}"
    story.append(_header_table(title1, title2, styles))
    story.append(Spacer(1, 0.5*cm))

    # ── Loan summary KPIs ─────────────────────────────────────────────────────
    kpi_labels = (
        ["Цена на имота", "Самоучастие", "Размер кредит", "Лихвен %", "Срок"]
        if lang == "bg" else
        ["Property price", "Down payment", "Loan amount", "Interest rate", "Term"]
    )
    kpis = [
        (kpi_labels[0], f"€ {property_price:,.0f}"),
        (kpi_labels[1], f"{down_pct:.0f}%"),
        (kpi_labels[2], f"€ {loan_eur:,.0f}"),
        (kpi_labels[3], f"{rate_pct:.2f}%"),
        (kpi_labels[4], f"{term_years} " + ("г." if lang=="bg" else "yr")),
    ]
    story.append(_kpi_table(kpis, styles))
    story.append(Spacer(1, 0.4*cm))

    # ── Key results ───────────────────────────────────────────────────────────
    hdr = "Резултати" if lang == "bg" else "Key Results"
    story.append(Paragraph(hdr, styles["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=8))

    res_labels = (
        ["Месечна вноска", "Общо изплатено", "Общо лихви", "Макс. кредит (40% DTI)", "Доход (нето)"]
        if lang == "bg" else
        ["Monthly payment", "Total paid", "Total interest", "Max loan (40% DTI)", "Net income"]
    )
    res_data = [
        [res_labels[0], f"€ {monthly_pmt:,.0f}", f"{monthly_pmt*1.9558:,.0f} лв."],
        [res_labels[1], f"€ {total_paid:,.0f}", f"{total_paid*1.9558:,.0f} лв."],
        [res_labels[2], f"€ {total_interest:,.0f}",
         f"{total_interest/loan_eur*100:.1f}% " + ("от главницата" if lang=="bg" else "of principal")],
        [res_labels[3], f"€ {max_loan:,.0f}", ""],
        [res_labels[4], f"{income_bgn:,.0f} лв.", f"€ {income_bgn/1.9558:,.0f}"],
    ]
    res_table = Table(res_data, colWidths=[7*cm, 5*cm, 5*cm])
    res_table.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,0), (0,-1), DARK_BLUE),
        ("ALIGN",         (1,0), (-1,-1), "RIGHT"),
        ("BACKGROUND",    (0,0), (-1,-1), WHITE),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [WHITE, LIGHT_GREY]),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#dde3ea")),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#eaeff4")),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Bank comparison table ─────────────────────────────────────────────────
    hdr2 = "Сравнение на банки" if lang == "bg" else "Bank Comparison"
    story.append(Paragraph(hdr2, styles["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=8))

    col_hdrs = (
        ["Банка", "Лихва %", "Месечна вноска", "Общо за срока", "Макс. LTV", "Такса"]
        if lang == "bg" else
        ["Bank", "Rate %", "Monthly payment", "Total over term", "Max LTV", "Fee"]
    )
    bank_rows = [col_hdrs]
    best_rate = min(b["rate"] for b in bank_comparison)
    for b in bank_comparison:
        is_best = b["rate"] == best_rate
        bank_rows.append([
            b["name"],
            f"{'★ ' if is_best else ''}{b['rate']:.2f}%",
            f"€ {b['monthly']:,.0f}",
            f"€ {b['total']:,.0f}",
            f"{b.get('max_ltv', 80)}%",
            f"{b.get('fee', 1.0):.1f}%",
        ])

    bank_table = Table(bank_rows, colWidths=[5.5*cm, 2.2*cm, 3*cm, 3*cm, 1.8*cm, 1.5*cm])
    best_rows = [i+1 for i, b in enumerate(bank_comparison) if b["rate"] == best_rate]
    ts = TableStyle([
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("BACKGROUND",    (0,0), (-1,0), MID_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GREY]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#dde3ea")),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#eaeff4")),
    ])
    for r in best_rows:
        ts.add("TEXTCOLOR", (0,r), (0,r), TEAL)
        ts.add("FONTNAME",  (0,r), (0,r), "Helvetica-Bold")
    bank_table.setStyle(ts)
    story.append(bank_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Saved scenarios ───────────────────────────────────────────────────────
    if scenarios:
        hdr3 = "Запазени сценарии" if lang == "bg" else "Saved Scenarios"
        story.append(Paragraph(hdr3, styles["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE, spaceAfter=8))
        sc_hdrs = (["Сценарий", "Кредит €", "Лихва %", "Срок", "Банка", "Вноска €"]
                   if lang == "bg" else
                   ["Scenario", "Loan €", "Rate %", "Term", "Bank", "Payment €"])
        sc_rows = [sc_hdrs]
        for sc in scenarios:
            sc_rows.append([
                sc.get("name", ""),
                f"{sc['loan_eur']:,.0f}",
                f"{sc['rate_pct']:.2f}%",
                f"{sc['term_years']} {'г.' if lang=='bg' else 'yr'}",
                sc.get("bank_id", ""),
                f"{sc['monthly_pmt']:,.0f}",
            ])
        sc_t = Table(sc_rows, colWidths=[4*cm, 2.5*cm, 2*cm, 1.8*cm, 4*cm, 2.7*cm])
        sc_t.setStyle(TableStyle([
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 8.5),
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f7a6e")),
            ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("BOX",        (0,0), (-1,-1), 0.5, colors.HexColor("#dde3ea")),
            ("INNERGRID",  (0,0), (-1,-1), 0.3, colors.HexColor("#eaeff4")),
        ]))
        story.append(sc_t)
        story.append(Spacer(1, 0.3*cm))

    # ── Disclaimer ────────────────────────────────────────────────────────────
    disclaimer = (
        "⚠️ Настоящият доклад е с информационна цел. Лихвените проценти са приблизителни и могат да се "
        "променят. Моля, проверявайте актуалните условия директно с банката преди вземане на финансово решение."
        if lang == "bg" else
        "⚠️ This report is for informational purposes only. Interest rates are approximate and subject to change. "
        "Always verify current terms directly with your bank before making any financial decisions."
    )
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(disclaimer, styles["note"]))

    footer_txt = f"БГ Имоти | BG Property Finder · Generated {datetime.date.today().strftime('%d %B %Y')}"
    story.append(Paragraph(footer_txt, styles["small"]))

    doc.build(story)
    return buf.getvalue()
