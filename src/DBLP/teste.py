import os
import xmltodict

def journals_without_pages(directory):
    journals = set()

    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            path = os.path.join(directory, filename)
            with open(path, "r", encoding="utf-8") as file:
                try:
                    data = xmltodict.parse(file.read())
                    
                    # Acessa a raiz do XML, que é <dblpperson>
                    records = data.get("dblpperson", {}).get("r", [])
                    
                    # Se houver só um <r>, transforma em lista
                    if isinstance(records, dict):
                        records = [records]
                    
                    for r in records:
                        article = r.get("article")
                        if article:
                            if "journal" in article and "pages" not in article:
                                journals.add(article["journal"])

                except Exception as e:
                    print(f"Erro ao processar {filename}: {e}")

    return journals


# Caminho da pasta onde estão os XMLs de autores
pasta = "../../data/cache/dblp"

# Chamada da função
resultado = journals_without_pages(pasta)

# Exibe os nomes dos jornais sem número de páginas
print("Jornais sem número de páginas:")
for journal in sorted(resultado):
    print(journal)
