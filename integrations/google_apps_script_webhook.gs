const SHEET_NAME = 'testes_ab';
const ACCESS_TOKEN = ''; // Opcional: preencha e use --sheets-webhook-token no Python.

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');

    if (ACCESS_TOKEN && payload.token !== ACCESS_TOKEN) {
      return jsonResponse({ ok: false, error: 'Token invalido.' });
    }

    const rows = payload.rows;
    if (!Array.isArray(rows) || rows.length === 0) {
      return jsonResponse({ ok: false, error: 'Payload sem linhas.' });
    }

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);

    sheet.clearContents();
    sheet.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, rows[0].length);
    sheet.getRange(1, 1, 1, rows[0].length).setFontWeight('bold').setBackground('#e6f4ef');

    return jsonResponse({ ok: true, url: spreadsheet.getUrl() });
  } catch (error) {
    return jsonResponse({ ok: false, error: String(error) });
  }
}

function jsonResponse(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
