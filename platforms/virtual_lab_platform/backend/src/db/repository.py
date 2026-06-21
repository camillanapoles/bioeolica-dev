"""
Data Access Layer for Virtual Lab Platform.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from .models import Simulation, Material, SolverExecution, Publication


class SimulationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, name: str, description: Optional[str] = None,
               parameters: Dict[str, Any],
               material_id: Optional[UUID] = None) -> Simulation:
        sim = Simulation(
            name=name,
            description=description,
            parameters=parameters,
            material_id=material_id,
        )
        self.session.add(sim)
        self.session.commit()
        self.session.refresh(sim)
        return sim

    def get(self, sim_id: UUID) -> Optional[Simulation]:
        stmt = select(Simulation).where(Simulation.id == sim_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_material(self, material_id: UUID) -> List[Simulation]:
        stmt = select(Simulation).where(Simulation.material_id == material_id)
        return list(self.session.execute(stmt).scalars())

    def update_status(self, sim_id: UUID, status: str) -> Optional[Simulation]:
        stmt = (
            update(Simulation)
            .where(Simulation.id == sim_id)
            .values(status=status)
            .returning(Simulation)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.scalar_one_or_none()

    def add_results(self, sim_id: UUID, results: Dict[str, Any]) -> Optional[Simulation]:
        stmt = (
            update(Simulation)
            .where(Simulation.id == sim_id)
            .values(results=results)
            .returning(Simulation)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.scalar_one_or_none()


class MaterialRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, name: str, formula: Optional[str] = None,
               density: Optional[float] = None,
               youngs_modulus: Optional[float] = None,
               poisson_ratio: Optional[float] = None,
               thermal_conductivity: Optional[float] = None,
               specific_heat: Optional[float] = None,
               melting_point: Optional[float] = None) -> Material:
        mat = Material(
            name=name,
            formula=formula,
            density=density,
            youngs_modulus=youngs_modulus,
            poisson_ratio=poisson_ratio,
            thermal_conductivity=thermal_conductivity,
            specific_heat=specific_heat,
            melting_point=melting_point,
        )
        self.session.add(mat)
        self.session.commit()
        self.session.refresh(mat)
        return mat

    def get_by_name(self, name: str) -> Optional[Material]:
        stmt = select(Material).where(Material.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> List[Material]:
        stmt = select(Material)
        return list(self.session.execute(stmt).scalars())


class SolverExecutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, simulation_id: UUID, solver_name: str,
               version: Optional[str] = None,
               parameters: Optional[Dict[str, Any]] = None) -> SolverExecution:
        exec_ = SolverExecution(
            simulation_id=simulation_id,
            solver_name=solver_name,
            version=version,
            parameters=parameters or {},
            status="pending",
        )
        self.session.add(exec_)
        self.session.commit()
        self.session.refresh(exec_)
        return exec_

    def update_status(self, exec_id: UUID, status: str,
                      ended_at: Optional[datetime] = None,
                      logs: Optional[str] = None,
                      result_path: Optional[str] = None) -> Optional[SolverExecution]:
        stmt = (
            update(SolverExecution)
            .where(SolverExecution.id == exec_id)
            .values(
                status=status,
                ended_at=ended_at,
                logs=logs,
                result_path=result_path,
            )
            .returning(SolverExecution)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        return result.scalar_one_or_none()

    def get_by_simulation(self, simulation_id: UUID) -> List[SolverExecution]:
        stmt = select(SolverExecution).where(SolverExecution.simulation_id == simulation_id)
        return list(self.session.execute(stmt).scalars())


class PublicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, simulation_id: UUID,
               title: Optional[str] = None,
               authors: Optional[List[Dict[str, str]]] = None,
               abstract: Optional[str] = None,
               doi: Optional[str] = None,
               file_path: Optional[str] = None) -> Publication:
        pub = Publication(
            simulation_id=simulation_id,
            title=title,
            authors=authors or [],
            abstract=abstract,
            doi=doi,
            file_path=file_path,
        )
        self.session.add(pub)
        self.session.commit()
        self.session.refresh(pub)
        return pub
