"""Shared settings. Change thresholds HERE so everyone uses the same numbers."""
import os

# Paths are relative to the repo, so scripts work whichever folder you run them from.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _first_existing(*folders):
    return next((f for f in folders if os.path.isdir(f)), folders[0])


# Uses data/train and data/test if you made them, otherwise the organisers' folders in the repo.
TRAIN_DIR = _first_existing(f"{ROOT}/data/train", f"{ROOT}/decode-and-detect-training-data/train")
TEST_DIR = _first_existing(f"{ROOT}/data/test", f"{ROOT}/decode-and-detect-test-data")
OUT_DIR = f"{ROOT}/outputs"
MODEL_PATH = f"{ROOT}/models/model.joblib"

PREDICTIONS_CSV = f"{OUT_DIR}/predictions.csv"   # one row per transaction, with every feature
SUBMISSION_CSV = f"{OUT_DIR}/submission.csv"     # UPLOAD THIS: TRANSACTION_HASH,score (test data only)
SUBMISSION_VARIANTS = {                           # same format, one per scoring variant (test data only)
    "stage1": f"{OUT_DIR}/submission_stage1.csv",   # stage-1 model alone
    "stage2": f"{OUT_DIR}/submission_stage2.csv",   # two-stage ranker alone
    "blend": f"{OUT_DIR}/submission_blend.csv",     # average rank of the two
    "specialist": f"{OUT_DIR}/submission_specialist.csv",  # blend + 5% medium specialist
    "mule": f"{OUT_DIR}/submission_mule.csv",              # blend + 20% mule network signal (aml_ranker/mule.py)
}
DEFAULT_SCORE = "mule"       # which variant becomes `probability` and submission.csv
ALERTS_JSON = f"{OUT_DIR}/alerts.json"           # trail_tracker.py -> alert_ranker.py
RANKED_JSON = f"{OUT_DIR}/ranked_alerts.json"    # alert_ranker.py  -> case_writer.py
SUMMARIES_JSON = f"{OUT_DIR}/summaries.json"
SUMMARIES_MD = f"{OUT_DIR}/summaries.md"
GRAPH_DIR = f"{OUT_DIR}/graphs"

# The provided dataset is synthetic, so its hashes don't exist on the real ledger.
# Leave EXPLORER_TX empty for the dataset; set it for live mainnet data.
EXPLORER_TX = ""             # e.g. "https://livenet.xrpl.org/transactions/"

# Live-data option (fetch_data.py)
XRPL_RPC = os.environ.get("XRPL_RPC", "https://xrplcluster.com/")
N_LEDGERS = 1000
EXCHANGE_MIN_TAGS = 20

# Trail tracker: which payments are flagged, and which burst grouping defines an alert.
# Top 1% + 10-min bursts tested best on train labels: no case split across alerts, 99% purity.
FLAG_TOP_SHARE = 0.01        # flag the highest-scored 1% of payments (the site's review budget)
BURST_LEVEL = "b10m"         # payments linked by chain / fan-out / fan-in within 10 min
MIN_ALERT_TXS = 2            # an alert needs at least this many flagged payments

TOP_N_SUMMARIES = 5
