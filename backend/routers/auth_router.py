"""
Auth Router — Registration and Login endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.database import get_db, execute_query
from backend.models import UserRegister, UserLogin, TokenResponse, UserResponse
from backend.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(user: UserRegister, conn=Depends(get_db)):
    """Register a new citizen/officer account."""
    # Check if email already exists
    existing = execute_query(
        conn, "SELECT user_id FROM users WHERE email = %s", (user.email,), fetch="one"
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check aadhaar uniqueness
    if user.aadhaar_number:
        aadhaar_check = execute_query(
            conn,
            "SELECT user_id FROM users WHERE aadhaar_number = %s",
            (user.aadhaar_number,),
            fetch="one",
        )
        if aadhaar_check:
            raise HTTPException(status_code=400, detail="Aadhaar number already registered")

    hashed = hash_password(user.password)

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (full_name, email, password_hash, phone, address,
                           date_of_birth, aadhaar_number, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user.full_name,
            user.email,
            hashed,
            user.phone,
            user.address,
            user.date_of_birth,
            user.aadhaar_number,
            user.role,
        ),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()

    token = create_access_token(
        {"user_id": user_id, "email": user.email, "role": user.role}
    )

    return TokenResponse(
        access_token=token,
        user_id=user_id,
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, conn=Depends(get_db)):
    """Login and receive a JWT token."""
    user = execute_query(
        conn,
        "SELECT user_id, full_name, email, password_hash, role, is_active FROM users WHERE email = %s",
        (credentials.email,),
        fetch="one",
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {"user_id": user["user_id"], "email": user["email"], "role": user["role"]}
    )

    return TokenResponse(
        access_token=token,
        user_id=user["user_id"],
        role=user["role"],
        full_name=user["full_name"],
    )


@router.get("/me", response_model=UserResponse)
def get_me(conn=Depends(get_db), current_user: dict = Depends(__import__("backend.auth", fromlist=["get_current_user"]).get_current_user)):
    """Get the currently authenticated user's profile."""
    user = execute_query(
        conn,
        """SELECT user_id, full_name, email, phone, address,
                  date_of_birth, aadhaar_number, role, is_active, created_at
           FROM users WHERE user_id = %s""",
        (current_user["user_id"],),
        fetch="one",
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
