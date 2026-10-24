"""Shared settings. Change thresholds HERE so everyone uses the same numbers."""
import os

# ---- Paths --------------------------------------------------------------
# HERE = the xrpl-detector folder (where this file lives)
# ROOT = the repo root, one level up (Decode&Detect)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _first_existing(*folders):
    """Return the first folder that exists, so the same config works on every laptop."""
    return next((f for f in folders if os.path.isdir(f)), folders[0])


# Looks inside xrpl-detector first, then the repo root, then data/train|test
TRAIN_DIR = _first_existing(f"{HERE}/decode-and-detect-training-data/train",
                            f"{ROOT}/decode-and-detect-training-data/train",
                            f"{HERE}/data/train")
TEST_DIR = _first_existing(f"{HERE}/decode-and-detect-test-data",
                           f"{ROOT}/decode-and-detect-test-data",
                           f"{HERE}/data/test")

OUT_DIR = f"{HERE}/outputs"
MODEL_PATH = f"{HERE}/models/model.joblib"

PREDICTIONS_CSV = f"{OUT_DIR}/predictions.csv"
SUBMISSION_CSV = f"{OUT_DIR}/submission.csv"   # SUBMISSION: one row per transaction
# One leaderboard file per model variant (predict.write_submissions)
SUBMISSION_VARIANTS = {
    "stage1": f"{OUT_DIR}/submission_stage1.csv",
    "stage2": f"{OUT_DIR}/submission_stage2.csv",
    "blend": f"{OUT_DIR}/submission_blend.csv",
}
ALERTS_JSON = f"{OUT_DIR}/alerts.json"           # trail_tracker.py -> alert_ranker.py
RANKED_JSON = f"{OUT_DIR}/ranked_alerts.json"    # alert_ranker.py  -> case_writer.py
SUMMARIES_JSON = f"{OUT_DIR}/summaries.json"
SUMMARIES_MD = f"{OUT_DIR}/summaries.md"
GRAPH_DIR = f"{OUT_DIR}/graphs"

# The provided dataset is synthetic, so its hashes don't exist on the real ledger.
# Leave EXPLORER_TX empty for the dataset; set it for live mainnet data.
EXPLORER_TX = ""             # e.g. "https://livenet.xrpl.org/transactions/"

# ---- Live-data option (only if you fetch real XRPL data) ----------------
XRPL_RPC = os.environ.get("XRPL_RPC", "https://xrplcluster.com/")
N_LEDGERS = 1000
EXCHANGE_MIN_TAGS = 20

# ---- Trail tracker ------------------------------------------------------
# Which burst grouping defines an alert ("b3m" = payments linked within 3 min)
BURST_LEVEL = "b10m"
MIN_ALERT_TXS = 2            # an alert needs at least this many flagged payments

# ---- Case writer --------------------------------------------------------
TOP_N_SUMMARIES = 5
