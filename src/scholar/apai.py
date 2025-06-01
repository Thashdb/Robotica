import requests
import time

def buscar_autores_por_palavra_chave(palavra_chave, limite=50):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": palavra_chave,
        "limit": limite,
        "fields": "title,authors"
    }

    response = requests.get(url, params=params)
    autores_encontrados = {}

    if response.status_code == 200:
        data = response.json().get("data", [])
        for paper in data:
            for autor in paper.get("authors", []):
                autor_id = autor.get("authorId")
                nome = autor.get("name")
                if autor_id and nome and autor_id not in autores_encontrados:
                    autores_encontrados[autor_id] = nome
    else:
        print("Erro:", response.status_code)

    return autores_encontrados

# Exemplo de uso
areas = ["robotics", "mechatronics", "electronics"]
for area in areas:
    print(f"\n🔍 Área: {area}")
    autores = buscar_autores_por_palavra_chave(area, limite=100)
    for id_autor, nome in list(autores.items())[:10]:  # Mostra os 10 primeiros
        print(f"{nome} -> {id_autor}")
    time.sleep(2)
