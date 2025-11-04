from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import Livro
from utils import BOOKS_DATA

router = APIRouter(
    prefix="/v1/books",
    tags=["Livros"],
)

# GET no /api/v1/books - lista todos os livros
@router.get("/", response_model=List[Livro], summary="Lista todos os livros disponíveis")
async def get_all_books():
    return BOOKS_DATA

@router.get("/search", response_model=List[Livro], summary="Busca livros por título e/ou categoria")
async def search_books(
    title: Optional[str] = Query(None, description="Parte do título do livro para buscar"),
    category: Optional[str] = Query(None, description="Parte do nome da categoria do livro para buscar")
):
    try:
        if not title and not category:
            return BOOKS_DATA

        results = [
            book for book in BOOKS_DATA
            if (not title or title.lower() in book['titulo'].lower())
            and (not category or category.lower() in book['categoria'].lower())
        ]

        if not results:
            raise HTTPException(status_code=404, detail="Nenhum livro encontrado com os filtros fornecidos")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


# GET no /api/v1/books/{id} - retorna detalhes de um livro pelo ID
@router.get("/{book_id}", response_model=Livro, summary="Retorna detalhes de um livro pelo ID")
async def get_book_by_id(book_id: int):
    # Busca o livro na lista pelo ID
    book = next((book for book in BOOKS_DATA if book['id'] == book_id), None)
    
    if book is None:
        # Se o livro não for encontrado, retorna 404 Not Found
        raise HTTPException(status_code=404, detail=f"Livro com ID {book_id} não encontrado")
        
    return book
