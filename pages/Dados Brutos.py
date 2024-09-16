import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Carregar estilos do arquivo CSS
with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Conexão com o banco de dados
connection = mysql.connector.connect(
    host='192.168.100.16',
    port='3306',
    database='analise_acidentes',
    user='dataframe',
    password='dataframe123!',
    auth_plugin= 'mysql_native_password'
)
cursor = connection.cursor()

st.title('Dados Brutos')

st.markdown('''    
    Nesta página, você encontrará os dados relativos aos acidentes e incidentes aeronáuticos que foram utilizados para realizar as análises apresentadas. Para facilitar a visualização e compreensão, os dados estão divididos em abas, cada uma representando os diferentes DataFrames usados nas análises.
            
    <span style="font-size: 25px; color:gray">**Importância da Transparência e Acessibilidade dos Dados**</spam>
    
    A disponibilização dos dados brutos é fundamental para garantir a transparência e a credibilidade das análises. Ao compartilhar as informações utilizadas, proporcionamos a oportunidade para que outros pesquisadores, profissionais da área e o público em geral possam verificar, reproduzir e expandir as análises realizadas. Isso não apenas fortalece a confiabilidade dos resultados apresentados, mas também promove um ambiente de colaboração e inovação, onde novas perspectivas e metodologias podem ser exploradas.
            
    <span style="font-size: 25px; color:gray">**Utilidade para a Comunidade**</spam>
            
    A disponibilização destes dados brutos serve não apenas para respaldar as análises apresentadas, mas também como um recurso valioso para a comunidade. O público interessado pode aumentar sua compreensão sobre a segurança aeronáutica e a complexidade das investigações de acidentes.
                                
''', unsafe_allow_html=True)

aba1, aba2, aba3, aba4 = st.tabs(['Tabela de ocorrência', 'Tabela do tipo de ocorrência', 'Tabela de aeronave', 'Tabela de fator contribuinte'])

with aba1:
    cursor.execute('SELECT * FROM ocorrencia')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    st.dataframe(df)
with aba2:
    cursor.execute('SELECT * FROM ocorrencia_tipo')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    st.dataframe(df)
with aba3:
    cursor.execute('SELECT * FROM aeronave')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    st.dataframe(df)
with aba4:
    cursor.execute('SELECT * FROM fator_contribuinte')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=cursor.column_names)
    st.dataframe(df)

