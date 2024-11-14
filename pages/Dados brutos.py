# Criando uma nova página para visualizar os dados brutos:
# Não esquecer de criar um nova pasta no diretório com o nome "pages" obrigatoriamente,
# e criar um novo arquivo com o nome da página que eu quero.

import streamlit as st
import requests
import pandas as pd
import time

# Opção de widemode por padrão
st.set_page_config(layout = 'wide')

# Deixando a planilha salva sem filtros no cache para não haver a necessidade de converter
@st.cache_data

# Função para converter o df em CSV e poder fazer o download.
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# Função para mensagem de sucesso após download
def mensagem_sucesso():
    sucesso = st.sucess('Arquivo baixado com sucesso!', icon = '✅')
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criação de filtros:

# O segundo "list(dados.columns)" é uma lista com os valores padrões que eu quero que
# mantenha selecionado no momento incial do multiselect
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Criando filtros da barra laterial
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    # É possível escolher um valor mínimo e um máximo, ao invés de um valor específico, com
    # esse último parâmetro "(0, 5000)". Ou seja, um valor entre 0 e 5000;
    # Importante dizer que é necessário que esteja dentro de uma tupla dois parenteses: (())
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))
with st.sidebar.expander('Data da compra'):
    # Função para pegar a data mínima do DF e a data máxima do DF.
    # Importante dizer que é necessário que esteja dentro de uma tupla dois parenteses: (())
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# Referente ao preco, vamos selecionar os valores da coluna preco e o @preco[0] e @preco [1]
# são os valores mínimos e máximos da variável preço do filtro acima no sidebar.
# O "Data de compra" por possuir espaços, precisa ser colocado entre crase.
 
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Importante alterar o nome do data frame para o que eu criei filtrado "dados_filtrados".
# Se deixar o nome original "dados" ele não será filtrado. 
st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em CSV', data = converte_csv(dados_filtrados), file_name= nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
