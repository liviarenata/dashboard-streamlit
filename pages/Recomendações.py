import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Carregar estilos do arquivo CSS
with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Conexão com o banco de dados
connection = mysql.connector.connect(
    host='localhost',
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

cursor.execute('SELECT * FROM recomendacao')
data = cursor.fetchall()
df = pd.DataFrame(data, columns=cursor.column_names)
st.dataframe(df)
