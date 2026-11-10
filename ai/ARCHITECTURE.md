# Accidion AI Module Architecture

## 1. Document status

This document describes intended architecture boundaries for product AI in Accidion Identity Cloud. It is a design baseline, not evidence of implemented or deployed components.

It supplements the repository-root `docs/ARCHITECTURE.md`, `AGENTS.md`, `RULES.md`, accepted ADRs, and security policies. Those sources remain authoritative. Any material architectural choice not already approved must be recorded and reviewed through the repository's ADR process before implementation.

## 2. Goals

The AI module is intended to provide a controlled, auditable integration point for approved AI-assisted IGA use cases while preserving:

- Tenant isolation and trusted identity context.
- Existing authentication, authorization, and deterministic policy enforcement.
- Human accountability for access decisions and privileged operations.
- Data minimisation, privacy, and approved provider use.
- Testability, evaluation, observability, and operational control.
- Provider portability without leaking provider-specific contracts into domain services.

## 3. Non-goals and hard boundaries

The AI module is not:

- An identity source of truth.
- An authorization engine or policy decision point.
- A replacement for IGA workflows, approvals, or connector verification.
- A mechanism for autonomous access provisioning or deprovisioning.
- A general-purpose route for sending arbitrary tenant data to external models.
- Permission to introduce a new provider, model, framework, or runtime without approval.

For the MVP, AI Copilot remains disabled by default. If approved and enabled, capabilities are limited to observe, reason, and recommend. AI output is advisory and must not directly mutate identity or access state.

## 4. Conceptual components

The existing directory names represent intended separation of responsibilities:

| Component area | Responsibility | Important boundary |
| --- | --- | --- |
| Gateway | Validate an AI request, establish approved execution context, apply limits, route to an approved provider adapter, and normalise the result. | Must not bypass platform authentication, authorization, tenant checks, safety checks, or audit requirements. |
| Providers | Adapt approved provider APIs to an internal contract. | Provider credentials and provider-specific details remain isolated; no provider is implicitly approved by this document. |
| Prompts | Store reviewed, versioned task instructions and metadata. | Prompt text is not a security boundary and cannot grant permissions. |
| Guardrails | Apply input/output validation, injection-aware handling, data minimisation, and safety restrictions. | Must fail safely when required checks cannot run. |
| Policies | Define permitted use cases, data classes, model capabilities, and prohibited behaviours. | Product authorization and deterministic policy remain outside model control. |
| Evaluations | Measure expected behaviour, regression, safety, and robustness. | Evaluation results are evidence with scope and limitations, not proof of universal correctness. |
| Audit | Define auditable records for AI use and human oversight. | Avoid recording raw sensitive prompts/responses unless specifically approved and protected. |

## 5. Conceptual request flow

An approved use case should follow this logical sequence:

1. An authenticated Accidion application or service requests an AI-assisted operation.
2. The platform performs ordinary authentication and authorization before the AI request is accepted.
3. Trusted tenant and actor context is attached by the platform; it is not inferred from model output or trusted solely because a caller supplied it.
4. The gateway validates the use case, input schema, data classification, feature state, limits, and applicable policy.
5. Guardrails minimise or redact data and treat user-supplied/retrieved content as untrusted.
6. The gateway selects only a provider/model explicitly approved for that use case and data category.
7. The provider adapter performs the model interaction with bounded timeouts and controlled error handling.
8. Output validation and guardrails check structure, safety, and policy constraints.
9. The application receives an advisory result with appropriate uncertainty and provenance metadata.
10. Appropriate audit and operational events are recorded, subject to approved data-retention rules.
11. Any actual access decision or state-changing operation remains in the existing authorized IGA workflow with its required human approvals and verification.

This is a conceptual sequence. It does not prescribe an unapproved implementation technology or claim that each step is currently implemented.

## 6. Trust boundaries and data handling

- Treat prompts, retrieved documents, connector data, user content, model output, and provider responses as untrusted.
- Tenant context must originate from trusted authenticated platform context and be enforced by application services and data-access layers.
- Do not rely on a prompt instruction as a substitute for tenant isolation or authorization.
- Minimise data sent to a model. Prefer purpose-specific, least-data context over full identity records.
- Do not transmit customer/tenant data to an external provider until provider approval, data-processing terms, permitted data categories, region, retention, security configuration, and technical controls have been reviewed.
- Keep secrets in approved secret-management systems; never place them in prompts, source, logs, fixtures, or model context.
- Define retention and deletion behaviour for prompts, responses, embeddings, caches, and evaluation datasets before implementing persistent storage.
- Do not use production identity data in development or evaluation datasets unless explicitly approved through the applicable data-governance process.

## 7. Failure and safety behaviour

The design must fail closed or return a controlled unavailable/denied result when required authentication context, tenant context, feature enablement, policy, provider approval, validation, or safety checks are missing or unavailable.

Provider timeouts, rate limits, malformed output, refusal, and network errors must not cause a fallback to an unapproved provider or unsafe execution path.

AI failure must not bypass or weaken ordinary IGA workflows. A recommendation must never be represented as a completed access action.

## 8. Evaluation and audit

Before a customer-facing AI use case is enabled, define measurable acceptance criteria and evaluation coverage appropriate to its risk. Include normal, boundary, adversarial, cross-tenant, privacy, and failure cases.

Audit design should identify, where appropriate and approved, the actor, tenant context, use-case identifier, prompt/template version, provider/model identifier, policy/guardrail outcome, correlation identifier, result status, and human review outcome. Avoid raw sensitive content by default. Exact fields, retention, integrity, and access controls require review against the platform audit and privacy design.

## 9. Decisions that require ADR or approval

The following must not be silently decided by implementation:

- Provider/model selection and permitted data categories.
- Hosting region, data residency, retention, and provider data-processing configuration.
- Internal gateway/API contract and service ownership.
- Prompt storage/versioning mechanism.
- Guardrail and policy enforcement technology.
- Evaluation framework and release thresholds.
- Audit schema, retention, and integrity controls.
- Any persistence, cache, queue, or new infrastructure for AI workloads.

## 10. Implementation status

The architecture above is a conceptual target. Existing folders are scaffolding unless implementation, tests, configuration, and operational evidence demonstrate otherwise. Do not create deployable services or add dependencies solely to make this design appear implemented.
