# API and compute cost accounting

| Component | Calls | Estimated API cost |
|---|---:|---:|
| Text extraction | 0 | $0.00 |
| PRG extraction baseline | 0 | $0.00 |
| Node alignment | 0 | $0.00 |
| Graph comparison | 0 | $0.00 |
| **Total** | **0** | **$0.00** |

Budget ceiling: **$7.00**. The prototype uses deterministic local rules rather than an LLM. Therefore the measured API spend is zero, not an estimate. This is a deliberate budget-safe baseline, not evidence that LLM extraction would be free. If an LLM adapter is added, record provider/model, prompt and completion tokens, price per token, retries, and cumulative spend; stop before the $7 ceiling. `llm_client.py` currently exposes an extension point but intentionally raises `NotImplementedError` rather than making an unmetered call.
