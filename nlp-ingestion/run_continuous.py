import time
from seen_articles import load_seen, save_seen
from filter_disruption_events import pull_with_themes, looks_relevant
from extract_entities import extract
from match_entities_to_graph import fetch_all_node_names
from match_with_aliases import match_entity_with_alias as match_entity
from neo4j import GraphDatabase
import requests
from tone_severity import refine_risk_with_tone

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
API_BASE = "http://localhost:8000"

POLL_SECONDS = 30  # lower this for local testing

RISK_BY_EVENT_TYPE = {
    "LABOR_STRIKE": "high", "NATURAL_DISASTER": "high",
    "TRADE_ACTION": "medium", "LOGISTICS_DELAY": "medium", "UNKNOWN": "low",
}

def run_once(seen, node_names, name_to_id):
    articles = pull_with_themes("supply chain disruption", 20)
    new_articles = [a for a in articles if a.get("url") not in seen and looks_relevant(a)]
    for article in new_articles:
        event = extract(article)
        base_risk = RISK_BY_EVENT_TYPE.get(event["event_type"], "low")
        tone = float(article.get("tone", 0) or 0)
        risk = refine_risk_with_tone(base_risk, tone)
        for entity in event["organizations"] + event["locations"]:
            m = match_entity(entity, node_names)
            if m and (node_id := name_to_id.get(m["matched_node"])):
                source_label = f"{article.get('domain', 'unknown')}: {event['title'][:80]}"
                requests.patch(
                    f"{API_BASE}/node/{node_id}/risk",
                    json={"risk": risk, "source": source_label},
                )
                print(f"[update] {m['matched_node']} -> {risk} (via {article.get('url')})")
        seen.add(article.get("url"))
    return seen

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        node_names = session.execute_read(fetch_all_node_names)
        name_to_id_result = session.run(
            "MATCH (n) WHERE n.name IS NOT NULL RETURN n.name AS name, n.id AS id"
        )
        name_to_id = {r["name"]: r["id"] for r in name_to_id_result}
    driver.close()
    
    seen = load_seen()
    print(f"Starting continuous polling every {POLL_SECONDS}s. Ctrl+C to stop.")
    try:
        while True:
            seen = run_once(seen, node_names, name_to_id)
            save_seen(seen)
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("Stopped.")
