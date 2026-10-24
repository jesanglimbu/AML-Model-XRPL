"""Shared settings. Change thresholds HERE so everyone uses the same numbers."""
import os

TRAIN_DIR = "data/train"     # transactions.parquet, transfers.parquet, market_rates.csv, labels.csv
TEST_DIR = "data/test"       # same files, no labels
OUT_DIR = "outputs"
MODEL_PATH = "models/model.joblib"

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
