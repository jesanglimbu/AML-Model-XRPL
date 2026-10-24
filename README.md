# AML-Model-XRPL

Our *Decode & Detect* entry: gives every payment on the synthetic XRPL ledger a suspicion
score from 0 to 1, groups the flagged payments into money trails, ranks them as alerts and
writes case reports. The code lives in [`xrpl-detector/`](xrpl-detector/README.md); team
handover notes are in [`TEAM_NOTES.md`](TEAM_NOTES.md).

## Reproduce the predictions CSV

Python 3.14 (tested on 3.14.8). Put the organisers' data in `decode-and-detect-training-data/`
and `decode-and-detect-test-data/` in this folder (or `data/train` and `data/test`), then:

```sh
python3 -m venv .venv
.venv/bin/pip install -r xrpl-detector/requirements.txt
.venv/bin/python xrpl-detector/train_model.py
.venv/bin/python xrpl-detector/run_pipeline.py
```

The upload file is `outputs/submission.csv` (`TRANSACTION_HASH,score`, one row per test payment).
The same run also writes the scoring variants we compared on the leaderboard, in the same format:
`outputs/submission_stage1.csv` (stage-1 model alone, 65.6), `outputs/submission_stage2.csv` (the
two-stage ranker alone, 65.4), `outputs/submission_blend.csv` (average rank of the two, 65.9) and
`outputs/submission_specialist.csv` (the blend mixed with a small medium-case specialist). The blend is
the default (`DEFAULT_SCORE` in `xrpl-detector/config.py`), so `submission.csv` ranks exactly like
`submission_blend.csv`.
Training takes about 20 minutes and the pipeline under a minute on a laptop CPU
(measured on an Apple M4, 16 GB). Results are deterministic (fixed seeds).

Tested with pandas 3.1.0, numpy 2.5.4, scikit-learn 1.9.1, scipy 1.18.1, pyarrow 26.0.0,
networkx 3.7, matplotlib 3.11.2 and joblib 1.6.0.

## Licence and credits

MIT, see [`LICENSE`](LICENSE). What we did not write ourselves is listed in
[`THIRD_PARTY.md`](THIRD_PARTY.md).
