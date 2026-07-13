from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from urllib import request


SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)


def sync_csv_to_google_sheets(
    tracking_csv: str | Path,
    credentials_path: str | Path,
    spreadsheet_id: str | None = None,
    spreadsheet_title: str = "Acompanhamento de testes AB - Meliuz",
    share_public: bool = False,
    share_with_email: str | None = None,
) -> str:
    """Create/update a Google Sheets spreadsheet from the tracking CSV."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Dependencias do Google Sheets nao instaladas. "
            "Rode: python -m pip install -e .[sheets]"
        ) from exc

    csv_path = Path(tracking_csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV de acompanhamento nao encontrado: {csv_path}")

    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=SCOPES,
    )
    sheets_service = build("sheets", "v4", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    if spreadsheet_id:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    else:
        spreadsheet = (
            sheets_service.spreadsheets()
            .create(
                body={
                    "properties": {"title": spreadsheet_title},
                    "sheets": [{"properties": {"title": "testes_ab"}}],
                },
                fields="spreadsheetId,spreadsheetUrl",
            )
            .execute()
        )
        spreadsheet_id = spreadsheet["spreadsheetId"]

    rows = _read_csv_rows(csv_path)
    _ensure_sheet_exists(sheets_service, spreadsheet_id)
    _replace_sheet_values(sheets_service, spreadsheet_id, rows)
    _format_sheet(sheets_service, spreadsheet_id)

    if share_with_email:
        _share_with_email(drive_service, spreadsheet_id, share_with_email)
    if share_public:
        _share_public_read_only(drive_service, spreadsheet_id)

    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="spreadsheetUrl",
    ).execute()
    return spreadsheet["spreadsheetUrl"]


def sync_csv_to_apps_script_webhook(
    tracking_csv: str | Path,
    webhook_url: str,
    token: str | None = None,
) -> str:
    """Send the tracking CSV to a Google Apps Script web app endpoint."""
    csv_path = Path(tracking_csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV de acompanhamento nao encontrado: {csv_path}")

    rows = _read_csv_rows(csv_path)
    payload = {"rows": rows}
    if token:
        payload["token"] = token

    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=30) as response:
        response_body = response.read().decode("utf-8")

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return response_body

    if not data.get("ok", False):
        raise RuntimeError(data.get("error", "Erro desconhecido ao sincronizar Apps Script"))
    return data.get("url", response_body)


def _read_csv_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.reader(file))


def _ensure_sheet_exists(service: Any, spreadsheet_id: str) -> None:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get("sheets", [])
    sheet_names = [s["properties"]["title"] for s in sheets]

    if "testes_ab" not in sheet_names:
        body = {"requests": [{"addSheet": {"properties": {"title": "testes_ab"}}}]}
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()


def _replace_sheet_values(service: Any, spreadsheet_id: str, rows: list[list[str]]) -> None:
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range="testes_ab!A:Z",
        body={},
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="testes_ab!A1",
        valueInputOption="USER_ENTERED",
        body={"values": rows},
    ).execute()


def _format_sheet(service: Any, spreadsheet_id: str) -> None:
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = metadata["sheets"][0]["properties"]["sheetId"]
    requests = [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.9, "green": 0.96, "blue": 0.93},
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1},
                },
                "fields": "gridProperties.frozenRowCount",
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 15,
                }
            }
        },
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests},
    ).execute()


def _share_with_email(drive_service: Any, spreadsheet_id: str, email: str) -> None:
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={"type": "user", "role": "writer", "emailAddress": email},
        sendNotificationEmail=False,
        fields="id",
    ).execute()


def _share_public_read_only(drive_service: Any, spreadsheet_id: str) -> None:
    drive_service.permissions().create(
        fileId=spreadsheet_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
    ).execute()
