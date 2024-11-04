import streamlit as st
import base64

st.set_page_config(layout = 'wide')

# Carregar a imagem e converter para base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
img_base64 = get_base64_of_bin_file('images/sky5.jpg')

background_imagem = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}
</style>
"""
st.markdown(background_imagem, unsafe_allow_html=True)

# Carregar estilos do arquivo CSS
with open("styles.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title('Análise de Acidentes Aéreos')

st.markdown('''
Esse site será um dashboard para ser usado como uma ferramenta de visualização de dados que obtemos atráves do CENIPA, permitindo pesquisar as ocorrências aeronáuticas ocorridas no Brasil desde 2007 até 2023 reportadas no Portal Único. Os dados são exibidos em forma de gráficos e tabelas, que são dinamicamente modificados conforme filtros de pesquisa aplicados pelo próprio usuário.

O CENIPA exerce a função de Autoridade de Investigação e, no âmbito da aviação civil, as atividades de prevenção, de competência do CENIPA, estão limitadas às investigações de acidentes e incidentes aeronáuticos e às tarefas relacionadas com a gestão dos sistemas de reporte voluntário, conforme disposto no § 6º do Art. nº 1 do Decreto nº 9540, de 25 de outubro de 2018, que dispõe sobre o Sistema de Investigação e Prevenção de Acidentes Aeronáuticos (SIPAER).

Todos os Relatórios Finais publicados pelo CENIPA são disponibilizados à Agência Nacional de Aviação Civil (ANAC) e ao Departamento de Controle do Espaço Aéreo (DECEA) para que as análises técnico-científicas das investigações sejam utilizadas como fonte de dados e informações, objetivando a identificação de perigos e a avaliação de riscos, conforme disposto no Programa Brasileiro para a Segurança Operacional da Aviação Civil (PSO-BR).
''', unsafe_allow_html=True)
