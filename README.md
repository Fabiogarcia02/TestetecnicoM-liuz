# Teste Tecnico - Growth AI-Native | Meliuz

Solucao reutilizavel para analisar testes A/B de cashback, gerar relatorios executivos em Markdown/HTML e registrar cada teste em uma planilha de acompanhamento (Google Sheets ou CSV local).

## Como funciona

O programa le arquivos CSV com dados de testes A/B de cashback, calcula metricas por variante (compradores, GMV, comissao, cashback, contribuicao liquida), compara cada variante contra o baseline usando dias pareados, e recomenda a melhor variante para escalar com base na **contribuicao liquida diaria** (`comissao - cashback`).

Tudo e feito com a biblioteca padrao do Python  sem dependencias externas para o uso basico.

Voce pode usar de **dois jeitos**:

---

## Jeito 1: Apenas relatorios locais (sem Google Sheets)

Requisitos: Python 3.10+ (sem pacotes extras)

```powershell
cd C:\Users\PC\Desktop\desafiomeliuz
python analyze.py data/raw/*.csv
```

Isso gera:

- Relatorios individuais em Markdown e HTML em `reports/`
- Relatorio consolidado em `reports/relatorio_consolidado.md` e `.html`
- CSV de acompanhamento em `data/processed/ab_tests_tracking.csv`

## Jeito 2: Relatorios locais + Google Sheets

Alem dos relatorios locais, sincroniza os resultados com uma planilha no Google Sheets. Ha duas formas de fazer isso:

### Opcao A: Google Apps Script (simples, sem credenciais)

1. Crie uma planilha no Google Sheets.
2. Va em **Extensoes > Apps Script**.
3. Cole o conteudo de `integrations/google_apps_script_webhook.gs`.
4. **Implantar > Nova implantacao** > **App da Web**.
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa com o link**
5. Copie a URL gerada e execute:

```powershell
$env:GOOGLE_SHEETS_WEBHOOK_URL="URL_DO_WEB_APP"
python analyze.py data/raw/*.csv --sync-sheets-webhook
```

### Opcao B: Google Sheets API (recomendada para producao)

#### 1. Instalar dependencias opcionais

```powershell
python -m pip install -e ".[sheets]"
pip install pip-system-certs   # necessario no Windows para certificado SSL
```

#### 2. Criar service account no Google Cloud

1. Crie um projeto em https://console.cloud.google.com/projectcreate
2. Habilite as APIs:
   - https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - https://console.cloud.google.com/apis/library/drive.googleapis.com
3. Em https://console.cloud.google.com/iam-admin/serviceaccounts crie uma service account
4. Va em **Chaves > Adicionar chave > JSON** e baixe o arquivo
5. Salve fora do repositorio (ex: `C:\Users\PC\Desktop\service-account-meliuz.json`)

#### 3. Compartilhar a planilha

1. Crie uma planilha no Google Sheets
2. Compartilhe com o e-mail da service account como **Editor**

#### 4. Rodar

```powershell
python analyze.py data/raw/*.csv --sync-google-sheets --google-credentials C:\Users\PC\Desktop\service-account-meliuz.json --spreadsheet-id ID_DA_PLANILHA
```

O `spreadsheet-id` e o hash na URL: `https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA/edit`

---

## Como ver os relatorios HTML

Os arquivos `.html` gerados em `reports/` sao auto-contidos (CSS embutido). Para ve-los:

1. Abra o **Windows Explorer** na pasta `reports/`
2. De um clique duplo em qualquer arquivo `.html` (ex: `relatorio_parceiro_a.html`)
3. O navegador padrao vai abrir com o relatorio formatado

ou usar a extensão live server para vizualizar os arquivos em html  no navegador


## Saidas geradas

```
C:\Users\PC\Desktop\desafiomeliuz\
|-- reports/
|   |-- relatorio_parceiro_a.md        # relatorio individual (texto)
|   |-- relatorio_parceiro_a.html      # relatorio individual (visual)
|   |-- relatorio_parceiro_b.md
|   |-- relatorio_parceiro_b.html
|   |-- relatorio_parceiro_c.md
|   |-- relatorio_parceiro_c.html
|   |-- relatorio_consolidado.md       # consolidado dos 3 (texto)
|   |-- relatorio_consolidado.html     # consolidado dos 3 (visual)
|-- data/processed/
|   `-- ab_tests_tracking.csv          # planilha de acompanhamento local
```

Quando `--sync-sheets-webhook` ou `--sync-google-sheets` e usado, o mesmo conteudo do CSV vai para o Google Sheets.

## Como validar

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## Criterios de decisao

1. Ler e validar o CSV, normalizando cabecalhos e valores monetarios em reais (`R$ 1.234,56`).
2. Consolidar por variante: compradores, GMV, comissao, cashback, contribuicao liquida, taxas.
3. Comparar cada variante contra o baseline (`Grupo 1`) em dias pareados com teste t (aproximacao normal).
4. Recomendar a variante com maior contribuicao liquida diaria, desde que positiva.
5. Registrar a decisao no CSV de acompanhamento.
