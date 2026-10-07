# Security

The security policy is in
[`SECURITY.md`](https://github.com/GuidoMerliniEnel/ai-act-hackaton/blob/main/SECURITY.md).

!!! danger "Reporting vulnerabilities"
    Do **not** open a public issue. Use
    [GitHub Security Advisories](https://github.com/GuidoMerliniEnel/ai-act-hackaton/security/advisories/new).

## In scope

- Any path that bypasses human oversight (execution without review, or
  under an active stop)
- Audit trail tampering not detected by `verifica_catena()`
- Leakage of LLM API keys
- Prompt injection through dataset fields reaching the LLM

## Practices (OP36 4.6)

| Practice                                  | Implementation                                   |
| ----------------------------------------- | ------------------------------------------------ |
| No secrets in the repository              | `.env` git-ignored; `.env.example` placeholders  |
| Dependency vulnerabilities                | `pip-audit` in CI; Renovate vulnerability alerts |
| Supply chain                              | GitHub Actions pinned to commit SHAs             |
| Least privilege in CI                     | `permissions: contents: read` by default         |
| Untrusted LLM output                      | Guardrails and template fallback                 |
| Tamper evidence                           | SHA-256 hash chain on the audit trail            |
