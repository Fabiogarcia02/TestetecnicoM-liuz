# Relatorio A/B - Parceiro A

## Decisao

**Acao recomendada:** Escalar Grupo 1 para 100% do trafego.

**Variante vencedora:** Grupo 1

**Confianca:** alta

**Racional:** Grupo 1 teve a maior contribuicao liquida diaria. As demais variantes aumentaram o custo de cashback sem compensar em margem.

## Contexto do teste

- Periodo: 2011-01-01 a 2011-04-02
- Parceiro: Parceiro A
- Baseline: Grupo 1
- Linhas analisadas: 276
- Qualidade dos dados: Sem alertas de qualidade.

## Leitura executiva

Grupo 1 e a recomendacao para Parceiro A: gerou R$ 404.711,00 de contribuicao liquida no periodo, media de R$ 4.399,03 por dia, com taxa de cashback de 4,16% sobre GMV. A leitura considera contribuicao liquida como metrica primaria porque cashback e custo direto.

## Metricas por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Contribuicao liquida | Cashback/GMV | Margem liquida | Liquido/dia | Liquido/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 92 | 9.633 | R$ 5.605.173,00 | R$ 638.135,00 | R$ 233.424,00 | R$ 404.711,00 | 4,16% | 7,22% | R$ 4.399,03 | R$ 42,01 |
| Grupo 2 | 92 | 10.814 | R$ 6.423.096,00 | R$ 728.178,00 | R$ 370.659,00 | R$ 357.519,00 | 5,77% | 5,57% | R$ 3.886,08 | R$ 33,06 |
| Grupo 3 | 92 | 11.410 | R$ 6.785.856,00 | R$ 767.887,00 | R$ 503.600,00 | R$ 264.287,00 | 7,42% | 3,89% | R$ 2.872,68 | R$ 23,16 |

## Comparacao contra baseline (Grupo 1)

| Variante | Metrica | Dias pareados | Delta medio diario | Delta % | IC 95% delta | p-valor aprox. |
|---|---|---:|---:|---:|---:|---:|
| Grupo 2 | Contribuicao liquida | 92 | -512,96 | -11,66% | -740,72 a -285,19 | 0,0000 |
| Grupo 2 | Compradores | 92 | 12,84 | 12,26% | 9,15 a 16,52 | 0,0000 |
| Grupo 2 | GMV | 92 | 8890,47 | 14,59% | 5155,07 a 12625,86 | 0,0000 |
| Grupo 3 | Contribuicao liquida | 92 | -1526,35 | -34,70% | -1914,38 a -1138,32 | 0,0000 |
| Grupo 3 | Compradores | 92 | 19,32 | 18,45% | 14,26 a 24,37 | 0,0000 |
| Grupo 3 | GMV | 92 | 12833,51 | 21,06% | 8454,56 a 17212,46 | 0,0000 |

## Observacoes e proximos cuidados

- O dataset nao traz usuarios expostos/sessoes; por isso a analise nao estima taxa de conversao real.
- A decisao prioriza contribuicao liquida diaria (comissao menos cashback), com compradores e GMV como sinais de suporte.
- Se a variante vencedora for escalada, acompanhar diariamente margem liquida, GMV e volume de compradores para detectar mudanca de mix.
