# Feature Specification: CRSLR Generator — Engineering Report Engine

**Feature Branch**: `009-crslr-generator`

**Status**: Draft

## Objective

Generate structured engineering reports following the CRSLR format (Context → Results → Synthesis → Limitations → Recommendations) from computational analysis results. M9 compliance: every communication must include context, quantified uncertainty, VVV status, and traceability.

## User Story 1 — Engineer: Generate Technical Report (Priority: P1)

An engineer wants to generate a professional engineering report from analysis results with one command.

**Independent Test**: `python -m src.crslr generate --input results.json --output report.pdf` succeeds.

**Acceptance Scenarios:**
1. Given analysis results JSON, When CRSLR generates, Then output contains all 5 sections (Context, Results, Synthesis, Limitations, Recommendations)
2. Given a result with quantified uncertainty, When report generates, Then every numeric value includes IC 95%
3. Given a result with VVV status PASS, When report generates, Then certification badge is included

## User Story 2 — Stakeholder: Receive Communication (Priority: P2)

A non-technical stakeholder wants a concise executive summary with clear recommendations.

**Independent Test**: Report renders with `< 2 pages` for standard analysis.

## Technical Approach

### Pipeline

```
results.json → CRSLR Engine → Jinja2 Template → PDF (WeasyPrint) / Markdown
```

### Data Flow

1. Parse results JSON: compliance, density field, VVV status, metadata
2. Map to CRSLR sections via template
3. Quantify uncertainty: all numbers → nominal ± IC 95%
4. Render via Jinja2: LaTeX-style equations via KaTeX
5. Output: Markdown (default) + PDF (optional, WeasyPrint)

## Out of Scope

- Interactive dashboards (future spec)
- Real-time report streaming
- Multi-language report generation
