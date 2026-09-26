"""
Complaints Router — Raise and manage complaints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db, execute_query
from backend.models import ComplaintCreate, ComplaintStatusUpdate, ComplaintResponse
from backend.auth import get_current_user, require_role

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])


def _generate_complaint_ref(conn) -> str:
    row = execute_query(
        conn, "SELECT COALESCE(MAX(complaint_id), 0) + 1 AS next_id FROM complaints", fetch="one"
    )
    return f"CMP{10000 + row['next_id']}"


@router.post("/", response_model=ComplaintResponse, status_code=201)
def raise_complaint(
    complaint: ComplaintCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Raise a new complaint."""
    ref = _generate_complaint_ref(conn)

    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO complaints (complaint_ref, citizen_id, application_id, subject, description, status, priority)
           VALUES (%s, %s, %s, %s, %s, 'Open', %s)""",
        (ref, current_user["user_id"], complaint.application_id, complaint.subject, complaint.description, complaint.priority),
    )
    conn.commit()
    cid = cursor.lastrowid
    cursor.close()

    return execute_query(conn, "SELECT * FROM complaints WHERE complaint_id = %s", (cid,), fetch="one")


@router.get("/my", response_model=List[ComplaintResponse])
def my_complaints(conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """List current citizen's complaints."""
    return execute_query(
        conn,
        "SELECT * FROM complaints WHERE citizen_id = %s ORDER BY created_at DESC",
        (current_user["user_id"],),
    )


@router.get("/all", response_model=List[ComplaintResponse])
def all_complaints(
    status: str = None,
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("officer", "admin")),
):
    """List all complaints (officer/admin)."""
    query = "SELECT * FROM complaints"
    params = []
    if status:
        query += " WHERE status = %s"
        params.append(status)
    query += " ORDER BY FIELD(priority, 'Critical', 'High', 'Medium', 'Low'), created_at ASC"
    return execute_query(conn, query, tuple(params))


@router.put("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    update: ComplaintStatusUpdate,
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("officer", "admin")),
):
    """Update complaint status (officer/admin only)."""
    existing = execute_query(
        conn, "SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,), fetch="one"
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Complaint not found")

    cursor = conn.cursor()
    resolved_sql = ", resolved_at = NOW()" if update.status in ("Resolved", "Closed") else ""
    cursor.execute(
        f"UPDATE complaints SET status = %s{resolved_sql} WHERE complaint_id = %s",
        (update.status, complaint_id),
    )
    conn.commit()
    cursor.close()

    return execute_query(
        conn, "SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,), fetch="one"
    )
