# Bioeólica Dev — Manual de Engenharia do Software

> Plataforma de simulação multifísica M³ (Macro-Meso-Micro). PQMS 92.2%.
> 839 testes | 7.158 símbolos | 11.464 arestas | 179 fluxos de execução

---

## Sumário

1. [Arquitetura do Sistema](#1-arquitetura-do-sistema)
2. [Mapa de Domínios de Engenharia](#2-mapa-de-domínios-de-engenharia)
3. [Catálogo de Módulos — physics-m3](#3-catálogo-de-módulos--physics-m3)
4. [Catálogo de Módulos — cad-cae-platform](#4-catálogo-de-módulos--cad-cae-platform)
5. [Catálogo de Módulos — kdi-m3-bridge](#5-catálogo-de-módulos--kdi-m3-bridge)
6. [Grafo de Importação entre Módulos](#6-grafo-de-importação-entre-módulos)
7. [VVV — Sistema de Certificação Multi-Escala](#7-vvv--sistema-de-certificação-multi-escala)
8. [Benchmarks Analíticos](#8-benchmarks-analíticos)
9. [Cobertura de Testes por Domínio](#9-cobertura-de-testes-por-domínio)
10. [Instalação e Dependências](#10-instalação-e-dependências)
11. [Fluxo de Dados entre Workspaces](#11-fluxo-de-dados-entre-workspaces)
12. [O que Não Foi Implementado](#12-o-que-não-foi-implementado)

---

## 1. Arquitetura do Sistema

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────────────┐
│                     kdi-m3-bridge (7 módulos)                       │
│  Acoplamento multi-física: FSI, termo-mecânico, M³ Analysis         │
│  Importa: physics_m3.* (fluid_dynamics, thermodynamics, etc.)        │
└───────────────────────┬─────────────────────────────────────────────┘
                        │ imports
┌───────────────────────▼─────────────────────────────────────────────┐
│                     physics-m3 (41 módulos)                         │
│  Núcleo de física e simulação computacional                         │
│  ┌─────────┬──────────┬───────────┬──────────┬──────────────────┐  │
│  │Mecânica │  Fluidos │Eletro/mag │ Materiais│  Suporte          │  │
│  │FEM      │  CFD     │PMSM       │ Compós.  │  VVV, Logging     │  │
│  │Fadiga   │  Arfólio │Piezo      │ Cristal  │  Context, Normas  │  │
│  │Creep    │  BL      │Bateria    │ Erosão   │  Econômico        │  │
│  └─────────┴──────────┴───────────┴──────────┴──────────────────┘  │
└───────────────────────┬─────────────────────────────────────────────┘
                        │ imports
┌───────────────────────▼─────────────────────────────────────────────┐
│                    cad-cae-platform (6 módulos)                     │
│  CAD → Malha → FEM → Visualização → Otimização                     │
│  CadModel → gmsh → CalculiX → VTK → DesignOptimizer                │
│  GPUAccelerator com fallback CPU                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Workspaces e Import Path

| Workspace | Pacote PIP | Import Python | Módulos | Testes |
|-----------|-----------|---------------|---------|--------|
| `workspaces/physics-m3` | `physics-m3` | `from physics_m3.*` | 41 | ~713 |
| `workspaces/cad-cae-platform` | `cad-cae-platform` | `from cad_cae.*` | 6 | 63 |
| `workspaces/kdi-m3-bridge` | `kdi-m3-bridge` | `from kdi_m3.*` | 7 | 63 |

### Dependências Externas por Workspace

| Workspace | numpy | scipy | matplotlib | cupy (opt) | calculix (opt) | gmsh (opt) |
|-----------|-------|-------|------------|------------|----------------|------------|
| physics-m3 | ✅ | ✅ | ✅ | — | — | — |
| cad-cae-platform | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| kdi-m3-bridge | ✅ | — | — | — | — | — |

---

## 2. Mapa de Domínios de Engenharia

### 10 Domínios Cobertos

| # | Domínio | Módulos | Métodos Numéricos | % Testes |
|---|---------|---------|-------------------|----------|
| 1 | ⚙️ Mecânica Estrutural | `structural_analysis`, `mechanical_tests`, `fatigue`, `creep`, `fem_solver`, `peridynamics`, `log_wal` | FEM, Peridynamics, Beam Theory, S-N, Norton-Bailey, LM | 28% |
| 2 | 🌊 Mecânica dos Fluidos | `fluid_dynamics`, `cfd_solver` | Navier-Stokes, RANS, BL Theory, Panel Methods | 7% |
| 3 | 🔥 Termodinâmica | `thermodynamics` | Condução 1D, Convecção, Radiação, Trocadores | 9% |
| 4 | ⚡ Eletrotécnica | `electromechanical`, `piezoelectric` | PMSM, DCMachine, d31/d33, Harvesting | 12% |
| 5 | 🧊 Materiais/Compósitos | `composite_model`, `crystal_lattice`, `erosion` | Halpin-Tsai, Hashin-Rosen, CLT, Finnie | 10% |
| 6 | 📐 Otimização | `topology_optimization`, `topopt_avancada`, `topopt_manufacturing`, `topopt_multiobj` | SIMP, BESO, MMA, OC | 31% |
| 7 | 📊 Incerteza/Validação | `uncertainty`, `validacao_experimental`, `simulation_comparison` | MC, Sensibilidade, Curve Fitting, RMSE | 9% |
| 8 | 🛡️ Degradação/Manutenção | `erosion`, `predictive_maintenance`, `digital_twin` | Kalman Filter, RUL, Degradation | 12% |
| 9 | 📝 Normas/Documentação | `normativo`, `scientific_writing`, `knowledge_base`, `mapa_unico` | ASTM D790, D3039, D3410, IEC 61400, NBR 6123 | 6% |
| 10 | 🔄 Acoplamento Multi-física | `kdi_multiphysics`, `kdi_macro`, `kdi_meso`, `kdi_micro`, `kdi_forwarder` | FSI, Termo-mecânico, M³ Analysis | 14% |

---

## 3. Catálogo de Módulos — physics-m3

### 3.1 Mecânica Estrutural

#### `structural_analysis.py` — Análise de Tensões e Esforços ⚙️

**Domínio**: Mecânica dos Sólidos — tensões em vigas, placas, cascas compósitas.

| Classe | Função |
|--------|--------|
| `BeamSection` | Propriedades geométricas (I, A, módulo elástico) |
| `PlyProperties` | Propriedades de cada lâmina do laminado |
| `CompositeLaminate` | Laminado completo com sequência de empilhamento |

**Métodos principais**:
- `von_mises_stress(s1, s2, t12)` → tensão equivalente von Mises
- `tresca_stress(s1, s2, t12)` → tensão equivalente Tresca
- `principal_stresses(sx, sy, txy)` → tensões principais (σ₁, σ₂)
- `bending_stress(M, y, I)` → σ = My/I
- `normal_stress(F, A)` → σ = F/A
- `shear_stress(V, Q, I, t)` → τ = VQ/(It)
- `buckling_euler(P, L, E, I)` → Pcr = π²EI/(KL)²

**Equações**: Von Mises (σ_v = √(σ₁² - σ₁σ₂ + σ₂² + 3τ²)), Euler buckling, flexão de Bernoulli-Euler.

**Testes**: 12 — verifica valores em casos clássicos (viga engastada, cisalhamento puro).
**Importa**: numpy. **Importado por**: kdi-m3-bridge, tests.

---

#### `mechanical_tests.py` — Ensaios Mecânicos ⚙️

**Domínio**: Caracterização de materiais compósitos via ensaios normalizados.

**Funções**:
- `flexure_test(E, strength_MPa, length_mm, width_mm, thickness_mm)` → Ensaio de flexão 3 pontos (ASTM D790)
- `tensile_test(E, strength_MPa, width_mm, thickness_mm)` → Ensaio de tração (ASTM D3039)
- `compression_test(E, strength_MPa, area_mm2)` → Ensaio de compressão (ASTM D3410)
- `buckling_test(E, length_mm, I_mm4, K)` → Flambagem de Euler
- `impact_test(mass_kg, velocity_ms, E_mod_MPa)` → Ensaio de impacto
- `shear_test(stress_MPa, area_mm2)` → Ensaio de cisalhamento

**Fluxo**: parâmetros de entrada → dicionário com `stress_MPa, strain, displacement_mm, status`.

**Testes**: 7 — valida ranges físicos (tensão > 0, deformação proporcional).
**Importa**: numpy.

---

#### `fatigue.py` — Análise de Fadiga ⚙️

**Domínio**: Vida em fadiga de materiais compósitos — curvas S-N, contagem rainflow.

| Classe | Função |
|--------|--------|
| `FatigueAnalysis` | Curvas SN, Goodman, Miner, Rainflow |

**Métodos**:
- `sn_curve(stress_range, R_ratio, N_cycles)` → vida em fadiga
- `goodman_correction(Sa, Sm, Su)` → correção de Goodman
- `rainflow3pt(series)` → contagem de ciclos rainflow (3-point)
- `miner_sum(blocks)` → dano acumulado de Miner
- `woehler_curve(N)` → curva de Wöhler (S = a·N^b)

**Equações**: Basquin (σ_f = σ'_f · (2N_f)^b), Goodman (S_a/S_e + S_m/S_u = 1/N), Miner (Σ n_i/N_i = D).

**Testes**: 24 — valida curvas SN, correção Goodman, rainflow, dano acumulado.
**Importa**: numpy. **Depende de**: CompositeMaterial (externo).

---

#### `creep.py` — Análise de Creep ⚙️

**Domínio**: Deformação por fluência (creep) em materiais sob carga constante.

| Classe | Função |
|--------|--------|
| `CreepModel` | Norton-Bailey, Larson-Miller, Voigt-Kelvin, Reuss |

**Métodos**:
- `norton_bailey_strain_rate(sigma, T, t, A, n, m, Q, R)` → ε̇ = A·σⁿ·tᵐ·exp(-Q/RT)
- `larson_miller(T, tr, C)` → parâmetro LM = T·(C + log₁₀(tr))
- `voigt_strain(sigma, E, eta, t)` → ε(t) = σ/E·(1 - exp(-t·E/η))
- `reuss_strain(sigma, E, t)` → ε(t) = σ·(1/E + t/η)

**Testes**: 25 — valida equação de Arrhenius, Voigt, LM, isotensional/isostrain.
**Importa**: numpy, scipy (optimize).

---

#### `fem_solver.py` — Solver de Elementos Finitos ⚙️

**Domínio**: Método dos Elementos Finitos — formulação de rigidez direta.

| Classe | Função |
|--------|--------|
| `BeamElement` | Matriz de rigidez de viga 2D (6 DOFs) |
| `FEModel` | Montagem, solução, análise modal |

**Métodos**:
- `stiffness_matrix(E, A, I, L)` → matriz de rigidez elementar (6×6)
- `assemble()` → matriz global
- `apply_bc(fixed_dofs)` → condições de contorno
- `solve()` → K·u = f
- `modal_analysis()` → ω²·M·φ = K·φ
- `element_stress()` → σ = E·B·u

**Testes**: 4 — montagem de matriz, solução, reações.
**Importa**: numpy.

---

#### `peridynamics.py` — Peridinâmica ⚙️

**Domínio**: Mecânica do contínuo não-local — formulação integral (sem derivadas espaciais).

| Classe | Função |
|--------|--------|
| `PeridynamicsModel` | Bond-based peridynamics, horizon, crack propagation |

**Métodos**:
- `create_grid(nx, ny, delta)` → discretização com horizonte δ
- `stiffness_matrix(E, rho)` → matriz de rigidez não-local
- `solve(forces, steps)` → solução iterativa
- `identify_crack(critical_stretch)` → detecção de trinca

**Equações**: ρ·ü(x,t) = ∫_{H_x} f(u(x',t)-u(x,t), x'-x) · dV_x' + b(x,t)

**Testes**: 3 — criação de grid, rigidez, solução.
**Importa**: numpy.

---

#### `kinematic_machine.py` — Máquinas Cinemáticas ⚙️

**Domínio**: Mecanismos articulados — 4 barras, cadeias cinemáticas.

| Classe | Função |
|--------|--------|
| `Ponto3D, JointType, Joint, Link, Mechanism4Bar, KinematicChain` | Cinemática de mecanismos |

**Métodos**:
- `grashof()` → critério de Grashof (rotatividade)
- `solve_position(theta2)` → posição do mecanismo
- `solve_velocity(omega2)` → velocidades
- `solve_acceleration(alpha2)` → acelerações
- `moment_of_inertia()` → momento de inércia

**Testes**: 8 — Grashof, posição, velocidade, aceleração.
**Importa**: numpy.

---

### 3.2 Fluidos

#### `fluid_dynamics.py` — Dinâmica dos Fluidos 🌊

**Domínio**: Aerodinâmica de perfis, escoamento em camada limite, turbulência.

| Classe | Função |
|--------|--------|
| `Airfoil` | NACA 4-digit, coeficientes aerodinâmicos |

**Métodos**:
- `wind_profile(z, z0, Vref, href)` → perfil de vento logarítmico: V(z) = Vref·ln(z/z₀)/ln(h_ref/z₀)
- `atmospheric_boundary_layer_height(Vref)` → altura da camada limite atmosférica
- `reynolds_number(rho, V, L, mu)` → Re = ρ·V·L/μ
- `boundary_layer_thickness(x, Re_x)` → δ = 5.0·x/√Re_x (laminar)
- `skin_friction_coefficient(Re_x)` → Cf = 0.0592/Re_x^(1/5) (turbulento)
- `lift_coefficient(alpha, camber)` → Cℓ(α) para perfil NACA
- `drag_coefficient(alpha)` → Cd(α)
- `moment_coefficient(alpha)` → Cm(α)
- `airfoil_polarities(alphas)` → polar completa

**Equações**: Reynolds number, BL thickness (Blasius), cf (Prandtl), perfil de vento logarítmico.

**Testes**: 32 — valida NACA0012 (Cℓ=0 a α=0, stall detection), Reynolds, BL, Cf, polares.
**Importa**: numpy. **Importado por**: `kdi_multiphysics.py`.

---

#### `cfd_solver.py` — Solver CFD 🌊

**Domínio**: CFD básico — equações de Navier-Stokes em diferenças finitas.

| Classe | Função |
|--------|--------|
| `CFDSolver` | Navier-Stokes, lid-driven cavity, energia |

**Métodos**:
- `create_mesh(Nx, Ny, Lx, Ly)` → malha uniforme
- `_build_laplacian(N)` → matriz Laplaciana (diferenças finitas)
- `solve_navier_stokes(Re, dt, max_it, tol)` → NS transient
- `lid_driven_cavity(Re, N)` → cavidade clássica (benchmark CFD)
- `solve_energy()` → equação da energia

**Equações**: Navier-Stokes (∇·u = 0, ∂u/∂t + u·∇u = -∇p + 1/Re·∇²u).

**Testes**: 4 — criação de malha, operadores, cavidade.
**Importa**: numpy, scipy (sparse).

---

### 3.3 Termodinâmica

#### `thermodynamics.py` — Termodinâmica 🔥

**Domínio**: Condução, convecção, radiação, transferência de calor, secagem.

| Classe | Função |
|--------|--------|
| `DryingProcess` | Modelagem de secagem |

**Funções**:
- `conduction_1D(k, A, dT, dx)` → Q = k·A·ΔT/Δx (Fourier)
- `convection(h, A, dT)` → Q = h·A·ΔT (Newton)
- `radiation(epsilon, A, T1, T2, sigma)` → Q = ε·σ·A·(T₁⁴ - T₂⁴) (Stefan-Boltzmann)
- `overall_heat_transfer(U, A, dT)` → Q = U·A·ΔT
- `energy_balance(Q_in, Q_out, Q_gen, m, cp, dt)` → balanço energético
- `heat_exchanger(m_dot, cp, T_in, T_out)` → trocador de calor
- `thermal_efficiency(W_out, Q_in)` → η = W_out/Q_in
- `drying_rate(X, T, P)` → taxa de secagem

**Testes**: 24 — Fourier 1D, Stefan-Boltzmann, Newton, balanço, trocador, ciclo Rankine.
**Importa**: numpy. **Importado por**: `kdi_multiphysics.py` (run_thermal).

---

### 3.4 Eletrotécnica

#### `electromechanical.py` — Máquinas Elétricas ⚡

**Domínio**: Geradores síncronos (PMSG), máquinas DC, baterias.

| Classe | Função |
|--------|--------|
| `PMSG` | Permanent Magnet Synchronous Generator |
| `DCMachine` | Máquina DC (motor/gerador) |
| `BatteryStorage` | Armazenamento (Li-Ion) |

**Métodos (PMSG)**:
- `electrical_freq_Hz(rpm, P)` → f = rpm·P/120
- `emf_V(rpm, flux)` → E = k·φ·ω
- `torque_max_Nm()` → torque máximo
- `efficiency(P_out, losses)` → η = Pₒᵤₜ/(Pₒᵤₜ + perdas)
- `summary()` → relatório completo

**Métodos (DCMachine)**:
- `torque_Nm(Ia, kt)` → T = kt·Ia
- `speed_rads(V, Ia, Ra, ke)` → ω = (V - Ia·Ra)/ke

**Testes**: 30 — PMSG (freq, EMF, torque, eficiência), DC Machine (torque, speed, potência), bateria.
**Importa**: numpy.

---

#### `piezoelectric.py` — Piezoeletricidade ⚡

**Domínio**: Materiais piezoelétricos — sensores, atuadores, energy harvesting.

| Classe | Função |
|--------|--------|
| `PiezoMaterial` | d31, d33, atuação, sensoriamento, harvesting |

**Métodos**:
- `eform_stress(E3, d31)` → σ = E₃·d₃₁·Y (modo e-form)
- `dform_strain(epsilon, d31)` → E = ε/d₃₁ (modo d-form)
- `actuator_strain(V, t, d31)` → ε = V·d₃₁/t
- `actuator_force(V, t, d31, Y, A)` → F = Y·A·V·d₃₁/t
- `sensor_voltage(strain, t, d31)` → V = strain·t/d₃₁
- `harvested_power(F, freq, C, R, d33)` → P = harvesting

**Equações**: d31 (transversal), d33 (longitudinal), acoplamento eletromecânico.

**Testes**: 22 — d31, d33, atuador, sensor, acoplamento.
**Importa**: numpy, scipy.

---

### 3.5 Materiais

#### `composite_model.py` — Materiais Compósitos 🧊

**Domínio**: Micromecânica de compósitos lamelares — Halpin-Tsai, Hashin-Rosen, CLT.

| Classe | Função |
|--------|--------|
| `FabricationProcess` | Parâmetros de fabricação (temperatura, pressão, curagem) |
| `CompositeMaterial` | Propriedades elásticas, resistência, CLT |

**Métodos**:
- `Vm(Vf)` → fração volumétrica de matriz
- `elastic_constants(E1, E2, G12, nu12, Vf)` → constantes ortotrópicas
- `estimate_strength(Vf)` → resistência via micromechanics
- `summary()` → relatório de propriedades
- `water_content_kg(...)` → absorção de água
- `total_energy_kWh(...)` → energia incorporada

**Equações**: Halpin-Tsai (E = Em·(1 + ξ·η·Vf)/(1 - η·Vf)), Hashin-Rosen (G12, G23), CLT (ABD matrix).

**Testes**: 3 — constantes elásticas, estimativa de resistência, fabricação.
**Importa**: numpy. **Importado por**: `m3_analysis.py`, `structural_analysis.py`.

---

#### `crystal_lattice.py` — Redes Cristalinas 🧊

**Domínio**: Cristalografia — células unitárias, índices de Miller, difração.

| Classe | Função |
|--------|--------|
| `CrystalLattice` | SC, BCC, FCC, HCP, Miller, Bragg |

**Métodos**:
- `unit_cell_atoms()` → átomos na célula unitária
- `supercell(nx, ny, nz)` → supercélula
- `miller_plane(h, k, l)` → plano de Miller
- `interplanar_spacing(h, k, l)` → distância interplanar (Bragg)
- `packing_factor()` → fator de empacotamento
- `bragg_angle(h, k, l, lambda)` → θ = arcsin(λ·√(h²+k²+l²)/(2a))
- `bond_angles()` → ângulos de ligação
- `structure_factor(h, k, l)` → fator de estrutura (difração de raios-X)

**Testes**: 22 — SC/BCC/FCC (átomos, empacotamento), Miller, Bragg, supercélula.
**Importa**: numpy.

---

#### `erosion.py` — Erosão por Partículas 🛡️

**Domínio**: Erosão de pás eólicas por partículas sólidas — modelo de Finnie.

| Classe | Função |
|--------|--------|
| `ErosionModel` | Erosão Finnie, erosão de pá, dano cumulativo |

**Métodos**:
- `finnie_erosion(mass, velocity, angle)` → volume removido (modelo Finnie)
- `erosion_vs_angle(angles)` → curva de erosão vs ângulo
- `blade_erosion(tip_speed, chord)` → erosão em pá eólica
- `cumulative_erosion(...)` → erosão acumulada (partículas)
- `erosion_over_time(...)` → erosão ao longo do tempo
- `time_to_failure(...)` → tempo até falha

**Equações**: Finnie: Q = K·m·Vⁿ·f(α)/H. Erosão ∝ V² (n=2 para materiais dúcteis).

**Testes**: 7 — V² scaling (ratio 3-5x para dobro de V), ângulo oblíquo > normal, partículas. **Spec 007**.
**Importa**: numpy, scipy.

---

### 3.6 Otimização Topológica

#### `topology_optimization.py` — SIMP 2D 📐

**Domínio**: Otimização topológica via SIMP (Solid Isotropic Material with Penalization).

| Classe | Função |
|--------|--------|
| `TopOpt` | Otimização SIMP 88-line (clássico) |

**Métodos**:
- `_create_element_stiffness(E, nu)` → matriz de rigidez elementar (quad4)
- `_node_indices(ely, elx, nx)` → índices nodais
- `_build_global(nx, ny)` → matriz de rigidez global
- `optimize(vol_frac, penalty, rmin)` → loop SIMP: xnew = x·(B/λ/∂c/∂x)^η

**Testes**: 46 — stiffness, nodal indices, SIMP loop, filtro de sensibilidade, topologia resultante.
**Importa**: numpy, scipy (sparse, linalg).

---

#### `topopt_avancada.py` — SIMP 3D 📐

**Domínio**: SIMP 3D com elementos hex8.

| Classe | Função |
|--------|--------|
| `TopOpt3D` | SIMP 3D com hex8 |

**Métodos**:
- `_hex8_shape_derivatives(xi, eta, zeta)` → derivadas das funções de forma hex8
- `_make_hex8_stiffness(E, nu)` → matriz de rigidez hex8 (24×24)
- `topopt_simp(volfrac, penal, rmin, ft)` → SIMP 3D: loop OC (optimality criteria)

**Testes**: 69 — hex8, stiffness, SIMP 3D, malha 60×20×4.
**Importa**: numpy, scipy (sparse, linalg).

---

#### `topopt_manufacturing.py` — Restrições de Manufatura 📐

**Domínio**: Restrições de manufatura aditiva (overhang angle) em otimização topológica.

| Classe | Função |
|--------|--------|
| `TopOptManufacturing` | Overhang angle, suportes mínimos |

**Métodos**:
- `_build_structuring_element(rmin)` → elemento estruturante
- `_detect_overhang_2d(...)` → overhang em 2D
- `apply_overhang_constraint(...)` → restrição de overhang

**Testes**: 13 — detecção de overhang, filtro, restrição.
**Importa**: numpy, scipy.

---

#### `topopt_multiobj.py` — Otimização Multi-Objetivo 📐

**Domínio**: Pareto ótimo entre complacência, massa e custo.

| Classe | Função |
|--------|--------|
| `TopOptMultiObj` | Multi-objective topology optimization |

**Métodos**:
- `_compute_compliance(x, penal)` → complacência
- `_compute_mass_fraction(x)` → fração de massa
- `_compute_cost_fraction(...)` → fração de custo
- `optimize(vol_frac, w1, w2, w3)` → Pareto ótimo: min(w₁·c + w₂·m + w₃·cost)

**Testes**: 10 — complacência, massa, custo, otimização.
**Importa**: numpy.

---

### 3.7 Incerteza e Validação

#### `uncertainty.py` — Quantificação de Incerteza 📊

**Domínio**: Monte Carlo, intervalos de confiança, sensibilidade.

| Classe | Função |
|--------|--------|
| `UncertainValue` | Valor nominal ± desvio |
| `MonteCarloSampler` | Amostragem MC com distribuições |

**Funções**:
- `confidence_interval(data)` → (média, lo, hi) com 95% CI
- `propagate_error(func, vars)` → propagação de incerteza

**Testes**: 3 — MC sampler, CI, propagação.
**Importa**: numpy.

---

#### `validacao_experimental.py` — Validação Experimental 📊

**Domínio**: Calibração de modelos numéricos vs. dados experimentais.

**Funções**:
- `compare_simulation_experiment(sim, exp)` → RMSE, R², MAE
- `calibrate_model(model_func, exp_data, p0)` → calibração por curve_fit

**Testes**: 27 — comparação sim/exp, calibração (linear, quadrática), goodness-of-fit.
**Importa**: numpy, scipy (optimize).

---

#### `simulation_comparison.py` — Comparação de Simulações 📊

**Domínio**: Métricas de comparação entre simulação e experimento.

| Classe | Função |
|--------|--------|
| `SimulationComparison` | Múltiplas métricas de erro |

**Métodos**:
- `rmse()` → root mean square error
- `mae()` → mean absolute error
- `r2()` → coeficiente de determinação R²
- `max_error()` → erro máximo absoluto
- `relative_error()` → erro relativo (%)

**Testes**: 8 — RMSE, MAE, R², erro máximo.
**Importa**: numpy.

---

### 3.8 Degradação e Manutenção

#### `digital_twin.py` — Gêmeo Digital 🛡️

**Domínio**: Monitoramento em tempo real — Kalman filter, anomalias, fusão de sensores.

| Classe | Função |
|--------|--------|
| `DigitalTwin` | Sensor fusion, Kalman filter, anomaly detection |

**Métodos**:
- `simulate_sensor(sensor_type, t)` → dados de sensor sintéticos (temperatura, strain, vibração)
- `kalman_update(measurement, dt)` → filtro de Kalman: x̅ = x + K·(z - H·x)
- `detect_anomaly(value, threshold)` → detecção de anomalias
- `degradation_model(t, params)` → modelo de degradação

**Testes**: 20 — Kalman, sensor simulation, anomaly detection, reset.
**Importa**: numpy, scipy.

---

#### `predictive_maintenance.py` — Manutenção Preditiva 🛡️

**Domínio**: Estimativa de vida útil restante (RUL), detecção de anomalias.

| Classe | Função |
|--------|--------|
| `DegradationModel` | Evolução da degradação |
| `AnomalyDetector` | Detecção de anomalias (IQR, z-score) |
| `RULEstimator` | RUL — vida útil restante |
| `RULResult` | Resultado da estimativa |

**Testes**: 13 — DegradationModel, anomaly detection, RUL, reset.
**Importa**: numpy.

---

### 3.9 Suporte

#### `context_engine.py` — Motor de Contexto

**Domínio**: Análise de contexto para seleção de metodologia.

| Classe | Função |
|--------|--------|
| `ContextEngine` | Camadas de contexto, complexidade, normas |

**Testes**: 14 — domínios, restrições, normas, geração de roteiro.

---

#### `normativo.py` — Verificação Normativa 📝

**Domínio**: Conformidade com normas técnicas (ASTM, IEC, NBR, ISO).

| Classe | Função |
|--------|--------|
| `StandardsCheck` | Validação contra normas |

**Métodos**:
- `check_astm_d790(...)` → Flexão (ASTM D790)
- `check_astm_d3039(...)` → Tração (ASTM D3039)
- `check_astm_d3410(...)` → Compressão (ASTM D3410)
- `check_iec_61400(...)` → Turbinas eólicas (IEC 61400)
- `check_iso_2533(...)` → Atmosfera padrão (ISO 2533)

**Testes**: 13 — ASTM D790, D3039, D3410, IEC 61400, ISO 2533, NBR 6123.
**Importa**: numpy.

---

#### `logging_wal.py` — Work Activity Log (WAL) 📝

**Domínio**: Log estruturado conforme mandato M5 — 5W1H.

| Classe | Função |
|--------|--------|
| `LogEntry` | Entrada de log (5W1H) |
| `WALogger` | Gerenciador de logs |

**Testes**: 3 — criar log, consultar, registrar.

---

#### `m3_analysis.py` — Framework M³

**Domínio**: Análise Macro-Meso-Micro para compósitos eólicos.

| Classe | Função |
|--------|--------|
| `MacroScale` | Ambiente externo (vento, cargas) |
| `PlyLayer` | Camada individual do laminado |
| `MesoScale` | Interface entre macro e micro |
| `MicroScale` | Propriedades micromecânicas |
| `M3Analysis` | Análise M³ completa |

**Testes**: 4 — Macro (wind pressure), Meso (von Mises, Tsai-Wu), Micro (homogeneização).
**Importa**: numpy, CompositeMaterial.

---

#### Outros módulos

| Módulo | Domínio | Testes |
|--------|---------|--------|
| `cad_visualization.py` | Visualização CAD — 3D geometry, stress heatmap | 10 |
| `method_selector.py` | Seleção de método numérico (FEM/MPM/SPH) | 3 |
| `model_calibration.py` | Calibração de parâmetros (curve_fit, LM) | 9 |
| `mkdelagen.py` | Geração de modelos paramétricos de pás | 3 |
| `economico.py` | Análise econômica — NPV, IRR, LCOE, payback | 16 |
| `knowledge_base.py` | Base de conhecimento com fontes | 2 |
| `scientific_writing.py` | Escrita científica — relatórios ABNT/IEEE | 13 |
| `experimental_data.py` | Dados experimentais — CSV, JSON, dict | 10 |
| `mapa_unico.py` | Mapa de Informação Única (M4) | 3 |

---

## 4. Catálogo de Módulos — cad-cae-platform

| Módulo | Classes | Funções | Testes | Importa |
|--------|---------|---------|--------|---------|
| `cad_bridge.py` | `CadModel` | `cantilever_beam`, `l_bracket`, `plate_with_hole`, `pressure_vessel` | 16 | numpy |
| `calculix_solver.py` | `FEMSolver` | solve, export_results, load_mesh | 11 | cad_cae.gmsh_mesher |
| `gmsh_mesher.py` | `MeshGenerator` | `create_beam_mesh`, export_msh, get_mesh_stats | 7 | numpy |
| `gpu_accelerator.py` | `GPUAccelerator` | `benchmark_comparison` | 6 | cupy (opt), numpy, scipy |
| `vtk_export.py` | — | `write_vtu`, `write_vtp` | 6 | numpy |
| `design_optimizer.py` | `DesignSpace`, `DesignOptimizer` | optimize, pareto | 13 | numpy, design_optimizer |

**Fluxo CAD-CAE**: `CadModel (cad_bridge)` → malha via `MeshGenerator (gmsh)` → solver via `FEMSolver (calculix)` → exportação VTK via `write_vtu/vtp (vtk_export)` → otimização via `DesignOptimizer`.

---

## 5. Catálogo de Módulos — kdi-m3-bridge

| Módulo | Classes | Funções | Testes | Importa |
|--------|---------|---------|--------|---------|
| `config_manager.py` | `ConfigManager` | load, save, get, set, validate | 16 | json, os |
| `kdi_macro.py` | `MacroEnvironment`, `WindScenario` | `simulate_wind`, wind_profile | 11 | numpy |
| `kdi_meso.py` | `MesoAnalysis` | stress_concentration, laminate_analysis | 4 | numpy |
| `kdi_micro.py` | `MicroMechanics` | homogenize, ply_properties | 4 | numpy |
| `kdi_multiphysics.py` | `MultiPhysicsCoupling`, `FSIAnalysis` | `run_structural`, `run_thermal`, `run_electrical`, `run_fluid`, `coupled_simulation` | 8 | `physics_m3.*` (thermo, fluid, electromechanical, structural) |
| `kdi_forwarder.py` | `M3Forwarder` | forward_macro_to_meso, forward_meso_to_micro | 6 | numpy, physics_m3 |

**Fluxo M³**: `MacroEnvironment (kdi_macro)` → `MesoAnalysis (kdi_meso)` → `MicroMechanics (kdi_micro)` → `MultiPhysicsAnalysis (kdi_multiphysics)` com acoplamento FSI.

---

## 6. Grafo de Importação entre Módulos

### Diagrama de Dependências

```
physics-m3 (núcleo)
├── structural_analysis.py ←── composite_model.py (materiais)
├── mechanical_tests.py ←── numpy
├── fatigue.py ←── composite_model.py (externo)
├── creep.py ←── numpy, scipy
├── fem_solver.py ←── numpy
├── peridynamics.py ←── numpy
├── fluid_dynamics.py ←── numpy ←── kdi_multiphysics.py
├── cfd_solver.py ←── numpy, scipy
├── thermodynamics.py ←── numpy ←── kdi_multiphysics.py
├── electromechanical.py ←── numpy ←── kdi_multiphysics.py
├── piezoelectric.py ←── numpy, scipy
├── composite_model.py ←── numpy ←── m3_analysis, structural, kdi
├── crystal_lattice.py ←── numpy
├── erosion.py ←── numpy, scipy
├── topology_optimization.py ←── numpy, scipy
├── topopt_avancada.py ←── numpy, scipy
├── topopt_manufacturing.py ←── numpy, scipy
├── topopt_multiobj.py ←── numpy
├── uncertainty.py ←── numpy
├── validacao_experimental.py ←── numpy, scipy
├── digital_twin.py ←── numpy, scipy
├── predictive_maintenance.py ←── numpy
├── normativo.py ←── numpy
├── vvv/ ─── (Spec 007) ←── physics_m3.vvv_protocol
│   ├── certificate.py ←── uuid, datetime
│   ├── criteria/convergence.py
│   ├── criteria/stability.py
│   ├── criteria/conservation.py
│   ├── criteria/benchmark.py
│   ├── criteria/cross_code.py
│   ├── criteria/units.py
│   └── orchestrator.py ←── todos os 6 critérios
└── gpu/ ─── (Spec 007)
    └── fallback.py ←── numpy, scipy, cupy (opt)

cad-cae-platform
├── cad_bridge.py ←── numpy
├── gmsh_mesher.py ←── numpy ←── calculix_solver, tests
├── calculix_solver.py ←── gmsh_mesher
├── gpu_accelerator.py ←── numpy, scipy, cupy (opt)
├── vtk_export.py ←── numpy
└── design_optimizer.py ←── numpy

kdi-m3-bridge (acoplamento)
├── config_manager.py ←── json, os
├── kdi_macro.py ←── numpy
├── kdi_meso.py ←── numpy
├── kdi_micro.py ←── numpy
├── kdi_forwarder.py ←── numpy, physics_m3
└── kdi_multiphysics.py ←── physics_m3.(fluid_dynamics, thermodynamics, 
                             electromechanical, structural_analysis, creep)
```

### Topologia de Importação (cross-workspace)

```
[physics-m3]─────→[kdi-m3-bridge]
    │                    │
    │                    │ imports: fluid_dynamics, thermodynamics,
    │                    │          electromechanical, structural_analysis
    │                    │
    └──────── imports via pip install -e workspaces/physics-m3
             (nenhum importlib.util.spec_from_file_location)

[cad-cae-platform] ←── auto-contido (importa apenas numpy/scipy)
```

---

## 7. VVV — Sistema de Certificação Multi-Escala

### Protocolo C11 (Spec 007)

```
VVVOrchestrator.run_all()
├── C1: MeshConvergenceCriterion    erro < 5%    → F5→F4
├── C2: TemporalStabilityCriterion  residual<1e-4 → F5→F4
├── C3: ConservationCriterion       massa/energia  → F5→F3
├── C4: BenchmarkCorrelationCriterion > 90%       → F5→F3
├── C5: CrossCodeCriterion          Δ < 5%        → F5→F4
└── C6: UnitsConsistencyCriterion   SI > 80%      → F5→F1
                              ↓
                    VVVCertificate.evaluate()
                              ↓
                    PASS / FAIL + return_phase
```

### Compatibilidade com Legado

```python
# Legado (pré-Spec 007)
from physics_m3.vvv_protocol import VVVReport
vvv = VVVReport(study_name="My Study")
vvv.validate_analytical(numerical=10.5, analytical=10.0, tol_pct=5.0)

# Novo (Spec 007)  
from physics_m3.vvv import VVVOrchestrator
orch = VVVOrchestrator()
result = orch.run_all(mass_balance_error=0.1, energy_balance_error=0.2)
print(result.to_dict())  # {'overall_status': 'PASS', 'criteria': {...}}
```

---

## 8. Benchmarks Analíticos

### Viga Engastada — PL³/(3EI)

```
Referência: Euler-Bernoulli beam theory
Fórmula: δ = P·L³/(3·E·I)
Módulo: test_benchmarks/test_cantilever_beam.py (4 testes)
Tolerância: < 5% (fino), < 10% (grosseiro)
Validação: 
  - test_cantilever_analytical_value → auto-consistência
  - test_cantilever_flexure_correlation → correlação com flexure_test
  - test_cantilever_beam_scale_invariance → L³ scaling
  - test_cantilever_linearity → P linearity
```

### Placa com Furo — Kirsch Kt = 3.0

```
Referência: Kirsch 1898 (solução analítica para tensão em placa infinita com furo)
Fórmula: Kt = σ_max / σ_nominal → 3.0
Módulo: test_benchmarks/test_plate_hole_kt.py (6 testes)
Tolerância: < 10% (16+ elementos)
Validação: convergência Kt(n) = 3.0 + C/n², simetria angular, decaimento com distância
```

### Pressão de Vento — NBR 6123

```
Referência: ABNT NBR 6123:1988 — Forças Devidas ao Vento em Edificações
Fórmula: q = 0.613 × Vk², Cp por geometria
Módulo: test_benchmarks/test_wind_pressure.py (7 testes)
Tolerância: < 10%
Validação: Cp windward=0.8, leeward h/b, sidewall=-0.7, cilíndrico por Re
```

---

## 9. Cobertura de Testes por Domínio

### physics-m3 (713 tests)

| Domínio | Testes | % | Principais |
|---------|--------|---|------------|
| Otimização Topológica | 138 | 19% | topopt_avancada (69), topology_optimization (46) |
| Mecânica Estrutural | 76 | 11% | creep (25), fatigue (24), structural (12), mechanical_tests (7) |
| Fluidos | 36 | 5% | fluid_dynamics (32), cfd_solver (4) |
| Eletrotécnica | 52 | 7% | electromechanical (30), piezoelectric (22) |
| Termodinâmica | 24 | 3% | thermodynamics (24) |
| Materiais | 52 | 7% | erosion (7), composite (3), crystal_lattice (22), mkdelagen (3) |
| Incerteza/Validação | 47 | 7% | validacao_experimental (27), uncertainty (3), comparison (8), calibration (9) |
| Degradação/Manutenção | 33 | 5% | digital_twin (20), predictive_maintenance (13) |
| Contexto/Normas | 30 | 4% | context_engine (14), normativo (13), method_selector (3) |
| VVV (Spec 007) | 26 | 4% | VVV orchestrator (13), VVV reinforced (10), VVV protocol (3) |
| Benchmarks (Spec 007) | 16 | 2% | cantilever (4), plate_hole (5), wind_pressure (7) |
| Outros | 183 | 26% | cad_viz (27), topology (13), topopt_manufacturing (13), topopt_multiobj (10), etc |

### cad-cae-platform (63 tests)

| Módulo | Testes |
|--------|--------|
| cad_bridge | 16 |
| design_optimizer | 13 |
| calculix_solver | 11 |
| gmsh_mesher | 7 |
| gpu_accelerator | 6 |
| vtk_export | 6 |

### kdi-m3-bridge (63 tests)

| Módulo | Testes |
|--------|--------|
| config_manager | 16 |
| kdi_macro | 11 |
| e2e_complete | 10 |
| kdi_multiphysics | 8 |
| kdi_forwarder | 6 |
| kdi_meso | 4 |
| kdi_micro | 4 |

---

## 10. Instalação e Dependências

### Instalação Mínima

```bash
pip install -e workspaces/physics-m3 -e workspaces/cad-cae-platform -e workspaces/kdi-m3-bridge
make test-quick  # 46 testes (benchmarks + VVV)
```

### Instalação Completa

```bash
make setup        # instala tudo + pytest + ruff
make test         # 713 + 63 + 63 = 839 testes
python scripts/compliance/report.py  # PQMS 92.2%
```

### Docker (com CalculiX + Gmsh)

```bash
docker build -f Dockerfile.ci -t bioeolica-ci .
docker run --rm bioeolica-ci make test
```

### Dependências Python

| Pacote | Obrigatório? | Função |
|--------|-------------|--------|
| `numpy>=1.24` | ✅ Sim | Arrays, álgebra linear, físicos |
| `scipy>=1.10` | ⚠️ Opcional | Sparse, optimize, curve_fit (sem ele, FEM e calibração falham) |
| `matplotlib` | ⚠️ Opcional | Visualização CAD |
| `cupy-cuda12x` | 🔲 Opcional | GPU acceleration (CPU fallback automático) |

### Dependências de Sistema

| Pacote | Obrigatório? | Função |
|--------|-------------|--------|
| `calculix-ccx` | 🔲 Opcional | FEM via CalculiX (auto-skip em testes) |
| `gmsh` | 🔲 Opcional | Geração de malha (auto-skip em testes) |
| `libglu1-mesa` | 🔲 Opcional | OpenGL (ParaView) |

---

## 11. Fluxo de Dados entre Workspaces

### Exemplo: Análise de Pá Eólica (Fluxo Completo)

```
1. CAD: CadModel.cantilever_beam(100, 10, 5)    [cad-cae]
       ↓ shape geometry
2. MALHA: MeshGenerator.create_beam_mesh(10,2,2)  [cad-cae]
       ↓ .msh file
3. FEM: FEMSolver.solve()                         [cad-cae]
       ↓ stress, displacement fields
4. MAT: CompositeMaterial(E1=150e9, E2=10e9)     [physics-m3]
       ↓ elastic constants
5. MEC: flexure_test(E=70, strength_MPa=250)      [physics-m3]
       ↓ failure mode
6. M³: MultiPhysicsAnalysis.coupled_simulation()  [kdi-m3]
       ↓ macro + meso + micro
7. VVV: VVVOrchestrator.run_all()                 [physics-m3 vvv]
       ↓ PASS/FAIL certificate
8. REP: ComplianceReport()                         [scripts/compliance]
       ↓ PQMS score
```

### Fluxo de Dados Cruzado Detalhado

```
               ┌───────────────────┐
               │ kdi_multiphysics  │
               │   (kdi-m3-bridge) │
               └──┬────┬────┬─────┘
                  │    │    │
        ┌─────────┘    │    └──────────┐
        ▼              ▼               ▼
┌──────────────┐ ┌──────────┐ ┌─────────────────┐
│ fluid_dynamics│ │thermo-   │ │electromechanical│
│ (physics-m3)  │ │dynamics  │ │ (physics-m3)     │
└──────────────┘ └──────────┘ └─────────────────┘
        │              │               │
        ▼              ▼               ▼
┌──────────────────────────────────────────┐
│         composite_model (physics-m3)      │
│         ─── fornece constantes elásticas  │
│         ─── usado por structural, m3      │
└──────────────────────────────────────────┘
```

---

## 12. O que Não Foi Implementado

### Funcionalidades Solicitadas em INSTRUCTIONS.md

| Item | Status | Motivo |
|------|--------|--------|
| **AI Assist CAD (NLP→geometria)** | ❌ Não implementado | Escopo não coberto por Spec 007. Requer NLP + integração com CadQuery |
| **UI Streamlit para simulações** | ❌ Não implementado | Requer frontend + backend de visualização |
| **OpenAPI/Swagger para API externa** | ❌ Não implementado | Documentação de API REST não iniciada |
| **CI ativo no repositório GitHub** | ⚠️ Pipeline criado, não ativado | .github/workflows/ci.yml existe, mas GitHub Actions não foi configurado no repositório |
| **Testes de carga/estresse para FEM** | ❌ Não implementado | Benchmarks existem, mas sem teste de convergência para malhas > 10k elementos |
| **Banco de materiais com interface web** | ⚠️ knowledge_base.py existe, sem UI | Apenas API Python, sem interface gráfica |

### Funcionalidades Implementadas Parcialmente

| Item | Status | Observação |
|------|--------|------------|
| Otimização topológica + manufatura aditiva | ⚠️ `topopt_manufacturing.py` existe | Sem testes de integração com `DesignOptimizer` do cad-cae |
| Documentação API (OpenAPI) | ⚠️ `docs/USAGE_GUIDE.md` + este manual | Documentação textual completa, sem especificação OpenAPI |
| CadQuery + Gmsh + CalculiX em CI | ⚠️ `Dockerfile.ci` criado | CI Docker não integrado ao GitHub Actions |

### Arquivos Limpos do Branch main

| Ação | Arquivos |
|------|----------|
| `.gitignore` atualizado | `*.egg-info/`, `__pycache__/`, `.pytest_cache/`, `.coverage` |
| Mantidos | `Plans/ethereal-wishing-quiche.md` (histórico), `scripts/agentic/state.json` (FSM) |

---

> **Versão**: 1.0.0 | **PQMS**: 92.2% | **Commit**: `5bed5ae` | **Data**: 2026-06-17
> **GitNexus**: 7.158 nós, 11.464 arestas, 387 clusters, 179 fluxos
