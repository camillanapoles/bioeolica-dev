# Requirements for Computational Lab Creation Platform

## Functional Requirements
1. Lab Type Definition
   - Ability to define custom lab types with:
     * Stages (based on Ciclo de Produção or custom)
     * Data model (entities, attributes, types, units, validation rules)
     * Workflow configuration (task types, solver mappings, data flow)
     * Visualization pipelines per stage
     - Metadata (domain, tags, version, description, scope)
   - Version control for lab types (semver)
   - Templates for common lab types (materials, CFD, structural, energy, etc.)

2. Lab Instance Management
   - Create instances from lab types
   - Track current stage and progression
   - Store stage-specific data and task completion status
   - Manage attachments (documents, datasets, etc.)
   - Collaboration features (comments, 5W1H log viewing)

3. Dynamic User Interface
   - Stage-based dashboards showing current tasks and visualizations
   - Forms generated from lab type data model (JSON Schema to Form)
   - Visualization components for 2D/3D scientific data, charts, and custom views
   - RAG knowledge integration for attaching and searching research materials

4. Workflow Execution
   - Extensible workflow engine supporting:
     * Solver tasks (OpenFOAM, CalculiX, MFEM, custom)
     * Manual tasks (human approvals, data entry)
     * Script tasks (Python, MATLAB, etc.)
     * Approval tasks (with notifications)
   - Parallel and conditional task execution
   - Task retry, timeout, and escalation policies
   - Progress monitoring and detailed logging

5. Single Source of Truth (SSOT)
   - Centralized repository for materials, constants, reference data
   - Versioned entities with temporal querying
   - SSOT-aware UI components (dropdowns, autocomplete)
   - Lab type definition specifies which attributes must come from SSOT

6. 5W1H Logging
   - Automatic logging of all user and system actions in structured format
   - Log storage with querying capabilities (by lab, user, time, action type)
   - Log correlation via trace IDs for distributed tracing
   - UI components to view and filter logs for lab instances

7. Mandato Enforcement (M0-M9)
   - M0: Automatic GitNexus impact analysis for changes to lab types/workflows/SSOT; blocks HIGH/CRITICAL risk without override
   - M1: Prevents stage advancement until all required tasks are complete and validated
   - M2: Enforces sequential stage progression by default (override requires justification)
   - M3: Requires full definition updates for lab type changes; validation tests on save
   - M4: Prohibits hardcoding of lab-relevant values; all must come from SSOT or lab type definition
   - M5: Generates 5W1H logs for all actions; requires valid logs for action acceptance
   - M6: Integrates with RAG knowledge base for storing/retrieving research materials
   - M7: Warns when users attempt to add out-of-scope data or tasks
   - M8: Provides lab instance archiving with point-in-time snapshots and artifact preservation
   - M9: Synchronizes lab instance milestones with external issue trackers (tasksToIssue)

8. Continuity and Reproducibility
   - Lab instance archiving:
     * Point-in-time data snapshot (including SSOT references)
     * Copy of all associated artifacts to WORM storage
     * 5W1H log archive and environment specification (tool versions, config)
     * DOI-like handle for citation
   - Reconstitution from archive:
     * Browse/search archive catalog
     * Fork new instances from archives (option to update to latest lab type)
   - Lab type evolution with migration scripts for non-breaking changes

9. Extensibility and Integration
   - Plugin system for solver tasks, manual tasks, and visualization components
   - Event-driven architecture for loose coupling between services
   - APIs for external integration (lab type definition, instance data, results)
   - Administration UI for managing plugins, users, and system configuration

## Non-Functional Requirements
1. Performance
   - Support 100+ concurrent lab instances
   - UI response time < 2s for standard operations
   - Visualization rendering < 5s for typical scientific datasets
   - Workflow engine scales horizontally with load

2. Scalability
   - Microservices architecture for independent scaling
   - Database read replicas and query optimization
   - Object storage for artifacts and archives
   - Caching layers for SSOT and frequently accessed data

3. Security
   - Authentication and authorization (RBAC, JWT-based)
   - Input validation and sanitization
   - Audit trails for all sensitive operations
   - Secure storage of credentials and secrets
   - Regular security scanning and penetration testing

4. Reliability
   - Service health checks and circuit breakers
   - Automated failover for critical services
   - Data backups and disaster recovery procedures
   - Graceful degradation for non-critical features

5. Usability
   - Progressive disclosure of complexity
   - Role-based views (designer vs. researcher vs. student)
   - Contextual help and tooltips
   - System Usability Scale (SUS) target > 80
   - Time-to-first-lab-type < 30 minutes for trained users

6. Observability
   - Comprehensive logging (structured, correlated)
   - Metrics collection (Request rates, error rates, durations)
   - Distributed tracing (via trace IDs in 5W1H logs)
   - Health dashboards and alerting

## Out of Scope
- Development of new scientific solvers (focus is on integrating existing open-source solvers)
- Hardware-specific optimizations (GPU, FPGA) - though plugin system can accommodate them
- Domain-specific AI/ML models (though RAG and workflow engine can integrate them)
- Legal/compliance consulting for regulated industries (platform provides tools but not legal advice)

## Acceptance Criteria
1. A user can define a new lab type (e.g., "Microchip Recycling for Tobogã Material") with custom stages, data model, and workflow.
2. A user can create an instance of that lab type, progress through stages via the UI, and execute tasks (including solver tasks).
3. The platform enforces all mandatos M0-M9; attempts to violate them are blocked or require justification and logging.
4. Lab instances can be archived and reconstituted with full reproducibility.
5. The system achieves target performance and usability metrics.
