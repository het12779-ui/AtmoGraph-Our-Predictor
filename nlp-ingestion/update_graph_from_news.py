import json
from neo4j import GraphDatabase
from filter_disruption_events import pull_with_themes, looks_relevant
from extract_entities import extract
from match_entities_to_graph import fetch_all_node_names, match_entity

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
RISK_BY_EVENT_TYPE = {
    "LABOR_STRIKE": "high", "NATURAL_DISASTER": "high",
    "TRADE_ACTION": "medium", "LOGISTICS_DELAY": "medium", "UNKNOWN": "low",
}

def set_node_risk(tx, node_name, risk):
    tx.run("MATCH (n {name: $name}) SET n.risk = $risk", name=node_name, risk=risk)

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        node_names = session.execute_read(fetch_all_node_names)
    
    articles = pull_with_themes("supply chain disruption", 20)
    relevant = [a for a in articles if looks_relevant(a)]
    
    updates = []
    with driver.session() as session:
        for article in relevant:
            event = extract(article)
            risk = RISK_BY_EVENT_TYPE.get(event["event_type"], "low")
            for entity in event["organizations"] + event["locations"]:
                m = match_entity(entity, node_names)
                if m:
                    session.execute_write(set_node_risk, m["matched_node"], risk)
                    updates.append({"node": m["matched_node"], "risk": risk,
                                    "source_title": event["title"]})
    
    driver.close()
    
    print(json.dumps(updates, indent=2))
    print(f"\nUpdated risk on {len(updates)} node(s) from real news events.")
