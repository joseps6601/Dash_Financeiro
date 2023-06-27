# Carrega as bibliotecas
import wget # biblioteca para realizar o download de sites 
import pandas as pd # biblioteca para manipulação de dados e data frames
from zipfile import ZipFile # biblioteca para extrair arquivo zipados
import os # biblioteca para gerenciar pastas

# Importa e Trata os dados ---------------------------------------------------

# Lê o arquivo do nomes das companhias e transforma em lista
names_companies = pd.read_csv('./dados/names_companies.csv', sep = ';')['DENOM_SOCIAL'].tolist() # transforma em lista para usar no input do dashboard e filtragem de dados

## Balanço Patrimonial --------------------------------------------------------

# Realiza a leitura do arquivo do BPA
bpa = pd.read_csv('DFP/dfp_cia_aberta_BPA_con_2010-2022.csv')

# Realiza a leitura do arquivo do BP
bpp = pd.read_csv('DFP/dfp_cia_aberta_BPP_con_2010-2022.csv')

# Empilha os dados do BP
bp = pd.concat([bpa, bpp], axis = 0)

# Realiza o filtro das contas contábeis, do código CVM e da ordem do exercício
bp_filtrado = (
                bp[bp.DS_CONTA.isin(["Ativo Total",
                                    "Passivo Total",
                                    "Patrimônio Líquido Consolidado",
                                    "Ativo Circulante",
                                    "Ativo Não Circulante",
                                    "Passivo Circulante",
                                    "Passivo Não Circulante"
                         ]) & bp.DENOM_CIA.isin(names_companies) & (bp.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
                 .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'DS_CONTA', values = 'VL_CONTA')
                 .assign(passivo = lambda x : x['Passivo Total'] - x['Patrimônio Líquido Consolidado'])
                 .reset_index() 
                )

## DRE --------------------------------------------------------

# Realiza a leitura do arquivo
dre = pd.read_csv('DFP/dfp_cia_aberta_DRE_con_2010-2022.csv')

dre_filtrado = ( 
            dre[dre.DS_CONTA.isin(["Receita de Venda de Bens e/ou Serviços",
                                    "Custo dos Bens e/ou Serviços Vendidos",
                                    "Lucro/Prejuízo Consolidado do Período"
                                    ]) 
                                    & dre.DENOM_CIA.isin(names_companies) 
                                    & dre.CD_CONTA.isin(['3.11', '3.01', '3.02']) 
                                    & (dre.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
                .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'DS_CONTA', values = 'VL_CONTA')
                .reset_index()
              )
## DFC --------------------------------------------------------

# Realiza a leitura do arquivo
dfc = pd.read_csv('DFP/dfp_cia_aberta_DFC_MI_con_2010-2022.csv')

dfc_filtrado = (
                    dfc[dfc.DS_CONTA.isin(["Caixa Líquido Atividades Operacionais",
                                    "Caixa Líquido Atividades de Investimento",
                                    "Caixa Líquido Atividades de Financiamento",
                                    "Aumento (Redução) de Caixa e Equivalentes",
                                    "Saldo Inicial de Caixa e Equivalentes",
                                    "Saldo Final de Caixa e Equivalentes"
                         ]) 
                         & dfc.DENOM_CIA.isin(names_companies) 
                         & (dfc.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]
                        .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'DS_CONTA', values = 'VL_CONTA')
                        .reset_index()
                )
# Indicadores --------------------------------------------------------------------

# Junta todos os dados para criar os indicadores
df_dfp = pd.concat([bp, dre], axis = 0)

# Filtra as empresas
df_dfp = df_dfp[df_dfp.DENOM_CIA.isin(names_companies)]

## Indicadores de Liquidez ---------------------
indic_liq = df_dfp[df_dfp.CD_CONTA.isin(["1.01.01", # Caixa
                                        "2.01",    # Passivo Circulante
                                        "1.01",    # Ativo Circulante
                                        "1.01.04", # Estoques
                                        "1.01.07", # Despesas Antecipadas
                                        "1.02",    # Ativo não circulante
                                        "2.02" # Passivo não circulante
                                 ]) 
                                 & (df_dfp.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]

indic_liq = (
    indic_liq
    .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'DS_CONTA', values = 'VL_CONTA')
    .reset_index()
    .assign(liquidez_imediata = lambda x : x['Caixa e Equivalentes de Caixa'] / x['Passivo Circulante'], 
            liquidez_seca = lambda x : (x['Ativo Circulante']  -  x['Estoques'] - x['Despesas Antecipadas']) / x['Passivo Circulante'],
            liquidez_corrente = lambda x : x['Ativo Circulante'] / x['Passivo Circulante'],
            liquidez_geral = lambda x : (x['Ativo Circulante'] + x['Ativo Não Circulante']) / (x['Passivo Circulante'] + x['Passivo Não Circulante'])
            )
    [['DT_REFER', "DENOM_CIA", "liquidez_imediata", "liquidez_seca", "liquidez_corrente", "liquidez_geral"]]
)

# Indicadores de Endividamento -------------------------------------
indic_end = df_dfp[df_dfp.CD_CONTA.isin(["1", # Ativo Total
                                        "2.01", # Passivo Circulante
                                        "2.02", # Passivo não circulante
                                        "2.01.04", # Empréstimos e Financiamento de CP
                                        "2.02.01", # Empréstimos e Financiamento de LP
                                        "2.03", # Patrimônio Líquido
                                        "3.05" # EBIT
                                        ]) 
                                        & (df_dfp.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]

indic_end = (
    indic_end
    .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'CD_CONTA', values = 'VL_CONTA')
    .reset_index()
    .assign(divida_pl = lambda x : (x["2.01.04"] + x["2.02.01"]) / x["2.03"],
            divida_ativos = lambda x :(x["2.01.04"] + x["2.02.01"]) / x["1"],
            divida_ebit = lambda x :(x["2.01.04"] + x["2.02.01"]) / x["3.05"],
            pl_ativos = lambda x : x["2.03"] / x["1"],
            passivos_ativos =  lambda x : (x["2.01"] + x["2.02"]) / x["1"])
    [['DT_REFER', "DENOM_CIA", "divida_pl", "divida_ativos", "divida_ebit", "pl_ativos", "passivos_ativos"]]           
)

# Indicadores de Eficiência --------------------------------------
indic_enf = df_dfp[df_dfp.CD_CONTA.isin(["3.01", # Receita de Venda de Bens e/ou Serviços
                                         "3.03", # Resultado Bruto
                                         "3.05", # EBIT
                                         "3.11"  # Lucro/Prejuízo Consolidado do Período
                                        ]) 
                                        & (df_dfp.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]

indic_enf = (
    indic_enf
    .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'CD_CONTA', values = 'VL_CONTA')
    .reset_index()
    .assign(margem_bruta = lambda x : (x["3.03"]) / x["3.01"] * 100,
            margem_liquida = lambda x : (x["3.11"]) / x["3.01"] * 100,
            margem_ebit = lambda x : (x["3.05"]) / x["3.01"] * 100)
    [['DT_REFER', "DENOM_CIA", "margem_bruta", "margem_liquida", "margem_ebit"]] 
)

# Indicadores de Rentabilidade --------------------------------------
indic_rent = df_dfp[df_dfp.CD_CONTA.isin(["1", # Ativo Total 
                                            "2", # Passivo total
                                            "2.03", # Patrimônio Líquido
                                            "3.05", # EBIT
                                            "3.08", # Imposto de Renda e Contribuição Social sobre o Lucro
                                            "3.11"  # Lucro/Prejuízo Consolidado do Período
                                        ]) 
                                        & (df_dfp.ORDEM_EXERC == 'ÚLTIMO')][["DT_REFER", "DENOM_CIA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]]

indic_rent = (
    indic_rent
    .pivot(index = ['DT_REFER', 'DENOM_CIA'], columns = 'CD_CONTA', values = 'VL_CONTA')
    .reset_index()
    .assign(roic = lambda x : (x["3.05"] - x["3.08"]) / x["2"] * 100,
            roe = lambda x : (x["3.11"]) / x["2.03"] * 100,
            roa = lambda x : (x["3.11"]) / x["1"] * 100)
    [['DT_REFER', "DENOM_CIA", "roic", "roe", "roa"]]
)

# Salva os arquivos de dados para criar o dashboard -----------------------------------------------
## Cria pasta caso não existir!
exist_path = os.path.exists("Dashboard") # Confirma existência
if not exist_path:
   # Cria a pasta
   os.makedirs("Dashboard")

# Salva os arquivos em formato .csv

bp_filtrado.to_csv('Dashboard/bp.csv', index = False, sep = ';', encoding = 'latin1')
dre_filtrado.to_csv('Dashboard/dre.csv', index = False, sep = ';', encoding = 'latin1')
dfc_filtrado.to_csv('Dashboard/dfc.csv', index = False, sep = ';', encoding = 'latin1')
indic_liq.to_csv('Dashboard/indic_liq.csv', index = False, sep = ';', encoding = 'latin1')
indic_end.to_csv('Dashboard/indic_end.csv', index = False, sep = ';', encoding = 'latin1')
indic_enf.to_csv('Dashboard/indic_enf.csv', index = False, sep = ';', encoding = 'latin1')
indic_rent.to_csv('Dashboard/indic_rent.csv', index = False, sep = ';', encoding = 'latin1')
names_companies_df = pd.read_csv('dados/names_companies.csv', sep = ';', encoding = 'latin1')
names_companies_df.to_csv('Dashboard/names_companies.csv', index = False, sep = ';', encoding = 'latin1')
