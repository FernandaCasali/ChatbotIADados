import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq

load_dotenv()

def create_agent():
    # sample_rows_in_table_info=0 economiza tokens (não envia linhas de exemplo)
    db = SQLDatabase.from_uri("sqlite:///vendas.db", sample_rows_in_table_info=0)

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
        if "rate_limit" in msg or "429" in msg or "tokens per day" in msg.lower():
            return ("ERRO_LIMITE: O limite diário de tokens da API Groq foi atingido. "
                    "Aguarde alguns minutos ou troque o modelo/chave de API.")
        return f"Erro ao processar a pergunta: {msg}"