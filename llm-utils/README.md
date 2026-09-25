# LLM utilities for OceENS

Tools around the project's LLM providers that live outside the application.

## Cost tracking has moved into the application

This folder used to hold `token-counting/`, which estimated the number of tokens in the **repository's source code** (`*.py`) and multiplied it by a hard-coded rate. That measure said nothing about what the application actually spends: summaries of free-text answers consume *prompt and response* tokens, not Python files, and the "4 characters = 1 token" approximation matches no provider's tokenizer.

Cost tracking is now **measured, not estimated**, and built into the application:

| Where | What |
| --- | --- |
| `services/llm_costs.py` | Cost computed from the tokens actually consumed |
| `/backend/llm/prices` | Editable price list per model (admin) |
| `/backend/llm/costs` | Overall cost, broken down by survey and by model (admin) |
| 💰 button on a survey row | Cost of that survey's summaries |

The daemon records the counts returned by the provider (`Summary.input_tokens` / `output_tokens` / `model_used`) at generation time: it is the only chance to capture them, as no API lets you ask for them afterwards.

See the "Summary costs" section of the root README.

---

## Planned utilities

This folder remains meant for LLM tools outside the application:

- prompt management and versioning;
- comparative model evaluation;
- provider switching scripts.
