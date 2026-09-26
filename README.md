# 🏛️ Digital E-Governance Service Management System

A comprehensive digital platform that enables citizens to apply for government services online, track applications in real-time, make payments, and receive notifications — while government officers can process applications, manage complaints, and view analytics.

## 📸 Architecture

```
Citizen / Officer
        ↕
  Streamlit Frontend (UI)
        ↕
  FastAPI Backend (REST API + Pydantic Validation)
        ↕
  MySQL Database (10 Tables + Views + Stored Procedures + Triggers)
```

## ✨ Features

### For Citizens
- 📝 **Register / Login** — Secure JWT-based authentication
- 📋 **Browse Services** — Filter by department and category
- 📄 **Apply Online** — Submit applications with document uploads
- 🔍 **Track Applications** — Real-time status timeline
- 💳 **Online Payments** — Simulated digital payments (UPI, Net Banking, Cards)
- 📢 **Notifications** — Auto-generated alerts on status changes
- 🗣️ **Complaints** — File and track complaints with priority levels

### For Officers / Admin
- 👮 **Officer Dashboard** — View and process pending applications
- ✅ **Approve / Reject** — Update application status with remarks
- 📊 **Analytics** — Interactive charts (Plotly) for reporting
- 🗣️ **Complaint Management** — Track and resolve citizen complaints
- 👥 **Officer Performance** — Processing metrics and leaderboard

## 🗄️ Database Design

### Tables (10)
| Table | Purpose |
|-------|---------|
| `users` | Citizens, officers, and admin accounts |
| `departments` | Government departments |
| `officers` | Officers linked to users and departments |
| `services` | Available government services |
| `service_requirements` | Required documents per service |
| `applications` | Citizen applications with status tracking |
| `documents` | Uploaded documents per application |
| `payments` | Payment records and transaction history |
| `complaints` | Citizen complaints with priority |
| `notifications` | In-app notification system |

### SQL Features Demonstrated
- ✅ **Primary & Foreign Keys** with proper constraints
- ✅ **Normalization** (3NF)
- ✅ **Indexes** for performance optimization
- ✅ **JOINs** — INNER, LEFT, multi-table
- ✅ **GROUP BY** with aggregate functions (COUNT, SUM, AVG)
- ✅ **Views** — `vw_application_details`, `vw_department_summary`, `vw_service_ranking`
- ✅ **Stored Procedures** — `sp_submit_application`, `sp_update_application_status`, `sp_generate_report`, etc.
- ✅ **Functions** — `generate_application_ref()`, `generate_complaint_ref()`
- ✅ **Triggers** — Auto-notifications on status change, payment, and complaint resolution
- ✅ **Window Functions** — RANK, ROW_NUMBER for service popularity ranking
- ✅ **CTEs** — Common Table Expressions for complex queries
- ✅ **EXPLAIN Analysis** — Query optimization with index strategies

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Language | Python 3.11+ |
| Database | MySQL 8.0+ |
| Validation | Pydantic v2 |
| Authentication | JWT (python-jose + bcrypt) |
| Visualization | Plotly, Matplotlib |
| Version Control | Git + GitHub |

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/priyanshu9047/E-Governance-Management-System.git
cd E-Governance-Management-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the schema
source database/schema.sql

# Load seed data
source database/seed_data.sql

# Create stored procedures
source database/stored_procedures.sql

# Create triggers
source database/triggers.sql
```

### 4. Configure Environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your MySQL credentials
```

### 5. Start the Backend
```bash
python -m backend.main
# or
uvicorn backend.main:app --reload --port 8000
```

### 6. Start the Frontend
```bash
streamlit run frontend/app.py
```

### 7. Access the Application
- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Citizen | rahul@example.com | password123 |
| Citizen | priya@example.com | password123 |
| Officer | suresh@gov.in | password123 |
| Officer | neha@gov.in | password123 |
| Admin | admin@gov.in | password123 |

## 📁 Project Structure

```
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config.py                     # Central configuration
│
├── database/
│   ├── schema.sql                # DDL — 10 tables, views, indexes
│   ├── seed_data.sql             # Sample data
│   ├── stored_procedures.sql     # 6 stored procedures/functions
│   ├── triggers.sql              # 3 database triggers
│   └── performance/
│       └── optimization.sql      # EXPLAIN analysis & optimization
│
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── database.py               # MySQL connection pool
│   ├── models.py                 # Pydantic validation models
│   ├── auth.py                   # JWT authentication
│   └── routers/
│       ├── auth_router.py        # Register/Login APIs
│       ├── services_router.py    # Service browsing APIs
│       ├── applications_router.py # Application CRUD APIs
│       ├── documents_router.py   # Document upload APIs
│       ├── payments_router.py    # Payment APIs
│       ├── complaints_router.py  # Complaint APIs
│       ├── notifications_router.py # Notification APIs
│       └── admin_router.py       # Admin analytics APIs
│
├── frontend/
│   ├── app.py                    # Streamlit main (login + dashboard)
│   ├── utils.py                  # API helper functions
│   └── pages/
│       ├── 1_🏠_Home.py           # Landing page
│       ├── 2_📋_Services.py       # Browse services
│       ├── 3_📝_Apply.py          # Submit application
│       ├── 4_🔍_Track_Application.py # Track with timeline
│       ├── 5_💳_Payments.py       # Payment management
│       ├── 6_📢_Notifications.py  # Notification center
│       ├── 7_🗣️_Complaints.py     # Complaint system
│       └── 8_👮_Officer_Dashboard.py # Officer/admin panel
│
├── reports/
│   └── analytics.py              # Matplotlib report generator
│
└── uploads/                      # Document storage
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/services/` | List all services |
| GET | `/api/services/{id}` | Get service details |
| GET | `/api/services/{id}/requirements` | Get required documents |
| POST | `/api/applications/` | Submit application |
| GET | `/api/applications/my` | My applications |
| GET | `/api/applications/track/{ref}` | Track by reference |
| PUT | `/api/applications/{id}/status` | Update status (officer) |
| POST | `/api/documents/upload` | Upload document |
| POST | `/api/payments/` | Make payment |
| GET | `/api/payments/my` | Payment history |
| POST | `/api/complaints/` | Raise complaint |
| GET | `/api/notifications/` | Get notifications |
| GET | `/api/admin/stats` | System analytics |
| GET | `/api/admin/department-summary` | Dept breakdown |
| GET | `/api/admin/service-ranking` | Service popularity |

## 📝 License

This project is for educational/demonstration purposes — SQL Database Project.

## 👤 Author

**Priyanshu** — [GitHub](https://github.com/priyanshu9047)
