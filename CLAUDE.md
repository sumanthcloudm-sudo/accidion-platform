# Claude Code Project Instructions

@AGENTS.md

## Purpose

These instructions configure Claude Code as a development assistant for the Accidion Identity Cloud repository. They do not authorize production access, deployments, infrastructure changes, security-policy changes, or autonomous product actions.

The imported `AGENTS.md` is the primary engineering instruction set. `RULES.md`, `docs/ARCHITECTURE.md`, accepted ADRs, security policies, and explicit maintainer decisions remain authoritative.

## Accidion-specific working context

- Accidion Identity Cloud is a multi-tenant Identity Governance and Administration platform.
- Treat architecture and roadmap documents as intended direction, not proof of implementation.
- The six-month MVP plan governs delivery scope. Do not implement deferred capabilities without approval.
- The product's `ai/` directory is for Accidion's own AI product capabilities. It is not the configuration directory for Claude Code.
- Accidion product Copilot remains disabled by default and, if approved, is limited to observe, reason, and recommend. Claude Code must not enable or implement autonomous product execution.

## Before each task

1. Run `git status --short --branch` and inspect the current branch and working-tree changes.
2. Never overwrite, discard, reset, or reformat unrelated user changes.
3. Read the relevant source, tests, build files, documentation, and ADRs before editing.
4. State a concise plan and identify affected services, contracts, data, and security boundaries.
5. Ask for maintainer approval before any category listed in `AGENTS.md` section 5.

## Implementation expectations

- Make the smallest coherent change that satisfies the task.
- Follow existing repository conventions; do not introduce dependencies or new frameworks without approval.
- Add or update appropriate tests and documentation.
- Run `make verify` and relevant focused checks when available.
- Report commands that could not run and never invent successful test results.
- Review the complete diff for unrelated changes, secrets, unsafe defaults, and accidental scope expansion.

## Git and GitHub workflow

- Work on a task-specific feature branch, never directly on `main`.
- Do not force-push, rewrite shared history, or change branch protections.
- Push a feature branch or create a pull request only when the user explicitly asks and the required GitHub tooling is configured.
- Never approve, merge, or close a pull request on the user's behalf.
- Leave all pull requests for human review and manual merge.

## Completion report

Summarize the change, affected files, tests actually run, checks not run, security and tenant-isolation considerations, outstanding approvals, and branch or pull-request details when applicable.
