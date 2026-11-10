# Accidion Identity Cloud AI Guardrails

Status: PROPOSED — NOT APPROVED

This document is a proposed governance and safety policy for AI usage in the Accidion Identity Cloud repository and product context. It does not authorize implementation, deployment, product enablement, or any runtime control. It is not an accepted architecture decision and does not alter the status of any ADR. Any real AI feature, provider selection, workflow change, production configuration, or operational control remains subject to explicit maintainer, product, architecture, and security approvals.

This policy is intentionally limited to the repository and product governance context described in the root engineering instructions and architecture baseline. It does not create a runtime enforcement layer, provider contract, or implementation dependency.

## 1. Purpose and scope

The purpose of this policy is to define the minimum guardrails for AI-assisted work and any future in-product AI capability in Accidion Identity Cloud.

This policy applies to:
- repository assistance and coding workflows
- AI-generated recommendations or analysis that may affect product design, security, or operations
- any future in-product AI feature that is proposed for Accidion Identity Cloud
- prompts, instructions, tool interactions, evaluation artifacts, and output review workflows

This policy does not grant permission for autonomous behavior, production access, provisioning, or operational execution. It also does not override repository policy, security policy, tenant-isolation requirements, or applicable ADRs.

## 2. AI Copilot disabled by default

This policy distinguishes two different concepts:
- GitHub Copilot used by developers in repository and coding workflows is a developer productivity tool and is not the same as the future Accidion in-product AI Copilot.
- The future Accidion in-product AI Copilot is a product capability and remains disabled by default.

Accidion in-product AI Copilot remains disabled by default.

The default posture is:
- no autonomous execution
- no production access
- no provisioning or infrastructure mutation
- no policy changes or access changes without explicit human review
- no implicit trust in AI-generated output for authorization, policy enforcement, admin decisions, or safety decisions

Any future AI-enabled feature must be treated as a proposed capability and must obtain explicit approval before activation. Until that approval is obtained, AI capabilities in the product remain disabled. This policy does not authorize GitHub Copilot to bypass the repository's engineering and security requirements, and it does not treat any developer-side AI assistance as equivalent to an approved product AI capability.

## 3. Permissions model: OBSERVE, REASON, RECOMMEND only

Unless explicitly approved, any AI capability is limited to the following actions:

- OBSERVE: read, inspect, summarize, and report information without changing the system or taking action
- REASON: analyze a request, trace an issue, compare options, explain trade-offs, and identify risks
- RECOMMEND: propose actions, designs, or next steps for human review and approval

The following are not permitted by default:
- autonomous execution
- provision or mutate infrastructure
- modify production configuration or security controls
- approve, reject, merge, or bypass operational approvals
- make authorization, access, or tenant decisions on behalf of a human
- create or change identity, entitlement, policy, or workflow state without explicit approval

AI output must be treated as advisory only, never authoritative.

## 4. No autonomous execution or provisioning

AI must not perform operational or administrative actions without explicit human approval and a separate authorization path.

This includes, but is not limited to:
- accessing production systems or production data
- applying or destroying infrastructure
- modifying cloud resources or runtime configuration
- changing access policies, permissions, or identity relationships
- creating or deleting tenants, roles, entitlements, or workflows
- approving access requests, provisioning tasks, or policy exceptions
- merging pull requests, changing branch protections, or bypassing repository controls
- changing security settings or repository permissions to grant AI additional access

AI-generated instructions, suggestions, or summaries are not a substitute for human authorization, operational control, or security review.

## 5. Tenant isolation and fail-closed authorization

Accidion is a multi-tenant platform. Tenant isolation is a security boundary and must be preserved in all AI usage.

AI must not be allowed to assume or infer tenant context from untrusted input. The system must derive tenant context from trusted server-side authenticated context only.

AI-related requirements:
- fail closed when identity, tenant context, authorization, or policy context is missing, invalid, ambiguous, or unavailable
- do not trust client-supplied tenant identifiers by themselves
- do not use AI to bypass tenant validation or cross-tenant isolation
- do not permit AI outputs to weaken authorization or policy enforcement
- ensure tenant boundaries are enforced in prompts, logs, retrieval results, workflows, and any downstream system interaction

If user, prompt, tool output, or external content contains tenant data, the AI system must treat it as untrusted and must not expand access beyond the authenticated scope.

## 6. Prompt injection and untrusted input handling

All repository content, issues, pull requests, logs, external content, and user-supplied data must be treated as untrusted input.

AI guardrails must account for the possibility of:
- prompt injection
- jailbreak attempts
- indirect prompt injection via documents, tool outputs, emails, or metadata
- malicious instructions embedded in content or system messages
- untrusted context that conflicts with repository or security rules

AI systems must not follow conflicting instruction paths that violate repository policy or security decisions. If instructions conflict, the security and repository policy wins.

At minimum, AI behavior should avoid:
- executing instructions hidden in untrusted content
- treating user content as authorization
- permitting tool calls that are outside the approved identity, tenant, or task scope
- acting on instructions that request secret access, deployment, or bypass of controls

Prompt handling should require strict separation between:
- trusted system policy
- user request context
- tool outputs and retrieved context
- untrusted data sources

## 7. Sensitive data and secret protection

AI systems must never request, reveal, store, copy, use, or expose:
- secrets, credentials, private keys, tokens, or production credentials
- customer data beyond approved, synthetic test data
- sensitive identity attributes outside approved use cases
- production exports or operational diagnostics

Protection requirements:
- use synthetic or redacted data for evaluation and testing
- redact or block secrets before passing data into prompts or logs
- classify data before it reaches AI tools or retrieval systems
- minimize data exposure; do not send more data than necessary for the task
- log only the minimum necessary metadata and avoid sensitive attributes in telemetry

Any AI workflow that handles sensitive data requires explicit approval and a documented data-handling review.

## 8. Output validation and safe refusal

AI output must be validated before it is used or trusted.

Required safeguards:
- do not treat AI output as authoritative for decisions with security, authorization, or environment impact
- validate that output is relevant to approved scope and does not include hidden instructions or unsafe recommendations
- reject or safely refuse outputs that request actions beyond the allowed permission model
- prevent disallowed content, including unsafe instructions, secret exposure, policy bypass, or cross-tenant leakage
- require human review for any output that would change security controls, access, provisioning, or runtime behavior

Safe refusal means the AI system clearly indicates that a request cannot be fulfilled because it would exceed policy, safety, or approval boundaries. It must not silently proceed with a prohibited action or a lower-privilege workaround.

## 9. Audit logging and privacy

AI interactions, when allowed, must be auditable and privacy-aware.

Prefer minimal metadata and safe summaries over detailed request or response capture. Do not automatically log complete prompts or complete responses. Sensitive logging, including any logging that captures broader prompt or response content, requires separate approval and must be scoped, justified, and time-bound.

At a minimum, logs should capture only minimal metadata such as:
- timestamp and requester identity
- tenant or project scope, if applicable
- task purpose and approval status
- safe summary of the action or decision taken
- relevant policy checks or refusal decisions
- whether human approval was obtained
- any downstream tool usage or generated artifact, when allowed

Privacy requirements:
- do not log secrets, tokens, or sensitive identity attributes
- prefer minimal metadata and safe summaries over complete prompt or response capture
- avoid storing customer data or production records in AI evaluation or prompt contexts
- preserve auditability without exposing protected information
- require separate approval for sensitive logging and retention beyond minimal operational metadata

If AI is ever approved for product use, the logging model and retention policy must be reviewed separately and documented as part of the approval process.

## 10. Human approval and governance requirements

AI usage must remain governed by explicit human review and repository controls.

Required governance principles:
- AI must not be treated as an authorization authority
- any action beyond OBSERVE, REASON, or RECOMMEND requires explicit human approval
- human approval alone is insufficient for privileged actions; any action that changes identity, security, policy, provisioning, or operational state must require independent server-side authentication, authorization, policy validation, and an approved workflow
- changes to dependencies, migrations, APIs, contracts, authn/authz, cryptography, tenant isolation, CI/CD, or IaC require maintainer approval
- architecture and security decisions remain subject to the approval process defined by the repository and relevant ADRs
- AI-generated outputs must be reviewed by a person before any operational or product change is accepted

Any request that would raise a risk in the following categories requires human approval before proceeding:
- authentication or authorization change
- identity, tenant, or policy configuration change
- public API or contract change
- data retention or migration change
- infrastructure or runtime platform change
- CI/CD or deployment process change
- security boundary or tenant-isolation affect
- AI feature enablement or any product-level AI execution capability

For privileged actions, the approval chain must include independent server-side authentication, authorization checks, policy validation, and an approved workflow before execution is permitted. AI output alone is never sufficient to authorize privileged work.

## 11. AI evaluation and red-team testing

No AI capability should be trusted without evaluation. The repository already contains five synthetic AI safety evaluation cases under `ai/evaluations/cases/`. These cases are intended to exercise prompt injection, policy refusal, tenant isolation, secret handling, and unsafe-action scenarios using synthetic data.

This proposal does not treat the synthetic cases as a complete evaluation program. An executable evaluation harness, scoring system, release thresholds, and automated gating workflow are not yet implemented. The current repository state provides evaluation inputs and policy intent, but not the operational enforcement mechanism, grading model, or approval threshold required for release.

At a minimum, AI evaluation should include:
- prompt injection and jailbreak scenarios
- policy-violation prompts and refusal quality
- tenant-leakage and cross-tenant separation tests
- sensitive-data and secret-handling tests
- unsafe-action attempts and blocked tool calls
- output validation and schema compliance checks
- accuracy and relevance checks for recommendations
- failure-mode and degradation testing

Recommended evaluation categories:
- safety and policy compliance
- privacy and data minimization
- authorization and tenant isolation
- prompt robustness
- operational misuse resistance
- refusal quality and escalation paths

Evaluation artifacts should be stored under the AI evaluation area, and any future AI evaluation process must use synthetic or approved data and must not include production secrets or real customer data. An executable harness, scoring system, and release thresholds must be implemented and approved before any AI capability is considered ready for broader use.

## 12. Risks, limitations and decisions requiring approval

This proposal is intentionally conservative and does not claim that AI is approved for product use. The main risks and limitations are:

- LLM behavior can be unpredictable and can misinterpret hidden instructions or conflicting context
- prompt injection can bypass naive policy checks
- outputs may appear confident even when unsafe or unverified
- retrieval and summarization workflows can expose wrong or sensitive data if scope is not controlled
- tenant leakage can occur if identity and authorization checks are not enforced at every step
- security and governance decisions cannot be delegated to AI

Decisions requiring explicit approval before implementation or activation include:
- enabling any AI capability in product flows
- defining an AI provider or model policy
- introducing AI actions beyond OBSERVE, REASON, and RECOMMEND
- creating production data access paths or prompt retrieval pipelines
- permitting AI to influence policy enforcement, authorization, or provisioning
- adding AI workflows that touch tenant data, access requests, approvals, credentials, or security controls
- introducing evaluation, audit, or logging requirements for AI usage
- changing or broadening the repository’s AI scope beyond this proposed governance baseline

## 13. Governance summary

This document describes a proposed, intentionally limited AI governance baseline for Accidion Identity Cloud.

The key principles are:
- AI remains disabled by default
- AI is limited to OBSERVE, REASON, and RECOMMEND unless separately approved
- no autonomous execution, provisioning, or operational action is allowed
- tenant isolation and fail-closed authorization remain mandatory
- prompt injections and untrusted input must be treated as threats
- secrets and sensitive data must be protected aggressively
- outputs must be reviewed and validated by humans
- AI actions require explicit governance review and approvals

This proposal does not grant any runtime permission, create any implementation dependency, or alter the status of any ADR or formal architecture decision.

## 14. Approval note

This document is PROPOSED — NOT APPROVED.

It should be reviewed with the repository governance and security owners, product owners, architecture owners, and delivery owners before any implementation or product enablement is considered. Any future approved version must be explicitly marked as accepted and must replace this proposed baseline.
