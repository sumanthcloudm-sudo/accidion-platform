# ADR-007: AI Copilot disabled by default and non-autonomous

- **Status:** Proposed — pending product, security, and architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Product owner / security owner (to be assigned)
- **Scope:** In-product Accidion AI Copilot

## Context

The architecture baseline states that the in-product AI Copilot is disabled by default and, if approved, is limited to observe, reason, and recommend. The repository rules additionally state that AI Copilot remains disabled by default with no autonomous execution.

## Proposed decision

Keep the in-product Accidion AI Copilot disabled by default. Any future approved capability is limited to observe, reason, and recommend. The Copilot must not autonomously execute access changes, provisioning, approvals, policy changes, or other actions. Any expansion beyond these boundaries requires a separate explicit review and approval.

## Alternatives considered

- **Autonomous execution:** Not proposed and not permitted by the current baseline.
- **Enablement by default:** Rejected; default state remains disabled.

## Consequences and constraints

- Feature flags and access controls must preserve the disabled default.
- AI-generated output must not be treated as authorization or as a substitute for required human decisions.
- Provider selection, data handling, prompt security, evaluation, retention, and user disclosures require separate review before any feature is enabled.
- This ADR concerns the product's in-platform Copilot; it does not grant a repository coding assistant permission to manage or change the repository autonomously.
- No AI service is enabled or deployed by this document.

## Approval

- **Product approver:** Pending
- **Security approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
