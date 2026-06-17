# Design: AI Assist CAD — Knowledge-Driven Machine Design System

> **Date**: 2026-06-17 | **Status**: Draft | **PQMS Target**: ≥ 94%

---

## 1. Philosophy

Projeto **agnóstico** conforme KDI P1 — "O método é o produto. O conteúdo é variável."

| Invariante (fixo) | Variável (config) |
|------------------|-------------------|
| Pipeline: NLP → CAD → KDI M³ → VVV → Viz | Máquina: gerador, turbina, motor, compressor... |
| Regras de mistura (Voigt, Halpin-Tsai, Hashin-Rosen) | Materiais: aço, alumínio, compósito, cerâmica... |
| Equações de dimensionamento (tensão, torque, potência) | Processos: jateamento, oxidação, têmpera, soldagem... |
| Mesh: h-refinement adaptativo com 3 níveis | Geometria: parâmetros de projeto calculados pela IA |
| VVV: 6 critérios C11 | Cargas: contexto do usuário |

---

## 2. Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                     AI ASSIST CAD ENGINE                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  External Data (Single Source of Truth)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────────┐ │
│  │materials │ │processes │ │ machine_know │ │ standards       │ │
│  │.json     │ │.json     │ │ .json        │ │ .json (normas)  │ │
│  └──────────┘ └──────────┘ └──────────────┘ └────────────────┘ │
│                                                                   │
│  1. NLP INTERFACE                                                 │
│     "Projete gerador 3MW, carcaça alumínio 3 camadas 6mm"        │
│     ├─ Extrai: [MÁQUINA] [POTÊNCIA] [MATERIAL] [CAMADAS]        │
│     └─ Se ambiguidade → pergunta (1 por vez)                    │
│                                                                   │
│  2. KNOWLEDGE ENGINE (WebSearch + RAG)                            │
│     ├─ Busca: normas (IEC, NBR, ASTM), parâmetros SOTA          │
│     ├─ Aplica: equações de dimensionamento                       │
│     └─ Retorna: parâmetros de projeto calculados                 │
│                                                                   │
│  3. COMPOSITE LAYER DESIGNER                                      │
│     ├─ LayerPattern: [mat: X% + mat: Y% + binder] → espessura   │
│     ├─ N pilhas → espessura total                                │
│     ├─ E_efetivo via Halpin-Tsai / Hashin-Rosen                  │
│     └─ Fabricação opcional: jateamento, oxidação, têmpera...     │
│                                                                   │
│  4. AI CAD GENERATOR (FreeCAD/CadQuery)                           │
│     ├─ Conhecimento de máquinas → dimensiona geometricamente     │
│     ├─ Gera STEP + VTK + malha                                   │
│     └─ Aplica materiais + layers aos componentes                 │
│                                                                   │
│  5. KDI M³ ANALYSIS (multi-domínio selecionável)                  │
│     ├─ Macro: cargas, vento, torque, rpm                         │
│     ├─ Meso: Kt, Tsai-Wu, von Mises, contato                    │
│     ├─ Micro: homogeneização, lâminas, microestrutura            │
│     └─ Domínios: [estrutural] [térmico] [fluido] [eletromag]     │
│                                                                   │
│  6. VVV CERTIFICATION (C11 — 6 critérios)                        │
│     ├─ Malha: 3 níveis (gross/médio/fino), erro < 5%            │
│     ├─ Benchmark: Kirsch Kt=3.0, PL³/(3EI)                       │
│     └─ Resultado: PASS/FAIL + return_phase                        │
│                                                                   │
│  7. 3D INTERACTIVE VIEWER (Three.js + Streamlit)                  │
│     ├─ Rotação/zoom (OrbitControls)                               │
│     ├─ Heat maps por campo escalar sobre o design                │
│     ├─ Seletor de domínio + componente + escala                  │
│     ├─ Corte transversal (ver camadas)                           │
│     ├─ Gráficos (tensão por camada, distribuição)                │
│     └─ VVV badge + export STEP/STL/PNG/PDF                      │
│                                                                   │
│  GPU ACCELERATION (transversal — NVIDIA)                          │
│  ├─ Modelagem: CuPy (operações matriciais)                       │
│  ├─ Renderização: WebGL (Three.js)                               │
│  └─ Cálculos: GPUAccelerator (CG, SIMP, FEM)                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Mesh Best Practices

| Objetivo | Elemento | Tamanho | Refino |
|----------|----------|---------|--------|
| Tensão estrutural | Hex20 | L/20 | Concentração: L/50 |
| Flambagem | Hex8 | L/15 | Global uniforme |
| Frequência natural | Hex20 | L/15 | Massa: refino |
| Contato | Hex8 reduzido | L/30 | Zona contato: L/100 |
| Térmico | Tetra4 | L/10 | Gradiente: L/30 |
| Multi-domínio | Hex20 | L/20 | Adaptativo h-refino |
| VVV 3 níveis | Gross: L/10 | Médio: L/20 | Fino: L/40 |

---

## 4. Subsistemas e Ordem de Implementação

| Fase | Subsistema | Depende de | Esforço |
|------|-----------|------------|---------|
| **P1** | NLP Interface + Composite Layer Designer | — | ~2h |
| **P2** | AI CAD Generator (Parametric Engine) | P1 | ~4h |
| **P3** | KDI M³ Integration (multi-domínio) | P1+P2 | ~3h |
| **P4** | 3D Interactive Viewer (Three.js + Streamlit) | P2+P3 | ~6h |
| **P5** | GPU Acceleration + VVV certification | P2+P3 | ~2h |
| **P6** | Mesh adaptive refinement | P2 | ~1h |
| **P7** | Documentation + compliance | P1-P6 | ~1h |

---

## 5. Dados de Entrada (Single Source of Truth)

```
data/
├── materials.json       # Base de materiais (E, ν, ρ, σ_y, custo...)
├── processes.json       # Processos de fabricação (parâmetros)
├── machine_knowledge/   # Templates paramétricos de máquinas
│   ├── generator_pmsg.json
│   ├── wind_turbine.json
│   ├── compressor.json
│   └── ...
└── standards/           # Normas
    ├── astm.json
    ├── iec.json
    └── nbr.json
```

---

## 6. Critérios de Sucesso

1. **Agnosticismo**: sistema funciona para 3+ máquinas diferentes sem alterar código
2. **NLP→CAD**: 80%+ das descrições naturais geram geometria coerente
3. **M³ analysis**: fluxo macro-meso-micro executa em < 30s para malha de 10k elementos
4. **VVV**: certificação automática com PASS em todos os 6 critérios
5. **Visualização**: renderização 3D interativa > 30 FPS em GPU NVIDIA
6. **Layer designer**: cálculo de homogeneização com erro < 5% vs. literatura
7. **PQMS**: ≥ 94% na auditoria de compliance
