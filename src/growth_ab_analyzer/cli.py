from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

from .analysis import analyze_observations
from .google_sheets import sync_csv_to_apps_script_webhook, sync_csv_to_google_sheets
from .loader import load_dataset
from .reporting import upsert_tracking_row, write_consolidated_report, write_report


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    dataset_paths = _expand_paths(args.datasets)
    if not dataset_paths:
        parser.error("Nenhum dataset encontrado.")

    results = []
    for dataset_path in dataset_paths:
        observations, quality = load_dataset(dataset_path)
        result = analyze_observations(
            observations=observations,
            quality=quality,
            source_path=dataset_path,
            baseline=args.baseline,
        )
        report_path = write_report(result, args.reports_dir)
        upsert_tracking_row(result, report_path, args.tracking_csv)
        results.append(result)
        print(f"OK: {dataset_path} -> {report_path} | decisao: {result.decision.action}")

    if len(results) > 1:
        consolidated_path = write_consolidated_report(results, args.reports_dir)
        print(f"OK: relatorio consolidado -> {consolidated_path}")

    if args.sync_google_sheets:
        if not args.google_credentials:
            raise SystemExit(
                "Credenciais Google nao informadas. Use --google-credentials ou "
                "configure GOOGLE_APPLICATION_CREDENTIALS."
            )
        sheet_url = sync_csv_to_google_sheets(
            tracking_csv=args.tracking_csv,
            credentials_path=args.google_credentials,
            spreadsheet_id=args.spreadsheet_id,
            spreadsheet_title=args.spreadsheet_title,
            share_public=args.share_public,
            share_with_email=args.share_with_email,
        )
        print(f"OK: Google Sheets atualizado -> {sheet_url}")

    if args.sync_sheets_webhook:
        if not args.sheets_webhook_url:
            raise SystemExit(
                "URL do Apps Script nao informada. Use --sheets-webhook-url ou "
                "configure GOOGLE_SHEETS_WEBHOOK_URL."
            )
        sheet_url = sync_csv_to_apps_script_webhook(
            tracking_csv=args.tracking_csv,
            webhook_url=args.sheets_webhook_url,
            token=args.sheets_webhook_token,
        )
        print(f"OK: Google Sheets atualizado via Apps Script -> {sheet_url}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analisa testes A/B de cashback e gera relatorios + CSV de acompanhamento.",
    )
    parser.add_argument(
        "datasets",
        nargs="+",
        help="Caminhos dos CSVs. Aceita globs como data/raw/*.csv.",
    )
    parser.add_argument(
        "--baseline",
        default="Grupo 1",
        help="Grupo usado como baseline. Padrao: Grupo 1.",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Diretorio de saida dos relatorios Markdown.",
    )
    parser.add_argument(
        "--tracking-csv",
        default="data/processed/ab_tests_tracking.csv",
        help="CSV de acompanhamento no formato de planilha.",
    )
    parser.add_argument(
        "--sync-google-sheets",
        action="store_true",
        help="Cria/atualiza uma planilha no Google Sheets a partir do CSV de acompanhamento.",
    )
    parser.add_argument(
        "--google-credentials",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        help="Caminho do JSON da service account. Tambem pode vir de GOOGLE_APPLICATION_CREDENTIALS.",
    )
    parser.add_argument(
        "--spreadsheet-id",
        default=None,
        help="ID de uma planilha existente. Se omitido, cria uma nova planilha.",
    )
    parser.add_argument(
        "--spreadsheet-title",
        default="Acompanhamento de testes AB - Meliuz",
        help="Titulo usado ao criar uma nova planilha.",
    )
    parser.add_argument(
        "--share-public",
        action="store_true",
        help="Compartilha a planilha criada/atualizada como leitura publica.",
    )
    parser.add_argument(
        "--share-with-email",
        default=None,
        help="Opcional: compartilha a planilha com um e-mail como editor.",
    )
    parser.add_argument(
        "--sync-sheets-webhook",
        action="store_true",
        help="Sincroniza o CSV com Google Sheets usando um Web App do Google Apps Script.",
    )
    parser.add_argument(
        "--sheets-webhook-url",
        default=os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL"),
        help="URL do Web App do Google Apps Script. Tambem pode vir de GOOGLE_SHEETS_WEBHOOK_URL.",
    )
    parser.add_argument(
        "--sheets-webhook-token",
        default=os.environ.get("GOOGLE_SHEETS_WEBHOOK_TOKEN"),
        help="Token simples opcional para proteger o Web App.",
    )
    return parser


def _expand_paths(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw_path in paths:
        matches = [Path(match) for match in glob.glob(raw_path)]
        expanded.extend(matches or [Path(raw_path)])

    unique_paths = []
    seen = set()
    for path in expanded:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_paths.append(path)

    missing = [str(path) for path in unique_paths if not path.exists()]
    if missing:
        raise SystemExit(f"Dataset nao encontrado: {', '.join(missing)}")

    return unique_paths


if __name__ == "__main__":
    main(sys.argv[1:])
