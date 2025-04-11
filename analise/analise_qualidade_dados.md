
# 📊 Análise de Qualidade dos Dados

## Introdução

A análise de qualidade dos dados é uma etapa fundamental para garantir que os resultados obtidos na fase de análise e visualização sejam confiáveis. Neste projeto, a camada **Silver** do domínio de criptoativos foi utilizada como base para essa verificação, após os dados terem sido processados e padronizados a partir da ingestão em JSON na camada **Bronze**.

## Verificações realizadas

### ✅ 1. Valores nulos

Foi realizada uma verificação de valores nulos nas principais colunas da tabela Silver (como `asset_name`, `symbol`, `timestamp`, `price`, `market_cap`, entre outras). O resultado demonstrou que **não há valores nulos** em atributos obrigatórios para as análises.

### ✅ 2. Duplicatas

As tabelas de origem seguem um padrão `insertOnly`, o que reduz o risco de duplicações. Ainda assim, foram aplicadas verificações para confirmar a ausência de registros duplicados (mesma combinação de `asset_name` + `timestamp`). Nenhuma duplicação foi identificada.

### ✅ 3. Valores fora do domínio esperado

Foram definidas regras de domínio para atributos numéricos, como:

- `price` ≥ 0
- `market_cap` ≥ 0
- `total_volume` ≥ 0

Foram encontrados alguns registros com valores muito próximos de zero em `market_cap` e `total_volume`, especialmente em ativos recém-listados. Esses registros foram mantidos por estarem de acordo com o comportamento real de mercado.

### ✅ 4. Cobertura temporal

Foi verificado se cada ativo possui registros diários contínuos desde sua primeira aparição. A análise identificou que alguns ativos possuem janelas com lacunas, especialmente nos primeiros dias após serem inseridos. Isso é esperado devido ao delay natural da primeira coleta e não compromete as análises futuras.

### ✅ 5. Estatísticas básicas por atributo numérico

Nesta análise, buscamos entender a distribuição básica dos principais atributos numéricos presentes na camada Silver. São extraídas informações como:

- Quantidade total de registros;
- Número de ativos distintos presentes no dataset;
- Preço mínimo e máximo observado entre todos os registros.

Essas métricas ajudam a identificar valores extremos (outliers), possíveis erros de coleta (ex: preços zerados ou negativos) e a diversidade de ativos processados. São fundamentais para contextualizar os dados e garantir que as análises posteriores estejam baseadas em um conjunto consistente e coerente.


## Conclusão

A análise de qualidade indicou que os dados da camada Silver estão com excelente qualidade. Não foram identificados problemas críticos que comprometam as análises. As poucas anomalias encontradas (valores baixos ou faltas pontuais em ativos novos) são compatíveis com a natureza dos dados de criptoativos.

Essa análise reforça a confiabilidade do pipeline de ingestão, transformação e enriquecimento utilizado no projeto.

