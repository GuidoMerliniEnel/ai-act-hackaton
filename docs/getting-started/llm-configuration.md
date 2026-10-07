# LLM Configuration

`explainer.py` turns model output into an explanation a control-room
operator can understand. It has two interchangeable engines:

| Engine                 | Behaviour                                                              |
| ---------------------- | ---------------------------------------------------------------------- |
| **Template** (default) | Deterministic, no API, no cost, always available                       |
| **External LLM**       | OpenAI, Anthropic, Azure OpenAI or any compatible endpoint (Ollama, vLLM, LM Studio) |

## Configure

1. Copy the template:

    ```bash
    cp .env.example .env
    ```

2. Fill in the variables:

    | Variable          | Example                                    |
    | ----------------- | ------------------------------------------ |
    | `LLM_PROVIDER`    | `azure`                                    |
    | `LLM_API_KEY`     | *(your key — never commit it)*             |
    | `LLM_MODEL`       | Azure deployment name, e.g. `gpt-4o-mini`  |
    | `LLM_BASE_URL`    | `https://<resource>.openai.azure.com`      |
    | `LLM_TIMEOUT`     | `20`                                       |
    | `LLM_API_VERSION` | `2024-12-01-preview`                       |

3. Verify:

    ```bash
    python test_llm.py
    ```

    The script prints the SHAP factors, the template explanation and the
    LLM explanation, with source and latency.

!!! danger "Secrets"
    `.env` is git-ignored. Never commit it, paste it in issues, or include
    it in a submission archive.

## Design guarantees

- **The LLM neither decides nor computes.** It receives numbers already
  produced by the model and translates them into operational language.
- **Guardrails.** A response is discarded, and the template is used, if it
  cites numbers not in the data, uses technical jargon, or omits the main
  factor.
- **Automatic fallback** on any error: network, quota, timeout or malformed
  JSON. No card is ever left without an explanation.
- **Declared source.** Each explanation states its source: `template`,
  `llm:provider/model` or `template(fallback:...)`. The call is recorded
  in the audit trail.
- **Untrusted input.** Dataset fields sent to the LLM are treated as
  untrusted (prompt injection).

## Why an LLM at all?

An LLM adds non-determinism and a dependency on an external provider. The
team uses it because operators found its explanations more readable. The
template remains the reference and the fallback
([D-20](../decisions/index.md#d-20)). The choice and its limits are
declared in the [model card](../compliance/model-card.md).
