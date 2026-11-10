# Accidion AI Safety Requirements

## 1. Purpose and authority

This document defines safety expectations for product AI capabilities developed under `ai/`. It supplements root `AGENTS.md`, `RULES.md`, `docs/ARCHITECTURE.md`, accepted ADRs, security/privacy policies, and maintainer decisions. It does not replace technical security controls or legal/privacy review.

These are engineering requirements and design expectations. Their presence in documentation is not evidence that controls have been implemented, tested, or independently assessed.

## 2. Product capability boundary

Accidion Identity Cloud is a multi-tenant IGA platform. For the MVP, AI Copilot remains disabled by default. If approved and enabled, AI capabilities are limited to:

- **Observe:** inspect only context explicitly authorised and provided by the platform.
- **Reason:** analyse approved context and explain relevant factors, with limitations and uncertainty.
- **Recommend:** provide advisory suggestions for an authorised person or existing workflow to consider.

AI must not autonomously execute privileged operations or make authoritative access decisions.

### Prohibited behaviour

AI must never independently:

- Grant, revoke, modify, or provision identities, accounts, roles, groups, permissions, or entitlements.
- Approve or reject an access request or certification on behalf of an accountable human.
- Change authorization policies, security settings, tenant configuration, or privileged credentials.
- Execute arbitrary tools, scripts, connector operations, or external actions that mutate state.
- Bypass an existing approval workflow, segregation-of-duties control, or target-side verification.

Any later proposal to expand this boundary requires explicit product, security, architecture, and governance approval and an appropriate ADR. A prompt or model instruction cannot grant such authority.

## 3. Tenant isolation and authorization

- Enforce authentication, authorization, and tenant isolation in trusted application code before data is made available to an AI operation.
- Derive tenant and actor context from trusted authenticated platform context. Do not trust a tenant identifier supplied only by a user, prompt, retrieved document, or model.
- Scope retrieval, database queries, caches, background jobs, events, audit access, and provider requests to the authorised tenant and use case.
- Never use one tenant's data to answer another tenant's request.
- Treat model output as untrusted. It cannot grant permissions, change tenant context, or override deterministic policy decisions.
- Fail closed when identity, authorization, tenant context, policy, or required validation is missing, invalid, ambiguous, or unavailable.
- Include negative tests for cross-tenant access and context-confusion attempts.

## 4. Provider and external data controls

No provider or model is approved merely because it is mentioned in documentation or is technically available.

Before tenant/customer data is sent to an external model provider, obtain the required approvals for:

- Provider and model identity, purpose, and permitted use cases.
- Data categories and minimisation/redaction strategy.
- Data-processing terms and whether inputs/outputs may be retained or used for training.
- Processing region, residency, subprocessors, and cross-border transfer implications.
- Retention, deletion, incident handling, and support access.
- Encryption, access control, network path, credentials, and operational monitoring.
- Contractual, privacy, security, and customer commitments.

Until those reviews are complete, use synthetic or otherwise approved non-sensitive data for development and testing. Do not silently fall back to another provider if the approved provider is unavailable.

## 5. Prompt injection and untrusted content

Treat user prompts, uploaded files, retrieved documents, connector attributes, web content, tool outputs, and model responses as untrusted data.

- Clearly separate trusted application instructions from untrusted content in the implementation.
- Do not follow instructions embedded in retrieved or user-provided content that attempt to override system policy, reveal data, change tenant context, or invoke tools.
- Do not treat prompt wording as the security enforcement layer.
- Restrict model capabilities and tool access to the minimum required for the approved use case.
- Do not expose secrets, system prompts containing sensitive operational details, or data outside the authorised request context.
- Test direct and indirect prompt-injection attempts, including malicious instructions in retrieved content.

## 6. Sensitive data, secrets, and logging

- Minimise personal and identity data before model submission.
- Never include credentials, passwords, API keys, access tokens, private keys, or secrets in prompts, model context, source code, test fixtures, or logs.
- Do not log raw prompts, raw responses, or identity attributes by default.
- Use approved redaction, access control, retention, and deletion rules for any stored AI interaction data.
- Protect evaluation datasets and audit records as potentially sensitive data.
- Do not use production/customer data for development, debugging, demonstrations, or evaluations without explicit approval.

## 7. Output safety and reliability

- Validate model outputs against an explicit schema and the approved use-case policy.
- Treat generated text as untrusted; encode or sanitise it before rendering or using it in downstream systems.
- Distinguish facts retrieved from trusted sources from model-generated interpretation or recommendation.
- Communicate uncertainty and missing evidence. Do not invent identity attributes, entitlements, policy results, approvals, or audit history.
- Do not convert model text directly into executable commands, SQL, policy changes, or connector operations.
- Handle refusals, malformed output, provider errors, timeouts, and unavailable safety checks with controlled failure.
- Never represent a recommendation as an approval, a completed operation, or a verified change.

## 8. Human oversight and auditability

A qualified human and the existing IGA workflow remain accountable for access decisions and state-changing operations.

For each approved use case, define what must be auditable. Depending on risk and approved policy, metadata may include actor, tenant, use case, correlation ID, prompt version, provider/model version, policy and guardrail outcomes, result status, and human review outcome. Avoid raw sensitive content unless explicitly approved with appropriate controls.

Audit records must follow the platform's approved integrity, access, retention, and privacy requirements. Do not invent a new audit store or schema without architectural approval.

## 9. Security testing and release gates

Before enabling an AI use case, define risk-based acceptance criteria and test at least the applicable cases:

- Tenant isolation and authorization failures.
- Prompt injection and malicious retrieved content.
- Sensitive-data leakage and secret disclosure.
- Unsupported or fabricated claims.
- Unsafe access recommendations and prohibited action requests.
- Invalid output schemas and unexpected model responses.
- Provider timeout, refusal, rate limits, and outage.
- Logging, audit, retention, and deletion behaviour.
- Feature-disabled and rollback behaviour.

Passing a finite evaluation suite does not prove that a model is universally safe or correct. Record evaluation scope, dataset provenance, known limitations, and residual risks.

## 10. Incident and stop conditions

Stop the affected AI operation and escalate through the established security/incident process if there is evidence of cross-tenant exposure, secret disclosure, unauthorised provider transmission, unsafe state-changing behaviour, audit bypass, or a material violation of approved data handling.

Do not conceal, silently retry through an unapproved path, or weaken controls to keep an AI feature available.

## 11. Enforcement status

This document states required safety expectations. Actual protection requires implementation and verification in application code, provider configuration, infrastructure, access controls, tests, monitoring, and operational procedures. Documentation alone cannot enforce tenant isolation, prevent data transmission, or guarantee model behaviour.
