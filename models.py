from pydantic import BaseModel
from typing import List, Optional

# Modelo para o objeto Livro
class Livro(BaseModel):
    id: int
    titulo: str
    preco: float
    rating: int 
    disponibilidade: str
    categoria: str
    url_imagem: str
    

# Modelo para o status de saúde da API
class HealthStatus(BaseModel):
    status: str
    data_source: str

# Modelo para contagem de livros por Rating
class RatingDistribution(BaseModel):
    rating: int
    count: int

# Modelo para estatíticas gerais
class OverviewStats(BaseModel):
    total_livros: int
    preco_medio: float
    distribuicao_ratings: List[RatingDistribution]

# Modelo para estatísticas por categoria
class CategoryStats(BaseModel):
    categoria: str
    total_livros: int
    preco_medio: float

# Modelos de Token
class Token(BaseModel):
    """Modelo para o Access Token e o Refresh Token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    """Modelo para receber o refresh token."""
    refresh_token: str

class UserLogin(BaseModel):
    """Modelo para dados de login."""
    username: str
    password: str

# Modelo Pydantic para o usuário que foi autenticado
class AuthenticatedUser(BaseModel):
    username: str
    user_id: Optional[int] = None # Um ID seria usado em um DB real
