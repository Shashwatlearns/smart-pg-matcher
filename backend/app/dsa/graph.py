from .heap import TopKHeap


class AdjacencyListGraph:
    def __init__(self):
        # Maps node_id -> {neighbor_id: edge_weight}
        self.adj_list = {}

    def add_node(self, node_id: str):
        """Adds a node to the graph if it doesn't already exist."""
        if node_id not in self.adj_list:
            self.adj_list[node_id] = {}

    def add_edge(self, node1: str, node2: str, weight: float):
        """Adds a weighted undirected edge. Missing nodes are created."""
        self.add_node(node1)
        self.add_node(node2)

        self.adj_list[node1][node2] = weight
        self.adj_list[node2][node1] = weight

    def get_top_k_neighbors(self, node_id: str, k: int) -> list:
        """
        Returns the K neighbors with the highest edge weight.

        Finding the node's neighbors is O(1). Ranking them with a bounded
        heap costs O(D log K), where D is the number of neighbors.
        """
        if node_id not in self.adj_list:
            return []

        top_heap = TopKHeap(k)
        for neighbor_id, score in self.adj_list[node_id].items():
            top_heap.push((score, neighbor_id))

        top_k = []
        for score, neighbor_id in top_heap.get_sorted_desc():
            top_k.append({
                "neighbor_id": neighbor_id,
                "score": score
            })
        return top_k