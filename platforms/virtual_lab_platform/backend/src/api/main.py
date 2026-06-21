"""
FastAPI application for the Virtual Lab Platform.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db.session import get_db, init_db
from ..db.models import Simulation, Material, SolverExecution, Publication
from ..db.repository import (
    SimulationRepository,
    MaterialRepository,
    SolverExecutionRepository,
    PublicationRepository,
)
from ..workflow.tasks import run_simulation_task
from ..auth.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_admin_user,
    get_current_researcher_or_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from pydantic import BaseModel, Field

# Initialize DB tables on startup
init_db()

app = FastAPI(
    title="Virtual Lab Platform API",
    description="API for managing deep‑tech computational laboratories",
    version="0.1.0",
)

# ----------------------------------------------------------------------
# Pydantic schemas (request/response)
# ----------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MaterialBase(BaseModel):
    name: str
    formula: Optional[str] = None
    density: Optional[float] = None
    youngs_modulus: Optional[float] = None
    poisson_ratio: Optional[float] = None
    thermal_conductivity: Optional[float] = None
    specific_heat: Optional[float] = None
    melting_point: Optional[float] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: uuid.UUID
    created_at: str

    class Config:
        orm_mode = True

class SimulationBase(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: dict = Field(default_factory=dict)
    material_id: Optional[uuid.UUID] = None

class SimulationCreate(SimulationBase):
    pass

class SimulationResponse(SimulationBase):
    id: uuid.UUID
    created_at: str
    updated_at: str
    status: str
    results: Optional[dict] = None

    class Config:
        orm_mode = True

class SolverExecutionBase(BaseModel):
    solver_name: str
    version: Optional[str] = None
    parameters: dict = Field(default_factory=dict)

class SolverExecutionCreate(SolverExecutionBase):
    pass

class SolverExecutionResponse(SolverExecutionBase):
    id: uuid.UUID
    simulation_id: uuid.UUID
    started_at: str
    ended_at: Optional[str] = None
    status: str
    logs: Optional[str] = None
    result_path: Optional[str] = None

    class Config:
        orm_mode = True

class PublicationBase(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[dict]] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    file_path: Optional[str] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationResponse(PublicationBase):
    id: uuid.UUID
    simulation_id: uuid.UUID
    uploaded_at: str

    class Config:
        orm_mode = True

# ----------------------------------------------------------------------
# Dependency
# ----------------------------------------------------------------------
def get_db_session() -> Session:
    return next(get_db())

# ----------------------------------------------------------------------
# Auth endpoints
# ----------------------------------------------------------------------
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------------------------------------------------------------
# Material endpoints
# ----------------------------------------------------------------------
@app.post("/materials/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_researcher_or_admin_user),
):
    repo = MaterialRepository(db)
    db_material = repo.create(
        name=material.name,
        formula=material.formula,
        density=material.density,
        youngs_modulus=material.youngs_modulus,
        poisson_ratio=material.poisson_ratio,
        thermal_conductivity=material.thermal_conductivity,
        specific_heat=material.specific_heat,
        melting_point=material.melting_point,
    )
    return db_material

@app.get("/materials/", response_model=List[MaterialResponse])
def list_materials(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = MaterialRepository(db)
    materials = repo.list_all()
    return materials[skip : skip + limit]

@app.get("/materials/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = MaterialRepository(db)
    material = repo.get_by_name(str(material_id))  # we only have get_by_name; adjust if needed
    if not material:
        # fallback: we could implement get by id; for simplicity we list and filter
        all_mats = repo.list_all()
        material = next((m for m in all_mats if m.id == material_id), None)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

# ----------------------------------------------------------------------
# Simulation endpoints
# ----------------------------------------------------------------------
@app.post("/simulations/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_simulation(
    sim: SimulationCreate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_researcher_or_admin_user),
):
    repo = SimulationRepository(db)
    db_sim = repo.create(
        name=sim.name,
        description=sim.description,
        parameters=sim.parameters,
        material_id=sim.material_id,
    )
    return db_sim

@app.get("/simulations/", response_model=List[SimulationResponse])
def list_simulations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = SimulationRepository(db)
    # For simplicity, get all then slice; in production use pagination query
    stmt = db.query(Simulation)
    sims = stmt.offset(skip).limit(limit).all()
    return sims

@app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = SimulationRepository(db)
    sim = repo.get(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim

@app.post("/simulations/{simulation_id}/run", response_model=dict)
def run_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_researcher_or_admin_user),
):
    # Trigger the Celery task
    task = run_simulation_task.delay(str(simulation_id))
    return {"task_id": task.id, "detail": "Simulation workflow started"}

@app.get("/simulations/{simulation_id}/status")
def get_simulation_status(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = SimulationRepository(db)
    sim = repo.get(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {
        "simulation_id": str(sim.id),
        "status": sim.status,
        "created_at": sim.created_at.isoformat(),
        "updated_at": sim.updated_at.isoformat(),
    }

# ----------------------------------------------------------------------
# Solver execution endpoints
# ----------------------------------------------------------------------
@app.get("/simulations/{simulation_id}/executions", response_model=List[SolverExecutionResponse])
def get_solver_executions(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_active_user),
):
    repo = SolverExecutionRepository(db)
    executions = repo.get_by_simulation(simulation_id)
    return executions

# ----------------------------------------------------------------------
# Publication endpoints
# ----------------------------------------------------------------------
@app.post("/publications/", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
def create_publication(
    pub: PublicationCreate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_researcher_or_admin_user),
):
    repo = PublicationRepository(db)
    db_pub = repo.create(
        simulation_id=pub.simulation_id,
        title=pub.title,
        authors=pub.authors,
        abstract=pub.abstract,
        doi=pub.doi,
        file_path=pub.file_path,
    )
    return db_pub

# ----------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------
@app.get("/healthz")
def health_check():
    return {"status": "ok"}
