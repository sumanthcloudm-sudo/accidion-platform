# Accidion AI Module: Phased Implementation Plan
## Executive Summary & Dependencies

**Created:** After comprehensive analysis of Accidion Platform repository  
**Scope:** Complete phased roadmap for AI runtime components (8 phases, ~26 weeks)  
**Authority:** Accidion MVP six-month plan; all ADRs are Proposed (pending approval)  
**Constraint:** NO file modifications, NO Product Copilot enabled

---

## What This Plan Covers

This comprehensive roadmap addresses all 8 major missing AI runtime components identified in the repository analysis:

1. **Feature Flags** – Disabled-by-default AI control mechanism (PHASE 1)
2. **AI Gateway** – Request validation, routing, response normalization (PHASE 2)
3. **Provider Adapters** – Claude and GPT integrations (PHASE 3)
4. **Guardrails** – 15 safety controls covering injection, redaction, validation (PHASE 4)
5. **Policy Engine** – Eligibility, classification enforcement, data blocking (PHASE 5)
6. **Prompt Registry** – Versioned prompts, audit, rollback (PHASE 6)
7. **Evaluation Runner** – Synthetic test harness for safety validation (PHASE 7)
8. **Integration & Audit** – E2E workflows, monitoring, documentation (PHASE 8)

---

## High-Level Timeline

| Phase | Weeks | Component | Status |
|-------|-------|-----------|--------|
| 1 | 1-3 | Feature flags, test doubles, contracts, trusted context | Pending approval |
| 2 | 4-6 | Gateway validation, routing, normalization | Depends on Phase 1 |
| 3 | 7-10 | Claude and GPT adapters (mock-first) | Depends on Phases 1-2 |
| 4 | 11-14 | 15 guardrails, injection detection, data redaction | Depends on Phases 2-3 |
| 5 | 15-18 | Policy engine, eligibility, classification, blocking | Depends on Phases 1-4 |
| 6 | 19-21 | Prompt registry, versioning, audit, rollback | Depends on DB schema |
| 7 | 22-24 | Evaluation harness, case execution, safety reports | Depends on Phases 3-4 |
| 8 | 25-26 | E2E workflows, audit integration, monitoring, docs | Depends on Phases 1-7 |

**Total Duration:** ~26 weeks (6 months), with limited parallelization (Phases 5 and 7 can start earlier)

---

## Critical Approvals Required

**None of these phases can start until approval is obtained:**

### Before Phase 1 (Blocking all phases):
- ✅ **ADR-007 Decision:** "AI Copilot disabled-by-default" – Currently PROPOSED
- ✅ **Feature Flag Strategy:** Config file vs. runtime vs. database approach
- ✅ **TrustedContext Design:** Which fields required; how host provides authentication/authorization

### Before Phase 3 (Provider Adapters):
- ✅ **Provider Approval:** Which of Claude/GPT approved for MVP?
- ✅ **Credentials Strategy:** Environment variables? Secrets manager (Vault/AWS Secrets)?
- ✅ **API Contract:** Which Claude model versions? Which GPT models?

### Before Phase 5 (Policy Engine):
- ✅ **Policy Rules Definition:** Which use cases are eligible for AI? Which are prohibited?
- ✅ **Data Classification Scheme:** Sensitivity levels? What triggers Restricted classification?
- ✅ **Feature Flag Scope:** Tenant-level? User-level? Operation-level?

### Before Phase 6 (Prompt Registry):
- ✅ **Database Schema:** Which database (PostgreSQL/MySQL/etc.)? Migration tool?
- ✅ **Versioning Strategy:** Semantic versioning? Hash-based? Deployment tagging?

### Before Phase 8 (Integration):
- ✅ **Audit Storage:** Which backend (database/log streaming/cloud)?
- ✅ **Metrics Backend:** Prometheus? CloudWatch? Custom time-series database?
- ✅ **Production Target:** Kubernetes? Container? Serverless?

---

## Key Design Principles (From Existing Documentation)

Every implementation must respect:

1. **Fail-Closed Security** (SAFETY.md)
   - When in doubt, reject request
   - Never grant access/capability when authorization unclear
   - Return errors to caller, don't attempt recovery silently

2. **Disabled-by-Default** (ADR-007)
   - AI features disabled by default
   - Require explicit feature flag to enable
   - No autonomous execution; only observe/reason/recommend

3. **Tenant Isolation** (ARCHITECTURE.md)
   - TrustedContext from platform, never from user input
   - Every audit event includes tenant_id
   - Verify tenant_id consistency throughout request/response

4. **No Secrets in Code** (RULES.md)
   - Provider credentials only via environment variables
   - No API keys in tests or repository
   - Use test doubles until credentials provided

5. **Guardrails Non-Bypassable** (GUARDRAILS_IMPLEMENTATION_PLAN.md)
   - 15 guards executed in sequence, fail-fast
   - Injection detection before request reaches provider
   - Data redaction happens to all provider responses
   - Cannot be disabled without feature flag override

6. **Audit Everything** (AI_AUDIT_EVENT_CONTRACT.md)
   - Record every AI request, guardrail trigger, provider call, response generation
   - Never log raw prompt/response (redact PII, credentials, secrets)
   - Immutable audit trail for compliance and debugging

---

## What Already Exists (Don't Rewrite)

### Existing Complete Work:
- ✅ **AI evaluation case catalog validator** (`scripts/validate/ai_evaluation_cases.py`)
  - 200+ lines, comprehensive, well-tested
  - Validates JSON schema for 5 synthetic test cases
  - Reuse this in Phase 7 case loader
  
- ✅ **5 Synthetic evaluation cases** (`ai/evaluations/cases/*.json`)
  - prompt-injection.json
  - tenant-isolation.json
  - sensitive-data-leakage.json
  - unsafe-access-recommendation.json
  - invalid-output.json
  - Use these to test guardrails (Phase 4) and evaluation runner (Phase 7)

- ✅ **Comprehensive design documents:**
  - ai/ARCHITECTURE.md – Trust model, request flow, isolation
  - ai/SAFETY.md – Security requirements, disabled-by-default principle
  - ai/gateway/CONTRACTS.md – Request/response schemas
  - ai/providers/PROVIDER_INTERFACE.md – Adapter interface
  - ai/policies/POLICY_ENGINE.md – Eligibility and classification rules
  - ai/guardrails/GUARDRAILS_IMPLEMENTATION_PLAN.md – 15 guardrails specification
  - ai/evaluations/HARNESS_DESIGN.md – Evaluation runner architecture
  - ai/audit/AI_AUDIT_EVENT_CONTRACT.md – Audit event schema
  - All design documents are complete; implement according to them

### Existing Placeholder Work (Will Be Replaced):
- ❌ `.gitkeep` files in all service directories (will be replaced with Phase 1-8 implementations)
- ❌ Empty Terraform modules in infrastructure/ (separate from AI implementation)
- ❌ Minimal CI/CD (verify.yml only checks structure; will add AI tests)

---

## Implementation Sequence: Why Phases Can't Be Reordered

```
PHASE 1 (Feature Flags, Contracts, Trusted Context)
   ↓
PHASE 2 (Gateway) ← Requires PHASE 1 contracts
   ↓
PHASE 3 (Provider Adapters) ← Requires PHASE 2 gateway + PHASE 1 test doubles
   ↓
PHASE 4 (Guardrails) ← Requires PHASE 3 adapters + PHASE 2 gateway
   ↓
PHASE 5 (Policy Engine) ← Requires PHASE 4 guardrails + PHASE 1 feature flags
   ↓
PHASE 6 (Prompt Registry) ← Requires PHASE 1 contracts + database schema (independent path)
   ↓
PHASE 7 (Evaluation Runner) ← Requires PHASE 3 providers + PHASE 4 guardrails
   ↓
PHASE 8 (Integration & Audit) ← Requires all Phases 1-7 complete
```

**Limited Parallelization Opportunities:**
- Phase 5 can start during Phase 4 (Week 11) once guardrails interface stable
- Phase 6 can start during Phase 4 (Week 11) if database schema approved
- Phase 7 can start during Phase 4 (Week 11) with mock providers from Phase 1
- All others are strictly sequential

---

## File Locations: Where Code Goes

### New Directories to Create:

```
libs/
├── ai-feature-flags/          ← PHASE 1
├── ai-contracts/              ← PHASE 1
└── ai-trusted-context/        ← PHASE 1

ai/
├── gateway/                   ← PHASE 2
│   └── src/
├── providers/                 ← PHASE 3
│   ├── claude/
│   ├── gpt/
│   └── test-doubles/          ← PHASE 1
├── guardrails/                ← PHASE 4
│   └── src/
├── policies/                  ← PHASE 5
│   └── src/
├── prompts/                   ← PHASE 6
│   └── src/
├── evaluations/               ← PHASE 7
│   └── src/
├── audit/                     ← PHASE 8
│   └── src/
└── observability/             ← PHASE 8
    └── src/

tests/
├── unit/                      ← Each phase adds test files
├── integration/               ← Each phase adds test files
├── e2e/                       ← PHASE 8 only
└── security/                  ← PHASE 4 and 8
```

### Existing Files to Update:

- `docs/engineering/adr/ADR-007-*.md` ← Requires approval before Phase 1
- `docs/engineering/adr/ADR-011-*.md` ← Create at end of Phase 8 (summary ADR)
- `scripts/validate/ai_evaluation_cases.py` ← Already complete, reuse in Phase 7
- `Makefile` ← Add targets for each phase's tests
- `package.json` or `.csproj` ← Add dependencies as needed per phase
- `CI/CD workflow` ← Add AI tests to verify.yml

---

## Testing Strategy by Phase

| Phase | Unit Tests | Integration Tests | E2E Tests | Security Tests |
|-------|-----------|------------------|-----------|----------------|
| 1 | Yes (80%+) | Yes | No | Yes (feature flags) |
| 2 | Yes (85%+) | Yes | No | Yes (tenant isolation) |
| 3 | Yes (85%+) | Yes | No | Yes (adapter contracts) |
| 4 | Yes (90%+) | Yes | No | Yes (injection, redaction) |
| 5 | Yes (80%+) | Yes | No | Yes (policy enforcement) |
| 6 | Yes (80%+) | Yes | No | Yes (audit immutability) |
| 7 | Yes (75%+) | Yes | No | Yes (synthetic cases) |
| 8 | Yes (varies) | Yes | Yes | Yes (all domains) |

**Target Coverage:** 85%+ for core logic (gateway, guardrails, policy engine); 90%+ for security-critical code

---

## Known Unknowns (Decisions Needed)

### Technical Decisions:
- Language for services – Python? Go? TypeScript? Java?
- Feature flag persistence – Configuration file? Runtime database? K8s ConfigMap?
- Secrets management – Environment variables? HashiCorp Vault? AWS Secrets Manager? Azure Key Vault?
- Test framework – Jest? Mocha? Python unittest? Go testing?
- Async execution – Guardrails blocking? Audit logging async? Retry async?
- Metric backend – Prometheus? CloudWatch? Datadog? Custom?

### Process Decisions:
- Approval workflow – Who signs off each phase? Architecture team? Product? Security?
- Release strategy – Which components release together? Feature-flag-locked releases?
- Monitoring on-call – Who responds to AI errors in production?
- Incident response – Playbook for audit log corruption? Provider API outage?

### Product Decisions:
- MVP scope – Which of the 8 components must be in MVP vs. post-MVP?
- Provider choice – Claude only? GPT only? Both? Others?
- Use case prioritization – Which eligibility rules apply to MVP?
- Data classification – Which sensitivity levels?

---

## Success Criteria: Phases Complete

✅ **Phase 1 Success:** Feature flags prevent AI execution; mock provider ready; contracts validated  
✅ **Phase 2 Success:** Gateway validates all requests, routes correctly, returns errors appropriately  
✅ **Phase 3 Success:** Provider adapters handle mock responses; error mapping complete  
✅ **Phase 4 Success:** 15 guardrails implemented; injection test case passes; redaction verified  
✅ **Phase 5 Success:** Policy engine blocks Restricted data; eligibility rules enforced  
✅ **Phase 6 Success:** Prompts versioned, audit logs changes, rollback works  
✅ **Phase 7 Success:** All 5 evaluation cases pass; safety report generated  
✅ **Phase 8 Success:** E2E workflows pass; audit events emitted; monitoring operational; docs complete

---

## Document Organization

This plan consists of THREE companion documents:

1. **AI_IMPLEMENTATION_PLAN_PHASE1_4.md** (This Directory)
   - Detailed Phase 1: Feature flags, test doubles, contracts, trusted context
   - Detailed Phase 2: Gateway (validation, routing, normalization)
   - Detailed Phase 3: Provider adapters (Claude, GPT, error handling)
   - Detailed Phase 4: Guardrails (15 controls, injection, redaction)

2. **AI_IMPLEMENTATION_PLAN_PHASE5_8.md** (This Directory)
   - Detailed Phase 5: Policy engine (eligibility, classification, data blocking)
   - Detailed Phase 6: Prompt registry (versioning, audit, rollback)
   - Detailed Phase 7: Evaluation runner (harness, case execution, reports)
   - Detailed Phase 8: Integration & audit (E2E, monitoring, documentation)
   - Approval gates and completion criteria
   - Dependencies matrix and timeline
   - Test strategy summary
   - File structure and approval requirements

3. **This Document: AI_IMPLEMENTATION_PLAN_SUMMARY.md**
   - Executive summary (you are here)
   - High-level timeline and critical approvals
   - Design principles (fail-closed, disabled-by-default, tenant isolation)
   - What already exists (don't rewrite)
   - Implementation sequence and parallelization
   - Known unknowns and decisions needed
   - Success criteria

---

## Next Steps: How to Use This Plan

### For Product Team:
1. Review approval gates (previous section)
2. Obtain decisions on provider choice, data classification, policy rules
3. Approve ADR-007 (AI disabled-by-default)
4. Schedule Phase 1 kickoff once approvals in place

### For Architecture Team:
1. Review all 8 design documents in `ai/` directory
2. Validate phase dependencies (can we reorder? parallelize more?)
3. Select implementation language and test framework per phase
4. Design database schema for Phase 6 (prompt registry)
5. Design monitoring/audit backend strategy (Phase 8)

### For Security Team:
1. Review SAFETY.md and all design documents
2. Validate guardrails specification (Phase 4)
3. Validate audit event contract (Phase 8)
4. Approve tenant isolation approach (Phase 1-2)
5. Security review Phase 8 completion before production

### For Development Team:
1. Assign team members to phases (aim for 3-4 people for 26 weeks)
2. Read companion documents (PHASE1_4 and PHASE5_8) in detail
3. Set up dev environment: testing framework, feature flag library, logging
4. Phase 1 starts with: feature flags library, test doubles, contracts
5. Run synthetic evaluation cases continuously (Phases 4-8)

### For Operations/DevOps:
1. Plan infrastructure for AI components (container size, memory, CPU)
2. Design secrets management (how will provider credentials be deployed?)
3. Set up monitoring backend (metrics, tracing, logs)
4. Plan high-availability for critical components (gateway, audit logging)
5. Develop incident response playbooks for AI failures

---

## Conclusion

This plan represents a complete, sequenced roadmap to implement all 8 missing AI runtime components over 26 weeks (6 months), aligned with Accidion's MVP scope, architecture, and security constraints.

**Key Success Factors:**
- Start with Phase 1 approval (feature flags, contracts, trusted context)
- Maintain fail-closed security throughout all phases
- Use synthetic test cases to verify safety goals (Phase 7)
- Keep AI disabled by default until explicitly enabled via feature flags
- Audit every decision for compliance and debugging
- Involve Product, Architecture, Security, and Development teams at approval gates

**Companion Documents:**
- See `AI_IMPLEMENTATION_PLAN_PHASE1_4.md` for detailed Phases 1-4
- See `AI_IMPLEMENTATION_PLAN_PHASE5_8.md` for detailed Phases 5-8

