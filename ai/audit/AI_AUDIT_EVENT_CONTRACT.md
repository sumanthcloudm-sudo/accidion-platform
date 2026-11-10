# Proposed AI Audit Event Contract

**Status: PROPOSED — NOT APPROVED**

This document proposes AI operation metadata for submission through a future host-owned Accidion `acc-audit` capability, if defined and approved. It is not an existing API or schema and does not authorize implementation, data retention, event delivery, or AI enablement.

## 1. Purpose and current evidence

The proposed contract is intended to make approved AI request decisions and outcomes traceable without recording prompt or response content by default.

Repository evidence:

- `ai/audit/` contains no implementation; this document and its README are proposals.
- `services/acc-audit/` is a placeholder. No host audit API, event schema, implementation, database schema, or operational contract was found.
- The AI architecture and Gateway documents refer to an approved host audit boundary but do not establish its concrete interface.
- The architecture baseline mentions platform messaging and persistence choices, but it does not define an audit-specific transport or schema. ADR-002 and ADR-003 remain Proposed.
- ADR-007 and ADR-008 remain Proposed and do not approve this contract, Copilot scope, or feature enablement.

The intended boundary is a host-owned `acc-audit` capability after the host audit owner identifies and approves its interface. This proposal adds no service, API, transport, database, event bus, or deployment. AI-specific documentation and any future mapping belong under `ai/audit/`; the host audit owner would own the authoritative audit contract, storage, access, integrity, and lifecycle.

## 2. Design principles

1. **Host-owned audit:** AI operation events are submitted only through the approved host audit boundary. They do not create an alternate audit source of truth.
2. **Trusted context:** Tenant and actor references originate in authenticated, server-side host context. Do not copy values from user input, prompts, retrieved content, or provider responses as trusted identities.
3. **Least data:** Record stable identifiers, bounded outcomes, versions, and safe metadata needed for accountability. Omit raw prompts, raw model responses, credentials, secrets, and unnecessary personal or identity data by default.
4. **No AI authority:** An event describes an AI operation; it is not an authorization decision, access approval, or evidence that a suggested action occurred.
5. **Explicit uncertainty:** A missing, conflicting, or untrusted field is not repaired into a trusted value. Reject or safely omit it according to the host-approved contract.
6. **No implied approval:** All names, fields, status values, and examples below are proposals. Provider, model, route, use case, schema version, and retention are not approved by appearing here.
7. **Disabled and advisory-only:** Copilot remains disabled by default. Only if separately approved and enabled may it observe, reason, and recommend; its output remains advisory and cannot authorize, approve, or execute an operation.

## 3. Proposed event envelope

The following illustrative JSON is a candidate logical envelope, not a finalized serialization, public API, or host event schema. All values are synthetic.

```json
{
  "schema_version": "proposed-v1",
  "event_id": "event-synth-1001",
  "event_type": "ai.guardrail.outcome",
  "occurred_at": "2026-11-10T09:00:00Z",
  "tenant_id": "tenant-synth-blue",
  "actor_id": "actor-synth-admin-3",
  "actor_type": "user",
  "correlation_id": "corr-synth-1001",
  "request_id": "req-synth-1001",
  "use_case": "explain-application-access",
  "status": "rejected",
  "reason_code": "classification_not_allowed",
  "prompt_version": "access-explanation-synth-v1",
  "policy_version": "ai-policy-synth-v1",
  "guardrail_version": "ai-guardrails-synth-v1",
  "provider": null,
  "model": null,
  "data_classification": "Restricted",
  "human_review": null,
  "metadata": {
    "duration_ms": 12
  }
}
```

### 3.1 Candidate fields

Requiredness and representation remain subject to the host audit owner's contract:

| Field | Candidate meaning and handling |
|---|---|
| `schema_version` | Version of this proposed AI event shape; define compatibility and evolution with the host audit owner. |
| `event_id` | Opaque event identifier. Generation, uniqueness, idempotency, and duplicate handling are unresolved host decisions. |
| `event_type` | Bounded event category from the list below. |
| `occurred_at` | Time the AI operation outcome occurred, not the audit delivery time. Clock source and timestamp format require agreement. |
| `tenant_id` | Trusted host tenant reference, if established and permitted by host privacy rules. Never trust a caller-supplied value. |
| `actor_id` | Trusted authenticated actor or service-principal reference, if established and permitted. Never derive it from user content or provider output. |
| `actor_type` | Bounded actor category if required by the host audit contract. |
| `correlation_id` | Host-trusted correlation reference for tracing the operation. |
| `request_id` | Opaque AI request reference; do not encode personal data or secrets. |
| `use_case` | Registered use-case identifier. Unknown or unapproved identifiers must not be used to imply eligibility. |
| `status` | **AI operation outcome** for this event type. It does not report whether the audit event was delivered. |
| `reason_code` | Optional bounded, non-sensitive reason code; never place raw error/provider text here. |
| `prompt_version` | Optional reviewed template/version reference, when a prompt was used and the identifier is approved for audit. No prompt text. |
| `policy_version` | Optional AI policy version reference, when evaluated. |
| `guardrail_version` | Optional guardrail version reference, when evaluated. |
| `provider` / `model` | Optional approved provider/model identifiers or profile references, only when that stage was reached and the host permits recording them. Null/omitted does not imply a provider was approved. |
| `data_classification` | Trusted host-assigned classification label, if available and approved for audit. Do not infer a less restrictive label from content. |
| `human_review` | Optional bounded review metadata as described in section 4.5; never an authorization grant. |
| `metadata` | Optional allowlisted, bounded, privacy-reviewed technical metadata. Do not use it as an untyped payload escape hatch. |

If authenticated context has not been established, do not persist untrusted tenant or actor values as if they were authoritative. Whether such a denial event may be recorded without those identifiers is a host audit owner decision.

## 4. Event categories and AI operation statuses

An event records the operation's state at a point in its lifecycle. The following names and values are proposed, and must be reconciled with the host audit naming and compatibility conventions:

| `event_type` | Candidate `status` values | Purpose |
|---|---|---|
| `ai.request.decision` | `accepted`, `denied`, `disabled`, `unavailable` | Record the host/Gateway decision to accept or reject an AI request. |
| `ai.policy.outcome` | `allowed`, `denied`, `error` | Record the AI-use policy result. An `allowed` status is not host resource authorization. |
| `ai.guardrail.outcome` | `passed`, `rejected`, `refused`, `error` | Record input/output guardrail processing. Provider-supplied claims do not set this status. |
| `ai.provider.outcome` | `completed`, `refused`, `timeout`, `throttled`, `error` | Record a provider-stage outcome, if an approved provider call occurred. All provider output remains untrusted. |
| `ai.human_review.outcome` | `required`, `reviewed`, `deferred`, `withdrawn`, `not_required` | Record an approved review-workflow outcome when applicable. It does not mean access was authorized or changed. |

The host audit owner must decide whether to emit separate lifecycle events, a terminal summary, or both. Do not create duplicate events that obscure ordering or operation status.

### 4.1 AI operation outcome is not audit delivery outcome

`status` describes the AI operation only. For example, `status: "denied"` means the AI request or a policy/guardrail stage was denied; it does not mean the audit submission failed.

Audit delivery has a separate, out-of-band outcome controlled by the host audit interface. Possible concepts such as acknowledged, rejected, retrying, or unavailable are illustrative only; this proposal does not define delivery statuses, transport responses, or delivery records. Do not overwrite an AI operation status with a delivery result, and do not add a recursive audit-delivery event unless the host audit owner defines one.

The host audit owner must define when an event is considered accepted, how delivery failures are surfaced, and how duplicate/retry behavior works. The producer must not claim audit success merely because it constructed an event.

### 4.2 Provider and model metadata

Provider/model identifiers may be recorded only if the corresponding approved route was actually used and the host audit owner and privacy/security reviewers approve the metadata. Do not record credentials, endpoints containing secrets, raw provider request/response bodies, or caller-selected provider/model values. Provider response fields never establish trusted event metadata.

### 4.3 Prompt and policy metadata

Record version identifiers, not prompt or policy contents. Omit identifiers for stages not reached. Version values must be generated or selected by trusted application configuration, not supplied by user text or provider output.

### 4.4 Data classification

Classification must be supplied by the approved host source. Missing, unknown, or conflicting classification is not converted into a permissive value. Whether the audit record may include the label itself, especially for Restricted data, requires host privacy and audit-owner approval. Do not include classified content in the event.

### 4.5 Human review metadata

If approved for a use case, a bounded `human_review` object may contain an opaque workflow/review reference, trusted reviewer reference, review time, and an enumerated review outcome. It must not include free-text reviewer notes by default. A human-review event is not a host authorization decision and does not establish that an access change was made.

## 5. Privacy and data minimization

- Do not include raw prompts, raw model responses, retrieved documents, source content, credentials, passwords, tokens, private keys, secrets, or full identity records by default.
- Do not put sensitive values in `reason_code`, `metadata`, or error descriptions.
- Include tenant and actor references only from trusted authenticated context and only as allowed by host privacy and access policy.
- Minimize resource references and avoid unnecessary subject identifiers; define any required references with Product, Privacy, Security, and the host audit owner.
- Keep provider/model and prompt-version metadata to opaque approved identifiers. Do not add provider payloads or prompt text for debugging.
- Treat audit metadata as potentially sensitive. Enforce host-defined tenant-scoped access, least privilege, monitoring, retention, and deletion.
- Any exception to content minimization needs a documented purpose, explicit Product/Security/Privacy approval, host audit-owner agreement, access restrictions, and a retention/deletion decision before implementation.

## 6. Proposed validation requirements

Future producers and the host audit boundary should agree on validation, including:

- Accept only a supported schema version and bounded event type/status combinations.
- Validate trusted identifier provenance, timestamp representation, and required fields; reject conflicting tenant/actor context.
- Enforce maximum lengths, enumerations, and allowlisted metadata keys/values.
- Reject raw prompt/response content, credentials, secret material, and unapproved personal data rather than silently truncating or transforming it into an apparently valid event.
- Preserve operation status and distinguish it from any audit delivery result.
- Use an explicit compatibility and deprecation process approved by the host audit owner.
- Do not fabricate defaults for unknown status, classification, actor, tenant, policy, or provider values. Fail safely and surface the validation failure through approved safe diagnostics.

The exact schema validator, enforcement point, error contract, and whether validation is performed by producers, the host boundary, or both remain undecided.

## 7. Integrity, access, and tenant isolation

The host audit owner and Security/Architecture must define and implement the integrity and access controls. This proposal selects no cryptographic mechanism or storage design.

Requirements to resolve include:

- Authenticate and authorize the event producer at the host boundary; do not trust event fields alone as proof of producer identity.
- Preserve provenance and integrity according to host audit requirements, with controls against unauthorized modification or deletion.
- Scope audit writes, reads, administrative access, exports, and any derived reporting by trusted tenant context and least privilege.
- Prevent caller-controlled tenant/actor fields from overriding authenticated context.
- Define idempotency, duplicate, ordering, replay, and clock-skew handling.
- Record only the minimum metadata required for accountability and investigation.

Cross-tenant visibility, integrity bypass, or an untrusted producer must fail closed under the approved host policy.

## 8. Retention and deletion

No retention period, archival method, deletion process, or legal hold policy is defined here. The host audit owner, Privacy/Data Governance, Security, and Product must determine the applicable host policy and whether AI metadata requires any additional handling.

AI integration must inherit approved host audit retention, deletion, access, and legal-hold controls. Do not introduce AI-specific persistence or retain prompts/responses in the audit stream by default. Any deviation requires explicit approval before implementation.

## 9. Audit failure and acknowledgment

Audit delivery failure must not be silently ignored, converted into a successful audit result, or handled by logging sensitive content elsewhere. Safe error reporting must not expose event contents or provider details.

### Unresolved acknowledgment-before-provider decision

It is not decided whether the host audit boundary must acknowledge a pre-provider decision event before the Gateway may invoke a provider. The decision has security, availability, latency, and data-processing implications and belongs to Product, Security, Architecture, and the host audit owner.

Before any AI runtime is implemented or enabled, explicitly decide:

1. Which events are mandatory and at which request stages they must be recorded.
2. Whether an audit write must be acknowledged before provider invocation.
3. What to do when audit is unavailable before provider invocation.
4. What response and operational handling applies when post-provider audit delivery fails.
5. Whether buffering/retries are permitted and, if so, how integrity, idempotency, ordering, and retention are assured.

Until approved, do not assume audit is optional, assume successful delivery, or choose a fail-open path. Where an approved policy makes audit a required check, inability to complete that check must fail closed. This proposal does not define a queue, local buffer, retry mechanism, or transport.

## 10. Future acceptance criteria and test scenarios

The following are proposed acceptance criteria for future contract and runtime work. They are **not completed tests** and provide no current evidence that an audit control is implemented.

### Contract/schema scenarios

- Valid examples for each event type and allowed status pass the approved schema.
- Unsupported schema versions, missing required fields, wrong types, oversized values, and invalid event/status combinations are rejected safely.
- AI operation outcome remains distinct from host audit delivery outcome in both successful and failed submissions.
- Optional provider, model, prompt, policy, guardrail, classification, and review fields are present only when their stage was reached and recording is approved.
- Duplicate, retry, out-of-order, and replayed events behave according to the host-approved contract.

### Trust, privacy, and tenant scenarios

- Forged, missing, or conflicting tenant/actor context is rejected or omitted as defined by host policy; untrusted values never become authoritative event fields.
- Cross-tenant writes, reads, exports, and report access are denied; tenant-scoped authorized access succeeds.
- Synthetic prompt, response, credential, secret, and unnecessary identity markers do not appear in events, diagnostics, or fallback logs.
- Provider-supplied status, tenant, actor, classification, policy, review, or advisory fields cannot override trusted event metadata.
- Untrusted producer identity, event tampering, or unauthorized modification/deletion is detected or denied under the host-approved integrity controls.

### Failure and audit-boundary scenarios

- Host audit unavailable before provider invocation exercises the explicitly approved acknowledgment/failure policy and verifies whether the provider call is prevented.
- Audit delivery failure after a provider outcome does not rewrite the AI operation status, silently discard mandatory records, or create sensitive fallback logs.
- Host validation rejection, timeout, retry, and duplicate acknowledgment behavior are handled without claiming an event was accepted when it was not.
- Audit access, retention, deletion, and any legal hold follow the approved host policy.

Test frameworks, test paths, implementation locations, and CI integration are not selected here. Tests should use synthetic values and host-approved test doubles; no live provider call is needed to validate event contract behavior.

## 11. Dependencies and approvals

The roles below are required decision owners or reviewers, not evidence that a named owner has been assigned or that approval has been obtained. The repository currently identifies no host `acc-audit` owner. All listed decisions remain outstanding unless separately recorded through the applicable approval process.

| Owner | Decisions requiring explicit approval | Approval state / dependency |
|---|---|---|
| Product | Whether an AI audit contract or runtime integration is MVP-eligible; approved use cases and lifecycle stages to audit; whether human-review metadata is needed; user-visible and operational consequences of audit failure. | Pending. Product must establish the use-case and scope boundary before a runtime contract is finalized. |
| Security | Trusted producer, tenant, and actor context; threat model; tenant isolation; integrity and access controls; safe failure behavior; whether audit acknowledgment gates provider invocation. | Pending. Security review is required before contract approval or runtime implementation. |
| Privacy / Data Governance | Permitted identifiers and classifications; minimization; tenant-scoped access; retention, deletion, legal hold; and any exception to excluding content from events. | Pending. Privacy/data-governance approval is required before collection, retention, or any content exception. |
| Architecture | The integration boundary with host `acc-audit`; ownership and versioning of the authoritative schema; compatibility and lifecycle semantics; whether any existing host capability can support the requirements. | Pending. Must not be used to select or imply an unapproved transport, persistence layer, separate service, event bus, or deployment. |
| Host `services/acc-audit` owner | Whether an applicable host interface exists; authoritative envelope and validation; producer authentication; acknowledgment and delivery semantics; idempotency, ordering, and integrity; tenant-scoped access; retention/deletion; outage behavior. | Owner not identified in the repository; approval pending. The host owner must establish the real boundary and semantics before this proposal can become an integration contract. |
| Repository maintainers | Whether this documentation is acceptable as a proposal; approval before implementation changes to event/API formats, tenant or security boundaries, privacy/retention behavior, dependencies, CI, or operations, as required by repository governance. | Pending. Review of this document does not itself approve implementation or supersede required domain-owner approvals. |
| Relevant ADR owners | **ADR-002:** architecture owner / CTO (to be assigned) must approve any reliance on its proposed messaging direction; it does not select an audit transport or schema. **ADR-003:** architecture owner / data owner (to be assigned) must approve any persistence decision; it does not approve an audit database, schema, or retention policy. **ADR-007:** Product owner / Security owner (to be assigned) must approve Copilot scope and disabled-by-default, non-autonomous boundaries. **ADR-008:** Product owner / delivery owner (to be assigned) must approve MVP scope and whether related runtime work is in scope. | All four ADRs are Proposed with approval pending. Their owners must use their respective ADR processes; this document does not change their status or claim those decisions are approved. |

These approvals are related but not interchangeable. In particular, ADR-002 and ADR-003 do not authorize a transport or persistence choice for AI audit; ADR-007 and ADR-008 do not approve this event contract or enable Copilot. Transport, acknowledgment, persistence, retention, and audit-failure policy remain undecided until the responsible owners approve them. No approval is implied by this proposal.
