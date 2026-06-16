import time
import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SEC_USER_AGENT,
    EDGAR_SUBMISSIONS_URL,
    EDGAR_ARCHIVE_URL,
    EDGAR_RATE_LIMIT_S,
)

_HEADERS = {"User-Agent": SEC_USER_AGENT}
_EFTS_URL = "https://efts.sec.gov/LATEST/search-index"


def get_recent_13f_filings(cik: str, n: int = 2) -> list[dict]:
    padded = cik.zfill(10)
    url = f"{EDGAR_SUBMISSIONS_URL}/CIK{padded}.json"
    time.sleep(EDGAR_RATE_LIMIT_S)
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    filings = data["filings"]["recent"]
    results = []
    for i, form in enumerate(filings["form"]):
        if form == "13F-HR":
            acc = filings["accessionNumber"][i]
            results.append({
                "accession":        acc,
                "accession_nodash": acc.replace("-", ""),
                "cik":              padded,
                "filing_date":      filings["filingDate"][i],
            })
            if len(results) == n:
                break

    if len(results) < n:
        raise ValueError(f"Only found {len(results)} 13F-HR filings for CIK {cik}, need {n}.")
    return results


def _get_infotable_filename(accession: str) -> str:
    """
    Uses EDGAR EFTS to find the information table document filename.
    Returns just the filename (e.g. '53405.xml' or 'form13f_infotable.xml').
    """
    time.sleep(EDGAR_RATE_LIMIT_S)
    resp = requests.get(
        _EFTS_URL,
        headers=_HEADERS,
        params={"q": f'"{accession}"', "forms": "13F-HR"},
        timeout=15,
    )
    resp.raise_for_status()
    hits = resp.json().get("hits", {}).get("hits", [])

    for hit in hits:
        source = hit.get("_source", {})
        if source.get("file_type") == "INFORMATION TABLE":
            doc_id = hit.get("_id", "")
            if ":" in doc_id:
                return doc_id.split(":", 1)[1]

    raise ValueError(
        f"No INFORMATION TABLE found in EFTS for accession {accession}. "
        f"Hits: {[h.get('_id') for h in hits]}"
    )


def fetch_infotable_xml(filing: dict) -> str:
    """
    Fetches the infotable XML. Uses the institution's own CIK for the
    archive path, then falls back to the accession-prefix CIK if that 404s.
    """
    accession     = filing["accession"]
    acc_nodash    = filing["accession_nodash"]
    institution_cik = filing["cik"]
    accession_cik   = acc_nodash[:10].zfill(10)

    filename = _get_infotable_filename(accession)

    # Try institution CIK first, then accession-prefix CIK as fallback
    for cik_to_try in [institution_cik, accession_cik]:
        xml_url = f"{EDGAR_ARCHIVE_URL}/{int(cik_to_try)}/{acc_nodash}/{filename}"
        time.sleep(EDGAR_RATE_LIMIT_S)
        resp = requests.get(xml_url, headers=_HEADERS, timeout=20)
        if resp.status_code == 200:
            return resp.text

    raise ValueError(
        f"Could not download infotable for {accession}. "
        f"Tried CIKs: {institution_cik}, {accession_cik}. "
        f"Filename: {filename}"
    )
