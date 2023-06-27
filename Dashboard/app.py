# Importa as bibliotecas
## Shiny
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget
## Gráficos
import plotly.express as px
import plotly.graph_objs as go
## Dados e manipulação
import numpy as np
import pandas as pd

# Lê o arquivo do nomes das companhias e transforma em lista
names_companies = pd.read_csv('Dashboard/names_companies.csv', sep = ';')['DENOM_SOCIAL'].tolist()

# Realiza a leitura dos arquivos
bp = pd.read_csv('Dashboard/bp.csv', sep = ';', encoding = 'latin1')
dre = pd.read_csv('Dashboard/dre.csv', sep = ';', encoding = 'latin1')
dfc = pd.read_csv('Dashboard/dfc.csv',sep = ';', encoding = 'latin1')
indic_liq = pd.read_csv('Dashboard/indic_liq.csv', sep = ';', encoding = 'latin1')
indic_end = pd.read_csv('Dashboard/indic_end.csv', sep = ';', encoding = 'latin1')
indic_enf = pd.read_csv('Dashboard/indic_enf.csv', sep = ';', encoding = 'latin1')
indic_rent = pd.read_csv('Dashboard/indic_rent.csv', sep = ';', encoding = 'latin1')

# Parte 1: Interface do usuário
app_ui = ui.page_fluid(
   # Título
   ui.panel_title(title = "Dashboard de Indicadores e Demonstrativos"),
   # Sidebar (painel lateral)
   ui.layout_sidebar(
    ui.panel_sidebar(
        # Texto do sidebar
        ui.p(""),
        # Escolha dos ativos e Pesos do portfólio
        ui.row(
                ui.column(6,
                      ui.input_select(id = "companies",
                                      label = "Selecione as companhias disponíveis",
                                      choices =  names_companies,
                                      multiple = False,
                                      selectize = True,
                                      selected = "VALE S.A."
                      )
                 )
          )
         ),
        # Cria o painel dos gráfios
        ui.panel_main(
                # Página de navegação
                ui.navset_tab(
                # Página dos demonstrativos
                ui.nav("Demonstrativos",
                # Balanço Patrimonial
                ui.row(
                    output_widget("bp_chart")
                ),
                # DRE
                ui.row(
                    output_widget("dre_chart")
                     )  
                  ),
                # Página dos Indicadores de Liquidez
                ui.nav("Indicadores de Liquidez",
                ui.row(
                    output_widget("indic_liq_corrente_chart")
                ),
                ui.row(
                    output_widget("indic_liq_imediata_chart")                                                      
                ),
                ui.row(
                    output_widget("indic_liq_seca_chart")                                                      
                ),                                
                ui.row(
                    output_widget("indic_liq_geral_chart")                                                      
                )
                ),
                # Página dos Indicadores de Endividamento
                ui.nav("Indicadores de Endividamento",
                ui.row(
                    output_widget("indic_end_dividapl_chart")
                ),
                ui.row(
                    output_widget("indic_end_dividaativos_chart")                                                      
                ),
                ui.row(
                    output_widget("indic_end_dividaebit_chart")                                                      
                ),                                
                ui.row(
                    output_widget("indic_end_plativos_chart")                                                      
                ),
                ui.row(
                    output_widget("indic_end_passivosativos_chart")                                                      
                )                
                ),
                # Página dos Indicadores de Eficiência
                ui.nav("Indicadores de Eficiência",
                ui.row(
                    output_widget("indic_enf_margembruta_chart")
                ),
                ui.row(
                    output_widget("indic_enf_margemliq_chart")                                                      
                ),
                ui.row(
                    output_widget("indic_enf_margemebit_chart")                                                      
                )
                ),
                # Página dos Indicadores de Rentabilidade
                ui.nav("Indicadores de Rentabilidade",
                ui.row(
                    output_widget("indic_rent_roic_chart")
                ),
                ui.row(
                    output_widget("indic_rent_roe_chart")                                                      
                ),
                ui.row(
                    output_widget("indic_rent_roa_chart")                                                      
                )
                )                    
            )
        )
    )
)

# Parte 2: Lógica de servidor
def server(input, output, session):
# Output: construção dos gráficos
# Balanço Patrimonial -------------------------------------------  
    @output
    @render_widget
    def bp_chart():
        # Filtra os dados pela empresa selecionada
        bp_filtered = bp[bp['DENOM_CIA'] == input.companies()]
        # Cria o gráfico do Balanço Patrimonial
        fig1 = go.Figure()
        fig1.add_scatter(x = bp_filtered['DT_REFER'], y = bp_filtered['Ativo Total'], mode = 'lines+markers', name = 'Ativo', 
                        line = dict(color = 'black', width = 3))  
        fig1.add_scatter(x = bp_filtered['DT_REFER'], y = bp_filtered['passivo'], mode = 'lines+markers', name = 'Passivo', 
                        line = dict(color = '#eace3f', width = 3))      
        fig1.add_bar(x = bp_filtered['DT_REFER'], y = bp_filtered['Ativo Circulante'], name = 'Ativo Circulante', marker_color = '#5f487c')
        fig1.add_bar(x = bp_filtered['DT_REFER'], y = bp_filtered['Ativo Não Circulante'], name = 'Ativo Não Circulante', marker_color = '#224f20')
        fig1.add_bar(x = bp_filtered['DT_REFER'], y = bp_filtered['Passivo Circulante'], name = 'Passivo Circulante', marker_color = '#666666')
        fig1.add_bar(x = bp_filtered['DT_REFER'], y = bp_filtered['Passivo Não Circulante'], name = 'Passivo Não Circulante', marker_color = '#b22200')
        fig1.update_layout(title_text = 'Balanço Patrimonial', legend = dict(x = 1, y = 1), 
                          xaxis_title = 'Data', yaxis_title = 'R$', template = 'plotly_white', hovermode = 'x unified', barmode = 'stack')
        return go.FigureWidget(fig1)

# DRE -----------------------------------------------
    @output
    @render_widget
    def dre_chart():
        # Filtra os dados pela empresa selecionada
        dre_filtered = dre[dre['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da DRE
        fig2 = go.Figure()
        fig2.add_bar(x = dre_filtered['DT_REFER'], y = dre_filtered['Receita de Venda de Bens e/ou Serviços'], name = 'Receitas', marker_color = '#282f6b')
        fig2.add_bar(x = dre_filtered['DT_REFER'], y = dre_filtered['Custo dos Bens e/ou Serviços Vendidos'], name = 'Custo', 
                    marker_color = '#b22200')
        fig2.add_scatter(x = dre_filtered['DT_REFER'], y = dre_filtered['Lucro/Prejuízo Consolidado do Período'], mode = 'lines+markers', name = 'Lucro/Prejuízo', 
                         line = dict(color = 'orange', width = 4))
        fig2.update_layout(title_text = 'DRE', legend = dict(x = 1, y = 1), 
                           xaxis_title = 'Data', yaxis_title = 'R$', template = 'plotly_white', hovermode = 'x unified', barmode = 'stack')
        return go.FigureWidget(fig2)
    
# Indicadores de Liquidez -------------------------------------------    
    @output
    @render_widget
    def indic_liq_corrente_chart():
        # Filtra os dados pela empresa selecionada
        indic_liq_filtered = indic_liq[indic_liq['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Liquidez Corrente
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x = indic_liq_filtered['DT_REFER'], y = indic_liq_filtered['liquidez_corrente'], 
                                  name = 'Liquidez Corrente', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig3.update_layout(title_text = "Liquidez Corrente", 
                           template = 'plotly_white')
        return go.FigureWidget(fig3)
    
    @output
    @render_widget
    def indic_liq_imediata_chart():
        # Filtra os dados pela empresa selecionada
        indic_liq_filtered = indic_liq[indic_liq['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Liquidez Imediata
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x = indic_liq_filtered['DT_REFER'], y = indic_liq_filtered['liquidez_imediata'], 
                                  name = 'Liquidez Imediata', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig4.update_layout(title_text = "Liquidez Imediata", 
                           template = 'plotly_white')
        return go.FigureWidget(fig4)
    
    @output
    @render_widget
    def indic_liq_seca_chart():
        # Filtra os dados pela empresa selecionada
        indic_liq_filtered = indic_liq[indic_liq['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Liquidez Seca
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x = indic_liq_filtered['DT_REFER'], y = indic_liq_filtered['liquidez_seca'], 
                                  name = 'Liquidez Seca', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig5.update_layout(title_text = "Liquidez Seca", 
                           template = 'plotly_white')
        return go.FigureWidget(fig5)

    @output
    @render_widget    
    def indic_liq_geral_chart():
        # Filtra os dados pela empresa selecionada
        indic_liq_filtered = indic_liq[indic_liq['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Liquidez Geral
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(x = indic_liq_filtered['DT_REFER'], y = indic_liq_filtered['liquidez_geral'], 
                                  name = 'Liquidez Geral', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig6.update_layout(title_text = "Liquidez Geral", 
                           template = 'plotly_white')
        return go.FigureWidget(fig6)

# Indicadores de Endividamento -------------------------------------------
    @output
    @render_widget
    def indic_end_dividapl_chart():
        # Filtra os dados pela empresa selecionada
        indic_end_filtered = indic_end[indic_end['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Divida/PL
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(x = indic_end_filtered['DT_REFER'], y = indic_end_filtered['divida_pl'], 
                                  name = 'Dívida/PL', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig7.update_layout(title_text = "Dívida/PL", 
                           template = 'plotly_white')
        return go.FigureWidget(fig7)
    @output
    @render_widget
    def indic_end_dividaativos_chart():
         # Filtra os dados pela empresa selecionada
        indic_end_filtered = indic_end[indic_end['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Dívida/Ativos
        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(x = indic_end_filtered['DT_REFER'], y = indic_end_filtered['divida_ativos'], 
                                  name = 'Dívida/Ativos', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig8.update_layout(title_text = "Dívida/Ativos", 
                           template = 'plotly_white')
        return go.FigureWidget(fig8)

    @output
    @render_widget
    def indic_end_dividaebit_chart():
         # Filtra os dados pela empresa selecionada
        indic_end_filtered = indic_end[indic_end['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Dívida/EBIT
        fig9 = go.Figure()
        fig9.add_trace(go.Scatter(x = indic_end_filtered['DT_REFER'], y = indic_end_filtered['divida_ebit'], 
                                  name = 'Dívida/EBIT', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig9.update_layout(title_text = "Dívida/EBIT", 
                           template = 'plotly_white')
        return go.FigureWidget(fig9)

    @output
    @render_widget    
    def indic_end_plativos_chart():
         # Filtra os dados pela empresa selecionada
        indic_end_filtered = indic_end[indic_end['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da PL/Ativos
        fig10 = go.Figure()
        fig10.add_trace(go.Scatter(x = indic_end_filtered['DT_REFER'], y = indic_end_filtered['pl_ativos'], 
                                  name = 'PL/Ativos', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig10.update_layout(title_text = "PL/Ativos", 
                           template = 'plotly_white')
        return go.FigureWidget(fig10)

    @output
    @render_widget
    def indic_end_passivosativos_chart():
        # Filtra os dados pela empresa selecionada
        indic_end_filtered = indic_end[indic_end['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Passivos/Ativos
        fig11 = go.Figure()
        fig11.add_trace(go.Scatter(x = indic_end_filtered['DT_REFER'], y = indic_end_filtered['passivos_ativos'], 
                                  name = 'Passivos/Ativos', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig11.update_layout(title_text = "Passivos/Ativos",
                           template = 'plotly_white')
        return go.FigureWidget(fig11)

# Indicadores de Eficiência -------------------------------------------
    @output
    @render_widget
    def indic_enf_margembruta_chart():
        # Filtra os dados pela empresa selecionada
        indic_enf_filtered = indic_enf[indic_enf['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Margem Bruta
        fig12 = go.Figure()
        fig12.add_trace(go.Scatter(x = indic_enf_filtered['DT_REFER'], y = indic_enf_filtered['margem_bruta'], 
                                  name = 'Margem Bruta', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig12.update_layout(title_text = "Margem Bruta",
                           template = 'plotly_white')
        return go.FigureWidget(fig12)

    @output
    @render_widget
    def indic_enf_margemliq_chart():
          # Filtra os dados pela empresa selecionada
        indic_enf_filtered = indic_enf[indic_enf['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Margem Líquida
        fig13 = go.Figure()
        fig13.add_trace(go.Scatter(x = indic_enf_filtered['DT_REFER'], y = indic_enf_filtered['margem_liquida'], 
                                  name = 'Margem Líquida', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig13.update_layout(title_text = "Margem Líquida",
                           template = 'plotly_white')
        return go.FigureWidget(fig13)

    @output
    @render_widget
    def indic_enf_margemebit_chart():
        # Filtra os dados pela empresa selecionada
        indic_enf_filtered = indic_enf[indic_enf['DENOM_CIA'] == input.companies()]
        # Cria o gráfico da Margem EBIT
        fig14 = go.Figure()
        fig14.add_trace(go.Scatter(x = indic_enf_filtered['DT_REFER'], y = indic_enf_filtered['margem_ebit'], 
                                  name = 'Margem EBIT', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig14.update_layout(title_text = "Margem EBIT",
                           template = 'plotly_white')
        return go.FigureWidget(fig14)

# Indicadores de Rentabilidade -------------------------------------------
    @output
    @render_widget
    def indic_rent_roic_chart():
        # Filtra os dados pela empresa selecionada
        indic_rent_filtered = indic_rent[indic_rent['DENOM_CIA'] == input.companies()]
        # Cria o gráfico do ROIC
        fig15 = go.Figure()
        fig15.add_trace(go.Scatter(x = indic_rent_filtered['DT_REFER'], y = indic_rent_filtered['roic'], 
                                  name = 'ROIC', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig15.update_layout(title_text = "ROIC",
                           template = 'plotly_white')
        return go.FigureWidget(fig15)

    @output
    @render_widget
    def indic_rent_roe_chart():
        # Filtra os dados pela empresa selecionada
        indic_rent_filtered = indic_rent[indic_rent['DENOM_CIA'] == input.companies()]
        # Cria o gráfico do ROE
        fig16 = go.Figure()
        fig16.add_trace(go.Scatter(x = indic_rent_filtered['DT_REFER'], y = indic_rent_filtered['roe'], 
                                  name = 'ROA', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig16.update_layout(title_text = "ROA",
                           template = 'plotly_white')
        return go.FigureWidget(fig16)

    @output
    @render_widget
    def indic_rent_roa_chart():
        # Filtra os dados pela empresa selecionada
        indic_rent_filtered = indic_rent[indic_rent['DENOM_CIA'] == input.companies()]
        # Cria o gráfico do ROA
        fig17 = go.Figure()
        fig17.add_trace(go.Scatter(x = indic_rent_filtered['DT_REFER'], y = indic_rent_filtered['roa'], 
                                  name = 'ROE', mode = 'lines+markers', line = dict(color = 'royalblue', width = 4)))
        fig17.update_layout(title_text = 'ROE',
                           template = 'plotly_white')
        return go.FigureWidget(fig17)

# Parte 3: aplicação
app = App(app_ui, server)