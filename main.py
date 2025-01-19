import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote, urlencode

def download_site(url, output_dir="downloaded_site", utm_source="bot-downloader"):
    headers = {
        "User-Agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
    }
    
    # Cria a pasta onde o site será salvo
    os.makedirs(output_dir, exist_ok=True)
    
    # Adiciona UTM à URL principal
    url = add_utm_to_url(url, utm_source)

    # Faz a requisição à página principal
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Salva o HTML da página principal
    main_page_path = os.path.join(output_dir, "index.html")
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
                # Constrói a URL completa do recurso com UTM
                resource_url = add_utm_to_url(urljoin(url, resource_url), utm_source)
                download_resource(resource_url, output_dir, headers)

    print("Download concluído.")

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

def add_utm_to_url(url, utm_source):
    parsed_url = urlparse(url)
    query = dict(parsed_url.query.split("=", 1) for part in parsed_url.query.split("&") if "=" in part)
    query["utm_source"] = utm_source
    new_query = urlencode(query)
    return parsed_url._replace(query=new_query).geturl()

# Uso do script
download_site("https://ajuda-com-amor.github.io/Gabriel/")
