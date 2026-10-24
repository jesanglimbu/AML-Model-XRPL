# What we did not write ourselves

- **Organiser material**: the dataset and the starter notebook, and the organisers' `payments.py`
  loader (not included in this repo). The ranker's amount decoding and hourly USD valuation
  (`xrpl-detector/aml_ranker/data.py`) follow `payments.py` and the organisers' README.
- **Libraries** (see `xrpl-detector/requirements.txt`): NumPy, pandas, PyArrow, scikit-learn
  (`HistGradientBoostingClassifier`, `StratifiedGroupKFold`, metrics), SciPy (`connected_components`),
  NetworkX, Matplotlib, joblib.
- **AI assistance**: parts of the code and documentation were written with Claude (Anthropic)
  via Claude Code. Owen's prompts and what they produced: [`OWEN_AI_PROMPTS.md`](OWEN_AI_PROMPTS.md).
- No pre-trained models, external data, external labels or outside services are used.
