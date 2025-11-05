# Arquivo: api/scrap.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from models import AuthenticatedUser
from auth_utils import get_current_user
from datetime import datetime
import sys
import os
import importlib.util

router = APIRouter(
    prefix="/v1",
    tags=["Web Scraping"],
)

# Variável de estado global para a tarefa de scraping
scraping_status = {
    "running": False,
    "success": None, # True, False ou None (Não iniciado/Pendente)
    "last_run": None,
    "error_message": None
}

# --- Importação Dinâmica do runScraping ---
def import_run_scraping():
    """Importa dinamicamente a função runScraping do Script/webscrap.py."""
    
    # Caminho para o arquivo webscrap.py (assumindo que está em PROJECT_ROOT/Script/webscrap.py)
    SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Script", "webscrap.py")
    
    if not os.path.exists(SCRIPT_PATH):
        raise FileNotFoundError(f"Script de web scraping não encontrado em: {SCRIPT_PATH}")

    # Cria um spec de módulo e carrega
    spec = importlib.util.spec_from_file_location("scrapeBooks", SCRIPT_PATH)
    if spec is None:
        raise ImportError(f"Não foi possível carregar o spec do módulo em: {SCRIPT_PATH}")

    scrapeBooks = importlib.util.module_from_spec(spec)
    sys.modules["scrapeBooks"] = scrapeBooks
    spec.loader.exec_module(scrapeBooks)
    
    return scrapeBooks.runScraping

# --- Tarefa de Background (síncrona) ---
def scrapingTask(runScraping_func):
    """
    Função síncrona que executa o scraping e atualiza o status.
    Deve ser rodada em um threadpool.
    """
    try:
        scraping_status["running"] = True
        scraping_status["success"] = None
        scraping_status["error_message"] = None
        scraping_status["last_run"] = datetime.now().isoformat()

        # Chama a função runScraping importada
        runScraping_func()

        scraping_status["success"] = True

    except Exception as e:
        scraping_status["success"] = False
        scraping_status["error_message"] = str(e)
        print("Erro no scraping:", e)
    finally:
        scraping_status["running"] = False

# ----------------------------------------------------
# POST /api/v1/scrap - Inicia o webscrap (Assíncrono)
# ----------------------------------------------------
@router.post(
    "/scrap", 
    status_code=status.HTTP_202_ACCEPTED, 
    summary="Inicia a atualização do Web Scraping em segundo plano"
)
async def run_webscrap(
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Inicia o script de web scraping em uma tarefa de background, retornando 202 imediatamente.
    """
    if scraping_status["running"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tarefa de Web Scraping já está em execução. Verifique /v1/scrap_status."
        )

    try:
        runScraping_func = import_run_scraping()
    except (FileNotFoundError, ImportError) as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao carregar o script de scraping: {e}"
        )

    # Adiciona a tarefa síncrona ao BackgroundTasks, movendo-a para o threadpool.
    background_tasks.add_task(scrapingTask, runScraping_func)
    
    return {
        "message": "Atualização do Web Scraping iniciada em segundo plano. Status: 202 Accepted.",
        "status_endpoint": "/v1/scrap_status",
        "user": current_user.username
    }

# ----------------------------------------------------
# GET /api/v1/scrap_status - Verifica o status
# ----------------------------------------------------
@router.get(
    "/scrap_status", 
    summary="Verifica o status atual da tarefa de Web Scraping"
)
def get_scraping_status():
    """
    Retorna o estado atual da última execução do Web Scraping.
    """
    return {
        "running": scraping_status["running"],
        "success": scraping_status["success"],
        "last_run": scraping_status["last_run"],
        "error_message": scraping_status["error_message"]
    }