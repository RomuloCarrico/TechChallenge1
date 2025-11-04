from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import csv
import time
import os

# --- Configurações e Variáveis Globais ---
URL_BASE = "https://books.toscrape.com/"
URL_PAGINA_BASE = "https://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGINAS = 50 
CABECALHO = ["Título", "Preço(£)", "Rating", "Disponibilidade", "Categoria", "URL da Imagem"]
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data')
NOME_ARQUIVO_CSV = os.path.join(DATA, "Livros.csv")

# Função para criar pasta /Data
def criar_pasta_data(caminho):
    """Cria a pasta recursivamente se ela não existir."""
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"Pasta criada: {caminho}")

# Função para converter o rating por extenso para integer
def rating_para_int(nota):
    """Converte a classe CSS de rating (e.g., 'star-rating Three') para um número."""
    notas_map = {
        'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
    }
    nota_por_extenso = nota.split()[-1]
    return notas_map.get(nota_por_extenso, 0)

# Função para limpar os dados de preço, e salvar em Float
def limpar_e_converter_preco(preco_string):
    """Remove o símbolo de libra (£) e converte a string para float."""
    # Remove o símbolo de libra ('£') e quaisquer outros caracteres não numéricos ou ponto
    preco_limpo = preco_string.replace('£', '').strip()
    
    try:
        # Converte a string limpa para float
        return float(preco_limpo)
    except ValueError:
        print(f"[ERRO DE CONVERSÃO] Não foi possível converter '{preco_string}' para float.")
        return 0.0 # Retorna 0.0 ou outro valor padrão em caso de erro

# Listas para armazenar dados
dados_a_coletar = [] 
dados_finais_csv = [] 
driver = None

try:
    # Criação da pasta /Data para salvar o CSV, caso não tenha pasta
    criar_pasta_data(DATA)

    # --- Configuração do WebDriver ---
    print("Iniciando o Chrome WebDriver...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(5)
    
    # --- Extração dos Dados das 50 Páginas do Catálogo ---
    print("\n--- Extraindo dados de todas as 50 páginas de catálogo ---")
    
    for pagina in range(1, TOTAL_PAGINAS + 1):
        url_catalogo = URL_PAGINA_BASE.format(pagina)
        if pagina == 1:
            url_catalogo = URL_BASE 

        print(f"Acessando Página {pagina}/{TOTAL_PAGINAS}: {url_catalogo}")
        driver.get(url_catalogo)
        
        livros = driver.find_elements(By.CSS_SELECTOR, 'li.col-xs-6.col-sm-4.col-md-3.col-lg-3')
        
        for livro in livros:
            try:
                # Título e URL de Detalhes
                titulo_link = livro.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a')
                titulo = titulo_link.get_attribute('title')
                url_detalhes_relativa = titulo_link.get_attribute('href')
                url_detalhes_absoluta = urljoin(URL_BASE, url_detalhes_relativa)
                
                # Preço
                preco_str = livro.find_element(By.CLASS_NAME, 'price_color').text
                preco = limpar_e_converter_preco(preco_str)

                # Rating
                rating_classe = livro.find_element(By.CSS_SELECTOR, 'p[class^="star-rating"]').get_attribute('class')
                rating = rating_para_int(rating_classe)
                
                # Disponibilidade
                disponibilidade = livro.find_element(By.CLASS_NAME, 'availability').text.strip()
                
                # URL da Imagem
                img_src_relativa = livro.find_element(By.TAG_NAME, 'img').get_attribute('src')
                url_imagem = urljoin(URL_BASE, img_src_relativa)

                dados_a_coletar.append({
                    "titulo": titulo,
                    "preco": preco,
                    "rating": rating,
                    "disponibilidade": disponibilidade,
                    "url_detalhes": url_detalhes_absoluta,
                    "url_imagem": url_imagem,
                })

            except Exception as e:
                print(f"  [AVISO] Erro ao extrair dados iniciais de um livro, pulando: {e}")
                continue

    print(f"\nTotal de livros encontrados nas 50 páginas: {len(dados_a_coletar)}")
    
    # --- Extração da Categoria  ---
    print("\n--- Extraindo Categoria por navegação (1 por 1) ---")
    
    for i, dado in enumerate(dados_a_coletar):
        print(f"  > Scraping {i+1}/{len(dados_a_coletar)}: {dado['titulo'][:40]}...")
        
        driver.get(dado['url_detalhes'])
        time.sleep(0.1) 
        
        categoria = "N/A"
        try:
            categoria_elemento = driver.find_element(By.CSS_SELECTOR, 'ul.breadcrumb li:nth-last-child(2) a')
            categoria = categoria_elemento.text
            
        except Exception:
            pass # Falha silenciosamente se a categoria não for encontrada
        
        dados_finais_csv.append([
            dado['titulo'],
            dado['preco'],
            dado['rating'],
            dado['disponibilidade'],
            categoria,
            dado['url_imagem']
        ])
    
    # --- Salvando no Arquivo CSV ---
    
    print("\n--- Salvando dos dados no arquivo CSV ---")
    
    with open(NOME_ARQUIVO_CSV, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        
        escritor.writerow(CABECALHO)
        escritor.writerows(dados_finais_csv)

    print("\n✅ Web scraping concluído com sucesso!")
    print(f"✅ {len(dados_finais_csv)} registros salvos em '{NOME_ARQUIVO_CSV}'.")

except Exception as e:
    print(f"\n❌ Ocorreu um erro geral durante a execução: {e}")

finally:
    if driver:
        print("Fechando o navegador.")
        driver.quit()
