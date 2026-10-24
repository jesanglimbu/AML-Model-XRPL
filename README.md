# AML-Model-XRPL

Our *Decode & Detect* entry: gives every payment on the synthetic XRPL ledger a suspicion
score from 0 to 1, groups the flagged payments into money trails, ranks them as alerts and
writes case reports. The code lives in [`xrpl-detector/`](xrpl-detector/README.md); team
handover notes are in [`TEAM_NOTES.md`](TEAM_NOTES.md).

## Reproduce the predictions CSV

**Python 3.9.6** with the exact library versions pinned in `xrpl-detector/requirements.txt`
(pandas 2.3.3, numpy 2.0.2, scikit-learn 1.6.1, scipy 1.13.1, pyarrow 21.0.0, networkx 3.2.1,
matplotlib 3.9.4, joblib 1.5.3). Use these versions to reproduce the submitted file exactly: the
same code with newer versions (Python 3.14, scikit-learn 1.9.1) gives slightly different scores
(blend 65.9 instead of 66.5 on the leaderboard).

Put the organisers' data in `decode-and-detect-training-data/` and `decode-and-detect-test-data/`
in this folder (or `data/train` and `data/test`), then:

```sh
python3.9 -m venv .venv
.venv/bin/pip install -r xrpl-detector/requirements.txt
.venv/bin/python xrpl-detector/train_model.py
.venv/bin/python xrpl-detector/run_pipeline.py
```

The upload file is `outputs/submission.csv` (`TRANSACTION_HASH,score`, one row per test payment).
It is the **mule network score with the relay look-alike penalty** (`DEFAULT_SCORE = "mule_relay"` in
`xrpl-detector/config.py`), which scored **67.0** on the leaderboard. The same run also writes the
other variants we compared, in the same format: `submission_stage1.csv` (65.6),
`submission_stage2.csv` (65.4), `submission_blend.csv` (65.9 / 66.5, see above),
`submission_specialist.csv`, `submission_mule.csv` (66.8) and `submission_mule_relay.csv` (= `submission.csv`).

Training takes about 25-30 minutes and the pipeline about a minute on a laptop CPU (measured on an
Apple Silicon MacBook). Results are deterministic (fixed seeds).

## Licence and credits

MIT, see [`LICENSE`](LICENSE). What we did not write ourselves is listed in
[`THIRD_PARTY.md`](THIRD_PARTY.md).
