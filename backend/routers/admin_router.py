"""
Admin Router — Dashboard analytics and reporting endpoints.
"""

from fastapi import APIRouter, Depends

from backend.database import get_db, execute_query
from backend.models import OverallStats, DepartmentSummary, ServiceRanking
from backend.auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


@router.get("/stats", response_model=OverallStats)
def overall_stats(conn=Depends(get_db), current_user: dict = Depends(require_role("officer", "admin"))):
    """Get overall system statistics."""
    row = execute_query(
        conn,
        """SELECT
               COUNT(*)                                                    AS total_applications,
               SUM(CASE WHEN status = 'Approved'     THEN 1 ELSE 0 END)  AS approved,
               SUM(CASE WHEN status = 'Rejected'     THEN 1 ELSE 0 END)  AS rejected,
               SUM(CASE WHEN status = 'Submitted'    THEN 1 ELSE 0 END)  AS pending,
               SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END)  AS under_review,
               ROUND(AVG(TIMESTAMPDIFF(DAY, submitted_at, COALESCE(completed_at, NOW()))), 1) AS avg_processing_days
           FROM applications""",
        fetch="one",
    )
    return row


@router.get("/department-summary")
def department_summary(conn=Depends(get_db), current_user: dict = Depends(require_role("officer", "admin"))):
    """Get department-wise application breakdown."""
    return execute_query(conn, "SELECT * FROM vw_department_summary")


@router.get("/service-ranking")
def service_ranking(conn=Depends(get_db), current_user: dict = Depends(require_role("officer", "admin"))):
    """Get service popularity ranking."""
    return execute_query(conn, "SELECT * FROM vw_service_ranking")


@router.get("/monthly-trend")
def monthly_trend(conn=Depends(get_db), current_user: dict = Depends(require_role("officer", "admin"))):
    """Get monthly application trend."""
    return execute_query(
        conn,
        """SELECT DATE_FORMAT(submitted_at, '%%Y-%%m') AS month,
                  COUNT(*) AS applications_count
           FROM applications
           GROUP BY DATE_FORMAT(submitted_at, '%%Y-%%m')
           ORDER BY month""",
    )


@router.get("/status-distribution")
def status_distribution(conn=Depends(get_db), current_user: dict = Depends(require_role("officer", "admin"))):
    """Get application status distribution."""
    return execute_query(
        conn,
        "SELECT status, COUNT(*) AS count FROM applications GROUP BY status ORDER BY count DESC",
    )


@router.get("/recent-applications")
def recent_applications(
    limit: int = 20,
    conn=Depends(get_db),
    current_user: dict = Depends(require_role("officer", "admin")),
):
    """Get most recent applications."""
    return execute_query(
        conn,
        """SELECT a.application_ref, a.status, a.submitted_at,
                  u.full_name AS citizen_name, s.name AS service_name,
                  d.name AS department_name
           FROM applications a
               INNER JOIN users u    ON a.citizen_id = u.user_id
               INNER JOIN services s ON a.service_id = s.service_id
               INNER JOIN departments d ON s.department_id = d.department_id
           ORDER BY a.submitted_at DESC
           LIMIT %s""",
        (limit,),
    )


@router.get("/officer-performance")
def officer_performance(conn=Depends(get_db), current_user: dict = Depends(require_role("admin"))):
    """Get officer performance metrics — applications processed."""
    return execute_query(
        conn,
        """SELECT
               ou.full_name AS officer_name,
               o.designation,
               d.name AS department_name,
               COUNT(a.application_id) AS total_processed,
               SUM(CASE WHEN a.status = 'Approved' THEN 1 ELSE 0 END) AS approved,
               SUM(CASE WHEN a.status = 'Rejected' THEN 1 ELSE 0 END) AS rejected,
               ROUND(AVG(TIMESTAMPDIFF(DAY, a.submitted_at, a.completed_at)), 1) AS avg_processing_days
           FROM officers o
               INNER JOIN users ou    ON o.user_id = ou.user_id
               INNER JOIN departments d ON o.department_id = d.department_id
               LEFT  JOIN applications a ON o.officer_id = a.officer_id
           GROUP BY o.officer_id, ou.full_name, o.designation, d.name
           ORDER BY total_processed DESC""",
    )
