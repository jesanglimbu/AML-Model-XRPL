# What we did not write ourselves

<<<<<<< HEAD
- **Organiser material**: `payments.py` (the organisers' loader, copied unchanged), the starter
  notebook and the dataset in `decode-and-detect-*`. The ranker's amount decoding and hourly USD
  valuation (`xrpl-detector/aml_ranker/data.py`) follow `payments.py` and the organisers' README.
=======
- **Organiser material**: the dataset and the starter notebook, and the organisers' `payments.py`
  loader (not included in this repo). The ranker's amount decoding and hourly USD valuation
  (`xrpl-detector/aml_ranker/data.py`) follow `payments.py` and the organisers' README.
>>>>>>> 562c84ea58325bf504343922fb5ef977c8606a69
- **Libraries** (see `xrpl-detector/requirements.txt`): NumPy, pandas, PyArrow, scikit-learn
  (`HistGradientBoostingClassifier`, `StratifiedGroupKFold`, metrics), SciPy (`connected_components`),
  NetworkX, Matplotlib, joblib.
- **AI assistance**: parts of the code and documentation were written with Claude (Anthropic)
<<<<<<< HEAD
  via Claude Code.
=======
  via Claude Code. Each team member's prompts and what they produced: [`chat-history/`](chat-history/README.md).
>>>>>>> 562c84ea58325bf504343922fb5ef977c8606a69
- No pre-trained models, external data, external labels or outside services are used.
