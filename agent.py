import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq

load_dotenv()

def create_agent():
    # Conexão READ-ONLY: o agente executa SQL gerado pelo LLM, então bloqueamos
    # qualquer escrita (DROP/DELETE/UPDATE) abrindo o banco em modo somente leitura.
    # sample_rows_in_table_info=0 economiza tokens (não envia linhas de exemplo).
    db = SQLDatabase.from_uri(
        "sqlite:///file:vendas.db?mode=ro&uri=true",
        sample_rows_in_table_info=0,
    )

    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
    
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        max_iterations=6,
        agent_executor_kwargs={"handle_parsing_errors": True},
        prefix="""Você é um analista de dados especialista em SQL.

A tabela se chama `vendas` e possui as colunas:
id, data, produto, categoria, quantidade, preco_unitario, total, regiao, vendedor.

Use SEMPRE essa tabela diretamente — não perca consultas listando tabelas ou
inspecionando o schema, pois ele já está descrito acima.

Responda sempre em português brasileiro.
Quando apresentar valores monetários, use o formato R$ X.XXX,XX.
Seja direto e objetivo e resolva com UMA única consulta SQL sempre que possível.
Apresente os dados em formato de tabela markdown.

Para perguntas de ranking ("quem mais", "qual o melhor", "top", "mais vende"),
NÃO retorne apenas o 1º colocado: traga os 4 ou 5 primeiros, ordenados, em uma
tabela markdown, com as colunas numéricas relevantes para comparação."""
    )
    return agent

def query(agent, pergunta: str) -> str:
    try:
        result = agent.invoke({"input": pergunta})
        return result["output"]
    except Exception as e:
        msg = str(e)
        low = msg.lower()

        is_rate_limit = "rate_limit" in low or "rate limit" in low or "error code: 429" in low
        # O Groq devolve 429 para limites POR DIA (TPD/RPD) e POR MINUTO (TPM/RPM).
        # Só é "limite diário" se a mensagem realmente citar o ciclo diário.
        is_daily = any(k in low for k in ("per day", "tpd", "rpd", "tokens per day",
                                          "requests per day", "daily"))
        # Pergunta pesada estoura contexto/payload — não é falta de cota.
        is_too_big = ("context_length" in low or "context length" in low
                      or "request too large" in low or "error code: 413" in low
                      or "reduce the length" in low)

        if is_rate_limit and is_daily:
            return ("ERRO_LIMITE_DIARIO: O limite DIÁRIO de tokens da API Groq foi atingido. "
                    "Ele renova à meia-noite (UTC). Troque a chave/modelo no .env para "
                    "continuar agora.")
        if is_rate_limit:
            return ("ERRO_LIMITE_MINUTO: Muitas requisições em pouco tempo (limite por "
                    "minuto da API Groq). Aguarde alguns segundos e tente de novo — a "
                    "cota diária NÃO foi atingida.")
        if is_too_big:
            return ("ERRO_TAMANHO: A pergunta gerou um contexto grande demais para o "
                    "modelo. Tente reformular de forma mais específica ou objetiva.")
        return f"Erro ao processar a pergunta: {msg}"