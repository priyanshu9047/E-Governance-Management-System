"""
Notifications Router — In-app notifications.
"""

from typing import List
from fastapi import APIRouter, Depends

from backend.database import get_db, execute_query
from backend.models import NotificationResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
def my_notifications(conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get all notifications for the current user."""
    return execute_query(
        conn,
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
        (current_user["user_id"],),
    )


@router.get("/unread/count")
def unread_count(conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get count of unread notifications."""
    row = execute_query(
        conn,
        "SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND is_read = FALSE",
        (current_user["user_id"],),
        fetch="one",
    )
    return {"unread_count": row["count"]}


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark a notification as read."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = TRUE WHERE notification_id = %s AND user_id = %s",
        (notification_id, current_user["user_id"]),
    )
    conn.commit()
    cursor.close()
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_read(conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE",
        (current_user["user_id"],),
    )
    conn.commit()
    cursor.close()
    return {"message": "All notifications marked as read"}
