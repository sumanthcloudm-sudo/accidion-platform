# Accidion AI Module: Phased Implementation Plan
## Phases 1-4: Foundation through Provider Adapters

**Status:** Design roadmap (no code changes, no Product Copilot enabled)
**Scope:** 8-phase plan covering all missing AI runtime components
**Duration:** ~26 weeks (6 months)
**Authority:** Accidion MVP six-month plan; all 10 ADRs are Proposed (pending approval)

---

## PHASE 1: Core Foundation (Weeks 1-3)

**Objective:** Establish feature flags, test doubles, core data models, and trusted context configuration.

### 1.1 Feature Flag Infrastructure
**Why First:** Controls disabled-by-default AI behavior (ADR-007 principle); gates all subsequent phases.

**Required Files to Create:**
- `libs/ai-feature-flags/README.md` – Configuration schema and environment variables
- `libs/ai-feature-flags/src/feature-flags.ts` – Flag evaluation logic (stub structure)
- `libs/ai-feature-flags/src/types.ts` – Flag definitions (disabled, test_mode, provider_[claude|gpt])
- `tests/unit/ai-feature-flags.test.ts` – Verify disabled-by-default behavior, override safety

**Implementation Order:**
1. Define flag enum: `AI_ENABLED`, `AI_TEST_MODE`, `AI_PROVIDER_CLAUDE`, `AI_PROVIDER_GPT`
2. Configuration loader from environment and config file (fail-closed on missing config)
3. Evaluation function with audit logging (every flag check logged)
4. Test: Verify AI disabled by default, no override without explicit env var, flag changes require restart

**Dependencies:** None (core library)
**Approval Gate:** Confirm feature flag approach acceptable (config file vs. runtime vs. database)

---

### 1.2 Test Doubles for Provider Adapters
**Why:** Unblock Phase 3 gateway+guardrails development without real provider credentials.

**Required Files to Create:**
- `ai/providers/test-doubles/mock-provider-adapter.ts` – Synthetic request/response generator
- `ai/providers/test-doubles/fixtures/` – Directory with 20+ synthetic responses
- `tests/integration/provider-adapters-mocks.test.ts` – Verify mock behavior matches contract

**Implementation Order:**
1. Create mock adapter implementing provider adapter interface (PROVIDER_INTERFACE.md)
2. Implement deterministic response generator (same seed → same response)
3. Add latency/timeout simulation (for timeout handling tests)
4. Error injection (connection failure, rate limit, model refusal, invalid JSON)
5. Test: All three operations (OBSERVE, REASON, RECOMMEND) return valid envelopes

**Dependencies:** Phase 2 (contracts must exist)
**Testing:** Unit tests for each response type; integration tests verify mock usable in gateway

---

### 1.3 Core Data Models and Contracts
**Why:** Establish shared request/response types before any service code.

**Required Files to Create:**
- `libs/ai-contracts/README.md` – Version and stability guarantee
- `libs/ai-contracts/src/types.ts` – All contract types (TypeScript/language TBD)
- `libs/ai-contracts/src/schemas/` – JSON Schema for runtime validation
  - `ai-request-envelope.schema.json`
  - `ai-response-envelope.schema.json`
  - `trusted-context.schema.json`
  - `classification.schema.json`
- `tests/unit/ai-contracts.test.ts` – Verify schema validity, examples parse correctly

**Key Types to Define (from gateway/CONTRACTS.md):**
- `AIRequest` (operation, user_input, trusted_context, classification)
- `AIResponse` (status, reasoning, output, metadata, audit_trace)
- `TrustedContext` (tenant_id, user_id, authenticated_at, permissions [array])
- `Classification` (data_type, sensitivity_level, requires_provider_approval)
- `AuditEvent` (event_id, timestamp, actor, operation, outcome, error)

**Dependencies:** None (but Phase 2+ consume these)
**Testing:** JSON Schema validation tests, serialization round-trips, example payloads

---

### 1.4 Trusted Context Configuration
**Why:** Establish how platform (not user) provides authentication/authorization context to AI.

**Required Files to Create:**
- `ai/TRUSTED_CONTEXT_DESIGN.md` – How tenant_id, user_id, permissions flow from host
- `libs/ai-trusted-context/src/trusted-context-builder.ts` – Builder with validation
- `libs/ai-trusted-context/src/validators.ts` – Fail-closed validators
- `tests/unit/trusted-context.test.ts` – Verify tenant isolation, reject user-supplied context

**Implementation Order:**
1. Define TrustedContext immutable type (user cannot modify after platform provides)
2. Builder enforces required fields: tenant_id, user_id, permissions array, authenticated_at
3. Validators: tenant_id format, no null/undefined, permissions array non-empty
4. Test: Reject attempt to override tenant_id with user input, validate timestamp freshness

**Dependencies:** Phase 1.3 (contracts)
**Approval Gate:** Confirm TrustedContext fields sufficient (what permissions needed?)

---

### Phase 1 Testing Strategy
- **Unit:** Feature flags disabled by default; test doubles match contract; contracts parse
- **Integration:** Mock provider works in gateway endpoint (early integration)
- **Security:** Trusted context cannot be overridden by user input; audit logging fires for flag checks
- **Coverage Target:** 80%+ for all Phase 1 libraries

**Phase 1 Completion Criteria:**
- ✅ Feature flags infrastructure deployed, AI disabled by default in all environments
- ✅ Mock provider adapter generates deterministic responses
- ✅ Core contract types and JSON schemas valid and documented
- ✅ Trusted context builder rejects user-supplied context
- ✅ All tests passing, security review completed
- ✅ Approval: Product/Security confirm feature flag and trusted context approach

---

## PHASE 2: AI Gateway (Weeks 4-6)

**Objective:** Implement request validation, response normalization, tenant verification, and routing.

### 2.1 Request Validation and Schema Enforcement
**Why:** First line of defense; reject malformed/incomplete requests before any processing.

**Required Files to Create:**
- `ai/gateway/src/request-validator.ts` – Validates against request envelope schema
- `ai/gateway/src/validators/operation-validator.ts` – Verify operation ∈ {OBSERVE, REASON, RECOMMEND}
- `ai/gateway/src/validators/input-validator.ts` – Input size limits, encoding checks
- `tests/unit/gateway-request-validator.test.ts`

**Implementation Order:**
1. Schema validation (JSON Schema against request envelope schema)
2. Operation whitelist (only OBSERVE, REASON, RECOMMEND permitted)
3. Input sanitization (max length, encoding, no binary, handle unicode safely)
4. Classification present and valid (data_type, sensitivity_level recognized)
5. TrustedContext validation (must come from platform, immutable)
6. Test: Reject oversized input, invalid operation, missing classification, null tenant_id

**Dependencies:** Phase 1 (contracts, trusted context)
**Testing:** Boundary tests (max input, null fields, invalid enums), malformed JSON

---

### 2.2 Response Normalization and Validation
**Why:** Ensure all provider responses conform to contract before returning to caller.

**Required Files to Create:**
- `ai/gateway/src/response-normalizer.ts` – Transform provider output → contract envelope
- `ai/gateway/src/response-validator.ts` – Verify normalized response is valid
- `tests/unit/gateway-response-validator.test.ts`

**Implementation Order:**
1. Normalizer takes provider response (any format, JSON or text)
2. Extract reasoning, output, metadata, create response envelope
3. Validator confirms required fields present, status valid, no malformed data
4. Error handling: Provider timeout → GATEWAY_TIMEOUT, invalid JSON → PROVIDER_ERROR
5. Test: Normalize Claude response, GPT response, mock provider response to valid envelope

**Dependencies:** Phase 1 (contracts), Phase 2.1 (error categories)
**Testing:** Each provider format, error cases, normalization preserves information

---

### 2.3 Tenant Context Verification
**Why:** Prevent cross-tenant data leakage through request routing and audit.

**Required Files to Create:**
- `ai/gateway/src/tenant-verifier.ts` – Verify tenant_id consistency throughout request
- `ai/gateway/src/audit-context-builder.ts` – Build audit event with tenant_id
- `tests/unit/gateway-tenant-verifier.test.ts`

**Implementation Order:**
1. Extract tenant_id from TrustedContext
2. Verify tenant_id present in all request/response objects
3. Verify tenant_id in all audit events
4. Test: Reject mismatched tenant_id, confirm audit trace includes tenant

**Dependencies:** Phase 1 (trusted context), Phase 2.1 (request validator)
**Testing:** Attempt cross-tenant override, audit logging includes tenant

---

### 2.4 Request Routing to Provider Adapters
**Why:** Route to correct provider adapter based on classification and feature flags.

**Required Files to Create:**
- `ai/gateway/src/provider-router.ts` – Route to Claude/GPT based on policy/flags
- `ai/gateway/src/adapter-selector.ts` – Determine which adapter can handle this request
- `ai/gateway/src/adapter-pool.ts` – Manage adapter lifecycle, connection pooling
- `tests/unit/gateway-routing.test.ts`

**Implementation Order:**
1. Router consults feature flags (AI_PROVIDER_CLAUDE, AI_PROVIDER_GPT)
2. If provider disabled, return error (NOT_ENABLED)
3. Select adapter based on availability and load
4. Timeout handling: Call adapter with timeout, if exceeded return GATEWAY_TIMEOUT
5. Retry logic (configurable attempts, exponential backoff)
6. Test: Route to Claude when enabled, route to GPT when Claude disabled, fail if all disabled

**Dependencies:** Phase 1 (feature flags, mock adapter), Phase 2.1, 2.2
**Testing:** Feature flag combinations, timeout simulation, retry exhaustion

---

### Phase 2 Testing Strategy
- **Unit:** Request validation rejects invalid input; response normalization produces valid output
- **Integration:** End-to-end request → validation → routing → mock provider → normalization → response
- **Security:** Tenant_id verified throughout; audit events include tenant; no cross-tenant leakage
- **Failure Modes:** Timeout, provider error, malformed response, provider disabled
- **Coverage Target:** 85%+ gateway code

**Phase 2 Completion Criteria:**
- ✅ All request validation rules enforced, boundary tests passing
- ✅ Response normalization handles all provider formats
- ✅ Tenant context verification prevents cross-tenant access
- ✅ Routing logic works with all feature flag combinations
- ✅ E2E test: valid request → mock provider → valid response
- ✅ Security review: no tenant_id leakage, audit logging works
- ✅ Approval: Architecture team confirm gateway design acceptable

---

## PHASE 3: Provider Adapters (Weeks 7-10)

**Objective:** Implement Claude and GPT adapters with test-double-first approach, error handling, capability declaration.

### 3.1 Claude Provider Adapter – Test Double First
**Why:** Develop adapter logic and error handling without real API credentials or cost.

**Required Files to Create:**
- `ai/providers/claude/adapter.ts` – Implements provider adapter interface
- `ai/providers/claude/client-factory.ts` – Factory for real vs. mock client
- `ai/providers/claude/error-handler.ts` – Claude-specific error mapping
- `ai/providers/claude/capabilities.ts` – Declare: OBSERVE, REASON, RECOMMEND support
- `ai/providers/claude/README.md` – Claude API version, models, rate limits
- `tests/unit/claude-adapter.test.ts`
- `tests/integration/claude-adapter-mock.test.ts`

**Implementation Order:**
1. Mock-first: Adapter calls mock client (from Phase 1.2)
2. Implement all three operations (OBSERVE, REASON, RECOMMEND)
3. Error mapping: Claude API errors → contract error categories
4. Capability declaration: Which operations supported, models available
5. Timeout and retry: Respect timeout in contract
6. Test mock version thoroughly before real version
7. Later (Phase 3, Week 9): Add real Claude client, gate behind feature flag

**Dependencies:** Phase 1.2 (mock provider), Phase 2 (gateway), Phase 1.3 (contracts)
**Testing:** Mock responses, error cases, timeout simulation
**Approval Gate:** Claude API access approval (credentials, rate limits, costs)

---

### 3.2 GPT Provider Adapter – Test Double First
**Why:** Same pattern as Claude; ready for real OpenAI API when approved.

**Required Files to Create:**
- `ai/providers/gpt/adapter.ts` – Implements provider adapter interface
- `ai/providers/gpt/client-factory.ts` – Factory for real vs. mock client
- `ai/providers/gpt/error-handler.ts` – OpenAI-specific error mapping
- `ai/providers/gpt/capabilities.ts` – Declare: OBSERVE, REASON, RECOMMEND support
- `ai/providers/gpt/README.md` – OpenAI API version, models, rate limits
- `tests/unit/gpt-adapter.test.ts`
- `tests/integration/gpt-adapter-mock.test.ts`

**Implementation Order:**
1. Mock-first: Adapter calls mock client
2. Implement all three operations
3. Error mapping: OpenAI API errors → contract error categories
4. Capability declaration
5. Timeout and retry
6. Test mock version thoroughly
7. Later (Phase 3, Week 9): Add real OpenAI client, gate behind feature flag

**Dependencies:** Phase 1.2 (mock provider), Phase 2 (gateway), Phase 1.3 (contracts)
**Testing:** Mock responses, error cases, timeout simulation
**Approval Gate:** OpenAI API access approval

---

### 3.3 Error and Timeout Handling
**Why:** Establish reliable fallback behavior (fail-closed, not fail-open).

**Required Files to Create:**
- `ai/providers/error-handler-base.ts` – Base error mapping logic
- `ai/providers/error-categories.ts` – Standardized error types from contract
- `ai/providers/timeout-handler.ts` – Timeout enforcement, graceful degradation
- `tests/unit/provider-error-handling.test.ts`

**Error Categories (from contract):**
- `PROVIDER_ERROR` – API call failed (network, 5xx, etc.)
- `PROVIDER_RATE_LIMIT` – Hit rate limit, should retry with backoff
- `PROVIDER_TIMEOUT` – Call exceeded configured timeout
- `PROVIDER_REFUSED` – Provider refused request (content policy, etc.)
- `PROVIDER_INVALID_RESPONSE` – Response doesn't match schema
- `GATEWAY_TIMEOUT` – Gateway timeout before provider responded
- `NOT_ENABLED` – Provider disabled by feature flag

**Implementation Order:**
1. Map Claude errors → categories
2. Map GPT errors → categories
3. Timeout handler: Kill call after configured max time
4. Retry handler: Backoff on rate limit (with max attempts)
5. Fallback: Return NOT_ENABLED error if all providers disabled
6. Test: Each error category, timeout at different points, retry exhaustion

**Dependencies:** Phase 3.1, 3.2 (provider adapters)
**Testing:** Inject each error type, verify mapping correct, retry behavior

---

### 3.4 Capability Declaration
**Why:** Advertise what this provider can do (operations, models, data types).

**Required Files to Create:**
- `ai/providers/capability-registry.ts` – Registry of all provider capabilities
- `ai/providers/capability-query-api.ts` – Query: "Can provider X do operation Y?"
- `tests/unit/capability-registry.test.ts`

**Capability Format:**
```
{
  provider_id: "claude",
  operations: ["OBSERVE", "REASON", "RECOMMEND"],
  models: ["claude-3-opus", "claude-3-sonnet"],
  supported_data_types: ["text", "json"],
  unsupported_data_types: ["image"],
  rate_limit: "100 req/min",
  max_input_tokens: 100000,
  max_output_tokens: 4096
}
```

**Implementation Order:**
1. Define capability schema
2. Claude: Declare supported operations, models, rate limits
3. GPT: Declare supported operations, models, rate limits
4. Query API: Check if provider supports operation before routing
5. Test: Query returns correct capabilities, unsupported operations rejected

**Dependencies:** Phase 3.1, 3.2
**Testing:** Query returns accurate data, unsupported operations rejected

---

### Phase 3 Testing Strategy
- **Unit:** Each adapter handles mock responses correctly
- **Integration:** Mock adapters work through gateway, routing selects correct adapter
- **Error Injection:** Timeout, connection failure, invalid response, rate limit
- **Feature Flags:** Real client not called if provider disabled
- **Secrets:** No credentials in code or tests (use environment variables only)
- **Coverage Target:** 85%+ adapter code

**Phase 3 Completion Criteria:**
- ✅ Claude adapter (mock) handles all three operations
- ✅ GPT adapter (mock) handles all three operations
- ✅ Error handling maps all error types correctly
- ✅ Timeout enforcement works reliably
- ✅ Capability registry accurate and queryable
- ✅ E2E test: request → gateway → adapter (mock) → response
- ✅ No provider credentials in repository
- ✅ Approval: Provider adapters reviewed by Architecture team

---

## PHASE 4: Guardrails (Weeks 11-14)

**Objective:** Implement 15 guardrail controls covering input validation, injection detection, output validation, sensitive data redaction.

### 4.1 Input Validation and Injection Detection (6 guardrails)
**Why:** Prevent prompt injection, command injection, XSS; validate input format and size.

**Guardrails to Implement (from GUARDRAILS_IMPLEMENTATION_PLAN.md):**

1. **Input Size Validation**
   - Files: `ai/guardrails/src/input-size-validator.ts`
   - Enforce: max_input_length (e.g., 10,000 chars), reject oversized
   - Test: At boundary, overflow, empty

2. **Encoding Validation**
   - Files: `ai/guardrails/src/encoding-validator.ts`
   - Enforce: UTF-8 only, reject invalid byte sequences
   - Test: Valid UTF-8, malformed bytes, emoji

3. **Prompt Injection Detection**
   - Files: `ai/guardrails/src/injection-detector.ts`
   - Detect: Common patterns (e.g., "Ignore above instructions", role-play attempts)
   - Use synthetic case: `ai/evaluations/cases/prompt-injection.json`
   - Test: Injection case passes detector

4. **Command Injection Detection**
   - Files: `ai/guardrails/src/command-injection-detector.ts`
   - Detect: Shell metacharacters, script syntax in input
   - Test: Shell commands rejected, normal text passes

5. **XSS Pattern Detection**
   - Files: `ai/guardrails/src/xss-detector.ts`
   - Detect: `<script>`, `javascript:`, HTML event handlers
   - Test: HTML tags rejected, markdown passes

6. **Structured Input Validation**
   - Files: `ai/guardrails/src/structured-input-validator.ts`
   - Enforce: If input_type="json", validate against provided schema
   - Test: Valid JSON passes, invalid fails

**Required Files to Create:**
- `ai/guardrails/src/input-validators/` – Directory for all 6 validators
- `tests/unit/guardrails-input.test.ts` – All 6 tests
- `tests/security/injection-detection.test.ts` – Injection-specific security tests

**Implementation Order:**
1. Size and encoding validators (simple, non-blocking)
2. Injection detection (regex-based patterns)
3. Command and XSS detectors (pattern lists)
4. Structured validation (schema-based)
5. Test with synthetic cases from evaluations

**Dependencies:** Phase 1.3 (contracts), Phase 2 (gateway)
**Testing:** Positive/negative for each detector, injection test cases

---

### 4.2 Output Validation and Schema Enforcement (4 guardrails)
**Why:** Ensure model output conforms to expected schema, prevent injection in responses.

**Guardrails to Implement:**

7. **Output Schema Validation**
   - Files: `ai/guardrails/src/output-schema-validator.ts`
   - Enforce: If response schema specified, validate against it
   - Test: Valid response passes, malformed fails

8. **Output Size Limits**
   - Files: `ai/guardrails/src/output-size-validator.ts`
   - Enforce: max_output_length (e.g., 50,000 chars)
   - Test: At boundary, overflow

9. **JSON Format Validation**
   - Files: `ai/guardrails/src/json-format-validator.ts`
   - Enforce: If response must be JSON, validate structure
   - Test: Valid JSON, malformed, not JSON

10. **Output Safety Scanning**
    - Files: `ai/guardrails/src/output-safety-scanner.ts`
    - Detect: Known-bad patterns (e.g., hardcoded secrets, URLs to malicious sites)
    - Test: Safe content passes, suspicious patterns flagged

**Required Files to Create:**
- `ai/guardrails/src/output-validators/` – Directory for 4 validators
- `tests/unit/guardrails-output.test.ts`

**Implementation Order:**
1. Schema validation (most important)
2. Size limits
3. JSON format
4. Safety scanning (pattern-based)

**Dependencies:** Phase 1.3 (contracts), Phase 3 (provider adapters)
**Testing:** Valid/invalid responses, boundary conditions

---

### 4.3 Sensitive Data Redaction (5 guardrails)
**Why:** Prevent leakage of PII, credentials, or restricted data from AI responses.

**Guardrails to Implement:**

11. **PII Detection and Redaction**
    - Files: `ai/guardrails/src/pii-detector.ts`
    - Detect: SSN, email, phone patterns
    - Redact: Replace with [PII_REDACTED]
    - Test: Synthetic case `sensitive-data-leakage.json`

12. **Credential Detection and Redaction**
    - Files: `ai/guardrails/src/credential-detector.ts`
    - Detect: API keys, passwords, connection strings
    - Redact: Replace with [CREDENTIAL_REDACTED]
    - Test: Common key patterns

13. **Secret Key Detection**
    - Files: `ai/guardrails/src/secret-detector.ts`
    - Use regex for common patterns (AWS_SECRET, PRIVATE_KEY, etc.)
    - Redact: Replace with [SECRET_REDACTED]
    - Test: Known secret formats

14. **Classification-Based Output Filtering**
    - Files: `ai/guardrails/src/classification-filter.ts`
    - If input classification is "Restricted", do not send to provider
    - Fail-closed: Reject request if Restricted data in input
    - Test: Restricted data rejected

15. **Data Lineage Tracking**
    - Files: `ai/guardrails/src/data-lineage-tracker.ts`
    - Track: Which fields from request appear in response
    - Audit: Log sensitive field flows
    - Test: Lineage accuracy

**Required Files to Create:**
- `ai/guardrails/src/data-redaction/` – Directory for 5 redactors
- `tests/unit/guardrails-redaction.test.ts`
- `tests/security/sensitive-data-leakage.test.ts`

**Implementation Order:**
1. PII detection (regex-based)
2. Credential detection
3. Secret keys
4. Classification filtering (fail-closed)
5. Data lineage tracking

**Dependencies:** Phase 1.3 (contracts, classification), Phase 4.1 (input validation)
**Testing:** Synthetic data with PII, credentials; verify redaction; lineage accuracy

---

### 4.4 Guardrail Integration and Sequencing
**Why:** Establish order of enforcement (fail-fast principle).

**Required Files to Create:**
- `ai/guardrails/src/guardrail-sequencer.ts` – Order and run all guards
- `ai/guardrails/src/guardrail-result.ts` – Unified result type
- `tests/unit/guardrails-sequencing.test.ts`

**Enforcement Order (fail-fast):**
1. Input size validation (reject oversized immediately)
2. Encoding validation (reject invalid bytes)
3. Injection detection (reject injection attempts)
4. Structured input validation (reject schema violations)
5. Classification check (reject Restricted data)
6. [Send to provider]
7. Output size validation
8. Output schema validation
9. JSON format validation
10. PII redaction
11. Credential redaction
12. Secret detection
13. Output safety scan
14. Data lineage tracking
15. [Return sanitized response]

**Implementation Order:**
1. Define sequencer interface
2. Run guards in order, return first failure (or all failures?)
3. Redaction happens on success (no failures)
4. Test: All 15 guards run in order, early failure stops sequence

**Dependencies:** All of Phase 4.1-4.3
**Testing:** Sequencing accuracy, early termination

---

### Phase 4 Testing Strategy
- **Unit:** Each of 15 guardrails tested independently
- **Security:** Injection detection with real injection patterns; PII redaction with real PII
- **Negative:** Verify guardrails reject dangerous inputs, not just pass safe inputs
- **Synthetic Cases:** Use 5 evaluation cases as integration tests
- **Coverage Target:** 90%+ guardrails code (security-critical)

**Phase 4 Completion Criteria:**
- ✅ All 15 guardrails implemented and tested
- ✅ Injection detection catches prompt injection case
- ✅ Sensitive data redaction handles PII, credentials, secrets
- ✅ Classification filtering prevents Restricted data to provider
- ✅ Sequencing enforces correct order, early failure stops processing
- ✅ E2E test: malicious input → guardrails reject; safe input → passes
- ✅ Security review: no data leakage, redaction complete
- ✅ Approval: Security team confirms guardrails sufficient

---

### End of Phase 1-4 Documentation

This document covers foundation, gateway, provider adapters, and guardrails. See companion document for Phases 5-8: Policy Engine, Prompt Registry, Evaluation Runner, and Integration/Audit.

