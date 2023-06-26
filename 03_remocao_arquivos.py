import os # biblioteca para gerenciar pastas
import shutil # biblioteca para remover pastas

# Define os caminhos da pasta a serem excluídas
pasta_download = './downloaded_files'
pasta_dfp = './DFP'

# Verifica se a pasta existe antes de excluí-la
if os.path.exists(pasta_download):
    # Remove a pasta e todos os seus arquivos e subdiretórios
    shutil.rmtree(pasta_download)
else:
    print("A pasta não existe.")

# Verifica se a pasta existe antes de excluí-la
if os.path.exists(pasta_dfp):
    # Remove a pasta e todos os seus arquivos e subdiretórios
    shutil.rmtree(pasta_dfp)
else:
    print("A pasta não existe.")