# Accidion AI Guardrails Implementation Plan

**Status: PROPOSED — NOT APPROVED**

This document is a read-only audit deliverable and a proposed implementation plan. It does not approve an architecture, define an accepted policy, implement a guardrail, authorize a provider or data transfer, or enable Accidion AI Copilot. The product Copilot remains disabled by default.

## 1. Scope and evidence

The guardrails directory currently contains:

- `ai/guardrails/README.md` — proposed governance and safety guidance.
- `ai/guardrails/GUARDRAILS_IMPLEMENTATION_PLAN.md` — this proposed, documentation-only coverage and implementation plan; it does not implement guardrails.
- `ai/guardrails/.gitkeep` — scaffold placeholder.

There is no executable guardrail implementation, configuration, or guardrail-specific test in `ai/guardrails/`. The repository does have five synthetic evaluation case descriptions, an offline structural catalog validator, and 19 unit tests for that validator. Those tests validate fixture shape; they do not execute or verify product guardrail behavior.

Related design evidence:

- `ai/SAFETY.md`, `ai/ARCHITECTURE.md`, and `ai/DEVELOPMENT.md` state requirements and explicitly distinguish design from enforcement.
- `ai/gateway/CONTRACTS.md`, `ai/policies/POLICY_ENGINE.md`, and `ai/providers/PROVIDER_INTERFACE.md` are proposed, not-approved designs.
- `ai/evaluations/HARNESS_DESIGN.md` is proposed, not-approved design; `ai/evaluations/README.md` says the cases are descriptive and the catalog validator does not evaluate model behavior.
- `docs/engineering/adr/ADR-007-decision-topic.md` and `ADR-008-decision-topic.md` both remain Proposed with approvals pending.

The exact host service, runtime language, feature-flag mechanism, platform data-classification authority, audit contract, provider/model, and applicable MVP AI use case are not established by the inspected artifacts. This plan does not choose them.

## 2. Guardrail coverage matrix

Status key: **D** = documented requirement/proposal exists; **I** = executable product enforcement exists; **T** = behavioral enforcement test exists. “No” means none was found in the inspected repository; the offline catalog validator is not counted as runtime enforcement.

| # | Guardrail | D / I / T | Evidence and current gap |
|---|---|---|---|
| 1 | Copilot disabled by default | Yes / No / No | Root rules, ADR-007, AI safety and Gateway/policy proposals require this. No product flag or runtime rejection path exists in the AI module. |
| 2 | OBSERVE, REASON, RECOMMEND; advisory only | Yes / No / No | Documented in AI safety, Gateway, and policy proposals. No runtime capability boundary or output-use restriction is implemented. |
| 3 | No autonomous provisioning, approval, privileged execution | Yes / No / No | Prohibited by rules and proposals. No implemented tool/action surface or negative test was found. |
| 4 | Prompt-injection handling | Yes / No / No | Trust-boundary guidance and synthetic case exist. No input handling control or behavioral test executes the case. |
| 5 | Input and output validation | Yes / No / No | Schemas and validation are proposed. The existing validator checks catalog JSON only, not product requests or provider responses. |
| 6 | Sensitive-data and classification enforcement | Yes / No / No | Data minimization and classification are documented; no product enforcement is present. |
| 7 | Block Restricted data from providers | Yes / No / No | Policy proposal says deny provider processing. No runtime pre-transmission check or test exists. |
| 8 | Tenant isolation and trusted context | Yes / No / No | Strongly documented, including host-derived context. No guardrail or host integration enforcing it was found. |
| 9 | Host authorization authoritative | Yes / No / No | Explicitly documented; no AI integration exists to demonstrate or test the boundary. |
| 10 | Fail closed on missing/unavailable checks | Yes / No / No | Specified in safety, gateway, and policy proposals. No runtime failure-path tests exist. |
| 11 | Provider response validation and refusal handling | Yes / No / No | Proposed contracts describe validation/refusal statuses. No adapter or output-validation code exists. |
| 12 | Safe errors and no sensitive logging | Yes / No / No | Privacy and safe-error guidance exists. No AI logging/error implementation or leakage test exists. |
| 13 | Human review and approval boundaries | Yes / No / No | Human accountability is documented. No workflow integration or review-state test exists. |
| 14 | Auditable guardrail decisions | Yes / No / No | Minimal audit metadata is proposed. `ai/audit/` is a placeholder; no audit integration or test exists. |
| 15 | Security/adversarial evaluation | Yes / No / No | Five synthetic descriptions and a proposed harness design exist. Only offline structure validation runs; there are no executable adversarial product evaluations. |

This matrix describes repository evidence, not the security posture of any uninspected external host system.

## 3. Proposed guardrail specifications

Every enforcement point below is a design proposal. Nothing in this section claims that the named component or control is implemented. Runtime candidate paths in the implementation checklist are filenames for planning only; their language and ownership must be confirmed before implementation.

Each future enforcement change must include and run its corresponding behavioral tests in the same implementation increment. A control is not complete based on code or documentation alone; tests must demonstrate its allow and deny/failure behavior at the stated enforcement boundary.

### G01 — Default-disabled Copilot

- **Purpose:** Ensure no AI work occurs unless a separately approved, trusted product control enables the relevant use case.
- **Threat/risk:** Accidental or unauthorized product AI activation, including activation through configuration presence or user input.
- **Expected behavior:** Default to disabled; check enablement in trusted host/Gateway configuration before retrieval or provider routing; do not allow prompts or model output to toggle the flag.
- **Enforcement point:** Host feature boundary and Gateway entry/routing boundary.
- **Failure behavior:** Missing, invalid, or unavailable feature state means disabled; return a safe disabled/unavailable result and make no provider call.
- **Required tests:** Default configuration; missing/invalid flag; user-controlled enablement attempt; assert no retrieval/provider invocation while disabled.
- **Dependencies:** ADR-007 approval, approved MVP scope, host flag/configuration ownership, explicit enablement and rollback process.
- **Acceptance criteria:** Every entry path remains off by default; disabled requests cannot reach retrieval/provider code; state changes require authorized configuration and approval.

### G02 — Advisory-only capability boundary

- **Purpose:** Restrict eligible AI behavior to OBSERVE, REASON, and RECOMMEND.
- **Threat/risk:** Model output being treated as an authoritative access/policy decision or action instruction.
- **Expected behavior:** Use-case capability is fixed by trusted registration; after validating provider output, the trusted Accidion AI Gateway/orchestrator establishes and labels the result as advisory. Provider-supplied content or metadata, including an `advisory` field, is never authoritative and cannot be consumed as an approval, authorization result, or provisioning command.
- **Enforcement point:** Use-case policy, Gateway request/response contract, and host consumer.
- **Failure behavior:** Unknown operation or non-advisory/invalid response is rejected; no downstream state change occurs.
- **Required tests:** Unknown capability rejection; Gateway establishes advisory status independently of provider output; provider-supplied advisory markers cannot affect the trusted status; host consumer cannot turn a recommendation into an action.
- **Dependencies:** Approved use case, product policy, Gateway/host contract, ADR-007.
- **Acceptance criteria:** Only approved operations pass; tests prove AI output cannot grant access, approve requests, or trigger state mutation.

### G03 — Prohibit autonomous actions

- **Purpose:** Prevent AI from provisioning, approving/rejecting access, or performing privileged execution.
- **Threat/risk:** Unauthorized identity/access changes, SoD bypass, connector operation, or privileged tool execution.
- **Expected behavior:** No action-capable tools or autonomous action endpoints are exposed; human workflows and deterministic policy remain authoritative.
- **Enforcement point:** Gateway capability surface and host workflow/action boundary; deny before action dispatch.
- **Failure behavior:** Any attempted action is refused safely and produces no mutation; missing action-control configuration cannot enable an action.
- **Required tests:** Requests to provision, approve, alter policy, invoke connector/admin tools; assert zero action dispatch and unchanged synthetic state.
- **Dependencies:** Product/security approval; host workflow and authorization contracts; ADR-007; maintainer approval for API/security-boundary changes.
- **Acceptance criteria:** No model-originated path can cause action; all negative tests verify no external side effect.

### G04 — Prompt-injection and untrusted-content handling

- **Purpose:** Prevent user/retrieved instructions from overriding trusted policy, task scope, or authorization.
- **Threat/risk:** Direct/indirect injection, exfiltration, tenant switching, or tool invocation through hostile content.
- **Expected behavior:** Keep trusted policy and untrusted content distinct; treat prompts/documents/provider output as data, not authority; minimize context and expose no unauthorized tools. Do not rely on a classifier or prompt instruction as the security boundary.
- **Enforcement point:** Host context assembly and Gateway input normalization/guardrail boundary; authorization remains outside the model.
- **Failure behavior:** If trusted/untrusted boundaries cannot be maintained or safety validation is unavailable, refuse or return unavailable before provider routing.
- **Required tests:** Direct and indirect hostile instructions, conflicting task content, tenant/actor override attempts, secret/system prompt extraction; verify no unauthorized tool or retrieval call.
- **Dependencies:** Approved use case and prompt ownership, trusted-context contract, retrieval design if applicable, synthetic test cases.
- **Acceptance criteria:** Injection text cannot alter identity, tenant, policy, task scope, or available capabilities; any uncertain control state blocks processing.

### G05 — Input and output validation

- **Purpose:** Constrain requests before processing and prevent malformed/unsafe provider output from reaching users or downstream systems.
- **Threat/risk:** Malformed requests, oversized input, schema confusion, unsafe output, downstream command interpretation.
- **Expected behavior:** Validate versioned request and use-case schemas, size limits and enumerations; validate provider response against an approved output schema; encode/sanitize when rendered; never “repair” malformed output into an authoritative decision.
- **Enforcement point:** Gateway ingress and post-adapter response boundary; host rendering/consumer boundary.
- **Failure behavior:** Reject invalid input before provider call; invalid output becomes controlled failure/refusal, never success-shaped fallback.
- **Required tests:** Missing/wrong-type/oversized/unknown fields; malformed, incomplete, extra-field, and unexpected-type provider outputs; downstream non-dispatch.
- **Dependencies:** Approved contracts, use-case schemas, limits, and host rendering path.
- **Acceptance criteria:** Invalid requests are blocked before external processing; invalid outputs cannot be surfaced as valid or passed to authorization/workflow/connector systems.

### G06 — Sensitive data and classification enforcement

- **Purpose:** Minimize data and ensure a route is eligible for the actual host-assigned data classification.
- **Threat/risk:** Secret/PII exposure, overbroad identity context, or processing under an incorrect classification.
- **Expected behavior:** After host authorization, resolve trusted classification metadata within the authenticated tenant and authorized resource scope before retrieving or releasing subject content into the AI path. Minimize/redact only eligible inputs; evaluate provider eligibility per use case, class, destination, and conditions; never infer a less restrictive class from content.
- **Enforcement point:** Host metadata-only classification check before subject-content retrieval/release to Copilot or the AI Gateway, followed by Gateway pre-route policy/minimization checks before provider request construction/transmission.
- **Failure behavior:** Missing, unknown, conflicting, or untrusted classification blocks subject-content retrieval for AI processing and provider transmission; unavailable classification or minimization checks fail closed. Do not treat blocking provider transmission alone as sufficient.
- **Required tests:** Classification metadata is checked before subject-content retrieval; classification mismatch, absent/unknown/conflicting class, synthetic secret markers, unnecessary attributes, redaction behavior, and no content retrieval/provider call on denial.
- **Dependencies:** Platform classification scheme, approved use-case data map, privacy/security/data-governance review.
- **Acceptance criteria:** Only minimum permitted fields are routed; each supported class has explicit approved routing rules; all deny paths prove no provider call.

### G07 — Restricted-data provider denial

- **Purpose:** Enforce the proposed absolute rule against transmitting Restricted data to an AI provider.
- **Threat/risk:** High-impact disclosure or transfer of data explicitly excluded from provider processing.
- **Expected behavior:** After host authorization, deny Restricted-class AI processing regardless of provider approval, prompt, user request, or human approval. A metadata-only classification lookup may occur, but subject content must not be retrieved/released into Copilot or the AI Gateway for AI processing.
- **Enforcement point:** Host classification gate before subject-content retrieval/release, with a second deterministic Gateway/policy check before provider request construction/transmission.
- **Failure behavior:** Unknown, missing, conflicting classification or unavailable decision is also denied before subject-content retrieval for AI processing; no fallback provider or route.
- **Required tests:** Restricted classification blocks subject-content retrieval and adapter/network calls; attempted downgrade; ambiguous/missing class; zero provider calls.
- **Dependencies:** Confirmed classification mapping and Security/Privacy/Architecture approval of the rule and boundary.
- **Acceptance criteria:** No Restricted payload reaches any provider adapter in negative tests; denial is deterministic and auditable without payload logging.

### G08 — Tenant isolation and trusted context

- **Purpose:** Preserve tenant and actor scope from authenticated host context.
- **Threat/risk:** Cross-tenant disclosure, forged tenant identity, confused-deputy access, or context leakage via cache/retrieval.
- **Expected behavior:** Host supplies trusted immutable tenant/actor context; user text and model output never establish authority; classification metadata lookup, content retrieval, cache, audit, and request scopes remain tenant-bound.
- **Enforcement point:** Host authentication/authorization/data-access layer, protected host-to-Gateway boundary, and any retrieval/cache layer.
- **Failure behavior:** Missing, malformed, conflicting, or caller-controlled context blocks provider routing and data access.
- **Required tests:** Forged/missing tenant and actor context; cross-tenant resource or classification-metadata request; tenant-scoped cache/retrieval; assert denial before subject-content retrieval and provider call.
- **Dependencies:** Host identity and tenant contract, authorization ownership, retrieval/cache design if introduced; maintainer/security approval for boundary changes.
- **Acceptance criteria:** Negative tests demonstrate no foreign-tenant data access or inference and verify trusted context cannot be overridden.

### G09 — Host authorization remains authoritative

- **Purpose:** Keep ordinary platform authorization, deterministic IGA/SoD policy, and workflow approval outside AI.
- **Threat/risk:** AI becoming a policy decision point or bypassing denial/approval requirements.
- **Expected behavior:** Host authenticates and authorizes before AI invocation; AI guardrail decisions can only further deny, never grant host permissions.
- **Enforcement point:** Calling host service before Gateway; no AI-side resource authorization.
- **Failure behavior:** Host authorization denied, missing, or unavailable means no AI request, retrieval, or provider call.
- **Required tests:** Host denial and authorization-service unavailable scenarios; verify no AI call; verify AI “allow” does not override host denial.
- **Dependencies:** Existing host authorization integration and accepted security/architecture decision; do not invent a replacement.
- **Acceptance criteria:** A denied host request cannot reach the AI path; AI policy allows are never interpreted as resource permissions.

### G10 — Fail-closed policy and safety checks

- **Purpose:** Avoid processing when a required guardrail, policy, classification, or validation result is absent or inconclusive.
- **Threat/risk:** Fail-open behavior due to exception, timeout, empty/stale configuration, or safety-service outage.
- **Expected behavior:** Require explicit successful checks before routing; use controlled safe statuses; no fallback to less restrictive policy/provider.
- **Enforcement point:** Gateway orchestration and policy/guardrail decision boundary.
- **Failure behavior:** Error, timeout, stale/malformed policy, or unavailable required check means deny/unavailable and no provider call.
- **Required tests:** Inject exceptions/timeouts/empty config at each check; assert no call and stable safe response.
- **Dependencies:** Approved error/status contract, policy ownership, operational failure semantics.
- **Acceptance criteria:** Every required check has a tested fail-closed branch; no error path returns allow or success-shaped output.

### G11 — Provider response validation and refusal handling

- **Purpose:** Treat provider responses as untrusted and preserve explicit refusal/failure semantics.
- **Threat/risk:** Malformed content accepted, refusal bypassed, provider output claiming approval, or unsafe fallback.
- **Expected behavior:** Treat every provider field and value as untrusted. Validate correlation, response shape, capability use, output bounds, and use-case schema; establish advisory status in the trusted Gateway/orchestrator, never from provider-supplied content or metadata; preserve refusal; do not retry around refusal or silently switch provider.
- **Enforcement point:** Provider adapter normalization and Gateway post-provider validation.
- **Failure behavior:** Malformed/unsafe response becomes controlled failure; no downstream use or action; unavailable validation blocks success.
- **Required tests:** Refusal, malformed/incomplete response, correlation mismatch, unsupported capability, provider-supplied `"advisory": true` ignored or rejected, Gateway-derived advisory status, timeout, rate limit, late response, no-fallback behavior.
- **Dependencies:** Approved provider-neutral interface and any explicit provider approval; no provider selection implied by this plan.
- **Acceptance criteria:** Only validated advisory results can be returned as completed; refusals and errors remain distinguishable; no error body leaks.

### G12 — Safe errors and sensitive logging prevention

- **Purpose:** Provide diagnosable failures without exposing prompts, responses, secrets, or protected identity data.
- **Threat/risk:** Sensitive-data leakage through logs, errors, traces, metrics, and reports.
- **Expected behavior:** Use stable safe error codes and minimal metadata; redact or omit content; restrict access and retention under approved platform controls.
- **Enforcement point:** Gateway/adapter exception mapping and shared logging/telemetry boundary.
- **Failure behavior:** Logging failure must not cause sensitive fallback logging; handling must follow an approved audit/availability policy and must not silently claim success.
- **Required tests:** Seed synthetic secret markers in provider/input errors and assert absent from logs, traces, errors, and reports; test redaction failure behavior.
- **Dependencies:** Platform logging, privacy/retention policy, safe error contract; maintainer approval for logging/retention changes.
- **Acceptance criteria:** Automated leakage tests pass for each output channel; raw prompts/responses are not logged by default.

### G13 — Human review and approval boundaries

- **Purpose:** Keep people and existing IGA workflows accountable for access/security decisions.
- **Threat/risk:** Recommendations presented as approved decisions or human review treated as a substitute for authorization.
- **Expected behavior:** Define review requirements per approved use case; present output as advisory; record review outcome only through approved workflow; human approval cannot override authorization, SoD, or policy.
- **Enforcement point:** Host UI/workflow consuming the recommendation and use-case registration.
- **Failure behavior:** Missing required review path blocks that use case; unreviewed output cannot trigger a state change.
- **Required tests:** Review-required behavior, missing/invalid reviewer outcome, attempts to treat recommendation as approval, no action until ordinary workflow authorizes it.
- **Dependencies:** Product workflow owner, approved use case, host IGA approval workflow, audit contract.
- **Acceptance criteria:** Recommendations affecting access cannot bypass existing approvals; review state is explicit and non-authoritative for authorization.

### G14 — Auditability of guardrail decisions

- **Purpose:** Support accountability and incident investigation with privacy-minimized decision evidence.
- **Threat/risk:** Undetectable denials, policy bypass, unverifiable feature/route decisions, or overcollection of sensitive content.
- **Expected behavior:** Emit approved metadata such as opaque request/correlation refs, outcome/reason code, policy/guardrail version, and status; exclude raw content by default.
- **Enforcement point:** Approved host audit boundary at decision and terminal outcome points.
- **Failure behavior:** Audit outage follows a preapproved fail-closed/availability rule; do not silently drop required evidence or log content as a workaround.
- **Required tests:** Decision events for allow/deny/disabled/error; no sensitive payload; audit unavailable; tenant-scoped audit access and integrity as applicable.
- **Dependencies:** Platform audit schema, retention/access controls, privacy/security approval; maintainer approval before schema/retention changes.
- **Acceptance criteria:** Required outcomes correlate end-to-end using safe metadata; audit failure behavior is documented and tested before enablement.

### G15 — Security and adversarial evaluations

- **Purpose:** Provide bounded evidence for guardrail behavior against defined synthetic threats.
- **Threat/risk:** False confidence from documentation or structural checks being mistaken for behavioral safety evidence.
- **Expected behavior:** Map each synthetic case to explicit reviewed assertions; distinguish pass, fail, skipped, and inconclusive; never treat finite tests as proof or automatic release approval.
- **Enforcement point:** Unit/contract/integration tests and a future approved offline evaluation runner; release decisions remain human-controlled.
- **Failure behavior:** Invalid case, harness error, skipped required assertion, or inconclusive result is not reported as a pass; no provider call unless separately approved.
- **Required tests:** Prompt injection, tenant isolation at host boundary, synthetic secret leakage, unsafe access claims/actions, malformed output, refusal and dependency failure.
- **Dependencies:** Approved output contract/use case, test doubles, synthetic cases, evaluation schema/assertions, test-data privacy review.
- **Acceptance criteria:** Each mandatory assertion has a test and evidence; tests run through approved verification; results state scope and limits; no unapproved score or threshold is introduced.

## 4. Approval dependencies

| Decision/work | Required review or approval | Repository evidence |
|---|---|---|
| Whether AI/Copilot belongs in the six-month MVP; delivery priority | Product and Delivery owners | ADR-008 is Proposed; approvers and date are pending. |
| Default-disabled and non-autonomous product boundary; any future enablement | Product, Security, Architecture; maintainer and controlled release review as applicable | ADR-007 is Proposed; approvers and implementation evidence are pending. |
| Host/Gateway boundary, request/response contract, policy/guardrail ownership | Architecture and Security; maintainer approval for API/contract/security-boundary changes | Gateway and policy documents are Proposed. |
| Trusted tenant context, host authorization, SoD and workflow integration | Security and Architecture; maintainer approval before auth/tenant/security changes | Root governance explicitly requires prior approval. |
| Classification mapping, Restricted-data denial, minimization/redaction | Security, Privacy/Data Governance, Architecture; Product for use-case scope | Proposed policy cannot replace the platform classification authority. |
| Provider/model, destination, retention, region, processing terms | Product, Security, Privacy/Legal, Architecture, Operations as applicable | No provider is selected or approved by these documents. |
| Logging, audit schema, retention and failure semantics | Security, Privacy, Operations, Architecture; maintainer approval for schema/retention changes | `ai/audit/` is placeholder-only. |
| Dependencies, runtime language/framework, CI workflow or security gate changes | Maintainer approval; relevant Architecture/Security/Operations review | Root governance requires prior approval for dependencies, tooling, and CI. |

No Proposed ADR or policy is an approval. Do not edit ADR status as part of implementation unless the authorized decision owners complete the required process.

## 5. Prioritized implementation plan

All implementation filenames below are **conditional planning candidates**, not approved architecture or a commitment to Python. The repository has no selected AI runtime language or implemented host service. Confirm the existing host language, package layout, and test runner before creating code. If they differ, revise the candidate filenames through review rather than introducing a new runtime or dependency.

### P0 — Approval and architecture dependencies

1. **Approve or explicitly defer AI in MVP.**
   - **Paths:** `docs/engineering/adr/ADR-007-decision-topic.md`, `docs/engineering/adr/ADR-008-decision-topic.md`, and the authoritative six-month plan if maintained outside `docs/`.
   - **Acceptance:** Named Product/Security/Architecture approvers resolve ADR-007 and Product/Delivery resolve ADR-008; first use case, owner, user, scope, and acceptance criteria are recorded. Until then, all runtime feature states stay disabled and no AI runtime is started.
2. **Approve the host trust boundary and guardrail ownership.**
   - **Paths:** `ai/gateway/CONTRACTS.md`, `ai/policies/POLICY_ENGINE.md`, `ai/guardrails/README.md`; any approved contract amendment is separately reviewed.
   - **Acceptance:** Documented decision identifies host authorization owner, trusted tenant/actor context source, guardrail enforcement locations, classification authority, Restricted-data behavior, and safe failure semantics. Maintainer approval is obtained before any API/auth/tenant/security contract change.
3. **Approve implementation technology and operational dependencies.**
   - **Paths:** `ai/DEVELOPMENT.md`, the approved host service build/test configuration, and `ai/guardrails/`.
   - **Acceptance:** Existing host language, test convention, configuration/feature-flag mechanism, audit/logging boundary, and rollback owner are identified; any dependency, CI, or operational change has explicit maintainer approval.

### P1 — Essential security guardrails

1. **Implement default-disabled routing and advisory-only use-case controls.**
   - **Candidate paths:** `ai/guardrails/feature_policy.py`, `ai/guardrails/capability_policy.py`, `ai/gateway/entrypoint.py`; actual host integration path must be named after P0.
   - **Acceptance:** No route executes while disabled; only registered observe/reason/recommend operations can proceed; output cannot represent authorization, approval, or action.
   - **Behavioral tests required with implementation:** Disabled/missing/invalid flag prevents retrieval and provider calls; unknown capability is rejected; provider-supplied advisory fields cannot establish trusted status; no host action can result.
2. **Implement deterministic input/classification/context controls.**
   - **Candidate paths:** `ai/guardrails/input_validation.py`, `ai/guardrails/data_policy.py`, `ai/guardrails/trusted_context.py`.
   - **Acceptance:** Schema and size bounds are enforced; tenant/actor context is host-derived; host authorization remains authoritative; trusted classification is checked before subject-content retrieval into the AI path; unknown/missing/conflicting classification and Restricted data are rejected before that retrieval and before adapter invocation; only minimized approved context is passed onward.
   - **Behavioral tests required with implementation:** Forged/cross-tenant context and host denial are rejected before subject-content retrieval; trusted classification metadata is checked first; Restricted/unknown/missing/conflicting classification prevents subject-content retrieval for AI processing and provider calls; invalid input and unavailable checks fail closed.
3. **Implement provider-output, refusal, and safe-error controls.**
   - **Candidate paths:** `ai/guardrails/output_validation.py`, `ai/guardrails/safe_errors.py`, `ai/gateway/response_validation.py`.
   - **Acceptance:** Responses must match approved schema and advisory boundary; refusal remains explicit; malformed output, unavailable validation, and provider error produce controlled failure with no fallback or downstream action; sensitive values are not exposed in errors/logs.
   - **Behavioral tests required with implementation:** Provider output and advisory claims are treated as untrusted; malformed/unsafe output and refusal are handled per contract; unavailable validation fails closed; errors and logs do not disclose synthetic sensitive markers; no downstream action occurs.
4. **Implement human-review and audit integration only against approved host contracts.**
   - **Candidate paths:** `ai/guardrails/review_policy.py`, `ai/audit/guardrail_events.py`; host workflow/audit paths are determined at P0.
   - **Acceptance:** Required review is represented in the existing workflow; audit records only approved minimal metadata; no AI-generated result bypasses authorization, SoD, or approval.
   - **Behavioral tests required with implementation:** Missing required review blocks completion/action; audit outcomes are correlated without sensitive content; audit outage follows its approved behavior; no AI result bypasses host authorization or SoD.

### P2 — Integration and behavioral tests

1. **Unit tests for each deterministic guardrail.**
   - **Candidate path:** `tests/unit/test_ai_guardrails.py`.
   - **Acceptance:** Covers enabled/disabled states, allowed/disallowed capabilities, invalid request/output, classifications, Restricted data, safe errors, and fail-closed exceptions/timeouts.
2. **Gateway and host contract tests.**
   - **Candidate path:** `tests/contract/test_ai_guardrails_gateway_contract.py`.
   - **Acceptance:** Host denial prevents Gateway/provider invocation; trusted context cannot be overridden; refusals and failures preserve their contract; no autonomous action operation exists.
3. **Tenant-isolation integration tests.**
   - **Candidate path:** `tests/tenant-isolation/test_ai_guardrails_tenant_isolation.py`.
   - **Acceptance:** Cross-tenant requests and forged IDs are denied before retrieval/provider call; synthetic cache/audit scoping, if present, cannot cross tenants.
4. **Adversarial and failure evaluations using synthetic fixtures.**
   - **Candidate path:** `tests/integration/test_ai_guardrails_adversarial.py` and the approved evaluation runner/case assertion files under `ai/evaluations/`.
   - **Acceptance:** Prompt injection, marker leakage, unsafe access recommendations, malformed output, refusal, timeout, and audit failure have explicit assertions; skipped/inconclusive is never reported as pass. No provider-backed run occurs without separate approval.
5. **Verification integration.**
   - **Candidate paths:** `Makefile`, `.github/workflows/verify.yml`.
   - **Acceptance:** After maintainer approval, the canonical verification command includes relevant unit/contract checks and fails on failure; CI remains offline unless a separate provider-evaluation approval exists.

### P3 — Advanced protections and improvements

1. **Expand red-team corpus and regression/version tracking.**
   - **Candidate paths:** `ai/evaluations/cases/`, `ai/evaluations/`, `tests/integration/`.
   - **Acceptance:** Additional cases are synthetic, reviewed, uniquely identified, versioned, and mapped to deterministic assertions; historical outcomes are retained only under approved privacy/retention rules.
2. **Add controlled operational telemetry and incident procedures.**
   - **Candidate paths:** `ai/audit/`, `ai/guardrails/README.md`, approved operations documentation.
   - **Acceptance:** Alert/stop conditions, ownership, safe diagnostics, retention, and rollback are documented and tested without logging raw prompt/response data.
3. **Consider model-assisted or provider-backed evaluations only after separate approval.**
   - **Candidate paths:** `ai/evaluations/`, approved provider adapter/configuration, CI only if separately approved.
   - **Acceptance:** Provider, data-processing, security, privacy, architecture, and product approvals are recorded; evaluation uses only authorized data, has bounded execution and human review, and cannot enable product Copilot or automatically approve release.

## 6. Implementation checklist

### Before runtime work

- [ ] Resolve ADR-007 and ADR-008 through their named decision owners.
- [ ] Identify the first MVP-eligible use case and acceptance criteria.
- [ ] Identify the host service, runtime language, test runner, authorization and tenant-context boundary.
- [ ] Approve the request/response contract and guardrail ownership.
- [ ] Approve data-classification mapping and provider restrictions, including Restricted-data denial.
- [ ] Approve audit, safe-error, retention, feature-flag, and rollback behavior.
- [ ] Obtain maintainer approval for any auth, tenant, API, dependency, build, CI, logging, or security-boundary change.

### Before any AI feature enablement

- [ ] Default-disabled behavior is proven at each host/Gateway entry point.
- [ ] Host authorization, tenant scope, and SoD/workflow decisions remain authoritative.
- [ ] No autonomous provisioning, access approval, or privileged execution path exists.
- [ ] Input, classification, minimization, output, refusal, and failure handling are implemented and tested.
- [ ] Human review and audit controls are integrated with approved platform boundaries.
- [ ] Synthetic adversarial tests and failure tests pass; limitations and residual risks are recorded.
- [ ] Provider/model and data-processing approvals exist if any external route is used.
- [ ] Product, Security, Privacy, Architecture, Operations, and Delivery approvals required for the selected use case are recorded.
- [ ] Human-controlled release and rollback are approved; finite evaluation results are not treated as proof of safety.

## 7. Exact next task

**P0 next task: obtain and record the Product/Delivery decision on whether an AI use case belongs in the six-month MVP, and resolve the related ADR-007/ADR-008 approval dependencies before runtime implementation.** Until that decision and the host/security boundary approvals are established, do not implement or enable product guardrails. The current context-value validation defect in the offline catalog validator is a separate task and does not establish runtime guardrail readiness.
