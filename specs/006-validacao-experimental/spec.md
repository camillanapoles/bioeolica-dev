# Feature Specification: Validação Experimental

**Branch**: `006-validacao-experimental`

**Status**: Draft

## Objective

Formal VVV (Verificação, Validação, Certificação) protocol for all computational models in the platform. Maps `tests/validation/` test files to formal validation protocols with ASTM/ISO references and quantified acceptance criteria.

## User Story 1 — Validation Engineer: Run VVV Protocol (Priority: P1)

A validation engineer wants to run formal VVV protocols against computational models to certify them for engineering use.

**Independent Test**: `pytest tests/validation/ -v --tb=short` passes with ≥6 protocol tests.

**Acceptance Scenarios:**
1. Given a computational model, When VVV protocol runs, Then all 6 certification criteria are evaluated
2. Given a PASS result, When reviewed, Then all criteria have documented evidence

## Certification Criteria (M3 VVV)

1. Fonte confiável (quality_score ≥ 7/10)
2. Comparação justa (same BCs, mesh independent)
3. Erro quantificado (nominal ± IC 95%)
4. Espaço operacional coberto
5. Reprodutível (seed fixa, versões documentadas)
6. Peer review (opcional para crítica)

## Protocol Mapping

| Test File | Domain | Reference | Acceptance Criterion |
|-----------|--------|-----------|---------------------|
| test_hidrologia_pressao | Hidrologia | ASTM D | erro < 5% |
| test_hidrologia_vazao | Hidrologia | ASTM D | erro < 5% |
| test_materiais_tracao | Materiais | ASTM E8 | erro < 3% |
| test_materiais_fadiga | Materiais | ASTM E466 | erro < 10% |
| test_materiais_dureza | Materiais | ASTM E18 | erro < 5% |
| test_estrutural_vibracao | Estrutural | ISO 7626 | erro < 8% |
