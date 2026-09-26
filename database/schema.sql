-- =============================================================================
-- E-Governance Service Management System
-- Database Schema (DDL)
-- =============================================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS e_governance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE e_governance;

-- =============================================================================
-- TABLE 1: users
-- Stores both citizens and officers. Differentiated by the 'role' column.
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(150)    NOT NULL,
    email           VARCHAR(200)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    phone           VARCHAR(15),
    address         TEXT,
    date_of_birth   DATE,
    aadhaar_number  VARCHAR(12)     UNIQUE,                -- Unique ID (like SSN)
    role            ENUM('citizen', 'officer', 'admin') NOT NULL DEFAULT 'citizen',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
);

-- =============================================================================
-- TABLE 2: departments
-- Government departments that offer services.
-- =============================================================================
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL UNIQUE,
    description     TEXT,
    head_name       VARCHAR(150),
    contact_email   VARCHAR(200),
    contact_phone   VARCHAR(15),
    address         TEXT,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABLE 3: officers
-- Officers assigned to departments who process applications.
-- =============================================================================
CREATE TABLE IF NOT EXISTS officers (
    officer_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    department_id   INT             NOT NULL,
    designation     VARCHAR(150)    NOT NULL,
    employee_code   VARCHAR(20)     NOT NULL UNIQUE,
    date_of_joining DATE,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,

    FOREIGN KEY (user_id)       REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,

    INDEX idx_officers_department (department_id),
    INDEX idx_officers_user (user_id)
);

-- =============================================================================
-- TABLE 4: services
-- Government services that citizens can apply for.
-- =============================================================================
CREATE TABLE IF NOT EXISTS services (
    service_id      INT AUTO_INCREMENT PRIMARY KEY,
    department_id   INT             NOT NULL,
    name            VARCHAR(200)    NOT NULL,
    description     TEXT,
    category        VARCHAR(100),
    fee             DECIMAL(10, 2)  NOT NULL DEFAULT 0.00,
    processing_days INT             NOT NULL DEFAULT 7,      -- Expected processing time
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE,

    INDEX idx_services_department (department_id),
    INDEX idx_services_category (category)
);

-- =============================================================================
-- TABLE 5: service_requirements
-- Documents required for each service (normalized M:N).
-- =============================================================================
CREATE TABLE IF NOT EXISTS service_requirements (
    requirement_id  INT AUTO_INCREMENT PRIMARY KEY,
    service_id      INT             NOT NULL,
    document_name   VARCHAR(200)    NOT NULL,
    description     VARCHAR(500),
    is_mandatory    BOOLEAN         NOT NULL DEFAULT TRUE,

    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,

    INDEX idx_requirements_service (service_id)
);

-- =============================================================================
-- TABLE 6: applications
-- Core table — every citizen application for a service.
-- =============================================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    application_ref VARCHAR(20)     NOT NULL UNIQUE,        -- Human-readable ref: APP10001
    citizen_id      INT             NOT NULL,
    service_id      INT             NOT NULL,
    officer_id      INT             DEFAULT NULL,            -- Assigned officer
    status          ENUM(
                        'Submitted',
                        'Under Review',
                        'Documents Verified',
                        'Approved',
                        'Rejected',
                        'Returned'
                    ) NOT NULL DEFAULT 'Submitted',
    remarks         TEXT,
    submitted_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP       NULL,

    FOREIGN KEY (citizen_id)  REFERENCES users(user_id)      ON DELETE CASCADE,
    FOREIGN KEY (service_id)  REFERENCES services(service_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id)  REFERENCES officers(officer_id) ON DELETE SET NULL,

    INDEX idx_applications_citizen (citizen_id),
    INDEX idx_applications_service (service_id),
    INDEX idx_applications_status (status),
    INDEX idx_applications_ref (application_ref),
    INDEX idx_applications_officer (officer_id)
);

-- =============================================================================
-- TABLE 7: documents
-- Files uploaded by citizens for their applications.
-- =============================================================================
CREATE TABLE IF NOT EXISTS documents (
    document_id     INT AUTO_INCREMENT PRIMARY KEY,
    application_id  INT             NOT NULL,
    document_name   VARCHAR(200)    NOT NULL,
    file_path       VARCHAR(500)    NOT NULL,
    file_type       VARCHAR(50),
    file_size_kb    INT,
    uploaded_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,

    INDEX idx_documents_application (application_id)
);

-- =============================================================================
-- TABLE 8: payments
-- Payment records for service fees.
-- =============================================================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    application_id  INT             NOT NULL,
    citizen_id      INT             NOT NULL,
    amount          DECIMAL(10, 2)  NOT NULL,
    payment_method  ENUM('UPI', 'Net Banking', 'Debit Card', 'Credit Card', 'Cash')
                        NOT NULL DEFAULT 'UPI',
    transaction_ref VARCHAR(50)     UNIQUE,
    status          ENUM('Pending', 'Completed', 'Failed', 'Refunded')
                        NOT NULL DEFAULT 'Pending',
    paid_at         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (citizen_id)     REFERENCES users(user_id)               ON DELETE CASCADE,

    INDEX idx_payments_application (application_id),
    INDEX idx_payments_citizen (citizen_id),
    INDEX idx_payments_status (status)
);

-- =============================================================================
-- TABLE 9: complaints
-- Citizen complaints about services or applications.
-- =============================================================================
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id    INT AUTO_INCREMENT PRIMARY KEY,
    complaint_ref   VARCHAR(20)     NOT NULL UNIQUE,        -- CMP10001
    citizen_id      INT             NOT NULL,
    application_id  INT             DEFAULT NULL,            -- Optional link
    subject         VARCHAR(300)    NOT NULL,
    description     TEXT            NOT NULL,
    status          ENUM('Open', 'In Progress', 'Resolved', 'Closed')
                        NOT NULL DEFAULT 'Open',
    priority        ENUM('Low', 'Medium', 'High', 'Critical')
                        NOT NULL DEFAULT 'Medium',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP       NULL,

    FOREIGN KEY (citizen_id)     REFERENCES users(user_id)               ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE SET NULL,

    INDEX idx_complaints_citizen (citizen_id),
    INDEX idx_complaints_status (status)
);

-- =============================================================================
-- TABLE 10: notifications
-- In-app notifications for citizens and officers.
-- =============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    title           VARCHAR(300)    NOT NULL,
    message         TEXT            NOT NULL,
    type            ENUM('Info', 'Success', 'Warning', 'Error')
                        NOT NULL DEFAULT 'Info',
    is_read         BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,

    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_read (is_read)
);

-- =============================================================================
-- VIEWS for Reporting
-- =============================================================================

-- View: Application details with citizen and service info (multi-table JOIN)
CREATE OR REPLACE VIEW vw_application_details AS
SELECT
    a.application_id,
    a.application_ref,
    a.status,
    a.remarks,
    a.submitted_at,
    a.updated_at,
    a.completed_at,
    u.user_id       AS citizen_id,
    u.full_name      AS citizen_name,
    u.email          AS citizen_email,
    u.phone          AS citizen_phone,
    s.service_id,
    s.name           AS service_name,
    s.category       AS service_category,
    s.fee            AS service_fee,
    d.department_id,
    d.name           AS department_name,
    o.officer_id,
    ou.full_name     AS officer_name
FROM applications a
    INNER JOIN users u      ON a.citizen_id  = u.user_id
    INNER JOIN services s   ON a.service_id  = s.service_id
    INNER JOIN departments d ON s.department_id = d.department_id
    LEFT  JOIN officers o   ON a.officer_id  = o.officer_id
    LEFT  JOIN users ou     ON o.user_id     = ou.user_id;

-- View: Department-wise application summary (GROUP BY)
CREATE OR REPLACE VIEW vw_department_summary AS
SELECT
    d.department_id,
    d.name                                          AS department_name,
    COUNT(a.application_id)                         AS total_applications,
    SUM(CASE WHEN a.status = 'Approved'  THEN 1 ELSE 0 END) AS approved,
    SUM(CASE WHEN a.status = 'Rejected'  THEN 1 ELSE 0 END) AS rejected,
    SUM(CASE WHEN a.status = 'Submitted' THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN a.status = 'Under Review' THEN 1 ELSE 0 END) AS under_review
FROM departments d
    LEFT JOIN services s     ON d.department_id = s.department_id
    LEFT JOIN applications a ON s.service_id    = a.service_id
GROUP BY d.department_id, d.name;

-- View: Service popularity ranking (Window Function)
CREATE OR REPLACE VIEW vw_service_ranking AS
SELECT
    s.service_id,
    s.name                                        AS service_name,
    d.name                                        AS department_name,
    COUNT(a.application_id)                       AS total_applications,
    RANK() OVER (ORDER BY COUNT(a.application_id) DESC) AS popularity_rank,
    ROW_NUMBER() OVER (ORDER BY COUNT(a.application_id) DESC) AS row_num
FROM services s
    INNER JOIN departments d  ON s.department_id = d.department_id
    LEFT  JOIN applications a ON s.service_id    = a.service_id
GROUP BY s.service_id, s.name, d.name;
