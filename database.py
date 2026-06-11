import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def create_and_seed():
    conn = sqlite3.connect("vendas.db")

    conn.execute("DROP TABLE IF EXISTS vendas")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY,
            data TEXT,
            produto TEXT,
            categoria TEXT,
            quantidade INTEGER,
            preco_unitario REAL,
            total REAL,
            regiao TEXT,
            vendedor TEXT
        )
    """)
    
    produtos = [
        ("Notebook Dell", "Eletrônicos"), ("iPhone 14", "Eletrônicos"),
        ("Cadeira Gamer", "Móveis"), ("Monitor 4K", "Eletrônicos"),
        ("Mesa Escritório", "Móveis"), ("Headset Sony", "Eletrônicos"),
        ("Teclado Mecânico", "Periféricos"), ("Mouse Logitech", "Periféricos"),
    ]
    regioes = ["Sul", "Norte", "Sudeste", "Nordeste", "Centro-Oeste"]
    vendedores = ["Ana Silva", "Bruno Costa", "Carla Melo", "Diego Rocha"]
    
    rows = []
    for i in range(500):
        prod, cat = random.choice(produtos)
        preco = round(random.uniform(50, 5000), 2)
        qtd = random.randint(1, 20)
        data = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        rows.append((
            data.strftime("%Y-%m-%d"), prod, cat, qtd,
            preco, round(preco * qtd, 2),
            random.choice(regioes), random.choice(vendedores)
        ))
    
    conn.executemany("""
        INSERT INTO vendas (data, produto, categoria, quantidade, 
                           preco_unitario, total, regiao, vendedor)
        VALUES (?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()
    conn.close()
    print("Banco criado com 500 registros!")

if __name__ == "__main__":
    create_and_seed()