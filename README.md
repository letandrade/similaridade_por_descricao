<h1 align="center"> Migração de Cadastros Hospitalares com Detecção de Similaridade <br /> </h1>

## **1.0 Visão geral**

No ramo da prestação de serviços de saúde é comum ouvir falar sobre glosa hospitalar. As glosas correspondem a valores de faturamento que não são recebidos ou são recusados pelas operadoras de saúde (convênios), geralmente devido a problemas de comunicação ou inconsistências nas informações fornecidas pelo prestador. 

Na maioria das vezes, as glosas ocorrem quando os dados enviados pelo prestador não coincidem com os registros da operadora. Por isso, evitar glosas é fundamental para manter a eficiência na gestão financeira das instituições de saúde.

Diante da relevância desse tema, propõe-se a criação de um modelo de regras de associação.

Este projeto aplica uma técnica de aprendizado de máquina não supervisionado, com foco na criação de regras de associação (Apriori), para analisar padrões recorrentes em glosas hospitalares.

Para este caso específico, o objetivo das regras é Identificar variáveis que frequentemente ocorrem juntas em casos de glosa, como tipo de despesa, tipo de atendimento, grupo e setor (nível 1 e 2). Essa abordagem possibilita compreender os principais fatores associados às glosas, tornando a análise mais estratégica e contribuindo para a redução de glosas e otimização do faturamento hospitalar.

## **2.0 Objetivos técnicos**

Desenvolver modelos de regras de associação (Apriori) segmentados por hospital, convênio e tipo de glosa, com o objetivo de identificar padrões e facilitar a análise das principais causas de glosas.

Foi implementada uma estrutura em loop, capaz de gerar automaticamente diferentes regras para cada combinação de hospital, operadora e tipo de glosa. Por exemplo:

- Para a base de dados 1, referente ao Hospital A, da Operadora B e do Tipo de Glosa C, foram identificados 50 regras.

- Já para a base de dados 2, correspondente ao Hospital E, da Operadora F e do Tipo de Glosa G, foram identificados 100 regras.

Essa rotina de criação dos modelos foi transformada em um processo automático, com a execução do script Python agendada por meio do Agendador de Tarefas do Windows, garantindo a atualização periódica dos dados sem necessidade de intervenção manual.

Além disso, um painel no Power BI será alimentado com os resultados dessas análises, permitindo o acompanhamento semanal da evolução das glosas, com foco na tomada de decisão mais rápida e estratégica por parte das áreas responsáveis.

## **3.0 Ferramentas utilizadas**

![{1743A47F-6D12-4614-BA3F-4EF85A242CC9}](https://github.com/user-attachments/assets/47abe4fb-2bea-4475-a92d-91fc4a766908)

- SQL: Utilizado para construção da bases de dados.

- Python: Utilizado para o processamento e modelagem dos dados, incluindo a criação dos modelos apriori e tratamento das bases segmentadas por hospital, operadora e tipo de glosa. É importante dizer que foi utilizado o ambiente Anaconda.

- Power Automate: Responsável pela automação da execução do script Python, garantindo que os modelos sejam atualizados de forma periódica e sem necessidade de intervenção manual.

- Teams:

- Power BI: Ferramenta utilizada para a visualização e monitoramento dos resultados. Os dados processados são integrados ao painel para acompanhamento semanal das glosas, facilitando a análise e as correções de glosa.
  
## **4.0 Desenvolvimento**

Todos os passos a seguir estão detalhados nos módulos e arquivos de texto em anexo.

### **4.1 Construção da base de dados em SQL**

A base de dados foi extraída de um banco de dados, esse script faz a seleção e tratamento de variáveis. 

A query construída foi chamada através da conexão com o banco de dados Oracle executada através da biblioteca cx_oracle.

### **4.2 Análise de Glosas com Regras de Associação (Apriori)**

O módulo modulo_apriori_hospital_recente.py aplica o algoritmo Apriori para identificar padrões recorrentes em glosas hospitalares. Ele analisa combinações frequentes de variáveis como tipo de despesa, setor, grupo e tipo de atendimento — por hospital, convênio e tipo de glosa — para apoiar ações estratégicas de auditoria e redução de glosas.

Funcionalidades principais:

- Conexão automatizada com banco Oracle e carregamento segmentado de dados.

- Geração de regras de associação com o algoritmo Apriori.

- Cálculo de suporte, confiança e lift das regras.

- Filtragem de regras redundantes.

- Inclusão automática do valor glosado, valor cobrado e índice de glosa por regra.

- Preparação de base final com as regras de associação.

### **4.3 Módulo de execução de funções**

O módulo modulo_apriori_hospital_recente_loop.py automatiza a geração de regras de associação para glosas hospitalares utilizando o algoritmo Apriori, aplicado a combinações específicas de hospitais, convênios e tipos de glosa.

Funcionalidades principais:

- Carregamento de dados de hospitais e combinações válidas (hospital, convênio, tipo de glosa).

- Execução de um loop que aplica, para cada combinação válida, um processo de análise utilizando o algoritmo Apriori.

- Armazenamento e concatenação dos resultados em um único DataFrame.

- Tratamento de valores nulos e exportação dos resultados consolidados para um arquivo CSV.

### **4.4 Agendamento do script de loop no Windows**

Funcionalidades principais:

- Criação um arquivo .bat (executar_modulo_apriori_hospital_recente_loop.bat) responsável por executar o script Python de clusterização.

- Organização dos arquivos necessários (modulo_apriori_hospital_recente.py, modulo_apriori_hospital_recente_loop.py, executar_modulo_apriori_hospital_recente_loop.bat) em uma pasta dedicada dentro de um diretório de trabalho.

- Configurar uma nova tarefa no Agendador de Tarefas do Windows, definindo a execução automática com frequência semanal e fazer o apontamento para o arquivo .bat presente na pasta anterior. Caminho: Agendador de Tarefas > Criar tarefa < Ações < Novo. Preencha o campo Programa/Script com o caminho do arquivo .bat e o campo Iniciar em com o caminho da pasta com os arquivos.

![apriori1](https://github.com/user-attachments/assets/b4deca53-6680-4a3c-b1b6-868f7ee87925)

![apriori2](https://github.com/user-attachments/assets/50b6bdc1-f1ed-4ef6-919d-c1af908226a7)

- Ao final de cada execução, o script exporta um arquivo.csv (base_apriori_por_hospital.csv) contendo o empilhamento dos clusters gerados, armazenando-o no diretório especificado no código.

- O tutorial a seguir esclarece de forma detalhada a implementação. https://medium.com/sucessoemvendasacademy/como-executar-scripts-de-python-de-forma-autom%C3%A1tica-e-recorrente-windows-867db62523bf

### **4.5 Dashboard de Regras de Associação**

Funcionalidades principais:

Importação do arquivo base_apriori_por_hospital.csv no Power BI desktop.
Construção dos visuais.
Criação dos slicers por hospital, convênio e tipo de glosa. Para cada chave são apresentadas as regras de associação criadas.

![{3B21F2FB-4A4B-403F-A702-2B4313AA969D}](https://github.com/user-attachments/assets/0f766d09-b631-4d3a-afcb-3cc99fba97f6)

## **5.0 Resultados**

Entre janeiro e abril de 2025, a ferramenta de regras de associação em conjunto com a ferramenta de [clusterização](https://github.com/letandrade/clusterizacao_glosas_hospitalares) identificaram 37 casos relevantes de glosas somando aproximadamente R$5 milhões, cuja tratativa resultou em uma glosa evitada anualizada de aproximadamente R$60 milhões.


Vale destacar que a ferramenta fornece os valores mensais de glosa por caso. Após a correção da causa da glosa, a perda financeira deixa de ocorrer. Por isso, o principal indicador de desempenho é a glosa evitada, ou seja, o valor anual que seria perdido caso os problemas não fossem identificados e corrigidos.

Além disso, a ferramenta foi incorporada como um processo autônomo, com atualizações semanais, garantindo agilidade e escalabilidade na detecção e prevenção de glosas ao longo do tempo.
