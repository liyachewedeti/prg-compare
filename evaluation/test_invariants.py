import json
import unittest
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

class PRGInvariantTests(unittest.TestCase):
    def test_generated_graphs_respect_schema_and_caps(self):
        for name in ('source_a_prg.json', 'source_b_prg.json'):
            data = json.loads((ROOT / 'output' / name).read_text(encoding='utf-8'))
            self.assertLessEqual(len(data['nodes']), 40)
            self.assertTrue(all(n['type'] in {'concept','example','motivation','formalism','exercise','connection'} for n in data['nodes']))
            g = nx.DiGraph()
            g.add_nodes_from(n['id'] for n in data['nodes'])
            g.add_edges_from((e['source'],e['target']) for e in data['edges'])
            self.assertTrue(nx.is_directed_acyclic_graph(g))

if __name__ == '__main__':
    unittest.main()
