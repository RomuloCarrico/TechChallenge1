📚 Books to Scrape RESTful API

## Visão Geral do Projeto

Este projeto consiste em uma **API RESTful de alto desempenho** construída com **FastAPI** para consultar, analisar e atualizar um *dataset* de livros extraído do site `books.toscrape.com`.

O projeto é um exemplo robusto de como integrar o **Web Scraping** (utilizando `requests` e `BeautifulSoup` para performance) com uma API assíncrona. A tarefa de *scraping* é isolada em um *thread* de *background* (`BackgroundTasks`), garantindo que o servidor permaneça responsivo em todos os momentos. Os dados são carregados em memória (`utils.py`) e disponibilizados através de *routers* especializados (Livros, Categorias, Estatísticas).

> 🏆 **Projeto:** Primeiro Tech Challenge de Rômulo Carriço

-----

## 🏗️ Arquitetura e Estrutura de Arquivos

A aplicação adota uma arquitetura modular com *routers* separados para cada domínio, facilitando a manutenção e o escalonamento.

```
.
├── api/
│   ├── main.py          # Ponto de entrada da aplicação FastAPI
│   ├── auth.py          # Roteador de Autenticação (Login, Refresh Token)
│   ├── books.py         # Roteador de Livros (Busca, Filtro, Detalhes)
│   ├── categories.py    # Roteador de Categorias (Lista única)
│   ├── health.py        # Roteador de Saúde (API e Dados)
│   ├── scrap.py         # Roteador de Orquestração do Web Scraping
│   └── stats.py         # Roteador para Estatísticas (Pandas)
├── Script/
│   └── WebScrap.py      # Lógica de Web Scraping (Requests + BeautifulSoup + Cache)
├── data/
│   └── Livros.csv       # Arquivo de dados principal
├── models.py            # Definição de Schemas Pydantic
├── utils.py             # Funções utilitárias (Carregamento e pré-processamento de dados)
├── auth_utils.py        # Funções de JWT (Criação/Verificação de Token, Segurança HTTP Bearer)
└── requirements.txt     # Dependências do projeto
```

-----

## ⚙️ Tecnologias e Configuração

### 1\. Dependências Fixadas (`requirements.txt`)

O arquivo `requirements.txt` lista todas as dependências com versões fixadas para garantir a reprodutibilidade, essencial para ambientes de *deploy* (como o Render).

### 2\. Configuração de Autenticação

O módulo `auth_utils.py` é responsável pela segurança, implementando:

  * Geração e decodificação de JWTs (HS256).
  * Tokens de **Acesso** (curta duração) e **Refresh** (longa duração) para melhor segurança e usabilidade.
  * Esquema de segurança **HTTP Bearer** (`get_current_user`) para proteger rotas.

> **Importante:** A verificação de senha é simplificada (`verify_password_simple`).

### 3\. Instalação e Execução

1.  **Instalação:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Execução Local:**

    ```bash
    uvicorn main:app --reload
    ```

    (Acesse a documentação interativa em `http://127.0.0.1:8000/docs`)

-----

## 💻 Endpoints da API

Todos os endpoints estão prefixados com `/api/v1`.

### A. Web Scraping & Dados (`api/scrap.py` e `api/health.py`)

| Método | Endpoint | Resumo |
| :--- | :--- | :--- |
| `POST` | `/v1/scrap` | **Inicia o Web Scraping.** Executado em *BackgroundTasks* (`202 Accepted`). **Protegido.** |
| `GET` | `/v1/scrap_status`| Verifica o *status* da tarefa de *scraping*. |
| `GET` | `/v1/health` | Verifica a saúde da API (`online`) e do *dataset* (`ok`/`erro`). |

### B. Autenticação (`api/auth.py`)

| Método | Endpoint | Resumo |
| :--- | :--- | :--- |
| `POST` | `/v1/auth/login` | Obtém `Access Token` e `Refresh Token`. |
| `POST` | `/v1/auth/refresh` | Renova o `Access Token` usando o `Refresh Token`. |

### C. Consultas aos Livros (`api/books.py` e `api/categories.py`)

| Método | Endpoint | Resumo |
| :--- | :--- | :--- |
| `GET` | `/v1/books/` | Lista todos os livros. |
| `GET` | `/v1/books/search`| Busca por `title` e/ou `category`. |
| `GET` | `/v1/books/price_range`| Filtra por faixa de preço (`min` e `max`). |
| `GET` | `/v1/books/{book_id}` | Retorna detalhes de um livro por ID. |
| `GET` | `/v1/categories` | Lista todas as categorias únicas, ordenadas alfabeticamente. |

### D. Análise de Dados (`api/stats.py`)

O módulo `stats.py` utiliza **Pandas** para realizar cálculos complexos em tempo real a partir dos dados carregados em memória.

| Método | Endpoint | Resumo |
| :--- | :--- | :--- |
| `GET` | `/v1/stats/overview` | Estatísticas gerais (Total, Preço Médio, Distribuição de Ratings 1-5). |
| `GET` | `/v1/stats/categories`| Estatísticas por categoria (Contagem e Preço Médio). |

-----

## 💡 Mecanismos Chave do Projeto

### 1\. Carregamento de Dados em Memória (`utils.py`)

  * A função `utils.load_data()` é executada uma vez na inicialização da API.
  * Lê o arquivo `Livros.csv`, normaliza os cabeçalhos, converte tipos (`preco` para float, `rating` para int) e **adiciona um `id` sequencial** (coluna zero).
  * Os dados pré-processados são armazenados na variável global `BOOKS_DATA`, eliminando a latência de I/O em cada requisição de leitura.

### 2\. Fluxo Otimizado de Web Scraping (`WebScrap.py`)

O script de *scraping* foi otimizado para velocidade:

  * **Requests & BeautifulSoup:** Conjunto rápido e seguro para extração dos dados.
  * **Cache:** Implementa um *cache* de **5 minutos** para evitar requisições desnecessárias, reutilizando o CSV mais recente.
  * **Rate Limiting:** Adiciona `time.sleep(0.1)` por livro para mitigar o risco de bloqueio pelo servidor.

### 3\. Modelação Robusta (`models.py`)

Todos os dados de entrada e saída são rigorosamente tipados e validados pelo Pydantic, garantindo:

  * Clareza na documentação (Swagger UI).
  * Validação automática de dados (ex: `preco` como `float`, `rating` como `int`).
  * Modelos específicos para respostas estatísticas (`OverviewStats`, `CategoryStats`), garantindo que o formato JSON retornado seja previsível.
