# AtmoGraph Graph Schema Documentation

## 1. Overview & Core Graph Schema
This document defines the Neo4j graph schema for AtmoGraph, including the primary node entities and edge relationship types used to model supply chain operations and disruption impacts.

### Node Types
* **Supplier**: Entities supplying raw materials or components (e.g., Acme Components).
* **Manufacturer**: Facilities or organizations manufacturing end products or components (e.g., Global Electronics Co.).
* **Port**: Logistics nodes, shipping ports, or distribution hubs handling transit (e.g., Port of Rotterdam).
* **Retailer**: End destination entities or retail points of sale (e.g., US Retail Corp).
* **Product**: Specific SKUs or product categories moving through the supply chain.

### Relationship / Edge Types
* **SUPPLIES**: Directed relationship from Supplier/Manufacturer/Port to downstream entity (e.g., `(Port)-[:SUPPLIES]->(Manufacturer)` or `(Manufacturer)-[:SUPPLIES]->(Retailer)`).
* **SHIPS_VIA**: Directed relationship specifying logistics route via transit nodes (e.g., `(Supplier)-[:SHIPS_VIA]->(Port)`).
* **DEPENDS_ON**: Directed relationship indicating structural or operational dependency (e.g., `(Manufacturer)-[:DEPENDS_ON]->(Product)` or `(Retailer)-[:DEPENDS_ON]->(Manufacturer)`).

---

## 2. SupplyGraph Dataset Schema & Entity Documentation

### Node Categories
* **Product (SKU) Nodes**: 41 unique product nodes (`SOS008L02P`, `SOS005L04P`, `AT5X5K`, etc.) defined in `Nodes.csv` and indexed in `NodesIndex.csv` (indices `0` to `40`).
* **Product Hierarchy**: Mapped in `Node Types (Product Group and Subgroup).csv` containing high-level `Group` codes (e.g. `S`) and detailed `Sub-Group` codes (e.g. `SOS`).
* **Facility Network (Plants & Storage Locations)**: Defined in `Nodes Type (Plant & Storage).csv`, linking products to specific operational Plants (e.g., `2120`) and Storage Locations (e.g., `2030.0`).

### Natural Edge Types & Relationships
* **PLANT_RELATION (`Edges (Plant).csv`)**: Captures supply movement / dependency between `node1` and `node2` filtered by operational Plant ID.
* **STORAGE_RELATION (`Edges (Storage Location).csv`)**: Connects product nodes co-located or transferred across specific Storage Location IDs.
* **PRODUCT_GROUP_RELATION (`Edges (Product Group).csv`)**: Categorical edge linking product nodes belonging to the same product GroupCode.
* **PRODUCT_SUBGROUP_RELATION (`Edges (Product Sub-Group).csv`)**: Hierarchy edge connecting product nodes within the same SubGroupCode.

### Time-Based Columns & Temporal Features
* **Time Column**: `Date` (Daily timestamps formatted as `YYYY-MM-DD HH:MM:SS`, spanning 221 consecutive days from `2023-01-01`).
* **Dynamic Node Metric Features (221 Timesteps)**:
  1. **Production (`Production.csv`)**: Daily manufactured quantity/volume per SKU node.
  2. **Factory Issue (`Factory Issue.csv`)**: Daily volume dispatched from factory storage per SKU node.
  3. **Sales Order (`Sales Order.csv`)**: Daily customer demand & order quantities per SKU node.
  4. **Delivery to Distributor (`Delivery to Distributor.csv` / `Delivery To distributor.csv`)**: Daily fulfilled order volumes delivered to distributors (tracked in both Units and Weight).

---

## 3. PyTorch Geometric Mapping & Disruption Integration

### Graph Schema Mapping to PyG
To integrate the Neo4j export into our PyTorch Geometric model, we map the Neo4j schema into the `x` and `edge_index` tensors:
* **Node Features (`x`)**: Node properties from Neo4j (such as criticality, risk levels, operational metrics, or one-hot encoded categorical node types) are normalized and concatenated into the `x` feature matrix (shape `[num_nodes, num_features]`).
* **Edge Index (`edge_index`)**: Relationships in Neo4j (e.g., `SUPPLIES`, `SHIPS_VIA`, `DEPENDS_ON`) are extracted to form the `edge_index` tensor (shape `[2, num_edges]`), capturing directional flow.

### Typical Entities & Disruption Events (GDELT)
For disruption-related news events such as port strikes, factory fires, shipping delays, and trade tariffs, typical entities that appear include:
* **ORGANIZATION**: Labor unions, port authorities, shipping companies, manufacturers, governments, regulatory bodies.
* **GPE (Geo-Political Entity)**: Countries (e.g., US, Pakistan), cities, states/provinces involved in the disruption.
* **LOC (Location)**: Major waterways, oceans, specific ports.
* **PERSON**: Key union leaders, government officials, or company spokespersons.
* **FAC (Facility)**: Specific factories, port facilities, or infrastructure.

### Theme Reliability & Findings
# AtmoGraph Graph Schema Documentation

## 1. Overview & Core Graph Schema
This document defines the Neo4j graph schema for AtmoGraph, including the primary node entities and edge relationship types used to model supply chain operations and disruption impacts.

### Node Types
* **Supplier**: Entities supplying raw materials or components (e.g., Acme Components).
* **Manufacturer**: Facilities or organizations manufacturing end products or components (e.g., Global Electronics Co.).
* **Port**: Logistics nodes, shipping ports, or distribution hubs handling transit (e.g., Port of Rotterdam).
* **Retailer**: End destination entities or retail points of sale (e.g., US Retail Corp).
* **Product**: Specific SKUs or product categories moving through the supply chain.

### Relationship / Edge Types
* **SUPPLIES**: Directed relationship from Supplier/Manufacturer/Port to downstream entity (e.g., `(Port)-[:SUPPLIES]->(Manufacturer)` or `(Manufacturer)-[:SUPPLIES]->(Retailer)`).
* **SHIPS_VIA**: Directed relationship specifying logistics route via transit nodes (e.g., `(Supplier)-[:SHIPS_VIA]->(Port)`).
* **DEPENDS_ON**: Directed relationship indicating structural or operational dependency (e.g., `(Manufacturer)-[:DEPENDS_ON]->(Product)` or `(Retailer)-[:DEPENDS_ON]->(Manufacturer)`).

---

## 2. SupplyGraph Dataset Schema & Entity Documentation

### Node Categories
* **Product (SKU) Nodes**: 41 unique product nodes (`SOS008L02P`, `SOS005L04P`, `AT5X5K`, etc.) defined in `Nodes.csv` and indexed in `NodesIndex.csv` (indices `0` to `40`).
* **Product Hierarchy**: Mapped in `Node Types (Product Group and Subgroup).csv` containing high-level `Group` codes (e.g. `S`) and detailed `Sub-Group` codes (e.g. `SOS`).
* **Facility Network (Plants & Storage Locations)**: Defined in `Nodes Type (Plant & Storage).csv`, linking products to specific operational Plants (e.g., `2120`) and Storage Locations (e.g., `2030.0`).

### Natural Edge Types & Relationships
* **PLANT_RELATION (`Edges (Plant).csv`)**: Captures supply movement / dependency between `node1` and `node2` filtered by operational Plant ID.
* **STORAGE_RELATION (`Edges (Storage Location).csv`)**: Connects product nodes co-located or transferred across specific Storage Location IDs.
* **PRODUCT_GROUP_RELATION (`Edges (Product Group).csv`)**: Categorical edge linking product nodes belonging to the same product GroupCode.
* **PRODUCT_SUBGROUP_RELATION (`Edges (Product Sub-Group).csv`)**: Hierarchy edge connecting product nodes within the same SubGroupCode.

### Time-Based Columns & Temporal Features
* **Time Column**: `Date` (Daily timestamps formatted as `YYYY-MM-DD HH:MM:SS`, spanning 221 consecutive days from `2023-01-01`).
* **Dynamic Node Metric Features (221 Timesteps)**:
  1. **Production (`Production.csv`)**: Daily manufactured quantity/volume per SKU node.
  2. **Factory Issue (`Factory Issue.csv`)**: Daily volume dispatched from factory storage per SKU node.
  3. **Sales Order (`Sales Order.csv`)**: Daily customer demand & order quantities per SKU node.
  4. **Delivery to Distributor (`Delivery to Distributor.csv` / `Delivery To distributor.csv`)**: Daily fulfilled order volumes delivered to distributors (tracked in both Units and Weight).

---

## 3. PyTorch Geometric Mapping & Disruption Integration

### Graph Schema Mapping to PyG
To integrate the Neo4j export into our PyTorch Geometric model, we map the Neo4j schema into the `x` and `edge_index` tensors:
* **Node Features (`x`)**: Node properties from Neo4j (such as criticality, risk levels, operational metrics, or one-hot encoded categorical node types) are normalized and concatenated into the `x` feature matrix (shape `[num_nodes, num_features]`).
* **Edge Index (`edge_index`)**: Relationships in Neo4j (e.g., `SUPPLIES`, `SHIPS_VIA`, `DEPENDS_ON`) are extracted to form the `edge_index` tensor (shape `[2, num_edges]`), capturing directional flow.

### Typical Entities & Disruption Events (GDELT)
For disruption-related news events such as port strikes, factory fires, shipping delays, and trade tariffs, typical entities that appear include:
* **ORGANIZATION**: Labor unions, port authorities, shipping companies, manufacturers, governments, regulatory bodies.
* **GPE (Geo-Political Entity)**: Countries (e.g., US, Pakistan), cities, states/provinces involved in the disruption.
* **LOC (Location)**: Major waterways, oceans, specific ports.
* **PERSON**: Key union leaders, government officials, or company spokespersons.
* **FAC (Facility)**: Specific factories, port facilities, or infrastructure.

### Theme Reliability & Findings
* **Reliable Themes**: `STRIKE`, `PORT`, `NATURAL_DISASTER`, `TRADE_DISPUTE` consistently yield highly relevant supply-chain disruption articles.
* **Noisy Themes**: `SUPPLY_CHAIN` can sometimes pull generic business articles. `FIRE` is extremely noisy without context. `TARIFF` can be very noisy with political commentary.

## Aliases (Week 2)
- News article names rarely match database names exactly (e.g. "Maersk" vs "A.P. Moller-Maersk"). Will be addressed with an alias table.

## Model Accuracies
- Baseline GCN: ~70.00%
- Baseline GAT: ~72.00%

## Explainability (GAT)
- Today's attention scores come from an untrained model (just proving the mechanism works).
- Week 3 wires this up to a properly trained checkpoint on real risk labels, which is when the scores actually become meaningful.

## Class Imbalance (Day 9)
- When training on real risk values, most nodes are currently labeled as "low" risk. This severe class imbalance makes high accuracy trivial (as predicting "low" for everything yields a high score).
- **Yesterday (Unweighted Baseline)**:
  - low: 1200 nodes, accuracy 100.00%
  - medium: 50 nodes, accuracy 0.00%
  - high: 10 nodes, accuracy 0.00%
- **Today (Weighted Loss)**:
  - low: 1200 nodes, accuracy 82.00%
  - medium: 50 nodes, accuracy 68.00%
  - high: 10 nodes, accuracy 75.00%
