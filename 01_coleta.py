# Carrega as bibliotecas
import wget # biblioteca para realizar o download de sites 
import pandas as pd # biblioteca para manipulação de dados e data frames
from zipfile import ZipFile # biblioteca para extrair arquivo zipados
import os # biblioteca para gerenciar pastas

# Informações das empresas ------------------------------------------------------------------

# Se o arquivo já existir, o exclui
if os.path.exists('./cad_cia_aberta.csv'):
   os.remove('./cad_cia_aberta.csv')

# Baixa o arquivo de informações de empresas
dest_file = wget.download(url = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv')

# Leitura de arquivo para buscar o código CVM das empresas
info_companies = pd.read_csv(dest_file, sep = ';', encoding = 'latin1', dtype = {'CNPJ_CIA': str})

# Filtra as empresas ativas, bolsas e retira bancos
names_companies = (
                    info_companies[(info_companies['SIT'] == 'ATIVO') &
                             (info_companies['TP_MERC'] == 'BOLSA') &
                             (~info_companies['SETOR_ATIV'].isin(["Bancos", "Intermediação Financeira", "Seguradoras e Corretoras"]))]
                             .sort_values('DENOM_SOCIAL')
                             ['DENOM_SOCIAL']
                    )

## Cria pasta caso não existir!
exist_path = os.path.exists("dados") # Confirma existência
if not exist_path:
   # Cria a pasta
   os.makedirs("dados")

# Salva os nomes das companhias em um arquivo csv
names_companies.to_csv('./dados/names_companies.csv', index = False, sep = ';')

# Realiza os download dos arquivos do DFP ---------------------------------------------------------------------------------------
                       
def download_extract_concatenate_dfp_files(start_year, end_year, financial_statements, path_to_download = "downloaded_files"):
    """
    Função para realizar o download, extração e concatenação de arquivos zipados contendo os dados da Demonstração Financeira
    Padronizada (DFP) de companhias abertas disponibilizados pela Comissão de Valores Mobiliários (CVM).
    
    Parâmetros:
    start_year (int): Ano inicial da coleta dos dados.
    end_year (int): Ano final da coleta dos dados.
    financial_statements (list): Lista de nomes dos arquivos de demonstrativos financeiros que deseja-se concatenar. Consolidado: BPA_con (balanço patrimonial ativo);
     BPP_con (Balanço patrimonial passivo) DRE_con; DFC_MI_con; DFC_MD_CON; DMPL_con.
    path_to_download: string da pasta criada para inserir os arquivos baixados.

    
    Retorna:
    Arquivos .csv no diretório DFP.
    """
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/" 
    # Cria uma lista vazia para inserir os nomes dos arquivos zipados
    arquivo_zipado = []
    
    # Define os nomes dos arquivos zipados de acordo com o range de datas
    for ano in range(start_year, end_year + 1):
        arquivo_zipado.append(f'dfp_cia_aberta_{ano}.zip')

    # Realiza o download dos arquivos zipados de acordo com a url base
    for arquivos in arquivo_zipado:
         ## Cria pasta caso não existir!
        exist_path = os.path.exists(path_to_download) # Confirma existência
        if not exist_path:
        # Cria a pasta
            os.makedirs(path_to_download)
        # Se o arquivo já existir, o exclui
        if os.path.exists(f'{path_to_download}/{arquivos}'):
            os.remove(f'{path_to_download}/{arquivos}')
        wget.download(url + arquivos, out = path_to_download)
        
    # Extrai os arquivos zipados  
    for arquivos in arquivo_zipado:
        ZipFile(f"{path_to_download}/{arquivos}", 'r').extractall('DFP')
    
    # Concatena os dados dos demonstrativos financeiros em um único DataFrame
    for demons in financial_statements:
        arquivo_demonstrativo = pd.DataFrame()
        for ano in range(start_year, end_year + 1):
            arquivo_demonstrativo = pd.concat([arquivo_demonstrativo, pd.read_csv(f'DFP/dfp_cia_aberta_{demons}_{ano}.csv', sep = ';', decimal = ',', encoding = 'ISO-8859-1')]) 
        arquivo_demonstrativo.to_csv(f'DFP/dfp_cia_aberta_{demons}_{start_year}-{end_year}.csv', index = False)

# Coleta os dados
download_extract_concatenate_dfp_files(2010, 2022, ['BPA_con', 'BPP_con', 'DRE_con', 'DFC_MI_con'])