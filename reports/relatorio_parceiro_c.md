# Relatorio A/B - Parceiro C

## Decisao

**Acao recomendada:** Escalar Grupo 1 para 100% do trafego.

**Variante vencedora:** Grupo 1

**Confianca:** media

**Racional:** Grupo 1 teve a maior contribuicao liquida diaria. As demais variantes aumentaram o custo de cashback sem compensar em margem.

## Contexto do teste

- Periodo: 2011-07-01 a 2011-08-14
- Parceiro: Parceiro C
- Baseline: Grupo 1
- Linhas analisadas: 90
- Qualidade dos dados: Sem alertas de qualidade.

## Leitura executiva

Grupo 1 e a recomendacao para Parceiro C: gerou R$ 34.769,00 de contribuicao liquida no periodo, media de R$ 772,64 por dia, com taxa de cashback de 5,00% sobre GMV. A leitura considera contribuicao liquida como metrica primaria porque cashback e custo direto.

## Metricas por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Contribuicao liquida | Cashback/GMV | Margem liquida | Liquido/dia | Liquido/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 45 | 4.549 | R$ 1.738.460,00 | R$ 121.693,00 | R$ 86.924,00 | R$ 34.769,00 | 5,00% | 2,00% | R$ 772,64 | R$ 7,64 |
| Grupo 2 | 45 | 4.522 | R$ 1.685.235,00 | R$ 117.967,00 | R$ 117.967,00 | R$ 0,00 | 7,00% | 0,00% | R$ 0,00 | R$ 0,00 |

## Comparacao contra baseline (Grupo 1)

| Variante | Metrica | Dias pareados | Delta medio diario | Delta % | IC 95% delta | p-valor aprox. |
|---|---|---:|---:|---:|---:|---:|
| Grupo 2 | Contribuicao liquida | 45 | -772,64 | -100,00% | -830,99 a -714,30 | 0,0000 |
| Grupo 2 | Compradores | 45 | -0,60 | -0,59% | -10,42 a 9,22 | 0,9047 |
| Grupo 2 | GMV | 45 | -1182,78 | -3,06% | -5344,24 a 2978,69 | 0,5775 |

## Observacoes e proximos cuidados

- O dataset nao traz usuarios expostos/sessoes; por isso a analise nao estima taxa de conversao real.
- A decisao prioriza contribuicao liquida diaria (comissao menos cashback), com compradores e GMV como sinais de suporte.
- Se a variante vencedora for escalada, acompanhar diariamente margem liquida, GMV e volume de compradores para detectar mudanca de mix.
