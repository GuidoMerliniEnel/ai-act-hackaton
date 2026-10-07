# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report them privately through
[GitHub Security Advisories](https://github.com/GuidoMerliniEnel/ai-act-hackaton/security/advisories/new).
Include a description, steps to reproduce, and the affected component.

## Response Timeline

| Severity | Response Time | Fix Target   |
| -------- | ------------- | ------------ |
| Critical | 24 hours      | 72 hours     |
| High     | 48 hours      | 2 weeks      |
| Medium   | 1 week        | 1 month      |
| Low      | 1 month       | Next release |

## Supported Versions

| Version | Supported |
| ------- | --------- |
| `main`  | ✅ Yes    |

## Scope

In scope:

- Bypass of human oversight: any path that executes a HIC/HITL decision
  without review, or any action under an active emergency stop
- Tampering with the audit trail that `verifica_catena()` does not detect
- Leakage of `.env` secrets (LLM API keys) to logs, UI or prompts
- Prompt injection through data fields that reach the LLM explainer

Out of scope:

- The synthetic dataset content
- Vulnerabilities in third-party dependencies already tracked upstream
  (report them to the upstream project; Renovate tracks updates here)

## Security Practices

- Secrets only in `.env`, which is git-ignored; `.env.example` holds
  placeholders.
- GitHub Actions are pinned to commit SHAs.
- CI runs `pip-audit` and a license gate on every pull request.
- The LLM never decides or computes: its output is validated by guardrails
  and falls back to deterministic templates.
