from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .models import DataQualityReport, Observation
from .parsing import normalize_header, parse_date, parse_int, parse_money


REQUIRED_COLUMNS = {
    "date": ("data",),
    "group": ("grupos", "usuarios"),
    "partner": ("parceiro",),
    "buyers": ("compradores",),
    "commission": ("comissao",),
    "cashback": ("cashback",),
    "gmv": ("vendas", "totais"),
}


def load_dataset(path: str | Path) -> tuple[list[Observation], DataQualityReport]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f"{source} has no header")

        column_map = _build_column_map(reader.fieldnames)
        rows = []
        warnings = []

        for line_number, raw in enumerate(reader, start=2):
            try:
                observation = Observation(
                    date=parse_date(raw[column_map["date"]]),
                    group=raw[column_map["group"]].strip(),
                    partner=raw[column_map["partner"]].strip(),
                    buyers=parse_int(raw[column_map["buyers"]]),
                    commission=parse_money(raw[column_map["commission"]]),
                    cashback=parse_money(raw[column_map["cashback"]]),
                    gmv=parse_money(raw[column_map["gmv"]]),
                )
            except Exception as exc:
                raise ValueError(f"Invalid row {line_number} in {source}: {exc}") from exc

            if observation.buyers < 0:
                warnings.append(f"Line {line_number}: compradores negativo.")
            if observation.gmv < 0 or observation.commission < 0 or observation.cashback < 0:
                warnings.append(f"Line {line_number}: valor financeiro negativo.")
            rows.append(observation)

    warnings.extend(_quality_warnings(rows))
    return rows, DataQualityReport(row_count=len(rows), warnings=tuple(warnings))


def _build_column_map(fieldnames: list[str]) -> dict[str, str]:
    normalized = {name: normalize_header(name) for name in fieldnames}
    column_map = {}

    for canonical, tokens in REQUIRED_COLUMNS.items():
        matches = [
            original
            for original, header in normalized.items()
            if all(token in header for token in tokens)
        ]
        if not matches:
            expected = " ".join(tokens)
            raise ValueError(f"Required column not found: {expected}")
        column_map[canonical] = matches[0]

    return column_map


def _quality_warnings(rows: list[Observation]) -> list[str]:
    warnings: list[str] = []
    if not rows:
        return ["Dataset vazio."]

    partners = sorted({row.partner for row in rows})
    if len(partners) > 1:
        warnings.append(f"Dataset contem mais de um parceiro: {', '.join(partners)}.")

    duplicate_keys = Counter((row.date, row.group) for row in rows)
    duplicates = [key for key, count in duplicate_keys.items() if count > 1]
    if duplicates:
        warnings.append(f"Dataset contem {len(duplicates)} combinacoes data/grupo duplicadas.")

    groups = sorted({row.group for row in rows})
    dates_by_group = {
        group: {row.date for row in rows if row.group == group}
        for group in groups
    }
    sizes = {group: len(dates) for group, dates in dates_by_group.items()}
    if len(set(sizes.values())) > 1:
        warnings.append(f"Grupos com janelas de tempo diferentes: {sizes}.")

    common_dates = set.intersection(*dates_by_group.values()) if dates_by_group else set()
    for group, dates in dates_by_group.items():
        missing = common_dates.symmetric_difference(dates)
        if missing:
            warnings.append(f"{group} tem {len(missing)} datas fora da intersecao comum.")

    return warnings
