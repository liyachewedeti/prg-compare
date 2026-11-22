"""Deterministic, auditable PRG extraction baseline for textbook prose."""
import re
from pathlib import Path

CONCEPTS = [
    ("net_force", "Net external force", [r"net (?:external )?force", r"\bFnet\b", r"∑F"]),
    ("force", "Force", [r"\bforce\b"]),
    ("mass", "Mass", [r"\bmass\b"]),
    ("acceleration", "Acceleration", [r"\bacceleration\b", r"accelerat(?:e|es|ed|ing)"]),
    ("velocity", "Velocity", [r"\bvelocity\b"]),
    ("motion", "Change in motion", [r"change in motion", r"motion"]),
    ("external_force", "External force", [r"external force"]),
    ("system", "System of interest", [r"system of interest", r"\bsystem\b"]),
    ("momentum", "Momentum", [r"\bmomentum\b"]),
    ("weight", "Weight / gravitational force", [r"\bweight\b", r"gravitational force"]),
    ("inertia", "Inertia", [r"\binertia\b"]),
    ("newton_first", "Newton's first law", [r"Newton[’']s first law"]),
    ("free_body", "Free-body diagram", [r"free.?body diagram"]),
]

def _sentences(text):
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", text) if len(s.strip()) > 35]

def extract_prg(path, source_id, concept_domain="Newton's Second Law"):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    low = text.lower()
    sents = _sentences(text)
    nodes, edges, seen = [], [], set()
    def add(nid, typ, label, desc, evidence, pos):
        if nid in seen or len(nodes) >= 40: return
        seen.add(nid); nodes.append({"id":nid,"type":typ,"label":label,"description":desc[:420],"evidence":evidence[:500],"position":pos})
    # Concept nodes: only retain concepts actually attested in the source.
    for nid,label,pats in CONCEPTS:
        matches = [(i,s) for i,s in enumerate(sents) if any(re.search(p,s,re.I) for p in pats)]
        if matches:
            i,s = matches[0]
            add(nid,"concept",label,s,s,i)
    # Motivations: rationale / cause-effect framing.
    mot = next(((i,s) for i,s in enumerate(sents) if re.search(r"why|cause|important|used to calculate|central question|what happens|reason",s,re.I)),None)
    if mot: add("motivation_1","motivation","Why force explains changes in motion",mot[1],mot[1],mot[0])
    # Formalism: equations and mathematical statement.
    forms = [(i,s) for i,s in enumerate(sents) if re.search(r"F\s*=\s*m|Fnet|∑F|mathematically|equation|vector equation|rate.*momentum",s,re.I)]
    if forms:
        i,s=forms[0]; add("formalism_1","formalism","Mathematical statement of Newton's second law",s,s,i)
    # Examples: named or concrete worked illustrations.
    ex = [(i,s) for i,s in enumerate(sents) if re.search(r"EXAMPLE|lawn mower|car|basketball|rocket sled|skydiver|students push",s,re.I)]
    for j,(i,s) in enumerate(ex[:5],1): add(f"example_{j}","example",f"Illustrative application {j}",s,s,i)
    # Exercises and checks.
    exs = [(i,s) for i,s in enumerate(sents) if re.search(r"practice problem|check your understanding|grasp check|exercise|solve the following|how much force",s,re.I)]
    for j,(i,s) in enumerate(exs[:5],1): add(f"exercise_{j}","exercise",f"Practice/check question {j}",s,s,i)
    # Connections to prior/future knowledge.
    cons = [(i,s) for i,s in enumerate(sents) if re.search(r"Newton[’']s first law|momentum|free.?body diagram|friction|weight",s,re.I)]
    for j,(i,s) in enumerate(cons[:4],1): add(f"connection_{j}","connection",f"Connection to {('prior law' if 'first law' in s.lower() else 'related mechanics')}",s,s,i)
    # Sort by textual position for a faithful instructional sequence.
    nodes.sort(key=lambda n:(n["position"],n["id"]))
    ids={n["id"] for n in nodes}
    def edge(a,b,t,evidence):
        if a in ids and b in ids and a!=b and not any(x['source']==a and x['target']==b and x['type']==t for x in edges):
            edges.append({"source":a,"target":b,"type":t,"evidence":evidence[:300]})
    # Evidence-grounded relation heuristics. Sequence edges are weak hypotheses, marked as inferred.
    concepts=[n for n in nodes if n['type']=='concept']
    for a,b in zip(concepts,concepts[1:]): edge(a['id'],b['id'],'leads_to','Textual-order heuristic; requires expert verification.')
    for n in nodes:
        if n['type']=='formalism':
            for c in concepts:
                if any(k in (c['label']+' '+c['description']).lower() for k in ['force','mass','acceleration']): edge(n['id'],c['id'],'formalizes','Equation and concept co-occurrence heuristic.')
                break
        elif n['type']=='example':
            for c in concepts:
                if any(k in n['description'].lower() for k in [c['label'].lower().split('/')[0].strip()]): edge(n['id'],c['id'],'illustrates','Example/concept lexical overlap heuristic.'); break
        elif n['type']=='motivation':
            if concepts: edge(n['id'],concepts[0]['id'],'motivates','Motivation precedes concept sequence in source.')
        elif n['type']=='connection':
            if concepts: edge(n['id'],concepts[0]['id'],'prerequisite_of','Related prior-knowledge concept; inferred, not asserted.')
    # Ensure acyclic output by dropping any edge that would close a cycle.
    import networkx as nx
    g=nx.DiGraph(); g.add_nodes_from(n['id'] for n in nodes)
    clean=[]
    for e in edges:
        if not nx.has_path(g,e['target'],e['source']): g.add_edge(e['source'],e['target']); clean.append(e)
    return {"source":source_id,"concept_domain":concept_domain,"nodes":nodes,"edges":clean,
            "extraction_metadata":{"method":"deterministic_rule_based_v1","model":"none (offline baseline)","api_cost_usd":0.0,"input_words":len(text.split()),"node_cap":40,"note":"Candidate relations are heuristically inferred and require human validation."}}
