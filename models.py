from pydantic import BaseModel

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