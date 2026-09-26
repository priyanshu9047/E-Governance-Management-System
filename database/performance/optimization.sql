-- =============================================================================
-- E-Governance Service Management System
-- Performance Optimization & Analysis
-- =============================================================================

USE e_governance;

-- =============================================================================
-- 1. EXPLAIN ANALYSIS — Before Indexing
-- =============================================================================

-- Query 1: Find all applications for a specific citizen
-- Without index on citizen_id, this would do a full table scan
EXPLAIN SELECT * FROM applications WHERE citizen_id = 1;

-- Query 2: Search applications by status
EXPLAIN SELECT * FROM applications WHERE status = 'Submitted';

-- Query 3: Multi-table JOIN query
EXPLAIN
SELECT a.application_ref, u.full_name, s.name, a.status
FROM applications a
    INNER JOIN users u    ON a.citizen_id = u.user_id
    INNER JOIN services s ON a.service_id = s.service_id
WHERE a.status = 'Submitted';

-- Query 4: Aggregation query for reporting
EXPLAIN
SELECT
    s.name,
    COUNT(*) AS total,
    SUM(CASE WHEN a.status = 'Approved' THEN 1 ELSE 0 END) AS approved
FROM services s
    LEFT JOIN applications a ON s.service_id = a.service_id
GROUP BY s.name;

-- =============================================================================
-- 2. INDEX STRATEGY
-- =============================================================================
-- The schema already includes indexes on frequently queried columns:
--
-- TABLE: users
--   - idx_users_email(email)         → Login lookups
--   - idx_users_role(role)           → Role-based filtering
--
-- TABLE: applications
--   - idx_applications_citizen(citizen_id)   → Citizen's application list
--   - idx_applications_service(service_id)   → Service-wise queries
--   - idx_applications_status(status)        → Status filtering
--   - idx_applications_ref(application_ref)  → Lookup by reference
--   - idx_applications_officer(officer_id)   → Officer's pending queue
--
-- TABLE: payments
--   - idx_payments_application(application_id)
--   - idx_payments_citizen(citizen_id)
--   - idx_payments_status(status)
--
-- Additional composite indexes for common query patterns:

-- Composite index for officer dashboard: filter by officer + status
CREATE INDEX IF NOT EXISTS idx_app_officer_status
ON applications (officer_id, status);

-- Composite index for date-range reports
CREATE INDEX IF NOT EXISTS idx_app_submitted_at
ON applications (submitted_at);

-- Composite index for notifications: user + read status (unread first)
CREATE INDEX IF NOT EXISTS idx_notif_user_read
ON notifications (user_id, is_read);

-- =============================================================================
-- 3. QUERY OPTIMIZATION EXAMPLES
-- =============================================================================

-- ─── Before Optimization ─────────────────────────────────────────────────────
-- Subquery approach (potentially slower for large datasets)
SELECT *
FROM applications
WHERE citizen_id IN (
    SELECT user_id FROM users WHERE email LIKE '%example.com'
);

-- ─── After Optimization ──────────────────────────────────────────────────────
-- JOIN approach (generally faster, allows index usage)
SELECT a.*
FROM applications a
    INNER JOIN users u ON a.citizen_id = u.user_id
WHERE u.email LIKE '%example.com';

-- ─── CTE for readability + performance ───────────────────────────────────────
-- Complex reporting query using CTE instead of nested subqueries
WITH service_stats AS (
    SELECT
        service_id,
        COUNT(*)                                                    AS total_apps,
        AVG(TIMESTAMPDIFF(DAY, submitted_at, COALESCE(completed_at, NOW()))) AS avg_days
    FROM applications
    GROUP BY service_id
),
top_services AS (
    SELECT
        s.name,
        ss.total_apps,
        ROUND(ss.avg_days, 1) AS avg_processing_days,
        RANK() OVER (ORDER BY ss.total_apps DESC) AS ranking
    FROM service_stats ss
        INNER JOIN services s ON ss.service_id = s.service_id
)
SELECT * FROM top_services WHERE ranking <= 5;

-- =============================================================================
-- 4. VERIFY OPTIMIZATION — After Indexing
-- =============================================================================

-- Re-run EXPLAIN to verify index usage
EXPLAIN SELECT * FROM applications WHERE citizen_id = 1;
-- Expected: type = ref, key = idx_applications_citizen

EXPLAIN SELECT * FROM applications WHERE officer_id = 1 AND status = 'Submitted';
-- Expected: type = ref, key = idx_app_officer_status

EXPLAIN SELECT * FROM notifications WHERE user_id = 1 AND is_read = FALSE;
-- Expected: type = ref, key = idx_notif_user_read
