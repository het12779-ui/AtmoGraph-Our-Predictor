import requests
from filter_disruption_events import pull_with_themes, looks_relevant
from extract_entities import extract
from match_entities_to_graph import fetch_all_node_names
from match_with_aliases import match_entity_with_alias as match_entity
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
API_BASE = "http://localhost:8000"

RISK_BY_EVENT_TYPE = {
   "LABOR_STRIKE": "high", "NATURAL_DISASTER": "high",
   "TRADE_ACTION": "medium", "LOGISTICS_DELAY": "medium", "UNKNOWN": "low",
}

def fetch_name_to_id(tx):
   result = tx.run("MATCH (n) WHERE n.name IS NOT NULL RETURN n.name AS name, n.id AS id")
   return {r["name"]: r["id"] for r in result}

if __name__ == "__main__":
   driver = GraphDatabase.driver(URI, auth=AUTH)
   with driver.session() as session:
       node_names = session.execute_read(fetch_all_node_names)
       name_to_id = session.execute_read(fetch_name_to_id)
   driver.close()

   articles = pull_with_themes("supply chain disruption", 20)
   relevant = [a for a in articles if looks_relevant(a)]
   updated = 0
   for article in relevant:
       event = extract(article)
       risk = RISK_BY_EVENT_TYPE.get(event["event_type"], "low")
       for entity in event["organizations"] + event["locations"]:
           m = match_entity(entity, node_names)
           if m:
               node_id = name_to_id.get(m["matched_node"])
               if node_id:
                   resp = requests.patch(f"{API_BASE}/node/{node_id}/risk", json={"risk": risk})
                   if resp.ok:
                       updated += 1
                       print(f"Updated {m['matched_node']} -> {risk} via API")
   print(f"\nUpdated {updated} node(s) through the graph-backend API (not direct Cypher).")
