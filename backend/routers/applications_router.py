"""
Applications Router — Submit, track, and manage applications.
"""

import random
import string
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.database import get_db, execute_query
from backend.models import ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse
from backend.auth import get_current_user, require_role

router = APIRouter(prefix="/api/applications", tags=["Applications"])


def _generate_ref(conn) -> str:
    """Generate a unique application reference."""
    row = execute_query(
        conn, "SELECT COALESCE(MAX(application_id), 0) + 1 AS next_id FROM applications", fetch="one"
    )
    next_id = row["next_id"]
    return f"APP{10000 + next_id}"


# ── Citizen Endpoints ──────────────────────────────────────────────────────────

@router.post("/", response_model=ApplicationResponse, status_code=201)
def submit_application(
    app: ApplicationCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submit a new application (citizen only)."""
    if current_user["role"] not in ("citizen", "admin"):
        raise HTTPException(status_code=403, detail="Only citizens can submit applications")

    # Validate service
    svc = execute_query(
        conn, "SELECT service_id FROM services WHERE service_id = %s AND is_active = TRUE",
        (app.service_id,), fetch="one"
    )
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found or inactive")

    ref = _generate_ref(conn)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO applications (application_ref, citizen_id, service_id, status)
           VALUES (%s, %s, %s, 'Submitted')""",
        (ref, current_user["user_id"], app.service_id),
    )
    conn.commit()
    app_id = cursor.lastrowid
    cursor.close()

    return execute_query(
        conn,
        """SELECT a.*, u.full_name AS citizen_name, s.name AS service_name,
                  d.name AS department_name
           FROM applications a
               INNER JOIN users u ON a.citizen_id = u.user_id
               INNER JOIN services s ON a.service_id = s.service_id
               INNER JOIN departments d ON s.department_id = d.department_id
           WHERE a.application_id = %s""",
        (app_id,),
        fetch="one",
    )


@router.get("/my", response_model=List[ApplicationResponse])
def my_applications(
    status: Optional[str] = None,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all applications of the current citizen."""
    query = """
        SELECT a.*, u.full_name AS citizen_name, s.name AS service_name,
               d.name AS department_name, ou.full_name AS officer_name
        FROM applications a
            INNER JOIN users u    ON a.citizen_id = u.user_id
            INNER JOIN services s ON a.service_id = s.service_id
            INNER JOIN departments d ON s.department_id = d.department_id
            LEFT  JOIN officers o  ON a.officer_id = o.officer_id
            LEFT  JOIN users ou    ON o.user_id = ou.user_id
        WHERE a.citizen_id = %s
    """
    params = [current_user["user_id"]]

    if status:
        query += " AND a.status = %s"
        params.append(status)

    query += " ORDER BY a.submitted_at DESC"
    return execute_query(conn, query, tuple(params))


@router.get("/track/{application_ref}")
def track_application(application_ref: str, conn=Depends(get_db)):
    """Track an application by its reference number (public)."""
    app = execute_query(
        conn,
        """SELECT a.application_ref, a.status, a.remarks, a.submitted_at, a.updated_at,
                  a.completed_at, s.name AS service_name, d.name AS department_name
           FROM applications a
               INNER JOIN services s ON a.service_id = s.service_id
               INNER JOIN departments d ON s.department_id = d.department_id
           WHERE a.application_ref = %s""",
        (application_ref,),
        fetch="one",
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Build timeline
    statuses = ['Submitted', 'Under Review', 'Documents Verified', 'Approved']
    current = app["status"]
    timeline = []
    for s in statuses:
        timeline.append({"step": s, "completed": statuses.index(s) <= statuses.index(current) if current in statuses else s == current})

    app["timeline"] = timeline
    return app


# ── Officer / Admin Endpoints ─────────────────────────────────────────────────

@router.get("/pending", response_model=List[ApplicationResponse])
def pending_applications(
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("officer", "admin")),
):
    """List all pending applications for officers."""
    # Get officer's department
    officer = execute_query(
        conn,
        "SELECT officer_id, department_id FROM officers WHERE user_id = %s",
        (current_user["user_id"],),
        fetch="one",
    )

    query = """
        SELECT a.*, u.full_name AS citizen_name, s.name AS service_name,
               d.name AS department_name, ou.full_name AS officer_name
        FROM applications a
            INNER JOIN users u    ON a.citizen_id = u.user_id
            INNER JOIN services s ON a.service_id = s.service_id
            INNER JOIN departments d ON s.department_id = d.department_id
            LEFT  JOIN officers o  ON a.officer_id = o.officer_id
            LEFT  JOIN users ou    ON o.user_id = ou.user_id
        WHERE a.status NOT IN ('Approved', 'Rejected')
    """
    params = []

    # Officers see only their department; admins see all
    if officer and current_user["role"] == "officer":
        query += " AND s.department_id = %s"
        params.append(officer["department_id"])

    query += " ORDER BY a.submitted_at ASC"
    return execute_query(conn, query, tuple(params))


@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_status(
    application_id: int,
    update: ApplicationStatusUpdate,
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("officer", "admin")),
):
    """Update application status (officer/admin only)."""
    # Get officer_id
    officer = execute_query(
        conn,
        "SELECT officer_id FROM officers WHERE user_id = %s",
        (current_user["user_id"],),
        fetch="one",
    )
    officer_id = officer["officer_id"] if officer else None

    # Check application exists
    app = execute_query(
        conn, "SELECT * FROM applications WHERE application_id = %s", (application_id,), fetch="one"
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app["status"] in ("Approved", "Rejected"):
        raise HTTPException(status_code=400, detail=f"Application already {app['status']}")

    cursor = conn.cursor()
    cursor.execute(
        """UPDATE applications
           SET status = %s, officer_id = %s, remarks = %s,
               completed_at = CASE WHEN %s IN ('Approved', 'Rejected') THEN NOW() ELSE NULL END
           WHERE application_id = %s""",
        (update.status, officer_id, update.remarks, update.status, application_id),
    )
    conn.commit()
    cursor.close()

    return execute_query(
        conn,
        """SELECT a.*, u.full_name AS citizen_name, s.name AS service_name,
                  d.name AS department_name, ou.full_name AS officer_name
           FROM applications a
               INNER JOIN users u    ON a.citizen_id = u.user_id
               INNER JOIN services s ON a.service_id = s.service_id
               INNER JOIN departments d ON s.department_id = d.department_id
               LEFT  JOIN officers o  ON a.officer_id = o.officer_id
               LEFT  JOIN users ou    ON o.user_id = ou.user_id
           WHERE a.application_id = %s""",
        (application_id,),
        fetch="one",
    )


@router.get("/all", response_model=List[ApplicationResponse])
def all_applications(
    status: Optional[str] = None,
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    """List all applications (admin only)."""
    query = """
        SELECT a.*, u.full_name AS citizen_name, s.name AS service_name,
               d.name AS department_name, ou.full_name AS officer_name
        FROM applications a
            INNER JOIN users u    ON a.citizen_id = u.user_id
            INNER JOIN services s ON a.service_id = s.service_id
            INNER JOIN departments d ON s.department_id = d.department_id
            LEFT  JOIN officers o  ON a.officer_id = o.officer_id
            LEFT  JOIN users ou    ON o.user_id = ou.user_id
    """
    params = []
    if status:
        query += " WHERE a.status = %s"
        params.append(status)
    query += " ORDER BY a.submitted_at DESC"
    return execute_query(conn, query, tuple(params))
