"""
Cleaning steps for the two public app datasets used in the workbook.

Inputs (kept exactly as downloaded, in this folder):
  googleplaystore.csv   Google Play Store apps
  AppleStore.csv        Apple App Store apps

The workbook holds the raw rows on the Raw sheets and the result of these
steps on the Clean sheets. Every step is counted in the Cleaning_Log sheet.
"""
import re
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).parent


def load_raw():
    g = pd.read_csv(HERE / "googleplaystore.csv", dtype=str, keep_default_na=False)
    a = pd.read_csv(HERE / "AppleStore.csv")
    return g, a


def pretty_category(c):
    s = c.replace("_", " ").title()
    return s.replace(" And ", " and ")


def min_android(v):
    m = re.match(r"^\s*(\d+)\.(\d+)", v or "")
    return float(f"{m.group(1)}.{m.group(2)}") if m else np.nan


def size_mb(v):
    m = re.match(r"^([\d.]+)([Mk])$", v or "")
    if not m:
        return np.nan
    x = float(m.group(1))
    return x if m.group(2) == "M" else x / 1024


def clean_android(raw):
    log = []
    n0 = len(raw)
    g = raw.copy()

    bad = ~g["Installs"].str.match(r"^[\d,]+\+?$")
    log.append(("Android", "Row with shifted columns (category shows 1.9, installs missing)",
                "Removed the row", int(bad.sum())))
    g = g[~bad]

    d = int(g.duplicated().sum())
    log.append(("Android", "Rows that repeat another row exactly", "Kept one copy", d))
    g = g.drop_duplicates()

    g = g.assign(_rev=g["Reviews"].astype(int))
    order = g.sort_values(["_rev"], ascending=False, kind="stable")
    keep = order.drop_duplicates(subset=["App"]).index
    dn = int(len(g) - len(keep))
    log.append(("Android", "Same app listed more than once with different review counts",
                "Kept the row with the most reviews", dn))
    g = g.loc[sorted(keep)]

    out = pd.DataFrame({
        "app": g["App"],
        "category": g["Category"].map(pretty_category),
        "rating": pd.to_numeric(g["Rating"].replace({"NaN": ""}), errors="coerce"),
        "reviews": g["Reviews"].astype(int),
        "size_mb": g["Size"].map(size_mb),
        "installs": g["Installs"].str.replace(r"[+,]", "", regex=True).astype(int),
        "type": g["Type"].replace({"NaN": ""}),
        "price": g["Price"].str.replace("$", "", regex=False).astype(float),
        "content_rating": g["Content Rating"],
        "last_updated": pd.to_datetime(g["Last Updated"], format="%B %d, %Y"),
        "min_android": g["Android Ver"].map(min_android),
    })
    log.append(("Android", "Reviews stored as text", "Converted to numbers", int(len(out))))
    log.append(("Android", "Installs written like 10,000+", "Kept the lower bound as a number", int(len(out))))
    log.append(("Android", "Price written like $0.99", "Converted to a number", int((out["price"] > 0).sum())))
    in_k = int(g["Size"].str.endswith("k").sum())
    log.append(("Android", "Size given in k, as in 201k", "Converted to MB", in_k))
    var = int(out["size_mb"].isna().sum())
    log.append(("Android", "Size is Varies with device", "Left empty, ignored in size averages", var))
    log.append(("Android", "Last updated stored as text", "Converted to a real date", int(len(out))))
    mv = int(out["min_android"].isna().sum())
    log.append(("Android", "Android version written like 4.0.3 and up or 5.0 to 8.0",
                "Kept the lowest version as x.y, Varies left empty", mv))
    miss_t = int((out["type"] == "").sum() + (out["type"] == "0").sum())
    out["type"] = np.where(out["price"] > 0, "Paid", "Free")
    log.append(("Android", "Type missing or wrong", "Set from the price (0 is Free)", miss_t))
    nr = int(out["rating"].isna().sum())
    log.append(("Android", "Apps with no rating", "Left empty, ignored in rating averages", nr))
    return out.reset_index(drop=True), log, n0


def clean_ios(raw):
    log = []
    n0 = len(raw)
    a = raw.copy()
    out = pd.DataFrame({
        "id": a["id"], "app": a["track_name"], "size_bytes": a["size_bytes"],
        "price": a["price"], "rating_count": a["rating_count_tot"],
        "rating": a["user_rating"], "age_rating": a["cont_rating"],
        "genre": a["prime_genre"], "supported_devices": a["sup_devices.num"],
        "languages": a["lang.num"], "ipad_screenshots": a["ipadSc_urls.num"],
    })
    unrated = (out["rating_count"] == 0)
    out.loc[unrated, "rating"] = np.nan
    log.append(("iOS", "Rating shown as 0 for apps with no ratings", "Left empty, ignored in rating averages",
                int(unrated.sum())))
    log.append(("iOS", "Columns not needed (currency, version, version ratings, licence flag)",
                "Left out of the Clean sheet", 5))
    dn = int(out["app"].duplicated().sum())
    log.append(("iOS", "Same app name with different IDs", "Kept both, the IDs are different apps", dn))
    return out, log, n0


CATEGORY_MAP = [
    # matched label, android category (clean), ios genre
    ("Games", "Game", "Games"),
    ("Education", "Education", "Education"),
    ("Entertainment", "Entertainment", "Entertainment"),
    ("Health and Fitness", "Health and Fitness", "Health & Fitness"),
    ("Social", "Social", "Social Networking"),
    ("Photo and Video", "Photography", "Photo & Video"),
    ("Productivity", "Productivity", "Productivity"),
    ("Lifestyle", "Lifestyle", "Lifestyle"),
    ("Shopping", "Shopping", "Shopping"),
    ("Sports", "Sports", "Sports"),
    ("Finance", "Finance", "Finance"),
    ("Travel", "Travel and Local", "Travel"),
    ("News", "News and Magazines", "News"),
    ("Business", "Business", "Business"),
    ("Medical", "Medical", "Medical"),
    ("Weather", "Weather", "Weather"),
    ("Food and Drink", "Food and Drink", "Food & Drink"),
    ("Navigation", "Maps and Navigation", "Navigation"),
]

if __name__ == "__main__":
    g, a = load_raw()
    ca, la, n_a = clean_android(g)
    ci, li, n_i = clean_ios(a)
    print(n_a, len(ca), n_i, len(ci))
    for row in la + li:
        print(row)
