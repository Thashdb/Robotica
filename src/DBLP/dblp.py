# pylint: disable=W0311,C0103,C0116,C0200,R1714

import os
import sys 
import time
import csv          #ler e escrever arquivos CSV.
import requests
import xmltodict



# Definindo a área de pesquisa como "Computer Science"
area_prefix = "cs"

# Caminho do arquivo CSV de saída
output_dir = "data/"

# Função para buscar os dados da API do DBLP para Computer Science
def fetch_dblp_data(area="cs"):
    # Base URL do DBLP para a busca
    url = f"https://dblp.org/search/publ/api?q={area}&h=150"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Imprimir o conteúdo da resposta para entender o que está sendo retornado
            print("Resposta da API:")
            print(response.text[:500])  # Exibe os primeiros 500 caracteres da resposta
            return response.text
        else:
            print(f"Erro ao buscar dados para {area}: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição ao DBLP: {e}")
        return None

# Função para salvar os dados em um arquivo CSV
def save_to_csv(data, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Authors", "Year", "Venue", "DOI", "URL"])  # Cabeçalhos do CSV
        for item in data:
            title = item.get("title", "N/A")
            # Ajustar o processamento dos autores para pegar os nomes
            authors = ", ".join([author["#text"] for author in item.get("author", []) if isinstance(author, dict)])
            year = item.get("year", "N/A")
            venue = item.get("venue", "N/A")
            doi = item.get("ee", "N/A")
            url = item.get("url", "N/A")
            writer.writerow([title, authors, year, venue, doi, url])  # Escreve os dados

# Função para processar o XML retornado pelo DBLP e extrair as informações necessárias
def process_dblp_data(dblp_xml):
    try:
        data_dict = xmltodict.parse(dblp_xml)
        # Verifica se a chave 'hits' existe na resposta
        if "hits" not in data_dict["result"]:
            print("Chave 'hits' não encontrada na resposta da API.")
            return []
        
        papers = data_dict["result"]["hits"]["hit"]  # Lista de artigos
        result = []
        
        for paper in papers:
            info = paper.get("info", {})
            title = info.get("title", "")
            
            # Verifica se 'authors' é uma lista ou uma string
            authors = info.get("authors", {}).get("author", [])
            if isinstance(authors, str):  # Caso seja uma string, transforme-a em uma lista
                authors = [authors]
            
            year = info.get("year", "")
            venue = info.get("venue", "")
            doi = info.get("ee", "")
            url = info.get("url", "")
            result.append({
                "title": title,
                "author": authors,
                "year": year,
                "venue": venue,
                "doi": doi,
                "url": url
            })
        
        return result
    except Exception as e:
        print(f"Erro ao processar dados do DBLP: {e}")
        return []

# Função principal para orquestrar o processo
def main():
    print(f"Buscando artigos para a área de 'Computer Science' no DBLP...")
    dblp_xml = fetch_dblp_data(area=area_prefix)
    
    if dblp_xml:
        print(f"Processando os dados de {area_prefix}...")
        papers_data = process_dblp_data(dblp_xml)
        if papers_data:
            print(f"Salvando os dados em um arquivo CSV...")
            save_to_csv(papers_data, os.path.join(output_dir, f"{area_prefix}-out-papers.csv"))
            print(f"Dados salvos com sucesso!")
        else:
            print("Nenhum dado encontrado ou erro ao processar.")
    else:
        print("Erro ao obter os dados do DBLP.")

if __name__ == "__main__":
    main()
