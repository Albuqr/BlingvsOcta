import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Bling vs Octalink · Comparativo ERP",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLING_PLANS = {
    "Cobalto": {"price_monthly": 55, "price_annual": 45.83, "users": 5, "dados": "60 MB", "arquivos": "1,5 GB", "mkt_imports": "200/mês", "production": False, "sped": False, "pdv": False, "note": "Plano de entrada. Estoque, vendas multicanal, contas a pagar/receber, Conta Digital PJ. Sem ordens de produção, sem SPED."},
    "Mercúrio": {"price_monthly": 110, "price_annual": 91.66, "users": 10, "dados": "120 MB", "arquivos": "3 GB", "mkt_imports": "500/mês", "production": True, "sped": False, "pdv": True, "note": "Tudo do Cobalto + ordens de produção + ficha técnica + gestão financeira completa + PDV. Sem SPED."},
    "Titânio ★": {"price_monthly": 185, "price_annual": 154.00, "users": 15, "dados": "360 MB", "arquivos": "9 GB", "mkt_imports": "2.000/mês", "production": True, "sped": True, "pdv": True, "note": "RECOMENDADO — Tudo do Mercúrio + SPED fiscal (abr/2026) + etiqueta logística + dashboards Meu Negócio + integração POS."},
    "Platina": {"price_monthly": 450, "price_annual": 375.00, "users": 50, "dados": "1,2 GB", "arquivos": "30 GB", "mkt_imports": "5.000/mês", "production": True, "sped": True, "pdv": True, "note": "Tudo do Titânio + dashboards com até 5 contas Bling + 3 maquininhas POS."},
    "Diamante": {"price_monthly": 650, "price_annual": 541.00, "users": 80, "dados": "1,8 GB", "arquivos": "45 GB", "mkt_imports": "Ilimitado", "production": True, "sped": True, "pdv": True, "note": "Tudo do Platina + dashboards até 10 contas + Suporte Premium incluso."},
}

OCTALINK_PLANS = {
    "Start": {"price_monthly": 1597, "users": "5 licenças Aurora ERP/CRM", "note": "5 licenças Aurora ERP/CRM · 200 docs fiscais/mês · 1 Analista Jr. · 500 MB backup · NF-e/NFS-e/CT-e · Almoxarifado + estoque · Open Finance · DRE + fluxo de caixa"},
    "Pro ★": {"price_monthly": 3797, "users": "10 licenças ERP/CRM", "note": "MELHOR OPÇÃO — 10 licenças ERP/CRM · 400 docs fiscais/mês · 1 CFO WhatsApp · Budget + Forecast · Workflow de aprovação · API · 1 GB backup"},
    "Growth": {"price_monthly": 7897, "users": "20 licenças ERP/CRM", "note": "20 licenças ERP/CRM · 800 docs fiscais/mês · 1 Analista Sr. + 1 CFO WhatsApp · Budget + Forecast · Workflow · API · 2 GB backup"},
}

OCTALINK_INDUSTRY = {
    "Almoxarifado e estoque": "Controle físico e financeiro. Posição de estoque por quantidade e valor. Custo médio calculado automaticamente a cada operação.",
    "Ordens de produção (OP)": "OP com árvore de produto (BOM). Baixa automática de insumos. Mostra disponibilidade por almoxarifado em tempo real antes de iniciar a produção.",
    "QR Code e localização": "QR Code por item e por endereçamento (estante, nível, altura, sala). Workflow: separação → qualidade → estoque. Transferência entre almoxarifados.",
    "Monitoramento de NF-e": "Varredura automática na SEFAZ para NFs emitidas contra o CNPJ do cliente. Lançamento sempre manual — usuário no controle.",
    "Fator de conversão de unidades": "Normalização kg/unidade/caixa. Fornecedores com unidades diferentes são normalizados automaticamente após configuração inicial.",
    "Importação internacional": "Moeda estrangeira, taxa de câmbio, Incoterms, AWB, II, IPI, PIS/COFINS, seguro, frete. Upload XML com centenas de itens de uma vez.",
    "Rastreabilidade de lotes": "Data de validade, data do lote, código APC. Rastreabilidade completa do lote ao longo da cadeia de produção.",
    "De-para de fornecedor": "Mapeamento de código do fornecedor para código interno. Feito uma vez — automático em todas as NFs futuras daquele fornecedor.",
}

FEATURES = {
    "Controle de Estoque":          {"Bling": 8, "Octalink": 7, "weight": 2.0, "bling_detail": "Multidepósito, código de barras, movimentações, baixa automática de insumos em OPs.", "octa_detail": "Almoxarifado completo: custo médio automático, QR Code por item e endereço, fator de conversão, lotes, monitoramento de NF-e na SEFAZ. Confirmado in-person."},
    "NF-e / NFS-e / CT-e":          {"Bling": 9, "Octalink": 8, "weight": 2.0, "bling_detail": "NF-e, NFC-e, NFS-e em todos os planos. Integrado à SEFAZ.", "octa_detail": "NF-e (tipo 55), CT-e (tipo 57), NFS-e confirmados. Regras fiscais automáticas: CST, CFOP por estado, retenções de ISS/PIS/COFINS. Comunicação SEFAZ + prefeitura."},
    "SPED / Obrigações Fiscais":     {"Bling": 7, "Octalink": 7, "weight": 1.5, "bling_detail": "SPED EFD expandindo para Titânio em abr/2026. Bloco K parcial.", "octa_detail": "Regras fiscais por operação (NCM, CFOP, CST, grupo de tributação). IBS/CBS já implementado para Reforma 2027. Bloco K não confirmado explicitamente."},
    "Ordens de Produção / BOM":      {"Bling": 6, "Octalink": 6, "weight": 3.0, "bling_detail": "OP + ficha técnica (BOM) a partir do Mercúrio. Baixa automática de insumos. OP a partir de pedido de venda.", "octa_detail": "OP com BOM confirmada in-person. Baixa automática com verificação de estoque por almoxarifado. Módulo secundário (8% da base de clientes são indústria)."},
    "Gestão Financeira / DRE":       {"Bling": 7, "Octalink": 9, "weight": 1.5, "bling_detail": "Contas a pagar/receber, fluxo de caixa, DRE, conciliação bancária, Conta Digital PIX/boleto.", "octa_detail": "Fluxo de caixa tripartite (operacional/financeiro/investimento). DRE com drilldown até documento original. Budget vs real. Fechamento no 1º dia útil. Centros de custo e BU."},
    "Controladoria / BI":            {"Bling": 4, "Octalink": 9, "weight": 1.0, "bling_detail": "Add-on Meu Negócio com dashboards básicos no Titânio+.", "octa_detail": "Produto mais maduro (desde 2015). Dashboards por nível de gestão, drilldown big number → DARF, budget vs real, data lake proprietário + Lovable para dashboards customizados."},
    "RH / Folha de Pagamento":       {"Bling": 0, "Octalink": 0, "weight": 2.0, "bling_detail": "❌ Zero. Stack separado: escritório contábil + Convenia + Pontomais.", "octa_detail": "❌ Apenas rateio e contabilização da folha — cálculo externo. Na prática: mesma lacuna do Bling."},
    "CRM / Pipeline Comercial":      {"Bling": 3, "Octalink": 8, "weight": 0.5, "bling_detail": "Sem CRM nativo. Disponível por extensões (Agendor, Pipedrive, RD Station).", "octa_detail": "CRM nativo completo: pipeline, origem de leads por canal, dashboards de conversão, agentes de IA no WhatsApp, URLs curtas para ativações."},
    "Recursos de IA":                {"Bling": 2, "Octalink": 8, "weight": 0.5, "bling_detail": "Sem IA no produto principal. Automações básicas apenas.", "octa_detail": "IA para criação de regras contábeis (beta mar/2026). Bot CFO WhatsApp. Parametrização automática de plano de contas. Data lake + Lovable. Cursor internamente."},
    "Conciliação Bancária":          {"Bling": 7, "Octalink": 9, "weight": 1.0, "bling_detail": "Conciliação via OFX. Conta Digital Bling com PIX/boleto.", "octa_detail": "Open Finance via API regulamentada pelo Banco Central (não screen-scraping). Itaú Empresas confirmado. Contabilização automática de baixa de passivos/ativos."},
    "Facilidade de Implantação":     {"Bling": 8, "Octalink": 4, "weight": 1.5, "bling_detail": "Trial 30 dias, auto-atendimento, central de ajuda extensa, grande comunidade.", "octa_detail": "Setup médio 90 dias. Exige contador engajado (80-90% do tempo é em regras contábeis). IA para setup em beta (abr/2026). Sem trial, sem auto-atendimento."},
    "Qualidade do Suporte":          {"Bling": 5, "Octalink": 5, "weight": 1.0, "bling_detail": "RA1000, mas suporte em queda pós-LWSA. Resposta até 20 dias. Premium WhatsApp R$150/mês extra.", "octa_detail": "Analista dedicado conforme plano. Sem avaliações independentes. Em expansão rápida — capacidade de suporte sendo testada."},
    "Solidez / Risco do Fornecedor": {"Bling": 9, "Octalink": 5, "weight": 1.5, "bling_detail": "LWSA (B3: LWSA3). R$1,49B receita FY2025. 300k+ clientes. Maior ERP PME do Brasil.", "octa_detail": "Bootstrap 8 anos, 20%/ano por indicação — forte sinal de product-market fit. R$10M grant FINEP. Sem avaliações independentes. Em aceleração desde out/2024."},
    "Custo-Benefício":               {"Bling": 9, "Octalink": 3, "weight": 2.0, "bling_detail": "R$55–650/mês. Trial gratuito. Sem setup. Cancela quando quiser.", "octa_detail": "R$1.597–7.897/mês software. 80% dos clientes compram serviço gerenciado além do plano. Custo real > preço do plano. Sem trial."},
    "Integração Marketplaces":       {"Bling": 9, "Octalink": 1, "weight": 0.5, "bling_detail": "250+ integrações: ML, Amazon, Shopee, Magalu, Shopify, Tray, WooCommerce…", "octa_detail": "Sem integrações com marketplaces. Não é o foco da plataforma."},
}

PROS_CONS = {
    "Bling": {
        "pros": ["Maior ERP para PME do Brasil — 300k+ clientes, 20 anos de mercado", "Módulo Pequena Indústria: OP + BOM a partir de R$110/mês", "NF-e/NFC-e/NFS-e completo + SPED expandindo para Titânio em abr/2026", "Trial gratuito 30 dias, sem taxa de setup, cancela quando quiser", "Ecossistema LWSA: Tray, Melhor Envio, Conta Digital, crédito embutido", "Capterra 4,7/5 · Reclame Aqui RA1000", "250+ integrações com marketplaces", "Grande comunidade + central de ajuda completa"],
        "cons": ["480 reclamações no Reclame Aqui em 6 meses — instabilidade recorrente", "Quedas às segundas, travamentos após atualizações", "Suporte com resposta de até 20 dias pós-aquisição pela LWSA", "Premium WhatsApp R$150/mês extra (gratuito só no Diamante)", "Sem RH/folha — stack separado necessário", "Sem MRP, sem roteiros, sem QA, sem chão de fábrica", "Custeio de produção manual e básico — não é motor industrial", "Reestruturação de planos em abr/2026 gera incerteza"],
    },
    "Octalink": {
        "pros": ["Módulo industrial confirmado: OP com BOM, almoxarifado, QR Code, custo médio", "Controladoria completa: fluxo tripartite, DRE com drilldown, budget vs real", "Open Finance via API regulamentada — conciliação real, não screen-scraping", "CRM nativo com rastreamento de leads e agentes de IA no WhatsApp", "IBS/CBS da Reforma 2027 já implementado no sistema", "Regras fiscais automáticas por operação — CST, CFOP, retenções", "IA para parametrização contábil (beta) — reduz setup de 90 dias", "Bootstrap 8 anos, 20%/ano, R$10M grant FINEP aprovado", "Escalável do Simples Nacional até Lucro Real S/A na mesma instância", "Fechamento de mês no 1º dia útil — prova do modelo funcionando"],
        "cons": ["Start R$1.597/mês = 8,6× mais caro que Bling Titânio R$185/mês", "Custo real = software + serviço gerenciado (80% dos clientes compram os dois)", "Setup de 90 dias — exige contador engajado (gargalo real reconhecido)", "Indústria é 8% da base — módulo industrial não é o foco principal", "ERP Aurora é o produto mais novo — controladoria é o maduro", "Perfil ideal: R$4M–R$10M — cliente abaixo disso é overkill no curto prazo", "Sem trial, sem auto-atendimento, sem avaliações independentes", "Em expansão rápida — suporte sendo testado", "Ativo fixo incompleto em algumas instâncias", "Sem RH/folha — mesma lacuna do Bling"],
    },
}

PAIN_POINTS = [
    {"pain": "Sem controle de estoque", "priority": "Crítico", "bling_score": 8, "octalink_score": 7, "bling_note": "Multidepósito, código de barras, movimentações, baixa automática de insumos em OPs.", "octalink_note": "Almoxarifado completo: custo médio automático, QR Code por item e endereço, fator de conversão, rastreamento de lotes. Confirmado in-person."},
    {"pain": "Sem RH / Folha / Ponto", "priority": "Crítico", "bling_score": 0, "octalink_score": 0, "bling_note": "Zero. Stack: escritório contábil + Convenia + Pontomais.", "octalink_note": "Rateio e contabilização apenas — cálculo externo. Na prática: mesma lacuna."},
    {"pain": "Sem controle de produção", "priority": "Crítico", "bling_score": 6, "octalink_score": 6, "bling_note": "OP + BOM a partir do Mercúrio. Baixa automática. OP a partir de pedido de venda.", "octalink_note": "OP com BOM confirmada in-person. Baixa automática com disponibilidade por almoxarifado. 8% dos clientes são indústria."},
    {"pain": "Sem NF-e / sistema fiscal", "priority": "Alto", "bling_score": 9, "octalink_score": 8, "bling_note": "Melhor da categoria. NF-e/NFC-e/NFS-e em todos os planos. SPED expandindo abr/2026.", "octalink_note": "NF-e (55), CT-e (57), NFS-e confirmados. Regras fiscais automáticas. CFOP por estado. Retenções automáticas."},
    {"pain": "Sem relatórios / dados", "priority": "Médio", "bling_score": 4, "octalink_score": 9, "bling_note": "Add-on Meu Negócio básico no Titânio+. Limitado.", "octalink_note": "Produto mais forte do Octalink. Drilldown até documento, budget vs real, data lake, Lovable. Genuinamente superior."},
    {"pain": "Conformidade fiscal (SPED, Reforma)", "priority": "Alto", "bling_score": 6, "octalink_score": 8, "bling_note": "SPED EFD expandindo. Bloco K parcial. Reforma a confirmar.", "octalink_note": "IBS/CBS já implementado. Regras por NCM, CST, CFOP. Devedor contumaz monitorado. Bloco K não confirmado."},
]

RECOMMENDATION_REASONS = [
    ("Estágio do negócio", "O cliente está digitalizando do zero. O Octalink foi projetado para empresas com R$4M–R$10M e maturidade financeira. O próprio CEO confirmou: para quem paga R$250–400/mês não faz sentido."),
    ("Custo vs. valor entregue agora", "Bling Titânio a R$185/mês entrega NF-e, estoque, produção básica e SPED. O Octalink Start a R$1.597/mês entrega funcionalidades que o cliente não vai usar no curto prazo — controladoria avançada, budget vs real, centros de custo."),
    ("Octalink é viável tecnicamente", "A razão para não recomendar mudou: não é mais 'zero produção' — é 'errado para o estágio atual'. O módulo industrial existe e funciona. A reavaliação em 12-18 meses é real."),
    ("RH permanece gap em ambos", "Nenhuma das plataformas processa folha. Stack: escritório contábil + Convenia + Pontomais — independente da escolha."),
    ("Reforma Tributária 2027", "A partir de 2027, Simples Nacional pode tornar empresas 20-30% mais caras que concorrentes. Maturidade fiscal importa no médio prazo — razão adicional para revisitar o Octalink quando o faturamento crescer."),
    ("Revisita em 12-18 meses", "Gatilhos: faturamento justifica R$1.597/mês, ferramenta de IA de setup estável (saindo do beta abr/2026), suporte do Octalink absorveu crescimento, contador engajado disponível."),
]

def weighted_score(platform):
    total_w = sum(v["weight"] for v in FEATURES.values())
    total_s = sum(v[platform] * v["weight"] for v in FEATURES.values())
    return round((total_s / (total_w * 10)) * 100)

BLING_SCORE    = weighted_score("Bling")
OCTALINK_SCORE = weighted_score("Octalink")

NAVY = "#0d2340"; GOLD = "#c9a040"; GOLD_L = "#e8b84b"; BLUE = "#1a4a8a"; BLUE_L = "#2563b0"
RED = "#b03030"; RED_L = "#dc4040"; GREEN = "#1a6640"; MUTED = "#5a6a80"; LIGHT = "#8090a8"
BG = "#ffffff"; BG2 = "#f4f6f9"; BG3 = "#eaf0f8"; BORDER = "#d0dae8"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {{ font-family: 'Sora', sans-serif; }}
.stApp {{ background: {BG}; }}
[data-testid="stSidebar"] {{ background: {NAVY} !important; border-right: 1px solid #1a3a5c; }}
[data-testid="stSidebar"] * {{ color: #c8d8e8 !important; }}
[data-testid="stSidebar"] hr {{ border-color: #1a3a5c !important; }}
h1 {{ color: {NAVY} !important; font-size: 1.9rem !important; font-weight: 700 !important; }}
h2 {{ color: {NAVY} !important; font-size: 1.4rem !important; font-weight: 600 !important; }}
h3 {{ color: {NAVY} !important; font-size: 1.15rem !important; font-weight: 600 !important; }}
h4 {{ color: {NAVY} !important; font-weight: 600 !important; }}
p, li {{ color: #2a3a4a !important; }}
[data-testid="metric-container"] {{ background: {BG2}; border: 1px solid {BORDER}; border-top: 3px solid {GOLD}; border-radius: 8px; padding: 14px; }}
[data-testid="stMetricValue"] {{ color: {NAVY} !important; font-size: 1.6rem !important; font-weight: 700 !important; }}
[data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-size: 0.78rem !important; }}
[data-testid="stTabs"] button {{ color: {MUTED} !important; font-weight: 600 !important; font-size: 0.85rem !important; background: transparent !important; }}
[data-testid="stTabs"] button[aria-selected="true"] {{ color: {NAVY} !important; border-bottom: 2px solid {GOLD} !important; }}
hr {{ border-color: {BORDER} !important; }}
[data-testid="stExpander"] {{ border: 1px solid {BORDER} !important; border-radius: 6px !important; background: {BG2} !important; }}
</style>""", unsafe_allow_html=True)

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG2, font=dict(family="Sora, sans-serif", color="#2a3a4a"))

with st.sidebar:
    st.markdown(f"<div style='color:{GOLD_L};font-size:1.1rem;font-weight:700;margin-bottom:4px'>⚙️ Comparativo ERP</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#a8c8e8;font-weight:600;font-size:0.9rem'>Bling vs Octalink</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6a8ab0;font-size:0.8rem;margin-top:2px'>Pequena Indústria · Brasil</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Navegar", ["📊  Visão Geral", "🏭  Módulo Industrial", "🔬  Análise de Recursos", "💰  Preços", "📈  Aderência à Fábrica", "📣  Prós e Contras", "🧭  Recomendação", "🏢  Perfil das Empresas"])
    st.divider()
    st.markdown(f"<div style='color:{GOLD_L};font-size:0.78rem;font-weight:700'>Status dos dados</div>", unsafe_allow_html=True)
    st.markdown("✅ Bling — verificado mar/2026")
    st.markdown("✅ Octalink — confirmado in-person")
    st.markdown(f"<div style='color:#6a8ab0;font-size:0.75rem;margin-top:4px'>Dados validados na apresentação oficial</div>", unsafe_allow_html=True)
    st.divider()
    st.caption("Albuquerque Consulting · Março 2026")

# ── VISÃO GERAL ──────────────────────────────────────────────────────────────
if page == "📊  Visão Geral":
    st.markdown(f"""<div style="background:{NAVY};padding:28px 32px;border-radius:10px;margin-bottom:24px">
        <div style="color:{GOLD_L};font-size:0.75rem;font-weight:700;letter-spacing:1.5px;margin-bottom:8px">COMPARATIVO ERP · MARÇO 2026</div>
        <div style="color:white;font-size:1.75rem;font-weight:700;line-height:1.2">Bling vs Octalink</div>
        <div style="color:#8ab0d0;font-size:0.9rem;margin-top:6px">Pequena indústria de manufatura · Brasil · Digitalização completa do zero</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="background:#f0f8f4;border:1px solid #2a7a4a;border-left:5px solid #2a7a4a;padding:16px 22px;border-radius:6px;margin-bottom:12px">
        <span style="color:#1a5a30;font-weight:700;font-size:13px">✅ CORREÇÃO — MÓDULO INDUSTRIAL OCTALINK CONFIRMADO IN-PERSON</span><br/>
        <span style="color:#1a3a28;font-size:13px;line-height:1.7">A pesquisa inicial indicava zero funcionalidades de produção no Octalink. <b>Isso foi corrigido após apresentação oficial:</b> a plataforma possui almoxarifado, OP com BOM, QR Code, custo médio automático e rastreamento de lotes. A recomendação mudou de motivo: <b>não é inadequado tecnicamente — é inadequado pelo estágio e custo para este cliente agora.</b></span>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="background:#fff8f0;border:1px solid {GOLD};border-left:5px solid {GOLD};padding:16px 22px;border-radius:6px;margin-bottom:24px">
        <span style="color:#7a5010;font-weight:700;font-size:13px">⚠ LACUNA PERMANENTE — RH E FOLHA EM NENHUMA DAS PLATAFORMAS</span><br/>
        <span style="color:#4a3010;font-size:13px;line-height:1.7"><b>Nenhuma das duas</b> processa folha. O Octalink faz apenas rateio e contabilização. Stack necessário nos dois casos: <b>escritório contábil + Convenia + Pontomais.</b></span>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=BLING_SCORE,
            title={"text": "Bling · Aderência à Fábrica", "font": {"color": NAVY, "size": 13}},
            number={"suffix": "/100", "font": {"color": BLUE, "size": 38}},
            gauge={"axis": {"range": [0,100]}, "bar": {"color": BLUE}, "bgcolor": BG2, "bordercolor": BORDER,
                   "steps": [{"range": [0,40], "color": "#fce8e8"}, {"range": [40,70], "color": "#fdf5e0"}, {"range": [70,100], "color": "#e8f4ee"}],
                   "threshold": {"line": {"color": GOLD, "width": 2}, "thickness": 0.75, "value": 70}}))
        fig.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure(go.Indicator(mode="gauge+number", value=OCTALINK_SCORE,
            title={"text": "Octalink · Aderência à Fábrica", "font": {"color": NAVY, "size": 13}},
            number={"suffix": "/100", "font": {"color": GOLD, "size": 38}},
            gauge={"axis": {"range": [0,100]}, "bar": {"color": GOLD}, "bgcolor": BG2, "bordercolor": BORDER,
                   "steps": [{"range": [0,40], "color": "#fce8e8"}, {"range": [40,70], "color": "#fdf5e0"}, {"range": [70,100], "color": "#e8f4ee"}],
                   "threshold": {"line": {"color": BLUE, "width": 2}, "thickness": 0.75, "value": 70}}))
        fig2.update_layout(**LAYOUT, height=230, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        diff = BLING_SCORE - OCTALINK_SCORE
        diff_str = f"Bling +{diff} pts" if diff > 0 else f"Octalink +{abs(diff)} pts" if diff < 0 else "Empate"
        st.metric("Diferença de Pontuação", diff_str, f"{len(FEATURES)} critérios ponderados")
        st.metric("Bling Titânio (recomendado)", "R$185/mês", "Produção + SPED + NF-e")
        st.metric("Octalink Start", "R$1.597/mês", f"{round(1597/185,1)}× o custo do Bling Titânio")
        st.metric("RH / Folha", "❌ Nenhum dos dois", "Stack separado necessário")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-top:4px solid {BLUE};padding:22px;border-radius:8px">
          <div style="color:{NAVY};font-weight:700;font-size:1.1rem">Bling</div>
          <div style="color:{LIGHT};font-size:0.75rem;margin-bottom:12px">bling.com.br · Grupo LWSA (B3: LWSA3)</div>
          <div style="color:#2a3a4a;font-size:0.85rem;line-height:1.9">Maior ERP para PME do Brasil. 300k+ clientes. Desde 2005.<br/>Adquirido pela LWSA por <b style="color:{GOLD}">R$524M</b> em 2021.<br/>Commerce: <b style="color:{BLUE}">R$1,07B</b> receita FY2025.<br/>Módulo <b>Pequena Indústria</b>: OP + BOM desde R$110/mês.<br/>Capterra <b>4,7/5</b> · Reclame Aqui <b>RA1000</b> · Trial 30 dias.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-top:4px solid {GOLD};padding:22px;border-radius:8px">
          <div style="color:{NAVY};font-weight:700;font-size:1.1rem">Octalink</div>
          <div style="color:{LIGHT};font-size:0.75rem;margin-bottom:12px">octalink.com.br · Sumaré, SP · Bootstrap</div>
          <div style="color:#2a3a4a;font-size:0.85rem;line-height:1.9">ERP Aurora + CRM + Controladoria + BI + IA. Fundada dez/2017.<br/><b>Bootstrap</b> 8 anos, 20%/ano por indicação. R$10M grant FINEP.<br/>Módulo industrial <b>confirmado</b>: OP + BOM + almoxarifado + QR Code.<br/>Perfil ideal: <b>R$4M–R$10M</b> faturamento, saindo do Simples.<br/>Planos: R$1.597 · R$3.797 · R$7.897/mês.</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Custo Acumulado — 24 Meses")
    months = list(range(1, 25))
    bling_cum = [185 * m for m in months]
    octa_cum  = [1597 * m for m in months]
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=months, y=bling_cum, name="Bling Titânio", line=dict(color=BLUE, width=2.5), fill="tozeroy", fillcolor="rgba(26,74,138,0.08)", hovertemplate="Mês %{x}: R$%{y:,.0f}<extra>Bling</extra>"))
    fig_c.add_trace(go.Scatter(x=months, y=octa_cum, name="Octalink Start", line=dict(color=GOLD, width=2.5), fill="tozeroy", fillcolor="rgba(201,160,64,0.08)", hovertemplate="Mês %{x}: R$%{y:,.0f}<extra>Octalink</extra>"))
    fig_c.add_vrect(x0=12, x1=18, fillcolor=GOLD, opacity=0.07, annotation_text="Janela de revisita Octalink", annotation_position="top left", annotation_font_size=10)
    fig_c.update_layout(**LAYOUT, height=300, yaxis=dict(title="R$ acumulado", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(title="Mês", gridcolor=BORDER, tickfont=dict(color=MUTED)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(t=20, b=20))
    st.plotly_chart(fig_c, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Bling Titânio — Ano 1", "R$2.220", "12 × R$185")
    c2.metric("Octalink Start — Ano 1", "R$19.164", "12 × R$1.597")
    c3.metric("Economia no Ano 1", "R$16.944", "Usando Bling no primeiro ano")

# ── MÓDULO INDUSTRIAL ────────────────────────────────────────────────────────
elif page == "🏭  Módulo Industrial":
    st.title("Módulo Industrial — Comparativo Detalhado")
    st.markdown(f"<p style='color:{MUTED}'>Dados Octalink confirmados in-person na apresentação oficial (março/2026). Pesquisa inicial corrigida.</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown(f"""<div style="background:#f0f8f4;border:1px solid #2a7a4a;border-left:5px solid #2a7a4a;padding:14px 20px;border-radius:6px;margin-bottom:20px">
        <span style="color:#1a5a30;font-weight:700">Correção da pesquisa inicial</span><br/>
        <span style="color:#1a3a28;font-size:0.85rem;line-height:1.7">A pesquisa pré-evento indicava "zero funcionalidades de produção" no Octalink com base no site. Após a apresentação, esse dado foi corrigido: <b>o módulo industrial existe e foi demonstrado ao vivo</b> incluindo OP com BOM, almoxarifado com QR Code e custo médio automático. A seção industrial foi apresentada em resposta a uma pergunta da plateia — não faz parte da demo padrão, indicando que indústria é um mercado secundário (8% da base de clientes).</span>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Funcionalidades Octalink Industrial", "Comparativo Bling vs Octalink", "Gaps e Riscos"])

    with tab1:
        st.markdown("#### Módulo Industrial Octalink — Confirmado In-Person")
        for func, desc in OCTALINK_INDUSTRY.items():
            st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:3px solid {GOLD};padding:12px 16px;border-radius:6px;margin-bottom:8px">
              <div style="color:{NAVY};font-weight:600;font-size:0.9rem">✅ {func}</div>
              <div style="color:{MUTED};font-size:0.82rem;margin-top:4px;line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)
        for icon, title, desc, color in [
            ("⚠", "Ativo Fixo", "Mencionado como previsto mas 'ainda não tem' na instância demo. Depreciação e registro de ativos podem não estar disponíveis em todos os ambientes.", GOLD),
            ("❌", "Folha de Pagamento / RH", "Apenas rateio e contabilização da folha — cálculo externo. Mesma limitação do Bling.", RED),
            ("❌", "MRP Completo / Roteiros / Chão de Fábrica", "Há OP com BOM e baixa de insumos, mas sem planejamento de capacidade, sem roteiros, sem apontamento de chão de fábrica, sem QA formal. É MRP-lite.", RED),
        ]:
            st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:3px solid {color};padding:12px 16px;border-radius:6px;margin-top:8px">
              <div style="color:{NAVY};font-weight:600;font-size:0.9rem">{icon} {title}</div>
              <div style="color:{MUTED};font-size:0.82rem;margin-top:4px;line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        industry_rows = [
            ("Almoxarifado / Estoque físico", True, True, "Multidepósito, código de barras, baixa automática.", "Posição por qtd/valor, custo médio automático, localização por QR Code."),
            ("Ordens de Produção (OP)", True, True, "OP com ficha técnica (BOM), baixa automática, OP a partir de pedido de venda.", "OP com BOM, baixa automática, disponibilidade por almoxarifado em tempo real."),
            ("QR Code / Rastreabilidade", True, True, "Código de barras para movimentações.", "QR Code por item E endereçamento. Workflow separação→qualidade→estoque."),
            ("Custo Médio Automático", True, True, "Calculado a cada entrada/saída.", "Calculado automaticamente. Atualizado em cada operação."),
            ("Fator de Conversão de Unidades", False, True, "Não documentado nativamente.", "Normalização kg/unidade/caixa entre fornecedores."),
            ("Rastreamento de Lotes", False, True, "Não documentado.", "Data de validade, código de lote, APC. Rastreabilidade completa."),
            ("Monitoramento NF-e (SEFAZ)", False, True, "Importação manual de XML.", "Varredura automática SEFAZ. NFs contra CNPJ aparecem automaticamente."),
            ("Importação Internacional", True, True, "Entrada de nota de importação.", "FX, Incoterms, AWB, II, IPI, PIS/COFINS, seguro, frete. XML com centenas de itens."),
            ("Transferência entre Almoxarifados", False, True, "Não documentado.", "Transferência e movimentação interna rastreada."),
            ("MRP Completo", False, False, "Sem MRP.", "BOM + estoque disponível = MRP-lite. Sem planejamento de capacidade."),
            ("Roteiros / Chão de Fábrica", False, False, "Sem roteiros.", "Sem roteiros, sem apontamento de chão de fábrica."),
            ("Controle de Qualidade Formal", False, False, "Sem módulo de QA.", "Workflow básico mencionado, sem módulo formal."),
            ("RH / Folha de Pagamento", False, False, "Zero — stack separado.", "Apenas rateio e contabilização — cálculo externo."),
            ("Ativo Fixo / Depreciação", False, False, "Não disponível.", "Previsto mas não implementado em todas as instâncias."),
        ]
        st.markdown(f"""<div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:0;background:{NAVY};padding:10px 16px;border-radius:6px 6px 0 0">
          <div style="color:{GOLD_L};font-weight:700;font-size:0.8rem">FUNCIONALIDADE</div>
          <div style="color:{GOLD_L};font-weight:700;font-size:0.8rem;text-align:center">BLING</div>
          <div style="color:{GOLD_L};font-weight:700;font-size:0.8rem;text-align:center">OCTALINK</div>
        </div>""", unsafe_allow_html=True)
        for feat, bling_has, octa_has, bn, on in industry_rows:
            b_icon = "✅" if bling_has else "❌"
            o_icon = "✅" if octa_has else "❌"
            with st.expander(f"{b_icon} Bling  {o_icon} Octalink  ·  **{feat}**"):
                c1, c2 = st.columns(2)
                with c1: st.markdown(f"**🟦 Bling**"); st.caption(bn)
                with c2: st.markdown(f"**🟨 Octalink**"); st.caption(on)

    with tab3:
        risks = [
            ("🟡 Mercado Secundário", "Indústria = 8% da base de clientes. Módulo existe, mas roadmap, suporte e profundidade refletem foco primário em serviços e comércio.", GOLD),
            ("🟡 Demo Não Planejada", "A seção industrial foi apresentada em resposta a pergunta da plateia. Reforça que não é o caso de uso principal.", GOLD),
            ("🔴 ERP Aurora é o Produto Mais Novo", "Octalink começou em 2015 como overlay BI sobre SAP/TOTVS. ERP Aurora (com módulo industrial) veio depois. Controladoria é o maduro; ERP operacional ainda evolui.", RED),
            ("🔴 Não é MRP Industrial Completo", "BOM + OP + baixa de insumos = suficiente para produção simples. Sem planejamento de capacidade, roteiros, apontamento ou QA formal.", RED),
            ("🔴 Ativo Fixo Incompleto", "CEO indicou 'ainda não tem' na instância demo. Depreciação e registro de ativos podem não estar disponíveis.", RED),
            ("🟢 Para Este Cliente Agora", "Operação simples partindo do zero. Tecnicamente, Octalink cobriria as necessidades básicas. O problema é custo (8,6×) e estágio. A avaliação em 12-18 meses é real.", GREEN),
        ]
        for title, desc, color in risks:
            st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:4px solid {color};padding:12px 16px;border-radius:6px;margin-bottom:8px">
              <div style="color:{NAVY};font-weight:600;font-size:0.9rem">{title}</div>
              <div style="color:{MUTED};font-size:0.82rem;margin-top:4px;line-height:1.6">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ── ANÁLISE DE RECURSOS ───────────────────────────────────────────────────────
elif page == "🔬  Análise de Recursos":
    st.title("Análise de Recursos")
    st.markdown(f"<p style='color:{MUTED}'>{len(FEATURES)} critérios pontuados de 0 a 10, com peso por relevância para a fábrica</p>", unsafe_allow_html=True)
    st.divider()

    features = list(FEATURES.keys())
    bs = [FEATURES[f]["Bling"] for f in features]
    os_ = [FEATURES[f]["Octalink"] for f in features]
    ws = [FEATURES[f]["weight"] for f in features]

    tab1, tab2, tab3, tab4 = st.tabs(["Radar", "Barras Horizontais", "Pontuação Ponderada", "Tabela Detalhada"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=bs+[bs[0]], theta=features+[features[0]], fill="toself", name="Bling", line_color=BLUE, fillcolor="rgba(26,74,138,0.15)"))
        fig.add_trace(go.Scatterpolar(r=os_+[os_[0]], theta=features+[features[0]], fill="toself", name="Octalink", line_color=GOLD, fillcolor="rgba(201,160,64,0.15)"))
        fig.update_layout(**LAYOUT, polar=dict(bgcolor=BG2, radialaxis=dict(visible=True, range=[0,10], color=MUTED, gridcolor=BORDER, tickfont=dict(size=9)), angularaxis=dict(color=MUTED, gridcolor=BORDER, tickfont=dict(size=10))), showlegend=True, legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), height=580, margin=dict(t=20,b=20,l=40,r=40))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame({"Recurso": features, "Bling": bs, "Octalink": os_, "Peso": ws}).sort_values("Peso", ascending=False)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Bling", y=df["Recurso"], x=df["Bling"], orientation="h", marker_color=BLUE, hovertemplate="<b>Bling</b> · %{y}: %{x}/10<extra></extra>"))
        fig2.add_trace(go.Bar(name="Octalink", y=df["Recurso"], x=df["Octalink"], orientation="h", marker_color=GOLD, hovertemplate="<b>Octalink</b> · %{y}: %{x}/10<extra></extra>"))
        fig2.update_layout(**LAYOUT, barmode="group", height=580, xaxis=dict(range=[0,10], gridcolor=BORDER, tickfont=dict(color=MUTED)), yaxis=dict(tickfont=dict(color=NAVY, size=11)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=20,t=20,b=20))
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        df_w = pd.DataFrame({"Recurso": features, "Bling": [b*w for b,w in zip(bs,ws)], "Octalink": [o*w for o,w in zip(os_,ws)], "Peso": ws}).sort_values("Peso", ascending=False)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Bling", y=df_w["Recurso"], x=df_w["Bling"], orientation="h", marker_color=BLUE, hovertemplate="Bling · %{y}: %{x:.1f} pts<extra></extra>"))
        fig3.add_trace(go.Bar(name="Octalink", y=df_w["Recurso"], x=df_w["Octalink"], orientation="h", marker_color=GOLD, hovertemplate="Octalink · %{y}: %{x:.1f} pts<extra></extra>"))
        fig3.update_layout(**LAYOUT, barmode="group", height=580, xaxis=dict(gridcolor=BORDER, tickfont=dict(color=MUTED), title="Pontuação ponderada"), yaxis=dict(tickfont=dict(color=NAVY, size=11)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=20,t=20,b=20))
        st.plotly_chart(fig3, use_container_width=True)
        c1, c2 = st.columns(2)
        total_w = sum(ws); max_pts = total_w * 10
        c1.metric("Bling — Pontuação Final", f"{BLING_SCORE}/100", f"{sum(b*w for b,w in zip(bs,ws)):.1f} de {max_pts:.1f} pts possíveis")
        c2.metric("Octalink — Pontuação Final", f"{OCTALINK_SCORE}/100", f"{sum(o*w for o,w in zip(os_,ws)):.1f} de {max_pts:.1f} pts possíveis")

    with tab4:
        for fname, fdata in sorted(FEATURES.items(), key=lambda x: -x[1]["weight"]):
            b = fdata["Bling"]; o = fdata["Octalink"]; w = fdata["weight"]
            with st.expander(f"**{fname}** — Bling: {b}/10   Octalink: {o}/10   peso: {w}×"):
                c1, c2 = st.columns(2)
                with c1: st.markdown(f"**Bling** {'🟦'*b+'⬜'*(10-b)}"); st.caption(fdata["bling_detail"])
                with c2: st.markdown(f"**Octalink** {'🟨'*o+'⬜'*(10-o)}"); st.caption(fdata["octa_detail"])

# ── PREÇOS ────────────────────────────────────────────────────────────────────
elif page == "💰  Preços":
    st.title("Comparativo de Preços")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Planos Bling", "Planos Octalink", "Análise de Custo"])

    with tab1:
        st.markdown("#### Bling — Planos Vigentes (Março 2026)")
        st.info("📅 **Mudança em abril/2026:** O Mercúrio será incorporado ao Titânio (nova Faixa 1). SPED fiscal passa a valer para o Titânio.")
        for name, p in BLING_PLANS.items():
            is_rec = "★" in name
            border = GOLD if is_rec else BORDER; bg = "#fffbf0" if is_rec else BG2
            st.markdown(f"""<div style="background:{bg};border:1px solid {border};border-left:4px solid {border};padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline"><span style="color:{NAVY};font-weight:700">{name}</span><span style="color:{GOLD};font-weight:700">R${p['price_monthly']}/mês</span></div>
              <div style="color:{LIGHT};font-size:0.75rem;margin:4px 0 8px 0">Anual: R${p['price_annual']}/mês · {p['users']} usuários · {p['dados']} · {p['arquivos']} · {p['mkt_imports']}</div>
              <div style="font-size:0.8rem;color:{MUTED}">{"✅ Produção" if p["production"] else "❌ Sem produção"} &nbsp; {"✅ SPED" if p["sped"] else "❌ Sem SPED"} &nbsp; {"✅ PDV" if p["pdv"] else "❌ Sem PDV"}</div>
              <div style="color:{LIGHT};font-size:0.75rem;margin-top:6px">{p['note']}</div>
            </div>""", unsafe_allow_html=True)
        names = list(BLING_PLANS.keys()); prices = [v["price_monthly"] for v in BLING_PLANS.values()]
        fig = go.Figure(go.Bar(x=names, y=prices, marker_color=[GOLD if "★" in n else BLUE for n in names], hovertemplate="%{x}: R$%{y}/mês<extra></extra>"))
        fig.update_layout(**LAYOUT, height=280, showlegend=False, yaxis=dict(title="R$/mês", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(tickfont=dict(color=NAVY)), margin=dict(t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Octalink — Planos (Confirmados In-Person, Março 2026)")
        st.success("✅ Preços e funcionalidades confirmados na apresentação oficial. Start = R$1.597/mês declarado pelo CEO.")
        for name, p in OCTALINK_PLANS.items():
            is_best = "★" in name; border_c = GOLD if is_best else BLUE; bg_c = "#fffbf0" if is_best else BG2
            st.markdown(f"""<div style="background:{bg_c};border:1px solid {border_c};border-left:4px solid {border_c};padding:14px 18px;border-radius:6px;margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;align-items:baseline"><span style="color:{NAVY};font-weight:700">{name}</span><span style="color:{GOLD};font-weight:700">R${p['price_monthly']:,}/mês</span></div>
              <div style="color:{LIGHT};font-size:0.75rem;margin:4px 0 8px 0">{p['users']} · ✅ Confirmado in-person</div>
              <div style="color:{MUTED};font-size:0.8rem">{p['note']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#fff8f0;border:1px solid {GOLD};border-left:4px solid {GOLD};padding:12px 16px;border-radius:6px;margin-top:8px">
          <span style="color:#7a5010;font-weight:600;font-size:0.85rem">⚠ Custo Real vs. Preço do Plano</span><br/>
          <span style="color:{MUTED};font-size:0.82rem;line-height:1.6">O CEO declarou que <b>80% dos clientes que fecham o ERP também compram o serviço gerenciado</b> (financeiro, contábil ou fiscal). O preço do plano é o piso — o custo total é maior.</span>
        </div>""", unsafe_allow_html=True)

    with tab3:
        comp_names = ["Bling\nCobalto", "Bling\nMercúrio", "Bling\nTitânio ★", "Bling\nPlatina", "Bling\nDiamante", "Octalink\nStart", "Octalink\nPro ★", "Octalink\nGrowth"]
        comp_prices = [55, 110, 185, 450, 650, 1597, 3797, 7897]
        fig2 = go.Figure(go.Bar(x=comp_names, y=comp_prices, marker_color=[BLUE]*5+[GOLD]*3, hovertemplate="%{x}: R$%{y}/mês<extra></extra>", text=[f"R${p}" for p in comp_prices], textposition="outside", textfont=dict(size=10, color=NAVY)))
        fig2.update_layout(**LAYOUT, height=400, showlegend=False, yaxis=dict(title="R$/mês", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(tickfont=dict(color=NAVY, size=10)), margin=dict(t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.markdown("#### Múltiplo de Custo vs Bling Titânio")
        multiples = [round(p/185, 1) for p in [1597, 3797, 7897]]
        fig3 = go.Figure(go.Bar(x=["Start (R$1.597)", "Pro (R$3.797)", "Growth (R$7.897)"], y=multiples, marker_color=GOLD, text=[f"{m}×" for m in multiples], textposition="outside", textfont=dict(size=14, color=NAVY), hovertemplate="%{x}: %{y}× o Bling Titânio<extra></extra>"))
        fig3.add_hline(y=1, line_dash="dash", line_color=BLUE, annotation_text="Bling Titânio (base)", annotation_position="right")
        fig3.update_layout(**LAYOUT, height=300, showlegend=False, yaxis=dict(title="Múltiplo", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(tickfont=dict(color=NAVY)), margin=dict(t=40,b=20))
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.markdown("#### Custo Anual Acumulado — Primeiro Ano")
        months = list(range(1,13))
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=months, y=[185*m for m in months], name="Bling Titânio", line=dict(color=BLUE, width=2.5), fill="tozeroy", fillcolor="rgba(26,74,138,0.08)", hovertemplate="Mês %{x}: R$%{y:,.0f}<extra>Bling</extra>"))
        fig4.add_trace(go.Scatter(x=months, y=[1597*m for m in months], name="Octalink Start", line=dict(color=GOLD, width=2.5), fill="tozeroy", fillcolor="rgba(201,160,64,0.08)", hovertemplate="Mês %{x}: R$%{y:,.0f}<extra>Octalink</extra>"))
        fig4.update_layout(**LAYOUT, height=300, yaxis=dict(title="Custo Acumulado (R$)", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(title="Mês", tickfont=dict(color=MUTED)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(t=20,b=20))
        st.plotly_chart(fig4, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Bling — Ano 1", "R$2.220", "12 × R$185"); c2.metric("Octalink — Ano 1", "R$19.164", "12 × R$1.597"); c3.metric("Economia Ano 1", "R$16.944", "Escolhendo Bling no primeiro ano")

# ── ADERÊNCIA À FÁBRICA ───────────────────────────────────────────────────────
elif page == "📈  Aderência à Fábrica":
    st.title("Aderência à Fábrica — Análise por Dor")
    st.markdown(f"<p style='color:{MUTED}'>Pontuação de cada plataforma frente às dores específicas do cliente. Dados pós-validação.</p>", unsafe_allow_html=True)
    st.divider()

    for pp in PAIN_POINTS:
        b = pp["bling_score"]; o = pp["octalink_score"]
        with st.expander(f"**{pp['pain']}** — Prioridade: {pp['priority']}   |   Bling: {b}/10   Octalink: {o}/10"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:14px;border-radius:6px">
                  <div style="color:{NAVY};font-weight:700;margin-bottom:8px">🟦 Bling — {b}/10</div>
                  <div style="background:{BORDER};border-radius:4px;height:8px;margin-bottom:10px"><div style="background:{BLUE if b>=5 else (GOLD if b>0 else RED)};width:{b*10}%;height:8px;border-radius:4px"></div></div>
                  <div style="color:{MUTED};font-size:0.82rem;line-height:1.6">{pp['bling_note']}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:14px;border-radius:6px">
                  <div style="color:{NAVY};font-weight:700;margin-bottom:8px">🟨 Octalink — {o}/10</div>
                  <div style="background:{BORDER};border-radius:4px;height:8px;margin-bottom:10px"><div style="background:{GOLD if o>=5 else (BLUE_L if o>0 else RED)};width:{o*10}%;height:8px;border-radius:4px"></div></div>
                  <div style="color:{MUTED};font-size:0.82rem;line-height:1.6">{pp['octalink_note']}</div>
                </div>""", unsafe_allow_html=True)

    st.divider()
    pain_names = [pp["pain"] for pp in PAIN_POINTS]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Bling", x=pain_names, y=[pp["bling_score"] for pp in PAIN_POINTS], marker_color=BLUE, hovertemplate="Bling · %{x}: %{y}/10<extra></extra>"))
    fig.add_trace(go.Bar(name="Octalink", x=pain_names, y=[pp["octalink_score"] for pp in PAIN_POINTS], marker_color=GOLD, hovertemplate="Octalink · %{x}: %{y}/10<extra></extra>"))
    fig.update_layout(**LAYOUT, barmode="group", height=380, yaxis=dict(range=[0,10], gridcolor=BORDER, title="Pontuação /10", tickfont=dict(color=MUTED)), xaxis=dict(tickangle=-20, tickfont=dict(size=10, color=NAVY)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(t=20,b=100,l=10,r=10))
    st.plotly_chart(fig, use_container_width=True)

# ── PRÓS E CONTRAS ────────────────────────────────────────────────────────────
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

    st.divider()
    fig_pc = go.Figure()
    fig_pc.add_trace(go.Bar(name="Prós", x=["Bling","Octalink"], y=[len(PROS_CONS["Bling"]["pros"]),len(PROS_CONS["Octalink"]["pros"])], marker_color=GREEN, hovertemplate="%{x}: %{y} prós<extra></extra>"))
    fig_pc.add_trace(go.Bar(name="Contras", x=["Bling","Octalink"], y=[-len(PROS_CONS["Bling"]["cons"]),-len(PROS_CONS["Octalink"]["cons"])], marker_color=RED, hovertemplate="%{x}: %{y} contras<extra></extra>"))
    fig_pc.update_layout(**LAYOUT, barmode="relative", height=300, yaxis=dict(title="Quantidade", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(tickfont=dict(color=NAVY, size=13)), legend=dict(font=dict(color=NAVY), bgcolor="rgba(0,0,0,0)"), margin=dict(t=20,b=20))
    st.plotly_chart(fig_pc, use_container_width=True)

# ── RECOMENDAÇÃO ──────────────────────────────────────────────────────────────
elif page == "🧭  Recomendação":
    st.title("Recomendação Final")
    st.divider()
    st.markdown(f"""<div style="background:{NAVY};padding:28px 32px;border-radius:10px;margin-bottom:24px">
        <div style="color:{GOLD_L};font-size:0.8rem;font-weight:700;letter-spacing:1.2px;margin-bottom:6px">RECOMENDAÇÃO</div>
        <div style="color:white;font-size:1.5rem;font-weight:700">Bling Titânio — Primeiro Passo</div>
        <div style="color:#8ab0d0;font-size:0.95rem;margin-top:6px">Revisitar Octalink em 12–18 meses quando o faturamento e a maturidade operacional justificarem</div>
    </div>""", unsafe_allow_html=True)

    for i, (title, desc) in enumerate(RECOMMENDATION_REASONS, 1):
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:4px solid {GOLD};padding:14px 20px;border-radius:6px;margin-bottom:10px">
          <div style="color:{NAVY};font-weight:700;font-size:0.9rem">{i}. {title}</div>
          <div style="color:{MUTED};font-size:0.85rem;margin-top:6px;line-height:1.7">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Stack Recomendado — Fase 1 (Imediato)")
    for name, price, color, desc in [
        ("🟦 Bling Titânio", "R$185/mês", BLUE, "ERP principal: NF-e/NFS-e/CT-e, estoque, OP com BOM, SPED (abr/2026), financeiro básico, 250+ integrações marketplace."),
        ("👥 Convenia", "~R$15/func/mês", "#2a6a4a", "Gestão de RH: admissão, férias, benefícios, documentos. Integra com folha do escritório contábil."),
        ("⏱ Pontomais", "~R$10/func/mês", "#2a4a8a", "Controle de ponto digital: app mobile, reconhecimento facial, relatórios para folha."),
        ("📋 Escritório Contábil", "Variável", "#6a2a6a", "Folha de pagamento, obrigações fiscais, SPED, Reforma Tributária 2027. Necessário em qualquer cenário."),
    ]:
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:4px solid {color};padding:14px 20px;border-radius:6px;margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;align-items:baseline"><span style="color:{NAVY};font-weight:700">{name}</span><span style="color:{GOLD};font-weight:600">{price}</span></div>
          <div style="color:{MUTED};font-size:0.82rem;margin-top:6px;line-height:1.6">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Gatilhos para Revisitar o Octalink (Fase 2)")
    triggers = [
        ("Faturamento justifica R$1.597/mês", "Quando o custo do Octalink representa menos de 0,5% do faturamento mensal."),
        ("Ferramenta de IA de setup estabilizada", "IA de parametrização entra em produção (abr/2026). Aguardar 3-6 meses de estabilidade antes de adotar."),
        ("Suporte do Octalink amadureceu", "A empresa triplicou vendas em 3 meses. Aguardar absorção do crescimento e estabilização do suporte."),
        ("Necessidade de controladoria avançada", "Quando DRE por centro de custo, budget vs real e EBITDA forem necessários para decisões."),
        ("Contador engajado disponível", "O setup de 90 dias exige um contador disposto a parametrizar regras contábeis — sem isso, o setup falha."),
        ("Reforma Tributária 2027 se aproxima", "Com IBS/CBS em vigor, a maturidade fiscal do Octalink se torna mais relevante e diferenciada."),
    ]
    for title, desc in triggers:
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-left:3px solid {GOLD_L};padding:10px 16px;border-radius:6px;margin-bottom:6px">
          <div style="color:{NAVY};font-weight:600;font-size:0.85rem">🎯 {title}</div>
          <div style="color:{MUTED};font-size:0.8rem;margin-top:4px">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Alternativas Industriais a Avaliar em Paralelo")
    for name, price, desc in [
        ("Nomus ERP Industrial", "~R$490/mês", "ERP focado 100% em manufatura. MRP completo, roteiros, chão de fábrica, custos industriais. Ideal se a complexidade de produção crescer."),
        ("WebMais", "~R$350/mês", "ERP industrial para PMEs. Bom equilíbrio funcionalidade/preço. Vale avaliação em paralelo ao Bling."),
        ("Omie", "R$149–499/mês", "Concorrente direto do Bling. Módulo industrial disponível. 200k+ usuários. Vale comparação de funcionalidades específicas."),
    ]:
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:12px 16px;border-radius:6px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between"><span style="color:{NAVY};font-weight:600">{name}</span><span style="color:{MUTED};font-size:0.85rem">{price}</span></div>
          <div style="color:{MUTED};font-size:0.82rem;margin-top:4px">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── PERFIL DAS EMPRESAS ───────────────────────────────────────────────────────
elif page == "🏢  Perfil das Empresas":
    st.title("Perfil das Empresas")
    st.divider()
    tab1, tab2 = st.tabs(["Bling / LWSA", "Octalink"])

    with tab1:
        st.markdown(f"<h3 style='color:{NAVY}'>Bling · Grupo LWSA</h3>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Fundação","2005"); c2.metric("Aquisição","R$524,3M","LWSA, junho/2021")
        c3.metric("Receita LWSA FY2025","R$1,49B","+10,3% ao ano"); c4.metric("Segmento Commerce","R$1,07B","+15,3% ao ano")
        st.divider()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Assinantes","206.300","+6,8% ao ano"); c2.metric("Capterra","4,7/5","102 avaliações")
        c3.metric("Reclame Aqui","RA1000","8,6/10 · 90,9% resolvidos"); c4.metric("Reclamações RA (6 meses)","480","Set/2025–Fev/2026")
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Ecossistema LWSA</h4>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:18px 22px;border-radius:8px;font-size:0.85rem;color:#2a3a4a;line-height:1.9">
        • <b>Tray</b> — lojas virtuais · <b>Melhor Envio</b> — logística · <b>Vindi</b> — pagamentos<br/>
        • <b>Conta Digital</b> — PIX, boleto, crédito rotativo · <b>250+ conectores de marketplace</b>
        </div>""", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Principais Reclamações no Reclame Aqui</h4>", unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=["Instabilidade/quedas","Demora no atendimento","Travamentos pós-update","Reajuste abr/2025","Falhas marketplace","Limitações de escala"], y=[34,24,18,12,8,4], marker_color=RED, hovertemplate="%{x}: ~%{y}%<extra></extra>"))
        fig.update_layout(**LAYOUT, height=290, showlegend=False, yaxis=dict(title="% das reclamações", gridcolor=BORDER, tickfont=dict(color=MUTED)), xaxis=dict(tickangle=-20, tickfont=dict(size=10, color=NAVY)), margin=dict(t=10,b=80))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown(f"<h3 style='color:{NAVY}'>Octalink · Octalink Tecnologia LTDA</h3>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Fundação","Dez/2017","Sumaré, SP"); c2.metric("Modelo","Bootstrap","100% capital próprio, 8 anos")
        c3.metric("Grant FINEP","R$10M","Fundo perdido aprovado"); c4.metric("Crescimento histórico","~20%/ano","6 anos só por indicação")
        st.divider()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Tamanho estimado","15–40 func.","Dev reduzida com IA"); c2.metric("Marketing digital","Out/2024","Antes: 100% indicação")
        c3.metric("Novas vendas (3 meses)","R$850k","Após início do marketing"); c4.metric("Avaliações independentes","ZERO","Sem Capterra, G2, RA")
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Fundadores e Origem</h4>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:14px 18px;border-radius:6px;font-size:0.85rem;color:#2a3a4a;line-height:1.8">
        • <b>Daniel Stavale</b> — CEO. Background finance/controlling em grandes empresas e escritório de contabilidade com 140 funcionários.<br/>
        • <b>Fernando Stavale</b> — Co-fundador / Tecnologia · Sumaré, SP<br/>
        • Iniciou em 2015 como overlay de BI sobre ERPs existentes (SAP, TOTVS). ERP Aurora veio depois.<br/>
        • A camada de controladoria é o produto mais maduro. ERP operacional é mais recente.
        </div>""", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Arquitetura da Plataforma</h4>", unsafe_allow_html=True)
        cols = st.columns(4)
        for col, (mod, col_hex, desc) in zip(cols, [
            ("ERP Aurora", BLUE, "NF-e/CT-e/NFS-e, almoxarifado, OP com BOM, conciliação Open Finance. Produto mais novo."),
            ("CRM", GOLD, "Pipeline de vendas, rastreamento de leads por canal, QR Code, agentes de IA no WhatsApp."),
            ("Controladoria + BI", NAVY, "Produto mais maduro (desde 2015). Fluxo tripartite, DRE, budget vs real, centros de custo, drilldown até documento."),
            ("IA + Vibe Coding", "#b05a20", "Regras contábeis por IA (beta). Data lake + Lovable para dashboards. Cursor internamente."),
        ]):
            with col:
                st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};border-top:3px solid {col_hex};padding:14px;border-radius:6px;text-align:center">
                  <div style="color:{col_hex};font-weight:700;font-size:0.85rem;margin-bottom:6px">{mod}</div>
                  <div style="color:{MUTED};font-size:0.78rem;line-height:1.5">{desc}</div>
                </div>""", unsafe_allow_html=True)
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Mix de Clientes (Confirmado na Apresentação)</h4>", unsafe_allow_html=True)
        fig_mix = go.Figure(go.Pie(labels=["Prestação de Serviços","Comércio","Indústria"], values=[84,8,8], marker_colors=[BLUE,GOLD,RED], hole=0.45, hovertemplate="%{label}: %{value}%<extra></extra>", textinfo="label+percent", textfont=dict(size=11)))
        fig_mix.update_layout(**LAYOUT, height=300, showlegend=False, margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig_mix, use_container_width=True)
        st.caption("Fonte: dados de pipeline compartilhados pelo CEO na apresentação de março/2026. 75% Simples Nacional · 15% Lucro Presumido.")
        st.divider()
        st.markdown(f"<h4 style='color:{NAVY}'>Posicionamento — As Três Ondas do Mercado de ERP</h4>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:{BG2};border:1px solid {BORDER};padding:16px 20px;border-radius:8px;font-size:0.85rem;color:#2a3a4a;line-height:1.9">
        <b>1ª Onda</b> — SAP, TOTVS Proteus (R$6B/ano), JD Edwards, NetSuite. Implantações de R$100k–300k+.<br/>
        <b>2ª Onda</b> — Conta Azul (vendida por R$1,7B), Omie (US$100M/ano), Excel. Foco em microempresas.<br/>
        <b>3ª Onda (Octalink)</b> — Agilidade do pequeno + robustez do grande. 20–30× mais barato que enterprise. Foco R$4M–R$10M.<br/>
        <b>Modelo complementar:</b> Para grandes empresas com SAP/TOTVS, Octalink atua como camada de controladoria — não substituição. Ex: empresa R$2B/3.500 func. + Amadeus (multinacional espanhola).
        </div>""", unsafe_allow_html=True)