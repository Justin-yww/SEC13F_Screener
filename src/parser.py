import xml.etree.ElementTree as ET
import pandas as pd

_NS = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"


def parse_infotable(xml_text: str) -> pd.DataFrame:
    root = ET.fromstring(xml_text)
    rows = []
    for entry in root.findall(f"{_NS}infoTable"):
        put_call = entry.findtext(f"{_NS}putCall", "").strip()
        if put_call:
            continue

        # sshPrnamt is nested inside shrsOrPrnAmt
        shrs_block = entry.find(f"{_NS}shrsOrPrnAmt")
        shares = 0
        if shrs_block is not None:
            shares = int(shrs_block.findtext(f"{_NS}sshPrnamt", "0") or "0")

        rows.append({
            "name":      entry.findtext(f"{_NS}nameOfIssuer", "").strip(),
            "cusip":     entry.findtext(f"{_NS}cusip", "").strip(),
            "value_usd": int(entry.findtext(f"{_NS}value", "0") or "0") * 1000,
            "shares":    shares,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    name_map = (
        df.sort_values("value_usd", ascending=False)
        .drop_duplicates("cusip")
        .set_index("cusip")["name"]
    )
    df = df.groupby("cusip", as_index=False)[["value_usd", "shares"]].sum()
    df["name"] = df["cusip"].map(name_map)
    return df
