# PR Prep Threat Model & Security Architecture

## Overview
This document outlines the threat model, trust boundaries, threat catalog, and security mitigations for PR Prep in accordance with Phase 11 requirements.

---

## 1. Trust Boundaries & Data Flow

```
[ GitHub Webhooks ] ---> ( HMAC-SHA256 Ingress ) ---> [ Redis / ARQ Queue ]
                                                               |
[ Specialist Agents ] <--- ( CapabilityScope ) <--- [ LangGraph Engine ]
        |
        v
[ Tiger Vector / Postgres ] (Append-only Audit Events & Code Chunks)
```

1. **Untrusted Ingress:** GitHub Webhook events (`X-Hub-Signature-256`, `X-GitHub-Delivery`).
2. **Untrusted Data:** PR code diffs, commit messages, PR descriptions, and repository comments.
3. **Privileged Boundaries:** GitHub App Tokens, OpenAI API Keys, Postgres/Redis connection strings, and Admin REST endpoints.

---

## 2. Threat Catalog & Mitigations

| Threat ID | Threat Category | Target | Description | Mitigation Strategy | Owner |
|---|---|---|---|---|---|
| **THREAT-01** | Forged Webhook | Ingress Endpoint | Attacker sends malicious POST to `/webhook/github` | Constant-time `HMAC-SHA256` signature verification (`verify_github_signature`) | Ingress Team |
| **THREAT-02** | Webhook Replay | Ingress Endpoint | Attacker replays valid delivery header to duplicate reviews | Idempotency key tracking via `X-GitHub-Delivery` (`_SEEN_DELIVERIES`) | Ingress Team |
| **THREAT-03** | Prompt Injection | Agent Prompt | Malicious diff or comment contains "Ignore previous instructions" | `InjectionGuard` pattern detection and data boundary isolation in prompt registry | Security Team |
| **THREAT-04** | Capability Escape | Tool Boundary | Specialist agent attempts unauthorized shell or path access | `CapabilityScope` default-deny validation and path prefix checks | Tooling Team |
| **THREAT-05** | Unauthorized Action | HITL / Admin API | Low-privilege user calls `/api/hitl/action` or `/api/economics` | Server-side RBAC dependencies (`require_role`) validating user roles | Security Team |
| **THREAT-06** | Secret Disclosure | Logs / Events | API key or token printed in structured JSON logs | `AuditLogger` secret masking replacing `bearer`, `sk-`, and `token` | Security Team |
| **THREAT-07** | Audit Tampering | Database | Application role attempts to UPDATE or DELETE audit events | Append-only hypertable roles preventing UPDATE/DELETE queries | Infra Team |
