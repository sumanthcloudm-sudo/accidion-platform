# Accidion AI Module Development Guide

## 1. Purpose and authority

This guide defines development expectations for code and configuration under `ai/`. It supplements the root `AGENTS.md`, `RULES.md`, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, accepted ADRs, and `ai/SAFETY.md`. Higher-level repository and security requirements take precedence.

This guide does not select a programming language, framework, provider, model, database, or test library. Follow the technologies and conventions actually present in the repository and obtain approval before introducing dependencies or changing architecture.

## 2. Before implementation

For each task:

1. Confirm the use case, owner, user, acceptance criteria, and MVP eligibility.
2. Confirm whether the AI feature is approved and how it is feature-flagged; AI Copilot is disabled by default.
3. Identify data categories, tenant boundary, actor context, external destinations, retention, and audit requirements.
4. Read relevant ADRs and inspect existing interfaces, code, tests, and build configuration.
5. Identify whether the change affects provider contracts, prompts, policy, guardrails, audit, privacy, or security.
6. Request approval for changes listed in root `AGENTS.md` and `ai/AGENTS.md`.

Do not implement a proposed architecture as if it were already an approved technical decision.

## 3. Design and coding practices

- Keep business-domain logic independent of provider-specific SDKs and response formats.
- Route model calls through the approved integration boundary; do not add hidden direct provider calls from unrelated services.
- Use explicit request/response schemas and validate both sides of the model boundary.
- Keep prompts in reviewed, versioned locations with a clear purpose, owner, and expected output format.
- Treat prompt templates and retrieved content as untrusted input. Never place secrets or authorization instructions in prompts.
- Keep tenant and actor context explicit in trusted application code. Never ask the model to establish or validate its own authority.
- Apply least-data principles. Send only fields required for the approved use case.
- Use bounded timeouts, cancellation where supported, rate limits, and controlled retries. Retries must not create duplicate state changes.
- Handle provider refusal, timeout, rate limiting, malformed output, and unavailable dependencies explicitly.
- Make advisory output distinguishable from deterministic platform decisions and completed operations.
- Avoid logging raw prompts, responses, identity records, or sensitive attributes. Log safe identifiers and outcome metadata according to approved policy.
- Use configuration and approved secret-management mechanisms; never commit credentials or local secret files.
- Document model/provider assumptions, limitations, fallback behaviour, feature flags, operational signals, and data handling.

## 4. Required test coverage

Choose tests based on the risk and behaviour being changed. Relevant coverage may include:

### Software tests

- Request/response schema validation.
- Gateway routing and provider-adapter contract tests.
- Authorization and tenant-context enforcement.
- Input minimisation and redaction.
- Error, timeout, rate-limit, retry, and cancellation behaviour.
- Feature-disabled behaviour and safe defaults.
- Audit event generation without sensitive payload leakage.
- Integration compatibility with calling IGA services.

### AI evaluations

- Expected task quality against reviewed examples.
- Unsupported claims, uncertainty, and refusal behaviour.
- Prompt-injection and malicious retrieved-content cases.
- Sensitive-data disclosure and cross-tenant leakage attempts.
- Unsafe recommendations and attempts to trigger prohibited actions.
- Output schema adherence and malformed responses.
- Regression checks across prompt/provider/model version changes.

Evaluation datasets must be synthetic or otherwise approved. Do not add customer identity data, credentials, or production records to fixtures or evaluation corpora without explicit data-governance approval.

## 5. Pull-request expectations

A change to this module should include, as applicable:

- Problem statement and approved use case.
- Design and relevant ADR references.
- Data categories and tenant-boundary analysis.
- Provider/model and prompt version impact.
- Guardrail and failure-mode behaviour.
- Tests and evaluation results, including known limitations.
- Audit, privacy, retention, and operational implications.
- Feature-flag and rollback approach.

Keep pull requests focused. Do not combine unrelated refactoring or dependency upgrades with an AI feature unless explicitly approved.

## 6. Verification

- Run focused tests for the changed code.
- Run relevant contract, security, tenant-isolation, and evaluation checks.
- Run `make verify` where available, as required by repository guidance.
- Report the exact commands run and their outcomes.
- Identify checks not run and explain why.
- Never report a test, evaluation, security review, or compliance check as passed unless it actually ran and passed.

## 7. Dependency and architecture control

Request maintainer approval before adding or upgrading provider SDKs, AI frameworks, model clients, vector/search systems, databases, queues, caches, observability packages, or evaluation tools. Also request approval before changing provider contracts, persistence, deployment, CI, infrastructure, public APIs, event formats, or security controls.

## 8. Implementation status

These practices are development guidance. They do not mean that a build pipeline, AI evaluation harness, provider integration, or automated guardrail is already present. Verify the repository before relying on any such capability.
