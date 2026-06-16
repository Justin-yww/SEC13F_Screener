""" 
Computes share and value changes between two quarters of 13F filings
"""

import pandas as pd


def _classify(row: pd.Series) -> str:
    if row["shares_prior"] == 0 and row["shares"] > 0:
        return "New position"
    if row["shares"] == 0 and row["shares_prior"] > 0:
        return "Closed position"
    if row["share_delta"] > 0:
        return "Added"
    if row["share_delta"] < 0:
        return "Reduced"
    return "Unchanged"


def compute_delta(
    df_current: pd.DataFrame,
    df_prior: pd.DataFrame,
    top_n: int = 10,
) -> dict:
      # Merges current and prior holdings on CUSIP and computes changes.
      """
      top_buys    = top_n rows with largest positive share_delta
      top_sells   = top_n rows with largest negative share_delta
      all_changes = full merged DataFrame sorted by share_delta descending
      """
      merged = df_current.merge(
            df_prior[["cusip", "shares", "value_usd"]].rename(
                  columns={"shares": "shares_prior", "value_usd": "value_prior"}
            ),
            on="cusip",
            how="outer",
      ).fillna(0)

      merged["share_delta"] = merged["shares"] - merged["shares_prior"]
      merged["value_delta"] = merged["value_usd"] - merged["value_prior"]
      merged["action"]      = merged.apply(_classify, axis=1)
      merged = merged.sort_values("share_delta", ascending=False)

      buys  = merged[merged["share_delta"] > 0].head(top_n)
      sells = merged[merged["share_delta"] < 0].tail(top_n).sort_values("share_delta")

      return {
            "top_buys":   buys,
            "top_sells":  sells,
            "all_changes": merged,
      }
