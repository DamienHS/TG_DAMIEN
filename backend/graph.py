class Graph:
    def __init__(self):
        # {id: {"x": int, "y": int, "capacity": int}}
        self.nodes = {}

        # {id: [(neighbor_id, weight), ...]}
        self.edges = {}

    def add_node(self, node_id, x=None, y=None, capacity=None):
        self.nodes[node_id] = {
            "x": x,
            "y": y,
            "capacity": capacity
        }
        self.edges.setdefault(node_id, [])

    def add_edge(self, u, v, weight):
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Les deux nœuds doivent exister avant d'ajouter une arête.")

        # arêtes non orientées
        self.edges[u].append((v, weight))
        self.edges[v].append((u, weight))

    def delete_node(self, node_id):
        if node_id in self.nodes:
            del self.nodes[node_id]

        if node_id in self.edges:
            del self.edges[node_id]

        # supprimer des voisins
        for src in self.edges:
            self.edges[src] = [
                (v, w) for (v, w) in self.edges[src] if v != node_id
            ]

    def delete_edge(self, src, dst):
        if src in self.edges:
            self.edges[src] = [e for e in self.edges[src] if e[0] != dst]

        if dst in self.edges:
            self.edges[dst] = [e for e in self.edges[dst] if e[0] != src]

    def get_graph(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }
