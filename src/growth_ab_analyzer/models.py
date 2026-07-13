from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path


Money = Decimal


@dataclass(frozen=True)
class Observation:
    date: date
    group: str
    partner: str
    buyers: int
    commission: Money
    cashback: Money
    gmv: Money

    @property
    def net_revenue(self) -> Money:
        return self.commission - self.cashback


@dataclass(frozen=True)
class DataQualityReport:
    row_count: int
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.warnings


@dataclass(frozen=True)
class GroupSummary:
    group: str
    days: int
    buyers: int
    commission: Money
    cashback: Money
    gmv: Money
    net_revenue: Money
    avg_daily_buyers: Decimal
    avg_daily_gmv: Money
    avg_daily_net_revenue: Money
    cashback_rate: Decimal
    commission_rate: Decimal
    net_margin_rate: Decimal
    net_revenue_per_buyer: Money


@dataclass(frozen=True)
class MetricComparison:
    metric: str
    variant: str
    baseline: str
    overlap_days: int
    mean_delta: Decimal
    pct_delta: Decimal
    ci_low: Decimal
    ci_high: Decimal
    p_value_approx: Decimal


@dataclass(frozen=True)
class Decision:
    winner: str
    action: str
    rationale: str
    confidence: str
    primary_metric: str


@dataclass(frozen=True)
class AnalysisResult:
    test_name: str
    partner: str
    start_date: date
    end_date: date
    baseline: str
    summaries: tuple[GroupSummary, ...]
    comparisons: tuple[MetricComparison, ...]
    decision: Decision
    quality: DataQualityReport
    source_path: Path
