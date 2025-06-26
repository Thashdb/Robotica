import csv
import glob
import os

# Recebe o caminho do arquivo e retorna o número de linhas
def file_size(file):
    try:
        with open(file, encoding="utf-8") as f:
            return sum(1 for line in f)
    except UnicodeDecodeError:
        with open(file, encoding="latin1") as f:
            return sum(1 for line in f)

# Para cada professor, verifica o tamanho dos arquivos encontrados
# Determina a área conforme o arquivo com maior número de linhas
def get_area(prof):
    size = 0
    area = ""
    files = glob.glob("../../data/configs/profs/papers/*" + prof + "-papers.csv")
    for file in files:
        size2 = file_size(file)
        if size2 > size:
            size = size2
            basename = os.path.basename(file)  # Só o nome do arquivo
            area = basename[:basename.index('-')]  # Pega até o primeiro '-'
    return area.upper()

# Função que cria o arquivo HTML individual de um professor, se ainda não existir
def create_p_file(prof_name):
    file_name = "../src/p/" + prof_name + '.html'
    if os.path.exists(file_name):
        return
    line = '      var corebr_author = "' + prof_name + '"\n'
    with open(file_name, 'w', encoding="utf-8") as out:
        with open('../src/utils/_authors1.html', 'r', encoding="utf-8") as file1:
            with open('../src/utils/_authors2.html', 'r', encoding="utf-8") as file2:
                out.write(file1.read())
                out.write(line)
                out.write(file2.read())

# Dicionário para armazenar a afiliação institucional de cada professor
inst = {}
reader1 = csv.reader(open("../../data/configs/all-researchers.csv", 'r', encoding="utf-8"))
for p in reader1:
    prof = p[0]
    dept = p[1]
    inst[prof] = dept

# Caminhos dos arquivos profs_top.html e profs_bottm.html
top_path = "../utils/profs_top.html"
bottom_path = "../utils/profs_bottm.html"

# Abre o arquivo onde será gerado o HTML com a lista de professores
out = open('../profs.html', 'w', encoding="utf-8")  # Usando 'w' para sobrescrever o arquivo
out2 = open('../../data/configs/profs/profs.csv', 'w', encoding="utf-8")  # Arquivo CSV para as informações

# Escreve o cabeçalho do arquivo CSV
# out2.write('Name,Institution,Area\n')

# Adiciona o conteúdo de profs_top.html no início do arquivo
with open(top_path, 'r', encoding="utf-8") as file1:
    out.write(file1.read())

# Leitura dos nomes em all-authors.csv
reader2 = csv.reader(open("../../data/configs/profs/all-authors.csv", 'r', encoding="utf-8"))
for p in reader2:
    prof = p[0]
    p2 = prof.replace(" ", "-")
    dept = inst[prof]
    
    # Aqui, chamamos a função get_area() para encontrar a área do professor
    area = get_area(p2)

    # Escreve o nome do professor, com link para a página dele
    out.write('<li>  <a href="https://csindexbr.org/authors.html?p=' + p2 + '">')
    out.write(' ' + prof + '</a>')
    out.write(' <small> (' + dept + ', ' + area + ') </small>')
    out.write('\n')

    # Escreve as informações no arquivo CSV (nome, instituição, área)
    out2.write(f'{prof},{dept},{area}\n')

# Adiciona o conteúdo de profs_bottm.html no final do arquivo
with open(bottom_path, 'r', encoding="utf-8") as file2:
    out.write(file2.read())

# Fecha os arquivos
out.close()
out2.close()