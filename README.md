# break-even-roas-calculator

Work out the ROAS you need just to not lose money on a first order, the MER your whole business can carry, and the iROAS a test has to beat. One small Python file, standard library only.

> **Built by [Brinker Analytics](https://brinkeranalytics.com).** Eric Brinker's marketing-measurement practice for DTC brands.
> **Contact:** [eric@brinkeranalytics.com](mailto:eric@brinkeranalytics.com) or the [contact page](https://brinkeranalytics.com/contact).

## What each number is for

Each number answers a different question, and none of them is a one-to-one stand-in for EBITDA.

- **Break-even ROAS** is a floor on attributed or platform revenue, for one order. It assumes the platform knows which sales the ads caused and which they didn't, and it only sees part of the data. Use it as a screen, not a goal.
- **MER** (store revenue divided by total marketing spend) tracks the whole business better. It can't tell you which ad or ad set did the work, and it includes demand that would have come anyway.
- **iROAS** (incremental revenue divided by the spend that changed) comes from a test. It's the closest you get to "what did this spend add," at the spend level and conditions you tested.

## The formulas

```
margin before ad spend   = order value - discounts - product cost - shipping and fulfillment - payment fees - returns allowance
break-even ROAS          = 1 / (margin before ad spend as a share of revenue after discounts)
break-even CPA           = margin before ad spend in dollars, per first order
MER                      = store revenue / total marketing spend
break-even MER           = 1 / (whole-business margin before marketing as a share of revenue)
EBITDA break-even MER    = revenue / (margin before marketing in dollars - fixed costs in dollars)
target iROAS             = good-month MER - return credited to always-on demand and seasonality
iROAS                    = incremental revenue / spend that differed between the test cells
```

"Margin before ad spend" is what's left after variable costs and before any ad or marketing spend. It isn't called gross margin here on purpose, because sources label it differently. Platform-reported revenue may include tax or shipping, so check it.

If the margin is zero or negative, no ROAS breaks even and the calculator says `undefined` instead of printing a number.

Break-even is first-order only. Repeat purchases, LTV and payback sit outside it.

## Run it

Python 3.9 or newer, no installs.

**One order.** This is a made-up $60 order: $21 product cost, $9 shipping and fulfillment, $1.80 payment fees and a $3 returns allowance.

```bash
python roas_calc.py order --aov 60 --product-cost 21 --shipping 9 --fees 1.8 --returns 3 --roas 2.0
```

```
margin before ad spend: $25.20
margin share: 42.0%
break even roas: 2.38x
break even cpa: $25.20
roas checked: 2.00x
profit per order at roas: -$4.80
roas vs break even: below
```

A 2.0 ROAS on that order spends $30 to earn $25.20 of margin, so it loses $4.80 on every first order.

**The whole business.** Made-up month: $100,000 revenue, $30,000 marketing spend, 42% margin before marketing, $8,000 fixed costs.

```bash
python roas_calc.py mer --revenue 100000 --spend 30000 --margin-share 0.42 --fixed-costs 8000
```

```
mer: 3.33x
break even mer: 2.38x
ebitda break even mer: 2.94x
```

Break-even MER is the line where marketing has used up the margin before marketing. EBITDA break-even MER also covers fixed costs, so it sits higher.

**A test result.** Made-up test: $66,000 incremental revenue on $30,000 of spend, a good-month MER of 3.0x, and 0.8x credited to always-on demand and seasonality.

```bash
python roas_calc.py iroas --incremental-revenue 66000 --spend 30000 --good-month-mer 3.0 --baseline-credit 0.8 --break-even-roas 2.38
```

```
iroas: 2.20x
target iroas: 2.20x
iroas vs target: at
iroas vs break even roas: below
```

Add `--json` before the command name to get JSON instead of text.

## Setting a target iROAS

Look at blended MER over the last 12 to 24 months. From your P&Ls, pick the MERs for your worst, middling, good and best months, and start from the good months. Subtract the return you'd credit to always-on demand and seasonality, written as a multiple. You may not know it: it can be a guess, a number an MMM suggests, or 0 if you credit the whole business to paid advertising. What's left is the target iROAS.

The same target applies to every channel at every funnel stage. The only reason to set different targets is to adjust for what you can and can't measure.

Whether iROAS uses revenue or contribution margin should match the number your media buyers and budget owners already decide with. If you use contribution margin, the break-even line is 1.0x, not break-even ROAS.

## What to do with this

- **If a channel's platform ROAS is below break-even ROAS,** treat it as a flag, not a verdict. Platform ROAS can't see other platforms or whether the ad caused the sale, so test before you cut a channel on this alone.
- **If MER is close to or below break-even MER,** marketing is using up the margin before marketing. Look at the whole budget before you look at any one channel.
- **If MER clears break-even MER but not EBITDA break-even MER,** the ads cover their variable costs but the business still doesn't cover fixed costs at this spend.
- **If your target iROAS is below break-even ROAS,** a test that hits the target would still lose money on first orders. Revisit the target, the margin, or whether repeat purchases justify it.
- **If a test's iROAS clears the target,** that's the case for keeping spend, or adding it up to the level you tested. A test is a point in time, so retest when spend or season changes a lot.

If you want to know which of these numbers should drive your budget, send me a note and we'll talk it through: [Get in touch](https://brinkeranalytics.com/contact).

Lined the floor up and still not sure which number to manage the business to? [Can One Number Run Your Whole Business?](https://brinkeranalytics.com/guides/can-one-number-run-your-whole-business) walks the ladder. For many brands, EBITDA sits at the top of the ladder, and MER is a rung under it.

## Free reading on brinkeranalytics.com

- [Break-even ROAS, MER and iROAS calculator](https://brinkeranalytics.com/break-even-roas-calculator): the same math in the browser, including a margin lookup table.
- [Why your Meta, Google, GA4, Shopify, and finance numbers disagree](https://brinkeranalytics.com/insights/why-marketing-numbers-disagree)
- [When Meta, Google and others claim the same sales, which number decides spend?](https://brinkeranalytics.com/insights/when-platforms-claim-the-same-sales)
- [Marketing measurement glossary for DTC brands](https://brinkeranalytics.com/insights/measurement-glossary-dtc)
- [Incrementality testing framework for DTC brands: 7 steps](https://brinkeranalytics.com/insights/incrementality-testing-framework-dtc-brands)
- [Geo test power analysis: will your test see the lift?](https://brinkeranalytics.com/insights/geo-test-power-check)

## Files

```
roas_calc.py              the calculator (functions and a command-line tool)
tests/test_roas_calc.py   checks the formulas, the undefined cases and the README examples
```

Run the tests with `python -m unittest discover -s tests`.

## License

The code is MIT licensed (see `LICENSE`). The documentation, including this README, is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see `LICENSE-docs`). If you reuse it, please credit Eric Brinker at [Brinker Analytics](https://www.brinkeranalytics.com).
