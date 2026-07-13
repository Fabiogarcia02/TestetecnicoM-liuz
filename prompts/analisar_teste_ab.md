# Prompt operacional para usar com IA

Use este prompt quando alguem do time quiser acionar a solucao por linguagem natural:

```text
Voce esta no repositorio da solucao de analise de testes A/B de cashback.
Analise o dataset CSV informado pelo usuario usando o comando:

python analyze.py <CAMINHO_DO_DATASET> --reports-dir reports --tracking-csv data/processed/ab_tests_tracking.csv

Depois leia o relatorio Markdown gerado em reports/ e devolva:
1. variante recomendada para escalar a 100% do trafego;
2. racional executivo em ate 5 bullets;
3. riscos/limitacoes dos dados;
4. caminho do relatorio e da planilha CSV de acompanhamento.

Nao altere codigo para trocar de dataset. Apenas mude o caminho do arquivo.
```
