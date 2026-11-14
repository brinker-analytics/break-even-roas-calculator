#!/usr/bin/env python3
"""Break-even ROAS, break-even CPA, MER, break-even MER, target iROAS and iROAS.

Standard library only. Every function returns None when the answer is undefined
(for example a margin of zero or less), so a caller never gets a divide-by-zero
or a meaningless negative "break-even".

By Eric Brinker, Brinker Analytics (https://brinkeranalytics.com). MIT license.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class OrderMargin:
    """Margin before ad spend for one order, in dollars and as a share of revenue."""

    revenue: float
    variable_costs: float
    margin_dollars: float
    margin_share: Optional[float]


def margin_before_ad_spend(
    aov: float,
    discounts: float = 0.0,
    product_cost: float = 0.0,
    shipping_fulfillment: float = 0.0,
    payment_fees: float = 0.0,
    returns_allowance: float = 0.0,
    other_variable: float = 0.0,
) -> OrderMargin:
    """What's left of one order after variable costs, before ad spend.

    `aov` is the order value before discounts; `discounts` come off it to give
    revenue. Every other cost is in dollars per order, on the same revenue base.
    This is not called gross margin on purpose: sources label it differently.
    """
    for name, v in (("aov", aov), ("discounts", discounts), ("product_cost", product_cost),
                    ("shipping_fulfillment", shipping_fulfillment), ("payment_fees", payment_fees),
                    ("returns_allowance", returns_allowance), ("other_variable", other_variable)):
        if v < 0:
            raise ValueError(f"{name} can't be negative")
    revenue = aov - discounts
    variable = product_cost + shipping_fulfillment + payment_fees + returns_allowance + other_variable
    margin = revenue - variable
    share = margin / revenue if revenue > 0 else None
    return OrderMargin(round(revenue, 6), round(variable, 6), round(margin, 6),
                       None if share is None else round(share, 6))


def break_even_roas(margin_share: Optional[float]) -> Optional[float]:
    """1 / margin before ad spend (as a share of revenue). None if the margin is zero or less."""
    if margin_share is None or margin_share <= 0:
        return None
    return 1.0 / margin_share


def break_even_cpa(margin_dollars: float) -> Optional[float]:
    """The most you can pay in ad spend per first order without losing money on it."""
    return margin_dollars if margin_dollars > 0 else None


def profit_per_order_at_roas(revenue: float, margin_dollars: float, roas: float) -> Optional[float]:
    """First-order profit after ad spend when ads return `roas` on this order's revenue."""
    if roas <= 0:
        return None
    return margin_dollars - revenue / roas


def mer(total_revenue: float, total_marketing_spend: float) -> Optional[float]:
    """Marketing efficiency ratio: store revenue / total marketing spend."""
    if total_marketing_spend <= 0:
        return None
    return total_revenue / total_marketing_spend


def break_even_mer(whole_business_margin_share: Optional[float]) -> Optional[float]:
    """Zero-contribution line: 1 / (whole-business margin before marketing, as a share of revenue).

    The MER at which marketing spend has used up the margin before marketing.
    It is not EBITDA break-even, which also has to cover fixed costs.
    """
    return break_even_roas(whole_business_margin_share)


def ebitda_break_even_mer(revenue: float, margin_before_marketing_dollars: float,
                          fixed_costs: float) -> Optional[float]:
    """revenue / (margin before marketing in dollars - fixed costs in dollars)."""
    room = margin_before_marketing_dollars - fixed_costs
    if room <= 0 or revenue <= 0:
        return None
    return revenue / room


def target_iroas(good_month_mer: float, baseline_credit: float = 0.0) -> Optional[float]:
    """Good-month MER minus the return credited to always-on demand and seasonality.

    `baseline_credit` is written as a multiple, like MER. 0 is allowed (it means
    100% of the business is credited to paid advertising).
    """
    if baseline_credit < 0:
        raise ValueError("baseline_credit can't be negative")
    t = good_month_mer - baseline_credit
    return t if t > 0 else None


def iroas(incremental_revenue: float, spend_changed: float) -> Optional[float]:
    """Incremental revenue from a test / the spend that differed between the cells."""
    if spend_changed <= 0:
        return None
    return incremental_revenue / spend_changed


def compare(value: Optional[float], line: Optional[float]) -> str:
    if value is None or line is None:
        return "undefined"
    if abs(value - line) < 1e-9:
        return "at"
    return "above" if value > line else "below"


def _fmt(x: Optional[float], unit: str = "x") -> str:
    if x is None:
        return "undefined"
    if unit == "$":
        return f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}"
    if unit == "%":
        return f"{x * 100:.1f}%"
    return f"{x:.2f}{unit}"


def _cmd_order(a: argparse.Namespace) -> dict:
    m = margin_before_ad_spend(a.aov, a.discounts, a.product_cost, a.shipping, a.fees,
                               a.returns, a.other)
    out = {
        "revenue_per_order": m.revenue,
        "variable_costs_per_order": m.variable_costs,
        "margin_before_ad_spend": m.margin_dollars,
        "margin_share": m.margin_share,
        "break_even_roas": break_even_roas(m.margin_share),
        "break_even_cpa": break_even_cpa(m.margin_dollars),
    }
    if a.roas is not None:
        out["roas_checked"] = a.roas
        out["profit_per_order_at_roas"] = profit_per_order_at_roas(m.revenue, m.margin_dollars, a.roas)
        out["roas_vs_break_even"] = compare(a.roas, out["break_even_roas"])
    return out


def _cmd_mer(a: argparse.Namespace) -> dict:
    out = {"mer": mer(a.revenue, a.spend)}
    if a.margin_share is not None:
        out["break_even_mer"] = break_even_mer(a.margin_share)
        out["mer_vs_break_even_mer"] = compare(out["mer"], out["break_even_mer"])
        if a.fixed_costs is not None:
            out["ebitda_break_even_mer"] = ebitda_break_even_mer(
                a.revenue, a.margin_share * a.revenue, a.fixed_costs)
            out["mer_vs_ebitda_break_even_mer"] = compare(out["mer"], out["ebitda_break_even_mer"])
    return out


def _cmd_iroas(a: argparse.Namespace) -> dict:
    out = {"iroas": iroas(a.incremental_revenue, a.spend)}
    if a.good_month_mer is not None:
        out["target_iroas"] = target_iroas(a.good_month_mer, a.baseline_credit)
        out["iroas_vs_target"] = compare(out["iroas"], out["target_iroas"])
    if a.break_even_roas is not None:
        out["iroas_vs_break_even_roas"] = compare(out["iroas"], a.break_even_roas)
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("order", help="break-even ROAS and CPA for one order")
    o.add_argument("--aov", type=float, required=True, help="order value before discounts, $")
    o.add_argument("--discounts", type=float, default=0.0)
    o.add_argument("--product-cost", type=float, default=0.0)
    o.add_argument("--shipping", type=float, default=0.0, help="shipping and fulfillment, $")
    o.add_argument("--fees", type=float, default=0.0, help="payment fees, $")
    o.add_argument("--returns", type=float, default=0.0, help="returns allowance, $")
    o.add_argument("--other", type=float, default=0.0, help="other variable costs, $")
    o.add_argument("--roas", type=float, help="a ROAS to check against break-even")

    m = sub.add_parser("mer", help="MER, break-even MER and EBITDA break-even MER")
    m.add_argument("--revenue", type=float, required=True)
    m.add_argument("--spend", type=float, required=True, help="total marketing spend")
    m.add_argument("--margin-share", type=float, help="whole-business margin before marketing, 0-1")
    m.add_argument("--fixed-costs", type=float, help="fixed costs for the same period, $")

    i = sub.add_parser("iroas", help="iROAS from a test, against a target and break-even")
    i.add_argument("--incremental-revenue", type=float, required=True)
    i.add_argument("--spend", type=float, required=True, help="spend that differed between cells")
    i.add_argument("--good-month-mer", type=float)
    i.add_argument("--baseline-credit", type=float, default=0.0,
                   help="return credited to always-on demand and seasonality, as a multiple")
    i.add_argument("--break-even-roas", type=float)
    return p


def main(argv: Optional[list] = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        out = {"order": _cmd_order, "mer": _cmd_mer, "iroas": _cmd_iroas}[a.cmd](a)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(out, indent=2))
        return 0
    for k, v in out.items():
        if isinstance(v, float):
            unit = "$" if k in {"revenue_per_order", "variable_costs_per_order", "margin_before_ad_spend",
                                "break_even_cpa", "profit_per_order_at_roas"} else (
                "%" if k == "margin_share" else "x")
            v = _fmt(v, unit)
        elif v is None:
            v = "undefined"
        print(f"{k.replace('_', ' ')}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
