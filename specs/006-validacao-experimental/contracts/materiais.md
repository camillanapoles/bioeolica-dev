# Contract: Materiais Validation Protocol

## Protocol: Tração

| Campo | Valor |
|-------|-------|
| Test File | `tests/validation/test_materiais_tracao.py` |
| Reference | ASTM E8 (tension testing) |
| Acceptance | erro < 3% vs. ensaio |
| VVV Criteria | 6/6 required |

## Protocol: Fadiga

| Campo | Valor |
|-------|-------|
| Test File | `tests/validation/test_materiais_fadiga.py` |
| Reference | ASTM E466 (fatigue testing) |
| Acceptance | erro < 10% S-N curve |
| VVV Criteria | 6/6 required |

## Protocol: Dureza

| Campo | Valor |
|-------|-------|
| Test File | `tests/validation/test_materiais_dureza.py` |
| Reference | ASTM E18 (Rockwell hardness) |
| Acceptance | erro < 5% HRC |
| VVV Criteria | 6/6 required |
