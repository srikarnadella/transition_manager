import networkx as nx
from database_manager import DatabaseManager

class GraphManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.graph = nx.DiGraph()
        self._load_from_db()

    def _load_from_db(self):
        for _id, fa, ft, ta, tt, note in self.db.get_all_transitions():
            label_from = f"{fa} – {ft}"
            label_to   = f"{ta} – {tt}"
            self.graph.add_edge(label_from, label_to, note=note)

    def add_transition(self, from_artist: str, from_title: str,
                       to_artist: str, to_title: str,
                       note: str):
        self.db.add_transition(from_artist, from_title, to_artist, to_title, note)
        label_from = f"{from_artist} – {from_title}"
        label_to   = f"{to_artist} – {to_title}"
        self.graph.add_edge(label_from, label_to, note=note)

    def get_disjoint_components(self):
        return list(nx.weakly_connected_components(self.graph))

    def get_longest_path(self):
        longest = []
        for s in self.graph.nodes():
            for t in self.graph.nodes():
                if s == t: continue
                for path in nx.all_simple_paths(self.graph, source=s, target=t):
                    if len(path) > len(longest):
                        longest = path
        return longest

    def get_graph(self):
        return self.graph
