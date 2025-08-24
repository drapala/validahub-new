# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the ValidaHub project.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences. ADRs help us:

- Document why decisions were made
- Share context with new team members
- Review past decisions when circumstances change
- Avoid repeating discussions

## ADR Format

We use a lightweight format based on Michael Nygard's template:

1. **Title**: ADR-NNN: Short descriptive title
2. **Date**: When the decision was made
3. **Status**: Proposed | Accepted | Deprecated | Superseded
4. **Context**: What is the issue we're addressing?
5. **Decision**: What have we decided to do?
6. **Consequences**: What happens as a result?
7. **Alternatives**: What other options were considered?

## Current ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-cqrs-architecture.md) | CQRS Architecture for Audit and Analytics | Proposed | 2025-01-14 |
| [002](002-dsl-v1-primitives.md) | DSL v1 Primitives | Accepted | 2025-01-15 |
| [003](003-bi-telemetry-architecture.md) | BI and Telemetry Architecture for Network Effects | Proposed | 2025-01-24 |

## Creating a New ADR

1. Copy the template: `cp template.md NNN-title-of-decision.md`
2. Fill in the sections
3. Submit for review via Pull Request
4. Once approved, update status to "Accepted"

## ADR Lifecycle

```
Proposed → Accepted → Deprecated/Superseded
           ↓
       Implemented
```

## Guidelines

- Keep ADRs concise but complete
- Focus on "why" more than "how"
- Include real alternatives that were seriously considered
- Update status when decisions change
- Link to related ADRs when relevant

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Michael Nygard
- [ADR Tools](https://github.com/npryce/adr-tools) - Command-line tools for working with ADRs
- [ADR GitHub Organization](https://adr.github.io/) - Collection of ADR resources