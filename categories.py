from fastapi import APIRouter
from typing import List
from utils import BOOKS_DATA

router = APIRouter(
    prefix="/v1/categories",
    tags=["Categorias"],
)

# GET no /api/v1/categories - lista todas as categorias
@router.get("/", response_model=List[str], summary="Lista todas as categorias de livros disponíveis")
async def get_all_categories():
    # Usa um set para obter apenas categorias únicas, depois converte para lista
    categories = sorted(list({book['categoria'] for book in BOOKS_DATA}))
    return categories