# SupplyGraph Dataset Schema & Entity Documentation

## 1. Overview
The SupplyGraph dataset captures Fast-Moving Consumer Goods (FMCG) supply chain operations, containing node definitions, multi-relational edges (plants, storage locations, product categories), and daily temporal time-series metrics.

---

## 2. Entities & Node Types

### Node Categories
* **Product (SKU) Nodes**: 41 unique product nodes (`SOS008L02P`, `SOS005L04P`, `AT5X5K`, etc.) defined in `Nodes.csv` and indexed in `NodesIndex.csv` (indices `0` to `40`).
* **Product Hierarchy**: Mapped in `Node Types (Product Group and Subgroup).csv` containing high-level `Group` codes (e.g. `S`) and detailed `Sub-Group` codes (e.g. `SOS`).
* **Facility Network (Plants & Storage Locations)**: Defined in `Nodes Type (Plant & Storage).csv`, linking products to specific operational Plants (e.g., `2120`) and Storage Locations (e.g., `2030.0`).

---

## 3. Natural Edge Types & Relationships

* **PLANT_RELATION (`Edges (Plant).csv`)**: Captures supply movement / dependency between `node1` and `node2` filtered by operational Plant ID.
* **STORAGE_RELATION (`Edges (Storage Location).csv`)**: Connects product nodes co-located or transferred across specific Storage Location IDs.
* **PRODUCT_GROUP_RELATION (`Edges (Product Group).csv`)**: Categorical edge linking product nodes belonging to the same product GroupCode.
* **PRODUCT_SUBGROUP_RELATION (`Edges (Product Sub-Group).csv`)**: Hierarchy edge connecting product nodes within the same SubGroupCode.

---

## 4. Time-Based Columns & Temporal Features

### Temporal Structure
* **Time Column**: `Date` (Daily timestamps formatted as `YYYY-MM-DD HH:MM:SS`, spanning 221 consecutive days from `2023-01-01`).

### Dynamic Node Metric Features (221 Timesteps)
1. **Production (`Production.csv`)**: Daily manufactured quantity/volume per SKU node.
2. **Factory Issue (`Factory Issue.csv`)**: Daily volume dispatched from factory storage per SKU node.
3. **Sales Order (`Sales Order.csv`)**: Daily customer demand & order quantities per SKU node.
4. **Delivery to Distributor (`Delivery to Distributor.csv` / `Delivery To distributor.csv`)**: Daily fulfilled order volumes delivered to distributors (tracked in both Units and Weight).

> **Note for GNN & Ripple Effect Predictor (Week 3)**:
> The 221 daily timesteps across `Production`, `Sales Order`, `Factory Issue`, and `Delivery` form the time-series node feature vectors used for temporal Graph Neural Network modeling and supply disruption ripple effect predictions.
