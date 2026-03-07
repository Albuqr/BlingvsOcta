import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Bling vs Octalink · Comparativo ERP",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DADOS — Atualizar após evento Octalink em 9 de março
# Seções marcadas com ⚠ PENDENTE precisam ser validadas no evento
# ─────────────────────────────────────────────────────────────────────────────

BLING_PLANS = {
    "Cobalto": {
        "price_monthly": 55, "price_annual": 45.83,
        "users": 5, "dados": "60 MB", "arquivos": "1,5 GB", "mkt_imports": "200/mês",
        "production": False, "sped": False, "pdv": False,
        "note": "Plano de entrada. Gestão de estoque, vendas multicanal, contas a pagar/receber, Conta Digital PJ. Sem ordens de produção, sem SPED."
    },
    "Mercúrio": {
        "price_monthly": 110, "price_annual": 91.66,
        "users": 10, "dados": "120 MB", "arquivos": "3 GB", "mkt_imports": "500/mês",
        "production": True, "sped": False, "pdv": True,
        "note": "Tudo do Cobalto + gestão financeira completa (emissão de boletos, conciliação bancária, DRE) + PDV com caixas individuais."
    },
    "Titânio ★": {
        "price_monthly": 185, "price_annual": 154.00,
        "users": 15, "dados": "360 MB", "arquivos": "9 GB", "mkt_imports": "2.000/mês",
        "production": True, "sped": True, "pdv": True,
        "note": "RECOMENDADO — Tudo do Mercúrio + etiqueta logística automática + dashboards Meu Negócio (até 3 contas Bling) + integração com 1 maquininha POS. SPED fiscal a partir de abril/2026."
    },
    "Platina": {
        "price_monthly": 450, "price_annual": 375.00,
        "users": 50, "dados": "1,2 GB", "arquivos": "30 GB", "mkt_imports": "5.000/mês",
        "production": True, "sped": True, "pdv": True,
        "note": "Tudo do Titânio + dashboards Meu Negócio com até 5 contas Bling + integração com 3 maquininhas POS."
    },
    "Diamante": {
        "price_monthly": 650, "price_annual": 541.00,
        "users": 80, "dados": "1,8 GB", "arquivos": "45 GB", "mkt_imports": "Ilimitado",
        "production": True, "sped": True, "pdv": True,
        "note": "Tudo do Platina + dashboards com até 10 contas Bling + Suporte Premium completo (telefone, chat e ticket) incluso."
    },
}

# Preços confirmados no site oficial do Octalink (março/2026)
OCTALINK_PLANS = {
    "Start": {
        "price_monthly": 1597, "price_annual": None,
        "users": "5 licenças Aurora", "storage": "500 MB backup",
        "note": "5 licenças Aurora · 200 documentos fiscais/mês · 1 Analista Jr. · 500 MB backup, infra e armazenamento de arquivos",
        "confirmed": True,
    },
    "Pro ★": {
        "price_monthly": 3797, "price_annual": None,
        "users": "10 licenças ERP/CRM", "storage": "1 GB backup",
        "note": "MELHOR OPÇÃO (conforme site) — 10 licenças Aurora ERP/CRM · 400 docs fiscais/mês · 1 CFO WhatsApp · Planejamento Orçamentário (Budget + Forecast) · Workflow de aprovação por alçada · Conexão API · 1 GB backup",
        "confirmed": True,
    },
    "Growth": {
        "price_monthly": 7897, "price_annual": None,
        "users": "20 licenças ERP/CRM", "storage": "2 GB backup",
        "note": "Controladoria estratégica + ERP + Analytics + equipe dedicada · 20 licenças Aurora ERP/CRM · 800 docs fiscais/mês · 1 Analista Sr. + 1 CFO WhatsApp · Planejamento Orçamentário · Workflow de aprovação · Conexão API · 2 GB backup",
        "confirmed": True,
    },
}

FEATURES = {
    "Controle de Estoque": {
        "Bling": 8, "Octalink": 5, "weight": 2.0,
        "bling_detail": "Multidepósito, leitor de código de barras, movimentações de estoque, baixa automática de insumos ao finalizar ordens de produção",
        "octa_detail": "Estoque básico no ERP Aurora — sem distinção entre matéria-prima e produto acabado para indústria"
    },
    "NF-e / NFC-e / NFS-e": {
        "Bling": 9, "Octalink": 6, "weight": 2.0,
        "bling_detail": "Emissão completa de NF-e, NFC-e e NFS-e em todos os planos. Integrado à SEFAZ.",
        "octa_detail": "NF-e disponível, mas profundidade da conformidade fiscal pouco documentada. Não é o foco principal da plataforma."
    },
    "SPED / Obrigações Fiscais": {
        "Bling": 7, "Octalink": 4, "weight": 1.5,
        "bling_detail": "SPED EFD expandindo para o plano Titânio a partir de abril/2026. Bloco K apenas parcial.",
        "octa_detail": "Automação de regras fiscais mencionada, mas Bloco K e SPED completo não estão documentados"
    },
    "Ordens de Produção / Ficha Técnica": {
        "Bling": 6, "Octalink": 0, "weight": 3.0,
        "bling_detail": "Ordens de produção + composição (ficha técnica) a partir do plano Mercúrio. Baixa automática de insumos. Pode gerar OP a partir de pedidos de venda.",
        "octa_detail": "⚠ CONFIRMADO: ZERO — nenhuma ordem de produção, nenhuma ficha técnica, nenhum MRP em qualquer parte da plataforma"
    },
    "Gestão Financeira": {
        "Bling": 7, "Octalink": 9, "weight": 1.5,
        "bling_detail": "Contas a pagar/receber, fluxo de caixa, DRE, conciliação bancária, Conta Digital com PIX/boleto",
        "octa_detail": "Camada de Controladoria com detecção de anomalias por IA, conciliação automatizada, planejamento orçamentário"
    },
    "RH / Folha de Pagamento": {
        "Bling": 0, "Octalink": 0, "weight": 2.0,
        "bling_detail": "❌ Nenhuma funcionalidade de RH. Exige stack separado: Convenia + Pontomais + escritório contábil.",
        "octa_detail": "❌ Nenhuma funcionalidade de RH. Mesma lacuna — sistema separado necessário independentemente da escolha."
    },
    "Relatórios / BI": {
        "Bling": 5, "Octalink": 8, "weight": 1.0,
        "bling_detail": "Add-on Meu Negócio com dashboards (Titânio+). Funcional, porém limitado comparado a ferramentas dedicadas de BI.",
        "octa_detail": "Integração com Power BI + squad dedicado de BI/Analytics no plano Scale"
    },
    "CRM / Pipeline Comercial": {
        "Bling": 3, "Octalink": 8, "weight": 0.5,
        "bling_detail": "Sem CRM nativo. Disponível por extensões (Agendor, Pipedrive, RD Station).",
        "octa_detail": "Gestão de pipeline de vendas nativa incluída em todos os planos"
    },
    "Recursos de IA": {
        "Bling": 2, "Octalink": 7, "weight": 0.5,
        "bling_detail": "Sem recursos de IA no produto principal. Apenas automações básicas.",
        "octa_detail": "Detecção de anomalias por IA, bot CFO no WhatsApp (Scale), previsão de fluxo de caixa assistida por IA"
    },
    "Facilidade de Implantação": {
        "Bling": 8, "Octalink": 4, "weight": 1.5,
        "bling_detail": "Teste gratuito de 30 dias, auto-atendimento. Central de ajuda extensa. Grande comunidade de usuários.",
        "octa_detail": "Implantação dedicada de 30 dias inclusa — mas sem teste self-service. Exige engajamento da equipe comercial."
    },
    "Qualidade do Suporte": {
        "Bling": 5, "Octalink": 5, "weight": 1.0,
        "bling_detail": "Certificação RA1000 no Reclame Aqui, mas suporte em queda desde a aquisição pela LWSA. Tempo de resposta pode chegar a 20 dias. Suporte Premium via WhatsApp custa R$150/mês extra.",
        "octa_detail": "Analista Sr. dedicado no plano Scale. Sem avaliações independentes para validar a qualidade."
    },
    "Solidez / Risco do Fornecedor": {
        "Bling": 9, "Octalink": 3, "weight": 1.5,
        "bling_detail": "Integrante da LWSA (B3: LWSA3). Receita de R$1,49B no FY2025. 300 mil+ clientes. Maior ERP para PME do Brasil.",
        "octa_detail": "Empresa bootstrapped. Estimativa de 15–40 colaboradores. Sem avaliações independentes. Todos os depoimentos no próprio site."
    },
    "Custo-Benefício": {
        "Bling": 9, "Octalink": 2, "weight": 2.0,
        "bling_detail": "R$55–650/mês. Teste gratuito de 30 dias. Sem taxa de implantação. Cancela quando quiser.",
        "octa_detail": "R$997–2.497/mês. Sem teste gratuito. Exige contato comercial. De 5,4× a 13,5× o valor de entrada do Bling."
    },
    "Integração com Marketplaces": {
        "Bling": 9, "Octalink": 1, "weight": 0.5,
        "bling_detail": "250+ integrações: Mercado Livre, Amazon, Shopee, Magalu, Shopify, Tray, WooCommerce…",
        "octa_detail": "Sem integrações com marketplaces. Plataforma não voltada para e-commerce."
    },
}

PROS_CONS = {
    "Bling": {
        "pros": [
            "Maior ERP para PME do Brasil — 300 mil+ clientes, 20 anos de mercado",
            "Módulo Pequena Indústria real: ordens de produção + ficha técnica a partir de R$110/mês",
            "NF-e/NFC-e/NFS-e completo + SPED expandindo para o Titânio em abril/2026",
            "Teste gratuito de 30 dias, sem taxa de setup, cancela quando quiser",
            "Ecossistema LWSA: Tray, Melhor Envio, Conta Digital, crédito embutido",
            "Capterra 4,7/5 (102 avaliações) · Reclame Aqui RA1000",
            "250+ integrações com marketplaces — referência no segmento",
            "Grande comunidade de usuários + central de ajuda completa",
        ],
        "cons": [
            "Instabilidade de sistema: 480 reclamações no Reclame Aqui em 6 meses",
            "Quedas recorrentes (especialmente às segundas), travamentos após atualizações, falha de banco em maio/2025",
            "Tempo de resposta do suporte chegando a 20 dias desde a aquisição pela LWSA",
            "Suporte Premium via WhatsApp custa R$150/mês extra (gratuito apenas no Diamante)",
            "Sem RH/folha de pagamento — necessário contratar sistema separado",
            "Sem MRP, sem roteiros de produção, sem controle de qualidade, sem chão de fábrica",
            "Custeio de produção é manual e básico — não é um motor de custeio industrial",
            "Reestruturação de planos em abril/2026 gera incerteza no curto prazo",
        ],
    },
    "Octalink": {
        "pros": [
            "Controladoria com IA: detecção de anomalias e alertas de fluxo de caixa",
            "CRM nativo de pipeline (Bling não tem sem extensão)",
            "Integração com Power BI para dashboards personalizados",
            "Bot CFO no WhatsApp: consulta pagamentos e confirma recebimentos via chat (Scale)",
            "Implantação de 30 dias com analista sênior dedicado (Scale)",
            "Conciliação bancária automatizada com categorização inteligente",
            "Promissor para empresas com maturidade financeira que precisam de controle rigoroso do backoffice",
        ],
        "cons": [
            "⚠ ZERO funcionalidades de produção industrial — sem OP, sem ficha técnica, sem MRP",
            "Zero avaliações independentes em qualquer plataforma (sem Capterra, G2, Reclame Aqui)",
            "Empresa bootstrapped, estimativa de 15–40 colaboradores — risco relevante de fornecedor",
            "Todas as referências de clientes são depoimentos no próprio site — não verificáveis",
            "R$997–2.497/mês sem teste gratuito — custo alto sem possibilidade de testar antes",
            "Funcionalidades dos planos Start e Growth não estão documentadas publicamente",
            "Sem integrações com marketplaces",
            "Sem RH/folha de pagamento — mesma lacuna do Bling",
        ],
    },
}

PAIN_POINTS = [
    {
        "pain": "Sem controle de estoque",
        "priority": "Crítico",
        "bling_score": 8,
        "octalink_score": 5,
        "bling_note": "Controle de estoque completo + multidepósito + código de barras + baixa automática de insumos nas ordens de produção",
        "octalink_note": "Estoque básico no ERP Aurora. Sem distinção entre matéria-prima e produto acabado.",
    },
    {
        "pain": "Sem RH / Folha / Ponto",
        "priority": "Crítico",
        "bling_score": 0,
        "octalink_score": 0,
        "bling_note": "Nenhuma funcionalidade de RH. Necessário: escritório contábil para folha + Convenia para gestão de RH + Pontomais para controle de ponto.",
        "octalink_note": "Nenhuma funcionalidade de RH. Mesma lacuna — exige exatamente o mesmo stack separado, independentemente da plataforma escolhida.",
    },
    {
        "pain": "Sem controle de produção",
        "priority": "Crítico",
        "bling_score": 6,
        "octalink_score": 0,
        "bling_note": "Ordens de produção + composição (ficha técnica) a partir do Mercúrio (R$110/mês). Baixa automática de insumos. Pode gerar OP a partir de pedidos de venda.",
        "octalink_note": "⚠ CONFIRMADO ZERO: sem ordens de produção, sem ficha técnica, sem MRP em nenhuma parte da plataforma.",
    },
    {
        "pain": "Sem emissão de NF-e / sistema fiscal",
        "priority": "Alto",
        "bling_score": 9,
        "octalink_score": 6,
        "bling_note": "Melhor da categoria em NF-e/NFC-e/NFS-e em todos os planos. SPED EFD expande para o Titânio em abril/2026. Integrado à SEFAZ.",
        "octalink_note": "NF-e disponível. Automação de regras fiscais mencionada. Profundidade do Bloco K e SPED completo não confirmados.",
    },
    {
        "pain": "Sem relatórios / dados estruturados",
        "priority": "Médio",
        "bling_score": 5,
        "octalink_score": 8,
        "bling_note": "Add-on Meu Negócio com dashboards no Titânio+. Funcional, porém limitado frente a ferramentas dedicadas de BI.",
        "octalink_note": "Integração com Power BI + squad dedicado de BI/Analytics. Octalink genuinamente superior neste quesito.",
    },
    {
        "pain": "Conformidade fiscal brasileira (SPED, Bloco K, Reforma)",
        "priority": "Alto",
        "bling_score": 6,
        "octalink_score": 4,
        "bling_note": "SPED ICMS/IPI expandindo para o Titânio. Bloco K parcial (obrigatório completo para grandes indústrias desde jan/2025). Roadmap da Reforma Tributária a verificar.",
        "octalink_note": "Profundidade da conformidade fiscal incerta. Roadmap de IBS/CBS da Reforma Tributária não documentado publicamente. Requer esclarecimento no evento.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# PONTUAÇÕES CALCULADAS
# ─────────────────────────────────────────────────────────────────────────────
def weighted_score(platform):
    total_w = sum(v["weight"] for v in FEATURES.values())
    total_s = sum(v[platform] * v["weight"] for v in FEATURES.values())
    return round((total_s / (total_w * 10)) * 100)

BLING_SCORE    = weighted_score("Bling")
OCTALINK_SCORE = weighted_score("Octalink")

# ─────────────────────────────────────────────────────────────────────────────
# TEMA — Fundo branco, navy + dourado
# ─────────────────────────────────────────────────────────────────────────────
NAVY   = "#0d2340"
GOLD   = "#c9a040"
GOLD_L = "#e8b84b"
BLUE   = "#1a4a8a"
BLUE_L = "#2563b0"
RED    = "#b03030"
RED_L  = "#dc4040"
GREEN  = "#1a6640"
MUTED  = "#5a6a80"
LIGHT  = "#8090a8"
BG     = "#ffffff"
BG2    = "#f4f6f9"
BG3    = "#eaf0f8"
BORDER = "#d0dae8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {{ font-family: 'Sora', sans-serif; }}
.stApp {{ background: {BG}; }}
[data-testid="stSidebar"] {{
    background: {NAVY} !important;
    border-right: 1px solid #1a3a5c;
}}
[data-testid="stSidebar"] * {{ color: #c8d8e8 !important; }}
[data-testid="stSidebar"] .stRadio label {{ color: #c8d8e8 !important; }}
[data-testid="stSidebar"] hr {{ border-color: #1a3a5c !important; }}
h1 {{ color: {NAVY} !important; font-size: 1.9rem !important; font-weight: 700 !important; }}
h2 {{ color: {NAVY} !important; font-size: 1.4rem !important; font-weight: 600 !important; }}
h3 {{ color: {NAVY} !important; font-size: 1.15rem !important; font-weight: 600 !important; }}
h4 {{ color: {NAVY} !important; font-weight: 600 !important; }}
p, li {{ color: #2a3a4a !important; }}
[data-testid="metric-container"] {{
    background: {BG2};
    border: 1px solid {BORDER};
    border-top: 3px solid {GOLD};
    border-radius: 8px;
    padding: 14px;
}}
[data-testid="stMetricValue"] {{ color: {NAVY} !important; font-size: 1.6rem !important; font-weight: 700 !important; }}
[data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-size: 0.78rem !important; }}
[data-testid="stMetricDelta"] {{ color: {BLUE_L} !important; }}
[data-testid="stTabs"] button {{
    color: {MUTED} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    background: transparent !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {NAVY} !important;
    border-bottom: 2px solid {GOLD} !important;
}}
hr {{ border-color: {BORDER} !important; }}
.stAlert {{ border-radius: 6px !important; }}
[data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    background: {BG2} !important;
}}
</style>
""", unsafe_allow_html=True)

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=BG2,
    font=dict(family="Sora, sans-serif", color="#2a3a4a"),
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='color:{GOLD_L};font-size:1.1rem;font-weight:700;margin-bottom:4px'>⚙️ Comparativo ERP</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#a8c8e8;font-weight:600;font-size:0.9rem'>Bling vs Octalink</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6a8ab0;font-size:0.8rem;margin-top:2px'>Pequena Indústria · Brasil</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navegar", [
        "📊  Visão Geral",
        "🔬  Análise de Recursos",
        "💰  Preços",
        "🏭  Aderência à Fábrica",
        "📣  Prós e Contras",
        "🏢  Perfil das Empresas",
    ])
    st.divider()
    st.markdown(f"<div style='color:{GOLD_L};font-size:0.78rem;font-weight:700'>Status dos dados</div>", unsafe_allow_html=True)
    st.markdown("✅ Bling — verificado mar/2026")
    st.markdown("🟡 Octalink — ⚠ preços a confirmar")
    st.markdown(f"📅 Atualizar após: **evento 9/3**")
    st.divider()
    st.caption("Albuquerque Consulting · Março 2026")

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: VISÃO GERAL
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Visão Geral":
    st.markdown(f"""
    <div style="background:{NAVY};padding:28px 32px;border-radius:10px;margin-bottom:24px">
        <div style="color:{GOLD_L};font-size:0.75rem;font-weight:700;letter-spacing:1.5px;margin-bottom:8px">COMPARATIVO ERP · MARÇO 2026</div>
        <div style="color:white;font-size:1.75rem;font-weight:700;line-height:1.2">Bling vs Octalink</div>
        <div style="color:#8ab0d0;font-size:0.9rem;margin-top:6px">Pequena indústria de manufatura · Brasil · Digitalização completa do zero</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#fff4f4;border:1px solid {RED_L};border-left:5px solid {RED_L};
                padding:16px 22px;border-radius:6px;margin-bottom:24px">
        <span style="color:{RED};font-weight:700;font-size:13px">⚠ DESCOBERTA CRÍTICA DA PESQUISA</span><br/>
        <span style="color:#4a2020;font-size:13px;line-height:1.7">
        O Octalink <b>não possui nenhum recurso de produção industrial</b> — zero ordens de produção, 
        zero ficha técnica, zero rastreamento de insumos. É uma <b>plataforma de backoffice financeiro</b>, 
        não um ERP industrial. Além disso, <b>nenhuma das duas plataformas inclui RH ou folha de pagamento</b> — 
        um sistema separado será necessário independentemente da escolha.
        </span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=BLING_SCORE,
            title={"text": "Bling · Aderência à Fábrica", "font": {"color": NAVY, "size": 13}},
            number={"suffix": "/100", "font": {"color": BLUE, "size": 38}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": BORDER},
                "bar": {"color": BLUE},
                "bgcolor": BG2, "bordercolor": BORDER,
                "steps": [
                    {"range": [0, 40],  "color": "#fce8e8"},
                    {"range": [40, 70], "color": "#fdf5e0"},
                    {"range": [70, 100],"color": "#e8f4ee"},
                ],
                "threshold": {"line": {"color": GOLD, "width": 2}, "thickness": 0.75, "value": 70},
            },
        ))
        fig.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=OCTALINK_SCORE,
            title={"text": "Octalink · Aderência à Fábrica", "font": {"color": NAVY, "size": 13}},
            number={"suffix": "/100", "font": {"color": RED, "size": 38}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": BORDER},
                "bar": {"color": RED},
                "bgcolor": BG2, "bordercolor": BORDER,
                "steps": [
                    {"range": [0, 40],  "color": "#fce8e8"},
                    {"range": [40, 70], "color": "#fdf5e0"},
                    {"range": [70, 100],"color": "#e8f4ee"},
                ],
            },
        ))
        fig2.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        st.metric("Diferença de Pontuação", f"Bling +{BLING_SCORE - OCTALINK_SCORE} pts", "Em 14 critérios ponderados")
        st.metric("Plano Mínimo Viável — Bling", "R$185/mês", "Titânio — produção + SPED inclusos")
        st.metric("Entrada Octalink (Start)", "R$1.597/mês", f"{round(1597/185,1)}× o Bling Titânio recomendado")
        st.metric("RH / Folha de Pagamento", "❌ Nenhum", "Sistema separado necessário nos dois casos")

    st.divider()

    cb, co = st.columns(2)
    with cb:
        st.markdown(f"""
        <div style="background:{BG2};border:1px solid {BORDER};border-top:4px solid {BLUE};padding:22px;border-radius:8px">
          <div style="color:{NAVY};font-weight:700;font-size:1.1rem">Bling</div>
          <div style="color:{LIGHT};font-size:0.75rem;margin-bottom:12px">bling.com.br · Grupo LWSA (B3: LWSA3)</div>
          <div style="color:#2a3a4a;font-size:0.85rem;line-height:1.9">
            Maior ERP para PME do Brasil. Mais de 300 mil clientes. No mercado desde 2005.<br/>
            Adquirido pela LWSA por <b style="color:{GOLD}">R$524 milhões</b> em 2021.<br/>
            Segmento Commerce: <b style="color:{BLUE}">R$1,07B</b> de receita no FY2025.<br/>
            Possui módulo <b>Pequena Indústria</b> com ordens de produção e ficha técnica.<br/>
            Capterra <b>4,7/5</b> · Reclame Aqui <b>RA1000</b> · Teste gratuito de 30 dias.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with co:
        st.markdown(f"""
        <div style="background:{BG2};border:1px solid {BORDER};border-top:4px solid {GOLD};padding:22px;border-radius:8px">
          <div style="color:{NAVY};font-weight:700;font-size:1.1rem">Octalink</div>
          <div style="color:{LIGHT};font-size:0.75rem;margin-bottom:12px">octalink.com.br · Octalink Tecnologia LTDA · Sumaré, SP</div>
          <div style="color:#2a3a4a;font-size:0.85rem;line-height:1.9">
            Plataforma de backoffice financeiro: ERP Aurora + CRM + Controladoria + BI + IA.<br/>
            Fundada em dez/2017 por Daniel e Fernando Stavale.<br/>
            <b>Bootstrapped</b>, estimativa de <b>15–40 colaboradores</b>. Sem investimento externo.<br/>
            <b style="color:{RED}">Zero avaliações independentes</b> — sem Capterra, G2, Reclame Aqui.<br/>
            <b style="color:{RED}">Nenhum recurso de produção confirmado.</b> Foco em empresas com receita acima de R$4M/ano. Planos: R$1.597 (Start) · R$3.797 (Pro) · R$7.897 (Growth)/mês.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: ANÁLISE DE RECURSOS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔬  Análise de Recursos":
    st.title("Análise de Recursos")
    st.markdown(f"<p style='color:{MUTED}'>14 critérios pontuados de 0 a 10, com peso por relevância para a fábrica</p>", unsafe_allow_html=True)
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Radar", "Comparativo em Barras", "Tabela Detalhada"])

    features = list(FEATURES.keys())
    bling_scores    = [FEATURES[f]["Bling"]    for f in features]
    octalink_scores = [FEATURES[f]["Octalink"] for f in features]

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=bling_scores + [bling_scores[0]],
            theta=features + [features[0]],
            fill="toself", name="Bling",
            line_color=BLUE, fillcolor="rgba(26,74,138,0.15)",
        ))
        fig.add_trace(go.Scatterpolar(
            r=octalink_scores + [octalink_scores[0]],
            theta=features + [features[0]],
            fill="toself", name="Octalink",
            line_color=GOLD, fillcolor="rgba(201,160,64,0.12)",
        ))
        fig.update_layout(
            **LAYOUT,
            polar=dict(
                bgcolor=BG2,
                radialaxis=dict(visible=True, range=[0, 10], color=MUTED,
                                gridcolor=BORDER, tickfont=dict(size=9)),
                angularaxis=dict(color=MUTED, gridcolor=BORDER, tickfont=dict(size=10)),
            ),
            showlegend=True,
            legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"),
            height=560, margin=dict(t=20, b=20, l=40, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame({
            "Recurso": features,
            "Bling": bling_scores,
            "Octalink": octalink_scores,
            "Peso": [FEATURES[f]["weight"] for f in features],
        }).sort_values("Peso", ascending=False)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Bling", y=df["Recurso"], x=df["Bling"],
            orientation="h", marker_color=BLUE,
            hovertemplate="<b>Bling</b> %{y}: %{x}/10<extra></extra>",
        ))
        fig2.add_trace(go.Bar(
            name="Octalink", y=df["Recurso"], x=df["Octalink"],
            orientation="h", marker_color=GOLD,
            hovertemplate="<b>Octalink</b> %{y}: %{x}/10<extra></extra>",
        ))
        fig2.update_layout(
            **LAYOUT, barmode="group", height=540,
            xaxis=dict(range=[0, 10], gridcolor=BORDER, tickfont=dict(color=MUTED)),
            yaxis=dict(tickfont=dict(color=NAVY, size=11)),
            legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown(f"<p style='color:{MUTED}'>Expanda cada linha para ver as notas detalhadas por plataforma.</p>", unsafe_allow_html=True)
        for fname, fdata in sorted(FEATURES.items(), key=lambda x: -x[1]["weight"]):
            b = fdata["Bling"]
            o = fdata["Octalink"]
            w = fdata["weight"]
            b_bar = "🟦" * b + "⬜" * (10 - b)
            o_bar = "🟨" * o + "⬜" * (10 - o)
            with st.expander(f"**{fname}** — Bling: {b}/10   Octalink: {o}/10   peso: {w}×"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Bling** {b_bar}")
                    st.caption(fdata["bling_detail"])
                with c2:
                    st.markdown(f"**Octalink** {o_bar}")
                    st.caption(fdata["octa_detail"])

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: PREÇOS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💰  Preços":
    st.title("Comparativo de Preços")
    st.divider()

    tab1, tab2 = st.tabs(["Planos Bling", "Planos Octalink"])

    with tab1:
        st.markdown("#### Bling — Planos Vigentes (Março 2026)")
        st.info("📅 **Mudança em abril/2026:** O Mercúrio será incorporado ao Titânio (nova Faixa 1). SPED fiscal passa a valer para o Titânio. Cobrança anual = 2 meses grátis (paga 10, ganha 12).")

        for name, p in BLING_PLANS.items():
            is_rec = "★" in name
            border = GOLD if is_rec else BORDER
            bg     = "#fffbf0" if is_rec else BG2
            tag_prod = "✅ Produção" if p["production"] else "❌ Sem produção"
            tag_sped = "✅ SPED"     if p["sped"]       else "❌ Sem SPED"
            tag_pdv  = "✅ PDV"      if p["pdv"]        else "❌ Sem PDV"
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-left:4px solid {border};
                        padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="color:{NAVY};font-weight:700;font-size:1rem">{name}</span>
                <span style="color:{GOLD};font-weight:700;font-size:1.1rem">R${p['price_monthly']}/mês</span>
              </div>
              <div style="color:{LIGHT};font-size:0.75rem;margin:4px 0 8px 0">
                Anual: R${p['price_annual']}/mês · {p['users']} usuários · {p['dados']} dados · {p['arquivos']} arquivos · {p['mkt_imports']} importações
              </div>
              <div style="font-size:0.8rem;color:{MUTED}">
                <span style="margin-right:12px">{tag_prod}</span>
                <span style="margin-right:12px">{tag_sped}</span>
                <span style="margin-right:12px">{tag_pdv}</span>
              </div>
              <div style="color:{LIGHT};font-size:0.75rem;margin-top:6px">{p['note']}</div>
            </div>
            """, unsafe_allow_html=True)

        names  = list(BLING_PLANS.keys())
        prices = [v["price_monthly"] for v in BLING_PLANS.values()]
        colors_bar = [GOLD if "★" in n else BLUE for n in names]
        fig = go.Figure(go.Bar(x=names, y=prices, marker_color=colors_bar,
                               hovertemplate="%{x}: R$%{y}/mês<extra></extra>"))
        fig.update_layout(**LAYOUT, height=280, showlegend=False,
                          yaxis=dict(title="R$/mês", gridcolor=BORDER, tickfont=dict(color=MUTED)),
                          xaxis=dict(tickfont=dict(color=NAVY)),
                          margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Octalink — Planos (⚠ Parcialmente Não Confirmados)")
        st.warning("⚠ Detalhes dos planos Start e Growth foram obtidos via conjunta.org (terceiro). Preços e funcionalidades precisam ser validados no **showcase de 9 de março**. Plano Scale verificado a partir do blog oficial.")

        for name, p in OCTALINK_PLANS.items():
            confirmed = p.get("confirmed", False)
            border_c  = BLUE if confirmed else "#e8834a"
            bg_c      = BG2  if confirmed else "#fff8f0"
            conf_label = "✅ Verificado" if confirmed else "⚠ Não confirmado"
            st.markdown(f"""
            <div style="background:{bg_c};border:1px solid {border_c};border-left:4px solid {border_c};
                        padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="color:{NAVY};font-weight:700;font-size:1rem">{name}</span>
                <span style="color:{GOLD};font-weight:700;font-size:1.1rem">R${p['price_monthly']:,}/mês</span>
              </div>
              <div style="color:{LIGHT};font-size:0.75rem;margin:4px 0 8px 0">
                {p['users']} · {p['storage']} · {conf_label}
              </div>
              <div style="color:{MUTED};font-size:0.8rem">{p['note']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Comparativo de Preços — Bling Titânio vs Entrada Octalink")
        comp_names  = ["Bling Cobalto", "Bling Mercúrio", "Bling Titânio ★",
                       "Bling Platina", "Bling Diamante",
                       "Octalink Start", "Octalink Pro ★", "Octalink Growth"]
        comp_prices = [55, 110, 185, 450, 650, 1597, 3797, 7897]
        comp_colors = [BLUE] * 5 + [GOLD] * 3
        fig2 = go.Figure(go.Bar(
            x=comp_names, y=comp_prices, marker_color=comp_colors,
            hovertemplate="%{x}: R$%{y}/mês<extra></extra>",
        ))
        fig2.update_layout(**LAYOUT, height=340, showlegend=False,
                           yaxis=dict(title="R$/mês", gridcolor=BORDER, tickfont=dict(color=MUTED)),
                           xaxis=dict(tickangle=-30, tickfont=dict(color=NAVY, size=10)),
                           margin=dict(t=20, b=80))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: ADERÊNCIA À FÁBRICA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏭  Aderência à Fábrica":
    st.title("Aderência à Fábrica — Análise por Dor")
    st.markdown(f"<p style='color:{MUTED}'>Pontuação de cada plataforma frente às dores específicas do cliente</p>", unsafe_allow_html=True)
    st.divider()

    priority_colors = {"Crítico": RED, "Alto": GOLD, "Médio": BLUE_L}

    for pp in PAIN_POINTS:
        b = pp["bling_score"]
        o = pp["octalink_score"]

        with st.expander(f"**{pp['pain']}** — Prioridade: {pp['priority']}   |   Bling: {b}/10   Octalink: {o}/10"):
            c1, c2 = st.columns(2)
            with c1:
                pct_b     = b * 10
                bar_col_b = BLUE if b > 0 else RED
                st.markdown(f"""
                <div style="background:{BG2};border:1px solid {BORDER};padding:14px;border-radius:6px">
                  <div style="color:{NAVY};font-weight:700;margin-bottom:8px">Bling — {b}/10</div>
                  <div style="background:{BORDER};border-radius:4px;height:8px;margin-bottom:10px">
                    <div style="background:{bar_col_b};width:{pct_b}%;height:8px;border-radius:4px"></div>
                  </div>
                  <div style="color:{MUTED};font-size:0.8rem;line-height:1.6">{pp['bling_note']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                pct_o     = o * 10
                bar_col_o = GOLD if o > 0 else RED
                st.markdown(f"""
                <div style="background:{BG2};border:1px solid {BORDER};padding:14px;border-radius:6px">
                  <div style="color:{NAVY};font-weight:700;margin-bottom:8px">Octalink — {o}/10</div>
                  <div style="background:{BORDER};border-radius:4px;height:8px;margin-bottom:10px">
                    <div style="background:{bar_col_o};width:{pct_o}%;height:8px;border-radius:4px"></div>
                  </div>
                  <div style="color:{MUTED};font-size:0.8rem;line-height:1.6">{pp['octalink_note']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Pontuação por Dor — Lado a Lado")
    pain_names  = [pp["pain"] for pp in PAIN_POINTS]
    bling_pp    = [pp["bling_score"]    for pp in PAIN_POINTS]
    octalink_pp = [pp["octalink_score"] for pp in PAIN_POINTS]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Bling",    x=pain_names, y=bling_pp,    marker_color=BLUE,
                         hovertemplate="Bling · %{x}: %{y}/10<extra></extra>"))
    fig.add_trace(go.Bar(name="Octalink", x=pain_names, y=octalink_pp, marker_color=GOLD,
                         hovertemplate="Octalink · %{x}: %{y}/10<extra></extra>"))
    fig.update_layout(**LAYOUT, barmode="group", height=340,
                      yaxis=dict(range=[0, 10], gridcolor=BORDER, title="Pontuação /10",
                                 tickfont=dict(color=MUTED)),
                      xaxis=dict(tickangle=-20, tickfont=dict(size=10, color=NAVY)),
                      legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"),
                      margin=dict(t=20, b=80, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: PRÓS E CONTRAS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📣  Prós e Contras":
    st.title("Prós e Contras")
    st.divider()

    cb, co = st.columns(2)

    with cb:
        st.markdown(f"<h3 style='color:{NAVY}'>🟦 Bling</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{GREEN};font-weight:600;font-size:0.9rem;margin-bottom:8px'>✅ Pontos Fortes</div>", unsafe_allow_html=True)
        for pro in PROS_CONS["Bling"]["pros"]:
            st.markdown(f"<div style='color:#1a3a1a;font-size:0.85rem;padding:6px 0;border-bottom:1px solid {BG3}'>✅ {pro}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{RED};font-weight:600;font-size:0.9rem;margin-bottom:8px'>⚠ Pontos de Atenção</div>", unsafe_allow_html=True)
        for con in PROS_CONS["Bling"]["cons"]:
            st.markdown(f"<div style='color:#3a1a1a;font-size:0.85rem;padding:6px 0;border-bottom:1px solid {BG3}'>⚠ {con}</div>", unsafe_allow_html=True)

    with co:
        st.markdown(f"<h3 style='color:{NAVY}'>🟨 Octalink</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{GREEN};font-weight:600;font-size:0.9rem;margin-bottom:8px'>✅ Pontos Fortes</div>", unsafe_allow_html=True)
        for pro in PROS_CONS["Octalink"]["pros"]:
            st.markdown(f"<div style='color:#1a3a1a;font-size:0.85rem;padding:6px 0;border-bottom:1px solid {BG3}'>✅ {pro}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:{RED};font-weight:600;font-size:0.9rem;margin-bottom:8px'>⚠ Pontos de Atenção</div>", unsafe_allow_html=True)
        for con in PROS_CONS["Octalink"]["cons"]:
            st.markdown(f"<div style='color:#3a1a1a;font-size:0.85rem;padding:6px 0;border-bottom:1px solid {BG3}'>⚠ {con}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: PERFIL DAS EMPRESAS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🏢  Perfil das Empresas":
    st.title("Perfil das Empresas")
    st.divider()

    tab1, tab2 = st.tabs(["Bling / LWSA", "Octalink"])

    with tab1:
        st.markdown(f"<h3 style='color:{NAVY}'>Bling · Grupo LWSA</h3>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fundação", "2005")
        c2.metric("Aquisição", "R$524,3M", "LWSA, junho/2021")
        c3.metric("Receita LWSA FY2025", "R$1,49B", "+10,3% ao ano")
        c4.metric("Segmento Commerce", "R$1,07B", "+15,3% ao ano (Bling + Tray + outros)")

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Assinantes (Plataformas)", "206.300", "+6,8% ao ano (todas as plataformas LWSA)")
        c2.metric("Capterra", "4,7 / 5", "102 avaliações")
        c3.metric("Reclame Aqui", "RA1000", "8,6/10 · 90,9% resolvidos")
        c4.metric("Reclamações RA (6 meses)", "480", "Set/2025–Fev/2026")

        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Ecossistema LWSA — Integrações do Bling</h4>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:{BG2};border:1px solid {BORDER};padding:18px 22px;border-radius:8px;
                    font-size:0.85rem;color:#2a3a4a;line-height:1.9">
        O Bling está inserido em um ecossistema de comércio com integração nativa:<br/>
        • <b>Tray</b> — lojas virtuais (empresa irmã dentro da LWSA)<br/>
        • <b>Melhor Envio</b> — logística de frete com tarifas competitivas (LWSA)<br/>
        • <b>Vindi</b> — processamento de pagamentos<br/>
        • <b>Conta Digital</b> — PIX, boleto e linhas de crédito rotativo baseadas no volume de NFs emitidas<br/>
        • <b>250+ conectores de marketplace</b> — Mercado Livre, Amazon, Shopee, Magalu, Americanas, Shopify, WooCommerce…
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Principais Categorias de Reclamação no Reclame Aqui</h4>", unsafe_allow_html=True)
        complaint_cats = [
            "Instabilidade / quedas",
            "Demora no atendimento",
            "Travamentos pós-update",
            "Reajuste abr/2025",
            "Falhas marketplace",
            "Limitações de escala",
        ]
        complaint_vol = [34, 24, 18, 12, 8, 4]
        fig = go.Figure(go.Bar(
            x=complaint_cats, y=complaint_vol, marker_color=RED,
            hovertemplate="%{x}: ~%{y}% das reclamações<extra></extra>",
        ))
        fig.update_layout(
            **LAYOUT, height=290, showlegend=False,
            yaxis=dict(title="% das reclamações", gridcolor=BORDER, tickfont=dict(color=MUTED)),
            xaxis=dict(tickangle=-20, tickfont=dict(size=10, color=NAVY)),
            margin=dict(t=10, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown(f"<h3 style='color:{NAVY}'>Octalink · Octalink Tecnologia LTDA</h3>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fundação", "Dez/2017", "Sumaré, SP")
        c2.metric("Investimento externo", "R$0", "Bootstrapped — sem captação")
        c3.metric("Tamanho estimado", "15–40 func.", "Glassdoor + ZoomInfo")
        c4.metric("Avaliações independentes", "ZERO", "Sem Capterra, G2, Reclame Aqui")

        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Fundadores</h4>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:{BG2};border:1px solid {BORDER};padding:14px 18px;border-radius:6px;
                    font-size:0.85rem;color:#2a3a4a">
        • <b>Daniel Stavale</b> — CEO<br/>
        • <b>Fernando Stavale</b> — CDO / Co-fundador<br/>
        • Sumaré, SP (Região Metropolitana de Campinas)
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Arquitetura da Plataforma</h4>", unsafe_allow_html=True)
        cols = st.columns(4)
        modules = [
            ("ERP Aurora",           BLUE,    "ERP proprietário — estoque, NF-e, gestão financeira. Sem funcionalidades de produção industrial."),
            ("CRM",                  GOLD,    "Gestão de pipeline de vendas nativa. Disponível em todos os planos."),
            ("Controladoria + IA",   NAVY,    "Detecção de anomalias por IA, conciliação automatizada, planejamento orçamentário, aprovações por fluxo."),
            ("BI / Analytics",       "#b05a20","Integração com Power BI + squad dedicado de Analytics no plano Scale."),
        ]
        for col, (mod, col_hex, desc) in zip(cols, modules):
            with col:
                st.markdown(f"""
                <div style="background:{BG2};border:1px solid {BORDER};border-top:3px solid {col_hex};
                            padding:14px;border-radius:6px;text-align:center">
                  <div style="color:{col_hex};font-weight:700;font-size:0.85rem;margin-bottom:6px">{mod}</div>
                  <div style="color:{MUTED};font-size:0.78rem;line-height:1.5">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Integrações Conhecidas</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{MUTED};font-size:0.85rem'>SOC (medicina do trabalho) · Power BI · WhatsApp Business API · PIX/boleto bancário · NF-e SEFAZ</p>", unsafe_allow_html=True)

        st.divider()
        st.warning("""
        **⚠ Validação necessária no evento de 9/3:**
        - Preços e funcionalidades dos planos Start e Growth
        - Existência de algum recurso de produção/manufatura
        - Prazo e processo detalhado de implantação
        - Referências nominais de clientes além dos depoimentos do site
        - Profundidade da conformidade com Bloco K / SPED
        - Roadmap para Reforma Tributária (IBS/CBS)
        """)
