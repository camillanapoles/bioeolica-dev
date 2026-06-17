# Bioeólica Dev — Guia de Uso Completo

> Plataforma de simulação multifísica com 3 workspaces integrados. PQMS 92.2%.
> 839 testes | 7.109 símbolos | 11.513 relações | 179 fluxos de execução

---

## Sumário

1. [Instalação Rápida](#1-instalação-rápida)
2. [Arquitetura do Projeto](#2-arquitetura-do-projeto)
3. [Funcionalidades por Workspace](#3-funcionalidades-por-workspace)
4. [Casos de Uso Testados](#4-casos-de-uso-testados)
5. [Comandos Makefile](#5-comandos-makefile)
6. [Como Usar as Funcionalidades](#6-como-usar-as-funcionalidades)
7. [Pipeline CI/CD](#7-pipeline-cicd)
8. [VVV — Verificação, Validação, Certificação](#8-vvv)
9. [Infraestrutura Cross-Workspace](#9-infraestrutura-cross-workspace)
10. [Relatório de Compliance](#10-relatório-de-compliance)
11. [Implementado vs Não Implementado](#11-implementado-vs-não-implementado)
12. [Solução de Problemas](#12-solução-de-problemas)

---

## 1. Instalação Rápida

### Sem dependências de sistema (CPU-only)

```bash
git clone https://github.com/camillanapoles/bioeolica-dev.git
cd bioeolica-dev
pip install -e workspaces/physics-m3 -e workspaces/cad-cae-platform -e workspaces/kdi-m3-bridge
make test-quick
```

### Com GPU (opcional)

```bash
pip install cupy-cuda12x  # Deve corresponder ao CUDA toolkit instalado
make test
```

### Com Docker (inclui CalculiX + Gmsh)

```bash
docker build -f Dockerfile.ci -t bioeolica-ci .
docker run --rm bioeolica-ci make test
```

### Verificação

```bash
python scripts/compliance/report.py
# PQMS atual: 92.2% | 8/8 NC fechadas | 839 testes PASS
```

---

## 2. Arquitetura do Projeto

### Estrutura

```
bioeolica-dev/
├── workspaces/
│   ├── physics-m3/          # 41 módulos de física e simulação
│   │   ├── modules/          # (legado) imports por from modules.xxx
│   │   ├── src/physics_m3/   # (canonical) imports por from physics_m3.xxx
│   │   │   ├── vvv/          # VVV multi-escala C11 (6 critérios)
│   │   │   └── gpu/          # GPUAccelerator com fallback CPU
│   │   └── tests/            # ~700 testes
│   ├── cad-cae-platform/     # 6 módulos CAD/CAE
│   │   ├── modules/          # (legado)
│   │   ├── src/cad_cae/      # (canonical)
│   │   └── tests/            # 63 testes
│   └── kdi-m3-bridge/        # 7 módulos de acoplamento multi-física
│       ├── modules/          # (legado)
│       ├── src/kdi_m3/       # (canonical)
│       └── tests/            # 63 testes
├── .github/workflows/ci.yml  # CI pipeline
├── Makefile                  # Comandos unificados
├── Dockerfile.ci             # Docker com CalculiX + Gmsh
├── .gitattributes            # Git LFS para meshes/VTK/STEP
└── scripts/compliance/       # Gerador de relatório de compliance
```

### Workspace → src package mapping

| Workspace | Pacote | Import canonical | Módulos |
|-----------|--------|------------------|---------|
| physics-m3 | `physics_m3` | `from physics_m3.erosion import ErosionModel` | 41 |
| cad-cae-platform | `cad_cae` | `from cad_cae.cad_bridge import CadModel` | 6 |
| kdi-m3-bridge | `kdi_m3` | `from kdi_m3.config_manager import ConfigManager` | 7 |

---

## 3. Funcionalidades por Workspace

### 3.1 physics-m3 — Física e Simulação (41 módulos)

| Domínio | Módulo | Classes/Funções | Testes |
|---------|--------|-----------------|--------|
| **Materiais Compósitos** | `composite_model.py` | `CompositeMaterial` | 3 |
| **Erosão** | `erosion.py` | `ErosionModel` (Finnie) | 7 |
| **Fadiga** | `fatigue.py` | SN curve, Goodman, Miner | 24 |
| **Fluidos** | `fluid_dynamics.py` | `Airfoil`, BL, Re | 32 |
| **FEM** | `fem_solver.py` | `FEMSolver`, `FEAMesh` | 4 |
| **Termodinâmica** | `thermodynamics.py` | condução, convecção | 24 |
| **Eletromecânica** | `electromechanical.py` | Motor/Generator | 30 |
| **Otimização Topológica** | `topology_optimization.py` | SIMP, BESO | 46 |
| **Otimização Avançada** | `topopt_avancada.py` | Multi-objetivo | 69 |
| **Creep** | `creep.py` | Norton-Bailey | 25 |
| **Piezoeletricidade** | `piezoelectric.py` | Acoplamento | 22 |
| **Peridinâmica** | `peridynamics.py` | Fratura não-local | 3 |
| **Incerteza** | `uncertainty.py` | MC, intervalo | 3 |
| **Validação Experimental** | `validacao_experimental.py` | Calibração | 27 |
| **Manutenção Preditiva** | `predictive_maintenance.py` | Degradação | 13 |
| **Gêmeo Digital** | `digital_twin.py` | Sensor fusion | 20 |
| **Rede de Cristal** | `crystal_lattice.py` | Estrutura cristalina | 22 |

### 3.2 cad-cae-platform — CAD/CAE (6 módulos)

| Módulo | Função | Testes |
|--------|--------|--------|
| `cad_bridge.py` | `CadModel` — box, cylinder, sphere, extrude, union, cut | 16 |
| `calculix_solver.py` | `FEMSolver` — interface CalculiX | 11 |
| `gmsh_mesher.py` | `MeshGenerator` — malha 2D/3D | 7 |
| `gpu_accelerator.py` | `GPUAccelerator` — CG solver GPU/CPU | 6 |
| `vtk_export.py` | `write_vtu`, `write_vtp` — exportação VTK | 6 |
| `design_optimizer.py` | `DesignSpace`, `DesignOptimizer` | 13 |

### 3.3 kdi-m3-bridge — Acoplamento Multi-Física (7 módulos)

| Módulo | Função | Testes |
|--------|--------|--------|
| `config_manager.py` | Config JSON + runtime | 16 |
| `kdi_macro.py` | Análise macro-escala | 11 |
| `kdi_meso.py` | Análise meso-escala | 4 |
| `kdi_micro.py` | Análise micro-escala | 4 |
| `kdi_multiphysics.py` | Acoplamento FSI + termo-mecânico | 8 |
| `kdi_forwarder.py` | Encaminhamento entre escalas | 6 |
| E2E | Fluxo completo M³ | 10 |

### 3.4 VVV Multi-Escala C11 (Spec 007)

| Componente | Critério | Tolerância |
|------------|----------|------------|
| `vvv.certificate.VVVCertificate` | Container 6 critérios + return_phase | — |
| `vvv.criteria.convergence` | Mesh convergence < 5% entre 3 refinos | 5% |
| `vvv.criteria.stability` | Temporal stability residual < 1e-4 | 1e-4 |
| `vvv.criteria.conservation` | Mass/energy balance < 1% | 1% |
| `vvv.criteria.benchmark` | Benchmark correlation > 90% | 10% |
| `vvv.criteria.cross_code` | Cross-code agreement < 5% | 5% |
| `vvv.criteria.units` | SI dimensional consistency | 80% |
| `vvv.orchestrator.VVVOrchestrator` | Run all 6 + PASS/FAIL | — |

---

## 4. Casos de Uso Testados

### Caso 1: Viga Engastada (Cantilever Beam)

```python
from physics_m3.mechanical_tests import flexure_test
from physics_m3.vvv import VVVOrchestrator

# Simulação FEM
result = flexure_test(E=70e9/1e9, strength_MPa=250, length_mm=2000, width_mm=50, thickness_mm=100)

# Certificação VVV
orch = VVVOrchestrator(domain="mecanica", scale="meso")
cert = orch.run_all(
    convergence_errors=[8.0, 3.0, 1.2],
    convergence_h=[0.5, 0.25, 0.125],
    mass_balance_error=0.3,
    energy_balance_error=0.5,
)
print(cert.overall_status)  # PASS
```

**Benchmark**: δ = PL³/(3EI) — erro < 5% validado em `test_benchmarks/test_cantilever_beam.py`.

### Caso 2: Placa com Furo (Kirsch Kt)

```python
from physics_m3.vvv.criteria.benchmark import BenchmarkCorrelationCriterion
from physics_m3.vvv.criteria.cross_code import CrossCodeCriterion

# Validar Kt → 3.0 (Kirsch 1898)
bench = BenchmarkCorrelationCriterion(tolerance_pct=10)
result = bench.evaluate_analytical(numerical=10.5, analytical=10.0)
assert result.passed  # ✅ erro 5% < 10%

# Cross-code: método A vs método B
cross = CrossCodeCriterion()
result = cross.evaluate([100, 200, 300], [102, 198, 305])
assert result.passed  # ✅ max Δ < 5%
```

### Caso 3: Pressão de Vento (NBR 6123)

```python
from physics_m3.tests.test_benchmarks.test_wind_pressure import (
    dynamic_pressure, cp_rectangular_windward
)

# Cálculo de carga de vento para fachada 50m² a 45 m/s
q = dynamic_pressure(45.0)  # 1241 Pa
Cp = cp_rectangular_windward()  # 0.8
F = q * Cp * 50  # ~49.7 kN
```

### Caso 4: Erosão de Pá Eólica (Finnie)

```python
from physics_m3.erosion import ErosionModel

model = ErosionModel(material_density=2700, hardness=3e9)
r = model.finnie_erosion(mass=1e-6, velocity=50, angle=30)
print(f"Volume removido: {r['volume_removed']:.2e} m³")
print(f"Taxa de erosão: {r['erosion_rate']:.2e}")

# Erosão em pá de turbina
blade = model.blade_erosion(tip_speed=80, chord=0.3)
print(f"Profundidade anual: {blade['max_erosion_depth']*1000:.2f} mm")
```

### Caso 5: Fadiga de Material Compósito

```python
from physics_m3.fatigue import FatigueAnalysis
from physics_m3.composite_model import CompositeMaterial

mat = CompositeMaterial(E1=150e9, E2=10e9, G12=5e9, nu12=0.3)
fatigue = FatigueAnalysis(mat)
life = fatigue.sn_curve(stress_range=300e6, R_ratio=-1)
print(f"Vida em fadiga: {life:.0f} ciclos")
```

### Caso 6: Eletromecânica — Motor Síncrono

```python
from physics_m3.electromechanical import SynchronousMachine
motor = SynchronousMachine()
torque = motor.torque(V=400, f=50, delta_deg=30)
print(f"Torque: {torque:.1f} N·m")
```

---

## 5. Comandos Makefile

| Comando | Descrição | Tempo |
|---------|-----------|-------|
| `make setup` | Instala workspaces + dev deps | ~30s |
| `make test` | Suite completa physics-m3 | ~75s |
| `make test-quick` | Benchmarks + VVV (validação rápida) | ~0.5s |
| `make test-kdi` | Testes kdi-m3-bridge | ~2s |
| `make coverage` | Cobertura com pytest-cov | ~80s |
| `make clean` | Remove __pycache__, .pytest_cache | ~1s |
| `make lint` | Ruff check | ~2s |
| `make install-docs` | Exibe deps de sistema | instantâneo |

---

## 6. Como Usar as Funcionalidades

### 6.1 Modelagem Computacional

```python
# Análise estrutural completa: material → geometria → FEM → validação
from physics_m3.composite_model import CompositeMaterial
from physics_m3.mechanical_tests import flexure_test, tensile_test
from physics_m3.structural_analysis import stress_analysis
from physics_m3.vvv import VVVOrchestrator

# 1. Material
mat = CompositeMaterial(E1=150e9, E2=10e9, G12=5e9, nu12=0.3)

# 2. Ensaio mecânico
result = flexure_test(E=70, strength_MPa=250, length_mm=2000, width_mm=50, thickness_mm=100)

# 3. Análise de tensões
stresses = stress_analysis(force_N=5000, area_m2=0.01, moment_Nm=1000, I_m4=1e-6)

# 4. Certificação VVV
orch = VVVOrchestrator(domain="mecanica", scale="meso")
cert = orch.run_all(mass_balance_error=0.1, energy_balance_error=0.2)
print(f"Status: {cert.overall_status}")
```

### 6.2 Otimização Topológica

```python
from physics_m3.topology_optimization import TopOpt
from physics_m3.topopt_avancada import topopt_simp

# Otimização SIMP clássica
opt = TopOpt()
result = opt.optimize(vol_frac=0.3, penalty=3.0)

# Otimização multi-objetivo
from physics_m3.topopt_multiobj import MultiObjectiveTopOpt
mopt = MultiObjectiveTopOpt()
pareto = mopt.optimize()
```

### 6.3 Análise de Incerteza

```python
from physics_m3.uncertainty import UncertaintyAnalyzer, SensitivityAnalyzer

# Propagação de incerteza via Monte Carlo
analyzer = UncertaintyAnalyzer()
result = analyzer.propagate(n_samples=10000)

# Análise de sensibilidade global
sensitivity = SensitivityAnalyzer()
sa_result = sensitivity.analyze()
```

### 6.4 Acoplamento Multi-Física (FSI)

```python
from kdi_m3.kdi_multiphysics import MultiPhysicsCoupling, FSIAnalysis

fsi = FSIAnalysis()
result = fsi.coupled_analysis(fluid_pressure=1e5, structural_stiffness=70e9)
print(f"Deformação acoplada: {result['deformation_m']:.4f} m")
```

---

## 7. Pipeline CI/CD

O CI executa automaticamente em push/PR para `main`:

```yaml
# .github/workflows/ci.yml
Jobs:
  1. Setup → pip install -e workspaces/*
  2. Quick tests → benchmarks + VVV
  3. physics-m3 suite → 713 tests
  4. cad-cae suite → 63 tests
  5. kdi-m3-bridge suite → 63 tests
```

**Runtime target**: < 15 minutos. Atual: ~2 min (paralelizável com xdist).

---

## 8. VVV — Verificação, Validação, Certificação

### Protocolo de 6 Critérios

```python
from physics_m3.vvv import VVVOrchestrator

orch = VVVOrchestrator(domain="fluidos", scale="macro")
result = orch.run_all(
    convergence_errors=[8.0, 3.0, 1.2],  # monótono decrescente + < 5%
    convergence_h=[0.5, 0.25, 0.125],
    stability_residuals=[1e-2, 1e-3, 5e-5],  # residual < 1e-4
    mass_balance_error=0.3,    # < 1%
    energy_balance_error=0.5,  # < 1%
    numerical_value=10.5,
    analytical_value=10.0,     # erro 5% < 10%
    cross_code_a=[100, 200, 300],
    cross_code_b=[102, 198, 305],
    units_quantities={"stress": (1e6, "pressure"), "velocity": (10.0, "velocity")},
)
print(result.to_dict())
# {'overall_status': 'PASS', 'return_phase': None, 'criteria': {...}, ...}
```

### Passo a passo da certificação

1. **Convergência de malha** — 3 níveis de refinamento, erro < 5%
2. **Estabilidade temporal** — redução de Δt, residual < 1e-4
3. **Conservação** — balanço de massa e energia < 1%
4. **Benchmark** — correlação com solução analítica > 90%
5. **Cross-code** — 2+ implementações independentes
6. **Unidades** — consistência dimensional SI > 80%

Se **qualquer critério falha** → `status = FAIL` + `return_phase` sugerido:
- `F5→F1`: unidades inconsistentes (rever contexto)
- `F5→F3`: conservação/benchmark falhou (rever escalas)
- `F5→F4`: malha/estabilidade/cross-code falhou (rever ferramenta)

---

## 9. Infraestrutura Cross-Workspace

### Imports diretos (sem hacks)

```python
# Qualquer workspace → qualquer outro:
from physics_m3.composite_model import CompositeMaterial
from cad_cae.cad_bridge import CadModel
from kdi_m3.config_manager import ConfigManager
```

### Reuso do VVV com vvv_protocol legado

```python
from physics_m3.vvv_protocol import VVVReport
from physics_m3.vvv import VVVOrchestrator

# Legado (pré-Spec 007)
vvv = VVVReport(study_name="test")
result = vvv.validate_analytical(numerical=10.5, analytical=10.0, tol_pct=5.0)

# Novo (Spec 007)
orch = VVVOrchestrator()
result = orch.run_all(mass_balance_error=0.1, energy_balance_error=0.2)
```

---

## 10. Relatório de Compliance

```bash
python scripts/compliance/report.py
```

Gera:
- **FDC-U scores** por objetivo (O1-O6 com pesos)
- **PQMS atual vs target**
- **Non-conformances tracking** (8/8 closed)
- **Veredito PASS/FAIL**

Output salvo em `docs/logs/compliance-YYYYMMDD.md`.

---

## 11. Implementado vs Não Implementado

### ✅ Implementado (Spec 007 — 40/40 tasks)

| Componente | Status | Testes |
|------------|--------|--------|
| Benchmarks analíticos (cantilever, Kirsch, NBR 6123) | ✅ | 16 |
| VVV multi-escala C11 (6 critérios + orchestrator) | ✅ | 13 |
| Cross-workspace src/ packages | ✅ | 63 cad-cae + 63 kdi |
| GPUAccelerator CPU fallback | ✅ | 6 |
| WAL patch protocol (unified diff + JSON Schema) | ✅ | docs |
| Git LFS (.gitattributes) | ✅ | 14 extensões |
| Compliance report generator | ✅ | FDC-U + NC |
| CI/CD pipeline (GitHub Actions) | ✅ | < 15 min |
| Makefile (setup, test, lint, coverage, clean) | ✅ | 7 targets |
| Dockerfile.ci (CalculiX + Gmsh) | ✅ | Docker-based |
| docs/INSTALL.md (no sudo, no PYTHONUTF8) | ✅ | completo |
| gitignore cleanup (egg-info, pycache) | ✅ | commit |
| 0 asserts genéricos em 49 test files | ✅ | 713 PASS |
| Importlib workaround eliminado | ✅ | from physics_m3.* |

### ⚠️ Pendências (fora do escopo da Spec 007)

| Item | Status | Motivo |
|------|--------|--------|
| AI Assist CAD (NLP→geometria) | 📋 Não iniciado | Requer nova spec |
| UI Streamlit interativa | 📋 Não iniciado | Requer nova spec |
| Otimização topológica com manufatura aditiva | 📋 Parcial | `topopt_manufacturing.py` existe, sem testes dedicados |
| CadQuery + Gmsh + CalculiX em CI real | 📋 Pendente | Dockerfile.ci criado, mas CI não ativado no repo |
| Testes de estresse/carga para métodos numéricos | 📋 Pendente | Fora do escopo |
| Documentação API para integração externa | 📋 Pendente | Guia de uso criado, OpenAPI/Swagger não | 

---

## 12. Solução de Problemas

### Erro: `ModuleNotFoundError: No module named 'physics_m3'`

```bash
pip install -e workspaces/physics-m3
```

### Erro: `ImportError: CuPy not available`

A plataforma tem fallback automático para CPU com warning. Se quiser silenciar:

```bash
python -W ignore::UserWarning -c "from physics_m3.gpu import GPUAccelerator"
```

### Erro: `'ascii' codec can't decode byte 0xc2`

Não use PYTHONUTF8. A plataforma usa `encoding="utf-8"` explicitamente em todas as leituras de arquivo.

### Erro: tests falham com `assert type(x) == float`

NumPy retorna `np.float64`, não `float`. Use `isinstance(x, (float, np.floating))`.

### Testes lentos?

```bash
# Rodar apenas quick checks:
make test-quick   # ~0.5s

# Rodar com paralelismo:
python -m pytest tests/ -n auto --tb=short -q
```

---

> **Última atualização**: 2026-06-17 | **Commit**: `5bed5ae` | **PQMS**: 92.2%
> **GitNexus**: 7.109 nós, 11.513 arestas, 179 fluxos
