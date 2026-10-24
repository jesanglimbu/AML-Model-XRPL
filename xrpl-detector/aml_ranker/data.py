"""Load one data split into a flat, one-row-per-transaction frame.

Each row is the effective customer edge (ACCOUNT -> Destination) of a payment,
valued in reference USD using the hourly market rates. Liquidity-provider legs
from transfers.parquet are only used for the actual source cost and leg count.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

XRP = "XRP"


def _asset_and_units(wire):
    """Decode an XRPL amount (drops string or IOU object) to (asset, units)."""
    if isinstance(wire, str):
        return XRP, int(wire) / 1_000_000
    return f"{wire['issuer']}:{wire['currency']}", float(wire["value"])


def _load_rates(directory):
    rates = pd.read_csv(directory / "market_rates.csv")
    return {(int(t), a): p / 1_000_000 for t, a, p in rates.itertuples(index=False)}


def _usd(rates, timestamps, assets, units):
    return np.array([u * rates[(t // 3600 * 3600, a)] for t, a, u in zip(timestamps, assets, units)])


def load_split(directory):
    directory = Path(directory)
    rates = _load_rates(directory)
    tx = pd.read_parquet(directory / "transactions.parquet")
    transfers = pd.read_parquet(directory / "transfers.parquet")

    fields = tx.EXTRA_TRANSACTION_FIELDS.map(json.loads)
    delivered = tx.DELIVERED_AMOUNT.map(lambda s: _asset_and_units(json.loads(s)))
    df = pd.DataFrame({
        "TRANSACTION_HASH": tx.TRANSACTION_HASH.to_numpy(),
        "t": tx.TIMESTAMP.astype(np.int64).to_numpy(),
        "sender": tx.ACCOUNT.to_numpy(),
        "receiver": fields.map(lambda f: f["Destination"]).to_numpy(),
        "dst_asset": delivered.str[0].to_numpy(),
        "dst_units": delivered.str[1].to_numpy(),
        "fee": tx.SOURCE_FEE.astype(int).to_numpy(),
        "ledger_pos": tx.TRANSACTION_INDEX.astype(int).to_numpy(),
    })
    df["usd"] = _usd(rates, df.t, df.dst_asset, df.dst_units)

    # SendMax is only a ceiling; it is kept to measure the slack the sender allowed.
    sendmax = fields.map(lambda f: _asset_and_units(f["SendMax"]) if "SendMax" in f else (None, np.nan))
    df["has_sendmax"] = sendmax.str[0].notna().to_numpy()
    sm_asset = sendmax.str[0].fillna(XRP).to_numpy()
    df["sendmax_usd"] = np.where(df.has_sendmax, _usd(rates, df.t, sm_asset, sendmax.str[1].fillna(0)), np.nan)

    # The first executed leg is the actual source debit.
    transfers = transfers.assign(idx=transfers.TRANSFER_INDEX.astype(int))
    legs = transfers.groupby("TRANSACTION_HASH").size()
    first = transfers[transfers.idx == 0].set_index("TRANSACTION_HASH")
    first_asset = np.where(first.SYMBOL == XRP, XRP, first.TOKEN_ADDRESS + ":" + first.SYMBOL)
    first_cost = pd.Series(_usd(rates, first.TIMESTAMP.astype(np.int64), first_asset, first.VALUE), first.index)
    df["n_legs"] = df.TRANSACTION_HASH.map(legs).to_numpy()
    df["src_asset"] = df.TRANSACTION_HASH.map(pd.Series(first_asset, first.index)).to_numpy()
    df["cost_usd"] = df.TRANSACTION_HASH.map(first_cost).to_numpy()

    return df.sort_values(["t", "ledger_pos", "TRANSACTION_HASH"]).reset_index(drop=True)


def load_labels(directory):
    return pd.read_csv(Path(directory) / "labels.csv")
