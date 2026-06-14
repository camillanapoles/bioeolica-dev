# Feature Specification: Turbine Upscaling for Economic Viability

**Feature Directory**: `specs/002-turbine-upscaling`

**Created**: 2026-06-13

**Status**: Draft

**Input**: Design iteration to resolve SC-004 (economic targets) and SC-005 (energy sizing) validation failures. Current 0.82 kW VAWT H-rotor Darrieus prototype fails all economic targets and covers only 24.6% of community demand. Root cause: fixed costs dominate at sub-1 kW scale.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Engineer: Upscaled Turbine System Design (Priority: P1)

The energy systems engineer must design an upscaled wind turbine system that meets economic viability targets (LCOE < $0.15/kWh, cost < $3,000/kW) and community demand coverage (>= 100% of 38 kWh/day at Assentamento Sertao Sustentavel). The design must compare vertical-axis (VAWT H-rotor Darrieus) vs horizontal-axis (HAWT Archimedes) topologies across the 10-15 kW range to identify which configuration achieves economic viability for semi-arid low-wind-speed conditions.

**Why this priority**: Without a turbine that economically meets community demand, the entire energy system is invalid — the SC-004/SC-005 CHECK constraints on `energy_systems` table block insertion of any failing design.

**Independent Test**: Can be tested by computing economic metrics (LCOE, cost/kW, demand coverage) for any proposed turbine configuration against SC-004/SC-005 targets. Passing all 4 economic checks = successful iteration.

**Acceptance Scenarios**:

1. **Given** a set of candidate turbine designs (VAWT and HAWT) in the 5-20 kW range with cost models derived from material bill-of-materials and manufacturing process analysis, **When** each design's LCOE and cost-per-kW are computed using the validated LCOE model (`src/02-wind-energy/energy-system/sizing_lcoe.py`), **Then** at least one design must achieve LCOE < $0.15/kWh AND cost-per-kW < $3,000/kW.
2. **Given** the economically viable turbine design, **When** its annual energy production (AEP) is computed against the validated wind resource profile for the semi-arid region (mean 5.5 m/s at 30m hub height, Weibull k=2.0), **Then** the system must achieve >= 100% coverage of the community's 38 kWh/day demand (including 20% growth margin = 45.6 kWh/day design demand).
3. **Given** the upscaled design, **When** an energy storage system (battery bank) is sized for autonomy >= 2 days, **Then** the combined turbine + storage system must maintain capacity factor >= 20%.
4. **Given** the final turbine design parameters, **When** registered in the `energy_systems` database table with all computed metrics, **Then** the SC-004 and SC-005 CHECK constraints must PASS and `run_all_checks.sh` must report 28/28 PASS.

---

### User Story 2 - Engineer: Manufacturing Cost Model (Priority: P1)

The manufacturing engineer must develop a bottom-up cost model for the upscaled turbine that accounts for materials (composite biomaterial blades, steel tower, permanent magnet generator, power electronics), manufacturing processes (blade infusion molding, tower fabrication, nacelle assembly), and balance-of-system (transport, installation, controller, inverter, battery bank). The cost model must explain why the current 0.82 kW prototype costs $39,527 ($48,204/kW) and identify what scale and design choices bring cost below $3,000/kW.

**Why this priority**: Economic viability is the binding constraint — cost-per-kW is 16x over target. Without understanding cost scaling behavior, no design can be validated economically.

**Independent Test**: Can be tested by decomposing cost into scaling vs. fixed components and verifying the cost model predicts realistic costs at multiple turbine scales.

**Acceptance Scenarios**:

1. **Given** the current 0.82 kW prototype bill-of-materials ($39,527 total), **When** costs are decomposed into scaling components (rotor, generator, tower proportional to size) vs. fixed components (controller, transport, installation), **Then** the scaling model must predict costs within +/- 20% for at least 3 distinct turbine sizes.
2. **Given** the validated cost scaling model, **When** applied to candidate turbine sizes (3, 5, 10, 15, 20 kW), **Then** the cost model must identify the minimum turbine size where cost-per-kW drops below $3,000/kW.
3. **Given** the identified minimum viable turbine size, **When** sensitivity analysis is run on key cost drivers (tower height, generator type, battery capacity, transport distance), **Then** the dominant cost drivers and their elasticities must be documented.

---

### User Story 3 - Engineer: Integrated Energy System Registration (Priority: P2)

The systems engineer must register the final upscaled turbine + storage energy system in the project database's `energy_systems` table with all required metrics (LCOE, cost/kW, capacity factor, autonomy days, demand coverage), ensure the SC-004/SC-005 CHECK constraints pass, and update the validation record so that `run_all_checks.sh` reports 28/28 PASS.

**Why this priority**: The database is the single source of truth — registration closes the validation loop and unblocks downstream tasks (T074, T069, T068).

**Independent Test**: Can be tested by running `run_all_checks.sh` and confirming 28/28 PASS with the new energy system.

**Acceptance Scenarios**:

1. **Given** the upscaled turbine design with all computed metrics, **When** registered in `energy_systems` with lcoe_usd_per_kwh < 0.15, cost_per_kw_usd < 3000, autonomy_days >= 2.0, capacity_factor_pct >= 20.0, **Then** INSERT must succeed (CHECK constraints not violated).
2. **Given** the successful registration, **When** `run_all_checks.sh` is executed, **Then** SC-004 (both checks) and SC-005 (both checks) must report PASS.

---

### Edge Cases

- What happens if NO turbine size achieves all 4 economic targets simultaneously? (e.g., LCOE < $0.15 but cost/kW > $3k, or vice versa)
- How does the system handle wind resource variability — extended low-wind periods (>7 days) requiring diesel backup?
- What if the composite biomaterial blade cost does not scale linearly with turbine rating (tooling cost dominates)?
- How does transport cost to remote semi-arid communities affect economic viability at different scales?
- What if the community demand profile changes seasonally (irrigation vs. dry season)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute LCOE (USD/kWh) for any candidate turbine configuration using the validated `sizing_lcoe.py` methodology with inputs: rated power, rotor diameter, hub height, installed cost, O&M cost, wind resource Weibull parameters, discount rate, and lifetime.
- **FR-002**: System MUST compute cost-per-kW (USD/kW) as total installed cost divided by rated power, including decomposition into scaling costs (rotor, generator, tower, foundation) and fixed costs (controller, inverter, transport, installation).
- **FR-003**: System MUST compute annual energy production (AEP) using site-specific wind resource data (mean 5.5 m/s at 30m, Weibull k=2.0) and turbine power curve appropriate to the selected topology (VAWT vs HAWT).
- **FR-004**: System MUST compute demand coverage (%) as (AEP / 365) / daily_demand, with minimum daily demand of 38 kWh/day and design demand of 45.6 kWh/day (20% growth margin).
- **FR-005**: System MUST size battery storage to achieve minimum 2 days autonomy at design demand, considering battery depth-of-discharge (DoD 80%), round-trip efficiency (85%), and temperature derating for semi-arid conditions.
- **FR-006**: System MUST compare VAWT H-rotor Darrieus and HAWT Archimedes topologies at minimum 3 turbine sizes (5, 10, 15 kW) and recommend the optimal configuration.
- **FR-007**: System MUST register the final design in `energy_systems` table with all computed metrics and verify SC-004/SC-005 CHECK constraints pass.
- **FR-008**: System MUST document all cost model assumptions, scaling factors, source references, and uncertainty ranges for auditability.

### Key Entities

- **TurbineConfiguration**: Rated power (kW), topology type (VAWT/HAWT), rotor diameter (m), hub height (m), power curve coefficients, estimated material cost ($), estimated manufacturing cost ($), estimated BOS cost ($)
- **EnergySystem**: The registered row in `energy_systems` table with lcoe_usd_per_kwh, cost_per_kw_usd, autonomy_days, capacity_factor_pct, demand_coverage_pct — must satisfy SC-004 and SC-005 CHECK constraints
- **CostScalingModel**: Mathematical model decomposing total cost into size-proportional terms (rotor_mass × $/kg, generator_rating × $/kW, tower_height × $/m) and fixed terms (controller $X, transport $Y, installation $Z)
- **WindResourceProfile**: Site-specific parameters (mean_wind_speed, weibull_k, air_density, turbulence_intensity) for Assentamento Sertao Sustentavel, semi-arid Brazil

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-004a**: LCOE < $0.15/kWh for the selected turbine configuration (measured by `sizing_lcoe.py` computation).
- **SC-004b**: Cost-per-kW < $3,000/kW for the selected turbine configuration (measured as total installed cost / rated power).
- **SC-005a**: Demand coverage >= 100% of community daily demand (38 kWh/day baseline, 45.6 kWh/day design target).
- **SC-005b**: Autonomy >= 2 days with battery storage sized for design demand.
- **SC-005c**: Capacity factor >= 20% for the combined turbine + storage system.
- **SC-006**: Cost scaling model validated against minimum 3 turbine sizes with error < 20%.
- **SC-007**: Recommended turbine topology (VAWT vs HAWT) documented with quantitative rationale including LCOE, cost/kW, maintenance requirements, and community manufacturing feasibility.
- **SC-008**: All computed metrics, input parameters, cost model assumptions, and uncertainty ranges documented in the project knowledge base (`knowledge/` directory).
- **SC-009**: `run_all_checks.sh` reports 28/28 PASS after energy system registration.

## Clarifications

### Session 2026-06-13

- Q1 (Manufacturing capability — welding equipment access): Deferred to final structure and annexes per user instruction. Material modeling (Part 1) is primary focus; manufacturing detail deferred.
- Q2 (Grid connection vs. off-grid): Deferred to final structure and annexes per user instruction. System configuration detail deferred to planning phase.
- Q3 (Diesel backup for extended low-wind): Deferred to final structure and annexes per user instruction. Backup strategy deferred to planning phase.
- Q4 (Seasonal demand profile): Transformed from clarification question into full engineering deliverable — LAB must produce average + seasonal energy demand calculation with complete VVV methodology, covering all possible profile types with cost-benefit analysis. Pending execution as standalone calculation artifact.

**Priority Refocus (User Directive)**: PART 1 (PRIMARY) — Mathematical/computational modeling of the new composite material (paper mache + graphite coating), including real mechanical test simulation, materials resistance analysis, treatments, and fabrication processes (technical, chemical). PART 2 (APPLICATION) — Wind generator modeling and community energy analysis (average + seasonal demand). Scope reordered: material science precedes turbine design iteration.

## Assumptions

- Wind resource at Assentamento Sertao Sustentavel: mean 5.5 m/s at 30m hub height, Weibull shape parameter k=2.0, annual average air density 1.15 kg/m³ (semi-arid, 400m elevation).
- Community demand: 38 kWh/day baseline, 45.6 kWh/day design (20% growth margin per community planning guidelines).
- VAWT topology: H-rotor Darrieus with NACA 0018 airfoil, 3 blades, solidity 0.3, nominal tip speed ratio 3.5.
- HAWT topology: 3-blade upwind with optimal tip speed ratio 6.0, pitch control for overspeed protection.
- Battery: Lithium-ion (LiFePO4), 80% depth of discharge, 85% round-trip efficiency, $200/kWh at system level (2026 pricing), 10-year lifetime.
- Generator: Permanent magnet synchronous (PMSG) for both topologies — eliminates gearbox (reduced maintenance, higher reliability for remote communities).
- Tower: Lattice steel tower for VAWT (easier transport, on-site assembly), tubular steel for HAWT (standard). Height scaled with rotor diameter.
- Economic: Discount rate 8% (Brazilian development project rate), 20-year project lifetime, O&M 2% of installed cost annually.
- Transport cost to remote semi-arid community: $0.50/kg/km for first 200 km from regional center, then $0.30/kg/km unpaved road surcharge for remaining distance.
- The composite biomaterial (paper mache + graphite coating) blade cost scales with blade mass at $15/kg manufactured cost (labor + materials + tooling amortization).
- [NEEDS CLARIFICATION: Community manufacturing capability — does the community have access to welding equipment for tower fabrication, or must all components be prefabricated and transported?]
- [NEEDS CLARIFICATION: Grid connection vs. off-grid — is the system designed for standalone off-grid operation with full battery backup, or can it leverage a weak grid connection when available?]
- [NEEDS CLARIFICATION: Diesel backup — is a diesel generator included as backup for extended low-wind periods, and if so, what fraction of annual energy is allowed from diesel?]
