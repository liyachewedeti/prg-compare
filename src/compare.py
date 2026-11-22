"""CLI and multi-scale PRG comparison engine."""
import argparse, json, re
from pathlib import Path
import networkx as nx
from extractor import extract_prg

SYNONYMS={
 'net force':'net external force','force':'net external force','fnet':'net external force',
 'acceleration':'change in velocity','mass':'inertia','velocity':'change in motion',
 'free-body diagram':'force diagram','weight':'gravitational force'
}

def norm(s):
 s=re.sub(r"[^a-z0-9 ]"," ",s.lower()); return re.sub(r"\s+"," ",s).strip()
def tokens(n):
 s=norm(n['label']+' '+n.get('description',''))
 for a,b in SYNONYMS.items(): s=s.replace(a,b)
 stop={'the','and','of','to','a','an','is','are','that','this','with','for','in','on','by','from','as','it','be'}
 return set(s.split())-stop

def align_nodes(A,B):
 na,nb=A['nodes'],B['nodes']; candidates=[]
 for a in na:
  for b in nb:
   if a['type']!=b['type']: continue
   ta,tb=tokens(a),tokens(b); jac=len(ta&tb)/max(1,len(ta|tb))
   label=1.0 if norm(a['label'])==norm(b['label']) else 0.0
   # Type agreement plus lexical overlap; no embedding service or hidden API cost.
   score=.75*jac+.25*label
   if score>=.16: candidates.append((score,a['id'],b['id']))
 candidates.sort(reverse=True); useda=set();usedb=set(); out=[]
 for score,a,b in candidates:
  if a not in useda and b not in usedb:
   useda.add(a);usedb.add(b);out.append({'source_a':a,'source_b':b,'score':round(score,3),'method':'type-constrained synonym-normalized token Jaccard'})
 return out

def degree_similarity(G,H):
 da=sorted([d for _,d in G.degree()]); db=sorted([d for _,d in H.degree()]); m=max(len(da),len(db),1)
 da=(da+[0]*m)[:m]; db=(db+[0]*m)[:m]
 return max(0,1-sum(abs(x-y) for x,y in zip(da,db))/(2*m*max(1,max(da+db))))

def edge_overlap(A,B,align):
 mp={x['source_a']:x['source_b'] for x in align}; ea={(mp[e['source']],mp[e['target']],e['type']) for e in A['edges'] if e['source'] in mp and e['target'] in mp}
 eb={(e['source'],e['target'],e['type']) for e in B['edges']}
 return len(ea&eb)/max(1,len(ea|eb)),ea,eb

def order_profile(P):
 by={n['id']:n for n in P['nodes']}; pos={n['id']:n.get('position',i) for i,n in enumerate(P['nodes'])}
 types=['motivation','concept','formalism','example','exercise']
 out={}
 for x in types:
  vals=[pos[n['id']] for n in P['nodes'] if n['type']==x]
  out[x]=min(vals) if vals else None
 return out

def analyze(A,B):
 GA=nx.DiGraph(); GB=nx.DiGraph(); GA.add_nodes_from(n['id'] for n in A['nodes']);GB.add_nodes_from(n['id'] for n in B['nodes'])
 GA.add_edges_from((e['source'],e['target']) for e in A['edges']);GB.add_edges_from((e['source'],e['target']) for e in B['edges'])
 align=align_nodes(A,B); alignment=len(align)/max(1,min(len(A['nodes']),len(B['nodes'])))
 eover,ea,eb=edge_overlap(A,B,align); deg=degree_similarity(GA,GB)
 topo=.6*eover+.4*deg
 pa,pb=order_profile(A),order_profile(B); diffs=[]
 for x,y in [('formalism','example'),('motivation','formalism'),('concept','formalism'),('example','exercise')]:
  if pa[x] is not None and pa[y] is not None and pb[x] is not None and pb[y] is not None:
   da=pa[x]<pa[y]; db=pb[x]<pb[y]
   if da!=db:
    diffs.append({'dimension':f'{x}_vs_{y}','source_a_order':'before' if da else 'after','source_b_order':'before' if db else 'after',
     'explanation':f"Source A places {x} {'before' if da else 'after'} {y}, whereas Source B places it {'before' if db else 'after'} {y}. This indicates a difference in instructional sequencing; it is consistent with, but does not by itself prove, an inductive or deductive teaching strategy."})
 # Path depth only defined for DAG; disconnected graphs use longest directed path among components.
 def depth(g):
  if not nx.is_directed_acyclic_graph(g): return None
  return max((len(p)-1 for p in nx.all_simple_paths(g,s,t) for s in [] for t in []),default=0) if False else max((len(c)-1 for c in nx.dag_longest_path(g) for _ in []),default=max(0,len(nx.dag_longest_path(g))-1))
 da,db=depth(GA),depth(GB)
 structural=round(topo,3); semantic=round(alignment,3)
 # The divergence is complementary to similarity; report components separately.
 overall=.45*structural+.35*semantic+.20*(1-len(diffs)/4)
 divergence=1-overall
 return {'source_a':A['source'],'source_b':B['source'],'metrics':{'node_alignment_coverage':semantic,'mapped_edge_jaccard':round(eover,3),'degree_distribution_similarity':round(deg,3),'structural_similarity':structural,'combined_similarity':round(overall,3),'pedagogical_divergence':round(divergence,3),'critical_path_edges':{'source_a':da,'source_b':db}},'node_alignment':align,'pedagogical_divergences':diffs,'scale_analysis':{'node_level':f"{len(align)} one-to-one node matches from {len(A['nodes'])} and {len(B['nodes'])} extracted nodes; alignment is lexical and type-constrained, not expert-validated.",'subgraph_level':f"Mapped edge Jaccard={eover:.3f}; edge agreement is assessed only among aligned nodes.",'graph_level':f"Longest directed path: A={da} edges; B={db} edges. These are heuristic graph depths, not validated measures of cognitive difficulty."},'validity':{'source_a_is_dag':nx.is_directed_acyclic_graph(GA),'source_b_is_dag':nx.is_directed_acyclic_graph(GB),'source_a_nodes':len(A['nodes']),'source_b_nodes':len(B['nodes'])}}

def main():
 p=argparse.ArgumentParser();p.add_argument('--source1',required=True);p.add_argument('--source2',required=True);p.add_argument('--outdir',default='output');args=p.parse_args()
 out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
 A=extract_prg(args.source1,'openstax_college_physics_2e_section_4_3');B=extract_prg(args.source2,'openstax_university_physics_volume_1_section_5_3')
 (out/'source_a_prg.json').write_text(json.dumps(A,indent=2,ensure_ascii=False),encoding='utf-8');(out/'source_b_prg.json').write_text(json.dumps(B,indent=2,ensure_ascii=False),encoding='utf-8')
 result=analyze(A,B);(out/'comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(result['metrics'],indent=2));print(f"Saved PRGs and comparison to {out.resolve()}")
if __name__=='__main__': main()
