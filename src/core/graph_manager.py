# core/graph_manager.py

from rdflib import Graph, URIRef, Literal

class GraphManager:
    def __init__(self):
        self.g = Graph()

    def add_triple(self, s, p, o):
        s_ref = URIRef(s)
        p_ref = URIRef(p)
        o_ref = URIRef(o) if o.startswith("http") else Literal(o)
        self.g.add((s_ref, p_ref, o_ref))

    def get_graph(self):
        return self.g

    # 🔜 For future use
    def load_namespace(self, prefix, uri):
        self.g.bind(prefix, uri)

    def serialize(self, format="ttl"):
        return self.g.serialize(format=format)

    # Optional hooks for validation, merging, etc. can be added here
