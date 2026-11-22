# PRGCE — Pedagogical Reasoning Graph Comparison Engine

A small, reproducible prototype for comparing how two STEM textbooks organize instruction about the same concept. The demonstration topic is **Newton's Second Law**.

## Research questions
1. How can textbook explanations be represented as attributed pedagogical reasoning graphs (PRGs)?
2. How can nodes with different wording be aligned without assuming identical labels?
3. How can structural and instructional-order differences be quantified and explained?
4. What can be validated automatically, and what requires expert judgement?

## Sources and provenance
- `data/source_a.txt`: text extracted from the user's uploaded *OpenStax College Physics 2e*, Sub-section 4.3, “Newton's Second Law of Motion”.
- `data/source_b.txt`: text extracted from the user's uploaded *OpenStax University Physics, Volume 1*, Sub-section 5.3, “Newton's Second Law”.

The files are source extracts, not full textbook chapters. Word counts are recorded in the generated PRG metadata. They are approximately 4,000–8,000 words per source. The two books are both OpenStax publications and share closely related explanations/examples. This is a material confound: the comparison is a pilot of graph extraction and comparison, not a clean comparison of independent authorial pedagogies.

## Requirements
Python 3.9+; NetworkX 3.x.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run
From the repository root:

```bash
python src/compare.py --source1 data/source_a.txt --source2 data/source_b.txt
```

Optional output directory:

```bash
python src/compare.py --source1 data/source_a.txt --source2 data/source_b.txt --outdir output
```

The command writes `source_a_prg.json`, `source_b_prg.json`, and `comparison.json`.

## PRG schema
Nodes have `id`, `type`, `label`, `description`, `evidence`, and `position`. Allowed types: `concept`, `example`, `motivation`, `formalism`, `exercise`, `connection`. Edges have `source`, `target`, `type`, and `evidence`. Allowed edge types: `prerequisite_of`, `illustrates`, `formalizes`, `motivates`, `leads_to`. The extractor caps each graph at 40 nodes and applies a DAG check before serialization.

## Method
The baseline is deterministic and offline. It detects candidate concepts and pedagogical elements using transparent lexical rules, then proposes relations using co-occurrence and textual-order heuristics. Node alignment is one-to-one and type-constrained, using synonym normalization and token Jaccard similarity. Graph comparison reports mapped-edge Jaccard, degree-distribution similarity, combined similarity, ordering divergences, and longest directed path.

**Important:** automatically inferred edges and node alignments are hypotheses, not ground truth. The reported alignment coverage is not alignment accuracy. The baseline deliberately avoids calling an LLM so the run is reproducible and API cost is $0.00. `llm_client.py` and `prompts.py` provide an extension point; no API call is made by the current CLI.

## Project structure

```text
prg-compare/
├── README.md
├── requirements.txt
├── COSTS.md
├── src/
│   ├── extractor.py
│   ├── compare.py
│   ├── llm_client.py
│   └── prompts.py
├── data/
│   ├── source_a.txt
│   └── source_b.txt
├── output/
│   ├── source_a_prg.json
│   ├── source_b_prg.json
│   └── comparison.json
└── evaluation/
    └── evaluation_protocol.md
```

## Limitations
- Rule-based extraction is brittle and may miss implicit pedagogical relations.
- The lexical matcher is not a contextual embedding model; polysemy and paraphrase remain difficult.
- Edge generation uses transparent heuristics and may create plausible but unsupported relations.
- A DAG is a simplifying assumption; real instructional materials can contain cycles, revisits, and feedback loops.
- The source pair is not independent enough for strong claims about authorial style.
- No second-rater assessment has been performed. The evaluation protocol states how to conduct it without inventing a result.

## Reproducibility
All outputs are generated from the included text files. No external API key is needed. Generated metrics are in `output/comparison.json`.
