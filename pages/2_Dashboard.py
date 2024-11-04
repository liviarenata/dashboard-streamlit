import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(layout = 'wide')

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
    auth_plugin='mysql_native_password'
)
cursor = connection.cursor()

st.sidebar.header("Filtros") # Filtros na barra lateral 
anos_selecionados = st.sidebar.slider( # Filtro de ano
    "Intervalo de anos:",
    min_value=2007,
    max_value=2023,
    value=(2007, 2023),
    step=1
)

# Filtro de classificação de ocorrência
classificacao_selecionada = st.sidebar.multiselect(
    "Classificação de ocorrência(s):",
    options=['ACIDENTE', 'INCIDENTE', 'INCIDENTE GRAVE']
)

# Filtro de UF (Estados)
ufs_selecionadas = st.sidebar.multiselect(
    "Selecione o(s) estado(s):",
    options=['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'CE', 'PE', 'AM', 'DF'],
)

def consultar_dados_classificacao(): # Gráfico 1
    classificacao_condicao = ''
    if classificacao_selecionada:
        classificacao_condicao = f"AND ocorrencia_classificacao IN ({', '.join([repr(c) for c in classificacao_selecionada])})"
    query = f'''
        SELECT ocorrencia_classificacao, COUNT(*) AS total_ocorrencias 
        FROM ocorrencia 
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN '{anos_selecionados[0]}-01-01' AND '{anos_selecionados[1]}-12-31'
        {classificacao_condicao}
        GROUP BY ocorrencia_classificacao
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['ocorrencia_classificacao', 'Total de Ocorrências'])
    return df

def consultar_dados_tipo_fator():  # Gráfico 2
    query = '''
        SELECT
            COUNT(DISTINCT f.codigo_ocorrencia3) AS total_ocorrencias,  
            f.fator_area AS tipo_ocorrencia,
            o.ocorrencia_tipo_categoria AS fator_contribuinte
        FROM fator_contribuinte AS f
        JOIN ocorrencia_tipo AS o ON f.codigo_ocorrencia3 = o.codigo_ocorrencia1
        JOIN ocorrencia AS oc ON oc.codigo_ocorrencia1 = o.codigo_ocorrencia1
        WHERE STR_TO_DATE(oc.ocorrencia_dia, '%d/%m/%Y') BETWEEN %s AND %s
        GROUP BY f.fator_area, o.ocorrencia_tipo_categoria 
    '''
    params = (f'{anos_selecionados[0]}-01-01', f'{anos_selecionados[1]}-12-31')
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['total_ocorrencias', 'tipo_ocorrencia', 'fator_contribuinte'])
    return df

def consultar_dados_mapa(): # Gráfico 3
    uf_condicao = ''
    if ufs_selecionadas:
        uf_condicao = f"AND ocorrencia_uf IN ({', '.join(['\'' + uf + '\'' for uf in ufs_selecionadas])})"
    query = f'''
        SELECT ocorrencia_uf, COUNT(*) AS total_ocorrencias
        FROM ocorrencia
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN '{anos_selecionados[0]}-01-01' AND '{anos_selecionados[1]}-12-31'
        {uf_condicao}
        GROUP BY ocorrencia_uf
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['ocorrencia_uf', 'Total de Ocorrências'])
    return df

def consultar_dados_por_ano(): # Gráfico 4
    classificacao_condicao = ''
    if classificacao_selecionada:
        classificacao_condicao = f"AND ocorrencia_classificacao IN ({', '.join(['\'' + c + '\'' for c in classificacao_selecionada])})"
    query = f'''
        SELECT 
            YEAR(STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y')) AS ano, 
            ocorrencia_classificacao, 
            COUNT(*) AS total_ocorrencias
        FROM ocorrencia
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN '{anos_selecionados[0]}-01-01' AND '{anos_selecionados[1]}-12-31'
        {classificacao_condicao}
        GROUP BY ano, ocorrencia_classificacao
        ORDER BY ano
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['ano', 'ocorrencia_classificacao', 'total_ocorrencias'])
    return df

def consultar_fatores_operacionais():  # Gráfico 5
    query = '''
        SELECT 
            f.fator_area AS "Fator Operacional",
            COUNT(*) AS "Quantidade de Ocorrências"
        FROM fator_contribuinte AS f
        JOIN ocorrencia AS o ON f.codigo_ocorrencia3 = o.codigo_ocorrencia3
        WHERE STR_TO_DATE(o.ocorrencia_dia, '%d/%m/%Y') BETWEEN %s AND %s
        GROUP BY f.fator_area
    '''
    params = (f'{anos_selecionados[0]}-01-01', f'{anos_selecionados[1]}-12-31')
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['Fator Operacional', 'Quantidade de Ocorrências'])
    return df

def consultar_tipos_ocorrencia(): # Gráfico 6
    query = f'''
        SELECT ocorrencia_tipo_categoria, COUNT(*) AS total_ocorrencias
        FROM ocorrencia_tipo
        JOIN ocorrencia ON ocorrencia_tipo.codigo_ocorrencia1 = ocorrencia.codigo_ocorrencia1
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN '{anos_selecionados[0]}-01-01' AND '{anos_selecionados[1]}-12-31'
        GROUP BY ocorrencia_tipo_categoria
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['ocorrencia_tipo_categoria', 'Total de Ocorrências'])
    return df

def consultar_dados_ocorrencia_tipo_veiculo():  # Gráfico 7
    classificacao_condicao = ''
    if classificacao_selecionada:
        classificacao_condicao = f"AND o.ocorrencia_classificacao IN ({', '.join(['\'' + c + '\'' for c in classificacao_selecionada])})"
    
    query = f'''
        SELECT 
            o.ocorrencia_classificacao, 
            a.aeronave_tipo_veiculo,
            COUNT(*) AS total_ocorrencias
        FROM aeronave AS a
        JOIN ocorrencia AS o ON a.codigo_ocorrencia2 = o.codigo_ocorrencia2
        WHERE STR_TO_DATE(o.ocorrencia_dia, '%d/%m/%Y') BETWEEN %s AND %s
        {classificacao_condicao}
        GROUP BY o.ocorrencia_classificacao, a.aeronave_tipo_veiculo
    '''
    params = (f'{anos_selecionados[0]}-01-01', f'{anos_selecionados[1]}-12-31')
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['ocorrencia_classificacao', 'aeronave_tipo_veiculo', 'Total de Ocorrências'])
    # Agrupando os tipos de veículos
    df['aeronave_tipo_veiculo'] = df['aeronave_tipo_veiculo'].apply(
        lambda x: x if x in ['AVIÃO', 'HELICÓPTERO'] else 'OUTROS'
    )
    return df

def consultar_dados_aeronave_tipo_operacao():  # Gráfico 8
    query = '''
        SELECT aeronave_tipo_operacao, COUNT(*) AS total_ocorrencias
        FROM aeronave
        JOIN ocorrencia ON aeronave.codigo_ocorrencia2 = ocorrencia.codigo_ocorrencia2
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN %s AND %s
        GROUP BY aeronave_tipo_operacao
    '''
    params = (f'{anos_selecionados[0]}-01-01', f'{anos_selecionados[1]}-12-31')
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['aeronave_tipo_operacao', 'Total de Ocorrências'])
    df = df.sort_values(by='Total de Ocorrências', ascending=False).head(5)
    return df

def consultar_dados_fatalidade_nivel_dano(): # Gráfico 9
    query = f'''
        SELECT 
            CASE 
                WHEN aeronave_nivel_dano IN ('DESTRUÍDA', 'LEVE', 'NENHUM', 'SUBSTANCIAL') THEN aeronave_nivel_dano
                ELSE 'OUTROS'
            END AS tipo_dano,
            SUM(aeronave_fatalidades_total) AS total_fatalidades
        FROM aeronave
        JOIN ocorrencia ON aeronave.codigo_ocorrencia2 = ocorrencia.codigo_ocorrencia2
        WHERE STR_TO_DATE(ocorrencia_dia, '%d/%m/%Y') BETWEEN '{anos_selecionados[0]}-01-01' AND '{anos_selecionados[1]}-12-31'
        GROUP BY tipo_dano
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    df = pd.DataFrame(resultados, columns=['Tipo de Dano', 'Total de Fatalidades'])
    return df

st.title('Análise de acidentes aéreos')

aba1, aba2, aba3  = st.tabs(['Panorama', 'Acidentes', 'Operações Aéreas'])

with aba1:
    df_classificacao = consultar_dados_classificacao()
    df_tipo_fator = consultar_dados_tipo_fator()
    df_mapa = consultar_dados_mapa()

    st.write('') # Quebrar linha

    # Gráfico 1: Quantidade de Acidentes por Classificação
    with st.expander('Quantidade de acidentes por classificação'):
        st.markdown('''
            <span style='font-family: serif'>
            Este gráfico mostra a quantidade de acidentes classificados por tipo. As categorias de classificação incluem: Acidente, Incidente e Incidente Grave. 
            
            <br><span style="font-size: 25px;">**Acidentes**</span>
                    
            Toda ocorrência aeronáutica relacionada à operação de uma aeronave tripulada, havida entre o momento em que uma pessoa nela embarca com a intenção de realizar um voo até o momento em que todas as pessoas tenham dela desembarcado ou; no caso de uma aeronave não tripulada, toda ocorrência havida entre o momento que a aeronave está pronta para se movimentar, com a intenção de voo, até a sua parada total pelo término do voo, e seu sistema de propulsão tenha sido desligado e, durante os quais, pelo menos uma das situações abaixo ocorra:
                    
            **a)** uma pessoa sofra lesão grave ou venha a falecer como resultado de: estar na aeronave;
            ter contato direto com qualquer parte da aeronave, incluindo aquelas que dela tenham se desprendido; ou ser submetida à exposição direta do sopro de hélice, de rotor ou de escapamento de jato, ou às suas consequências.
                    
            **NOTA 1 -** Exceção será feita quando as lesões, ou óbito, resultarem de causas naturais, forem autoinfligidas ou infligidas por terceiros, ou forem causadas a pessoas que embarcaram clandestinamente e se acomodaram em área que não as destinadas aos passageiros e tripulantes.
                    
            **NOTA 2 -** As lesões decorrentes de um Acidente Aeronáutico que resultem óbito em até 30 dias após a data da ocorrência são consideradas lesões fatais. b) a aeronave tenha falha estrutural ou dano que:
            afete a resistência estrutural, o seu desempenho ou as suas características de voo; ou normalmente exija a realização de grande reparo ou a substituição do componente afetado.
                
            **NOTA 3 -** Exceção será feita para falha ou danos quando limitados a um único motor (incluindo carenagens ou acessórios), para danos limitados às hélices, às pontas de asa, às antenas, aos probes, aletas, aos pneus, aos freios, às rodas, às carenagens do trem, aos painéis, às portas do trem de pouso, aos para-brisas, aos amassamentos leves e pequenas perfurações no revestimento da aeronave, ou danos menores às pás do rotor principal e de cauda, ao trem de pouso, e aqueles danos resultantes de colisão com granizo ou ave (incluindo perfurações no radome).
                    
            **NOTA 4 -** O Adendo E do Anexo 13 à Convenção sobre Aviação Civil Internacional apresenta uma lista de danos que podem ser considerados exemplos de acidentes aeronáuticos. Uma tradução livre desta lista encontra- se no Anexo B desta Norma.
                    
            **c)** a aeronave seja considerada desaparecida ou esteja em local inacessível. NOTA 5 - Uma aeronave será considerada desaparecida quando as buscas oficiais forem suspensas e os destroços não forem encontrados.
            
            <br><span style="font-size: 25px;">**Incidentes**</span>
                    
            Uma ocorrência aeronáutica, não classificada como um acidente, associada à operação de uma aeronave, que afete ou possa afetar a segurança da operação.
                    
            **NOTA 1 -** Os tipos de incidentes que são de interesse principal à ICAO para estudos de prevenção de acidentes estão listados no Adendo C do Anexo 13 à Convenção sobre Aviação Civil Internacional. Uma tradução livre desta lista encontra-se na NSCA 3-6 e NSCA 3-13. 
                    
            <br><span style="font-size: 25px;">**Incidentes Graves**</span>
                    
            Incidente aeronáutico envolvendo circunstâncias que indiquem que houve elevado risco de acidente relacionado à operação de uma aeronave que, no caso de aeronave tripulada, ocorre entre o momento em que uma pessoa nela embarca, com a intenção de realizar um voo, até o momento em que todas as pessoas tenham dela desembarcado; ou, no caso de uma aeronave não tripulada, ocorre entre o momento em que a aeronave está pronta para se movimentar, com a intenção de voo, até a sua parada total pelo término do voo, e seu sistema de propulsão tenha sido desligado.
                    
            **NOTA 1 -** A diferença entre o incidente grave e o acidente está apenas nas consequências.
                    
            **NOTA 2 -** O Adendo C do Anexo 13 à Convenção sobre Aviação Civil Internacional apresenta uma lista de situações que podem ser consideradas exemplos de incidentes aeronáuticos graves. Essa lista encontra-se transcrita, em anexo, na NSCA 3-6 e NSCA 3-13.
            </span>
        ''', unsafe_allow_html=True)
    
    grafico_classificacao = px.bar(
        df_classificacao,
        x='ocorrencia_classificacao',
        y='Total de Ocorrências',
        title='Quantidade de acidentes por classificação',
        color='ocorrencia_classificacao',
        labels={
            'ocorrencia_classificacao': 'Classificação do Acidente',
            'Total de Ocorrências': 'Contagem de Ocorrências'
        }
    )
    grafico_classificacao.update_traces(texttemplate='%{y}', textposition='inside')
    grafico_classificacao.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(grafico_classificacao, use_container_width=True)
    
    # Gráfico 2: Tipo de Ocorrência por Fator Contribuinte
    with st.expander('Tipo de ocorrência por fator contribuinte'):
        st.markdown('''
            <span style='font-family: serif'>
            Este gráfico mostra os tipos de ocorrências de acidentes e seus respectivos fatores contribuintes.
            Ele destaca as áreas principais que contribuíram para cada tipo de acidente.
            </span>
        ''', unsafe_allow_html=True)

    grafico_tipo_fator = px.bar(
        df_tipo_fator,
        x='tipo_ocorrencia',
        y='total_ocorrencias',  
        color='fator_contribuinte',
        title='Tipo de ocorrência por fator contribuinte',
        barmode='group',
        labels={
            'tipo_ocorrencia': 'Tipo de Ocorrência do Acidente',
            'fator_contribuinte': 'Fator Contribuinte',
            'total_ocorrencias': 'Ocorrências'  
        }
    )

    st.write('') # Quebrar linha
    st.write('') # Quebrar linha

    st.plotly_chart(
        grafico_tipo_fator.update_layout(
            height=600,
            width=1500,  
            legend=dict(
                orientation='v',
                xanchor='right',
                yanchor='top',
                x=0.5,
                y=-0.3,
                traceorder='normal',
                font=dict(size=100)
            ),
            showlegend=False, # Remove a descrição
            margin=dict(l=0, r=0, t=30, b=0)
        )
    )
    
    st.write('') # Quebrar linha
    st.write('') # Quebrar linha    

    #  Gráfico 3: Mapa de estados com ocorrências de acidentes
    with st.expander('Mapa de estados com ocorrências de acidentes'):
        st.markdown('''
            <span style='font-family: serif'>
            Este mapa mostra a distribuição de ocorrências de acidentes (incluindo incidentes e acidentes graves) por estado.
            </span>
        ''', unsafe_allow_html=True)
    
    mapa_ocorrencias = px.choropleth(
        df_mapa,
        geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations='ocorrencia_uf',
        featureidkey="properties.sigla",
        color='Total de Ocorrências',
        color_continuous_scale="blues",
        scope="south america",
        title='Distribuição de ocorrências de acidentes por estado',
        height=650
    )
    mapa_ocorrencias.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(mapa_ocorrencias, use_container_width=True)

with aba2:
    df_ano = consultar_dados_por_ano()
    df_fatores = consultar_fatores_operacionais()
    df_tipos_ocorrencia = consultar_tipos_ocorrencia()

    # Gráfico 4: Quantidade de Acidentes, Incidentes e Incidentes Graves por Ano
    grafico_por_ano = px.line(
        df_ano,
        x='ano',
        y='total_ocorrencias',
        color='ocorrencia_classificacao',
        title='Quantidade de ocorrências por ano',
        labels={
            'ano': 'Ano',
            'total_ocorrencias': 'Total de Ocorrências',
            'ocorrencia_classificacao': 'Classificação da Ocorrência'
        }
    )
    st.plotly_chart(grafico_por_ano, use_container_width=True)

    # Gráfico 5: Aspecto do Fator Contribuinte
    fator_contribuinte = px.pie(df_fatores, 
                                    values='Quantidade de Ocorrências', 
                                    names='Fator Operacional',
                                    title='Aspecto do fator contribuinte')
    st.plotly_chart(fator_contribuinte)

    # Gráfico 6: 10 Maiores tipos de ocorrência
    df_top_tipos_ocorrencia = df_tipos_ocorrencia.sort_values(by='Total de Ocorrências', ascending=False).head(10)
    tipos_ocorrencia = px.pie(df_top_tipos_ocorrencia,
                                  values='Total de Ocorrências', 
                                  names='ocorrencia_tipo_categoria',
                                  title='10 Maiores tipos de ocorrência')
    st.plotly_chart(tipos_ocorrencia)

with aba3: 
    df_ocorrencia_tipo_veiculo = consultar_dados_ocorrencia_tipo_veiculo()
    df_aeronave_tipo_operacao = consultar_dados_aeronave_tipo_operacao()
    df_fatalidade_nivel_dano = consultar_dados_fatalidade_nivel_dano()

    # Gráfico 7: Detalhamento das operações aéreas
    grafico_ocorrencia_veiculo = px.bar(
        df_ocorrencia_tipo_veiculo,
        x='aeronave_tipo_veiculo',
        y='Total de Ocorrências',
        color='ocorrencia_classificacao',
        title='Detalhamento das operações aéreas',
        barmode='group',
        labels={
            'aeronave_tipo_veiculo': 'Tipo de Veículo',
            'Total de Ocorrências': 'Total de Ocorrências',
            'ocorrencia_classificacao': 'Classificação da Ocorrência'
        }
    )
    grafico_ocorrencia_veiculo.update_traces(texttemplate='%{y}', textposition='none')
    grafico_ocorrencia_veiculo.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(grafico_ocorrencia_veiculo, use_container_width=True)

    # Gráfico 8: Tipos de operações que mais ocorrem acidentes
    with st.expander('Tipos de operações que mais ocorrem acidentes'):
        st.markdown('''
            <span style='font-family: serif'>
            
            <br><span style="font-size: 25px;">**Operação**</span>
                    
            **Regular:** Doméstico ou Internacional (TPR): aeronaves empregadas em serviços de transporte aéreo público, realizado por pessoas jurídicas brasileiras, por concessão e mediante remuneração, de passageiro, carga ou mala postal, de âmbito regional, nacional ou internacional.
                    
            **Privada:** Serviços Aéreos Privados (TPP): aeronaves empregadas em serviços realizados sem remuneração, em benefício dos proprietários ou operadores, compreendendo as atividades aéreas de recreio ou desportivas, de transporte reservado ao proprietário ou operador, de serviços aéreos especializados realizados em benefício exclusivo do proprietário ou operador, não podendo efetuar quaisquer serviços aéreos remunerados.
                    
            **Táxi Aéreo:** Aeronaves empregadas em serviços de transporte aéreo público não-regular de passageiro ou carga, realizados por empregadas em serviços de transporte aéreo público não-regular de passageiro ou carga, realizados por pessoa física ou jurídica brasileira, autorizada, mediante remuneração convencionada entre o usuário e o transportador, visando a proporcionar atendimento imediato, independente de horário, percurso ou escala.    
            
            **Instrução:** Aeronaves empregadas na instrução, treinamento e adestramento de voo pelos aeroclubes, clubes ou escolas de aviação civil proprietárias da aeronave, podendo ser usada, ainda, para prestar tais serviços a pessoal de outras organizações sob contrato aprovado pela ANAC e como aeronave administrativa da entidade sua proprietária.
            Experimental: Aeronaves visando à certificação na categoria experimental, para os usos previstos no RBAC 21.191 e no RBAC 21.195.                    

            **Agrícola:** Serviços aéreos especializados públicos (SAE) ou operações privadas de fomento ou proteção da agricultura em geral;
            Instrução: Aeronaves empregadas na instrução, treinamento e adestramento de voo pelos aeroclubes, clubes ou escolas de aviação civil proprietárias da aeronave, podendo ser usada, ainda, para prestar tais serviços a pessoal de outras organizações sob contrato aprovado pela ANAC e como aeronave administrativa da entidade sua proprietária.                                    
            </span>
        ''', unsafe_allow_html=True)

    aeronave_operacao = px.pie(
        df_aeronave_tipo_operacao,
        values='Total de Ocorrências',
        names='aeronave_tipo_operacao',
        title='Tipos de operações que mais ocorrem acidentes'
    )
    st.plotly_chart(aeronave_operacao)

    # Gráfico 9: Quantidade de fatalidades por nível de dano da aeronave
    with st.expander('Quantidade de fatalidades por nível de dano da aeronave'):
        st.markdown('''
            <span style='font-family: serif'>
                    
            **Destruída:** A aeronave sofreu danos irrecuperáveis e é considerada perda total. A estrutura e componentes principais não são restauráveis.
                    
            **Substancial:** Danos consideráveis foram sofridos, o que deve exigir reparos extensivos. No entanto, a aeronave ainda é considerada reparável e pode ser restaurada para operação.
         
            **Leve:** Danos mínimos que geralmente não comprometem significativamente a integridade estrutural ou a capacidade operacional da aeronave.

            **Nenhum:** A aeronave não sofreu nenhum dano perceptível. Isso indica que o evento foi tão leve que não causou qualquer impacto físico ou estrutural.
                    
            **Outros:** Inclui danos que não se encaixam em nenhuma das classificações padrão ou que podem estar em avaliação.                                                                                        
            </span>
        ''', unsafe_allow_html=True)
    df_fatalidade_nivel_dano['Tipo de Dano'] = df_fatalidade_nivel_dano['Tipo de Dano'].map({
        'DESTRUÍDA': 'Destruída',
        'LEVE': 'Leve',
        'NENHUM': 'Nenhum',
        'SUBSTANCIAL': 'Substancial',
        'OUTROS': 'Outros'
    })
    fatalidade_dano = px.pie(
        df_fatalidade_nivel_dano,
        values='Total de Fatalidades',
        names='Tipo de Dano',
        title='Quantidade de fatalidades por nível de dano da aeronave'
    )
    st.plotly_chart(fatalidade_dano)

connection.close()
