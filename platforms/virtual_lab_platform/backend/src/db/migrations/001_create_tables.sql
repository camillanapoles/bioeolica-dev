-- Create tables for Virtual Lab Platform
-- This is a simple SQL migration; in production use Flyway/Liquibase with versioning.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    formula VARCHAR(255),
    density DOUBLE PRECISION,
    youngs_modulus DOUBLE PRECISION,
    poisson_ratio DOUBLE PRECISION,
    thermal_conductivity DOUBLE PRECISION,
    specific_heat DOUBLE PRECISION,
    melting_point DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'created',
    parameters JSONB NOT NULL,
    results JSONB,
    material_id UUID REFERENCES materials(id)
);

CREATE TABLE solver_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id),
    solver_name VARCHAR(100) NOT NULL,
    version VARCHAR(50),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    logs TEXT,
    parameters JSONB,
    result_path VARCHAR(500),
    UNIQUE (simulation_id, solver_name)
);

CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_id UUID NOT NULL REFERENCES simulations(id),
    title VARCHAR(500),
    authors JSONB,
    abstract TEXT,
    doi VARCHAR(255),
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    file_path VARCHAR(500)
);

-- Indexes for frequent queries
CREATE INDEX idx_simulations_status ON simulations(status);
CREATE INDEX idx_solver_executions_simulation ON solver_executions(simulation_id);
CREATE INDEX idx_publications_simulation ON publications(simulation_id);
