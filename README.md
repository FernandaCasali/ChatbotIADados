# DataChat AI

Converse com uma base de vendas em **português** — o app traduz a pergunta em SQL,
executa numa base SQLite (modo somente leitura) e responde com tabela + gráfico.

Construído com **Streamlit** + **LangChain** + **Groq** (`llama-3.3-70b-versatile`).

## Stack

- `app.py` — interface Streamlit (chat, sidebar, render de tabela/gráfico)
- `agent.py` — agente SQL (LangChain + Groq) e tratamento de erros da API
- `database.py` — cria e popula `vendas.db` com 500 registros de exemplo
- `theme.py` — tema visual (CSS + componentes HTML)

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

Crie um `.env` (veja `.env.example`) com sua chave da Groq:

```
GROQ_API_KEY=...
```

Depois:

```bash
streamlit run app.py
```

> O banco `vendas.db` é criado e semeado automaticamente na primeira execução,
> então não é necessário rodar `database.py` manualmente.

No Windows há também o atalho `run.bat`.

## Deploy (Streamlit Community Cloud)

1. Suba o repositório no GitHub (o `.env` e o `*.db` ficam de fora pelo `.gitignore` —
   isso é esperado).
2. Em [share.streamlit.io](https://share.streamlit.io), aponte para `app.py`.
3. Em **Settings → Secrets**, adicione:
   ```
   GROQ_API_KEY = "sua_chave"
   ```
4. Deploy. O `vendas.db` é gerado no primeiro carregamento.

## Limites da API

A Groq aplica limites **por minuto** (TPM/RPM) e **por dia** (TPD/RPD). O app
diferencia os dois: perguntas pesadas podem atingir o limite por minuto
temporariamente — basta aguardar alguns segundos; isso **não** consome a cota diária.
