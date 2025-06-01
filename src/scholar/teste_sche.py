# How to use (from src/scholar/):
# python scholar.py
# python scholar.py -test

import os
import sys
import time
import csv
import requests
import json

# Caminho da pasta de cache
CACHE_DIR = "../../data/cache/scholar/"

def is_in_cache(prof):
    file = os.path.join(CACHE_DIR, prof + ".json")
    return os.path.exists(file)

def save_cache(prof, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    file = os.path.join(CACHE_DIR, prof + ".json")
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def read_cache(prof):
    file = os.path.join(CACHE_DIR, prof + ".json")
    with open(file, encoding='utf-8') as f:
        return json.load(f)

def crawl_semantic_scholar(author_id):
    try:
        url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?limit=1000&fields=title,year,venue,authors,citationCount,url"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar dados do autor {author_id}: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(e)
        sys.exit(1)

def get_scholar_data(author_id, prof):
    if is_in_cache(prof):
        return read_cache(prof)
    else:
        data = crawl_semantic_scholar(author_id)
        if data:
            save_cache(prof, data)
        return data

def download_all_prof_data():
    start_time = time.time()
    reader = csv.reader(open("../../data/configs/all-researchers.csv", 'r', encoding='utf-8'))
    count = 1
    for researcher in reader:
        name, author_id, institution = researcher
        print(f"{count} > {name}, {institution}")
        prof = name.replace(" ", "-")
        get_scholar_data(author_id, prof)
        time.sleep(1)  # Para evitar sobrecarga da API
        count += 1
    elapsed_time = round((time.time() - start_time) / 60, 2)
    print(f"Elapsed time (min): {elapsed_time}")

def test_all_prof_data():
    print("Testing cached files...")
    reader = csv.reader(open("../../data/configs/all-researchers.csv", 'r', encoding='utf-8'))
    count = 1
    for researcher in reader:
        name, author_id, institution = researcher
        print(f"{count} > {name}, {institution}")
        prof = name.replace(" ", "-")
        try:
            data = read_cache(prof)
            assert isinstance(data, dict)
        except Exception as e:
            print(f"Erro ao testar cache para {name}: {e}")
        count += 1

if __name__ == "__main__":
    download = len(sys.argv) < 2 or sys.argv[1] != "-test"
    if download:
        download_all_prof_data()
    test_all_prof_data()
