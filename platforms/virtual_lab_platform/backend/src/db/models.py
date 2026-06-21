"""
SQLAlchemy models for the Virtual Lab Platform.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Text,
    Boolean,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(String(50), default="created")  # created, queued, running, completed, failed
    parameters = Column(JSON, nullable=False)  # store input parameters as JSON
    results = Column(JSON)  # store output results as JSON
    material_id = Column(PG_UUID(as_uuid=True), ForeignKey("materials.id"))
    material = relationship("Material", back_populates="simulations")

    def __repr__(self) -> str:
        return f"<Simulation {self.id}>"


class Material(Base):
    __tablename__ = "materials"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    formula = Column(String(255))
    density = Column(Float)  # g/cm^3
    youngs_modulus = Column(Float)  # Pa
    poisson_ratio = Column(Float)
    thermal_conductivity = Column(Float)  # W/(m·K)
    specific_heat = Column(Float)  # J/(kg·K)
    melting_point = Column(Float)  # K
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    simulations = relationship("Simulation", back_populates="material")

    def __repr__(self) -> str:
        return f"<Material {self.name}>"


class SolverExecution(Base):
    __tablename__ = "solver_executions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(PG_UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    solver_name = Column(String(100), nullable=False)  # e.g., openfoam, calculix
    version = Column(String(50))
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime)
    status = Column(String(50))  # pending, running, success, failed
    logs = Column(Text)
    parameters = Column(JSON)  # solver-specific parameters
    result_path = Column(String(500))  # path to output artifacts in storage
    simulation = relationship("Simulation")

    __table_args__ = (UniqueConstraint("simulation_id", "solver_name", name="uq_solver_exec"),)

    def __repr__(self) -> str:
        return f"<SolverExecution {self.id} for sim {self.simulation_id}>"


class Publication(Base):
    __tablename__ = "publications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(PG_UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    title = Column(String(500))
    authors = Column(JSON)  # list of author dicts
    abstract = Column(Text)
    doi = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_path = Column(String(500))  # path to manuscript or dataset
    simulation = relationship("Simulation")

    def __repr__(self) -> str:
        return f"<Publication {self.id}>"
