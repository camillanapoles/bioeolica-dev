---

description: "Task list for Spec 009 — CRSLR Generator (C2)"
---

# Tasks: 009 CRSLR Generator — Engineering Report Engine

**Input**: Design documents from `specs/009-crslr-generator/`

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Create directory `src/crslr/` with `__init__.py`
- [X] T002 [P] Create `src/crslr/templates/` directory for Jinja2 templates
- [X] T003 Create test file `tests/test_engine.py`

---

## Phase 2: Foundational (Blocking)

**Purpose**: Core engine that all user stories depend on

- [X] T004 Implement `src/crslr/schema.py` — input JSON validation with AnalysisResult entity (report_id, domain, metrics, vvv_status, uncertainty)
- [X] T005 [P] Create Jinja2 template `src/crslr/templates/report.md.j2` — CRSLR 5-section layout (Context, Results, Synthesis, Limitations, Recommendations)
- [X] T006 [P] Create Jinja2 template `src/crslr/templates/report.html.j2` — HTML layout with KaTeX equations for PDF rendering
- [X] T007 Implement `src/crslr/engine.py` — CRSLR engine: parse input JSON, validate via schema, render via Jinja2, output Markdown
- [X] T008 Implement `src/crslr/render.py` — Markdown → PDF conversion via WeasyPrint, optional CLI flag

**Checkpoint**: Engine generates valid Markdown report from JSON input

---

## Phase 3: User Story 1 — Engineer Generate Report (Priority: P1)

**Goal**: Engineer runs one command and receives professional engineering report

**Independent Test**: `python -m src.crslr.engine --input tests/fixtures/sample_results.json --output /tmp/test_report.md && test -f /tmp/test_report.md`

### Implementation for User Story 1

- [X] T009 [US1] Create test fixture `tests/fixtures/sample_results.json` — valid CRSLR input with all 5 sections, metrics, VVV status PASS, IC 95%
- [X] T010 [US1] Implement `src/crslr/engine.py` CLI entry point — argparse with --input, --output, --format (markdown/pdf)
- [X] T011 [US1] Add uncertainty quantification in `src/crslr/engine.py` — every numeric metric renders as "nominal ± IC 95%"
- [X] T012 [US1] Add VVV certification badge rendering in `src/crslr/engine.py` — PASS (green) / FAIL (red) / PENDING (yellow) based on vvv_status
- [X] T013 [US1] Add M9 compliance section in report template — include reference to Mapa Único index, log UUID, last review date
- [X] T014 [US1] Run validation test: `python -m src.crslr.engine --input tests/fixtures/sample_results.json --output /tmp/test_report.md && grep -c "## " /tmp/test_report.md`

**Checkpoint**: US1 complete — report has all 5 CRSLR sections, quantified uncertainty, VVV badge, M9 compliance

---

## Phase 4: User Story 2 — Stakeholder Summary (Priority: P2)

**Goal**: Non-technical stakeholder receives concise summary

**Independent Test**: Report renders with ≤ 2 pages for standard analysis

### Implementation for User Story 2

- [X] T015 [US2] Add executive summary section in template `src/crslr/templates/report.md.j2` — first page, bullet-style, max 300 words
- [X] T016 [US2] Add page-limit enforcement in `src/crslr/engine.py` — warn if generated content exceeds 2 pages for standard analysis
- [X] T017 [US2] Create test fixture `tests/fixtures/sample_results_minimal.json` — minimal input for stakeholder reports
- [X] T018 [US2] Run stakeholder validation: generate report from minimal fixture and verify ≤ 2 pages when rendered

**Checkpoint**: US2 complete — executive summary generated, page limit enforced

---

## Phase 5: Polish & Cross-Cutting

- [X] T019 [P] Verify all templates render without errors — `python -m src.crslr.engine --help`
- [X] T020 Run full test suite: `pytest tests/test_engine.py -v --tb=short`
- [X] T021 Generate golden report from sample_results.json and manually verify 5 CRSLR sections
- [ ] T022 Commit Fase 1 C2 with message "009 Fase 1: CRSLR Generator — engineering report engine"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2
- **US2 (Phase 4)**: Depends on Phase 2 — independent of US1
- **Polish (Phase 5)**: Depends on all phases complete

### Parallel Opportunities

- T002 + T003: different directories, independent
- T005 + T006: different templates, independent
- T019 + T020: independent checks

### Parallel Examples

```bash
# Phase 2 parallel
Task: "Create Jinja2 template report.md.j2"
Task: "Create Jinja2 template report.html.j2"

# Phase 3 parallel
Task: "Add uncertainty quantification in engine.py"
Task: "Add VVV certification badge in engine.py"
```

---

## Implementation Strategy

### MVP (Phase 1 + Phase 2 + Phase 3 only)

1. Complete Setup: T001-T003
2. Complete Foundational: T004-T008
3. Complete US1: T009-T014
4. **STOP**: Engineer can generate professional CRSLR report from JSON

### Incremental Delivery

1. Phase 1 + 2 → Core engine renders Markdown reports
2. Add US1 → Full CRSLR with uncertainty + VVV + M9 compliance
3. Add US2 → Stakeholder summary with page limit
4. Phase 5 → Integration verified and committed
