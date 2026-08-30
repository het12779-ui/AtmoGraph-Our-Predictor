import json
from match_entities_to_graph import match_entity

with open("aliases.json") as f:
    ALIASES = json.load(f)

def match_entity_with_alias(entity_name, node_names):
    if entity_name in ALIASES:
        canonical = ALIASES[entity_name]
        if canonical in node_names:
            return {"matched_node": canonical, "score": 100, "via": "alias"}
    result = match_entity(entity_name, node_names)
    if result:
        result["via"] = "fuzzy"
    return result
