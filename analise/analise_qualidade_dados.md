
# 📊 Análise de Qualidade dos Dados

## Introdução

A análise de qualidade dos dados é uma etapa fundamental para garantir que os resultados obtidos na fase de análise e visualização sejam confiáveis. Neste projeto, a camada **Silver** do domínio de criptoativos foi utilizada como base para essa verificação, após os dados terem sido processados e padronizados a partir da ingestão em JSON na camada **Bronze**.

## Verificações realizadas

### ✅ 1. Valores nulos

Foi realizada uma verificação de valores nulos nas principais colunas da tabela Silver (como `asset_name`, `symbol`, `timestamp`, `price`, `market_cap`, entre outras). O resultado demonstrou que **não há valores nulos** em atributos obrigatórios para as análises.

![](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/df46ffcac063da8b36748b0330bd0cd13da32da4/docs/images/1.%20Verifica%C3%A7%C3%A3o%20de%20valores%20nulos%20ou%20ausentes.png?raw=true)

### ✅ 2. Duplicatas

As tabelas de origem seguem um padrão `insertOnly`, o que reduz o risco de duplicações. Ainda assim, foram aplicadas verificações para confirmar a ausência de registros duplicados (mesma combinação de `asset_name` + `timestamp`). Nenhuma duplicação foi identificada.

![](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/df46ffcac063da8b36748b0330bd0cd13da32da4/docs/images/2.%20Verifica%C3%A7%C3%A3o%20de%20duplicidade%20de%20registros.png?raw=true)

### ✅ 3. Valores fora do domínio esperado

Foram definidas regras de domínio para atributos numéricos, como:

- `price` ≥ 0

![](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/df46ffcac063da8b36748b0330bd0cd13da32da4/docs/images/3.%20Verifica%C3%A7%C3%A3o%20de%20valores%20fora%20do%20dom%C3%ADnio%20esperado.png?raw=true)

### ✅ 4. Cobertura temporal

Foi verificado se cada ativo possui registros diários contínuos desde sua primeira aparição. A análise identificou que alguns ativos possuem janelas com lacunas, especialmente nos primeiros dias após serem inseridos. Isso é esperado devido ao delay natural da primeira coleta e não compromete as análises futuras.
Foi também analisado o número de registros totais diários, que deve ser 24 por cada ativo, uma para cada hora.

![](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/1038ecefad30552b44bf80ddbfdcd89ea54a354c/docs/images/4.%20Distribui%C3%A7%C3%A3o%20de%20registros%20por%20data.png?raw=true)

### ✅ 5. Estatísticas básicas por atributo numérico

Nesta análise, buscamos entender a distribuição básica dos principais atributos numéricos presentes na camada Silver. São extraídas informações como:

- Quantidade total de registros;
- Número de ativos distintos presentes no dataset;
- Preço mínimo e máximo observado entre todos os registros.

![](https://github.com/douglas-engenheirodedados/mvpEngDadosPosPuc/blob/1038ecefad30552b44bf80ddbfdcd89ea54a354c/docs/images/5.%20Estat%C3%ADsticas%20b%C3%A1sicas%20por%20atributo%20num%C3%A9rico.png?raw=true)

Essas métricas ajudam a identificar valores extremos (outliers), possíveis erros de coleta (ex: preços zerados ou negativos) e a diversidade de ativos processados. São fundamentais para contextualizar os dados e garantir que as análises posteriores estejam baseadas em um conjunto consistente e coerente.


## Conclusão

A análise de qualidade indicou que os dados da camada Silver estão com excelente qualidade. Não foram identificados problemas críticos que comprometam as análises. As poucas anomalias encontradas (valores baixos ou faltas pontuais em ativos novos) são compatíveis com a natureza dos dados de criptoativos.

Essa análise reforça a confiabilidade do pipeline de ingestão, transformação e enriquecimento utilizado no projeto.

