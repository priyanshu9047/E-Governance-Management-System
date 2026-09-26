"""
Services Router — Browse available government services.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db, execute_query
from backend.models import ServiceResponse, ServiceRequirementResponse

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/", response_model=List[ServiceResponse])
def list_services(category: str = None, department_id: int = None, conn=Depends(get_db)):
    """List all active services with optional filtering."""
    query = """
        SELECT s.*, d.name AS department_name
        FROM services s
            INNER JOIN departments d ON s.department_id = d.department_id
        WHERE s.is_active = TRUE
    """
    params = []

    if category:
        query += " AND s.category = %s"
        params.append(category)
    if department_id:
        query += " AND s.department_id = %s"
        params.append(department_id)

    query += " ORDER BY d.name, s.name"
    return execute_query(conn, query, tuple(params))


@router.get("/categories")
def list_categories(conn=Depends(get_db)):
    """List all unique service categories."""
    rows = execute_query(
        conn,
        "SELECT DISTINCT category FROM services WHERE is_active = TRUE ORDER BY category",
    )
    return [r["category"] for r in rows]


@router.get("/departments")
def list_departments(conn=Depends(get_db)):
    """List all active departments."""
    return execute_query(
        conn,
        "SELECT department_id, name, description, contact_email, contact_phone FROM departments WHERE is_active = TRUE ORDER BY name",
    )


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, conn=Depends(get_db)):
    """Get details of a specific service."""
    svc = execute_query(
        conn,
        """SELECT s.*, d.name AS department_name
           FROM services s
               INNER JOIN departments d ON s.department_id = d.department_id
           WHERE s.service_id = %s""",
        (service_id,),
        fetch="one",
    )
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc


@router.get("/{service_id}/requirements", response_model=List[ServiceRequirementResponse])
def get_requirements(service_id: int, conn=Depends(get_db)):
    """Get document requirements for a service."""
    return execute_query(
        conn,
        "SELECT * FROM service_requirements WHERE service_id = %s ORDER BY is_mandatory DESC",
        (service_id,),
    )
