"""Runs everything after training:  predictions -> trails -> ranking -> pictures -> summaries

    python train_model.py              # once (and after any change to features.py)
    python run_pipeline.py             # on data/test
    python run_pipeline.py data/train  # on the training data (demo / debugging)
"""
import json
import os
import sys

import alert_ranker
import case_writer
import config
import predict
import schemas
import trail_graph
import trail_tracker

folder = sys.argv[1] if len(sys.argv) > 1 else config.TEST_DIR
folder = {"train": config.TRAIN_DIR, "data/train": config.TRAIN_DIR,
          "test": config.TEST_DIR, "data/test": config.TEST_DIR}.get(folder, folder)
os.makedirs(config.OUT_DIR, exist_ok=True)

print(f"1/5 scoring transactions in {folder}...")
pred = predict.predict(folder)
pred.drop(columns=["time"]).to_csv(config.PREDICTIONS_CSV, index=False)
print(f"    {len(pred)} scored, {pred['is_suspicious'].sum()} flagged")
if folder == config.TEST_DIR:
    submission = pred[["hash", "probability"]].rename(columns={"hash": "TRANSACTION_HASH", "probability": "score"})
    submission.to_csv(config.SUBMISSION_CSV, index=False)
    print(f"    upload file -> {config.SUBMISSION_CSV}")
    predict.write_submissions(pred)

print("2/5 grouping flagged payments into trails...")
alerts = trail_tracker.find_trails(pred)
json.dump(alerts, open(config.ALERTS_JSON, "w"), indent=2)
print(f"    {len(alerts)} alerts")

print("3/5 ranking alerts...")
ranked = alert_ranker.rank(alerts, pred)
json.dump(ranked, open(config.RANKED_JSON, "w"), indent=2)

print("4/5 drawing top trails...")
for a in ranked[:config.TOP_N_SUMMARIES]:
    trail_graph.draw_trail(a)

print("5/5 writing case summaries...")
case_writer.save(case_writer.write(ranked))

print("\nTop alerts:")
for a in ranked[:5]:
    print(f"  {a['alert_id']}  risk {a['risk_score']:.2f}  {len(a['tx_hashes'])} payments  "
          f"{a['minutes_total']} min  -> {a['reasons'][0]}")
if folder == config.TEST_DIR:
    print(f"\nUpload: {config.SUBMISSION_CSV}")
print(f"All predictions: {config.PREDICTIONS_CSV}   Report: {config.SUMMARIES_MD}   Pictures: {config.GRAPH_DIR}/")
print("\nFormat check:")
schemas.validate_all()
