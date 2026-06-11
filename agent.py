import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

def create_agent():
    db = SQLDatabase.from_uri("sqlite:///vendas.db")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": True},
        prefix="""Você é um analista de dados especialista em SQL.
Responda sempre em português brasileiro.
Quando apresentar valores monetários, use o formato R$ X.XXX,XX.
Seja direto e objetivo.
Sempre que possível, apresente os dados em formato de tabela markdown."""
    )
    return agent

def query(agent, pergunta: str) -> str:
    try:
        result = agent.invoke({"input": pergunta})
        return result["output"]
    except Exception as e:
        return f"Erro ao processar a pergunta: {str(e)}"