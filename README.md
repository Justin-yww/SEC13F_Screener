# 13F Terminal

A lightweight institutional holdings tracker built on raw SEC EDGAR data.

Enter any institution's CIK and the pipeline fetches their two most recent 13F-HR filings, parses the infotable XML, resolves CUSIP codes to tickers via OpenFIGI, and computes share-level changes between quarters — surfacing the top 10 buys and sells in an interactive Streamlit dashboard.

---

**Data source:** SEC EDGAR (free, no API key required)  
**CUSIP resolution:** OpenFIGI (free tier, optional API key for higher rate limits)  
**Stack:**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

---

## Quick start

```bash
git clone https://github.com/Justin-yww/13f-terminal
cd 13f-terminal
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your name and email for SEC User-Agent
streamlit run app.py
```

## How it works

1. Enter a 10-digit CIK (find any institution at [sec.gov](https://www.sec.gov/cgi-bin/browse-edgar))
2. The pipeline fetches the two most recent 13F-HR filings from EDGAR
3. CUSIP codes are resolved to tickers via OpenFIGI and cached locally
4. Share deltas between quarters are computed and ranked
5. Top 10 buys and sells render in the dashboard alongside the full position table