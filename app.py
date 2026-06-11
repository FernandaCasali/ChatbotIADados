import streamlit as st
import pandas as pd
import plotly.express as px
from agent import create_agent, query
import sqlite3
import json
import re

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="DataChat AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS customizado (visual profissional) ───────────────────────────
st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .sql-box {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 12px 16px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
    }
    .tag {
        display: inline-block;
        background: #e8f4fd;
        color: #1a6fa3;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Agente (cache para não recriar a cada interação) ────────────────
@st.cache_resource
def get_agent():
    return create_agent()

# ── Helpers ─────────────────────────────────────────────────────────
def get_db_stats():
    """Retorna métricas rápidas do banco para o sidebar."""
    conn = sqlite3.connect("vendas.db")
    total   = pd.read_sql("SELECT COUNT(*) as n FROM vendas", conn).iloc[0,0]
    receita = pd.read_sql("SELECT SUM(total) as r FROM vendas", conn).iloc[0,0]
    prods   = pd.read_sql("SELECT COUNT(DISTINCT produto) as p FROM vendas", conn).iloc[0,0]
    conn.close()
    return total, receita, prods

def try_render_chart(resposta: str):
    """
    Tenta extrair uma tabela da resposta e plotar um gráfico.
    Funciona quando o LLM retorna dados em formato de tabela markdown.
    """
    lines = [l.strip() for l in resposta.split("\n") if "|" in l and "---" not in l]
    if len(lines) < 2:
        return

    try:
        header = [c.strip() for c in lines[0].split("|") if c.strip()]
        rows   = [[c.strip() for c in l.split("|") if c.strip()] for l in lines[1:]]
        df = pd.DataFrame(rows, columns=header)

        # Tenta converter colunas numéricas
        for col in df.columns:
            df[col] = df[col].str.replace(r"[R$\s.]", "", regex=True).str.replace(",", ".")
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass

        num_cols = df.select_dtypes(include="number").columns.tolist()
        str_cols = df.select_dtypes(exclude="number").columns.tolist()

        if num_cols and str_cols:
            st.divider()
            chart_type = st.selectbox(
                "Visualização automática",
                ["Barra", "Pizza", "Linha"],
                key=f"chart_{len(st.session_state.messages)}"
            )
            if chart_type == "Barra":
                fig = px.bar(df, x=str_cols[0], y=num_cols[0],
                             color_discrete_sequence=["#4C78A8"])
            elif chart_type == "Pizza":
                fig = px.pie(df, names=str_cols[0], values=num_cols[0])
            else:
                fig = px.line(df, x=str_cols[0], y=num_cols[0], markers=True)

            fig.update_layout(margin=dict(t=20, b=0), height=320)
            st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass  # Se falhar, só não mostra o gráfico

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 DataChat AI")
    st.caption("Análise de dados por linguagem natural")
    st.divider()

    # Métricas do banco
    with st.spinner("Carregando métricas..."):
        total, receita, prods = get_db_stats()

    st.markdown("**Base de dados**")
    col1, col2 = st.columns(2)
    col1.metric("Registros", f"{total:,}")
    col2.metric("Produtos", prods)
    st.metric("Receita total", f"R$ {receita:,.2f}")
    st.divider()

    # Perguntas exemplo por categoria
    st.markdown("**Perguntas sugeridas**")

    categorias = {
        "📈 Vendas": [
            "Qual produto mais vendido em 2024?",
            "Top 5 dias com maior faturamento?",
            "Evolução mensal da receita em 2024",
        ],
        "🗺️ Regiões": [
            "Qual região gerou mais receita?",
            "Compare vendas entre Sul e Sudeste",
            "Ranking de regiões por quantidade vendida",
        ],
        "👤 Vendedores": [
            "Top 3 vendedores por receita total",
            "Média de vendas por vendedor",
            "Qual vendedor vende mais eletrônicos?",
        ],
    }

    for categoria, perguntas in categorias.items():
        with st.expander(categoria):
            for p in perguntas:
                if st.button(p, key=p, use_container_width=True):
                    st.session_state.pergunta_rapida = p

    st.divider()

    # Configurações
    st.markdown("**Configurações**")
    show_sql = st.toggle("Mostrar SQL gerado", value=True)
    show_chart = st.toggle("Sugerir gráfico", value=True)

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# ÁREA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
st.title("💬 Converse com seus dados")
st.caption("Pergunte em português sobre qualquer métrica de vendas")

# Inicializa histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mensagem inicial
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "Olá! Sou seu analista de dados com IA. "
            "Pode me fazer perguntas como:\n\n"
            "- *Qual foi o produto mais vendido?*\n"
            "- *Me mostre as vendas por região*\n"
            "- *Quem foi o melhor vendedor em março?*"
        )

# Renderiza histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sql") and show_sql:
            with st.expander("Ver SQL gerado"):
                st.code(msg["sql"], language="sql")
        if msg.get("has_table") and show_chart:
            try_render_chart(msg["content"])

# ── Input do usuário ────────────────────────────────────────────────
pergunta = st.chat_input("Faça uma pergunta sobre os dados...")

# Preenche se clicou em pergunta sugerida
if "pergunta_rapida" in st.session_state:
    pergunta = st.session_state.pop("pergunta_rapida")

if pergunta:
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Processa com o agente
    with st.chat_message("assistant"):
        with st.spinner("Analisando... ⏳"):
            agent = get_agent()
            resposta = query(agent, pergunta)

        st.markdown(resposta)

        # Detecta se tem tabela para oferecer gráfico
        has_table = "|" in resposta and "---" in resposta

        # Tenta extrair o SQL dos logs internos do agente
        sql_gerado = None
        sql_match = re.search(r"```sql\n(.*?)```", resposta, re.DOTALL)
        if sql_match:
            sql_gerado = sql_match.group(1).strip()

        if sql_gerado and show_sql:
            with st.expander("Ver SQL gerado"):
                st.code(sql_gerado, language="sql")

        if has_table and show_chart:
            try_render_chart(resposta)

    # Salva no histórico com metadados
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta,
        "sql": sql_gerado,
        "has_table": has_table,
    })