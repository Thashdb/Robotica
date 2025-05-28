# Desativa certos tipos de alertas do Pylint para permitir uma maior flexibilidade no código.
# pylint: disable=W0311,C0103,C0116,C0200,R1714

import csv          # Biblioteca para ler e escrever arquivos CSV.
import re           # Biblioteca para trabalhar com expressões regulares.
import sys          # Biblioteca para acessar variáveis do sistema e argumentos de linha de comando.
import glob         # Biblioteca para buscar arquivos com padrões de nomes específicos.
import os           # Biblioteca para interagir com o sistema operacional (como acessar arquivos).
from difflib import SequenceMatcher  # Biblioteca para comparar sequências de strings.
import requests     # Biblioteca para fazer requisições HTTP (ex: acessar a DBLP).
import xmltodict    # Biblioteca para converter XML para dicionários Python.

# Definindo o intervalo de anos para os artigos a serem processados
FIRST_YEAR = 2020
LAST_YEAR = 2025

class Global:
    default_min_paper_size = 0  # Tamanho mínimo de página padrão para artigos
    black_list = {}             # Lista de artigos que não devem ser contados (por exemplo, artigos em trilhas inválidas)
    white_list = {}             # Lista de artigos que devem ser contados (por exemplo, artigos sem número de páginas)
    conflist = []               # Lista de conferências da área de pesquisa
    journallist = []            # Lista de jornais da área de pesquisa
    out = {}                    # Armazena os artigos já encontrados
    score = {}                  # Armazena a pontuação dos departamentos
    confdata = {}               # Armazena informações sobre conferências
    profs = {}                  # Armazena dados sobre os professores
    profs_list = []             # Lista de professores
    arxiv_cache = {}            # Cache de links arXiv
    manual_journals = {}        # Jornais classificados manualmente
    manual_classification = {}  # Classificação manual de URLs
    pid_papers = []             # Lista de artigos processados
    area_prefix = sys.argv[1]  # Prefixo da área de pesquisa (como 'cs' para Ciência da Computação)
    multi_area_journal_list = []  # Lista de jornais multi-área
    mc_failed_file = open('manual-classification-failed.csv', 'a')  # Arquivo para registrar falhas de classificação manual

# Funções para lidar com jornais classificados manualmente

def init_manual_files():
    # Lê arquivos de classificação manual de jornais e armazena as informações
    with open('manual-journals.txt') as mf:
        Global.manual_journals = mf.read().splitlines()  # Carrega os jornais manualmente classificados
    reader = csv.reader(open('manual-classification.csv', 'r'))
    for row in reader:
        m_area, _, _, _, m_url = row  # Extrai a área e a URL do jornal
        Global.manual_classification[m_url] = m_area  # Associa a URL à área correspondente

def output_mc_failed(year, dblp_venue, title, url):
    # Registra falhas de classificação de jornais multi-área
    if url in Global.multi_area_journal_list:
        return  # Se o URL já estiver na lista, não faz nada
    Global.multi_area_journal_list.append(url)  # Adiciona o URL à lista
    file = Global.mc_failed_file
    # Escreve a falha no arquivo
    file.write(",")
    file.write(str(year))
    file.write(",")
    file.write('"' + str(dblp_venue) + '"')
    file.write(",")
    file.write('"' + title + '"')
    file.write(",")
    file.write(str(url))
    file.write("\n")

def outuput_multi_area_journal():
    # Exibe uma mensagem e fecha o arquivo de falhas
    if Global.multi_area_journal_list:
        print('\033[94m' + "Found papers in MULTI-AREA journals" + '\033[0m')
    Global.mc_failed_file.close()

# arxiv-related functions

def init_arxiv_cache():
    # Inicializa o cache de URLs do arXiv a partir de um arquivo CSV
    fname = '../cache/arxiv/' + Global.area_prefix + '-arxiv-cache.csv'
    if os.path.exists(fname):
        reader = csv.reader(open(fname, 'r'))
        for line in reader:
            Global.arxiv_cache[line[0]] = line[1] # Armazena o DOI e seu link correspondente

def output_arxiv_cache():
    # Salva o cache do arXiv em um arquivo CSV
    if Global.arxiv_cache:
        f = open('../cache/arxiv/' + Global.area_prefix + '-arxiv-cache.csv', 'w')
        for doi in Global.arxiv_cache:
            f.write(doi)
            f.write(',')
            f.write(Global.arxiv_cache[doi])
            f.write('\n')
        f.close()

def get_arxiv_url(doi, title):
    # Tenta obter o URL do arXiv com base no DOI e título do artigo
    if not isinstance(doi, str):
        return "no_arxiv"
    if doi in Global.arxiv_cache:
        return Global.arxiv_cache[doi]  # Retorna o URL do arXiv do cache
    try:
        title = title[:-1]
        ti = '"' + title + '"'
        url = "http://export.arxiv.org/api/query"
        payload = {'search_query': ti, 'start': 0, 'max_results': 1}
        arxiv_xml = requests.get(url, params=payload).text  # Faz uma requisição ao arXiv
        arxiv = xmltodict.parse(arxiv_xml)
        arxiv = arxiv["feed"]
        arxiv_url = "no_arxiv"
        nb_results = int(arxiv["opensearch:totalResults"]["#text"])
        if nb_results == 1:
            arxiv = arxiv["entry"]
            arxiv_title = arxiv["title"]
            t1 = arxiv_title.lower()
            t2 = title.lower()
            if SequenceMatcher(None, t1, t2).ratio() >= 0.9:
                arxiv_url = arxiv["id"]
    except:
        arxiv_url = "no_arxiv"
    Global.arxiv_cache[doi] = arxiv_url # Atualiza o cache
    return arxiv_url

# Funções de saída de dados

def outuput_everything():
    # Chama várias funções para gerar arquivos de saída
    output_papers()
    output_scores()
    output_venues()
    output_profs_list()
    output_arxiv_cache()
    output_search_box_list()
    outuput_multi_area_journal()

def output_venues_confs(result):
    # Exibe as conferências em um arquivo CSV
    if len(result) > 0:
        f = open(Global.area_prefix + '-out-confs.csv', 'w')
        for conf in result:
            f.write(conf[0])
            f.write(',')
            f.write(str(conf[1]))
            f.write('\n')
        f.close()

def output_venues_journals(result):
    # Exibe os jornais em um arquivo CSV
    if len(result) > 0:
        f = open(Global.area_prefix + '-out-journals.csv', 'w')
        for journal in result:
            f.write(journal[0])
            f.write(',')
            f.write(str(journal[1]))
            f.write('\n')
        f.close()

def output_venues():
    # Organiza e escreve as conferências e jornais nos arquivos apropriados
    confs = []
    journals = []
    for p in Global.out.items():
        if p[1][7] == "C":
            confs.append(p[1][1])
        else:
            journals.append(p[1][1])
    result1_temp = sorted([(c, confs.count(c)) for c in Global.conflist], key=lambda x: x[0])
    result1 = sorted(result1_temp, key=lambda x: x[1], reverse=True)
    result2_temp = sorted([(c, journals.count(c)) for c in Global.journallist], key=lambda x: x[0])
    result2 = sorted(result2_temp, key=lambda x: x[1], reverse=True)
    output_venues_confs(result1)
    output_venues_journals(result2)


# Função que escreve os detalhes de um artigo no arquivo   
    # coloca as infos em um csv
def write_paper(f, is_prof_tab, paper):
    f.write(str(paper[0]))      # Ano do artigo
    f.write(',')
    f.write(str(paper[1]))      # Local de publicação (Conferência/Jornal)
    f.write(',')
    f.write(str(paper[2]))      # Título
    f.write(',')
    if is_prof_tab:
        f.write(str(paper[3]))  # department
        f.write(',')
    authors = paper[4]
    for author in authors[:-1]:      # Autor(es)
        f.write(str(author))
        f.write('; ')
    f.write(str(authors[-1]))       # Último autor
    f.write(',')
    f.write(str(paper[5]))      # DOI
    f.write(',')
    f.write(str(paper[6]))      # Tipo de conferência/jornal
    f.write(',')
    f.write(str(paper[7]))      # Tipo de publicação
    f.write(',')
    f.write(str(paper[8]))  # Link arxiv
    f.write(',')
    if paper[9] != -1:
        f.write(str(paper[9]))  # Citações
    f.write('\n')


# Função que gera os arquivos de saída para os artigos
def output_papers():
    # Ordena os artigos primeiro pela conferência/jornal e, em seguida, pelo título (colunas 1 e 2)
    out2 = sorted(Global.out.items(), key=lambda x: (x[1][1], x[1][2]))

    # Ordena os artigos pela data de publicação (coluna 0) em ordem decrescente
    sorted_papers = sorted(out2, key=lambda x: x[1][0], reverse=True)

    # Abre um arquivo CSV para salvar os artigos processados
    f = open(Global.area_prefix + '-out-papers.csv', 'w')
    for i in range(0, len(sorted_papers)):
        paper = sorted_papers[i][1]
        write_paper(f, True, paper)
    f.close()

def output_prof_papers(prof):
    # Substitui espaços no nome do professor por hífens para formar o nome do arquivo
    prof = prof.replace(" ", "-")

    # Abre um arquivo CSV específico para armazenar os artigos do professor
    f = open("../cache/profs/" + Global.area_prefix + "-" + prof + '-papers.csv', 'w')

    # Escreve todos os artigos do professor usando o identificador 'pid_papers' armazenado em Global
    for url in Global.pid_papers:
        paper = Global.out[url]
        write_paper(f, False, paper)
    f.close()

def write_scores(sorted_scores):
    # Abre um arquivo CSV para salvar as pontuações dos departamentos
    f = open(Global.area_prefix + '-out-scores.csv', 'w')

    # Escreve as pontuações dos departamentos no arquivo
    for i in range(0, len(sorted_scores)):
        dept = sorted_scores[i][0]  # Departamento
        f.write(str(dept))
        f.write(',')
        s = round(sorted_scores[i][1], 2)   # Pontuação arredondada para 2 casas decimais
        f.write(str(s))
        f.write('\n')
    f.close()

def output_scores():
    final_score = {}

    # Filtra os departamentos que têm pontuação maior que 0
    for dept in Global.score:
        s = Global.score[dept]
        if s > 0:
            final_score[dept] = s

    # Ordena os departamentos pela pontuação de forma crescente pelo nome
    sorted_scores_temp = sorted(final_score.items(), key=lambda x: x[0])
    # Ordena novamente pela pontuação de forma decrescente
    sorted_scores = sorted(sorted_scores_temp, key=lambda x: x[1], reverse=True)
    write_scores(sorted_scores)

def write_profs(sorted_profs):
    # Abre um arquivo CSV para salvar a lista de professores e suas pontuações
    f = open(Global.area_prefix + '-out-profs.csv', 'w')

    # Escreve o nome do departamento e a pontuação dos professores no arquivo
    for i in range(0, len(sorted_profs)):
        dept = sorted_profs[i][0]
        f.write(str(dept))
        f.write(',')
        s = sorted_profs[i][1]
        f.write(str(s))
        f.write('\n')
    f.close()

def output_profs():
    final_profs = {}

    # Filtra os professores com pontuação maior que 0
    for dept in Global.profs:
        s = Global.profs[dept]
        if s > 0:
            final_profs[dept] = s

    # Ordena os departamentos por pontuação de forma crescente pelo nome
    sorted_profs_temp = sorted(final_profs.items(), key=lambda x: x[0])

    # Ordena novamente pela pontuação de forma decrescente
    sorted_profs = sorted(sorted_profs_temp, key=lambda x: x[1], reverse=True)

    # Limita a lista a apenas os 16 primeiros professores
    if len(sorted_profs) >= 16:
        sorted_profs = sorted_profs[:16]
    write_profs(sorted_profs)

def output_profs_list():
    # Ordena a lista de professores pela ordem alfabética
    profs = Global.profs_list
    profs = sorted(profs, key=lambda x: x[0])

    # Abre um arquivo CSV para salvar a lista de professores
    f = open(Global.area_prefix + '-out-profs-list.csv', 'w')
    for i in range(0, len(profs)):
        f.write(str(profs[i][0]))   # Nome do professor
        f.write(',')
        f.write(str(profs[i][1]))   # Departamento do professor
        f.write('\n')
    f.close()

def merge_output_prof_papers(prof):
    # Muda o diretório para o local onde estão armazenados os artigos dos professores
    os.chdir("../cache/profs")

    # Cria uma lista
    filenames = []

    # Substitui espaços por hífens no nome do professor para criar o nome do arquivo
    prof = prof.replace(" ", "-")

    # Busca todos os arquivos que possuem o nome do professor e terminam com "-papers.csv"
    for file in glob.glob("*" + prof + "-papers.csv"):
        filenames.append(file)

    # Ordena os arquivos pelo nome
    filenames.sort()

    # Abre um arquivo de saída para armazenar os artigos unidos
    outfile = open("../../data/profs/search/" + prof + ".csv", 'w')


    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())
    os.chdir("../../data")

def output_search_box_list():
    # Muda o diretório para a pasta onde os arquivos de pesquisa dos professores estão localizados
    os.chdir("./profs/search")

    # Cria uma lista para armazenar os nomes dos professores
    profs = []

    # Busca todos os arquivos CSV na pasta e os adiciona à lista
    for file in glob.glob("*.csv"):
        file = file.replace(".csv", "") # Remove a extensão ".csv"
        file = file.replace("-", " ")   # Substitui hífens por espaços
        profs.append(file)

    # Remove o item "empty" da lista, se existir
    profs.remove("empty")

    # Ordena os professores em ordem alfabética
    profs.sort()

    f = open("../all-authors.csv", 'w')
    for p in profs:
        f.write(p)
        f.write('\n')
    f.close()

# dblp parsing auxiliary functions

def get_paper_score(weight):
    # Atribui uma pontuação com base no peso (classificação) do artigo
    if (weight == 1) or (weight == 4):
        return 1.0  # Artigos em conferências ou revistas top
    if weight == 2:
        return 0.66  # Artigos em conferências de nível intermediário
    if (weight == 3) or (weight == 6) or (weight == 7):
        return 0.33  # Artigos em conferências de baixo nível
    if weight == 5:
        return 0.4   # Artigos em revistas de baixo nível
    return 0.0       # Artigos sem pontuação definida

def get_doi(doi):
    # Verifica o tipo do DOI e retorna o valor correto
    if isinstance(doi, list):
        doi = doi[0]
    if isinstance(doi, dict):
        doi = doi["#text"]
    return doi

def get_venue_tier(weight):
    # Retorna o "nível" do evento baseado no peso (classificação)
    if (weight == 1) or (weight == 4):
        return "top"  # Top venues
    if weight == 2:
        return "near-top"  # Near-top venues
    return "null"  # Outros

def get_venue_type(weight):
    # Retorna o tipo do evento (C para conferência, J para jornal)
    if weight <= 3:
        return "C"  # Conferência
    return "J"  # Jornal

def get_authors(author_list):
    authors = []
    if isinstance(author_list, dict):  # Artigo com um único autor
        author_list = author_list["#text"]
        authors.append(author_list)
    elif isinstance(author_list, str):  # Artigo com um único autor
        authors.append(author_list)
    else:  # Artigo com múltiplos autores
        for name in author_list:
            if isinstance(name, dict):
                name = name["#text"]
            authors.append(name)
    return authors

def get_title(title):
    # Extrai o título de um artigo, removendo as aspas
    if isinstance(title, dict):
        return title["#text"]
    return title.replace("\"", "")  # Remove aspas do título

def get_min_paper_size(weight):
    if weight == 6:  # magazine
        return 6  # Artigos em revistas (com peso 6) têm tamanho mínimo de 6 páginas
    if (weight == 4) or (weight == 5) or (weight == 7):  # journals
        return 0   # Para artigos em jornais com peso 4, 5 ou 7, o tamanho mínimo é 0 (devido à falta de número de páginas nos jornais da Elsevier)
    return Global.default_min_paper_size  # Para conferências, usa o tamanho mínimo padrão definido na classe Global

def as_int(i):
    try:
        return int(i)  # Tenta converter o valor para um inteiro
    except:
        return 0  # Se ocorrer um erro (valor não for um número válido), retorna 0

def parse_paper_size(dblp_pages):
    page = re.split(r"-|:", dblp_pages)  # Divide o intervalo de páginas, separando por "-" ou ":"
    
    if len(page) == 2:
        p1 = as_int(page[0])  # Página inicial
        p2 = as_int(page[1])  # Página final
        return p2 - p1 + 1  # Calcula o número total de páginas

    if len(page) == 4:
        p1 = as_int(page[1])  # Página inicial
        p2 = as_int(page[3])  # Página final
        return int(p2) - int(p1) + 1  # Calcula o número total de páginas

    if len(page) == 3:
        p1 = as_int(page[1])  # Página inicial
        p2 = as_int(page[2])  # Página final
        return int(p2) - int(p1) + 1  # Calcula o número total de páginas
    
    return 0  # Caso não tenha um formato esperado, retorna 0

def get_paper_size(url, dblp, dblp_venue):
    if url in Global.white_list:  # Se o URL estiver na lista branca, o artigo tem um tamanho de 10 páginas
        return 10
    
    if 'pages' in dblp:  # Se o campo 'pages' estiver no artigo, chama a função para calcular o tamanho da página
        return parse_paper_size(dblp['pages'])
    
    if (dblp_venue == "Briefings Bioinform.") or \
        (dblp_venue == "J. Intell. Robotic Syst.") or \
        (dblp_venue == "NeurIPS"):  # Para conferências específicas, o tamanho é fixo de 10
        return 10  # Devido à falta de campos de página em alguns artigos
    return 0  # Retorna 0 se não houver informações suficientes sobre o tamanho do artigo

def get_dblp_venue(dblp):
    if 'journal' in dblp:  # Se o artigo estiver em um jornal
        if (dblp['journal'] == "PACMPL") or \
            (dblp['journal'] == "PACMHCI") or \
            (dblp['journal'] == "Proc. ACM Program. Lang.") or \
            (dblp['journal'] == "Proc. ACM Softw. Eng.") or \
            (dblp['journal'] == "Proc. ACM Hum. Comput. Interact."):  # Se for uma conferência/jornal específico
            if 'number' in dblp:
                dblp_venue = dblp['number']  # Número do evento
            else:
                dblp_venue = dblp['journal']  # Se não houver número, usa o nome do jornal
        else:
            dblp_venue = dblp['journal']  # Caso padrão, pega o nome do jornal
    elif 'booktitle' in dblp:  # Se o artigo foi publicado em um livro
        dblp_venue = dblp['booktitle']
    else:
        print("Failed parsing DBLP")  # Caso não seja nem um jornal nem um livro
        sys.exit(1)  # Encerra o programa devido a erro na análise
    return dblp_venue  # Retorna o nome do jornal ou livro

def has_dept(dept_str, dept):
    dept_list = dept_str.split(";")  # Divide a string de departamentos em uma lista
    for d in dept_list:
        d = d.replace(" ", "")  # Remove espaços em branco
        if d == dept:  # Verifica se o departamento atual corresponde ao departamento procurado
            return True
    return False  # Retorna False se o departamento não for encontrado

def is_manual_journal(year, dblp_venue, title, url):
    # Verifica se o jornal está na lista manual de jornais classificados
    if dblp_venue in Global.manual_journals:
        # Se o URL do jornal estiver na classificação manual, verifica a área
        if url in Global.manual_classification:
            m_area = Global.manual_classification[url]  # Obtém a área do jornal
            if m_area != Global.area_prefix:  # Se a área não coincidir com a área de pesquisa
                return True  # Retorna True para indicar que é um jornal manual
        else:
            # Se o URL não estiver na classificação manual, registra a falha
            output_mc_failed(year, dblp_venue, title, url)
            return True  # Retorna True indicando que é um jornal manual
    return False  # Se não for manual, retorna False

# main dblp parse function

def is_paper_size_ok(url, dblp, dblp_venue, weight):
    # Obtém o tamanho do artigo (número de páginas) com base nos dados fornecidos
    size = get_paper_size(url, dblp, dblp_venue)
    # Obtém o tamanho mínimo do artigo baseado no peso do artigo (classificação)
    minimum_size = get_min_paper_size(weight)
    # Verifica se o tamanho do artigo é maior ou igual ao tamanho mínimo
    return size >= minimum_size

def update_paper(paper, dept, url, weight):
    # Atualiza os dados do artigo no dicionário `Global.out`
    Global.out[url] = (paper[0], paper[1], paper[2], paper[3] + "; " + dept,
                        paper[4], paper[5], paper[6], paper[7], paper[8],
                        paper[9])
    # Atualiza a pontuação do departamento associado ao artigo
    Global.score[dept] += get_paper_score(weight)

def add_new_paper(weight, doi, title, dblp, url, year, venue, global_department):
    # Determina o nível da conferência/jornal com base no peso
    tier = get_venue_tier(weight)
    # Determina o tipo de evento (conferência ou jornal)
    venue_type = get_venue_type(weight)
    # Obtém o link para o arXiv associado ao artigo
    arxiv = get_arxiv_url(doi, title)
    # Inicializa o número de citações como 0
    citations = 0
    # Obtém a lista de autores do artigo
    authors = get_authors(dblp['author'])
    # Adiciona o artigo aos dados globais
    Global.out[url] = (year, venue, '"' + title + '"', global_department, authors, doi,
                        tier, venue_type, arxiv, citations)
    # Atualiza a pontuação do departamento com base no peso do artigo
    Global.score[global_department] += get_paper_score(weight)

def is_paper_indexable(dblp):
    # Verifica se o artigo é indexável (se possui 'journal' ou 'booktitle' e está no intervalo de anos permitido)
    if not isinstance(dblp, dict):
        return False
    if ('journal' in dblp) or ('booktitle' in dblp):
        dblp_venue = get_dblp_venue(dblp)  # Obtém o local da conferência/jornal
        year = int(dblp['year'])  # Obtém o ano do artigo
        # Verifica se o artigo está no intervalo de anos e se a conferência/jornal é válida
        if (year >= FIRST_YEAR) and (year <= LAST_YEAR) and (dblp_venue in Global.confdata):
            _, weight = Global.confdata[dblp_venue]
            url = dblp['url']
            if url in Global.black_list:
                return False  # Se o artigo estiver na lista negra, não é indexável
            title = get_title(dblp['title'])
            # Verifica se o jornal é manualmente classificado e se não deve ser indexado
            if is_manual_journal(year, dblp_venue, title, url):
                return False
            # Verifica se o artigo tem um tamanho adequado
            return is_paper_size_ok(url, dblp, dblp_venue, weight)
    return False  # Se o artigo não for válido para indexação, retorna False

def parse_dblp(_, dblp):
    global global_department, global_found_paper

    # Verifica se o artigo pode ser indexado
    if is_paper_indexable(dblp):
        dblp_venue = get_dblp_venue(dblp)  # Obtém o local da conferência/jornal
        year = int(dblp['year'])  # Obtém o ano do artigo
        venue, weight = Global.confdata[dblp_venue]  # Obtém o nome da conferência/jornal e seu peso
        url = dblp['url']  # URL do artigo
        doi = get_doi(dblp['ee'])  # DOI do artigo
        title = get_title(dblp['title'])  # Título do artigo

        global_found_paper = True   # Marca que o artigo foi encontrado
        Global.pid_papers.append(url)  # Adiciona o artigo à lista de artigos encontrados

        if url in Global.out:  # Se o artigo já foi processado
            paper = Global.out[url]
            # Verifica se o artigo já foi atribuído ao departamento
            if has_dept(paper[3], global_department):
                return True  # Se já foi, não faz nada
            update_paper(paper, global_department, url, weight)  # Atualiza os dados do artigo
            return True
        
        # Adiciona um novo artigo ao banco de dados
        add_new_paper(weight, doi, title, dblp, url, year, venue, global_department)
    
    return True   # Continua processando os próximos artigos

# init functions

def init_black_list():
    # Lê a lista negra de artigos que não devem ser contados
    black_list_file = Global.area_prefix + "-black-list.txt"
    if os.path.exists(black_list_file):
        with open(black_list_file) as blf:
            Global.black_list = blf.read().splitlines()  # Armazena os URLs dos artigos na lista negra

def init_white_list():
    # Lê a lista branca de artigos que devem ser contados
    white_list_file = Global.area_prefix + "-white-list.txt"
    if os.path.exists(white_list_file):
        with open(white_list_file) as wlf:
            Global.white_list = wlf.read().splitlines()  # Armazena os URLs dos artigos na lista branca

def init_prof_cache():
    # Remove os arquivos de cache antigos dos professores
    prof_cache_pattern = "../cache/profs/" + Global.area_prefix + "-*.csv"
    for f in glob.glob(prof_cache_pattern):
        os.remove(f)

def init_confs():
    # Lê os dados das conferências e jornais a partir de um arquivo CSV
    reader = csv.reader(open(Global.area_prefix + "-confs.csv", 'r'))
    for conf_row in reader:
        conf_dblp, conf_name, conf_weight = conf_row
        Global.confdata[conf_dblp] = conf_name, int(conf_weight)  # Armazena o nome e peso da conferência
        if int(conf_weight) <= 3:
            Global.conflist.append(conf_name)  # Se o peso for baixo, é uma conferência
        else:
            Global.journallist.append(conf_name)  #_

def init_min_paper_size():
    # Abre o arquivo "research-areas-config.csv" para ler as configurações da área de pesquisa
    reader = csv.reader(open("research-areas-config.csv", 'r'))
    
    # Itera sobre cada linha do arquivo CSV
    for area_tuple in reader:
        # Verifica se o prefixo da área de pesquisa no arquivo é igual ao prefixo global da área
        if area_tuple[0] == Global.area_prefix:
            # Se for, define o tamanho mínimo de página (paper size) com base na configuração do arquivo
            Global.default_min_paper_size = int(area_tuple[1])
            break  # Sai do loop após encontrar a área correspondente

def init_everything():
    # Inicializa várias configurações, incluindo o tamanho mínimo de artigo, conferências, listas manualmente classificadas, etc.
    init_min_paper_size()    # Inicializa o tamanho mínimo de artigo
    init_confs()             # Inicializa dados de conferências
    init_black_list()        # Inicializa a lista negra de artigos a serem ignorados
    init_white_list()        # Inicializa a lista branca de artigos a serem incluídos
    init_manual_files()      # Inicializa arquivos de classificação manual
    init_arxiv_cache()       # Inicializa o cache de links do arXiv
    init_prof_cache()        # Inicializa o cache de professores

# main loop that process each researcher

def read_dblp_file(pid, prof):
    # Substitui espaços no nome do professor por hífens para formar o nome do arquivo
    prof = prof.replace(" ", "-")
    
    # Define o caminho do arquivo XML no cache para o professor
    file = '../cache/dblp/' + prof + '.xml'
    
    # Se o arquivo XML já existe no cache, abre e lê seu conteúdo
    if os.path.exists(file):
        with open(file) as f:
            dblp_xml = f.read()
    else:
        # Caso contrário, faz uma requisição à DBLP para obter o arquivo XML
        try:
            url = "http://dblp.org/pid/" + pid + ".xml"
            dblp_xml = requests.get(url).text
            # Salva o arquivo XML no cache local
            with open(file, 'w') as f:
                f.write(str(dblp_xml))
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)  # Encerra o programa se houver erro na requisição
    return dblp_xml  # Retorna o conteúdo do arquivo XML

def process_prof_with_paper(prof, dept):
    # Adiciona o professor e seu departamento à lista de professores
    Global.profs_list.append((prof, dept))
    
    # Aumenta a contagem de professores no departamento correspondente
    Global.profs[dept] += 1
    
    # Chama a função para gerar o arquivo com os artigos do professor
    output_prof_papers(prof)
    
    # Junta os artigos do professor e os salva em um único arquivo CSV
    merge_output_prof_papers(prof)

def process_department_data(dept):
    # Se o departamento não tiver uma pontuação definida, inicializa com 0
    if not dept in Global.score:
        Global.score[dept] = 0.0
    
    # Se o departamento não tiver sido registrado, inicializa a contagem de professores
    if not dept in Global.profs:
        Global.profs[dept] = 0

def process_all_researchers():
    global global_department, global_found_paper
    
    # Lê o arquivo com todos os pesquisadores
    all_researchers = csv.reader(open("all-researchers.csv", 'r'))
    count = 1
    print("Research Area: " + Global.area_prefix)  # Exibe a área de pesquisa
    
    # Itera sobre todos os pesquisadores
    for researcher in all_researchers:
        prof = researcher[0]   # Nome do professor
        global_department = researcher[1]   # Departamento do professor
        pid = researcher[2]    # ID do professor na DBLP
        
        # Processa os dados do departamento do professor
        process_department_data(global_department)
        
        # Lê o arquivo XML do DBLP para o professor
        bibfile = read_dblp_file(pid, prof)
        
        # Reseta a lista de artigos do professor
        Global.pid_papers = []
        global_found_paper = False    # Variável global para indicar se o artigo foi encontrado
        
        # Converte o XML para dicionário e processa os artigos
        xmltodict.parse(bibfile, item_depth=3, item_callback=parse_dblp)
        
        # Se um artigo foi encontrado, processa o professor e seus artigos
        if global_found_paper:
            process_prof_with_paper(prof, global_department)
            print(str(count) + " >> " + prof + ", " + global_department)  # Exibe o progresso
        
        count = count + 1  # Aumenta o contador de pesquisadores processados

# main program

init_everything()
process_all_researchers()
outuput_everything()
