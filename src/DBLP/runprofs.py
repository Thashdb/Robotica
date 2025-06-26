import csv
import glob
import os

# recebe o caminho do arquivo e retorna o numero de linhas
def file_size(file):
    num_lines = sum(1 for line in open(file))
    return num_lines

# para cada professor, verifica o tamnho dos arquivos encontrados
    # determina a area conforme o arquivo com maior numero de lionhas
def get_area(prof):
    size = 0
    area = ""
    for file in glob.glob("../cache/profs/papers/*" + prof + "-papers.csv"):
        size2 = file_size(file)
        if size2 > size:
            size = size2
            area = file[15:file.index('-')]
    return area.upper()


# Função que cria o arquivo HTML individual de um professor, se ainda não existir
# Esse HTML é construído combinando os arquivos _authors1.html e _authors2.html
def create_p_file(prof_name):
    file_name = "../src/p/" + prof_name + '.html'
    if os.path.exists(file_name):
        return
    line = '      var corebr_author = "' + prof_name + '"\n'
    out = open(file_name, 'w')
    file1 = open('../src/_authors1.html', 'r')
    # src\utils\_authors1.html
    file2 = open('../src/_authors2.html', 'r')
    out.write(file1.read())
    out.write(line)
    out.write(file2.read())
    out.close

# Dicionário para armazenar a afiliação institucional de cada professor
inst = {}
reader1 = csv.reader(open("../../data/configs/all-researchers.csv", 'r'))

# Preenche o dicionário inst com nome do professor e sua instituição
for p in reader1:
    prof = p[0]
    dept = p[1]
    inst[prof] = dept

# Abre o arquivo onde será gerado o HTML com a lista de professores
out = open('../profs.html','a')
# Cria arquivo CSV com as informações dos professores (nome, instituição, área)
out2 = open('../../data/configs/profs/profs.csv','w')

# out3 = open('../html/sitemap_p.txt','w')

# Leitura dos nomes em all-authors.csv
reader2 = csv.reader(open("../../data/configs/profs/all-authors.csv", 'r'))


# Para cada professor listado em all-authors, escreve seu link em profs.html e registra info em profs.csv
for p in reader2:
    prof = p[0]
    p2 = prof.replace(" ", "-")
    dept = inst[prof]
    area = get_area(p2)
    out.write('<li>  <a hre f="https://csindexbr.org/authors.html?p=' + p2 + '">')
    out.write(' ' + prof + '</a>')
    out.write(' <small> (' + dept + ', ' + area + ') </small>')
    out.write('\n')

    out2.write(prof)
    out2.write(',')
    out2.write(dept)
    out2.write(',')
    out2.write(area)
    out2.write('\n')
    #create_p_file(p2)
#    out3.write('https://csindexbr.org/authors.html?p=' + p2 + '\n')
out.close
out2.close
#out3.close
