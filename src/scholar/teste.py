import csv
import time
import requests

# Função para buscar artigos no Semantic Scholar, filtrando por universidade e tema
def search_articles_by_university_and_topic(university_sigla, topic_keywords, start_year=2020, end_year=2025, max_results=100):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    query = f"{university_sigla} {' '.join(topic_keywords)}"  # Combina a universidade com as palavras-chave do tema
    params = {
        'query': query,
        'limit': max_results,
        'fields': 'title,authors,paperId,year,venue'
    }
    
    articles = []
    try:
        # Realiza a requisição à API do Semantic Scholar
        response = requests.get(url, params=params)
        
        # Verifica o código de resposta
        if response.status_code == 200:
            data = response.json()
            for paper in data.get('data', []):
                # Verifica se o ano está presente e é um número válido
                year = paper.get('year', None)
                if year is None:
                    year = 0  # Valor padrão caso o ano não esteja presente

                # Filtra os artigos dentro do intervalo de anos
                if start_year <= int(year) <= end_year:
                    # Processa os autores, caso seja uma lista ou dicionário
                    if isinstance(paper.get('authors', []), list):
                        authors = ', '.join([author['name'] for author in paper['authors']]) if 'authors' in paper else 'N/A'
                    else:
                        authors = 'N/A'  # Caso não seja uma lista de autores válida
                    
                    articles.append({
                        'title': paper['title'],
                        'authors': authors,
                        'year': year,
                        'university': university_sigla,
                        'venue': paper.get('venue', 'N/A'),
                        'url': f"https://semanticscholar.org/paper/{paper['paperId']}"
                    })
        elif response.status_code == 429:
            # Se atingir o limite de requisições (429), espera 1 minuto e tenta novamente
            print(f"Limite de requisições atingido para a universidade {university_sigla}. Esperando 60 segundos...")
            time.sleep(60)  # Delay de 1 minuto
            return search_articles_by_university_and_topic(university_sigla, topic_keywords, start_year, end_year, max_results)
        else:
            print(f"Erro na requisição para {university_sigla}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição para {university_sigla}: {e}")
        return []
    
    return articles

# Função para ler as universidades brasileiras de um arquivo CSV
def read_universities_csv(file_path):
    universities = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            universities.append(row[1])  # Considera que a sigla está na segunda coluna
    return universities

# Função para salvar os artigos encontrados em um arquivo CSV
def save_articles_to_csv(articles, output_file):
    # Define os campos do CSV
    fieldnames = ['title', 'authors', 'year', 'university', 'venue', 'url']
    
    # Escreve os dados no arquivo CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)

# Função principal
def main():
    # Caminho para o arquivo CSV com as siglas das universidades brasileiras
    universities_csv = 'universidades.csv'  # Substitua com o caminho real do seu CSV
    output_csv = 'artigos_brasileiros_2020_2025.csv'  # Caminho do arquivo de saída

    # Lê as universidades do CSV
    universities = read_universities_csv(universities_csv)

    # Defina as palavras-chave do tema "Mechanical Design and Mechatronics"
    topic_keywords = ["Mechanical Design", "Mechatronics"]

    # Lista para armazenar todos os artigos encontrados
    all_articles = []

    # Busca os artigos no Semantic Scholar para cada universidade
    for university in universities:
        print(f"Buscando artigos para a universidade {university}...")
        articles = search_articles_by_university_and_topic(university, topic_keywords, start_year=2020, end_year=2025)
        all_articles.extend(articles)

    # Salva os artigos no arquivo CSV
    save_articles_to_csv(all_articles, output_csv)
    print(f"Artigos salvos no arquivo {output_csv}")

# Executa o script
if __name__ == '__main__':
    main()
