import argparse, requests

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

def pull_articles(query, max_records=10):
    params = {"query": query, "mode": "artlist", "maxrecords": max_records,
              "format": "json", "sort": "hybridrel"}
    r = requests.get(GDELT_DOC_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("articles", [])

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="port strike")
    p.add_argument("--maxrecords", type=int, default=10)
    args = p.parse_args()
    articles = pull_articles(args.query, args.maxrecords)
    for a in articles:
        print(f"- [{a.get('domain','')}] {a.get('title','')}")
        print(f"  tone={a.get('tone','n/a')} url={a.get('url','')}\n")
