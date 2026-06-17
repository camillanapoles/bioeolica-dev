# Contract: Spec 006 Validação Experimental

> Create spec.md + plan.md + tasks.md for spec 006, mapping tests/validation/ to formal VVV protocol.

## Scope

- `tests/validation/` exists with conftest.py + 6 test files
- Map each test file to a `validation_protocol` entity
- Each protocol must satisfy M3 VVV (6 certification criteria)

## Protocol Mapping

| Test File | Domain | Reference | Acceptance Criterion |
|-----------|--------|-----------|---------------------|
| `tests/validation/test_hidrologia_pressao.py` | Hidrologia | ASTM D | erro < 5% vs. experimental |
| `tests/validation/test_hidrologia_vazao.py` | Hidrologia | ASTM D | erro < 5% vs. experimental |
| `tests/validation/test_materiais_tracao.py` | Materiais | ASTM E8 | erro < 3% vs. ensaio |
| `tests/validation/test_materiais_fadiga.py` | Materiais | ASTM E466 | erro < 10% S-N curve |
| `tests/validation/test_materiais_dureza.py` | Materiais | ASTM E18 | erro < 5% HRC |
| `tests/validation/test_estrutural_vibracao.py` | Estrutural | ISO 7626 | erro < 8% modal |

## VVV Criteria per Protocol

1. **Verification (math):** mesh convergence < 5%, temporal stability < 1e-4 residual
2. **Validation (experimental):** benchmark from published data or field measurement
3. **Certified (binary):** PASS only if ALL 6 criteria met:
   - Fonte confiável (quality_score ≥ 7/10)
   - Comparação justa (same BCs, same mesh independence)
   - Erro quantificado (nominal ± IC 95%)
   - Espaço operacional coberto
   - Reprodutível (seed fixa, versões documentadas)
   - Peer review (opcional para crítica)
