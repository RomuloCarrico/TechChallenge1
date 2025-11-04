from fastapi import APIRouter
from models import HealthStatus
from utils import BOOKS_DATA

router = APIRouter(
    prefix="/v1/health",
    tags=["Saúde"],
)

# GET no /api/v1/health - verifica o status da api e conectividade com os dados
@router.get("/", response_model=HealthStatus, summary="Verifica o status da API e conectividade com os dados")
async def health_check():
    # Verifica se os dados foram carregados (lista não vazia)
    data_status = "ok" if BOOKS_DATA else "erro (dados não carregados)"
    
    return HealthStatus(
        status="online",
        data_source=data_status
    )