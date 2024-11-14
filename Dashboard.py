import streamlit as st  
import requests
import pandas as pd
import plotly.express as px

# .\venv\Scripts/activate
# streamlit run app.py -- para poder rodar o Streamlit

# Opção de widemode por padrão
st.set_page_config(layout = 'wide')

# Função para formatar o número, colocando prefixo e a unidade
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'Mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} Milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

# Filtro no sidebar - como minha API permite filtrar por padrão, é possível eu colocar
# esse filtro do side bar já aqui antes de importar a API para o Streamlit
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

# Brasil não é um filtro da minha tabela, mas ele representa todas as regiões, então é
# necessário fazer essa condicional para que nada seja filtrado quando clicar no BR. 
if regiao == 'Brasil':
    regiao = ''

# Se não deixar a check box clicada, aparecerá um slider para selecionar a qtd. de anos
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

# Passando as modificações para URL
# O .lower é para transformar o nome das regiões em letra minúsculas, pois a API só aceita
# letras minúsculas, e na lista "regioes" havíamos colocado com letra maiúscula.
query_string = {'regiao': regiao.lower(), 'ano': ano}

# O segundo parâmetro "params = " é para aplicar os filtros que eu fiz acima
response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())

# Tratando os dados de datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Fazendo o filtro de vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

# Caso o filtro de vendedores esteja selcionado, essa condiçã abaixo vai filtrar
# as infos dos códigos abaixo
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Agrupamento da receita - fazendo como cópia para não perder as infos de lat e lon
# Tabelas de receita:
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False) 

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

# Tabela de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

# Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

# Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                    lat = 'lat',
                                    lon = 'lon',
                                    scope = 'south america',
                                    size = 'Preço',
                                    template = 'seaborn',
                                    hover_name = 'Local da compra',
                                    hover_data = {'lat': False, 'lon': False},
                                    title = 'Receita por estado')
###################################
fig_receita_mensal = px.line(receita_mensal,
                            x = 'Mes',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, receita_mensal.max()), # Importante o gráfico sempre começar em 0
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')
###################################
# O .head() após o df é para eu pegar apenas o top 5 estados
fig_receita_estados = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True, # Colocar o valor das receitas em cima de cada coluna
                            title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')
###################################
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True, 
                                title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')
###################################
# Gráficos do desafio
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )
###################################
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')
###################################
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')
###################################
fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

# Visualização no Strealit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    # Criando colunas para colocar as métricas lado a lado
    # Além da criação das colunas no código abaixo, é necessário colocar o "with"
    # acima da métrica, conforme mais abaixo
    coluna1, coluna2 = st.columns(2)
    # Criando colunas
    with coluna1:
        # Como adicionar métricas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # Adicionando gráfico na coluna 1
        # O "use_container_width = True" é para o gráfico sempre respeitar a coluna 
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)


    with coluna2:
        # Como o "Shape" traz os dados das linhas do df, se eu colocar 0 ele vai me trazer a
        # quantidade de linhas totais do df, que é a primeira informação mostrada nessa função
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        # Adicionando gráficos na coluna 2
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    # Criando colunas
    with coluna1:
        # Como adicionar métricas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        # Como o "Shape" traz os dados das linhas do df, se eu colocar 0 ele vai me trazer a
        # quantidade de linhas totais do df, que é a primeira informação mostrada nessa função
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    # Criando botão para selecionar vendedores
    # 2 é o mínimo, 10 é o máximo e 5 é padrão
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    # Criando colunas
    with coluna1:
        # Como adicionar métricas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # Preciso criar o gráfico de vendedores aqui porque eu coloquei o input para
        # selecionar os vendedores nessa aba.
        # Mesmo criando uma tabela lá, note que ainda tive que fazer ajustes aqui 
        # (tratamento de dados)
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        # Como o "Shape" traz os dados das linhas do df, se eu colocar 0 ele vai me trazer a
        # quantidade de linhas totais do df, que é a primeira informação mostrada nessa função
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        # Mesmo gráfico da coluna 1 acima, porém ao invés de ser receita(sum) 
        # é a quantidade (count).
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)
        
# Colocando um DataFrame no Stremlit
# st.dataframe(dados)