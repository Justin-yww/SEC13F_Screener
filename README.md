# 13F Terminal
---
A lightweight institutional holdings tracker built on raw SEC EDGAR data: 
Select any institution by CIK, and the pipeline fetches their two most recent 13F filings, parses the infotable XML, resolves CUSIP codes to tickers via OpenFIGI, and computes share-level changes between quarters (surfacing the top 10 buys and sells in an interactive Streamlit dashboard).

--- 
**Data source:** SEC EDGAR (free, no API key required)  
**CUSIP resolution:** OpenFIGI (free tier, optional API key for higher rate limits)  
**Preset institutions:** Berkshire Hathaway · Khazanah Nasional · GIC · Temasek · Scion Asset Mgmt
