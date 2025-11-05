from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import Livro
from utils import BOOKS_DATA

router = APIRouter(
    prefix="/v1/books",
    tags=["Livros"],
)

# Lista todos os livros
@router.get("/", response_model=List[Livro], summary="Lista todos os livros disponíveis")
async def get_all_books():
    return BOOKS_DATA

# Busca livros por categoria e/ou titulo
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

# Livros com melhor avaliação
@router.get("/top-rated", response_model=List[Livro], summary="Lista os livros com a melhor avaliação (Rating 5)")
async def get_top_rated_books():
    """
    Retorna todos os livros que possuem a avaliação máxima (rating 5).
    """
    # Filtra livros com rating 5
    top_rated = [book for book in BOOKS_DATA if book['rating'] == 5]
    
    if not top_rated:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado com avaliação máxima (5)")
        
    return top_rated

# Filtra os livros por faixa de preço
@router.get("/price-range", response_model=List[Livro], summary="Filtra livros por faixa de preço")
async def get_books_by_price_range(
    min: float = Query(0.0, description="Preço mínimo (inclusivo)"),
    max: Optional[float] = Query(None, description="Preço máximo (inclusivo)")
):
    """
    Filtra os livros cuja faixa de preço se encaixa entre 'min' e 'max'.
    O valor 'max' padrão é infinito para pegar todos os livros acima do 'min' se o 'max' não for especificado.
    """

    # Incluindo o valor infinto como padrão do valor máximo, caso não seja usado nenhum
    max_inf = max if max is not None else float('inf')
    if min >= max_inf:
        raise HTTPException(status_code=400, detail="O valor 'min' deve ser menor que o valor 'max'")
    
    results = [
        book for book in BOOKS_DATA
        if min <= book['preco'] <= max_inf
    ]
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado na faixa de preço de £{min:.2f} a £{max_inf:.2f}")
        
    return results

# Retorna detalhes de um livro pelo ID
@router.get("/{book_id}", response_model=Livro, summary="Retorna detalhes de um livro pelo ID")
async def get_book_by_id(book_id: int):
    # Busca o livro na lista pelo ID
    book = next((book for book in BOOKS_DATA if book['id'] == book_id), None)
    
    if book is None:
        # Se o livro não for encontrado, retorna 404 Not Found
        raise HTTPException(status_code=404, detail=f"Livro com ID {book_id} não encontrado")
        
    return book
