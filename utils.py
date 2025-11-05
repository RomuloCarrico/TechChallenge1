import pandas as pd
from typing import List, Dict, Any

DATA_PATH = "Data/Livros.csv"

def load_data() -> List[Dict[str, Any]]:
    """
    Carrega o arquivo CSV, pré-processa os dados e retorna uma lista de dicionários.
    """
    try:
        # Lê o CSV com cuidado: encoding, aspas e delimitador
        df = pd.read_csv(
            DATA_PATH,
            sep=",",
            quotechar='"',
            encoding="utf-8"
        )

        # Normaliza nomes de colunas
        df.columns = [
            'titulo', 'preco', 'rating', 'disponibilidade',
            'categoria', 'url_imagem'
        ]

        # Limpeza de dados
        df['preco'] = df['preco'].astype(float)
        df['rating'] = df['rating'].astype(int)
        df['disponibilidade'] = df['disponibilidade'].fillna("Indefinido")
        df['categoria'] = df['categoria'].fillna("Indefinido")
        df['url_imagem'] = df['url_imagem'].fillna("")

        # Adiciona ID sequencial
        df.insert(0, 'id', range(1, len(df) + 1))

        data = df.to_dict('records')
        return data

    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return []


# Carrega os dados uma única vez na inicialização
BOOKS_DATA = load_data()
