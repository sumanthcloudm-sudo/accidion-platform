# Accidion AI Module: Phased Implementation Plan
## Phases 5-8: Policy Engine through Integration & Audit

---

## PHASE 5: Policy Engine (Weeks 15-18)

**Objective:** Implement use-case eligibility evaluation, data classification enforcement, feature state checking, and restricted data blocking.

### 5.1 Use-Case Eligibility Evaluation
- **Files:** `ai/policies/src/eligibility-evaluator.ts`, `tests/unit/policy-eligibility.test.ts`
- **Implementation:** Define eligible use cases (OBSERVE, REASON, RECOMMEND patterns)
- **Example:** "OBSERVE: Summarize employee records" is eligible; "REASON: Override access policy" is not
- **Test:** Each use case approved/rejected based on policy rules
- **Dependencies:** Phase 1.3 (contracts), Phase 3 (provider adapters)

### 5.2 Data Classification Enforcement
- **Files:** `ai/policies/src/classification-enforcer.ts`, `tests/unit/policy-classification.test.ts`
- **Implementation:** Apply rules from POLICY_ENGINE.md
- **Rules:** Restricted = no provider access; Public = allowed; Internal = provider approval required
- **Test:** Restricted data rejected, Public allowed, Internal checked against approval
- **Dependencies:** Phase 1.4 (trusted context), Phase 4.1 (input validation)

### 5.3 Feature State Checking
- **Files:** `ai/policies/src/feature-state-checker.ts`, `tests/unit/policy-features.test.ts`
- **Implementation:** Verify AI features enabled for tenant, user, operation
- **Test:** Enabled features allowed, disabled features rejected
- **Dependencies:** Phase 1.1 (feature flags), Phase 1.4 (trusted context)

### 5.4 Restricted Data Blocking
- **Files:** `ai/policies/src/restricted-data-blocker.ts`, `tests/unit/policy-restricted-data.test.ts`
- **Implementation:** Fail-closed: if data marked Restricted, reject entire request
- **Test:** Restricted data never reaches provider, error returned to caller
- **Dependencies:** Phase 4 (guardrails), Phase 5.2 (classification)

### Phase 5 Completion Criteria:
- ✅ All four policy components implemented and tested
- ✅ E2E test: ineligible use case rejected; Restricted data blocked
- ✅ Security review: fail-closed behavior verified
- ✅ Approval: Policy rules approved by Product/Security team

---

## PHASE 6: Prompt Registry (Weeks 19-21)

**Objective:** Implement versioned prompt storage, prompt management API, audit of changes, rollback mechanism.

### 6.1 Prompt Storage and Versioning
- **Files:** `ai/prompts/src/prompt-store.ts`, `ai/prompts/src/prompt-version.ts`
- **Schema:** Create `prompts` table in database (operations: create, read, list, update, delete)
- **Versioning:** Immutable versions, semantic versioning (v1.0.0, v1.0.1, etc.)
- **Test:** Create prompt, read by ID/version, list all versions
- **Dependencies:** Database schema migrations, Phase 1.3 (contracts)

### 6.2 Prompt Management API
- **Files:** `ai/prompts/src/prompt-api.ts`, `api/prompt-routes.ts`
- **Endpoints:**
  - `POST /api/ai/prompts` – Create new prompt
  - `GET /api/ai/prompts/{id}` – Retrieve prompt
  - `GET /api/ai/prompts/{id}/versions` – List all versions
  - `PUT /api/ai/prompts/{id}` – Create new version
  - `DELETE /api/ai/prompts/{id}` – Soft delete (mark as deprecated)
- **Test:** All endpoints working, correct versioning
- **Dependencies:** Phase 6.1 (storage)

### 6.3 Audit of Prompt Changes
- **Files:** `ai/prompts/src/prompt-audit.ts`, `tests/unit/prompt-audit.test.ts`
- **Events:** Who created/updated/deleted prompt, when, what changed
- **Storage:** Immutable audit log (cannot be deleted or modified)
- **Test:** Audit events recorded for all prompt operations
- **Dependencies:** Phase 1.3 (contracts, audit event schema)

### 6.4 Rollback Mechanism
- **Files:** `ai/prompts/src/prompt-rollback.ts`, `tests/unit/prompt-rollback.test.ts`
- **Operation:** Revert to previous prompt version
- **Implementation:** Create new version pointing to old content
- **Test:** Rollback to v1.0.0, verify new version created with old content
- **Dependencies:** Phase 6.1 (versioning), Phase 6.3 (audit)

### Phase 6 Completion Criteria:
- ✅ Prompt storage with versioning implemented
- ✅ Management API fully functional
- ✅ Audit log captures all changes
- ✅ Rollback works and creates new version (not rewrites history)
- ✅ E2E test: create → update → rollback → verify version history
- ✅ Approval: Database schema reviewed by DBA/Architecture team

---

## PHASE 7: Evaluation Runner (Weeks 22-24)

**Objective:** Implement executable evaluation harness, run synthetic test cases, generate safety reports, enable regression testing.

### 7.1 Evaluation Harness
- **Files:** `ai/evaluations/src/harness.ts`, `ai/evaluations/src/test-runner.ts`
- **Design:** Based on HARNESS_DESIGN.md
- **Responsibilities:**
  - Discover test cases from `ai/evaluations/cases/*.json`
  - Load synthetic evaluation data
  - Execute against live or mock provider
  - Collect results and metrics
- **Test:** Harness starts, finds cases, reports ready
- **Dependencies:** Phase 7.2 (case loader), Phase 3 (adapters)

### 7.2 Case Discovery and Loading
- **Files:** `ai/evaluations/src/case-loader.ts`, `tests/unit/evaluation-case-loader.test.ts`
- **Discovery:** Scan `ai/evaluations/cases/` for `.json` files
- **Validation:** Use existing `scripts/validate/ai_evaluation_cases.py` (already complete)
- **Loading:** Parse JSON, hydrate into test case objects
- **Test:** Discover all 5 cases, load without error
- **Dependencies:** Phase 1.3 (contracts), existing validator script

### 7.3 Synthetic Test Case Execution
- **Files:** `ai/evaluations/src/case-executor.ts`, `tests/integration/evaluation-execution.test.ts`
- **Execution:** For each case: prepare input → call provider → validate output
- **Cases to Execute (from evaluations/cases/):**
  1. prompt-injection.json – Verify injection rejected
  2. tenant-isolation.json – Verify tenant boundary enforced
  3. sensitive-data-leakage.json – Verify PII redacted
  4. unsafe-access-recommendation.json – Verify dangerous recommendations blocked
  5. invalid-output.json – Verify invalid responses rejected
- **Test:** Each case executed, results captured, pass/fail determined
- **Dependencies:** Phase 4 (guardrails), Phase 3 (providers), Phase 7.2 (case loader)

### 7.4 Safety Report Generation
- **Files:** `ai/evaluations/src/safety-report-generator.ts`, `tests/unit/evaluation-reports.test.ts`
- **Report Schema:** Summary table, per-case results, metrics (pass rate, coverage, time)
- **Output:** JSON and markdown formats
- **Example Report Content:**
  ```
  Total Cases: 5
  Passed: 5
  Failed: 0
  Coverage: 100% (all guardrails exercised)
  Execution Time: 45 seconds
  
  Case Results:
  - prompt-injection: PASS
  - tenant-isolation: PASS
  - sensitive-data-leakage: PASS
  - unsafe-access-recommendation: PASS
  - invalid-output: PASS
  ```
- **Test:** Report structure valid, metrics calculated correctly
- **Dependencies:** Phase 7.3 (executor)

### 7.5 Regression Testing
- **Files:** `ai/evaluations/src/regression-detector.ts`, `scripts/run-evaluation-suite.sh`
- **Implementation:** Compare current report to baseline
- **Baseline:** Store latest passing report as golden standard
- **Detection:** If any case fails that previously passed, flag as regression
- **CI/CD:** Integration: evaluation suite runs on every commit (see Phase 8)
- **Test:** Regression detection identifies newly-failing cases
- **Dependencies:** Phase 7.4 (reports)

### Phase 7 Completion Criteria:
- ✅ Evaluation harness discovers and runs all 5 test cases
- ✅ Each case executes against mock provider successfully
- ✅ Safety report generated with correct metrics
- ✅ Regression detection flags failing cases
- ✅ Full test run completes in <2 minutes
- ✅ All tests passing, report shows 100% case pass rate
- ✅ Approval: Evaluation runner design reviewed, baseline approved

---

## PHASE 8: Integration & Audit (Weeks 25-26)

**Objective:** Implement end-to-end workflow testing, audit event emission, monitoring and observability, documentation and runbooks.

### 8.1 End-to-End Workflow Testing
- **Files:** `tests/e2e/ai-workflows.test.ts`
- **Workflows to Test:**
  1. Happy path: valid request → provider → valid response
  2. Injection detection: malicious input → rejected by guardrails
  3. Tenant isolation: request from TenantA → data from TenantB rejected
  4. Classification blocking: Restricted data → request rejected
  5. Provider disabled: AI_PROVIDER disabled → NOT_ENABLED returned
  6. Timeout: provider slow → timeout error returned
- **Test:** Each workflow runs end-to-end, assertions verify expected behavior
- **Dependencies:** All phases 1-7 (full system)

### 8.2 Audit Event Emission
- **Files:** `ai/audit/src/audit-emitter.ts`, `tests/unit/audit-emitter.test.ts`
- **Schema:** AI_AUDIT_EVENT_CONTRACT.md (existing)
- **Events Emitted:**
  - ai.request.submitted (input, user, tenant, timestamp, no raw content)
  - ai.guardrail.triggered (which guardrail, action taken)
  - ai.provider.called (which provider, which operation, duration)
  - ai.provider.error (error type, provider response)
  - ai.response.generated (output size, redactions applied, user, tenant)
  - ai.feature.flag.checked (flag name, value at time of check)
- **Privacy:** Never log raw prompt, response, or sensitive data (use redacted versions)
- **Test:** Audit event for each major step, no raw data in logs
- **Dependencies:** Phase 1.3 (contracts, audit event schema)

### 8.3 Monitoring and Observability
- **Files:** `ai/observability/src/metrics.ts`, `ai/observability/src/tracing.ts`
- **Metrics (to send to monitoring system):**
  - `ai.request.count` – total requests
  - `ai.request.latency_ms` – p50, p95, p99
  - `ai.provider.latency_ms` – per provider
  - `ai.guardrail.triggered_count` – per guardrail
  - `ai.error.count` – per error type
  - `ai.feature_flag.value` – current state of each flag
- **Tracing:** Unique trace_id for each request, logged in all audit events
- **Test:** Metrics emission, trace correlation across components
- **Dependencies:** Phase 8.2 (audit events)

### 8.4 Documentation and Runbooks
- **Files to Create:**
  - `ai/IMPLEMENTATION_GUIDE.md` – How to deploy Phase 1-8
  - `ai/OPERATIONAL_RUNBOOK.md` – How to monitor, debug, troubleshoot in production
  - `ai/TROUBLESHOOTING.md` – Common issues and solutions
  - `ai/PROVIDER_SETUP.md` – How to configure Claude/GPT credentials
  - `ai/SECURITY_VALIDATION.md` – Security checklist for each phase
  - `ai/TEST_STRATEGY.md` – Which tests to run before production
  - `docs/engineering/adr/ADR-011-AI-Implementation-Complete.md` – Summary ADR
- **Content:**
  - Deployment checklist (which files to deploy in which order)
  - Production troubleshooting (debug logs, metrics to check)
  - Emergency procedures (disable AI, rollback, failsafe behavior)
  - Security validation (verify guardrails, audit logging, tenant isolation)
  - Test suite instructions (which tests must pass before release)
- **Test:** Documentation examples run successfully (runbooks are executable)
- **Dependencies:** All phases 1-7 (full system)

### 8.5 Final Integration and Approval Gates
- **Gate 1: Security Review**
  - Audit logging captures all AI decisions
  - No credentials in logs
  - Tenant isolation verified
  - Guardrails cannot be bypassed
  - Feature flags prevent autonomous execution
- **Gate 2: Performance Review**
  - Request/response latency acceptable (<500ms average)
  - No memory leaks in long-running tests
  - Timeout handling works (no hangs)
- **Gate 3: Architecture Review**
  - All 8 phases implemented per design
  - Error handling is fail-closed
  - Contracts enforced
  - Dependencies documented
- **Gate 4: Product Approval**
  - MVP scope met
  - Feature flags disabled by default
  - No autonomous execution
  - Monitoring sufficient for production

### Phase 8 Completion Criteria:
- ✅ All 6 E2E workflows passing
- ✅ Audit events emitted for all major operations
- ✅ Metrics and tracing operational
- ✅ Documentation complete and reviewed
- ✅ All four approval gates passed
- ✅ Production checklist signed off
- ✅ Feature flags verified: AI disabled, test mode available, providers gatable

---

## Summary: 8-Phase Dependencies and Timeline

**Phase 1: Weeks 1-3**
- Outputs: Feature flags, test doubles, contracts, trusted context
- Critical path gate: Approve feature flag approach and trusted context design

**Phase 2: Weeks 4-6**
- Inputs: Phase 1 outputs
- Outputs: Gateway validation, normalization, routing
- Critical path gate: Gateway design approval

**Phase 3: Weeks 7-10**
- Inputs: Phase 2 gateway + Phase 1 test doubles
- Outputs: Claude and GPT adapters (mock), error handling, capabilities
- Critical path gate: Provider approval (Claude/GPT APIs)

**Phase 4: Weeks 11-14**
- Inputs: Phase 3 adapters, Phase 2 gateway
- Outputs: 15 guardrails, injection detection, data redaction
- Parallel with Phase 5 (policy can start Week 11)
- Critical path gate: Security review of guardrails

**Phase 5: Weeks 15-18**
- Inputs: Phase 1, 2, 4 outputs
- Outputs: Policy engine, eligibility, classification, data blocking
- Critical path gate: Policy rules approval (Product/Security)

**Phase 6: Weeks 19-21**
- Inputs: Phase 1 contracts, database schema
- Outputs: Prompt storage, versioning, audit, rollback
- Parallel with Phase 7 (evaluation can start Week 19)
- Critical path gate: Database schema approval

**Phase 7: Weeks 22-24**
- Inputs: Phase 3 providers, Phase 4 guardrails, Phase 1 contracts
- Outputs: Evaluation harness, case execution, safety reports
- Critical path gate: Baseline report approval (all 5 cases passing)

**Phase 8: Weeks 25-26**
- Inputs: All phases 1-7 outputs
- Outputs: E2E tests, audit integration, monitoring, documentation
- Gate: All 4 approval gates (security, performance, architecture, product)

---

## Required Approvals and Decision Points

**Before Phase 1 Starts:**
- ❌ ADR-007 (AI Copilot disabled-by-default) – Currently Proposed, needs approval
- ❌ Feature flag implementation strategy – Config file? Runtime? Database?
- ❌ TrustedContext design – Which fields required? How does host provide context?

**Before Phase 3 Starts (Provider Adapters):**
- ❌ Provider credentials strategy – Environment variables? Secrets manager?
- ❌ Which providers approved for MVP – Claude only? GPT? Others?
- ❌ Claude/GPT API contracts – Which API versions? Which models?

**Before Phase 5 Starts (Policy Engine):**
- ❌ Policy rules definition – What use cases are eligible? Which data classes?
- ❌ Data classification scheme – Which sensitivity levels? What triggers restrictions?
- ❌ Feature flag implementation for tenant/user-level features

**Before Phase 6 Starts (Prompt Registry):**
- ❌ Database schema design and migration tool
- ❌ Prompt versioning strategy – Semantic versioning? Hash-based?

**Before Phase 8 Starts (Integration):**
- ❌ Audit log storage backend – Which database/service?
- ❌ Metrics backend – Prometheus? CloudWatch? Custom?
- ❌ Production deployment target – Kubernetes? Container? Serverless?

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Provider API changes mid-implementation | Adapter interface insulates changes; test doubles allow development without real API |
| Guardrails incomplete or bypass-able | Security review gate (Phase 8); synthetic test cases verify coverage |
| Tenant isolation breach | TrustedContext immutable (Phase 1); verification in gateway (Phase 2); audit logging (Phase 8) |
| Performance degradation from guardrails | Measure latency in Phase 8; optimize hot paths; consider async guardrails |
| Feature flags become unmanageable | Keep flag set small (5-6 flags); document each flag purpose and disable procedures |
| Audit log storage overwhelmed | Log redacted/summarized events (not raw content); implement retention/cleanup policy |
| Prompt registry versioning conflicts | Immutable versions; rollback creates new version (never rewrites history) |

---

## File Directory Structure (All Phases)

```
libs/
  ai-feature-flags/
  ai-contracts/
  ai-trusted-context/

ai/
  gateway/
    src/
      request-validator.ts
      response-normalizer.ts
      tenant-verifier.ts
      provider-router.ts
  providers/
    claude/
    gpt/
    test-doubles/
  guardrails/
    src/
      input-validators/
      output-validators/
      data-redaction/
  policies/
    src/
      eligibility-evaluator.ts
      classification-enforcer.ts
      feature-state-checker.ts
      restricted-data-blocker.ts
  prompts/
    src/
      prompt-store.ts
      prompt-api.ts
      prompt-audit.ts
      prompt-rollback.ts
  evaluations/
    src/
      harness.ts
      case-loader.ts
      case-executor.ts
      safety-report-generator.ts
      regression-detector.ts
    cases/
      prompt-injection.json
      tenant-isolation.json
      sensitive-data-leakage.json
      unsafe-access-recommendation.json
      invalid-output.json
  audit/
    src/
      audit-emitter.ts
  observability/
    src/
      metrics.ts
      tracing.ts

tests/
  unit/
    ai-*.test.ts
  integration/
    ai-*.test.ts
  e2e/
    ai-workflows.test.ts
  security/
    injection-detection.test.ts
    sensitive-data-leakage.test.ts

scripts/
  run-evaluation-suite.sh
  validate/
    ai_evaluation_cases.py (existing)
```

---

## Test Strategy Summary

- **Unit Tests:** Each component tested independently (90%+ coverage target)
- **Integration Tests:** Components working together (phases test previous phases)
- **E2E Tests:** Full request/response flow (Phase 8)
- **Security Tests:** Injection detection, data redaction, tenant isolation
- **Synthetic Evaluation:** 5 test cases verify safety goals (Phase 7)
- **Regression Testing:** Every phase builds on and tests previous phases

---

## Completion Definition

All 8 phases complete when:
- ✅ All required files exist and are reviewed
- ✅ All tests passing (unit, integration, E2E, security, synthetic)
- ✅ All 4 approval gates passed (security, performance, architecture, product)
- ✅ Documentation complete and reviewed
- ✅ Production deployment plan finalized
- ✅ Monitoring and observability operational
- ✅ Feature flags verified: AI disabled by default, no autonomous execution

