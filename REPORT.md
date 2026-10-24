# Decode & Detect: report

**Team:** Pookies of The Caribbean · **Captain:** Mohamed Mustafa Avoor · **Members:** Jesang Limbu, Hemayu Vikeekumar, Owen Leung, Mohamed Mustafa Avoor

**Submitted commit:** _TODO (record after the final change)_

Our tool gives every payment on the synthetic ledger a suspicion score from 0 to 1, groups the
most suspicious payments into money trails, ranks them as alerts, and writes a plain-English case
report for each one, citing the transaction hashes behind every claim.

**Best leaderboard score: 66.8** (100 × average precision). Of the 1% of payments we rank most
suspicious, 92% are labelled suspicious.

> **Important:** a flag is a reason to investigate, not evidence of a crime. This is an
> experimental prototype tested only on synthetic data. See [Limitations](#limitations).

## 1. Data sources

- **Only the organisers' synthetic dataset**: a fictional week of XRP, issued-currency and
  cross-currency payments, with labelled training data and unlabelled test data.
  Training: 40,131 payments, 1,250 suspicious (about 3%) from 169 planted scenarios.
  Test: 40,101 payments between 700 accounts.
- Payments are valued in US dollars with the organisers' hourly reference prices
  (`market_rates.csv`).
- **No external data, external labels, pre-trained models or outside services.** No LLM is called
  when the code runs.
- The dataset is not included in this repository. Download both packages from
  https://hackathon.ukcbt.org and unzip them into `decode-and-detect-training-data/` and
  `decode-and-detect-test-data/`.

## 2. Methodology

```
payments ──► score every payment ──► top 1% ──► group into trails ──► rank alerts ──► case reports
             aml_ranker/             trail_tracker.py   alert_ranker.py   case_writer.py
             (two-stage ranker       (10-min bursts)                      + trail_graph.py
              + mule network)
```

### What separates laundering from legitimate look-alikes

The legitimate data contains payments with **the same shapes** as the planted laundering
(fan-out, fan-in, chains, cycles), so shape alone gives many false alarms. Two signals worked:

1. **Speed.** Planted money moves fast: about 1 minute per hop, with easy scenarios finished in
   about 5 minutes, against about 60 minutes for legitimate look-alikes.
2. **New relationships.** Legitimate commerce repeats the same sender→receiver pairs. Planted
   flows almost always use a pair that has never paid before.

### Scoring (`xrpl-detector/aml_ranker/`)

- **About 220 features per payment**, computed from the split's own week: value and conversion
  legs, whether the sender→receiver pair is new, each account's weekly profile, bursts of
  activity from 1 minute to 2 days, money in just before and out just after, and **episodes**
  (an account's consecutive payments linked within 30 seconds to 1 day).
- **Stage 1:** gradient-boosting classifiers (scikit-learn `HistGradientBoostingClassifier`,
  3 seeds).
- **Stage 2:** adds how suspicious each payment's episode-mates look to stage 1, so a planted
  pattern lifts all of its payments together.
- **Blend:** the average rank of stage 1 and stage 2. Stage 2 is better on medium and hard
  cases and stage 1 on easy ones, so the blend beats both.
- **Final score: mule network signal** (`aml_ranker/mule.py`). Mules receive suspicious money and
  pass it on, so for each payment we take the highest blend score among the *other* payments
  touching the same sender or receiver within ±1 hour, and mix its rank into the blend at 20%.
  Payments in the same scheme pull each other up. It uses no labels and adds no training time.

### Alerts and case reports

- **Flag** the top 1% of scores (about 400 payments), matching the site's review budget.
- **Group** flagged payments linked within 10 minutes (chain, fan-out or fan-in) into one alert;
  lone flagged payments are not shown as alerts but keep their score in the submission.
- **Rank** alerts by 0.5 × average payment score + 0.3 × highest payment score + 0.2 × size.
- **Report** each top alert with a template (no LLM): the pattern (for example layering or
  split and recombine), who sent, passed on and collected the money, how fast intermediaries
  passed it on, the trail graph, every payment with its hash, and a glossary for non-specialists. A citation check confirms every
  transaction hash in a report belongs to that alert.

## 3. Evaluation

### Leaderboard (test data)

| Run | Score | Top-1% precision | Top-1% recall |
|---|---|---|---|
| Organisers' starter notebook | 33.5 | 62% | 20% |
| Single gradient-boosting model | 59.2 | 94% | 30% |
| Two-stage ranker | 65.4 | 91% | 29% |
| Stage 1 alone | 65.6 | 92% | – |
| Blend of stage 1 and stage 2 (Python 3.14, scikit-learn 1.9.1) | 65.9 | 91% | – |
| Blend of stage 1 and stage 2 (Python 3.9.6, scikit-learn 1.6.1) | 66.5 | – | – |
| **Blend + mule network signal (Python 3.9.6, scikit-learn 1.6.1; submitted)** | **66.8** | 92% | 30% |

The top 1% holds about 400 payments, so it can contain at most about 32% of the ~1,250
suspicious payments. 29–30% recall is close to that ceiling.

### Cross-validation (training data)

5 folds **grouped by scenario and by relay cohort**, so payments from one planted scenario (and
its look-alikes) never appear in both the training and the checking part. Without this the
scores would be unrealistically high.

| | Average precision × 100 |
|---|---|
| All | 55.4 |
| Easy cases (64% of suspicious payments) | 68.8 |
| Medium (18%) | 7.5 |
| Hard (18%) | 1.5 |

Recall by family at the F1-best threshold: strongest on cycle (85%), chain and fan-out-in (79%);
weakest on the relay families (aggregate relay 4%, distributed relay 0%).

**Mule network signal**, same folds (measured on Python 3.9 / scikit-learn 1.6.1, where the blend
scores 56.86): with the mule signal **57.75** (easy 75.0 → 75.6, medium 4.7 → 5.2, hard 1.1 → 1.2).
We tested windows of ±10 min, 30 min, 1 h, 2 h, 6 h and 1 day at weights of 5–40%, and applying the
signal repeatedly; ±1 h at 20% was best (30% within 0.02). On the leaderboard, from the same
machine: blend **66.5**, blend + mule **66.8** (+0.3).

### Alert quality

Measured on the training labels with out-of-fold scores, before the final model (comparing
grouping rules, not models):

| Grouping | Alerts | Alerts that are real cases | Alerts per real case | Purity |
|---|---|---|---|---|
| Top 1%, 3-minute bursts | 62 | 85% | 1.15 | 99% |
| **Top 1%, 10-minute bursts (used)** | 54 | 85% | **1.00** | 99% |
| Top 1%, 60-minute bursts | 21 | 95% | 1.00 | 85% |

With 10-minute bursts **no real case is split across alerts** and alerts almost never mix two
cases. Longer windows start merging different cases (purity falls).

## 4. Limitations

- **A flag is not proof.** About 8% of our top 1% are false positives. A score is a reason for a
  human to look, not a finding of money laundering or of any wrongdoing.
- **Synthetic data only.** Good performance here does not show the tool would detect real fraud
  or laundering. Real data would need new testing, and data-protection checks before use.
- **Medium and hard cases are mostly missed.** Medium cases are slow and resemble legitimate
  activity (AP 7.5). Each relay cohort hides one planted scenario among 99 legitimate ones that
  match it on every feature we tried, so relay recall is about 0%. 25 hard payments are labelled
  independently of anything observable, by design.
- **Lone payments are not alerted.** A highly scored payment with no linked flagged payment
  within 10 minutes keeps its score but does not appear as an alert or case report.
- **Results vary slightly between library versions** (cross-validation 55.4 with the tested
  versions in `README.md`, 57.1 on Python 3.9 with scikit-learn 1.6.1). Use the pinned versions
  to reproduce the submitted predictions exactly.
- **Possible bias:** the model favours fast, new-relationship activity. Legitimate businesses
  that genuinely work this way (new customers, fast settlement) are more likely to be flagged.
- **Not a compliance product.** This is an educational prototype. It is not certified, not legal
  or financial advice, and not validated against any regulatory requirement.

## 5. Reproducing the results

See [`README.md`](README.md) for the exact commands, Python and library versions and run times.
Training takes about 15–20 minutes on a laptop CPU and the pipeline under a minute. No GPU,
internet connection, paid service or API key is needed.

## 6. What we built and what we used

- **Our work** (built during the hacking period): everything in `xrpl-detector/`, this report and
  the slides.
- **Not ours:** the organisers' dataset, starter notebook and `payments.py`, and open-source
  libraries. Full list with licences in [`THIRD_PARTY.md`](THIRD_PARTY.md).
- **AI assistance:** Claude (Anthropic) via Claude Code helped write code and documentation,
  including this report. Prompts: [`chat-history/`](chat-history/README.md). No AI is used
  when the tool runs.
