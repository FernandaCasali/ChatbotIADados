import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq

load_dotenv()

def create_agent():
    db = SQLDatabase.from_uri("sqlite:///vendas.db")
    
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
    
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        max_iterations=8,
        early_stopping_method="generate",
        agent_executor_kwargs={"handle_parsing_errors": True},
        prefix="""Você é um analista de dados especialista em SQL.
Responda sempre em português brasileiro.
Quando apresentar valores monetários, use o formato R$ X.XXX,XX.
Seja direto e objetivo.
Resolva a pergunta com o menor número possível de consultas SQL (idealmente uma única).
Sempre que possível, apresente os dados em formato de tabela markdown."""
    )
    return agent

def query(agent, pergunta: str) -> str:
    try:
        result = agent.invoke({"input": pergunta})
        return result["output"]
    except Exception as e:
        return f"Erro ao processar a pergunta: {str(e)}"