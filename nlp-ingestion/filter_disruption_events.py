import argparse
import requests

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
# A starter list — expand this as you learn which themes actually show up in relevant articles.
RELEVANT_THEMES = [
"STRIKE", "PORT", "SUPPLY_CHAIN", "NATURAL_DISASTER", "TRADE_DISPUTE", "SANCTIONS", "FIRE", "TARIFF"
]

def pull_with_themes(query, max_records=20):
    params = {
    "query": query, "mode": "artlist", "maxrecords": max_records,
    "format": "json", "sort": "hybridrel",
    }
    r = requests.get(GDELT_DOC_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("articles", [])

def looks_relevant(article):
    text = (article.get("title", "") + " " + article.get("domain", "")).upper()
    return any(theme.replace("_", " ") in text or theme in text for theme in RELEVANT_THEMES)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="supply chain disruption")
    p.add_argument("--maxrecords", type=int, default=20)
    args = p.parse_args()
    articles = pull_with_themes(args.query, args.maxrecords)
    relevant = [a for a in articles if looks_relevant(a)]
    print(f"Pulled {len(articles)} articles, {len(relevant)} look disruption-relevant:\n")
    for a in relevant:
        print(f"- [{a.get('domain','')}] {a.get('title','')}")
        print(f" url={a.get('url','')}\n")
