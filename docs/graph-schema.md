# Graph Schema Mapping

To integrate Het's real Neo4j export into our PyTorch Geometric model, we will map the Neo4j schema into the `x` and `edge_index` tensors. 
The node properties from Neo4j (such as criticality, risk levels, and operational metrics for Ports, Suppliers, Manufacturers, and Retailers) will be normalized and concatenated into the `x` feature matrix (shape `[num_nodes, num_features]`). 
The relationships in Neo4j (such as 'SUPPLIES_TO' or 'SHIPS_VIA') will be extracted to form the `edge_index` tensor (shape `[2, num_edges]`), capturing the directional flow of the supply chain. 
Categorical node types can also be one-hot encoded and appended to the `x` features so the GCN layer can differentiate between a Port and a Retailer.
