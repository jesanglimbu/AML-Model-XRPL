# What we did not write ourselves

## Organiser material

- **Dataset**: the synthetic *Decode & Detect* training, validation and test data, supplied by the
  UK Centre for Blockchain Technologies for this event. It is not ours to redistribute: download it
  from https://hackathon.ukcbt.org (see `README.md` for where to put it).
- **Starter notebook and `payments.py` loader** (organiser code, not included in this repo). The
  ranker's amount decoding and hourly USD valuation (`xrpl-detector/aml_ranker/data.py`) follow
  `payments.py` and the organisers' README.

## Libraries

Installed from PyPI at the versions pinned in `xrpl-detector/requirements.txt` (Python 3.9.6).
Licences as declared in each package's metadata:

| Library | Pinned version | Licence | Used for |
|---|---|---|---|
| NumPy | 2.0.2 | BSD-3-Clause (bundled parts: 0BSD, MIT, Zlib, CC0-1.0) | arrays |
| pandas | 2.3.3 | BSD-3-Clause | tables |
| PyArrow | 21.0.0 | Apache-2.0 | reading Parquet |
| scikit-learn | 1.6.1 | BSD-3-Clause | `HistGradientBoostingClassifier`, `StratifiedGroupKFold`, metrics |
| SciPy | 1.13.1 | BSD-3-Clause | `connected_components` (payment episodes) |
| NetworkX | 3.2.1 | BSD-3-Clause | trail graphs |
| Matplotlib | 3.9.4 | Matplotlib License (PSF-based) | trail pictures |
| joblib | 1.5.3 | BSD-3-Clause | saving the model |

All are compatible with our MIT licence. We changed none of them.

## AI assistance

- **Model and provider:** Claude Opus 5.5 (`claude-opus-5-5`) by Anthropic, used through Claude Code
  (desktop app and terminal) with its default settings. Every commit it helped with carries a
  `Co-Authored-By: Claude Opus 5.5` line.
- **What it did:** helped write code, documentation and analysis; the team reviewed, ran and checked
  the results (cross-validation, leaderboard uploads, reproduction runs).
- **Prompts and outputs:** each team member's prompts and what they produced are in
  [`chat-history/`](chat-history/README.md).
- **Reproducibility:** the tool itself calls no AI service: predictions come only from the code and
  the data, with fixed seeds, so they reproduce exactly. Re-running the same prompts would not give
  identical AI output, because LLM responses vary between runs.

## Model weights

The trained model (`models/model.joblib`, tens of MB) is not in the code ZIP, which is limited to
8 MiB. It is fully reproducible: `python xrpl-detector/train_model.py` rebuilds the identical model
in about 25-30 minutes (fixed seeds, pinned library versions), and `README.md` has the exact commands.

## Not used

No pre-trained models, external data, external labels, test answers or outside services.
