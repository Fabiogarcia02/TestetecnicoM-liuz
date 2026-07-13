from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from statistics import mean, stdev

from .models import (
    AnalysisResult,
    DataQualityReport,
    Decision,
    GroupSummary,
    MetricComparison,
    Observation,
)

PRIMARY_METRIC = "contribuicao_liquida_diaria"
SUPPORT_METRICS = ("net_revenue", "buyers", "gmv")


def analyze_observations(
    observations: list[Observation],
    quality: DataQualityReport,
    source_path: str | Path,
    baseline: str = "Grupo 1",
) -> AnalysisResult:
    if not observations:
        raise ValueError("Cannot analyze an empty dataset")

    groups = sorted({row.group for row in observations})
    if baseline not in groups:
        baseline = groups[0]

    partner = sorted({row.partner for row in observations})[0]
    start_date = min(row.date for row in observations)
    end_date = max(row.date for row in observations)
    summaries = tuple(_summarize_group(group, observations) for group in groups)
    comparisons = tuple(_compare_against_baseline(observations, baseline))
    decision = _make_decision(summaries, comparisons, baseline)
    test_name = f"Teste cashback - {partner} ({start_date.isoformat()} a {end_date.isoformat()})"

    return AnalysisResult(
        test_name=test_name,
        partner=partner,
        start_date=start_date,
        end_date=end_date,
        baseline=baseline,
        summaries=summaries,
        comparisons=comparisons,
        decision=decision,
        quality=quality,
        source_path=Path(source_path),
    )


def _summarize_group(group: str, observations: list[Observation]) -> GroupSummary:
    rows = [row for row in observations if row.group == group]
    days = len({row.date for row in rows})
    buyers = sum(row.buyers for row in rows)
    commission = sum(row.commission for row in rows)
    cashback = sum(row.cashback for row in rows)
    gmv = sum(row.gmv for row in rows)
    net_revenue = commission - cashback

    return GroupSummary(
        group=group,
        days=days,
        buyers=buyers,
        commission=commission,
        cashback=cashback,
        gmv=gmv,
        net_revenue=net_revenue,
        avg_daily_buyers=_safe_div(Decimal(buyers), Decimal(days)),
        avg_daily_gmv=_safe_div(gmv, Decimal(days)),
        avg_daily_net_revenue=_safe_div(net_revenue, Decimal(days)),
        cashback_rate=_safe_div(cashback, gmv),
        commission_rate=_safe_div(commission, gmv),
        net_margin_rate=_safe_div(net_revenue, gmv),
        net_revenue_per_buyer=_safe_div(net_revenue, Decimal(buyers)),
    )


def _compare_against_baseline(
    observations: list[Observation],
    baseline: str,
) -> list[MetricComparison]:
    by_group_date: dict[str, dict[date, Observation]] = defaultdict(dict)
    for row in observations:
        by_group_date[row.group][row.date] = row

    comparisons: list[MetricComparison] = []
    for variant in sorted(by_group_date):
        if variant == baseline:
            continue

        common_dates = sorted(set(by_group_date[baseline]) & set(by_group_date[variant]))
        for metric in SUPPORT_METRICS:
            baseline_values = [_metric_value(by_group_date[baseline][day], metric) for day in common_dates]
            variant_values = [_metric_value(by_group_date[variant][day], metric) for day in common_dates]
            deltas = [variant_value - baseline_value for variant_value, baseline_value in zip(variant_values, baseline_values)]
            baseline_mean = Decimal(str(mean(float(value) for value in baseline_values))) if baseline_values else Decimal("0")
            stats = _delta_stats(deltas)
            comparisons.append(
                MetricComparison(
                    metric=metric,
                    variant=variant,
                    baseline=baseline,
                    overlap_days=len(common_dates),
                    mean_delta=stats["mean"],
                    pct_delta=_safe_div(stats["mean"], baseline_mean),
                    ci_low=stats["ci_low"],
                    ci_high=stats["ci_high"],
                    p_value_approx=stats["p_value"],
                )
            )

    return comparisons


def _metric_value(observation: Observation, metric: str) -> Decimal:
    if metric == "net_revenue":
        return observation.net_revenue
    if metric == "buyers":
        return Decimal(observation.buyers)
    if metric == "gmv":
        return observation.gmv
    raise ValueError(f"Unknown metric: {metric}")


def _delta_stats(deltas: list[Decimal]) -> dict[str, Decimal]:
    if not deltas:
        return {
            "mean": Decimal("0"),
            "ci_low": Decimal("0"),
            "ci_high": Decimal("0"),
            "p_value": Decimal("1"),
        }

    values = [float(delta) for delta in deltas]
    avg = mean(values)
    if len(values) < 2:
        return {
            "mean": Decimal(str(avg)),
            "ci_low": Decimal(str(avg)),
            "ci_high": Decimal(str(avg)),
            "p_value": Decimal("1"),
        }

    standard_error = stdev(values) / math.sqrt(len(values))
    ci_low = avg - 1.96 * standard_error
    ci_high = avg + 1.96 * standard_error
    z_score = abs(avg / standard_error) if standard_error else float("inf")
    p_value = math.erfc(z_score / math.sqrt(2)) if math.isfinite(z_score) else 0.0

    return {
        "mean": Decimal(str(avg)),
        "ci_low": Decimal(str(ci_low)),
        "ci_high": Decimal(str(ci_high)),
        "p_value": Decimal(str(p_value)),
    }


def _make_decision(
    summaries: tuple[GroupSummary, ...],
    comparisons: tuple[MetricComparison, ...],
    baseline: str,
) -> Decision:
    ranked = sorted(summaries, key=lambda item: item.avg_daily_net_revenue, reverse=True)
    winner = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else ranked[0]

    if winner.net_revenue <= 0:
        return Decision(
            winner=baseline,
            action=f"Nao escalar variantes com contribuicao liquida nao positiva; manter {baseline}.",
            rationale="Nenhuma variante gerou contribuicao liquida positiva suficiente para justificar escala.",
            confidence="alta",
            primary_metric=PRIMARY_METRIC,
        )

    lift_vs_runner_up = _safe_div(
        winner.avg_daily_net_revenue - runner_up.avg_daily_net_revenue,
        runner_up.avg_daily_net_revenue,
    )

    if winner.group == baseline:
        confidence = "alta" if lift_vs_runner_up >= Decimal("0.10") else "media"
        return Decision(
            winner=winner.group,
            action=f"Escalar {winner.group} para 100% do trafego.",
            rationale=(
                f"{winner.group} teve a maior contribuicao liquida diaria. "
                "As demais variantes aumentaram o custo de cashback sem compensar em margem."
            ),
            confidence=confidence,
            primary_metric=PRIMARY_METRIC,
        )

    net_comparison = next(
        (
            comparison
            for comparison in comparisons
            if comparison.variant == winner.group and comparison.metric == "net_revenue"
        ),
        None,
    )
    statistically_positive = bool(net_comparison and net_comparison.ci_low > 0)
    confidence = "alta" if statistically_positive else "media"
    monitoring = "" if statistically_positive else " com monitoramento diario de margem"

    return Decision(
        winner=winner.group,
        action=f"Escalar {winner.group} para 100% do trafego{monitoring}.",
        rationale=f"{winner.group} maximizou a contribuicao liquida diaria entre as variantes.",
        confidence=confidence,
        primary_metric=PRIMARY_METRIC,
    )


def _safe_div(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return Decimal("0")
    return numerator / denominator
