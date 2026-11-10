# ADR-010: Kubernetes remains an inactive future target

- **Status:** Proposed — pending architecture approval
- **Date:** 2026-11-10
- **Decision owner:** Architecture owner / CTO (to be assigned)
- **Scope:** Deployment platform beyond the active MVP runtime

## Context

The broader architecture may describe Kubernetes deployment assets, while the MVP baseline explicitly identifies AWS ECS Fargate as the active runtime and says Kubernetes is inactive until ADR approval.

## Proposed decision

Keep Kubernetes deployment assets inactive and non-production for the MVP. Do not create a second active deployment path, deploy workloads to Kubernetes, or introduce Kubernetes as an operational dependency unless a separate architecture decision is explicitly approved.

## Alternatives considered

- **Activate Kubernetes alongside ECS for the MVP:** Not proposed; it would introduce a second runtime path outside the current baseline.
- **Use Kubernetes as the MVP runtime instead of ECS:** Not proposed by the current MVP baseline and would require a reviewed change to ADR-001.

## Consequences and constraints

- Any Kubernetes manifests, Helm charts, Kustomize overlays, or GitOps materials must be labelled inactive/future-target until approval.
- ECS remains the active MVP runtime proposal.
- A future activation decision must address operational ownership, security, networking, observability, deployment, cost, and migration implications.
- This ADR does not provision clusters, modify IaC, or activate Kubernetes assets.

## Approval

- **Approver:** Pending
- **Approval date:** Pending
- **Implementation evidence:** Not established by this ADR.
