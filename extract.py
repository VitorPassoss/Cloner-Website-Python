import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

def download_site(url, slug, output_dir="downloaded_site"):
    headers = {
        "User-Agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
    }

    # Cria a pasta para o site atual
    site_dir = os.path.join(output_dir, slug)
    os.makedirs(site_dir, exist_ok=True)

    # Faz a requisição à página principal
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Salva o HTML da página principal
    main_page_path = os.path.join(site_dir, "index.html")
    with open(main_page_path, "w", encoding=response.encoding or "utf-8") as file:
        file.write(response.text)

    # Analisa o conteúdo HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Define as tags e atributos para recursos externos
    resources = {
        "img": "src",        # Imagens
        "link": "href",      # CSS
        "script": "src",     # JS
    }

    # Faz o download dos recursos
    for tag, attr in resources.items():
        for element in soup.find_all(tag):
            resource_url = element.get(attr)
            if resource_url:
                # Constrói a URL completa do recurso
                resource_url = urljoin(url, resource_url)
                download_resource(resource_url, site_dir, headers)

    print(f"Download concluído para {slug}.")

def download_resource(url, output_dir, headers):
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        parsed_url = urlparse(url)
        # Decodificar o caminho do recurso
        decoded_path = unquote(parsed_url.path)
        resource_path = os.path.join(output_dir, parsed_url.netloc, decoded_path.lstrip("/"))

        # Corrigir caminho que termina em diretório
        if resource_path.endswith("/") or not os.path.basename(resource_path):
            resource_path = os.path.join(resource_path, "index.html")

        # Criar os diretórios necessários
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)

        # Salvar o arquivo
        content_type = response.headers.get("Content-Type", "")
        response.encoding = response.apparent_encoding or response.encoding

        if "text" in content_type or "application/javascript" in content_type:
            with open(resource_path, "w", encoding="utf-8") as file:
                file.write(response.text)
        else:
            with open(resource_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

        print(f"Recurso baixado: {resource_path}")
    except requests.RequestException as e:
        print(f"Erro ao baixar {url}: {e}")

def move_index_to_site_dir(output_dir, slug):
    source_path = os.path.join(output_dir, "index.html")
    dest_dir = os.path.join(output_dir, slug)
    dest_path = os.path.join(dest_dir, "index.html")

    if os.path.exists(source_path):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(source_path, dest_path)
        print(f"index.html movido para {dest_path}")
    else:
        print(f"index.html não encontrado na raiz para {slug}.")

# Uso do script
site_raiz = "https://www.casadoespelhos.com/products"
slugs = [
         'espelho-glam-redondo-50x50cm', 'espelho-adnet-em-couro-50cm-suporte-copia', 'espelho-fogo-corpo-inteiro-170x70cm', 'espelho-corpo-inteiro-arco-170x80cm']

output_dir = "downloaded_site"

# Baixar cada slug
for slug in slugs:
    site_url = f"{site_raiz}/{slug}"
    download_site(site_url, slug, output_dir)
    move_index_to_site_dir(output_dir, slug)
