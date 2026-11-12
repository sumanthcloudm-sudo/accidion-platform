# Accidion AI Implementation: Getting Started Guide

This guide provides practical, actionable first steps to begin Phase 1 implementation.

---

## Pre-Phase-1 Actions: What Must Happen First

**Duration:** 1-2 weeks  
**Owner:** Product/Architecture/Security teams  
**Deliverable:** Approval decision on 5 key questions

### 1. Approval Decision: ADR-007 (AI Disabled-by-Default)
**Status:** Currently PROPOSED  
**Action Required:** 
- [ ] Product team: Review and approve
- [ ] Security team: Review and approve  
- [ ] Architecture team: Review and approve

**If Not Approved:** Phase 1 cannot start (feature flags won't have authority to disable AI)

**Document:** `docs/engineering/adr/ADR-007-*.md` in repository

---

### 2. Technical Decision: Feature Flag Implementation
**Question:** How should feature flags be persisted and evaluated?

**Options:**
- A) Configuration file (yaml/json in git)
- B) Environment variables only
- C) Runtime database (separate service)
- D) Kubernetes ConfigMap (if using K8s)

**Recommendation:** Start with A (config file + env override), easiest for MVP

**Phase 1 Impact:** File location and loading logic depend on this choice  
**Phase 8 Impact:** How operators enable/disable AI in production

**Decision Needed By:** Week 1, before Phase 1 starts

---

### 3. Technical Decision: TrustedContext Design
**Question:** How does the host platform provide authentication/authorization context to AI?

**Required Fields:** At minimum—
- `tenant_id` (which tenant this request belongs to)
- `user_id` (which user made this request)
- `authenticated_at` (when was authentication performed)
- `permissions` array (what can this user do)

**Additional Fields:** Decide if needed—
- `ip_address` (source of request, for security)
- `mfa_verified` (was MFA used?)
- `session_id` (correlation with user session)
- `role` (user role for RBAC)

**Phase 1 Impact:** TrustedContext builder and validator types  
**Phase 2 Impact:** Gateway must pass TrustedContext to all downstream components  
**Phase 5 Impact:** Policy engine uses permissions field for eligibility checks

**Decision Needed By:** Week 1, before Phase 1 starts

**Recommendation:** Start minimal (tenant_id, user_id, authenticated_at, permissions); add fields later as needed

---

### 4. Conditional: Provider Credentials Strategy
**Question:** How will Claude/GPT API credentials be made available to adapters?

**Options:**
- A) Environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY)
- B) Secrets manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
- C) Kubernetes Secrets (if running on K8s)
- D) Config file (NOT RECOMMENDED – credential leakage risk)

**Phase 3 Impact:** Adapter client factory must read credentials from chosen source  
**Testing Impact:** Unit tests must use test doubles (never real API keys)

**Decision Needed By:** Week 2, before Phase 3 (but can be decided later if Phase 3 deferred)

**Recommendation:** Environment variables for MVP (simplest); upgrade to secrets manager for production

---

### 5. Conditional: Provider Approval
**Question:** Which AI providers are approved for MVP?

**Options:**
- A) Claude only
- B) GPT only
- C) Both Claude and GPT
- D) Neither (AI features stay disabled, Phase 3 is future work)

**Phase 3 Impact:** Determines which adapters to implement  
**Feature Flags Impact:** Only approved providers get feature flag support

**Decision Needed By:** Week 2, before Phase 3 (but can be deferred if Phase 3 deferred)

**Recommendation:** Decide on both, implement mock-first for both; real API only after provider approval

---

## Phase 1 Kickoff Checklist

**Prerequisites:** All 5 decisions above must be made

**Duration:** Weeks 1-3  
**Team Size:** 2-3 developers + 1 QA

### Step 1: Set Up Repository Structure (Day 1)

```bash
# Create Phase 1 directories
mkdir -p libs/ai-feature-flags/src
mkdir -p libs/ai-contracts/src libs/ai-contracts/src/schemas
mkdir -p libs/ai-trusted-context/src
mkdir -p ai/providers/test-doubles

# Create placeholder files (will be edited, not created fresh)
touch libs/ai-feature-flags/README.md
touch libs/ai-feature-flags/src/feature-flags.ts
touch libs/ai-feature-flags/src/types.ts

touch libs/ai-contracts/README.md
touch libs/ai-contracts/src/types.ts
touch libs/ai-contracts/src/schemas/ai-request-envelope.schema.json
touch libs/ai-contracts/src/schemas/ai-response-envelope.schema.json
touch libs/ai-contracts/src/schemas/trusted-context.schema.json
touch libs/ai-contracts/src/schemas/classification.schema.json

touch libs/ai-trusted-context/README.md
touch libs/ai-trusted-context/src/trusted-context-builder.ts
touch libs/ai-trusted-context/src/validators.ts

touch ai/providers/test-doubles/mock-provider-adapter.ts
touch ai/providers/test-doubles/fixtures/README.md
```

### Step 2: Create JSON Schemas (Days 1-2)

**File:** `libs/ai-contracts/src/schemas/ai-request-envelope.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AI Request Envelope",
  "type": "object",
  "required": ["operation", "user_input", "trusted_context", "classification"],
  "properties": {
    "request_id": { "type": "string", "description": "Unique request ID (UUID)" },
    "operation": { "enum": ["OBSERVE", "REASON", "RECOMMEND"], "description": "Operation type" },
    "user_input": { "type": "string", "description": "User input text", "maxLength": 10000 },
    "trusted_context": { 
      "type": "object",
      "description": "Authentication/authorization context from host platform",
      "required": ["tenant_id", "user_id", "authenticated_at"],
      "properties": {
        "tenant_id": { "type": "string" },
        "user_id": { "type": "string" },
        "authenticated_at": { "type": "string", "format": "date-time" },
        "permissions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "classification": {
      "type": "object",
      "description": "Data classification level",
      "required": ["data_type", "sensitivity_level"],
      "properties": {
        "data_type": { "enum": ["text", "json", "structured"] },
        "sensitivity_level": { "enum": ["public", "internal", "restricted"] },
        "requires_provider_approval": { "type": "boolean", "default": false }
      }
    },
    "metadata": { "type": "object", "description": "Optional metadata" }
  }
}
```

**File:** `libs/ai-contracts/src/schemas/ai-response-envelope.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AI Response Envelope",
  "type": "object",
  "required": ["request_id", "status", "output"],
  "properties": {
    "request_id": { "type": "string", "description": "Echoed from request" },
    "status": { "enum": ["success", "error"], "type": "string" },
    "reasoning": { "type": "string", "description": "How AI arrived at output" },
    "output": { "type": ["string", "object"], "description": "AI output (text or structured)" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1, "description": "Confidence score (0-1)" },
    "metadata": { "type": "object" },
    "error": {
      "type": "object",
      "properties": {
        "code": { "enum": ["PROVIDER_ERROR", "PROVIDER_TIMEOUT", "GATEWAY_TIMEOUT", "NOT_ENABLED", "INVALID_REQUEST"] },
        "message": { "type": "string" },
        "details": { "type": "object" }
      }
    },
    "audit_trace": { "type": "array", "items": { "type": "object" }, "description": "Audit events for this request" }
  }
}
```

### Step 3: Create TypeScript Types (Days 2-3)

**File:** `libs/ai-contracts/src/types.ts`

```typescript
// Core operation types
export type AIOperation = 'OBSERVE' | 'REASON' | 'RECOMMEND';
export type ResponseStatus = 'success' | 'error';
export type SensitivityLevel = 'public' | 'internal' | 'restricted';
export type DataType = 'text' | 'json' | 'structured';

// TrustedContext: from platform, never from user
export interface TrustedContext {
  tenant_id: string;
  user_id: string;
  authenticated_at: Date;
  permissions: string[];
  ip_address?: string;
  mfa_verified?: boolean;
  session_id?: string;
}

// Classification: metadata about data
export interface Classification {
  data_type: DataType;
  sensitivity_level: SensitivityLevel;
  requires_provider_approval?: boolean;
}

// Request from user/platform
export interface AIRequest {
  request_id: string;
  operation: AIOperation;
  user_input: string;
  trusted_context: TrustedContext;
  classification: Classification;
  metadata?: Record<string, unknown>;
}

// Response to user/platform
export interface AIResponse {
  request_id: string;
  status: ResponseStatus;
  reasoning?: string;
  output?: string | Record<string, unknown>;
  confidence?: number;
  metadata?: Record<string, unknown>;
  error?: {
    code: 'PROVIDER_ERROR' | 'PROVIDER_TIMEOUT' | 'GATEWAY_TIMEOUT' | 'NOT_ENABLED' | 'INVALID_REQUEST';
    message: string;
    details?: Record<string, unknown>;
  };
  audit_trace?: AuditEvent[];
}

// Audit event
export interface AuditEvent {
  event_id: string;
  timestamp: Date;
  actor: string; // system component name
  operation: string;
  outcome: 'success' | 'failure';
  error?: string;
  metadata?: Record<string, unknown>;
}
```

### Step 4: Implement Feature Flags (Days 3-5)

**File:** `libs/ai-feature-flags/src/types.ts`

```typescript
export interface FeatureFlagState {
  AI_ENABLED: boolean;
  AI_TEST_MODE: boolean;
  AI_PROVIDER_CLAUDE: boolean;
  AI_PROVIDER_GPT: boolean;
}

export type FeatureFlagName = keyof FeatureFlagState;
```

**File:** `libs/ai-feature-flags/src/feature-flags.ts`

```typescript
import { FeatureFlagState, FeatureFlagName } from './types';

export class FeatureFlags {
  private flags: FeatureFlagState;
  
  constructor(config: Partial<FeatureFlagState> = {}) {
    // Default: all AI features disabled
    this.flags = {
      AI_ENABLED: false,
      AI_TEST_MODE: false,
      AI_PROVIDER_CLAUDE: false,
      AI_PROVIDER_GPT: false,
      ...config,
    };
  }
  
  isEnabled(flagName: FeatureFlagName): boolean {
    // If AI_ENABLED is false, no feature is enabled
    if (flagName !== 'AI_ENABLED' && !this.flags.AI_ENABLED) {
      return false;
    }
    return this.flags[flagName];
  }
  
  getAll(): FeatureFlagState {
    return { ...this.flags };
  }
}

// Factory: load from environment
export function createFlagsFromEnv(): FeatureFlags {
  return new FeatureFlags({
    AI_ENABLED: process.env.AI_ENABLED === 'true',
    AI_TEST_MODE: process.env.AI_TEST_MODE === 'true',
    AI_PROVIDER_CLAUDE: process.env.AI_PROVIDER_CLAUDE === 'true',
    AI_PROVIDER_GPT: process.env.AI_PROVIDER_GPT === 'true',
  });
}
```

### Step 5: Implement TrustedContext (Day 5)

**File:** `libs/ai-trusted-context/src/trusted-context-builder.ts`

```typescript
import { TrustedContext } from '@libs/ai-contracts';

export class TrustedContextBuilder {
  private context: Partial<TrustedContext> = {};
  
  setTenantId(tenantId: string): this {
    if (!tenantId) throw new Error('tenant_id is required');
    this.context.tenant_id = tenantId;
    return this;
  }
  
  setUserId(userId: string): this {
    if (!userId) throw new Error('user_id is required');
    this.context.user_id = userId;
    return this;
  }
  
  setAuthenticatedAt(date: Date): this {
    if (!date) throw new Error('authenticated_at is required');
    this.context.authenticated_at = date;
    return this;
  }
  
  setPermissions(permissions: string[]): this {
    if (!permissions || !Array.isArray(permissions)) {
      throw new Error('permissions must be an array');
    }
    this.context.permissions = permissions;
    return this;
  }
  
  build(): TrustedContext {
    if (!this.context.tenant_id) throw new Error('tenant_id not set');
    if (!this.context.user_id) throw new Error('user_id not set');
    if (!this.context.authenticated_at) throw new Error('authenticated_at not set');
    if (!this.context.permissions) throw new Error('permissions not set');
    
    return this.context as TrustedContext;
  }
}
```

### Step 6: Create Mock Provider Adapter (Day 5)

**File:** `ai/providers/test-doubles/mock-provider-adapter.ts`

```typescript
import { AIRequest, AIResponse, AuditEvent } from '@libs/ai-contracts';

export interface ProviderAdapter {
  observe(request: AIRequest): Promise<AIResponse>;
  reason(request: AIRequest): Promise<AIResponse>;
  recommend(request: AIRequest): Promise<AIResponse>;
}

export class MockProviderAdapter implements ProviderAdapter {
  async observe(request: AIRequest): Promise<AIResponse> {
    const auditEvent: AuditEvent = {
      event_id: `audit-${Date.now()}`,
      timestamp: new Date(),
      actor: 'mock-provider',
      operation: 'observe',
      outcome: 'success',
    };
    
    return {
      request_id: request.request_id,
      status: 'success',
      reasoning: 'Mock provider synthesized observation',
      output: `Observed: ${request.user_input.substring(0, 50)}...`,
      confidence: 0.9,
      audit_trace: [auditEvent],
    };
  }
  
  async reason(request: AIRequest): Promise<AIResponse> {
    const auditEvent: AuditEvent = {
      event_id: `audit-${Date.now()}`,
      timestamp: new Date(),
      actor: 'mock-provider',
      operation: 'reason',
      outcome: 'success',
    };
    
    return {
      request_id: request.request_id,
      status: 'success',
      reasoning: 'Mock provider synthesized reasoning',
      output: `Analysis: Given input "${request.user_input.substring(0, 30)}...", the reasoning is synthetic`,
      confidence: 0.85,
      audit_trace: [auditEvent],
    };
  }
  
  async recommend(request: AIRequest): Promise<AIResponse> {
    const auditEvent: AuditEvent = {
      event_id: `audit-${Date.now()}`,
      timestamp: new Date(),
      actor: 'mock-provider',
      operation: 'recommend',
      outcome: 'success',
    };
    
    return {
      request_id: request.request_id,
      status: 'success',
      reasoning: 'Mock provider synthesized recommendation',
      output: `Recommendation: Based on ${request.user_input.substring(0, 20)}..., consider this action`,
      confidence: 0.75,
      audit_trace: [auditEvent],
    };
  }
}
```

### Step 7: Write Tests (Days 5-6)

**File:** `tests/unit/feature-flags.test.ts`

```typescript
import { FeatureFlags, createFlagsFromEnv } from '@libs/ai-feature-flags';

describe('FeatureFlags', () => {
  test('AI disabled by default', () => {
    const flags = new FeatureFlags();
    expect(flags.isEnabled('AI_ENABLED')).toBe(false);
  });
  
  test('Provider flags disabled if AI_ENABLED is false', () => {
    const flags = new FeatureFlags({ AI_ENABLED: false, AI_PROVIDER_CLAUDE: true });
    expect(flags.isEnabled('AI_PROVIDER_CLAUDE')).toBe(false);
  });
  
  test('Provider flags enabled when both AI and provider flag enabled', () => {
    const flags = new FeatureFlags({ AI_ENABLED: true, AI_PROVIDER_CLAUDE: true });
    expect(flags.isEnabled('AI_PROVIDER_CLAUDE')).toBe(true);
  });
});
```

### Step 8: Create README Files (Day 6)

**File:** `libs/ai-contracts/README.md`

```markdown
# AI Contracts

Shared request/response schemas for AI gateway and provider adapters.

## Usage

```typescript
import { AIRequest, AIResponse, TrustedContext } from '@libs/ai-contracts';
```

## Schemas

- `ai-request-envelope.schema.json` – Request validation
- `ai-response-envelope.schema.json` – Response validation
- `trusted-context.schema.json` – TrustedContext validation
- `classification.schema.json` – Data classification validation

## Security

Never create TrustedContext from user input. Always derive from authenticated platform context.
```

---

## Phase 1 Completion Criteria (End of Week 3)

- ✅ Feature flags library complete with tests
- ✅ Core contract types defined in TypeScript
- ✅ JSON schemas valid and documented
- ✅ TrustedContext builder with fail-closed validation
- ✅ Mock provider adapter implements all three operations
- ✅ All unit tests passing (80%+ coverage)
- ✅ Documentation complete (README files)

---

## What Gets Handed Off to Phase 2

At the end of Phase 1:
1. Feature flags library (ready to integrate into gateway)
2. Contract types and schemas (for gateway validation)
3. TrustedContext builder (for gateway to use)
4. Mock provider adapter (for gateway testing)

Phase 2 starts with: "Build gateway that validates requests against contracts and routes to mock provider"

---

## Keeping Track of Progress

Create a `PHASE_1_STATUS.md` file to track daily progress:

```markdown
# Phase 1 Implementation Status

## Week 1
- [ ] Day 1: Repository structure created
- [ ] Day 2: JSON schemas created
- [ ] Day 3: TypeScript types implemented
- [ ] Day 4: Feature flags implementation started
- [ ] Day 5: Feature flags complete, tests written

## Week 2
- [ ] Day 1: TrustedContext builder implemented
- [ ] Day 2: Mock provider adapter implemented
- [ ] Day 3: All unit tests passing
- [ ] Day 4: Documentation written
- [ ] Day 5: Code review and fixes

## Week 3
- [ ] Day 1: Integration tests passing
- [ ] Day 2: Security review
- [ ] Day 3: Architecture review
- [ ] Day 4: Approval sign-off
- [ ] Day 5: Phase 1 complete, Phase 2 kickoff

## Known Issues
- None yet

## Approved Decisions
- Feature flags: [stored in decision from Phase 0]
- TrustedContext fields: [stored in decision from Phase 0]
```

---

## Getting Help: Who to Ask

- **Architecture questions:** Review ai/ARCHITECTURE.md, ask Architecture team
- **Security questions:** Review ai/SAFETY.md, ask Security team
- **API design questions:** Review ai/gateway/CONTRACTS.md
- **Testing strategy:** Review test files in companion docs, ask QA lead
- **Approval gates:** Ask Product/Security/Architecture team leads

---

## Next: Phase 2 Starts Here

Once Phase 1 is approved, Phase 2 begins: "Build the AI Gateway"

See `AI_IMPLEMENTATION_PLAN_PHASE1_4.md` for Phase 2 detailed specification.

