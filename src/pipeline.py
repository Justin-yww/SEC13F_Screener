import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from config import FILINGS_DIR, ENTITIES_PATH, CACHE_TTL_HOURS, TOP_N
from .edgar import get_recent_13f_filings, fetch_infotable_xml
from .parser import parse_infotable
from .cusip import resolve_cusips
from .delta import compute_delta


def _cache_is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < timedelta(hours=CACHE_TTL_HOURS)


def load_entities() -> list[dict]:
    return json.loads(ENTITIES_PATH.read_text())


def run(cik: str, force_refresh: bool = False) -> dict:
    cache_dir   = FILINGS_DIR / cik
    cache_dir.mkdir(parents=True, exist_ok=True)
    latest_path = cache_dir / "latest.json"
    prior_path  = cache_dir / "prior.json"
    meta_path   = cache_dir / "meta.json"

    use_cache = (
        not force_refresh
        and _cache_is_fresh(latest_path)
        and _cache_is_fresh(prior_path)
    )

    if use_cache:
        df_latest = pd.read_json(latest_path)
        df_prior  = pd.read_json(prior_path)
        meta      = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    else:
        filings = get_recent_13f_filings(cik, n=2)

        xml_latest = fetch_infotable_xml(filings[0])
        xml_prior  = fetch_infotable_xml(filings[1])

        df_latest = parse_infotable(xml_latest)
        df_prior  = parse_infotable(xml_prior)

        df_latest.to_json(latest_path)
        df_prior.to_json(prior_path)

        meta = {
            "accessions": [filings[0]["accession"], filings[1]["accession"]],
            "filing_dates": [filings[0]["filing_date"], filings[1]["filing_date"]],
            "fetched_at": datetime.now().isoformat(),
        }
        meta_path.write_text(json.dumps(meta, indent=2))

    all_cusips = list(set(df_latest["cusip"].tolist() + df_prior["cusip"].tolist()))
    ticker_map = resolve_cusips(all_cusips)

    for df in [df_latest, df_prior]:
        df["ticker"] = df["cusip"].map(ticker_map).fillna("")

    result = compute_delta(df_latest, df_prior, top_n=TOP_N)
    result["meta"] = meta
    return result
