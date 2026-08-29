import json
from rapidfuzz import process, fuzz
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "atmograph123")
MATCH_THRESHOLD = 75

def fetch_all_node_names(tx):
    result = tx.run("MATCH (n) WHERE n.name IS NOT NULL RETURN DISTINCT n.name AS name")
    return [record["name"] for record in result]

def match_entity(entity_name, node_names):
    match = process.extractOne(entity_name, node_names, scorer=fuzz.WRatio)
    if match and match[1] >= MATCH_THRESHOLD:
        return {"matched_node": match[0], "score": match[1]}
    return None

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        node_names = session.execute_read(fetch_all_node_names)
    driver.close()

    with open("sample_extracted_events.json") as f:
        events = json.load(f)

    for event in events:
        event["matched_nodes"] = []
        for entity in event.get("organizations", []) + event.get("locations", []):
            m = match_entity(entity, node_names)
            if m:
                event["matched_nodes"].append({"entity": entity, **m})

    with open("sample_matched_events.json", "w") as f:
        json.dump(events, f, indent=2)

    matched_count = sum(1 for e in events if e["matched_nodes"])
    print(f"{matched_count}/{len(events)} events matched to at least one real graph node.")
    print("Saved sample_matched_events.json")
