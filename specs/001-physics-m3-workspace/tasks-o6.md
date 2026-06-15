---

description: "Validação Experimental — calibração de modelos com dados reais de ensaio, comparação sistemática simulação vs. experimental, pipeline VVV reforçado"
---

# Tasks: Validação Experimental (FDC-U O6 Score: 0.690)

**Prerequisites**: workspaces/physics-m3/ com 30+ módulos existentes

---
## Phase 1: Setup

- [ ] T001 Criar `modules/experimental_data.py` — ingestão de dados experimentais (CSV, JSON, HDF5)
- [ ] T002 Criar `tests/test_experimental_data.py` — testes de ingestão
- [ ] T003 Criar `modules/simulation_comparison.py` — comparação sim vs exp com métricas RMSE/MAE/R²
- [ ] T004 Criar `tests/test_simulation_comparison.py` — testes de comparação
- [ ] T005 Criar `modules/model_calibration.py` — calibração de parâmetros via otimização (scipy.optimize)
- [ ] T006 Criar `tests/test_model_calibration.py` — testes de calibração
- [ ] T007 Criar `modules/vvv_reinforced.py` — pipeline VVV reforçado com métricas de certificação
- [ ] T008 Criar `tests/test_vvv_reinforced.py` — testes VVV
- [ ] T009 Integrar no `demo_completa.py`
- [ ] T010 Validar: `python demo_completa.py` — pipeline completo
