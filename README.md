<h1 align="center"> Migração de Cadastros Hospitalares com Detecção de Similaridade <br /> </h1>

## **1.0 Visão geral**

Contexto
Em redes hospitalares, é comum o processo de expansão por meio da aquisição de novos hospitais, os chamados projetos Brownfield. Entretanto, um dos principais desafios dessa integração é a padronização dos cadastros hospitalares, especialmente quando o hospital adquirido utiliza um sistema de gestão diferente do padrão da rede.

Durante o processo de integração, é necessário alinhar os cadastros de itens e serviços hospitalares para garantir consistência nos processos de faturamento. A utilização incorreta de códigos de cobrança — por divergência na descrição ou estrutura dos cadastros — pode gerar glosas de codificação, ou seja, recusas de pagamento pelos convênios devido ao uso de códigos não negociados.

Este projeto apresenta uma solução baseada em Python que automatiza a identificação de similaridade entre os cadastros do hospital adquirido e o cadastro padrão da rede. O código analisa as descrições dos itens, calculando a similaridade textual entre elas. A melhor correspondência encontrada é utilizada para sugerir o código correto que deve ser utilizado no novo hospital.

## **2.0 Objetivos técnicos**

Desenvolver uma ferramenta autônoma capaz de calcular a similaridade textual entre descrições de itens hospitalares de diferentes bases de dados (hospital adquirido vs. padrão da rede), com o objetivo de:

- Mapear automaticamente os itens do hospital novo aos itens do cadastro padrão;

- Apontar o código de sistema correto a ser utilizado para cobrança;

- Minimizar o risco de glosas por codificação incorreta;

- Apoiar o processo de padronização de cadastros durante a integração de novos hospitais.

A ferramenta utiliza bibliotecas de processamento de linguagem natural (NLP) e técnicas de matching textual para identificar a melhor correspondência entre descrições, entregando como resultado a sugestão de item equivalente e seu respectivo código no sistema padrão.

Essa ferramenta foi transformada em um processo automático, com a execução do script Python via prompt de comando( CMD) acioando pelo Power Automate, garantindo a extração dos itens similares sem necessidade de intervenção manual.

É importante dizer que foram desenvolvidos dois scripts, uma para materiais e outro para medicamentos, considerando que os itens possuem características unicas que devem ser consideradas no desenvolvimento.

## **3.0 Ferramentas utilizadas**

![image](https://github.com/user-attachments/assets/9fef4416-1a70-498c-a434-eadc44753f39)

- Pasta local: Repositório de dados input no script. 

- SQL: Utilizado para construção da bases de dados de cadastro padão.

- Python: Utilizado para o processamento dos dados. É importante dizer que foi utilizado o ambiente Anaconda com as seguintes bibliotecas:
  - Pandas
  - Numpy
  - NLTK
  - cx_Oracle
  - Regex
  - Difflib (SequenceMatcher)

- Power Automate: Responsável pela automação da execução do script Python via prompt de comando (CMD).

- Teams: Criação de grupo para ser trigger do start da aplição no power automate.
  
## **4.0 Desenvolvimento**

### 4.1 Módulos python

Os módulos similaridade_por_descricao_mat_codigo_oficial.py e similaridade_por_descricao_mat_codigo_oficial são o core da aplicação, suas funcionalidades principais são:

**4.1.1 Conexão e leitura de dados**:
  - Integração com banco de dados Oracle e leitura de arquivos Excel.
  - Importação de dados do hospital adquirido (xlsx) e da base padrão (tabela no banco de dados).

**4.1.2 Pré-processamento das descrições**:
  - Remoção de acentos, caracteres especiais, stop words e padronização textual.

**4.1.3 Cálculo de similaridade**:

  - Comparação baseada em múltiplos critérios:
    - Similaridade de palavras (apenas letras).
    - Similaridade de medidas (numéricas).
    - Similaridade das primeiras 4 palavras.
      
  - Cálculo de **score final de similaridade para materiais**:
    - (Similaridade de palavras * 5 + Similaridade das primeiras palavras * 2 + Similaridade de medidas * 3) / 10
   
 - Cálculo de **score final de similaridade para medicamentos**:
    - (Similaridade de palavras * 5 + Similaridade das primeiras palavras * 2 + Similaridade de medidas * 3) / 10

**4.1.4 Geração de resultados**:
    - União dos dados com códigos e valores oficiais.
    - Exportação do resultado final em Excel, com os códigos sugeridos para cobrança.

### 4.5 Fluxo de execução da ferramenta 

**4.5.1 Power Automate**

Para automatizar a execução do módulo foi criada uma aplicação no power automated que executa o módulo python através do prompt de comando da máquina local. 

**4.5.2 Pasta local**

Na pasta local o usário preenche um template com as informações do novo hospital (Hospital, Código da tabela própria, Descrição do item, Valor), essas informação vão ser importadas no script. 

**4.5.3 Teams**

Após preencher o template, o usuário digita uma palavra chave no grupo do teams e inicia a execução do script python. 


Funcionalidades principais:


## **5.0 Resultados**

Entre janeiro e abril de 2025, a ferramenta de regras de associação em conjunto com a ferramenta de [clusterização](https://github.com/letandrade/clusterizacao_glosas_hospitalares) identificaram 37 casos relevantes de glosas somando aproximadamente R$5 milhões, cuja tratativa resultou em uma glosa evitada anualizada de aproximadamente R$60 milhões.


Vale destacar que a ferramenta fornece os valores mensais de glosa por caso. Após a correção da causa da glosa, a perda financeira deixa de ocorrer. Por isso, o principal indicador de desempenho é a glosa evitada, ou seja, o valor anual que seria perdido caso os problemas não fossem identificados e corrigidos.

Além disso, a ferramenta foi incorporada como um processo autônomo, com atualizações semanais, garantindo agilidade e escalabilidade na detecção e prevenção de glosas ao longo do tempo.
