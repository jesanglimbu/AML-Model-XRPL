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

PREDICTIONS_CSV = f"{OUT_DIR}/predictions.csv"   # SUBMISSION: one row per transaction
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

# Trail tracker: which burst grouping defines an alert ("b3m" = payments linked within 3 min)
BURST_LEVEL = "b3m"
MIN_ALERT_TXS = 2            # an alert needs at least this many flagged payments

TOP_N_SUMMARIES = 5
