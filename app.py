"""
DataChat AI — app Streamlit com o tema novo.
Coloque junto de theme.py, agent.py, database.py e vendas.db.
Rode:  streamlit run app.py
"""
import re
import sqlite3
import pandas as pd
import streamlit as st

import theme
from agent import create_agent, query

# ── página ───────────────────────────────────────────────────────────
st.set_page_config(page_title="DataChat AI", page_icon=":material/insights:",
                   layout="wide", initial_sidebar_state="expanded")
theme.inject()   # ← fontes + CSS (a única coisa que você precisa para o visual)


@st.cache_resource
def get_agent():
    return create_agent()


@st.cache_data
def db_stats():
    conn = sqlite3.connect("vendas.db")
    total = pd.read_sql("SELECT COUNT(*) n FROM vendas", conn).iloc[0, 0]
    receita = pd.read_sql("SELECT SUM(total) r FROM vendas", conn).iloc[0, 0]
    prods = pd.read_sql("SELECT COUNT(DISTINCT produto) p FROM vendas", conn).iloc[0, 0]
    cols = pd.read_sql("PRAGMA table_info(vendas)", conn).shape[0]
    conn.close()
    return total, receita, prods, cols


def parse_md_table(txt: str):
    """Extrai um DataFrame de uma tabela markdown na resposta do agente."""
    lines = [l.strip() for l in txt.split("\n") if "|" in l and "---" not in l]
    if len(lines) < 2:
        return None
    header = [c.strip() for c in lines[0].split("|") if c.strip()]
    rows = [[c.strip() for c in l.split("|") if c.strip()] for l in lines[1:]]
    rows = [r for r in rows if len(r) == len(header)]
    if not rows:
        return None
    return pd.DataFrame(rows, columns=header)


def to_number(series: pd.Series):
    cleaned = (series.astype(str)
               .str.replace(r"[R$\s.]", "", regex=True)
               .str.replace(",", ".", regex=False))
    return pd.to_numeric(cleaned, errors="coerce")


def render_answer(resposta: str, sql: str | None = None, show_chart: bool = True):
    """Renderiza a resposta do agente com o visual DataChat (tabela + gráfico)."""
    df = parse_md_table(resposta)
    # texto antes da tabela
    head_txt = resposta.split("|")[0].strip() if df is not None else resposta.strip()
    inner = theme.text(head_txt.replace("\n", "<br>")) if head_txt else ""

    blocks = []
    if df is not None:
        num_idx = [i for i, c in enumerate(df.columns) if to_number(df[c]).notna().all()]
        # tabela
        blocks.append(theme.table(df.columns.tolist(), df.values.tolist(),
                                  numeric_cols=set(num_idx), lead_row=0))
        # gráfico: 1ª coluna texto + 1ª coluna numérica
        str_idx = [i for i in range(len(df.columns)) if i not in num_idx]
        if show_chart and num_idx and str_idx:
            li, vi = str_idx[0], num_idx[0]
            rows = [(df.iloc[r, li], df.iloc[r, vi], to_number(df[df.columns[vi]]).iloc[r])
                    for r in range(len(df))]
            rows = [r for r in rows if pd.notna(r[2])]
            if rows:
                lead = max(range(len(rows)), key=lambda k: rows[k][2])
                blocks.append(theme.bar_chart(df.columns[vi], rows, lead_row=lead))
    if sql:
        blocks.append(theme.sql_block(sql, open=False))

    body = inner + (theme.card("Resultado", *blocks, pill=f"{len(df)} linhas")
                    if blocks else "")
    theme.assistant(body)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR  (nativo = funcional; o CSS cuida do visual)
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    theme.html(theme.sidebar_brand())
    st.divider()

    total, receita, prods, n_cols = db_stats()
    theme.html(theme.eyebrow("Base de dados"))
    c1, c2 = st.columns(2)
    c1.metric("Registros", f"{total:,}".replace(",", "."))
    c2.metric("Produtos", prods)
    theme.html(theme.metrics([
        {"label": "Receita total", "value": f"R$ {receita:,.0f}".replace(",", ".")}
    ]))
    st.divider()

    theme.html(theme.eyebrow("Perguntas sugeridas"))
    categorias = {
        "Vendas": (":material/trending_up:",
                   ["Qual produto mais vendido em 2024?",
                    "Top 5 dias com maior faturamento", "Evolução mensal da receita"]),
        "Regiões": (":material/public:",
                    ["Qual região gerou mais receita?",
                     "Compare Sul e Sudeste", "Ranking por quantidade vendida"]),
        "Vendedores": (":material/groups:",
                       ["Top 3 vendedores por receita",
                        "Média de vendas por vendedor", "Qual vendedor vende mais eletrônicos?"]),
    }
    for cat, (icon, perguntas) in categorias.items():
        with st.expander(cat, icon=icon):
            for p in perguntas:
                if st.button(p, key=p, use_container_width=True):
                    st.session_state.pergunta_rapida = p

    st.divider()
    theme.html(theme.eyebrow("Configurações"))
    show_sql = st.toggle("Mostrar SQL gerado", value=True)
    show_chart = st.toggle("Sugerir gráfico", value=True)
    if st.button("Limpar conversa", icon=":material/delete:", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
#  ÁREA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
_total, _receita, _prods, _n_cols = db_stats()
theme.html(theme.topbar("vendas.db", _total, _n_cols, "llama-3.3-70b"))

st.title("Converse com seus dados")
st.caption("Pergunte em português sobre qualquer métrica de vendas — "
           "produtos, regiões, vendedores e períodos.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# estado vazio
if not st.session_state.messages:
    theme.assistant(theme.welcome())
    theme.html('<div class="ds-chips-label">COMECE POR AQUI</div>')
    sugestoes = ["Top produtos de 2024", "Receita por região",
                  "Melhor vendedor em março", "Ticket médio por categoria"]
    cols = st.columns(len(sugestoes))
    for col, s in zip(cols, sugestoes):
        with col:
            theme.html('<div class="ds-chip-btn">')
            if st.button(s, key=f"chip_{s}", use_container_width=True):
                st.session_state.pergunta_rapida = s
            theme.html('</div>')

# histórico
for msg in st.session_state.messages:
    if msg["role"] == "user":
        theme.user(msg["content"])
    else:
        render_answer(msg["content"], msg.get("sql") if show_sql else None, show_chart)

# ── input ───────────────────────────────────────────────────────────
pergunta = st.chat_input("Faça uma pergunta sobre os dados…")
if "pergunta_rapida" in st.session_state:
    pergunta = st.session_state.pop("pergunta_rapida")

if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})
    theme.user(pergunta)

    placeholder = st.empty()
    with placeholder.container():
        theme.assistant(theme.thinking())   # estado "pensando"

    resposta = query(get_agent(), pergunta)
    sql_match = re.search(r"```sql\n(.*?)```", resposta, re.DOTALL)
    sql = sql_match.group(1).strip() if sql_match else None

    placeholder.empty()
    if resposta.lower().startswith("erro"):
        theme.assistant(theme.error_box(
            "Não consegui processar a pergunta",
            "Verifique se ela se refere a colunas existentes: "
            "<code>produto</code>, <code>categoria</code>, <code>regiao</code>, "
            "<code>vendedor</code>, <code>quantidade</code>, <code>preco_unitario</code>, "
            "<code>total</code>."))
    else:
        render_answer(resposta, sql if show_sql else None, show_chart)

    st.session_state.messages.append({"role": "assistant", "content": resposta, "sql": sql})
