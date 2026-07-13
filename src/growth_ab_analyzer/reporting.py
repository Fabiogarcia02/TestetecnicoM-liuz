from __future__ import annotations

import csv
import html
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from .models import AnalysisResult, GroupSummary, MetricComparison


TRACKING_FIELDS = [
    "nome_do_teste",
    "parceiro",
    "periodo",
    "descricao",
    "resultado",
    "decisao_tomada",
    "variante_vencedora",
    "baseline",
    "quantidade_de_variantes",
    "metrica_primaria",
    "contribuicao_liquida_vencedora",
    "taxa_cashback_vencedora",
    "confianca",
    "relatorio",
    "gerado_em_utc",
]


def write_report(result: AnalysisResult, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    markdown_path = directory / _report_filename(result, "md")
    html_path = directory / _report_filename(result, "html")
    markdown_path.write_text(render_markdown_report(result), encoding="utf-8")
    html_path.write_text(render_html_report(result), encoding="utf-8")
    return html_path


def render_markdown_report(result: AnalysisResult) -> str:
    winner = next(summary for summary in result.summaries if summary.group == result.decision.winner)
    quality = "Sem alertas de qualidade." if result.quality.ok else "; ".join(result.quality.warnings)

    lines = [
        f"# Relatorio A/B - {result.partner}",
        "",
        "## Decisao",
        "",
        f"**Acao recomendada:** {result.decision.action}",
        "",
        f"**Variante vencedora:** {result.decision.winner}",
        "",
        f"**Confianca:** {result.decision.confidence}",
        "",
        f"**Racional:** {result.decision.rationale}",
        "",
        "## Contexto do teste",
        "",
        f"- Periodo: {result.start_date.isoformat()} a {result.end_date.isoformat()}",
        f"- Parceiro: {result.partner}",
        f"- Baseline: {result.baseline}",
        f"- Linhas analisadas: {result.quality.row_count}",
        f"- Qualidade dos dados: {quality}",
        "",
        "## Leitura executiva",
        "",
        _executive_summary(result, winner),
        "",
        "## Metricas por variante",
        "",
        "| Variante | Dias | Compradores | GMV | Comissao | Cashback | Contribuicao liquida | Cashback/GMV | Margem liquida | Liquido/dia | Liquido/comprador |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for summary in sorted(result.summaries, key=lambda item: item.avg_daily_net_revenue, reverse=True):
        lines.append(_summary_row(summary))

    lines.extend(
        [
            "",
            f"## Comparacao contra baseline ({result.baseline})",
            "",
            "| Variante | Metrica | Dias pareados | Delta medio diario | Delta % | IC 95% delta | p-valor aprox. |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )

    for comparison in result.comparisons:
        lines.append(_comparison_row(comparison))

    lines.extend(
        [
            "",
            "## Observacoes e proximos cuidados",
            "",
            "- O dataset nao traz usuarios expostos/sessoes; por isso a analise nao estima taxa de conversao real.",
            "- A decisao prioriza contribuicao liquida diaria (comissao menos cashback), com compradores e GMV como sinais de suporte.",
            "- Se a variante vencedora for escalada, acompanhar diariamente margem liquida, GMV e volume de compradores para detectar mudanca de mix.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html_report(result: AnalysisResult) -> str:
    winner = next(summary for summary in result.summaries if summary.group == result.decision.winner)
    quality = "Sem alertas de qualidade." if result.quality.ok else "; ".join(result.quality.warnings)
    sorted_summaries = sorted(result.summaries, key=lambda item: item.avg_daily_net_revenue, reverse=True)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatorio A/B - {html.escape(result.partner)}</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --surface: #ffffff;
      --ink: #202124;
      --muted: #5f6368;
      --line: #dfe3e8;
      --accent: #087f5b;
      --accent-soft: #e6f4ef;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 Arial, Helvetica, sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 24px 56px;
    }}
    header {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 28px;
      margin-bottom: 18px;
    }}
    h1, h2 {{
      margin: 0;
      line-height: 1.2;
    }}
    h1 {{
      font-size: 28px;
    }}
    h2 {{
      font-size: 18px;
      margin-bottom: 12px;
    }}
    section {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
      margin-top: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
      background: #fafbfc;
    }}
    .decision {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 22px;
    }}
    .kpi {{
      background: var(--accent-soft);
      border: 1px solid #cce8dd;
      border-radius: 8px;
      padding: 14px;
    }}
    .kpi span {{
      color: var(--muted);
      display: block;
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .kpi strong {{
      color: var(--accent);
      display: block;
      font-size: 18px;
    }}
    .muted {{
      color: var(--muted);
    }}
    .callout {{
      border-left: 4px solid var(--accent);
      padding-left: 14px;
      margin-top: 16px;
      font-size: 16px;
    }}
    ul {{
      margin: 10px 0 0;
      padding-left: 20px;
    }}
    @media (max-width: 820px) {{
      main {{
        padding: 18px 12px 32px;
      }}
      .decision {{
        grid-template-columns: 1fr;
      }}
      section {{
        overflow-x: auto;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="muted">Teste A/B de cashback</p>
      <h1>{html.escape(result.partner)}</h1>
      <p class="muted">Periodo: {result.start_date.isoformat()} a {result.end_date.isoformat()} | Baseline: {html.escape(result.baseline)}</p>
      <div class="decision">
        <div class="kpi"><span>Acao recomendada</span><strong>{html.escape(result.decision.action)}</strong></div>
        <div class="kpi"><span>Confianca</span><strong>{html.escape(result.decision.confidence)}</strong></div>
        <div class="kpi"><span>Liquido vencedor</span><strong>{format_money(winner.net_revenue)}</strong></div>
        <div class="kpi"><span>Cashback/GMV</span><strong>{format_pct(winner.cashback_rate)}</strong></div>
      </div>
      <p class="callout">{html.escape(result.decision.action)} {html.escape(result.decision.rationale)}</p>
    </header>

    <section>
      <h2>Leitura executiva</h2>
      <p>{html.escape(_executive_summary(result, winner))}</p>
      <p class="muted">Qualidade dos dados: {html.escape(quality)} Linhas analisadas: {result.quality.row_count}.</p>
    </section>

    <section>
      <h2>Metricas por variante</h2>
      <table>
        <thead>
          <tr>
            <th>Variante</th><th>Dias</th><th>Compradores</th><th>GMV</th><th>Comissao</th>
            <th>Cashback</th><th>Contribuicao liquida</th><th>Cashback/GMV</th>
            <th>Margem liquida</th><th>Liquido/dia</th><th>Liquido/comprador</th>
          </tr>
        </thead>
        <tbody>
          {"".join(_summary_html_row(summary) for summary in sorted_summaries)}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Comparacao contra baseline ({html.escape(result.baseline)})</h2>
      <table>
        <thead>
          <tr>
            <th>Variante</th><th>Metrica</th><th>Dias pareados</th><th>Delta medio diario</th>
            <th>Delta %</th><th>IC 95% delta</th><th>p-valor aprox.</th>
          </tr>
        </thead>
        <tbody>
          {"".join(_comparison_html_row(comparison) for comparison in result.comparisons)}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Observacoes e proximos cuidados</h2>
      <ul>
        <li>O dataset nao traz usuarios expostos/sessoes; por isso a analise nao estima taxa de conversao real.</li>
        <li>A decisao prioriza contribuicao liquida diaria, com compradores e GMV como sinais de suporte.</li>
        <li>Se a variante vencedora for escalada, acompanhar diariamente margem liquida, GMV e volume de compradores.</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""


def upsert_tracking_row(result: AnalysisResult, report_path: Path, tracking_path: str | Path) -> None:
    path = Path(tracking_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_rows = []

    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as file:
            existing_rows = list(csv.DictReader(file))

    new_row = build_tracking_row(result, report_path)
    existing_rows = [row for row in existing_rows if row.get("nome_do_teste") != result.test_name]
    existing_rows.append(new_row)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TRACKING_FIELDS)
        writer.writeheader()
        writer.writerows(existing_rows)


def write_consolidated_report(results: list[AnalysisResult], output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "relatorio_consolidado.md"
    html_path = directory / "relatorio_consolidado.html"

    lines = [
        "# Relatorio consolidado dos testes A/B",
        "",
        "| Parceiro | Periodo | Vencedor | Decisao | Confianca | Contribuicao liquida vencedora | Cashback/GMV vencedor |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for result in results:
        winner = next(summary for summary in result.summaries if summary.group == result.decision.winner)
        lines.append(
            "| {partner} | {period} | {winner} | {decision} | {confidence} | {net} | {rate} |".format(
                partner=result.partner,
                period=f"{result.start_date.isoformat()} a {result.end_date.isoformat()}",
                winner=result.decision.winner,
                decision=result.decision.action,
                confidence=result.decision.confidence,
                net=format_money(winner.net_revenue),
                rate=format_pct(winner.cashback_rate),
            )
        )

    lines.extend(
        [
            "",
            "## Resumo das decisoes",
            "",
        ]
    )
    for result in results:
        lines.append(f"- {result.partner}: {result.decision.action} {result.decision.rationale}")

    markdown = "\n".join(lines) + "\n"
    path.write_text(markdown, encoding="utf-8")
    html_path.write_text(render_consolidated_html_report(results), encoding="utf-8")
    return html_path


def render_consolidated_html_report(results: list[AnalysisResult]) -> str:
    rows = []
    items = []
    for result in results:
        winner = next(summary for summary in result.summaries if summary.group == result.decision.winner)
        rows.append(
            "<tr>"
            f"<td>{html.escape(result.partner)}</td>"
            f"<td>{result.start_date.isoformat()} a {result.end_date.isoformat()}</td>"
            f"<td>{html.escape(result.decision.winner)}</td>"
            f"<td>{html.escape(result.decision.action)}</td>"
            f"<td>{html.escape(result.decision.confidence)}</td>"
            f"<td>{format_money(winner.net_revenue)}</td>"
            f"<td>{format_pct(winner.cashback_rate)}</td>"
            "</tr>"
        )
        items.append(f"<li><strong>{html.escape(result.partner)}:</strong> {html.escape(result.decision.action)} {html.escape(result.decision.rationale)}</li>")

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatorio consolidado dos testes A/B</title>
  <style>
    body {{ margin: 0; background: #f6f7f9; color: #202124; font: 14px/1.5 Arial, Helvetica, sans-serif; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 32px 24px 56px; }}
    header, section {{ background: #fff; border: 1px solid #dfe3e8; border-radius: 8px; padding: 24px; margin-bottom: 18px; }}
    h1, h2 {{ margin: 0 0 12px; line-height: 1.2; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 18px; }}
    p {{ color: #5f6368; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #dfe3e8; padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6368; background: #fafbfc; }}
    li {{ margin-bottom: 8px; }}
    @media (max-width: 820px) {{ main {{ padding: 18px 12px 32px; }} section {{ overflow-x: auto; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Relatorio consolidado dos testes A/B</h1>
      <p>Resumo executivo das decisoes de escala para os datasets analisados.</p>
    </header>
    <section>
      <h2>Resumo consolidado</h2>
      <table>
        <thead>
          <tr><th>Parceiro</th><th>Periodo</th><th>Vencedor</th><th>Decisao</th><th>Confianca</th><th>Liquido vencedor</th><th>Cashback/GMV</th></tr>
        </thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </section>
    <section>
      <h2>Resumo das decisoes</h2>
      <ul>{"".join(items)}</ul>
    </section>
  </main>
</body>
</html>
"""


def build_tracking_row(result: AnalysisResult, report_path: Path) -> dict[str, str]:
    winner = next(summary for summary in result.summaries if summary.group == result.decision.winner)
    return {
        "nome_do_teste": result.test_name,
        "parceiro": result.partner,
        "periodo": f"{result.start_date.isoformat()} a {result.end_date.isoformat()}",
        "descricao": "Teste A/B de variantes de cashback por grupo de usuarios.",
        "resultado": result.decision.rationale,
        "decisao_tomada": result.decision.action,
        "variante_vencedora": result.decision.winner,
        "baseline": result.baseline,
        "quantidade_de_variantes": str(len(result.summaries)),
        "metrica_primaria": result.decision.primary_metric,
        "contribuicao_liquida_vencedora": format_money(winner.net_revenue),
        "taxa_cashback_vencedora": format_pct(winner.cashback_rate),
        "confianca": result.decision.confidence,
        "relatorio": str(report_path.as_posix()),
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _executive_summary(result: AnalysisResult, winner: GroupSummary) -> str:
    return (
        f"{winner.group} e a recomendacao para {result.partner}: gerou "
        f"{format_money(winner.net_revenue)} de contribuicao liquida no periodo, "
        f"media de {format_money(winner.avg_daily_net_revenue)} por dia, "
        f"com taxa de cashback de {format_pct(winner.cashback_rate)} sobre GMV. "
        "A leitura considera contribuicao liquida como metrica primaria porque cashback e custo direto."
    )


def _summary_row(summary: GroupSummary) -> str:
    buyers = f"{summary.buyers:,}".replace(",", ".")
    return (
        f"| {summary.group} | {summary.days} | {buyers} | "
        f"{format_money(summary.gmv)} | {format_money(summary.commission)} | "
        f"{format_money(summary.cashback)} | {format_money(summary.net_revenue)} | "
        f"{format_pct(summary.cashback_rate)} | {format_pct(summary.net_margin_rate)} | "
        f"{format_money(summary.avg_daily_net_revenue)} | {format_money(summary.net_revenue_per_buyer)} |"
    )


def _comparison_row(comparison: MetricComparison) -> str:
    metric_labels = {
        "net_revenue": "Contribuicao liquida",
        "buyers": "Compradores",
        "gmv": "GMV",
    }
    return (
        f"| {comparison.variant} | {metric_labels[comparison.metric]} | "
        f"{comparison.overlap_days} | {format_decimal(comparison.mean_delta)} | "
        f"{format_pct(comparison.pct_delta)} | "
        f"{format_decimal(comparison.ci_low)} a {format_decimal(comparison.ci_high)} | "
        f"{format_decimal(comparison.p_value_approx, places=4)} |"
    )


def _summary_html_row(summary: GroupSummary) -> str:
    buyers = f"{summary.buyers:,}".replace(",", ".")
    cells = [
        summary.group,
        str(summary.days),
        buyers,
        format_money(summary.gmv),
        format_money(summary.commission),
        format_money(summary.cashback),
        format_money(summary.net_revenue),
        format_pct(summary.cashback_rate),
        format_pct(summary.net_margin_rate),
        format_money(summary.avg_daily_net_revenue),
        format_money(summary.net_revenue_per_buyer),
    ]
    return "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>"


def _comparison_html_row(comparison: MetricComparison) -> str:
    metric_labels = {
        "net_revenue": "Contribuicao liquida",
        "buyers": "Compradores",
        "gmv": "GMV",
    }
    cells = [
        comparison.variant,
        metric_labels[comparison.metric],
        str(comparison.overlap_days),
        format_decimal(comparison.mean_delta),
        format_pct(comparison.pct_delta),
        f"{format_decimal(comparison.ci_low)} a {format_decimal(comparison.ci_high)}",
        format_decimal(comparison.p_value_approx, places=4),
    ]
    return "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>"


def _report_filename(result: AnalysisResult, extension: str) -> str:
    slug = result.partner.lower().replace(" ", "_")
    return f"relatorio_{slug}.{extension}"


def format_money(value: Decimal) -> str:
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    formatted = f"{quantized:,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(value: Decimal) -> str:
    return f"{format_decimal(value * Decimal('100'))}%"


def format_decimal(value: Decimal, places: int = 2) -> str:
    quant = Decimal("1").scaleb(-places)
    return str(value.quantize(quant, rounding=ROUND_HALF_UP)).replace(".", ",")
