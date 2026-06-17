# Data Model — CRSLR Generator

## Entity: ReportSection

| Field | Type | Description |
|-------|------|-------------|
| section_id | TEXT | `context`, `results`, `synthesis`, `limitations`, `recommendations` |
| title | TEXT | Section header |
| content | TEXT | Markdown body |
| priority | INTEGER | Display order (1-5) |
| required | BOOLEAN | Section is mandatory |

## Entity: AnalysisResult (input)

| Field | Type | Description |
|-------|------|-------------|
| analysis_id | TEXT | UUID |
| domain | TEXT | Domain name |
| metrics | JSON | Key-value numeric results |
| uncertainty | JSON | IC 95% per metric |
| vvv_status | TEXT | `PASS`/`FAIL`/`PENDING` |
| metadata | JSON | Analysis metadata |
