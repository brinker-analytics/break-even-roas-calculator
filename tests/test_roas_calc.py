import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import roas_calc as rc  # noqa: E402


class OrderMath(unittest.TestCase):
    def setUp(self):
        # The made-up $60 order used in the README.
        self.m = rc.margin_before_ad_spend(60, product_cost=21, shipping_fulfillment=9,
                                           payment_fees=1.8, returns_allowance=3)

    def test_margin_before_ad_spend(self):
        self.assertAlmostEqual(self.m.variable_costs, 34.80)
        self.assertAlmostEqual(self.m.margin_dollars, 25.20)
        self.assertAlmostEqual(self.m.margin_share, 0.42)

    def test_break_even_roas_is_one_over_margin_share(self):
        self.assertAlmostEqual(rc.break_even_roas(self.m.margin_share), 60 / 25.2)

    def test_break_even_cpa_is_dollar_margin(self):
        self.assertAlmostEqual(rc.break_even_cpa(self.m.margin_dollars), 25.20)

    def test_roas_below_break_even_loses_money(self):
        self.assertAlmostEqual(rc.profit_per_order_at_roas(60, 25.2, 2.0), -4.80)

    def test_profit_is_zero_at_break_even(self):
        be = rc.break_even_roas(self.m.margin_share)
        self.assertAlmostEqual(rc.profit_per_order_at_roas(60, 25.2, be), 0.0)

    def test_discounts_reduce_revenue(self):
        m = rc.margin_before_ad_spend(60, discounts=10, product_cost=21)
        self.assertAlmostEqual(m.revenue, 50)
        self.assertAlmostEqual(m.margin_dollars, 29)


class Undefined(unittest.TestCase):
    def test_no_break_even_when_margin_is_zero_or_negative(self):
        self.assertIsNone(rc.break_even_roas(0))
        self.assertIsNone(rc.break_even_roas(-0.1))
        self.assertIsNone(rc.break_even_roas(None))
        self.assertIsNone(rc.break_even_cpa(0))

    def test_no_mer_without_spend(self):
        self.assertIsNone(rc.mer(1000, 0))

    def test_ebitda_break_even_undefined_when_fixed_costs_eat_margin(self):
        self.assertIsNone(rc.ebitda_break_even_mer(100000, 42000, 42000))

    def test_negative_costs_rejected(self):
        with self.assertRaises(ValueError):
            rc.margin_before_ad_spend(60, product_cost=-1)


class WholeBusiness(unittest.TestCase):
    def test_mer(self):
        self.assertAlmostEqual(rc.mer(100000, 25000), 4.0)

    def test_break_even_mer_matches_one_over_margin(self):
        self.assertAlmostEqual(rc.break_even_mer(0.5), 2.0)

    def test_ebitda_break_even_mer_is_above_zero_contribution_line(self):
        zero_line = rc.break_even_mer(0.42)
        ebitda_line = rc.ebitda_break_even_mer(100000, 42000, 8000)
        self.assertAlmostEqual(ebitda_line, 100000 / 34000)
        self.assertGreater(ebitda_line, zero_line)


class Targets(unittest.TestCase):
    def test_target_iroas_is_good_month_mer_minus_baseline(self):
        self.assertAlmostEqual(rc.target_iroas(3.0, 0.8), 2.2)

    def test_zero_baseline_allowed(self):
        self.assertAlmostEqual(rc.target_iroas(3.0, 0), 3.0)

    def test_iroas(self):
        self.assertAlmostEqual(rc.iroas(66000, 30000), 2.2)
        self.assertIsNone(rc.iroas(1000, 0))

    def test_compare(self):
        self.assertEqual(rc.compare(2.2, 3.0 - 0.8), "at")
        self.assertEqual(rc.compare(2.0, 2.38), "below")
        self.assertEqual(rc.compare(None, 2.0), "undefined")


class Cli(unittest.TestCase):
    def test_cli_runs(self):
        self.assertEqual(rc.main(["order", "--aov", "60", "--product-cost", "21", "--roas", "2"]), 0)
        self.assertEqual(rc.main(["--json", "mer", "--revenue", "100", "--spend", "20"]), 0)
        self.assertEqual(rc.main(["iroas", "--incremental-revenue", "50", "--spend", "20"]), 0)


if __name__ == "__main__":
    unittest.main()
