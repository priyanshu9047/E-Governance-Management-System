"""
Payments Router — Payment processing simulation.
"""

import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db, execute_query
from backend.models import PaymentCreate, PaymentResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
def make_payment(
    payment: PaymentCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Process a payment for an application."""
    # Verify application
    app = execute_query(
        conn,
        """SELECT a.application_id, a.citizen_id, s.fee
           FROM applications a
               INNER JOIN services s ON a.service_id = s.service_id
           WHERE a.application_id = %s""",
        (payment.application_id,),
        fetch="one",
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["citizen_id"] != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not your application")

    # Check if already paid
    existing = execute_query(
        conn,
        "SELECT payment_id FROM payments WHERE application_id = %s AND status = 'Completed'",
        (payment.application_id,),
        fetch="one",
    )
    if existing:
        raise HTTPException(status_code=400, detail="Payment already completed")

    # Generate transaction reference
    txn_ref = f"TXN{random.randint(100000000, 999999999)}"

    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO payments (application_id, citizen_id, amount, payment_method, transaction_ref, status)
           VALUES (%s, %s, %s, %s, %s, 'Completed')""",
        (payment.application_id, current_user["user_id"], app["fee"], payment.payment_method, txn_ref),
    )
    conn.commit()
    pay_id = cursor.lastrowid
    cursor.close()

    return execute_query(
        conn, "SELECT * FROM payments WHERE payment_id = %s", (pay_id,), fetch="one"
    )


@router.get("/my", response_model=List[PaymentResponse])
def my_payments(conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """List all payments of the current citizen."""
    return execute_query(
        conn,
        "SELECT * FROM payments WHERE citizen_id = %s ORDER BY paid_at DESC",
        (current_user["user_id"],),
    )


@router.get("/application/{application_id}", response_model=List[PaymentResponse])
def application_payments(
    application_id: int,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get payment records for a specific application."""
    return execute_query(
        conn,
        "SELECT * FROM payments WHERE application_id = %s",
        (application_id,),
    )
