"""
Documents Router — Upload and manage application documents.
"""

import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from backend.database import get_db, execute_query
from backend.auth import get_current_user
from config import UPLOAD_DIR

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    application_id: int = Form(...),
    document_name: str = Form(...),
    file: UploadFile = File(...),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload a document for an application."""
    # Verify the application belongs to this citizen
    app = execute_query(
        conn,
        "SELECT application_id, citizen_id FROM applications WHERE application_id = %s",
        (application_id,),
        fetch="one",
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["citizen_id"] != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not your application")

    # Validate file type
    allowed = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    # Save file
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    content = await file.read()
    file_size_kb = len(content) // 1024

    with open(file_path, "wb") as f:
        f.write(content)

    # Insert record
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO documents (application_id, document_name, file_path, file_type, file_size_kb)
           VALUES (%s, %s, %s, %s, %s)""",
        (application_id, document_name, unique_name, ext.lstrip("."), file_size_kb),
    )
    conn.commit()
    doc_id = cursor.lastrowid
    cursor.close()

    return {
        "document_id": doc_id,
        "document_name": document_name,
        "file_name": unique_name,
        "file_size_kb": file_size_kb,
        "message": "Document uploaded successfully",
    }


@router.get("/application/{application_id}")
def list_documents(
    application_id: int,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all documents for an application."""
    return execute_query(
        conn,
        "SELECT * FROM documents WHERE application_id = %s ORDER BY uploaded_at",
        (application_id,),
    )
