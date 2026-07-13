# Relatorio A/B - Parceiro B

## Decisao

**Acao recomendada:** Escalar Grupo 1 para 100% do trafego.

**Variante vencedora:** Grupo 1

**Confianca:** alta

**Racional:** Grupo 1 teve a maior contribuicao liquida diaria. As demais variantes aumentaram o custo de cashback sem compensar em margem.

## Contexto do teste

- Periodo: 2011-05-01 a 2011-06-30
- Parceiro: Parceiro B
- Baseline: Grupo 1
- Linhas analisadas: 183
- Qualidade dos dados: Sem alertas de qualidade.

## Leitura executiva

Grupo 1 e a recomendacao para Parceiro B: gerou R$ 286.570,00 de contribuicao liquida no periodo, media de R$ 4.697,87 por dia, com taxa de cashback de 4,00% sobre GMV. A leitura considera contribuicao liquida como metrica primaria porque cashback e custo direto.

## Metricas por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Contribuicao liquida | Cashback/GMV | Margem liquida | Liquido/dia | Liquido/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 61 | 7.990 | R$ 4.093.818,00 | R$ 450.321,00 | R$ 163.751,00 | R$ 286.570,00 | 4,00% | 7,00% | R$ 4.697,87 | R$ 35,87 |
| Grupo 2 | 61 | 5.452 | R$ 2.863.019,00 | R$ 314.935,00 | R$ 171.778,00 | R$ 143.157,00 | 6,00% | 5,00% | R$ 2.346,84 | R$ 26,26 |
| Grupo 3 | 61 | 5.029 | R$ 2.629.963,00 | R$ 289.290,00 | R$ 236.697,00 | R$ 52.593,00 | 9,00% | 2,00% | R$ 862,18 | R$ 10,46 |

## Comparacao contra baseline (Grupo 1)

| Variante | Metrica | Dias pareados | Delta medio diario | Delta % | IC 95% delta | p-valor aprox. |
|---|---|---:|---:|---:|---:|---:|
| Grupo 2 | Contribuicao liquida | 61 | -2351,03 | -50,04% | -2650,43 a -2051,64 | 0,0000 |
| Grupo 2 | Compradores | 61 | -41,61 | -31,76% | -47,35 a -35,87 | 0,0000 |
| Grupo 2 | GMV | 61 | -20177,03 | -30,06% | -24089,41 a -16264,65 | 0,0000 |
| Grupo 3 | Contribuicao liquida | 61 | -3835,69 | -81,65% | -4247,24 a -3424,14 | 0,0000 |
| Grupo 3 | Compradores | 61 | -48,54 | -37,06% | -55,90 a -41,19 | 0,0000 |
| Grupo 3 | GMV | 61 | -23997,62 | -35,76% | -28428,13 a -19567,12 | 0,0000 |

## Observacoes e proximos cuidados

- O dataset nao traz usuarios expostos/sessoes; por isso a analise nao estima taxa de conversao real.
- A decisao prioriza contribuicao liquida diaria (comissao menos cashback), com compradores e GMV como sinais de suporte.
- Se a variante vencedora for escalada, acompanhar diariamente margem liquida, GMV e volume de compradores para detectar mudanca de mix.
