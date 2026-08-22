import argparse
import json
import spacy
from filter_disruption_events import pull_with_themes, looks_relevant

nlp = spacy.load("en_core_web_sm")

EVENT_KEYWORDS = {
    "strike": "LABOR_STRIKE",
    "flood": "NATURAL_DISASTER",
    "fire": "NATURAL_DISASTER",
    "tariff": "TRADE_ACTION",
    "sanction": "TRADE_ACTION",
    "delay": "LOGISTICS_DELAY",
}

def infer_event_type(title: str) -> str:
    lower = title.lower()
    for kw, label in EVENT_KEYWORDS.items():
        if kw in lower:
            return label
    return "UNKNOWN"

def extract(article: dict) -> dict:
    doc = nlp(article.get("title", ""))
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    places = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return {
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "organizations": orgs,
        "locations": places,
        "event_type": infer_event_type(article.get("title", "")),
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="supply chain disruption")
    p.add_argument("--maxrecords", type=int, default=20)
    args = p.parse_args()
    articles = pull_with_themes(args.query, args.maxrecords)
    relevant = [a for a in articles if looks_relevant(a)]
    structured = [extract(a) for a in relevant]
    print(json.dumps(structured, indent=2))
    with open("sample_extracted_events.json", "w") as f:
        json.dump(structured, f, indent=2)
    print(f"\nSaved {len(structured)} structured events to sample_extracted_events.json")
