#!/usr/bin/env python
# coding: utf-8

# # <center>Identificação de itens - Medicamentos </center>
# ---

# ## 1.0 Cálculo de similaridade - Tabela própria

# ### 1.1 Importando bibliotecas

# In[ ]:


#banco de dados
import cx_Oracle

#tratamento
import pandas as pd
import numpy  as np
from datetime import datetime
import os

#pre-processamento
from unidecode import unidecode
from nltk.corpus import stopwords

#pre-selecao
from collections import Counter
from collections import defaultdict

#calculo de similaridade
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher
import re


# ### 1.2 Importando dados do banco

# #### 1.2.1 Definição de variáveis

# In[ ]:


# Caminho da pasta onde o arquivo Excel está localizado
pasta_arquivo = r'\\Fscorp05\monitoramento$\08.Desenvolvimento\10_Similaridade_por_Descricao\MED\01_TEMPLATE_MED'

# Listar todos os arquivos da pasta
arquivos = os.listdir(pasta_arquivo)

# Filtrar apenas os arquivos com extensão .xlsx
arquivos_xlsx = [arquivo for arquivo in arquivos if arquivo.endswith('.xlsx')]

# Garantir que existe ao menos um arquivo Excel na pasta
if len(arquivos_xlsx) > 0:
    # Selecionar o primeiro arquivo Excel da lista
    caminho_arquivo = os.path.join(pasta_arquivo, arquivos_xlsx[0])
    
    # Ler o arquivo Excel e criar o DataFrame
    base_tab_propria_full = pd.read_excel(caminho_arquivo)


# In[ ]:


base_tab_propria_full


# In[ ]:


# Solicita a entrada do usuário - Hospital
var_hospital = base_tab_propria_full['HOSPITAL'][0]


# In[ ]:


# Solicita a entrada do usuário - Código
var_codigo = base_tab_propria_full['CODIGO_RETORNO'][0]


# In[ ]:


base_tab_propria = base_tab_propria_full[['COD_TAB_PROPRIA', 'DESCRICAO_TAB_PROPRIA', 'VALOR_UNIT']]
base_tab_propria


# #### 1.2.2 Conectando ao banco de dados

# In[ ]:


print("Iniciei conexão ao banco")


# In[ ]:


#conectando ao banco de dados

uid = "*****"   # usuário
pwd = "*****"   # senha
db =  "*****"    # string de conexão do Oracle, configurado no
                # cliente Oracle, arquivo tnsnames.ora
    
connection = cx_Oracle.connect(uid+"/"+pwd+"@"+db) #cria a conexão
cursor = connection.cursor() # cria um cursor


# In[ ]:


if var_codigo == 'COD_SISTEMA':
    
    # Query
    querystring_cadastro = """ 
    SELECT /*+PARALLEL(10)*/ CODIGO AS CODIGO_SISTEMA, DESCRICAO_CADASTRO, REF_FAB_PADRAO AS REFERENCIA
    FROM TASY.CADASTRO_SEM_DUPLICADOS 
    WHERE HOSPITAL_CORRIGIDO = :1 AND TIPO = 'MED' AND BLOQUEADO = 'N'
    GROUP BY CODIGO, DESCRICAO_CADASTRO, REF_FAB_PADRAO
    """
    
    # Executar a query com variáveis
    cursor.execute(querystring_cadastro, (var_hospital,))
    
else:
    # Query
    querystring_cadastro = """ 
    SELECT /*+PARALLEL(10)*/ A.CODIGO AS COD_P12, A.DESCRICAO_CADASTRO, B.REFERENCIA, B.FABRICANTE
    FROM TASY.CADASTRO_SEM_DUPLICADOS A 
    LEFT JOIN TASY.BASE_PROTHEUS B ON LPAD(B.CORPORATIVO, 10, 0) = LPAD(A.CODIGO, 10, 0)
    WHERE A.HOSPITAL_CORRIGIDO LIKE '%Hospital P12%' AND A.TIPO = 'MED' AND B.STATUS = 'Desbloqueado'
    GROUP BY A.CODIGO, A.DESCRICAO_CADASTRO, B.REFERENCIA, B.FABRICANTE
    """

    # Execute the query with the parameter as a tuple
    cursor.execute(querystring_cadastro, (var_hospital,))
    

# Obter os nomes das colunas
nome_colunas = [row[0] for row in cursor.description]

# Criar um DataFrame pandas com os dados retornados
base_cadastro = pd.DataFrame(cursor.execute(str(querystring_cadastro)), columns=nome_colunas)
base_cadastro


# In[ ]:


print("Carreguei os dados")


# ### 1.3 Pré - processamento

# Trata-se da remoção de caracteres especiais, pontuações, acentuações e stop words. Mantemos apenas caracteres alfanuméricos e espaços em branco. O objetivo é limpar o texto para facilitar o processamento subsequente.

# In[ ]:


#remove stop words
def remove_stop_words_portuguese(texto):
    stop_words = set(stopwords.words('portuguese'))
    
    # Mantenha a palavra 'sem' na lista de stop words
    stop_words.remove('sem') if 'sem' in stop_words else None
    
    palavras = word_tokenize(texto, language='portuguese')
    
    palavras_filtradas = [palavra for palavra in palavras if palavra.lower() not in stop_words]
    
    return ' '.join(palavras_filtradas)


# In[ ]:


def preprocess_texto(texto):
    # Remove a acentuação
    texto = unidecode(texto)
    # Substitui vírgulas por pontos
    texto = texto.replace(',', '.')
    # Substitui caracteres especiais por espaços - (exceto o ponto entre números)
    texto = re.sub(r'(?<!\d)\.(?!\d)|[^a-zA-Z0-9.\s]', ' ', texto)
    # Substitui múltiplos espaços por um único espaço
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


# In[ ]:


def separar_termos(texto):
    # Processa o texto para remoção de acentuação e caracteres especiais
    texto = preprocess_texto(texto)
    # Adiciona espaço antes e depois de cada dígito seguido de letra e letra seguida de dígito
    texto = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', texto)
    texto = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', texto)
    # Adiciona espaço antes e depois de vírgulas
    #texto = re.sub(r',', ' , ', texto)
    # Substitui múltiplos espaços por um único espaço
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


# In[ ]:


# Aplica a função a cada linha do DataFrame usando apply
base_cadastro['DESCRICAO_TRATADA'] = base_cadastro['DESCRICAO_CADASTRO'].apply(remove_stop_words_portuguese).apply(separar_termos).str.upper()
base_cadastro

# Aplica a função a cada linha do DataFrame usando apply
base_tab_propria['DESCRICAO_TRATADA'] = base_tab_propria['DESCRICAO_TAB_PROPRIA'].apply(remove_stop_words_portuguese).apply(separar_termos).str.upper()
base_tab_propria


# In[ ]:


# listas de descrições
lista_cadastro = base_cadastro['DESCRICAO_TRATADA'].unique()
lista_tab_propria = base_tab_propria['DESCRICAO_TRATADA'].unique()


# ### 1.4 Seleção de itens - Tabela própria

# In[ ]:


# Inicializa um dicionário para armazenar os dados
data_tab_propria = defaultdict(list)

# Conjunto para rastrear combinações já adicionadas
combinacoes_ja_adicionadas = set()

# Itera sobre cada item na lista_tab_propria
for tab_propria_item in lista_tab_propria:
    tab_propria_palavras = set(tab_propria_item.split())

    # Lista temporária para armazenar combinações com 1 palavra em comum
    combinacoes_1_palavra = []

    # Itera sobre cada item na lista_cadastro
    for cadastro_item in lista_cadastro:
        cadastro_palavras = set(cadastro_item.split())

        # Calcula o número de palavras em comum
        palavras_comum = len(tab_propria_palavras.intersection(cadastro_palavras))

        # Cria a chave da combinação
        combinacao = (tab_propria_item, cadastro_item)

        # Prioriza 2 ou mais palavras em comum
        if palavras_comum >= 2:
            if combinacao not in combinacoes_ja_adicionadas:
                data_tab_propria['item_tab_propria'].append(tab_propria_item)
                data_tab_propria['item_cadastro'].append(cadastro_item)
                data_tab_propria['qtd_palavras_comum_tab_propria'].append(palavras_comum)
                combinacoes_ja_adicionadas.add(combinacao)
        # Caso com 1 palavra em comum, armazena para possível adição futura
        elif palavras_comum == 1:
            if combinacao not in combinacoes_ja_adicionadas:
                combinacoes_1_palavra.append((tab_propria_item, cadastro_item, palavras_comum))

    # Adiciona combinações de 1 palavra em comum apenas se não houver nenhuma com 2 ou mais
    for tab_propria_item, cadastro_item, palavras_comum in combinacoes_1_palavra:
        if (tab_propria_item, cadastro_item) not in combinacoes_ja_adicionadas:
            data_tab_propria['item_tab_propria'].append(tab_propria_item)
            data_tab_propria['item_cadastro'].append(cadastro_item)
            data_tab_propria['qtd_palavras_comum_tab_propria'].append(palavras_comum)
            combinacoes_ja_adicionadas.add((tab_propria_item, cadastro_item))


# In[ ]:


df_similaridade_tab_propria = pd.DataFrame(data_tab_propria)


# In[ ]:


df_similaridade_tab_propria


# In[ ]:


# Criar colunas temporárias para a primeira palavra
df_similaridade_tab_propria['primeira_palavra_tab_propria'] = df_similaridade_tab_propria['item_tab_propria'].str.split().str[0]
df_similaridade_tab_propria['primeira_palavra_cadastro'] = df_similaridade_tab_propria['item_cadastro'].str.split().str[0]

# Filtrar os casos onde as primeiras palavras são iguais
df_similaridade_tab_propria = df_similaridade_tab_propria[
    df_similaridade_tab_propria['primeira_palavra_tab_propria'] == df_similaridade_tab_propria['primeira_palavra_cadastro']
]

# Opcional: Remover as colunas temporárias (se não forem mais necessárias)
df_similaridade_tab_propria.drop(['primeira_palavra_tab_propria', 'primeira_palavra_cadastro'], axis=1, inplace=True)

# Redefinir o índice do DataFrame
df_similaridade_tab_propria = df_similaridade_tab_propria.reset_index(drop=True)

df_similaridade_tab_propria
# In[ ]:


print("Fim - Pré seleção tabela própria")


# ### 1.5 Cálculo da similaridade - Tabela própria

# In[ ]:


def calcular_similaridade_tab_propria(row, threshold=0.8):
    
    # Seleciona apenas palavras que contêm somente letras
    palavras_tab_propria = {palavra for palavra in row['item_tab_propria'].split() if palavra.isalpha()}
    palavras_cadastro = {palavra for palavra in row['item_cadastro'].split() if palavra.isalpha()}
      
    # Função para calcular a similaridade de sequência entre duas palavras
    def similaridade_sequencia(palavra1, palavra2):
        seq_matcher = SequenceMatcher(None, palavra1, palavra2)
        return seq_matcher.ratio()
        
    # Função para verificar se duas palavras são similares com base no limiar
    def palavras_similares(palavra1, palavra2, threshold=0.8):
        if palavra1.isalpha() and palavra2.isalpha():
            return (
                len(set(palavra1) & set(palavra2)) / len(set(palavra1)) >= threshold and
                similaridade_sequencia(palavra1, palavra2) >= threshold
            )
        return False

    # Armazena as palavras já contadas
    palavras_contadas = set()

    # Calcula a quantidade de palavras em item_tab_propria que têm pelo menos 80% das letras em comum com item_cadastro
    qtd_palavras_comuns = 0
    for palavra1 in palavras_tab_propria:
        for palavra2 in palavras_cadastro:
            if palavra1 not in palavras_contadas and palavras_similares(palavra1, palavra2, threshold):
                qtd_palavras_comuns += 1
                palavras_contadas.add(palavra1)  # Marca a palavra como contada
    
    # Calcula o resultado desejado
    similaridade = qtd_palavras_comuns / len(palavras_tab_propria) if palavras_tab_propria else 0
    
    return pd.DataFrame({
        'similaridade_tab_prop': [similaridade],
        'qtd_palavras_comum_ajustada_tab_prop': [qtd_palavras_comuns]
    })


# In[ ]:


def verificar_primeira_palavra_tab_propria(row):
    # Dividindo as descrições em palavras
    palavras_tab_propria = row['item_tab_propria'].split()
    palavras_cadastro = row['item_cadastro'].split()
    
    # Extraindo as 4 primeiras palavras de cada item
    palavras_tab_propria_relevantes = palavras_tab_propria[:4]
    palavras_cadastro_relevantes = palavras_cadastro[:4]
    
    # Definindo pesos e normalização baseados no número de palavras em item_tab_propria
    num_palavras = len(palavras_tab_propria)
    
    if num_palavras >= 4:
        pesos = [4, 3, 2, 1]
        divisor = 10
    elif num_palavras == 3:
        pesos = [3, 2, 1]
        divisor = 6
    elif num_palavras == 2:
        pesos = [2, 1]
        divisor = 3
    elif num_palavras == 1:
        pesos = [1]
        divisor = 1
    else:
        return 0  # Se não houver palavras, a pontuação é zero
    
    # Calculando a soma ponderada das correspondências por posição
    soma_ponderada = sum(pesos[i] for i in range(len(palavras_tab_propria_relevantes))
                         if i < len(palavras_cadastro_relevantes) 
                         and palavras_tab_propria_relevantes[i] == palavras_cadastro_relevantes[i])
    
    # Normalizar a pontuação pela soma total dos pesos
    pontuacao = soma_ponderada / divisor
    
    return pontuacao


# In[ ]:


def calcular_similaridade_medidas_tab_propria(row):
    palavras_tab_propria = set(row['item_tab_propria'].split()) 
    palavras_cadastro = set(row['item_cadastro'].split())       

    # Função para calcular a similaridade de sequência entre duas palavras
    def similaridade_sequencia(palavra1, palavra2):
        seq_matcher = SequenceMatcher(None, palavra1, palavra2)
        return seq_matcher.ratio()
    
    def palavras_nao_alfabeticas_similares(palavra1, palavra2):
        def contem_digito_e_letra(palavra):
            return any(char.replace('.', '', 1).isdigit() for char in palavra) and any(char.isalpha() for char in palavra)
        
        # Verifica se ambas as palavras são compostas apenas por dígitos
        if palavra1.replace('.', '', 1).isdigit() and palavra2.replace('.', '', 1).isdigit():
            return similaridade_sequencia(palavra1, palavra2) == 1
        
        # Verifica se ambas as palavras contêm tanto letras quanto dígitos
        if contem_digito_e_letra(palavra1) and contem_digito_e_letra(palavra2):
            # Verifica se todas as letras de palavra1 estão em palavra2
            if len(set(palavra1) & set(palavra2)) == len(set(palavra1)):
                # Verifica a similaridade de sequência
                return similaridade_sequencia(palavra1, palavra2) == 1
    
        return False

    # Calcula a quantidade de palavras em item_tab_propria que têm 100% das letras em comum com item_cadastro
    qtd_palavras_comuns = sum(
        1 for palavra1 in palavras_tab_propria
        for palavra2 in palavras_cadastro
        if palavras_nao_alfabeticas_similares(palavra1, palavra2)
    )

    def palavra_e_medida(palavra):
        return palavra.replace('.', '', 1).isdigit() or \
               (any(char.isdigit() for char in palavra) and any(char.isalpha() for char in palavra))


    # Calcula o divisor como o número de palavras em item_tab_propria que são medidas
    divisor = sum(1 for palavra in palavras_tab_propria if palavra_e_medida(palavra))

    # Calcula o resultado desejado
    similaridade_medidas = qtd_palavras_comuns / divisor if divisor > 0 else 0

    return similaridade_medidas


# In[ ]:


# Aplicar a função à coluna desejada
#similaridade_tab_prop e qtd_palavras_comum_ajustada_tab_prop
df_similaridade_tab_propria[['similaridade_tab_prop', 'qtd_palavras_comum_ajustada_tab_prop']] = pd.concat(df_similaridade_tab_propria.apply(calcular_similaridade_tab_propria, axis=1).tolist(), ignore_index=True)


# In[ ]:


#peso_primeira_palavra_tab_prop
df_similaridade_tab_propria['peso_primeira_palavra_tab_prop'] = df_similaridade_tab_propria.apply(verificar_primeira_palavra_tab_propria, axis=1)


# In[ ]:


#similaridade_medidas_tab_prop
df_similaridade_tab_propria['similaridade_medidas_tab_prop'] = df_similaridade_tab_propria.apply(calcular_similaridade_medidas_tab_propria, axis=1)


# In[ ]:


# Aplicando a lógica condicional
df_similaridade_tab_propria['similaridade_media_tab_prop'] = np.where(
    (df_similaridade_tab_propria['similaridade_medidas_tab_prop'] == 0) &  # Condição 1: similaridade_medidas_tab_pro == 0
    (df_similaridade_tab_propria['item_tab_propria'].apply(lambda x: all(char.isalpha() or char.isspace() for char in x))),       # Condição 2: item_tab_propria contém apenas letras
    # Condição2: verifica se tem letras e espaços
    
    # Se a condição for verdadeira
    
    (df_similaridade_tab_propria['similaridade_tab_prop'] * 4 +  
     df_similaridade_tab_propria['peso_primeira_palavra_tab_prop'] * 6) / 10,
    
    # Se a condição for falsa
    (df_similaridade_tab_propria['similaridade_tab_prop'] * 2 + 
     df_similaridade_tab_propria['peso_primeira_palavra_tab_prop'] * 6 + 
     df_similaridade_tab_propria['similaridade_medidas_tab_prop'] * 2) / 10)


# In[ ]:


#df_similaridade_tab_propria['similaridade_final_tab_prop']
df_similaridade_tab_propria['similaridade_final_tab_prop'] = df_similaridade_tab_propria['similaridade_media_tab_prop']


# In[ ]:


df_similaridade_tab_propria


# In[ ]:


print("Fim - Cálculo da similaridade da tabela própria")


# In[ ]:


df_similaridade_tab_propria


# ## 2.0 Cálculo de similaridade - Cadastro

# ### 2.1 Seleção de itens - Cadastro

# In[ ]:


# Inicializa um dicionário para armazenar os dados
data_cadastro = defaultdict(list)

# Conjunto para rastrear combinações já adicionadas
combinacoes_ja_adicionadas_cad = set()

# Itera sobre cada item na lista_tab_propria
for cadastro_item in lista_cadastro:
    cadastro_palavras = set(cadastro_item.split())

    # Lista temporária para armazenar combinações com 1 palavra em comum
    combinacoes_1_palavra_cad = []

    # Itera sobre cada item na lista_cadastro
    for tab_propria_item in lista_tab_propria:
        tab_propria_palavras = set(tab_propria_item.split())

        # Calcula o número de palavras em comum
        palavras_comum_cad = len(cadastro_palavras.intersection(tab_propria_palavras))

        # Cria a chave da combinação
        combinacao_cad = (cadastro_item, tab_propria_item)

        # Prioriza 2 ou mais palavras em comum
        if palavras_comum_cad >= 2:
            if combinacao_cad not in combinacoes_ja_adicionadas_cad:
                data_cadastro['item_cadastro'].append(cadastro_item)
                data_cadastro['item_tab_propria'].append(tab_propria_item)
                data_cadastro['qtd_palavras_comum_cadastro'].append(palavras_comum_cad)
                combinacoes_ja_adicionadas_cad.add(combinacao_cad)
        # Caso com 1 palavra em comum, armazena para possível adição futura
        elif  palavras_comum_cad == 1:
            if combinacao_cad not in combinacoes_ja_adicionadas_cad:
                combinacoes_1_palavra_cad.append((cadastro_item, tab_propria_item, palavras_comum_cad))

    # Adiciona combinações de 1 palavra em comum apenas se não houver nenhuma com 2 ou mais
    for cadastro_item, tab_propria_item, palavras_comum_cad in combinacoes_1_palavra_cad:
        if (cadastro_item, tab_propria_item) not in combinacoes_ja_adicionadas_cad:
            data_cadastro['item_cadastro'].append(cadastro_item)
            data_cadastro['item_tab_propria'].append(tab_propria_item)
            data_cadastro['qtd_palavras_comum_cadastro'].append(palavras_comum_cad)
            combinacoes_ja_adicionadas_cad.add((cadastro_item, tab_propria_item))


# In[ ]:


df_similaridade_cadastro = pd.DataFrame(data_cadastro)


# In[ ]:


# Criar colunas temporárias para a primeira palavra
df_similaridade_cadastro['primeira_palavra_cadastro'] = df_similaridade_cadastro['item_cadastro'].str.split().str[0]
df_similaridade_cadastro['primeira_palavra_tab_propria'] = df_similaridade_cadastro['item_tab_propria'].str.split().str[0]


# Filtrar os casos onde as primeiras palavras são iguais
df_similaridade_cadastro = df_similaridade_cadastro[
     df_similaridade_cadastro['primeira_palavra_cadastro'] == df_similaridade_cadastro['primeira_palavra_tab_propria']
]

# Opcional: Remover as colunas temporárias (se não forem mais necessárias)
df_similaridade_cadastro.drop(['primeira_palavra_cadastro', 'primeira_palavra_tab_propria'], axis=1, inplace=True)

# Redefinir o índice do DataFrame
df_similaridade_cadastro = df_similaridade_cadastro.reset_index(drop=True)

df_similaridade_cadastro
# In[ ]:


print("Fim - Pré - Seleção de cadastro")


# ### 2.2 Cálculo da similaridade - Cadastro

# In[ ]:


def calcular_similaridade_cadastro(row, threshold=0.8):
    
    # Seleciona apenas palavras que contêm somente letras
    palavras_cadastro = {palavra for palavra in row['item_cadastro'].split() if palavra.isalpha()}
    palavras_tab_propria = {palavra for palavra in row['item_tab_propria'].split() if palavra.isalpha()}
    
    # Função para calcular a similaridade de sequência entre duas palavras
    def similaridade_sequencia(palavra1, palavra2):
        seq_matcher = SequenceMatcher(None, palavra1, palavra2)
        return seq_matcher.ratio()
        
    # Função para verificar se duas palavras são similares com base no limiar
    def palavras_similares(palavra1, palavra2, threshold=0.8):
        if palavra1.isalpha() and palavra2.isalpha():
            return (
                len(set(palavra1) & set(palavra2)) / len(set(palavra1)) >= threshold and
                similaridade_sequencia(palavra1, palavra2) >= threshold
            )
        return False

    # Armazena as palavras já contadas
    palavras_contadas = set()

    # Calcula a quantidade de palavras em item_tab_propria que têm pelo menos 80% das letras em comum com item_cadastro
    qtd_palavras_comuns = 0
    for palavra1 in palavras_cadastro:
        for palavra2 in palavras_tab_propria:
            if palavra1 not in palavras_contadas and palavras_similares(palavra1, palavra2, threshold):
                qtd_palavras_comuns += 1
                palavras_contadas.add(palavra1)  # Marca a palavra como contada
    
    # Calcula o resultado desejado
    similaridade = qtd_palavras_comuns / len(palavras_cadastro) if palavras_cadastro else 0
    
    return pd.DataFrame({
        'similaridade_cadastro': [similaridade],
        'qtd_palavras_comum_ajustada_cadastro': [qtd_palavras_comuns]
    })


# In[ ]:


def verificar_primeira_palavra_cadastro(row):
    # Dividindo as descrições em palavras
    palavras_cadastro = row['item_cadastro'].split()
    palavras_tab_propria = row['item_tab_propria'].split()
    
    # Extraindo as 4 primeiras palavras de cada item
    palavras_cadastro_relevantes = palavras_cadastro[:4]
    palavras_tab_propria_relevantes = palavras_tab_propria[:4]
    
    # Definindo pesos e normalização baseados no número de palavras em item_tab_propria
    num_palavras = len(palavras_cadastro_relevantes)
    
    if num_palavras >= 4:
        pesos = [4, 3, 2, 1]
        divisor = 10
    elif num_palavras == 3:
        pesos = [3, 2, 1]
        divisor = 6
    elif num_palavras == 2:
        pesos = [2, 1]
        divisor = 3
    elif num_palavras == 1:
        pesos = [1]
        divisor = 1
    else:
        return 0  # Se não houver palavras, a pontuação é zero
    
    # Calculando a soma ponderada das correspondências por posição
    soma_ponderada = sum(pesos[i] for i in range(len(palavras_cadastro_relevantes))
                         if i < len(palavras_tab_propria_relevantes) 
                         and palavras_cadastro_relevantes[i] == palavras_tab_propria_relevantes[i])
    
    # Normalizar a pontuação pela soma total dos pesos
    pontuacao = soma_ponderada / divisor
    
    return pontuacao


# In[ ]:


def calcular_similaridade_medidas_cadastro(row):
    palavras_cadastro = set(row['item_cadastro'].split())
    palavras_tab_propria = set(row['item_tab_propria'].split())      

    # Função para calcular a similaridade de sequência entre duas palavras
    def similaridade_sequencia(palavra1, palavra2):
        seq_matcher = SequenceMatcher(None, palavra1, palavra2)
        return seq_matcher.ratio()
    
    #def similaridade_sequencia(palavra1, palavra2):
        #seq_matcher = SequenceMatcher(None, palavra1, palavra2)
        #match = seq_matcher.find_longest_match(0, len(palavra1), 0, len(palavra2))
        #correspondencias = match.size
        #return correspondencias / len(palavra1)
    
    def palavras_nao_alfabeticas_similares(palavra1, palavra2):
        def contem_digito_e_letra(palavra):
            return any(char.replace('.', '', 1).isdigit() for char in palavra) and any(char.isalpha() for char in palavra)
        
        # Verifica se ambas as palavras são compostas apenas por dígitos
        if palavra1.replace('.', '', 1).isdigit() and palavra2.replace('.', '', 1).isdigit():
            return similaridade_sequencia(palavra1, palavra2) == 1
        
        # Verifica se ambas as palavras contêm tanto letras quanto dígitos
        if contem_digito_e_letra(palavra1) and contem_digito_e_letra(palavra2):
            # Verifica se todas as letras de palavra1 estão em palavra2
            if len(set(palavra1) & set(palavra2)) == len(set(palavra1)):
                # Verifica a similaridade de sequência
                return similaridade_sequencia(palavra1, palavra2) == 1
    
        return False

    # Calcula a quantidade de palavras em item_tab_propria que têm 100% das letras em comum com item_cadastro
    qtd_palavras_comuns = sum(
        1 for palavra1 in palavras_cadastro
        for palavra2 in palavras_tab_propria 
        if palavras_nao_alfabeticas_similares(palavra1, palavra2)
    )

    def palavra_e_medida(palavra):
        return palavra.replace('.', '', 1).isdigit() or \
               (any(char.isdigit() for char in palavra) and any(char.isalpha() for char in palavra))


    # Calcula o divisor como o número de palavras em item_tab_propria que são medidas
    divisor = sum(1 for palavra in palavras_cadastro if palavra_e_medida(palavra))

    # Calcula o resultado desejado
    similaridade_medidas = qtd_palavras_comuns / divisor if divisor > 0 else 0

    return similaridade_medidas


# In[ ]:


# Aplicar a função à coluna desejada
#similaridade_cadastro e peso_primeira_palavra_cadastro
df_similaridade_cadastro[['similaridade_cadastro', 'qtd_palavras_comum_ajustada_cadastro']] = pd.concat(df_similaridade_cadastro.apply(calcular_similaridade_cadastro, axis=1).tolist(), ignore_index=True)


# In[ ]:


#peso_primeira_palavra_cadastro
df_similaridade_cadastro['peso_primeira_palavra_cadastro'] = df_similaridade_cadastro.apply(verificar_primeira_palavra_cadastro, axis=1)


# In[ ]:


#similaridade_medidas_cadastro
df_similaridade_cadastro['similaridade_medidas_cadastro'] = df_similaridade_cadastro.apply(calcular_similaridade_medidas_cadastro, axis=1)


# In[ ]:


#similaridade_media_cadastro
df_similaridade_cadastro['similaridade_media_cadastro'] = np.where(
    (df_similaridade_cadastro['similaridade_medidas_cadastro'] == 0) &  # Condição 1: similaridade_medidas_cadastro == 0
    (df_similaridade_cadastro['item_cadastro'].apply(lambda x: all(char.isalpha() or char.isspace() for char in x))),
    # Condição 2: item_tab_propria contém apenas letras e espaços
    
    # Se ambas as condições forem verdadeiras
    (df_similaridade_cadastro['similaridade_cadastro'] * 4 +  
     df_similaridade_cadastro['peso_primeira_palavra_cadastro'] * 6) / 10,
    
    # Se qualquer condição for falsa
    (df_similaridade_cadastro['similaridade_cadastro'] * 2 + 
     df_similaridade_cadastro['peso_primeira_palavra_cadastro'] * 6 + 
     df_similaridade_cadastro['similaridade_medidas_cadastro'] * 2) / 10)


# In[ ]:


#df_similaridade_cadastro['similaridade_final_cadastro']
df_similaridade_cadastro['similaridade_final_cadastro'] = df_similaridade_cadastro['similaridade_media_cadastro']


# In[ ]:


df_similaridade_cadastro


# In[ ]:


print("Fim - Cálculo da similaridade da cadastro")


# # 3.0 Unir dataframes

# In[ ]:


df_similaridade_tab_propria


# In[ ]:


df_similaridade_cadastro


# In[ ]:


# Empilhar os DataFrames
df_combinado = pd.concat([df_similaridade_tab_propria[['item_tab_propria','item_cadastro']],
                          df_similaridade_cadastro[['item_tab_propria','item_cadastro']]], ignore_index=True)

# Remover duplicatas com base em todas as colunas
df_combinado = df_combinado.drop_duplicates()


# In[ ]:


df_combinado 


# In[ ]:


#tabela própria
#traz as métricas do df_similaridade_tab_propria
df_combinado = pd.merge(df_combinado, df_similaridade_tab_propria, right_on=['item_tab_propria','item_cadastro'],
                        left_on=['item_tab_propria','item_cadastro'], how='left')

#cadastro
#traz as métrica do df_similaridade_cadastro
df_combinado = pd.merge(df_combinado, df_similaridade_cadastro, right_on=['item_tab_propria','item_cadastro'],
                        left_on=['item_tab_propria','item_cadastro'], how='left')


# In[ ]:


df_combinado.info()


# In[ ]:


#traz informações da tabela própria através da base original

# Realizar o merge utilizando a coluna DESCRIÇÃO_TRATADA
df_combinado = pd.merge(df_combinado, base_tab_propria[['DESCRICAO_TRATADA','DESCRICAO_TAB_PROPRIA','COD_TAB_PROPRIA','VALOR_UNIT']],
                        right_on='DESCRICAO_TRATADA',left_on='item_tab_propria', how='left')

# Dropar a coluna redundante 'DESCRICAO_TRATADA' que veio da base_tab_propria
df_combinado = df_combinado.drop('DESCRICAO_TRATADA', axis=1)


# In[ ]:


df_combinado


# In[ ]:


if var_codigo == 'COD_SISTEMA' :
    
    #traz 'CODIGO_SISTEMA','REFERENCIA'
    # Realizar o merge utilizando a coluna DESCRIÇÃO_TRATADA
    df_combinado = pd.merge(df_combinado, base_cadastro[['DESCRICAO_TRATADA','DESCRICAO_CADASTRO', 'CODIGO_SISTEMA','REFERENCIA']],
                        left_on='item_cadastro', right_on='DESCRICAO_TRATADA', how='left')

    # Dropar a coluna redundante 'DESCRICAO_TRATADA' que veio da base_cadastro
    df_combinado = df_combinado.drop('DESCRICAO_TRATADA', axis=1)
    
else:
    
    #traz COD_P12, REFERENCIA,FABRICANTE da base cadastro
    # Realizar o merge utilizando a coluna DESCRIÇÃO_TRATADA
    df_combinado = pd.merge(df_combinado, base_cadastro[['DESCRICAO_TRATADA','DESCRICAO_CADASTRO', 'COD_P12','REFERENCIA','FABRICANTE']],
                            left_on='item_cadastro', right_on='DESCRICAO_TRATADA', how='left')

    # Dropar a coluna redundante 'DESCRICAO_TRATADA' que veio da base_cadastro
    df_combinado = df_combinado.drop('DESCRICAO_TRATADA', axis=1)
    


# In[ ]:


df_combinado.info()


# ## 4.0 Resultado final

# In[ ]:


if var_codigo == 'COD_SISTEMA' :
    
    df_combinado = df_combinado[['item_tab_propria','item_cadastro',
                             'DESCRICAO_TAB_PROPRIA','DESCRICAO_CADASTRO',
                             'COD_TAB_PROPRIA','VALOR_UNIT','CODIGO_SISTEMA','REFERENCIA',
                             'qtd_palavras_comum_tab_propria', 'qtd_palavras_comum_ajustada_tab_prop',
                             'similaridade_tab_prop','similaridade_medidas_tab_prop','peso_primeira_palavra_tab_prop','similaridade_media_tab_prop','similaridade_final_tab_prop',
                             'qtd_palavras_comum_cadastro','qtd_palavras_comum_ajustada_cadastro',
                             'similaridade_cadastro','similaridade_medidas_cadastro','peso_primeira_palavra_cadastro','similaridade_media_cadastro','similaridade_final_cadastro']]            
    
else:
    df_combinado = df_combinado[['item_tab_propria','item_cadastro',
                             'DESCRICAO_TAB_PROPRIA','DESCRICAO_CADASTRO',
                             'COD_TAB_PROPRIA','VALOR_UNIT','COD_P12','REFERENCIA','FABRICANTE',
                             'qtd_palavras_comum_tab_propria', 'qtd_palavras_comum_ajustada_tab_prop',
                             'similaridade_tab_prop','similaridade_medidas_tab_prop','peso_primeira_palavra_tab_prop','similaridade_media_tab_prop','similaridade_final_tab_prop',
                             'qtd_palavras_comum_cadastro','qtd_palavras_comum_ajustada_cadastro',
                             'similaridade_cadastro','similaridade_medidas_cadastro','peso_primeira_palavra_cadastro','similaridade_media_cadastro','similaridade_final_cadastro']]            
    


# In[ ]:


#Nesse agrupamento vamos verificar as DESCRICAO_TAB_PROPRIA que tem pelo menos 1 item do cadastro com a 1 palavra igual
data_aux = df_combinado[['DESCRICAO_TAB_PROPRIA', 'DESCRICAO_CADASTRO']][df_combinado['peso_primeira_palavra_tab_prop'] > 0] \
    .groupby(['DESCRICAO_TAB_PROPRIA']).count().reset_index()

# Renomear a coluna de contagem
data_aux = data_aux.rename(columns={'DESCRICAO_CADASTRO': 'QTD_PESO1'})


# In[ ]:


data_aux


# In[ ]:


#Traz as informações de peso de primeira palavra para o df_combinado
df_combinado = pd.merge(df_combinado, data_aux, left_on='DESCRICAO_TAB_PROPRIA', right_on='DESCRICAO_TAB_PROPRIA', how='left')


# In[ ]:


#Preenchendo valores nulos com 0 no DataFrame df_combinado
df_combinado['QTD_PESO1'].fillna(0, inplace=True)


# In[ ]:


df_combinado = df_combinado.sort_values(by=['DESCRICAO_TAB_PROPRIA','similaridade_final_tab_prop'],
                                        ascending=[True, False])


# In[ ]:


# Criar a coluna de prioridade
df_combinado['prioridade'] = df_combinado.groupby('DESCRICAO_TAB_PROPRIA')['similaridade_final_tab_prop'].rank(method='min', ascending=False)


# In[ ]:


# Definindo a data atual e o nome base do arquivo
#data_atual = datetime.now().strftime("%Y-%m-%d")
#nome_arquivo = (
   # r"\\Fscorp05\monitoramento$\08.Desenvolvimento\10_Similaridade_por_Descricao\MED\03_RESULTADO_MED"
    #f"\\similaridade_por_descricao_MED_{var_hospital}_total_{data_atual}.xlsx")

# Definindo o limite de linhas por aba
#limite_linhas = 1000000

# Verificando o tamanho do DataFrame
#total_linhas = len(df_combinado)

# Exportando o DataFrame em partes, cada uma em uma aba diferente
#with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
    #for i in range(0, total_linhas, limite_linhas):
     #   parte_df = df_combinado[i:i + limite_linhas]
     #   nome_aba = f'Parte_{i // limite_linhas + 1}'
     #   parte_df.to_excel(writer, sheet_name=nome_aba, index=False)
     #   print(f'Aba {nome_aba} salva com {len(parte_df)} linhas.')


# In[ ]:


df_combinado_final = df_combinado[df_combinado['prioridade'] == 1]


# In[ ]:


df_combinado_final = df_combinado_final.sort_values(by=['DESCRICAO_TAB_PROPRIA','peso_primeira_palavra_tab_prop'],
                                        ascending=[True, False])


# In[ ]:


# Criar a coluna de prioridade
df_combinado_final['prioridade_peso_palavra'] = df_combinado_final.groupby('DESCRICAO_TAB_PROPRIA')['peso_primeira_palavra_tab_prop'].rank(method='min', ascending=False)


# In[ ]:


# Data atual
data_atual = datetime.now().strftime("%Y-%m-%d")

# Ajustando o caminho base
caminho_base = r"\\Fscorp05\monitoramento$\08.Desenvolvimento\10_Similaridade_por_Descricao\MED\03_RESULTADO_MED"

# Lógica condicional para salvar o DataFrame
if var_codigo == 'COD_SISTEMA':
    df_final = df_combinado_final[df_combinado_final['prioridade_peso_palavra'] == 1]
    df_final = df_final[['DESCRICAO_TAB_PROPRIA', 'DESCRICAO_CADASTRO',
                         'COD_TAB_PROPRIA', 'VALOR_UNIT', 'CODIGO_SISTEMA', 'REFERENCIA',
                         'similaridade_final_tab_prop', 'similaridade_final_cadastro']]
else:
    df_final = df_combinado_final[df_combinado_final['prioridade_peso_palavra'] == 1]
    df_final = df_final[['DESCRICAO_TAB_PROPRIA', 'DESCRICAO_CADASTRO',
                         'COD_TAB_PROPRIA', 'VALOR_UNIT', 'COD_P12', 'REFERENCIA',
                         'similaridade_final_tab_prop', 'similaridade_final_cadastro']]

# Concatenando o nome do arquivo ao caminho base
nome_do_arquivo_excel = f"{caminho_base}\\similaridade_por_descricao_MED_{var_hospital}_{data_atual}.xlsx"

# Salvando o DataFrame no arquivo Excel
df_final.to_excel(nome_do_arquivo_excel, index=False)
print(f"Arquivo salvo em: {nome_do_arquivo_excel}")


# In[ ]:


print("Fim de execução")

