# Evaluation protocol (to complete with an independent reviewer)

## 1. Node alignment audit
1. Export `output/comparison.json` and both PRGs.
2. Hide the algorithm's similarity scores from the reviewer.
3. For every proposed node pair, label: correct / partial / incorrect / ambiguous.
4. Separately list missed matches by inspecting unmatched nodes in both graphs.
5. Report precision = correct proposed pairs / all proposed pairs; recall = correct proposed pairs / all gold-standard pairs; F1 = harmonic mean. Do not call coverage accuracy.

## 2. Edge and DAG audit
- Verify every edge against its evidence sentence and the surrounding paragraph.
- Label each edge correct / unsupported / wrong direction / wrong relation type.
- Record cycles in the unfiltered annotation separately. A cycle may represent iterative review, not necessarily an error.

## 3. Divergence explanation review
Give the reviewer the source passages, relevant graph fragments, and generated explanation. Ask whether it is (a) supported by source evidence, (b) understandable, and (c) educationally meaningful. Record comments and disagreements. Do not claim this step is complete until a second person has performed it.

## 4. Budget audit
Current baseline makes zero API calls and costs $0.00. If an LLM is added, log model, prompt/completion tokens, retries, and per-call cost; stop at a cumulative $7.00.
