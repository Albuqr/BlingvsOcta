import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Bling vs Octalink · ERP Comparison",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA — Update after March 9th Octalink showcase
# Sections marked ⚠ UNCONFIRMED need validation at the event
# ─────────────────────────────────────────────────────────────────────────────

BLING_PLANS = {
    "Cobalto": {
        "price_monthly": 55, "price_annual": 45.83,
        "users": 5, "storage": "1.5 GB", "mkt_imports": "200/mo",
        "production": False, "sped": False, "pdv": False,
        "note": "Entry tier — no production orders, no SPED"
    },
    "Mercúrio": {
        "price_monthly": 110, "price_annual": 91.66,
        "users": 10, "storage": "3 GB", "mkt_imports": "500/mo",
        "production": True, "sped": False, "pdv": True,
        "note": "Production orders available from this tier"
    },
    "Titânio ★": {
        "price_monthly": 185, "price_annual": 154.00,
        "users": 15, "storage": "9 GB", "mkt_imports": "2,000/mo",
        "production": True, "sped": True, "pdv": True,
        "note": "RECOMMENDED — SPED fiscal from April 2026. April 2026: merges with Mercúrio tier."
    },
    "Platina": {
        "price_monthly": 450, "price_annual": 375.00,
        "users": 50, "storage": "30 GB", "mkt_imports": "5,000/mo",
        "production": True, "sped": True, "pdv": True,
        "note": "For growing operations with higher import volume"
    },
    "Diamante": {
        "price_monthly": 650, "price_annual": 541.00,
        "users": 80, "storage": "45 GB", "mkt_imports": "Unlimited",
        "production": True, "sped": True, "pdv": True,
        "note": "High-volume marketplace. Includes free Premium WhatsApp support."
    },
}

# ⚠ Start and Growth pricing sourced from conjunta.org — validate March 9th
OCTALINK_PLANS = {
    "Start ⚠": {
        "price_monthly": 997, "price_annual": None,
        "users": "N/A — confirm at event", "storage": "Cloud",
        "note": "⚠ Details not publicly disclosed. Requires sales contact.",
        "confirmed": False,
    },
    "Growth ⚠": {
        "price_monthly": 1497, "price_annual": None,
        "users": "N/A — confirm at event", "storage": "Cloud",
        "note": "⚠ Details not publicly disclosed. Requires sales contact.",
        "confirmed": False,
    },
    "Scale": {
        "price_monthly": 2497, "price_annual": None,
        "users": "20 ERP/CRM licenses", "storage": "2 GB backup",
        "note": "800 fiscal docs/mo · 1 dedicated Sr. Analyst · WhatsApp CFO bot · Budget planning · Workflow approval · API connectivity",
        "confirmed": True,
    },
}

# Feature scores: 0–10, with factory weight
# ⚠ Octalink scores based on public info + blog only — no independent reviews exist
FEATURES = {
    "Inventory Control":          {"Bling": 8, "Octalink": 5, "weight": 2.0,
        "bling_detail": "Multi-warehouse, barcode, stock movements, auto-deduction from production",
        "octa_detail": "Basic inventory in ERP Aurora — no manufacturing distinction (raw vs finished)"},
    "NF-e / NFC-e / NFS-e":       {"Bling": 9, "Octalink": 6, "weight": 2.0,
        "bling_detail": "Full NF-e, NFC-e, NFS-e emission across all plans. SEFAZ-integrated.",
        "octa_detail": "NF-e present but fiscal compliance depth unclear. Not core focus."},
    "SPED / Fiscal Compliance":   {"Bling": 7, "Octalink": 4, "weight": 1.5,
        "bling_detail": "SPED EFD expanding to Titânio from April 2026. Bloco K partial only.",
        "octa_detail": "Tax rule automation mentioned but Bloco K / full SPED not documented"},
    "Production Orders / BOM":    {"Bling": 6, "Octalink": 0, "weight": 3.0,
        "bling_detail": "Production orders + composição (BOM) from Mercúrio plan. Auto raw-material deduction. Can generate from sales orders.",
        "octa_detail": "⚠ CONFIRMED ZERO — no production orders, no BOM, no MRP anywhere in platform"},
    "Financial Management":       {"Bling": 7, "Octalink": 9, "weight": 1.5,
        "bling_detail": "AP/AR, cash flow, DRE, bank reconciliation, Conta Digital with PIX/boleto",
        "octa_detail": "Controladoria layer with AI anomaly detection, automated reconciliation, budget planning"},
    "HR / Payroll":               {"Bling": 0, "Octalink": 0, "weight": 2.0,
        "bling_detail": "❌ No HR capability whatsoever. Requires separate Convenia + Pontomais + accountant stack.",
        "octa_detail": "❌ No HR capability. Same gap — separate system required regardless."},
    "Reporting / BI":             {"Bling": 5, "Octalink": 8, "weight": 1.0,
        "bling_detail": "Meu Negócio add-on dashboards (Titânio+). Functional but basic.",
        "octa_detail": "Power BI integration + dedicated BI/Data Analytics squad on Scale plan"},
    "CRM Pipeline":               {"Bling": 3, "Octalink": 8, "weight": 0.5,
        "bling_detail": "No native CRM. Available via extensions (Agendor, Pipedrive, RD Station).",
        "octa_detail": "Native CRM pipeline management included across all plans"},
    "AI Features":                {"Bling": 2, "Octalink": 7, "weight": 0.5,
        "bling_detail": "No AI features in core product. Basic automation only.",
        "octa_detail": "AI anomaly detection, WhatsApp CFO bot (Scale), AI-assisted cash flow forecasting"},
    "Implementation Ease":        {"Bling": 8, "Octalink": 4, "weight": 1.5,
        "bling_detail": "30-day self-serve free trial. Extensive help center. Large user community.",
        "octa_detail": "30-day dedicated implementation included — but no self-serve trial. Requires sales engagement."},
    "Support Quality":            {"Bling": 5, "Octalink": 5, "weight": 1.0,
        "bling_detail": "RA1000 designation but support declining. Up to 20-day ticket response. Premium WhatsApp R$150/mo extra.",
        "octa_detail": "Dedicated Sr. Analyst on Scale plan. No independent reviews to verify quality."},
    "Vendor Stability / Risk":    {"Bling": 9, "Octalink": 3, "weight": 1.5,
        "bling_detail": "Part of LWSA (B3: LWSA3). R$1.49B revenue FY2025. 300k+ users. Largest SME ERP in Brazil.",
        "octa_detail": "Bootstrapped. Est. 15–40 employees. Zero independent reviews. All testimonials on own website."},
    "Pricing Accessibility":      {"Bling": 9, "Octalink": 2, "weight": 2.0,
        "bling_detail": "R$55–650/mo. 30-day free trial. No setup fee. Cancel anytime.",
        "octa_detail": "R$997–2,497/mo. No free trial. Requires sales contact. 5.4–13.5× Bling's entry price."},
    "Marketplace Integration":    {"Bling": 9, "Octalink": 1, "weight": 0.5,
        "bling_detail": "250+ integrations: Mercado Livre, Amazon, Shopee, Magalu, Shopify, Tray, WooCommerce…",
        "octa_detail": "No marketplace integrations. Platform not designed for e-commerce/marketplace."},
}

PROS_CONS = {
    "Bling": {
        "pros": [
            "Largest SME ERP in Brazil — 300k+ users, 20 years in market",
            "Genuine Pequena Indústria module: production orders + BOM from R$110/mo",
            "Full NF-e/NFC-e/NFS-e + SPED expanding to Titânio in April 2026",
            "30-day free trial, no setup fee, cancel anytime",
            "LWSA ecosystem: Tray, Melhor Envio, Conta Digital, embedded credit",
            "Capterra 4.7/5 (102 reviews) · Reclame Aqui RA1000 designation",
            "250+ marketplace integrations — best-in-class for commerce",
            "Large community + extensive help center documentation",
        ],
        "cons": [
            "System instability: 480 complaints on Reclame Aqui in 6 months",
            "Recurring outages (Mondays), post-update crashes, May 2025 DB failure",
            "Support response times up to 20 days since LWSA acquisition",
            "Premium WhatsApp support costs R$150/mo extra (free only Diamante)",
            "Zero HR/payroll — must budget separate system",
            "No MRP, no routing, no quality control, no shop floor management",
            "Production costing is manual/basic — not a proper costing engine",
            "April 2026 pricing restructuring adds near-term uncertainty",
        ],
    },
    "Octalink": {
        "pros": [
            "AI-powered Controladoria with anomaly detection and cash flow alerts",
            "Native CRM pipeline (Bling has none without extension)",
            "Power BI integration for custom dashboards and analytics",
            "WhatsApp CFO bot: query payments, confirm receipts via chat (Scale)",
            "Dedicated 30-day implementation with senior human analyst (Scale)",
            "Automated bank reconciliation with intelligent categorisation",
            "Promising for financially mature companies needing deep backoffice control",
        ],
        "cons": [
            "⚠ ZERO manufacturing production features — no orders, no BOM, no MRP",
            "Zero independent reviews anywhere (no Capterra, G2, Reclame Aqui)",
            "Bootstrapped company, est. 15–40 employees — significant vendor risk",
            "All client references are testimonials on own website — unverifiable",
            "R$997–2,497/mo with no free trial — high cost with no way to test",
            "Start/Growth feature sets not publicly documented",
            "No marketplace integrations whatsoever",
            "Zero HR/payroll — same gap as Bling",
        ],
    },
}

PAIN_POINTS = [
    {
        "pain": "No Inventory System",
        "priority": "Critical",
        "bling_score": 8,
        "octalink_score": 5,
        "bling_note": "Full inventory control + multi-warehouse + barcode + auto stock-deduction from production orders",
        "octalink_note": "Basic inventory in ERP Aurora. No distinction between raw materials and finished goods.",
    },
    {
        "pain": "No HR / Payroll / Attendance",
        "priority": "Critical",
        "bling_score": 0,
        "octalink_score": 0,
        "bling_note": "No HR capability. Requires: accountant for payroll + Convenia for HR admin + Pontomais for attendance.",
        "octalink_note": "No HR capability. Same gap — requires exactly the same separate stack regardless of which platform is chosen.",
    },
    {
        "pain": "No Production Control",
        "priority": "Critical",
        "bling_score": 6,
        "octalink_score": 0,
        "bling_note": "Production orders + BOM composição from Mercúrio (R$110/mo). Auto-deducts raw materials. Can generate from sales orders.",
        "octalink_note": "⚠ CONFIRMED ZERO: no production orders, no bill of materials, no MRP anywhere in the platform.",
    },
    {
        "pain": "No Fiscal / NF-e System",
        "priority": "High",
        "bling_score": 9,
        "octalink_score": 6,
        "bling_note": "Best-in-class NF-e/NFC-e/NFS-e across all plans. SPED EFD expands to Titânio from April 2026. SEFAZ-integrated.",
        "octalink_note": "NF-e present. Tax rule automation mentioned. Bloco K and full SPED depth not documented or confirmed.",
    },
    {
        "pain": "No Structured Reporting / Data",
        "priority": "Medium",
        "bling_score": 5,
        "octalink_score": 8,
        "bling_note": "Meu Negócio add-on dashboards on Titânio+. Functional but limited compared to dedicated BI tools.",
        "octalink_note": "Power BI integration + dedicated BI Data Analytics squad. Octalink genuinely stronger here.",
    },
    {
        "pain": "Brazilian Tax Compliance (SPED, Bloco K, Reforma)",
        "priority": "High",
        "bling_score": 6,
        "octalink_score": 4,
        "bling_note": "SPED ICMS/IPI expanding to Titânio. Bloco K partial (full mandatory for large industrials from Jan 2025). Reforma Tributária roadmap to verify.",
        "octalink_note": "Tax compliance depth unclear. Reforma Tributária IBS/CBS roadmap not publicly documented. Requires event clarification.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATED SCORES
# ─────────────────────────────────────────────────────────────────────────────
def weighted_score(platform):
    total_w = sum(v["weight"] for v in FEATURES.values())
    total_s = sum(v[platform] * v["weight"] for v in FEATURES.values())
    return round((total_s / (total_w * 10)) * 100)

BLING_SCORE  = weighted_score("Bling")
OCTALINK_SCORE = weighted_score("Octalink")

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background: #0a0f1e; }
[data-testid="stSidebar"] { background: #0d1428 !important; border-right: 1px solid #1e2d4a; }
[data-testid="stSidebar"] * { color: #a8b8d0 !important; }
h1, h2, h3 { font-family: 'Sora', sans-serif !important; color: #e8eef8 !important; }
[data-testid="metric-container"] { background: #0d1428; border: 1px solid #1e2d4a; border-radius: 10px; padding: 16px; }
[data-testid="stMetricValue"] { color: #f0a500 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #6a8ab0 !important; }
[data-testid="stMetricDelta"] { color: #4db8ff !important; }
[data-testid="stTabs"] button { color: #6a8ab0 !important; font-weight: 600 !important; font-size: 0.85rem !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #f0a500 !important; border-bottom-color: #f0a500 !important; }
hr { border-color: #1e2d4a !important; }
p, li, span { color: #a8b8d0 !important; }
</style>
""", unsafe_allow_html=True)

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,40,0.6)",
              font=dict(family="Sora, sans-serif", color="#a8b8d0"))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ ERP Comparison")
    st.markdown("**Bling vs Octalink**")
    st.markdown("*Small Manufacturing Factory · Brazil*")
    st.divider()
    page = st.radio("Navigate", [
        "📊  Overview",
        "🔬  Feature Analysis",
        "💰  Pricing",
        "🏭  Factory Fit",
        "📣  Pros & Cons",
        "🏢  Company Profiles",
    ])
    st.divider()
    st.markdown("**Data status**")
    st.markdown("✅ Bling — verified Mar 2026")
    st.markdown("🟡 Octalink pricing — ⚠ unconfirmed")
    st.markdown("📅 Update after: **March 9th event**")
    st.divider()
    st.caption("Albuquerque Consulting · March 2026")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Overview":
    st.title("Bling vs Octalink · ERP Evaluation")
    st.markdown("*Small manufacturing factory · Brazil · Full digitisation from zero · March 2026*")
    st.divider()

    st.markdown("""
    <div style="background:#1c0a0a;border:1px solid #e85a5a;border-left:4px solid #e85a5a;
                padding:14px 20px;border-radius:6px;margin-bottom:20px">
        <span style="color:#e85a5a;font-weight:700;font-size:13px">⚠ CRITICAL RESEARCH FINDING</span><br/>
        <span style="color:#c8a8a8;font-size:13px">
        Octalink has <b>zero manufacturing production features</b> — no production orders, no bill of materials, 
        no raw material tracking. It is a <b>financial backoffice platform</b>, not a manufacturing ERP. 
        Additionally, <b>neither platform includes HR or payroll</b> — a separate system is required regardless of choice.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Gauges
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=BLING_SCORE,
            title={"text": "Bling · Weighted Factory Fit", "font": {"color": "#e8eef8", "size": 13}},
            number={"suffix": "/100", "font": {"color": "#4db8ff", "size": 38}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#1e2d4a"},
                "bar": {"color": "#4db8ff"},
                "bgcolor": "#0d1428", "bordercolor": "#1e2d4a",
                "steps": [{"range": [0, 40], "color": "#111a2a"},
                           {"range": [40, 70], "color": "#162236"},
                           {"range": [70, 100], "color": "#1a2e42"}],
                "threshold": {"line": {"color": "#f0a500", "width": 2}, "thickness": 0.75, "value": 70},
            },
        ))
        fig.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=OCTALINK_SCORE,
            title={"text": "Octalink · Weighted Factory Fit", "font": {"color": "#e8eef8", "size": 13}},
            number={"suffix": "/100", "font": {"color": "#f0a500", "size": 38}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#1e2d4a"},
                "bar": {"color": "#f0a500"},
                "bgcolor": "#0d1428", "bordercolor": "#1e2d4a",
                "steps": [{"range": [0, 40], "color": "#111a2a"},
                           {"range": [40, 70], "color": "#162236"},
                           {"range": [70, 100], "color": "#1a2e42"}],
            },
        ))
        fig2.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        st.metric("Score Gap", f"Bling +{BLING_SCORE - OCTALINK_SCORE} pts", "Across 14 weighted criteria")
        st.metric("Bling Min. Viable Plan", "R$185/mo", "Titânio — includes production + SPED")
        st.metric("Octalink Entry Price", "R$997/mo", f"⚠ Unconfirmed · {round(997/185,1)}× Bling Titânio")
        st.metric("HR/Payroll", "❌ Neither", "Separate system required for both")

    st.divider()

    cb, co = st.columns(2)
    with cb:
        st.markdown("""
        <div style="background:#0d1428;border:1px solid #4db8ff;border-top:3px solid #4db8ff;padding:20px;border-radius:8px">
          <div style="color:#4db8ff;font-weight:700;font-size:17px">Bling</div>
          <div style="color:#3d5a78;font-size:11px;margin-bottom:12px">bling.com.br · Part of LWSA Group (BVMF: LWSA3)</div>
          <div style="color:#a8b8d0;font-size:13px;line-height:1.8">
            Brazil's most-used SME ERP. 300,000+ users. Founded 2005.<br/>
            Acquired by LWSA for <b style="color:#f0a500">R$524M</b> in 2021.<br/>
            Commerce segment revenue: <b style="color:#4db8ff">R$1.07B</b> in FY2025.<br/>
            Has a dedicated <b>Pequena Indústria</b> module with production orders and BOM.<br/>
            Capterra <b>4.7/5</b> · Reclame Aqui <b>RA1000</b> · 30-day free trial.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with co:
        st.markdown("""
        <div style="background:#0d1428;border:1px solid #f0a500;border-top:3px solid #f0a500;padding:20px;border-radius:8px">
          <div style="color:#f0a500;font-weight:700;font-size:17px">Octalink</div>
          <div style="color:#3d5a78;font-size:11px;margin-bottom:12px">octalink.com.br · Octalink Tecnologia LTDA · Sumaré, SP</div>
          <div style="color:#a8b8d0;font-size:13px;line-height:1.8">
            Financial backoffice platform: ERP Aurora + CRM + Controladoria + BI + AI.<br/>
            Founded Dec 2017 by Daniel & Fernando Stavale.<br/>
            <b>Bootstrapped</b>, est. <b>15–40 employees</b>. Zero external funding.<br/>
            <b style="color:#e85a5a">Zero independent reviews</b> anywhere — no Capterra, G2, Reclame Aqui.<br/>
            <b style="color:#e85a5a">No production features confirmed.</b> Targets R$4M+ revenue companies.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FEATURE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔬  Feature Analysis":
    st.title("Feature Analysis")
    st.markdown("*14 criteria scored 0–10, weighted by factory relevance*")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Radar Chart", "Bar Comparison", "Detail Table"])

    features = list(FEATURES.keys())
    bling_scores  = [FEATURES[f]["Bling"]    for f in features]
    octalink_scores = [FEATURES[f]["Octalink"] for f in features]

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=bling_scores + [bling_scores[0]],
            theta=features + [features[0]],
            fill="toself", name="Bling",
            line_color="#4db8ff", fillcolor="rgba(77,184,255,0.15)",
        ))
        fig.add_trace(go.Scatterpolar(
            r=octalink_scores + [octalink_scores[0]],
            theta=features + [features[0]],
            fill="toself", name="Octalink",
            line_color="#f0a500", fillcolor="rgba(240,165,0,0.12)",
        ))
        fig.update_layout(
            **LAYOUT,
            polar=dict(
                bgcolor="#0d1428",
                radialaxis=dict(visible=True, range=[0, 10], color="#3d5a78",
                                gridcolor="#1e2d4a", tickfont=dict(size=9)),
                angularaxis=dict(color="#6a8ab0", gridcolor="#1e2d4a",
                                 tickfont=dict(size=10)),
            ),
            showlegend=True,
            legend=dict(font=dict(color="#a8b8d0"), bgcolor="rgba(0,0,0,0)"),
            height=560, margin=dict(t=20, b=20, l=40, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame({
            "Feature": features,
            "Bling": bling_scores,
            "Octalink": octalink_scores,
            "Weight": [FEATURES[f]["weight"] for f in features],
        }).sort_values("Weight", ascending=False)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Bling", y=df["Feature"], x=df["Bling"],
            orientation="h", marker_color="#4db8ff",
            hovertemplate="<b>Bling</b> %{y}: %{x}/10<extra></extra>",
        ))
        fig2.add_trace(go.Bar(
            name="Octalink", y=df["Feature"], x=df["Octalink"],
            orientation="h", marker_color="#f0a500",
            hovertemplate="<b>Octalink</b> %{y}: %{x}/10<extra></extra>",
        ))
        fig2.update_layout(
            **LAYOUT, barmode="group", height=540,
            xaxis=dict(range=[0, 10], gridcolor="#1e2d4a", tickfont=dict(color="#6a8ab0")),
            yaxis=dict(tickfont=dict(color="#a8b8d0", size=11)),
            legend=dict(font=dict(color="#a8b8d0"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("**Expand any row to see detailed notes per platform.**")
        for fname, fdata in sorted(FEATURES.items(), key=lambda x: -x[1]["weight"]):
            b = fdata["Bling"]
            o = fdata["Octalink"]
            w = fdata["weight"]
            b_bar = "🟦" * b + "⬛" * (10 - b)
            o_bar = "🟧" * o + "⬛" * (10 - o)
            with st.expander(f"**{fname}** — Bling: {b}/10   Octalink: {o}/10   weight: {w}×"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Bling** {b_bar}")
                    st.caption(fdata["bling_detail"])
                with c2:
                    st.markdown(f"**Octalink** {o_bar}")
                    st.caption(fdata["octa_detail"])

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PRICING
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💰  Pricing":
    st.title("Pricing Comparison")
    st.divider()

    tab1, tab2 = st.tabs(["Bling Plans", "Octalink Plans"])

    with tab1:
        st.markdown("#### Bling — Current Plans (March 2026)")
        st.info("📅 **April 2026 change incoming:** Mercúrio merges into a new Titânio Faixa 1 tier. SPED fiscal expands down to Titânio level. Annual billing = 2 months free (pay 10, get 12).")

        for name, p in BLING_PLANS.items():
            is_rec = "★" in name
            border = "#f0a500" if is_rec else "#1e2d4a"
            tag_prod = "✅ Production" if p["production"] else "❌ No production"
            tag_sped = "✅ SPED" if p["sped"] else "❌ No SPED"
            tag_pdv  = "✅ PDV" if p["pdv"] else "❌ No PDV"
            st.markdown(f"""
            <div style="background:#0d1428;border:1px solid {border};border-left:4px solid {border};
                        padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="color:#e8eef8;font-weight:700;font-size:15px">{name}</span>
                <span style="color:#f0a500;font-weight:700;font-size:18px">R${p['price_monthly']}/mo</span>
              </div>
              <div style="color:#6a8ab0;font-size:11px;margin:4px 0 8px 0">
                Annual: R${p['price_annual']}/mo · {p['users']} users · {p['storage']} · {p['mkt_imports']} imports
              </div>
              <div style="font-size:12px;color:#a8b8d0">
                <span style="margin-right:12px">{tag_prod}</span>
                <span style="margin-right:12px">{tag_sped}</span>
                <span style="margin-right:12px">{tag_pdv}</span>
              </div>
              <div style="color:#6a8ab0;font-size:11px;margin-top:6px">{p['note']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Bar chart
        names = list(BLING_PLANS.keys())
        prices = [v["price_monthly"] for v in BLING_PLANS.values()]
        colors_bar = ["#f0a500" if "★" in n else "#4db8ff" for n in names]
        fig = go.Figure(go.Bar(x=names, y=prices, marker_color=colors_bar,
                               hovertemplate="%{x}: R$%{y}/mo<extra></extra>"))
        fig.update_layout(**LAYOUT, height=280, showlegend=False,
                          yaxis=dict(title="R$/month", gridcolor="#1e2d4a"),
                          xaxis=dict(tickfont=dict(color="#a8b8d0")),
                          margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Octalink — Plans (⚠ Partially Unconfirmed)")
        st.warning("⚠ Start and Growth tier details sourced from conjunta.org (third-party). Pricing and features must be validated at the **March 9th product showcase**. Scale tier details verified from official blog.")

        for name, p in OCTALINK_PLANS.items():
            confirmed = p.get("confirmed", False)
            border = "#4db8ff" if confirmed else "#e8834a"
            conf_label = "✅ Verified" if confirmed else "⚠ Unconfirmed"
            st.markdown(f"""
            <div style="background:#0d1428;border:1px solid {border};border-left:4px solid {border};
                        padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="color:#e8eef8;font-weight:700;font-size:15px">{name}</span>
                <span style="color:#f0a500;font-weight:700;font-size:18px">R${p['price_monthly']:,}/mo</span>
              </div>
              <div style="color:#6a8ab0;font-size:11px;margin:4px 0 8px 0">
                {p['users']} · {p['storage']} · {conf_label}
              </div>
              <div style="color:#a8b8d0;font-size:12px">{p['note']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Side-by-side price comparison
        st.markdown("#### Price Comparison — Bling Titânio vs Octalink Entry")
        comp_names = ["Bling Cobalto", "Bling Mercúrio", "Bling Titânio ★", "Bling Platina", "Bling Diamante",
                      "Octalink Start ⚠", "Octalink Growth ⚠", "Octalink Scale"]
        comp_prices = [55, 110, 185, 450, 650, 997, 1497, 2497]
        comp_colors = ["#4db8ff"]*5 + ["#f0a500"]*3
        fig2 = go.Figure(go.Bar(
            x=comp_names, y=comp_prices, marker_color=comp_colors,
            hovertemplate="%{x}: R$%{y}/mo<extra></extra>",
        ))
        fig2.update_layout(**LAYOUT, height=340, showlegend=False,
                           yaxis=dict(title="R$/month", gridcolor="#1e2d4a"),
                           xaxis=dict(tickangle=-30, tickfont=dict(color="#a8b8d0", size=10)),
                           margin=dict(t=20, b=80))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FACTORY FIT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏭  Factory Fit":
    st.title("Factory Fit — Pain Point Analysis")
    st.markdown("*Scoring each platform against the client's specific pain points*")
    st.divider()

    priority_colors = {"Critical": "#e85a5a", "High": "#f0a500", "Medium": "#8aa8c8"}

    for pp in PAIN_POINTS:
        p_col = priority_colors.get(pp["priority"], "#8aa8c8")
        b = pp["bling_score"]
        o = pp["octalink_score"]

        with st.expander(f"**{pp['pain']}** — Priority: {pp['priority']}   |   Bling: {b}/10   Octalink: {o}/10"):
            c1, c2 = st.columns(2)
            with c1:
                pct_b = b * 10
                bar_col_b = "#4db8ff" if b > 0 else "#e85a5a"
                st.markdown(f"""
                <div style="background:#0d1428;border:1px solid #1e2d4a;padding:14px;border-radius:6px">
                  <div style="color:#4db8ff;font-weight:700;margin-bottom:8px">Bling — {b}/10</div>
                  <div style="background:#1e2d4a;border-radius:4px;height:8px;margin-bottom:10px">
                    <div style="background:{bar_col_b};width:{pct_b}%;height:8px;border-radius:4px"></div>
                  </div>
                  <div style="color:#8aa8c8;font-size:12px;line-height:1.6">{pp['bling_note']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                pct_o = o * 10
                bar_col_o = "#f0a500" if o > 0 else "#e85a5a"
                st.markdown(f"""
                <div style="background:#0d1428;border:1px solid #1e2d4a;padding:14px;border-radius:6px">
                  <div style="color:#f0a500;font-weight:700;margin-bottom:8px">Octalink — {o}/10</div>
                  <div style="background:#1e2d4a;border-radius:4px;height:8px;margin-bottom:10px">
                    <div style="background:{bar_col_o};width:{pct_o}%;height:8px;border-radius:4px"></div>
                  </div>
                  <div style="color:#8aa8c8;font-size:12px;line-height:1.6">{pp['octalink_note']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # Summary bar chart
    st.markdown("#### Pain Point Scores — Side by Side")
    pain_names  = [pp["pain"] for pp in PAIN_POINTS]
    bling_pp    = [pp["bling_score"] for pp in PAIN_POINTS]
    octalink_pp = [pp["octalink_score"] for pp in PAIN_POINTS]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Bling", x=pain_names, y=bling_pp, marker_color="#4db8ff",
                         hovertemplate="Bling · %{x}: %{y}/10<extra></extra>"))
    fig.add_trace(go.Bar(name="Octalink", x=pain_names, y=octalink_pp, marker_color="#f0a500",
                         hovertemplate="Octalink · %{x}: %{y}/10<extra></extra>"))
    fig.update_layout(**LAYOUT, barmode="group", height=340,
                      yaxis=dict(range=[0, 10], gridcolor="#1e2d4a", title="Score /10"),
                      xaxis=dict(tickangle=-20, tickfont=dict(size=10, color="#a8b8d0")),
                      legend=dict(font=dict(color="#a8b8d0"), bgcolor="rgba(0,0,0,0)"),
                      margin=dict(t=20, b=80, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROS & CONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📣  Pros & Cons":
    st.title("Pros & Cons")
    st.divider()

    cb, co = st.columns(2)

    with cb:
        st.markdown("#### 🟦 Bling")
        st.markdown("**Pros**")
        for pro in PROS_CONS["Bling"]["pros"]:
            st.markdown(f"✅ {pro}")
        st.divider()
        st.markdown("**Cons**")
        for con in PROS_CONS["Bling"]["cons"]:
            st.markdown(f"❌ {con}")

    with co:
        st.markdown("#### 🟧 Octalink")
        st.markdown("**Pros**")
        for pro in PROS_CONS["Octalink"]["pros"]:
            st.markdown(f"✅ {pro}")
        st.divider()
        st.markdown("**Cons**")
        for con in PROS_CONS["Octalink"]["cons"]:
            st.markdown(f"❌ {con}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: COMPANY PROFILES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏢  Company Profiles":
    st.title("Company Profiles")
    st.divider()

    tab1, tab2 = st.tabs(["Bling / LWSA", "Octalink"])

    with tab1:
        st.markdown("### Bling · LWSA Group")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Founded", "2005")
        c2.metric("Acquisition", "R$524.3M", "LWSA June 2021")
        c3.metric("LWSA FY2025 Revenue", "R$1.49B", "+10.3% YoY")
        c4.metric("Commerce Segment", "R$1.07B", "+15.3% YoY (Bling + Tray + others)")

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Platform Subscribers", "206,300", "+6.8% YoY (all LWSA platforms)")
        c2.metric("Capterra", "4.7 / 5", "102 reviews")
        c3.metric("Reclame Aqui", "RA1000", "8.6/10 · 90.9% resolved")
        c4.metric("RA Complaints (6mo)", "480", "Sep 2025–Feb 2026")

        st.divider()
        st.markdown("**LWSA Ecosystem — Bling Integrations**")
        st.markdown("""
        Bling sits inside a tightly integrated commerce stack:
        - **Tray** — e-commerce storefronts (LWSA sister company)
        - **Melhor Envio** — shipping logistics (LWSA, competitive rates)
        - **Vindi** — payment processing
        - **Conta Digital** — embedded PIX, boleto, rotating credit lines based on invoice volume
        - **250+ marketplace connectors** — Mercado Livre, Amazon, Shopee, Magalu, Americanas, Shopify, WooCommerce…
        """)

        st.divider()
        st.markdown("**Top Reclame Aqui Complaint Categories**")
        complaint_cats = ["System instability / outages", "Support response time", "Post-update crashes",
                          "Price increase (Apr 2025)", "Marketplace sync failures", "Scalability limits"]
        complaint_vol = [34, 24, 18, 12, 8, 4]
        fig = go.Figure(go.Bar(x=complaint_cats, y=complaint_vol, marker_color="#e85a5a",
                               hovertemplate="%{x}: ~%{y}% of complaints<extra></extra>"))
        fig.update_layout(**LAYOUT, height=280, showlegend=False,
                          yaxis=dict(title="% of complaints", gridcolor="#1e2d4a"),
                          xaxis=dict(tickangle=-20, tickfont=dict(size=10, color="#a8b8d0")),
                          margin=dict(t=10, b=80))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Octalink · Octalink Tecnologia LTDA")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Founded", "Dec 2017", "Sumaré, SP")
        c2.metric("Funding", "R$0", "Bootstrapped — zero external investment")
        c3.metric("Team Size", "15–40 est.", "Glassdoor + ZoomInfo estimate")
        c4.metric("Independent Reviews", "ZERO", "No Capterra, G2, Reclame Aqui")

        st.divider()
        st.markdown("**Founders**")
        st.markdown("""
        - **Daniel Stavale** — CEO
        - **Fernando Stavale** — CDO / Co-founder
        - Sumaré, SP (Campinas metropolitan area)
        """)

        st.divider()
        st.markdown("**Platform Architecture**")
        cols = st.columns(4)
        modules = [
            ("ERP Aurora", "#f0a500", "Proprietary ERP — inventory, NF-e, financial management. No production features."),
            ("CRM", "#4db8ff", "Native CRM pipeline management. Included across all plans."),
            ("Controladoria + AI", "#8aa8c8", "AI anomaly detection, automated reconciliation, budget planning, workflow approvals."),
            ("BI / Analytics", "#e8834a", "Power BI integration + dedicated Data Analytics squad on Scale plan."),
        ]
        for col, (mod, col_hex, desc) in zip(cols, modules):
            with col:
                st.markdown(f"""
                <div style="background:#0d1428;border:1px solid {col_hex};border-top:3px solid {col_hex};
                            padding:12px;border-radius:6px;text-align:center">
                  <div style="color:{col_hex};font-weight:700;font-size:13px;margin-bottom:6px">{mod}</div>
                  <div style="color:#6a8ab0;font-size:11px;line-height:1.5">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**Known Integrations**")
        st.markdown("SOC (occupational health) · Power BI · WhatsApp Business API · PIX/boleto banking · NF-e SEFAZ")

        st.divider()
        st.warning("""
        **⚠ Data validation required at March 9th event:**
        - Start and Growth plan pricing and feature details
        - Whether any production/manufacturing features exist
        - Implementation timeline and onboarding process detail
        - Named client references beyond website testimonials
        - Bloco K / SPED fiscal compliance depth
        - Reforma Tributária (IBS/CBS) roadmap
        """)