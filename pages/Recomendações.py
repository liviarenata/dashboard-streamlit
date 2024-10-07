import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Carregar estilos do arquivo CSS
with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Conexão com o banco de dados
connection = mysql.connector.connect(
    host='177.174.97.130',
    port='3306',
    database='analise_acidentes',
    user='dataframe',
    password='dataframe123!',
    auth_plugin= 'mysql_native_password'
)
cursor = connection.cursor()

st.title('Recomendações')

st.markdown('''    
    As recomendações emitidas pela ANAC (Agência Nacional de Aviação Civil) e pela ABAG (Associação Brasileira de Aviação Geral) após cada acidente aéreo desempenham um papel fundamental na segurança e na prevenção de novos incidentes na aviação. Essas orientações, geralmente baseadas em investigações detalhadas sobre as causas dos acidentes, têm como objetivo identificar falhas técnicas, operacionais ou humanas que contribuíram para o evento. A importância de seguir essas recomendações pode ser explicada por vários fatores:
            
    <span style="font-size: 25px; color:gray">**Prevenção de Acidentes Futuros**</spam>
    
    Cada recomendação é uma resposta direta a uma falha identificada no sistema de aviação, seja na manutenção de aeronaves, no treinamento de pilotos, na operação de voos ou nas políticas de segurança. Ao adotar essas recomendações, o setor de aviação pode implementar melhorias que ajudam a evitar que o mesmo tipo de acidente aconteça novamente, protegendo vidas e preservando bens materiais.
            
    <span style="font-size: 25px; color:gray">**Melhoria Contínua na Aviação**</spam>
            
    A indústria aeronáutica é caracterizada por uma constante evolução tecnológica e operacional. As recomendações ajudam as empresas e profissionais da aviação a se adaptarem a essas mudanças, atualizando procedimentos e práticas para que o setor opere com o máximo de segurança e eficiência.
    
    <span style="font-size: 25px; color:gray">**Segurança**</spam>
            
    A aviação opera dentro de uma cultura de segurança rigorosa, onde cada detalhe pode impactar a vida de passageiros e tripulação. Seguir as recomendações é uma forma de promover essa cultura, fortalecendo o compromisso de todos os envolvidos com a integridade dos voos.
''', unsafe_allow_html=True)

st.divider()  # Adiciona uma linha horizontal

# Consulta ao banco de dados para obter as recomendações
cursor.execute('SELECT * FROM recomendacao')
data = cursor.fetchall()
df = pd.DataFrame(data, columns=cursor.column_names)
# st.dataframe(df)

# Inicializar variável de controle para o índice
if 'id' not in st.session_state:
    st.session_state.id = 0

def proxima_recomendacao():
    if st.session_state.id < len(df) - 1:
        st.session_state.id += 1

def recomendacao_anterior():
    if st.session_state.id > 0:
        st.session_state.id -= 1

def buscar_recomendacao_por_id(codigo_ocorrencia4):
    resultado = df[df['codigo_ocorrencia4'] == codigo_ocorrencia4]
    if not resultado.empty:
        st.session_state.id = resultado.id[0]
    else:
        st.warning(f"ID {codigo_ocorrencia4} não encontrado.")
id_pesquisado = st.text_input('ID da Recomendação', value='')
if st.button('Buscar'):
    buscar_recomendacao_por_id(id_pesquisado)

st.write('')  # Quebrar linha
st.write('')  # Quebrar linha

# Botões de navegação
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.button('⬅️ Anterior', on_click=recomendacao_anterior)
with col3:
    st.button('Próxima ➡️', on_click=proxima_recomendacao)

# Exibir a recomendação atual com base na navegação
id = st.session_state.id
recomendacao = df.iloc[id]

st.markdown(f"""
<div style="background-color:#f0f0f5; padding:20px; border-radius:10px; margin-top:20px; border: 1px solid #ccc;">
    <h3 style="color:#2c3e50;">Recomendação #{id + 1}</h3>
    <p><b>Ocorrência:</b> {recomendacao['codigo_ocorrencia4']}</p>
    <p><b>Conteúdo:</b> {recomendacao['recomendacao_conteudo']}</p>
    <p><b>Status:</b> {recomendacao['recomendacao_status']}</p>
    <p><b>Destinatário:</b> {recomendacao['recomendacao_destinatario']} ({recomendacao['recomendacao_destinatario_sigla']})</p>
</div>
""", unsafe_allow_html=True)

# Exibir a posição atual
st.write(f"Recomendação {id + 1} de {len(df)}")