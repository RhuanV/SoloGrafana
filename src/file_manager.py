import csv
import os
import datetime

def criar_arquivo_csv(pasta_base, nome_missao):
    if not os.path.exists(pasta_base):
        os.makedirs(pasta_base)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{pasta_base}/{nome_missao}_{timestamp}.csv"
    
    # Retorna o caminho e cria o arquivo vazio
    with open(filename, 'w', newline='') as f:
        pass 
    
    return filename

def salvar_dados(filename, dados_dict):
    """Escreve uma linha no CSV baseada nas chaves do dicionário"""
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=dados_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(dados_dict)