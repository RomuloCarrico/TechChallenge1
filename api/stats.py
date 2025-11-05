from fastapi import APIRouter
from typing import List
from models import OverviewStats, CategoryStats, RatingDistribution
from utils import BOOKS_DATA
import pandas as pd

router = APIRouter(
    prefix="/v1/stats",
    tags=["Estatísticas"],
)

# Estatísticas gerais
@router.get("/overview", response_model=OverviewStats, summary="Estatísticas gerais da coleção")
async def get_overview_stats():
    df = pd.DataFrame(BOOKS_DATA)
    if df.empty:
        return OverviewStats(total_livros=0, preco_medio=0.0, distribuicao_ratings=[])

    # Preço Médio
    preco_medio = df['preco'].mean().round(2)
    
    # Distribuição de Ratings
    rating_counts = df['rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['rating', 'count']
    
    # Preenche gaps, garantindo que ratings de 1 a 5 estejam sempre presentes
    full_ratings = pd.DataFrame({'rating': range(1, 6)})
    rating_counts = full_ratings.merge(rating_counts, on='rating', how='left').fillna(0)
    rating_counts['count'] = rating_counts['count'].astype(int)
    
    distribuicao_ratings = [
        RatingDistribution(**row) 
        for row in rating_counts.to_dict('records')
    ]
    
    return OverviewStats(
        total_livros=len(df),
        preco_medio=preco_medio,
        distribuicao_ratings=distribuicao_ratings
    )

# Estatísticas detalhadas por categorias
@router.get("/categories", response_model=List[CategoryStats], summary="Estatísticas detalhadas por categoria")
async def get_category_stats():
    df = pd.DataFrame(BOOKS_DATA)
    if df.empty:
        return []

    # Agrupa por categoria para calcular contagem e preço médio
    stats_df = df.groupby('categoria').agg(
        total_livros=('id', 'count'),
        preco_medio=('preco', 'mean')
    ).reset_index()
    
    # Formatação e renomeação
    stats_df['preco_medio'] = stats_df['preco_medio'].round(2)
    stats_df.rename(columns={'categoria': 'categoria'}, inplace=True)
    
    stats = [
        CategoryStats(**row)
        for row in stats_df.to_dict('records')
    ]
    
    return stats