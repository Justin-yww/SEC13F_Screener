"""
EDGAR API setup for API calls to the SEC EDGAR database
"""

import time 
import requests

from config import (
      SEC_USER_AGENT,
      EDGAR_SUBMISSIONS_URL,
      EDGAR_ARCHIVE_URL,
      EDGAR_RATE_LIMIT_S
) 

_HEADERS = {"User-Agent": SEC_USER_AGENT}

def get_recent_13f_accessions(cik: str, n: int = 2) -> list[str]:
      # Used to return the most recent 13F accessions for a given CIK
      padded = cik.zfill(10)
      url = f"{EDGAR_SUBMISSIONS_URL}/CIK{padded}.json"
      resp = requests.get(url, headers=_HEADERS, timeout=15)
      resp.raise_for_status()
      data = resp.json()

      filings = data["filings"]["recent"]
      accessions = []
      for i, form in enumerate(filings["form"]):
            if form == "13F-HR":
                  accession = filings["accessionNumber"][i].replace("-", "")
                  accessions.append(accession)
                  if len(accessions) == n:
                        break

      if len(accessions) < n:
            raise ValueError(
                  f"Only found {len(accessions)} 13F-HR filings for CIK {cik} "
                  f"(need {n} to compute delta)."
            )
      return accessions

def fetch_infotable_xml(cik: str, accession: str) -> str:
    # Downloads the raw infotable XML for a given CIK + accession number.
    # Accounts for sleeping before the request to stay within EDGAR_RATE_LIMIT_S 

    padded = cik.zfill(10)
    # EDGAR archive path: accession without dashes, in subdirectory
    acc_nodash = accession.replace("-", "")
    acc_dashes = f"{acc_nodash[:10]}-{acc_nodash[10:12]}-{acc_nodash[12:]}"
    url = f"{EDGAR_ARCHIVE_URL}/{padded}/{acc_nodash}/infotable.xml"

    time.sleep(EDGAR_RATE_LIMIT_S)
    resp = requests.get(url, headers=_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text
