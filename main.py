from fastapi import FastAPI
from api import books, categories, health, stats, auth, scrap

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="Books to Scrape RESTful API",
    description="API de demonstração utilizando dados de web scraping do Books to Scrape.",
    version="1.0.0",
)

# Inclusão dos routers (endpoints)
app.include_router(health.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(auth.router, prefix="/api") 
app.include_router(scrap.router, prefix="/api") 

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao deploy do Primeiro Tech Challenge de Rômulo Carriço. Acesse /docs para a documentação interativa."}
