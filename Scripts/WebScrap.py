# Arquivo: Script/webscrap.py

import requests
from bs4 import BeautifulSoup
import os
import csv
import glob
import time
from urllib.parse import urljoin
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
FINAL_CSV = os.path.join(DATA_DIR, "Livros.csv")

def checkCacheFile() -> bool:
    """Verifica se existe CSV recente e reutiliza como cache."""
    CACHE_MINUTES = 5
    files = glob.glob(os.path.join(DATA_DIR, "books_*.csv"))

    if files:
        latestFile = max(files, key=os.path.getctime)
        lastModified = os.path.getmtime(latestFile)
        if time.time() - lastModified < CACHE_MINUTES * 60:
            print(f"Usando cache local: {latestFile}")
            if not os.path.exists(FINAL_CSV):
                os.rename(latestFile, FINAL_CSV)
                print(f"Cache salvo como: {FINAL_CSV}")
            return True
    return False


def runScraping():
    """Executa o scraping e salva o CSV limpo (Livros.csv)."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(FINAL_CSV):
        print(f"Arquivo já existe: {FINAL_CSV}")
        return

    if checkCacheFile():
        print("Cache válido encontrado. Nenhum scraping necessário.")
        return

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    tempFile = os.path.join(DATA_DIR, f"books_{timestamp}.csv")

    print(f"Criando novo arquivo: {tempFile}")

    BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
    BASE_BASE = "https://books.toscrape.com/"
    NUM_PAGES = 50

    # Dicionário para converter rating textual em número
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    with open(tempFile, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Título", "Preço(£)", "Rating", "Disponibilidade", "Categoria", "URL da Imagem"])

        for page in range(1, NUM_PAGES + 1):
            print(f"Lendo página {page}")
            url = BASE_URL.format(page)
            response = requests.get(url)
            response.encoding = "utf-8"

            if response.status_code != 200:
                print(f"Erro ao acessar página {page}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.find_all("article", class_="product_pod")

            for book in books:
                title = book.h3.a["title"]

                # Preço -> float
                price_text = book.find("p", class_="price_color").text.strip()
                price = float(price_text.replace("£", ""))

                # Rating -> número
                rating_class = book.p["class"][1]
                rating = rating_map.get(rating_class, 0)

                stock = book.find("p", class_="instock availability").text.strip()

                # Corrige URL da imagem
                image_src = book.find("img")["src"].replace("../../", "")
                image_url = urljoin(BASE_BASE, image_src)

                # Descobre categoria
                href = book.h3.a["href"]
                detail_url = urljoin(url, href)
                detail_resp = requests.get(detail_url)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                category = detail_soup.find("ul", class_="breadcrumb").find_all("a")[2].text.strip()

                writer.writerow([title, price, rating, stock, category, image_url])

    os.rename(tempFile, FINAL_CSV)
    print(f"✅ Arquivo salvo como: {FINAL_CSV}")
    print("Script finalizado com sucesso.")


if __name__ == "__main__":
    runScraping()
