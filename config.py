"""
Configuration for the 13F Terminal app.

"""
import os 
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root 
_ROOT = Path(__file__).parent
load_dotenv(Path(_ROOT, '.env'))

# SEC EDGAR credentials
# NOTE: SEC requires a valid name and email for each request so do update in the .env file
SEC_USER_NAME: str  = os.environ["SEC_USER_NAME"]
SEC_USER_EMAIL: str = os.environ["SEC_USER_EMAIL"]
SEC_USER_AGENT: str = f"{SEC_USER_NAME} {SEC_USER_EMAIL}"

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions"
EDGAR_ARCHIVE_URL     = "https://www.sec.gov/Archives/edgar"
EDGAR_RATE_LIMIT_S    = 0.12   # 10 req/s max → sleep 120ms between calls

# OpenFIGI API 
# NOTE: OpenFIGI requires a valid API key so do update in the .env file
OPENFIGI_API_KEY: str = os.environ["OPENFIGI_API_KEY"]
OPENFIGI_BASE_URL: str = "https://api.openfigi.com/v1"
OPENFIGI_RATE_LIMIT_S = 0.12   # 10 req/s max → sleep 120ms between calls

# Cache configuration
CACHE_DIR        = _ROOT / "data" / "cache"
FILINGS_DIR      = CACHE_DIR / "filings"
CUSIP_CACHE_PATH = CACHE_DIR / "cusip_ticker.json"
ENTITIES_PATH    = _ROOT / "data" / "entities.json"
CACHE_TTL_HOURS  = int(os.getenv("CACHE_TTL_HOURS", "6"))

# Dashboard Defaults
DEFAULT_CIK      = os.getenv("DEFAULT_CIK", "0001600177") # EPF's CIK is used as the default institution
TOP_N            = 10 # The number of top buys and sells to display in the dashboard



