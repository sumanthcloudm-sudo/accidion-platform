# Accidion AI: Implementation Plan Reference Guide
## Mapping Phases to Existing Design Documents

This document cross-references each phase of the implementation plan to the existing design documentation in the repository. Use this to understand where each requirement comes from and which existing documents to follow during implementation.

---

## Design Documents by Component

### Core Architecture & Security

**ai/ARCHITECTURE.md**
- Defines: Trust model, request flow, threat model, isolation boundaries
- Used by: All 8 phases
- Key sections:
  - Lines 34-80: Trust boundaries (platform authoritative, user input untrusted)
  - Lines 85-120: Isolation levels (host auth → gateway policy → guardrails → provider)
  - Lines 130-160: Data flow and classification
- Implementation impact:
  - Phase 1: TrustedContext must follow trust model
  - Phase 2: Gateway must enforce isolation levels
  - Phase 4: Guardrails must implement classification rules
  - Phase 8: Audit events must preserve trust boundaries

**ai/SAFETY.md**
- Defines: Security requirements, prohibited behaviors, disabled-by-default principle
- Used by: Phases 1, 5, 7, 8
- Key sections:
  - Lines 40-60: Product capability boundary (observe/reason/recommend only)
  - Lines 70-90: Tenant isolation and data protection
  - Lines 100-120: Provider controls and output safety
  - Lines 130-150: Audit and compliance requirements
- Implementation impact:
  - Phase 1: Feature flags must enforce disabled-by-default (Section 3)
  - Phase 4: Guardrails must prevent autonomous decisions
  - Phase 5: Policy engine must fail-closed
  - Phase 8: Audit logging must capture all decisions

---

## Gateway & Request/Response

**ai/gateway/CONTRACTS.md**
- Defines: Provider-neutral request/response schemas, error categories
- Used by: Phases 1, 2, 3, 4, 5
- Key sections:
  - Lines 30-50: Request envelope schema (operation, user_input, trusted_context, classification)
  - Lines 55-85: Response envelope schema (status, reasoning, output, metadata)
  - Lines 90-130: Error categories and codes
  - Lines 140-160: Audit event fields
- Implementation impact:
  - Phase 1: Create contract types and JSON schemas
  - Phase 2: Validate all requests against request envelope schema
  - Phase 2: Normalize all responses to response envelope schema
  - Phase 3: Provider adapters must return response envelope format
  - Phase 4: Guardrails must operate on request/response envelopes
  - Phase 5: Policy engine must operate on classification field from request

---

## Provider Integration

**ai/providers/PROVIDER_INTERFACE.md**
- Defines: How provider adapters integrate with gateway
- Used by: Phases 1, 3, 8
- Key sections:
  - Lines 50-80: Adapter interface (methods: observe(), reason(), recommend())
  - Lines 85-110: Request/response format (matches CONTRACTS.md)
  - Lines 115-140: Timeout handling (max_wait_ms, retry semantics)
  - Lines 145-170: Capability declaration
  - Lines 175-200: Error handling and refusal patterns
- Implementation impact:
  - Phase 1: Test double adapter must implement this interface
  - Phase 3: Claude and GPT adapters must implement this interface
  - Phase 3: Timeout and retry logic must match specification
  - Phase 8: Capability registry query API

---

## Data Protection & Classification

**ai/policies/POLICY_ENGINE.md**
- Defines: Eligibility rules, data classification, provider approval requirements
- Used by: Phases 1, 4, 5
- Key sections:
  - Lines 50-80: Supported operations (OBSERVE, REASON, RECOMMEND)
  - Lines 85-130: Data classification (Restricted, Internal, Public)
  - Lines 135-170: Classification rules and enforcement
  - Lines 175-200: Restricted data blocking (fail-closed)
  - Lines 205-240: Provider approval requirements
- Implementation impact:
  - Phase 1: Define Classification type in contracts
  - Phase 4: Guardrails must enforce classification rules (no Restricted to provider)
  - Phase 5: Policy engine must evaluate eligibility per operation
  - Phase 5: Policy engine must block Restricted data before provider call

**ai/guardrails/GUARDRAILS_IMPLEMENTATION_PLAN.md**
- Defines: 15 specific guardrail controls
- Used by: Phases 4, 7
- Key sections:
  - Lines 40-80: Guardrail coverage matrix (design vs. implementation)
  - Lines 90-200: Specification for all 15 guardrails:
    1. Input size validation
    2. Encoding validation
    3. Prompt injection detection
    4. Command injection detection
    5. XSS pattern detection
    6. Structured input validation
    7. Output schema validation
    8. Output size limits
    9. JSON format validation
    10. Output safety scanning
    11. PII detection and redaction
    12. Credential detection and redaction
    13. Secret key detection
    14. Classification-based output filtering
    15. Data lineage tracking
- Implementation impact:
  - Phase 4: Implement all 15 in specified order (fail-fast sequencing)
  - Phase 7: Verify each guardrail with synthetic test cases

---

## Evaluation & Safety Validation

**ai/evaluations/HARNESS_DESIGN.md**
- Defines: Architecture for evaluation runner
- Used by: Phase 7
- Key sections:
  - Lines 50-80: High-level architecture (case discovery, execution, reporting)
  - Lines 85-120: Case discovery flow (scan directory, parse JSON, validate)
  - Lines 125-160: Execution engine (run case against provider, collect results)
  - Lines 165-200: Result aggregation and reporting
- Implementation impact:
  - Phase 7: Evaluation harness must follow this architecture
  - Phase 7: Case loader must discover and validate all 5 cases
  - Phase 7: Case executor must handle all operations (OBSERVE, REASON, RECOMMEND)
  - Phase 7: Safety report must aggregate results per HARNESS_DESIGN

**ai/evaluations/cases/*.json** (5 files)
- Defines: Synthetic test cases for safety validation
- Used by: Phases 4, 7
- Files:
  1. prompt-injection.json – Test injection detection
  2. tenant-isolation.json – Test tenant boundary enforcement
  3. sensitive-data-leakage.json – Test PII redaction
  4. unsafe-access-recommendation.json – Test dangerous recommendation blocking
  5. invalid-output.json – Test invalid response rejection
- Implementation impact:
  - Phase 4: Use these cases to verify guardrails work (integration tests)
  - Phase 7: Case executor must run all 5 cases and generate safety report
  - Phase 8: Regression testing must compare results to baseline

---

## Audit & Compliance

**ai/audit/AI_AUDIT_EVENT_CONTRACT.md**
- Defines: Audit event schema and compliance requirements
- Used by: Phases 1, 4, 5, 8
- Key sections:
  - Lines 40-80: Audit event schema
  - Lines 85-130: Events to audit (request, guardrail, provider, response, feature flag)
  - Lines 135-170: Privacy-aware logging (never log raw content)
  - Lines 175-210: Trace ID correlation across components
  - Lines 215-240: Immutability and retention requirements
- Implementation impact:
  - Phase 1: Feature flag checks must audit
  - Phase 4: Each guardrail trigger must emit audit event
  - Phase 5: Policy engine decisions must audit
  - Phase 8: Gateway and provider calls must audit, full trace logged

---

## Approved Decision Records (ADRs)

**docs/engineering/adr/ADR-007-*.md** (Proposed)
- Status: PROPOSED (not approved – blocks Phase 1)
- Defines: AI Copilot disabled-by-default principle
- Impact: Feature flags (Phase 1) must implement this decision
- Approval required before: Phase 1 can start

**All 10 ADRs** (ADR-001 through ADR-010)
- Status: All PROPOSED (none approved yet)
- Use: Reference for design constraints and architectural direction
- Approval required: Before production deployment (Phase 8)
- Implementation impact: Code must comply with all approved ADRs

---

## Implementation Checklists: When to Consult Each Document

### Phase 1 Checklist: Core Foundation
- ✅ Read: ARCHITECTURE.md (lines 34-80: trust model)
- ✅ Read: SAFETY.md (lines 40-60: disabled-by-default)
- ✅ Read: CONTRACTS.md (lines 30-160: all schemas)
- ✅ Reference: ADR-007 (feature flags principle)
- ✅ Confirm: Feature flags implement Section 3 of SAFETY.md

### Phase 2 Checklist: Gateway
- ✅ Read: ARCHITECTURE.md (lines 85-120: isolation levels)
- ✅ Read: CONTRACTS.md (lines 30-160: request/response validation)
- ✅ Read: POLICY_ENGINE.md (lines 50-80: supported operations)
- ✅ Reference: PROVIDER_INTERFACE.md (lines 115-140: timeout semantics)
- ✅ Confirm: Gateway enforces all isolation levels

### Phase 3 Checklist: Provider Adapters
- ✅ Read: PROVIDER_INTERFACE.md (entire document)
- ✅ Read: CONTRACTS.md (lines 90-130: error categories)
- ✅ Reference: SAFETY.md (lines 100-120: provider controls)
- ✅ Confirm: Adapters implement all interface methods
- ✅ Confirm: Error mapping covers all categories

### Phase 4 Checklist: Guardrails
- ✅ Read: GUARDRAILS_IMPLEMENTATION_PLAN.md (entire document)
- ✅ Read: ARCHITECTURE.md (lines 130-160: data flow and classification)
- ✅ Read: POLICY_ENGINE.md (lines 85-130: data classification)
- ✅ Reference: All 5 evaluation cases (synthetic test data)
- ✅ Confirm: All 15 guardrails implemented per specification
- ✅ Confirm: Injection case passes detection

### Phase 5 Checklist: Policy Engine
- ✅ Read: POLICY_ENGINE.md (entire document)
- ✅ Read: SAFETY.md (lines 70-90: tenant isolation)
- ✅ Reference: CONTRACTS.md (lines 30-50: classification field)
- ✅ Confirm: Eligible use cases defined
- ✅ Confirm: Classification rules enforced
- ✅ Confirm: Restricted data never sent to provider

### Phase 6 Checklist: Prompt Registry
- ✅ Read: CONTRACTS.md (audit event fields)
- ✅ Reference: AI_AUDIT_EVENT_CONTRACT.md (audit requirements)
- ✅ Confirm: Versioning immutable
- ✅ Confirm: All changes audited
- ✅ Confirm: No re-write of history (rollback creates new version)

### Phase 7 Checklist: Evaluation Runner
- ✅ Read: HARNESS_DESIGN.md (entire document)
- ✅ Read: All 5 evaluation cases (case structure)
- ✅ Reference: CONTRACTS.md (request/response envelope)
- ✅ Reference: PROVIDER_INTERFACE.md (adapter interface)
- ✅ Confirm: All 5 cases execute successfully
- ✅ Confirm: Safety report matches HARNESS_DESIGN specification

### Phase 8 Checklist: Integration & Audit
- ✅ Read: AI_AUDIT_EVENT_CONTRACT.md (entire document)
- ✅ Read: ARCHITECTURE.md (entire document)
- ✅ Read: SAFETY.md (entire document)
- ✅ Confirm: Audit events cover all operations
- ✅ Confirm: No raw content logged (privacy)
- ✅ Confirm: Trace correlation across components
- ✅ Confirm: E2E workflows match ARCHITECTURE.md request flow

---

## Documentation Standards for Each Phase

When creating implementation documentation (README.md for each component):

**Phase 1 Libraries (ai-feature-flags, ai-contracts, ai-trusted-context):**
- Document which design document section they implement
- Include examples from CONTRACTS.md (request/response)
- Reference SAFETY.md section on disabled-by-default
- Document test strategy

**Phase 2 Gateway:**
- Document request validation rules (from CONTRACTS.md)
- Document response normalization (from CONTRACTS.md)
- Document isolation levels (from ARCHITECTURE.md)
- Document error categories (from CONTRACTS.md)

**Phase 3 Providers:**
- Document adapter interface (from PROVIDER_INTERFACE.md)
- Document capability declaration format
- Document error mapping strategy
- Document timeout/retry behavior

**Phase 4 Guardrails:**
- Document all 15 guards (from GUARDRAILS_IMPLEMENTATION_PLAN.md)
- Document sequencing order (fail-fast)
- Document test cases used (from evaluations/cases/)
- Document synthetic case mappings

**Phase 5 Policy Engine:**
- Document eligibility rules (from POLICY_ENGINE.md)
- Document data classification scheme (from POLICY_ENGINE.md)
- Document feature flag checking
- Document fail-closed behavior

**Phase 6 Prompt Registry:**
- Document versioning strategy
- Document audit event schema (from AI_AUDIT_EVENT_CONTRACT.md)
- Document rollback procedure
- Document immutability guarantees

**Phase 7 Evaluation Runner:**
- Document harness architecture (from HARNESS_DESIGN.md)
- Document case discovery and loading
- Document result aggregation
- Document regression testing

**Phase 8 Integration & Audit:**
- Document E2E workflow (from ARCHITECTURE.md)
- Document audit event emission (from AI_AUDIT_EVENT_CONTRACT.md)
- Document monitoring strategy
- Document incident response playbooks

---

## Approval Sign-Off Template

Each phase should include approval sign-off against relevant design documents:

```markdown
## Phase X Approval Sign-Off

### Design Document Compliance:
- ✅ Implemented per [DOCUMENT_NAME.md] (lines X-Y)
- ✅ Tested per [DOCUMENT_NAME.md] (lines X-Y)
- ✅ Audit strategy per [AI_AUDIT_EVENT_CONTRACT.md]
- ✅ Security review per [SAFETY.md]

### Approval Gates:
- ✅ Architecture team review (implementation matches design)
- ✅ Security team review (fail-closed behavior verified)
- ✅ Product team review (feature flags disabled by default)
- ✅ Test coverage (90%+ for security-critical code)

### Sign-Offs:
- Architecture: _______________ Date: ___
- Security: _______________ Date: ___
- Product: _______________ Date: ___
- QA: _______________ Date: ___
```

---

## Using This Reference During Implementation

1. **Before starting a phase:** Read the "Phase X Checklist" above
2. **While implementing:** Keep relevant design documents open alongside code
3. **Before submitting code:** Verify checklist items with code review
4. **Before production:** Include approval sign-off (template above)

---

## Quick Reference: Document Locations in Repository

```
ai/
├── ARCHITECTURE.md              ← Start here (trust model)
├── SAFETY.md                    ← Security requirements
├── gateway/
│   └── CONTRACTS.md             ← Request/response schemas
├── providers/
│   └── PROVIDER_INTERFACE.md    ← Adapter interface
├── policies/
│   └── POLICY_ENGINE.md         ← Classification and eligibility
├── guardrails/
│   └── GUARDRAILS_IMPLEMENTATION_PLAN.md  ← 15 guard specs
├── evaluations/
│   ├── HARNESS_DESIGN.md        ← Evaluation runner architecture
│   └── cases/
│       ├── prompt-injection.json
│       ├── tenant-isolation.json
│       ├── sensitive-data-leakage.json
│       ├── unsafe-access-recommendation.json
│       └── invalid-output.json
└── audit/
    └── AI_AUDIT_EVENT_CONTRACT.md  ← Audit event schema

docs/engineering/adr/
├── ADR-007-*.md                 ← Disabled-by-default principle
└── (9 other ADRs)

scripts/validate/
└── ai_evaluation_cases.py       ← Existing validator (reuse in Phase 7)
```

---

## Conclusion

Every line of code implemented in Phases 1-8 should be traceable back to one of these design documents. When in doubt about requirements or behavior, consult the relevant document sections listed in the phase checklist above.

This reference guide ensures implementation stays aligned with architecture, security, and product requirements defined during the design phase.

