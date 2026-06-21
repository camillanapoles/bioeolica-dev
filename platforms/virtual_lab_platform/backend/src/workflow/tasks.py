"""
Celery tasks for executing simulation workflows with real solvers via Docker.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from celery import Celery
from sqlalchemy.orm import Session

# Import local Celery app
from .celery_app import celery_app

# Solver preparation functions
from .solvers.openfoam import prepare_openfoam_case
from .solvers.calculix import prepare_calculix_case
from .solvers.mfem import prepare_mfem_case

from ..db.session import SessionLocal
from ..db.models import Simulation, SolverExecution
from ..db.repository import (
    SimulationRepository,
    SolverExecutionRepository,
    MaterialRepository,
)

logger = logging.getLogger(__name__)

def get_db_session() -> Session:
    return SessionLocal()

# Environment-configurable base paths
WORKDIR_BASE = os.getenv("WORKDIR_BASE")
if not WORKDIR_BASE:
    raise RuntimeError("WORKDIR_BASE environment variable must be set")
STORAGE_BASE = os.getenv("STORAGE_BASE")
if not STORAGE_BASE:
    raise RuntimeError("STORAGE_BASE environment variable must be set")

# Solver image names (can be overridden via env)
OPENFOAM_IMAGE = os.getenv("OPENFOAM_IMAGE", "openfoam/openfoam2312")
CALCULIX_IMAGE = os.getenv("CALCULIX_IMAGE", "calculix:latest")
MFEM_IMAGE = os.getenv("MFEM_IMAGE", "mfem:latest")

def _prepare_solver_input(solver_name: str, params: Dict[str, Any]) -> str:
    """
    Prepare solver input files in a unique workdir under WORKDIR_BASE.
    Returns the absolute path to the workdir.
    """
    workdir_id = uuid.uuid4().hex
    workdir = os.path.join(WORKDIR_BASE, f"virtuallab_{workdir_id}")
    os.makedirs(workdir, exist_ok=True)

    if solver_name == "openfoam":
        prepare_openfoam_case(params, workdir)
    elif solver_name == "calculix":
        prepare_calculix_case(params, workdir)
    elif solver_name == "mfem":
        prepare_mfem_case(params, workdir)
    else:
        raise ValueError(f"Unknown solver: {solver_name}")

    return workdir

def _run_solver_container(solver_name: str, workdir: str) -> tuple[int, str, str]:
    """
    Run the Docker container for the given solver.
    Returns (returncode, stdout, stderr).
    """
    # Ensure workdir is absolute
    workdir = os.path.abspath(workdir)

    if solver_name == "openfoam":
        image = OPENFOAM_IMAGE
        # The OpenFOAM image expects to run inside /case; we set workdir to /case
        # We'll mount workdir to /case and run the default CMD (blockMesh && simpleFoam)
        cmd = ["docker", "run", "--rm",
               "-v", f"{workdir}:/case",
               "--workdir", "/case",
               image]
    elif solver_name == "calculix":
        image = CALCULIX_IMAGE
        # The calculix image we made expects the input file to be model.inp
        # and runs `calculix -i model`. We'll pass the basename without extension.
        # We'll mount workdir to /case and run the command.
        cmd = ["docker", "run", "--rm",
               "-v", f"{workdir}:/case",
               "--workdir", "/case",
               image,
               "calculix", "-i", "model"]
    elif solver_name == "mfem":
        image = MFEM_IMAGE
        # Assume MFEM image has an entrypoint that runs mfem with a JSON input.
        # We'll mount workdir and run mfem input.json (assuming it reads input.json by default or we specify)
        cmd = ["docker", "run", "--rm",
               "-v", f"{workdir}:/case",
               "--workdir", "/case",
               image,
               "mfem"]  # adjust if needed
    else:
        raise ValueError(f"Unknown solver: {solver_name}")

    logger.info(f"Running solver {solver_name} with command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as e:
        return -1, e.stdout or "", e.stderr or f"Timeout after {e.timeout} seconds"
    except Exception as e:
        return -2, "", str(e)

def _store_solver_output(solver_name: str, workdir: str, results: Dict[str, Any]) -> str:
    """
    Store solver output (including results.json and any logs) to storage under STORAGE_BASE.
    Returns the relative path (from STORAGE_BASE) where the output is stored.
    """
    storage_id = uuid.uuid4().hex
    storagedir = os.path.join(STORAGE_BASE, f"virtuallab_{storage_id}")
    os.makedirs(storagedir, exist_ok=True)

    # Copy the entire workdir to storage (preserving input and output)
    shutil.copytree(workdir, storagedir, dirs_exist_ok=True)

    # Also write a combined results.json if not already present (some solvers may not produce it)
    results_path = os.path.join(storagedir, "results.json")
    if not os.path.exists(results_path):
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

    # Return relative path for storage
    return os.path.relpath(storagedir, STORAGE_BASE)

@celery_app.task(bind=True, max_retries=3)
def run_simulation_task(self, simulation_id: str):
    """
    Celery task that orchestrates a full simulation:
    1. Load simulation parameters from DB.
    2. For each solver specified (could be multiple), run the adapter.
    3. Store results and update DB.
    """
    logger.info(f"Starting workflow for simulation {simulation_id}")
    db: Session = get_db_session()
    try:
        sim_repo = SimulationRepository(db)
        solver_repo = SolverExecutionRepository(db)

        simulation = sim_repo.get(uuid.UUID(simulation_id))
        if not simulation:
            logger.error(f"Simulation {simulation_id} not found")
            return {"error": "Simulation not found"}

        # Update status to running
        sim_repo.update_status(simulation.id, "running")
        db.commit()

        # Determine which solvers to run from parameters
        params = simulation.parameters or {}
        solvers_to_run = params.get("solvers", ["openfoam"])  # default

        for solver_name in solvers_to_run:
            logger.info(f"Running solver {solver_name} for sim {simulation.id}")
            # Create solver execution record
            exec_record = solver_repo.create(
                simulation_id=simulation.id,
                solver_name=solver_name,
                version="1.0",
                parameters=params.get(f"{solver_name}_params", {}),
            )
            db.commit()

            try:
                # Prepare input files
                workdir = _prepare_solver_input(solver_name, params.get(f"{solver_name}_params", {}))
                # Run solver container
                returncode, stdout, stderr = _run_solver_container(solver_name, workdir)
                logs = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"

                if returncode != 0:
                    logger.error(f"Solver {solver_name} failed for sim {simulation.id} with code {returncode}")
                    solver_repo.update_status(
                        exec_record.id,
                        status="failed",
                        ended_at=datetime.utcnow(),
                        logs=logs,
                    )
                    db.commit()
                    # Mark simulation as failed and break
                    sim_repo.update_status(simulation.id, "failed")
                    db.commit()
                    raise Exception(f"Solver {solver_name} failed with return code {returncode}")

                # If successful, we expect results.json in workdir (or storage after copy)
                # For simplicity, we'll read results.json from workdir (before copying)
                results_path = os.path.join(workdir, "results.json")
                if os.path.exists(results_path):
                    with open(results_path, "r") as f:
                        results = json.load(f)
                else:
                    results = {"status": "completed", "message": f"Solver {solver_name} produced no results.json"}

                # Store output (copy workdir to storage)
                storage_rel_path = _store_solver_output(solver_name, workdir, results)
                # Update execution record with success
                solver_repo.update_status(
                    exec_record.id,
                    status="success",
                    ended_at=datetime.utcnow(),
                    logs=logs,
                    result_path=storage_rel_path,
                )
                db.commit()
                # Accumulate results into simulation.results
                current_results = simulation.results or {}
                if isinstance(current_results, str):
                    try:
                        current_results = json.loads(current_results)
                    except Exception:
                        current_results = {}
                current_results[solver_name] = results
                sim_repo.add_results(simulation.id, current_results)
                db.commit()
            except Exception as exc:
                logger.exception(f"Solver {solver_name} failed for sim {simulation.id}")
                # Ensure execution record is marked failed
                try:
                    solver_repo.update_status(
                        exec_record.id,
                        status="failed",
                        ended_at=datetime.utcnow(),
                        logs=str(exc),
                    )
                    db.commit()
                except Exception:
                    pass
                # Mark simulation as failed
                sim_repo.update_status(simulation.id, "failed")
                db.commit()
                raise self.retry(exc=exc, countdown=60, max_retries=3)

        # Finalize simulation as completed
        sim_repo.update_status(simulation.id, "completed")
        db.commit()
        logger.info(f"Workflow completed for simulation {simulation.id}")
        return {"status": "completed", "simulation_id": str(simulation.id)}
    finally:
        db.close()
