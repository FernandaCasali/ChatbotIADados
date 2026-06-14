"""
DataChat AI — tema visual + componentes (paleta terrosa, escuro).
Direção: layout editorial + tipografia Archivo / IBM Plex Mono.

Uso no app.py:
    import streamlit as st
    import theme
    st.set_page_config(page_title="DataChat AI", page_icon="📊", layout="wide")
    theme.inject()                      # injeta fontes + CSS (1x, no topo)
    ...
    theme.assistant(theme.answer_block(...))   # renderiza resposta rica

Todos os helpers retornam HTML (str). Use theme.html(...) para imprimir,
ou os atalhos theme.user(...) / theme.assistant(...).
"""
import re
import html as _html
import streamlit as st

# ── paleta ───────────────────────────────────────────────────────────
PALETTE = {
    "black": "#000000", "navy": "#1F3345", "terra": "#B54745",
    "gold": "#C78F57", "teal": "#85ABAB", "cream": "#F0EDE5",
}

# Cores para gráficos Plotly (caso você prefira manter o Plotly).
PLOTLY_SEQUENCE = ["#C78F57", "#85ABAB", "#B54745", "#1F3345", "#9FB8B8"]

# ── ícones (SVG inline) ──────────────────────────────────────────────
_BOT = ('<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">'
        '<path d="M12 2.2l1.9 6.4 6.4 1.9-6.4 1.9L12 18.8l-1.9-6.4L3.7 10.5l6.4-1.9z"/></svg>')
_USER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">'
         '<circle cx="12" cy="8" r="3.2"/><path d="M5 20c0-3.5 3.1-6 7-6s7 2.5 7 6"/></svg>')
_CHEV = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
         'stroke-linecap="round" width="14" height="14"><path d="M9 6l6 6-6 6"/></svg>')
_ALERT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
          'stroke-linecap="round" stroke-linejoin="round" width="22" height="22">'
          '<path d="M12 9v4M12 17h.01"/>'
          '<path d="M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>')

_MARK = ('<svg width="32" height="32" viewBox="0 0 36 36" fill="none">'
         '<rect width="36" height="36" rx="9" fill="#1F3345"/>'
         '<rect x="8.5" y="19" width="4.5" height="9" rx="1.5" fill="#85ABAB"/>'
         '<rect x="15.75" y="12.5" width="4.5" height="15.5" rx="1.5" fill="#C78F57"/>'
         '<rect x="23" y="8" width="4.5" height="20" rx="1.5" fill="#B54745"/></svg>')

# ════════════════════════════════════════════════════════════════════
#  CSS
# ════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
  --app-bg:#0A1016; --side-bg:#0C141C; --panel-bg:#152838; --panel-2:#0F2030;
  --line:rgba(240,237,229,0.10); --line-2:rgba(240,237,229,0.18);
  --text:#F0EDE5; --muted:rgba(240,237,229,0.56); --faint:rgba(240,237,229,0.32);
  --terra:#B54745; --gold:#C78F57; --teal:#85ABAB; --cream:#F0EDE5;
  --font-ui:'Archivo',system-ui,sans-serif; --font-mono:'IBM Plex Mono',monospace;
}

/* ---- base / tipografia ---- */
html, body, .stApp, [data-testid="stSidebar"],
input, textarea, button, .stMarkdown, [data-testid="stMetricValue"]{
  font-family:var(--font-ui) !important;
}
code, pre, kbd, .ds-code, .ds-bar-val, .ds-col-val, .ds-table .num{
  font-family:var(--font-mono) !important;
}
.stApp{ background:var(--app-bg); color:var(--text); }
.block-container{ padding-top:2.2rem; max-width:1060px; }
h1,h2,h3{ font-family:var(--font-ui) !important; letter-spacing:-.02em; }
h1{ font-weight:700 !important; font-size:2.6rem !important; }
::selection{ background:rgba(197,143,87,.30); }

/* ---- esconder cromo do Streamlit ---- */
[data-testid="stHeader"]{ background:transparent; }
#MainMenu, [data-testid="stToolbar"]{ visibility:hidden; }
footer{ visibility:hidden; }

/* ---- sidebar ---- */
[data-testid="stSidebar"]{ background:var(--side-bg); border-right:1px solid var(--line); }
[data-testid="stSidebar"] h2{ font-weight:700; letter-spacing:-.02em; }
[data-testid="stSidebar"] hr{ border-color:var(--line); }
[data-testid="stMetricLabel"]{ color:var(--muted) !important; font-size:.78rem !important; }
[data-testid="stMetricValue"]{ font-weight:700 !important; letter-spacing:-.01em; }
/* botões de pergunta sugerida */
.stButton button{
  background:transparent; border:1px solid var(--line); color:var(--muted);
  border-radius:9px; font-size:.82rem; text-align:left; justify-content:flex-start;
  padding:.55rem .8rem; transition:border-color .15s,color .15s;
}
.stButton button:hover{ border-color:var(--terra); color:var(--cream); }
[data-testid="stExpander"]{ border:1px solid var(--line); border-radius:10px; background:transparent; }
[data-testid="stExpander"] summary{ font-weight:600; }

/* ---- chat input ---- */
[data-testid="stChatInput"]{
  background:var(--panel-bg); border:1px solid var(--line-2); border-radius:14px;
}
[data-testid="stChatInput"] textarea{ color:var(--text); }
[data-testid="stChatInput"] textarea::placeholder{ color:var(--faint); }

/* ════════ COMPONENTES (HTML injetado) ════════ */
.ds-msg{ display:flex; gap:16px; margin:22px 0; }
.ds-av{ width:36px; height:36px; flex:0 0 36px; border-radius:9px;
  display:flex; align-items:center; justify-content:center; }
.ds-av-bot{ background:var(--terra); color:var(--cream); }
.ds-av-user{ background:var(--panel-bg); color:var(--teal); border:1px solid var(--line-2); }
.ds-body{ flex:1 1 auto; min-width:0; padding-top:5px; }
.ds-role{ font-family:var(--font-mono); font-size:11px; font-weight:600; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); margin-bottom:8px; }
.ds-text{ font-size:16px; line-height:1.6; color:var(--text); }
.ds-text strong{ color:var(--gold); font-weight:600; }
.ds-welcome{ margin:10px 0 0; padding-left:20px; }
.ds-welcome li{ margin:8px 0; color:var(--muted); }
.ds-welcome li em{ color:var(--text); font-style:italic; }
.ds-userq{ display:inline-block; background:var(--panel-bg); border:1px solid var(--line);
  padding:12px 18px; border-radius:12px; font-size:16px; color:var(--text); }

/* métricas */
.ds-metrics{ display:flex; gap:0; margin:22px 0 4px; }
.ds-metric{ flex:1; padding:2px 26px; border-left:1px solid var(--line); }
.ds-metric:first-child{ border-left:0; padding-left:0; }
.ds-metric-label{ font-size:12px; color:var(--muted); margin-bottom:9px; }
.ds-metric-value{ font-weight:700; font-size:34px; line-height:1; color:var(--gold);
  font-variant-numeric:tabular-nums; }
.ds-metric-value small{ font-size:16px; color:var(--muted); margin-left:4px; font-weight:600; }
.ds-metric-value.name{ font-size:26px; color:var(--text); }
.ds-metric-sub{ font-size:12px; color:var(--teal); margin-top:8px; }

/* card de resposta */
.ds-card-out{ margin-top:20px; border:1px solid var(--line); border-radius:14px;
  background:var(--panel-2); overflow:hidden; }
.ds-card-head{ display:flex; align-items:center; gap:10px; padding:14px 20px;
  border-bottom:1px solid var(--line); font-family:var(--font-mono); font-size:12px;
  font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.ds-pill{ margin-left:auto; font-size:11px; color:var(--teal); border:1px solid var(--line);
  border-radius:20px; padding:4px 11px; text-transform:none; letter-spacing:0; }

/* tabela */
.ds-table{ width:100%; border-collapse:collapse; font-size:14px; }
.ds-table th{ text-align:left; font-family:var(--font-mono); font-size:11px; font-weight:600;
  letter-spacing:.08em; text-transform:uppercase; color:var(--teal); padding:14px 20px;
  border-bottom:1px solid var(--line); }
.ds-table td{ padding:14px 20px; border-bottom:1px solid var(--line); color:var(--text); }
.ds-table tr:last-child td{ border-bottom:0; }
.ds-table .num{ text-align:right; font-variant-numeric:tabular-nums; }
.ds-table .rank{ color:var(--faint); width:30px; }
.ds-table tr.lead .name{ color:var(--gold); font-weight:600; }

/* gráfico de barras (horizontal) */
.ds-chart{ padding:20px; }
.ds-chart-title{ font-family:var(--font-mono); font-size:12px; color:var(--muted);
  margin-bottom:18px; letter-spacing:.04em; }
.ds-bar-row{ display:grid; grid-template-columns:130px 1fr 60px; align-items:center;
  gap:14px; margin:13px 0; }
.ds-bar-name{ font-size:13px; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ds-bar-track{ height:14px; background:rgba(240,237,229,.06); border-radius:3px; overflow:hidden; }
.ds-bar-fill{ height:100%; border-radius:3px; background:var(--teal); }
.ds-bar-row.lead .ds-bar-fill{ background:var(--gold); }
.ds-bar-val{ font-size:13px; color:var(--muted); text-align:right; }
.ds-bar-row.lead .ds-bar-val{ color:var(--gold); }

/* gráfico de colunas (vertical) */
.ds-col-chart{ padding:6px 24px 18px; }
.ds-col-chart-title{ font-family:var(--font-mono); font-size:12px; color:var(--muted);
  margin:14px 0 18px; letter-spacing:.04em; }
.ds-cols{ display:flex; align-items:flex-end; gap:26px; height:230px; }
.ds-col{ flex:1; height:100%; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; }
.ds-col-bar{ width:100%; max-width:78px; flex:1 1 auto; display:flex; align-items:flex-end; }
.ds-col-fill{ width:100%; border-radius:6px 6px 0 0; background:var(--teal); min-height:4px; }
.ds-col.lead .ds-col-fill{ background:var(--gold); }
.ds-col-val{ font-size:12px; color:var(--muted); margin-top:12px; white-space:nowrap; }
.ds-col.lead .ds-col-val{ color:var(--gold); }
.ds-col-name{ font-size:12px; color:var(--text); margin-top:5px; }

/* SQL */
.ds-sql{ border-top:1px solid var(--line); }
.ds-sql-head{ display:flex; align-items:center; gap:10px; padding:13px 20px;
  font-size:12px; color:var(--muted); font-weight:500; }
.ds-sql-head .ds-lang{ margin-left:auto; font-family:var(--font-mono); font-size:11px; color:var(--teal); }
.ds-code{ font-size:13px; line-height:1.7; padding:4px 20px 20px; color:#cdd6df;
  white-space:pre; overflow-x:auto; margin:0; }
.ds-code .kw{ color:var(--terra); } .ds-code .fn{ color:var(--gold); }
.ds-code .str{ color:var(--teal); } .ds-code .cm{ color:var(--faint); }

/* segmentado (tipo de gráfico) */
.ds-seg{ display:inline-flex; border:1px solid var(--line); border-radius:9px; padding:3px; gap:2px; }
.ds-seg span{ font-size:12px; padding:7px 16px; border-radius:6px; color:var(--muted); }
.ds-seg span.on{ background:var(--panel-bg); color:var(--text); box-shadow:inset 0 0 0 1px var(--line-2); }

/* chips */
.ds-chips-label{ margin:24px 0 12px; font-family:var(--font-mono); font-size:12px;
  color:var(--faint); letter-spacing:.06em; }
.ds-chips{ display:flex; flex-wrap:wrap; gap:10px; }
.ds-chip-q{ display:inline-flex; align-items:center; font-size:13px; color:var(--text);
  background:var(--panel-bg); border:1px solid var(--line-2); border-radius:22px; padding:10px 16px; }

/* chips clicáveis (st.button) */
.ds-chip-btn .stButton button{
  border-radius:22px !important; padding:10px 18px !important; font-size:13px !important;
  background:var(--panel-bg) !important; border:1px solid var(--line-2) !important;
  color:var(--text) !important; text-align:center !important; justify-content:center !important;
  width:auto !important;
}
.ds-chip-btn .stButton button:hover{ border-color:var(--gold) !important; color:var(--gold) !important; }

/* acessibilidade / foco */
a:focus-visible, button:focus-visible, [tabindex]:focus-visible,
.stButton button:focus-visible, [data-testid="stChatInput"] textarea:focus-visible{
  outline:2px solid var(--teal) !important; outline-offset:2px; }

/* tabela: hover de linha p/ leitura */
.ds-table tbody tr:hover{ background:rgba(240,237,229,0.04); }
.ds-table tbody tr.lead:hover{ background:rgba(199,143,87,0.06); }

/* scrollbar */
::-webkit-scrollbar{ width:10px; height:10px; }
::-webkit-scrollbar-thumb{ background:var(--panel-bg); border-radius:6px; border:1px solid var(--line); }
::-webkit-scrollbar-track{ background:transparent; }

/* ---- barra superior ---- */
.ds-topbar{ display:flex; align-items:center; gap:10px; padding:0 0 18px;
  font-size:13px; color:var(--muted); border-bottom:1px solid var(--line); margin-bottom:18px; }
.ds-topbar .dot{ width:8px; height:8px; border-radius:50%; background:var(--teal); flex:0 0 8px; }
.ds-topbar b{ color:var(--text); font-weight:600; }
.ds-topbar .sep{ color:var(--faint); }
.ds-topbar .spacer{ flex:1; }
.ds-topbar .model{ font-family:var(--font-mono); font-size:12px; color:var(--muted);
  border:1px solid var(--line); border-radius:20px; padding:5px 14px; }

/* ---- sidebar: categorias (estilo lista plana, igual ao mock) ---- */
[data-testid="stSidebar"] [data-testid="stExpander"]{
  border:0 !important; background:transparent !important; border-radius:0 !important;
  border-bottom:1px solid var(--line) !important; box-shadow:none !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] > div{
  border:0 !important; background:transparent !important; box-shadow:none !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary{
  font-weight:700; font-size:14.5px; padding:.85rem .15rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover{ color:var(--cream); }
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg{ color:var(--teal); }
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"]{
  padding:0 .15rem .5rem 2.0rem; }
/* sub-itens das categorias: texto simples alinhado à esquerda, sem caixa */
[data-testid="stSidebar"] [data-testid="stExpander"] .stButton button{
  border:0 !important; background:transparent !important; color:var(--muted) !important;
  padding:.32rem 0 !important; font-size:13px !important; border-radius:0 !important;
  text-align:left !important; justify-content:flex-start !important;
  box-shadow:none !important; min-height:auto !important; line-height:1.45 !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] .stButton button:hover{
  color:var(--gold) !important; border:0 !important; }

/* ---- toggles (Mostrar SQL / Sugerir gráfico) ---- */
[data-testid="stSidebar"] [data-testid="stToggle"] label p{ font-size:13px; color:var(--muted); }

/* responsivo */
@media (max-width: 640px){
  .ds-metrics{ flex-direction:column; gap:18px; }
  .ds-metric{ border-left:0; padding-left:0; padding-bottom:12px; border-bottom:1px solid var(--line); }
  .ds-metric:last-child{ border-bottom:0; }
  .ds-bar-row{ grid-template-columns:90px 1fr 50px; gap:8px; }
  .ds-cols{ gap:10px; }
  h1{ font-size:1.9rem !important; }
}

/* erro */
.ds-error{ display:flex; gap:14px; align-items:flex-start; border:1px solid rgba(181,71,69,.42);
  background:rgba(181,71,69,.09); border-radius:14px; padding:18px 20px; }
.ds-error .ds-err-ico{ color:var(--terra); flex:0 0 22px; margin-top:1px; }
.ds-err-title{ font-weight:600; color:var(--text); font-size:15px; margin-bottom:6px; }
.ds-err-body{ color:var(--muted); font-size:14px; line-height:1.55; }
.ds-err-body code{ font-family:var(--font-mono); font-size:12.5px; color:var(--teal);
  background:rgba(133,171,171,.1); padding:1px 6px; border-radius:5px; }

/* thinking */
.ds-typing{ display:inline-flex; gap:7px; align-items:center; padding:6px 0 4px; }
.ds-typing i{ width:8px; height:8px; border-radius:50%; background:var(--teal); display:block;
  animation:ds-dot 1.2s infinite ease-in-out; }
.ds-typing i:nth-child(2){ animation-delay:.16s; } .ds-typing i:nth-child(3){ animation-delay:.32s; }
@keyframes ds-dot{ 0%,70%,100%{opacity:.25;transform:translateY(0);} 35%{opacity:1;transform:translateY(-4px);} }
.ds-thinking-label{ font-size:13px; color:var(--muted); margin:10px 0 2px; }
</style>
"""


# ════════════════════════════════════════════════════════════════════
#  API
# ════════════════════════════════════════════════════════════════════
def inject():
    """Injeta fontes + CSS. Chame 1x, logo após set_page_config."""
    st.markdown(CSS, unsafe_allow_html=True)


def html(block: str):
    """Imprime um bloco HTML."""
    st.markdown(block, unsafe_allow_html=True)


def sidebar_brand() -> str:
    """Logo + nome + tagline (sem emoji) para o topo da sidebar."""
    return (f'<div style="display:flex;align-items:center;gap:12px;margin:2px 0 14px">'
            f'{_MARK}<span style="font-size:20px;font-weight:700;letter-spacing:-.02em;'
            f'color:var(--text)">DataChat AI</span></div>'
            f'<div style="color:var(--muted);font-size:13px;line-height:1.45">'
            f'Análise de dados de vendas por linguagem natural</div>')


def topbar(db_name: str, n_rows: int, n_cols: int, model: str) -> str:
    """Barra superior: status de conexão + modelo em uso."""
    n_rows_fmt = f"{n_rows:,}".replace(",", ".")
    return (f'<div class="ds-topbar"><span class="dot"></span>'
            f'Conectado a <b>{_e(db_name)}</b>'
            f'<span class="sep">·</span>{n_rows_fmt} registros · {n_cols} colunas'
            f'<span class="spacer"></span><span class="model">{_e(model)}</span></div>')


def eyebrow(t: str) -> str:
    """Rótulo de seção em mono/teal (igual ao mock)."""
    return (f'<div style="font-family:var(--font-mono);font-size:11px;font-weight:600;'
            f'letter-spacing:.16em;text-transform:uppercase;color:var(--teal);'
            f'margin:8px 0 4px">{_e(t)}</div>')


def _e(s):  # escape
    return _html.escape(str(s))


# ---- mensagens ------------------------------------------------------
def user(text: str):
    html(f'<div class="ds-msg ds-msg-user"><div class="ds-av ds-av-user">{_USER}</div>'
         f'<div class="ds-body"><div class="ds-role">Você</div>'
         f'<div class="ds-userq">{_e(text)}</div></div></div>')


def assistant(inner_html: str, role: str = "Analista IA"):
    html(f'<div class="ds-msg ds-msg-bot"><div class="ds-av ds-av-bot">{_BOT}</div>'
         f'<div class="ds-body"><div class="ds-role">{_e(role)}</div>{inner_html}</div></div>')


def text(t: str) -> str:
    return f'<div class="ds-text">{t}</div>'


def welcome() -> str:
    return (
        '<div class="ds-text">Olá! Sou seu analista de dados. Posso responder perguntas como:'
        '<ul class="ds-welcome">'
        '<li><em>Qual foi o produto mais vendido?</em></li>'
        '<li><em>Me mostre as vendas por região</em></li>'
        '<li><em>Quem foi o melhor vendedor em março?</em></li>'
        '</ul></div>')


# ---- métricas -------------------------------------------------------
def metrics(items) -> str:
    """items: lista de dicts {label, value, unit?, sub?, is_name?}"""
    cells = []
    for m in items:
        cls = "ds-metric-value name" if m.get("is_name") else "ds-metric-value"
        unit = f'<small>{_e(m["unit"])}</small>' if m.get("unit") else ""
        sub = f'<div class="ds-metric-sub">{_e(m["sub"])}</div>' if m.get("sub") else ""
        cells.append(
            f'<div class="ds-metric"><div class="ds-metric-label">{_e(m["label"])}</div>'
            f'<div class="{cls}">{_e(m["value"])}{unit}</div>{sub}</div>')
    return f'<div class="ds-metrics">{"".join(cells)}</div>'


# ---- tabela ---------------------------------------------------------
def table(headers, rows, numeric_cols=(), lead_row=0) -> str:
    """headers: lista de str. rows: lista de listas. numeric_cols: índices
    alinhados à direita (mono). lead_row: índice da linha em destaque (ou None)."""
    ths = ['<th class="rank">#</th>']
    for i, h in enumerate(headers):
        ths.append(f'<th class="{"num" if i in numeric_cols else ""}">{_e(h)}</th>')
    trs = []
    for r, row in enumerate(rows):
        lead = " lead" if r == lead_row else ""
        tds = [f'<td class="rank">{r + 1}</td>']
        for i, cell in enumerate(row):
            cls = "num" if i in numeric_cols else ("name" if i == 0 else "")
            tds.append(f'<td class="{cls}">{_e(cell)}</td>')
        trs.append(f'<tr class="{lead.strip()}">{"".join(tds)}</tr>')
    return (f'<table class="ds-table"><thead><tr>{"".join(ths)}</tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table>')


# ---- gráficos -------------------------------------------------------
def bar_chart(title, rows, lead_row=0) -> str:
    """Barras horizontais. rows: lista de (nome, valor_exibido, valor_numerico)."""
    nums = [float(x[2]) for x in rows] or [1]
    mx = max(nums) or 1
    out = [f'<div class="ds-chart"><div class="ds-chart-title">{_e(title)}</div>']
    for i, (name, disp, val) in enumerate(rows):
        lead = " lead" if i == lead_row else ""
        w = max(2, round(float(val) / mx * 100))
        out.append(
            f'<div class="ds-bar-row{lead}"><div class="ds-bar-name">{_e(name)}</div>'
            f'<div class="ds-bar-track"><div class="ds-bar-fill" style="width:{w}%"></div></div>'
            f'<div class="ds-bar-val">{_e(disp)}</div></div>')
    out.append('</div>')
    return "".join(out)


def column_chart(title, rows, lead_row=0, switcher=None) -> str:
    """Colunas verticais. rows: (nome, valor_exibido, valor_numerico).
    switcher: lista p/ o segmentado, ex. ['Barra','Pizza','Linha'] (1º = ativo)."""
    nums = [float(x[2]) for x in rows] or [1]
    mx = max(nums) or 1
    cols = []
    for i, (name, disp, val) in enumerate(rows):
        lead = " lead" if i == lead_row else ""
        h = max(3, round(float(val) / mx * 100))
        cols.append(
            f'<div class="ds-col{lead}"><div class="ds-col-bar">'
            f'<div class="ds-col-fill" style="height:{h}%"></div></div>'
            f'<div class="ds-col-val">{_e(disp)}</div><div class="ds-col-name">{_e(name)}</div></div>')
    seg = ""
    if switcher:
        spans = "".join(f'<span class="{"on" if j == 0 else ""}">{_e(s)}</span>'
                        for j, s in enumerate(switcher))
        seg = f'<div style="display:flex;justify-content:flex-end;margin:-4px 0 4px"><div class="ds-seg">{spans}</div></div>'
    return (f'<div class="ds-col-chart">{seg}<div class="ds-col-chart-title">{_e(title)}</div>'
            f'<div class="ds-cols">{"".join(cols)}</div></div>')


# ---- SQL ------------------------------------------------------------
_SQL_KW = (r"\b(SELECT|FROM|WHERE|GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT|JOIN|LEFT|"
           r"RIGHT|INNER|OUTER|ON|AS|AND|OR|NOT|IN|IS|NULL|DESC|ASC|DISTINCT|"
           r"BETWEEN|LIKE|UNION|CASE|WHEN|THEN|ELSE|END)\b")
_SQL_FN = r"\b(SUM|COUNT|AVG|MIN|MAX|ROUND|COALESCE|CAST|DATE|STRFTIME|UPPER|LOWER)\b"


def highlight_sql(sql: str) -> str:
    out = []
    for line in _e(sql).split("\n"):
        s = line.lstrip()
        if s.startswith("--"):
            out.append(f'<span class="cm">{line}</span>')
            continue
        line = re.sub(r"&#x27;([^&]*?)&#x27;", r'<span class="str">&#x27;\1&#x27;</span>', line)
        line = re.sub(_SQL_FN, r'<span class="fn">\1</span>', line, flags=re.I)
        line = re.sub(_SQL_KW, r'<span class="kw">\1</span>', line, flags=re.I)
        out.append(line)
    return "\n".join(out)


def sql_block(sql: str, open: bool = False) -> str:
    code = f'<pre class="ds-code">{highlight_sql(sql)}</pre>' if open else ""
    return (f'<div class="ds-sql"><div class="ds-sql-head">{_CHEV}'
            f'Ver SQL gerado<span class="ds-lang">SQL</span></div>{code}</div>')


# ---- card (junta tabela + gráfico + sql) ----------------------------
def card(head, *blocks, pill=None) -> str:
    pill_html = f'<span class="ds-pill">{_e(pill)}</span>' if pill else ""
    return (f'<div class="ds-card-out"><div class="ds-card-head">{_e(head)}{pill_html}</div>'
            f'{"".join(blocks)}</div>')


# ---- chips / erro / thinking ---------------------------------------
def chips(items, label="COMECE POR AQUI") -> str:
    cs = "".join(f'<span class="ds-chip-q">{_e(c)}</span>' for c in items)
    return f'<div class="ds-chips-label">{_e(label)}</div><div class="ds-chips">{cs}</div>'


def error_box(title, body_html) -> str:
    return (f'<div class="ds-error"><span class="ds-err-ico">{_ALERT}</span>'
            f'<div><div class="ds-err-title">{_e(title)}</div>'
            f'<div class="ds-err-body">{body_html}</div></div></div>')


def thinking(label="Interpretando a pergunta e gerando a consulta SQL…") -> str:
    return (f'<div class="ds-typing"><i></i><i></i><i></i></div>'
            f'<div class="ds-thinking-label">{_e(label)}</div>')


# ---- Plotly opcional (caso prefira manter os gráficos do Plotly) ----
def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Archivo, sans-serif", color="#F0EDE5", size=13),
        colorway=PLOTLY_SEQUENCE, margin=dict(t=20, b=10, l=10, r=10), height=320,
    )
    fig.update_xaxes(gridcolor="rgba(240,237,229,0.08)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(240,237,229,0.08)", zeroline=False)
    return fig
