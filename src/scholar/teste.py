import csv
from scholarly import scholarly

# Função para buscar artigos no Google Scholar, filtrando por ano
def search_articles_by_university(university_sigla, start_year=2020, end_year=2025, max_results=100):
    search_query = scholarly.search_pubs(f"{university_sigla}")
    articles = []
    count = 0

    while count < max_results:
        try:
            pub = next(search_query)
            # Filtra apenas artigos dentro do intervalo de anos
            year = int(pub['bib']['pub_year']) if pub['bib']['pub_year'].isdigit() else 0

            # Se o artigo não estiver dentro do intervalo de anos, pula para o próximo
            if not (start_year <= year <= end_year):
                continue

            title = pub['bib']['title']
            authors = pub['bib']['author']
            venue = pub['bib']['venue']
            url = pub.get('pub_url', 'No URL')

            # Adiciona os dados do artigo à lista
            articles.append({
                'title': title,
                'authors': authors,
                'year': year,
                'university': university_sigla,
                'venue': venue,
                'url': url
            })

            count += 1
        except StopIteration:
            break  # Quando não houver mais artigos

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

    # Lista para armazenar todos os artigos encontrados
    all_articles = []

    # Busca os artigos no Google Scholar para cada universidade
    for university in universities:
        print(f"Buscando artigos para a universidade {university}...")
        articles = search_articles_by_university(university, start_year=2020, end_year=2025)
        all_articles.extend(articles)

    # Salva os artigos no arquivo CSV
    save_articles_to_csv(all_articles, output_csv)
    print(f"Artigos salvos no arquivo {output_csv}")

# Executa o script
if __name__ == '__main__':
    main()