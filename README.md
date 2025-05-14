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

A ferramenta utiliza algoritmos de processamento de linguagem natural (PLN) e técnicas de matching textual para identificar a melhor correspondência entre descrições, entregando como resultado a sugestão de item equivalente e seu respectivo código no sistema padrão.

Essa rotina de criação dos modelos foi transformada em um processo automático, com a execução do script Python agendada por meio do Agendador de Tarefas do Windows, garantindo a atualização periódica dos dados sem necessidade de intervenção manual.

É importante dizer que foram desenvolvidos dois scripts, uma para materiais e outra para medicamentos, considerando que os itens possuem características unicas que devem ser consideradas no script. 

## **3.0 Ferramentas utilizadas**

- Pasta local: Repositório de dados input no script. 

- SQL: Utilizado para construção da bases de dados de cadastro padão.

- Python: Utilizado para o processamento dos dados. É importante dizer que foi utilizado o ambiente Anaconda.

- Power Automate: Responsável pela automação da execução do script Python via prompt de comando (CMD).

- Teams: Criação de grupo para ser trigger do start da aplição no power automate.
  
## **4.0 Desenvolvimento**

Todos os passos a seguir estão detalhados nos módulos e arquivos de texto em anexo.

O módulo modulo_apriori_hospital_recente.py aplica o algoritmo Apriori para identificar padrões recorrentes em glosas hospitalares. Ele analisa combinações frequentes de variáveis como tipo de despesa, setor, grupo e tipo de atendimento — por hospital, convênio e tipo de glosa — para apoiar ações estratégicas de auditoria e redução de glosas.

Funcionalidades principais:

**4.1 Conexão e leitura de dados**:
  - Integração com banco de dados Oracle e leitura de arquivos Excel.
  - Importação de dados do hospital adquirido e da base padrão.

**4.2 Pré-processamento das descrições**:
  - Remoção de acentos, caracteres especiais, stop words e padronização textual.

**4.3 Cálculo de similaridade**:
  - Comparação baseada em múltiplos critérios:
    - Quantidade de palavras em comum.
    - Peso das primeiras palavras.
    - Similaridade de medidas (alfa-numéricas e numéricas).
    - Similaridade por sequência de caracteres (via `SequenceMatcher`).
  - Cálculo de **score final de similaridade** e priorização dos pares mais relevantes.

**4.4 Geração de resultados**:
  - União dos dados com códigos e valores oficiais.
  - Exportação do resultado final em Excel, com os códigos sugeridos para cobrança.

**4.5 Tecnologias utilizadas**

- Python 3.x
- Pandas
- Numpy
- NLTK
- cx_Oracle
- Regex
- Difflib (SequenceMatcher)

## 📁 Estrutura do projeto

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
