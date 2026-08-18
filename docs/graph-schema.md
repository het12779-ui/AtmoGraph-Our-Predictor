# Graph Schema Mapping

To integrate Het's real Neo4j export into our PyTorch Geometric model, we will map the Neo4j schema into the `x` and `edge_index` tensors. 
The node properties from Neo4j (such as criticality, risk levels, and operational metrics for Ports, Suppliers, Manufacturers, and Retailers) will be normalized and concatenated into the `x` feature matrix (shape `[num_nodes, num_features]`). 
The relationships in Neo4j (such as 'SUPPLIES_TO' or 'SHIPS_VIA') will be extracted to form the `edge_index` tensor (shape `[2, num_edges]`), capturing the directional flow of the supply chain. 
Categorical node types can also be one-hot encoded and appended to the `x` features so the GCN layer can differentiate between a Port and a Retailer.

## Typical Entities/Locations in Disruption Events (GDELT)
For disruption-related news events such as port strikes, factory fires, shipping delays, and trade tariffs, typical entities that appear include:
* **ORGANIZATION**: Labor unions, port authorities, shipping companies, manufacturers, governments, regulatory bodies.
* **GPE (Geo-Political Entity)**: Countries (e.g., US, Pakistan), cities, states/provinces involved in the disruption.
* **LOC (Location)**: Major waterways, oceans, specific ports.
* **PERSON**: Key union leaders, government officials, or company spokespersons.
* **FAC (Facility)**: Specific factories, port facilities, or infrastructure.
These entities guide the NER extraction rules for tracking disruptions in the supply chain graph.

## Theme Reliability (Day 2 Findings)
* **Reliable Themes**: `STRIKE`, `PORT`, `NATURAL_DISASTER`, `TRADE_DISPUTE` consistently yield highly relevant supply-chain disruption articles.
* **Noisy Themes**: `SUPPLY_CHAIN` can sometimes pull generic business articles. `FIRE` is extremely noisy without context, pulling residential fires instead of just factories. `TARIFF` can be very noisy with political commentary.

## NER Extraction Quality (Day 3 Findings)
* **Organizations (ORG)**: spaCy often extracts noisy or partial phrases from titles (e.g., "Retail Supply Chain Leaders Say Disruption" instead of just the organization name).
* **Locations (GPE)**: Extraction is sparse and can miss implicit or abbreviated locations (e.g., "TN" for Tamil Nadu).
* **Event Types**: A simple keyword-based approach defaults to `UNKNOWN` too frequently because news titles use varied synonyms and complex syntax that strict string matching misses.
