-- =============================================================================
-- E-Governance Service Management System
-- Stored Procedures & Functions
-- =============================================================================

USE e_governance;

DELIMITER //

-- ─────────────────────────────────────────────────────────────────────────────
-- FUNCTION: generate_application_ref
-- Generates the next application reference number (APP10001, APP10002, …)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE FUNCTION IF NOT EXISTS generate_application_ref()
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE next_id INT;
    SELECT COALESCE(MAX(application_id), 0) + 1 INTO next_id FROM applications;
    RETURN CONCAT('APP', LPAD(10000 + next_id, 5, '0'));
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- FUNCTION: generate_complaint_ref
-- Generates the next complaint reference number (CMP10001, CMP10002, …)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE FUNCTION IF NOT EXISTS generate_complaint_ref()
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE next_id INT;
    SELECT COALESCE(MAX(complaint_id), 0) + 1 INTO next_id FROM complaints;
    RETURN CONCAT('CMP', LPAD(10000 + next_id, 5, '0'));
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDURE: sp_submit_application
-- Submits a new application for a citizen.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE PROCEDURE IF NOT EXISTS sp_submit_application(
    IN p_citizen_id INT,
    IN p_service_id INT,
    OUT p_application_ref VARCHAR(20),
    OUT p_result_message VARCHAR(255)
)
BEGIN
    DECLARE v_service_exists INT DEFAULT 0;
    DECLARE v_citizen_exists INT DEFAULT 0;
    DECLARE v_ref VARCHAR(20);

    -- Validate citizen
    SELECT COUNT(*) INTO v_citizen_exists
    FROM users WHERE user_id = p_citizen_id AND role = 'citizen' AND is_active = TRUE;

    IF v_citizen_exists = 0 THEN
        SET p_application_ref = NULL;
        SET p_result_message = 'ERROR: Invalid or inactive citizen.';
    ELSE
        -- Validate service
        SELECT COUNT(*) INTO v_service_exists
        FROM services WHERE service_id = p_service_id AND is_active = TRUE;

        IF v_service_exists = 0 THEN
            SET p_application_ref = NULL;
            SET p_result_message = 'ERROR: Invalid or inactive service.';
        ELSE
            SET v_ref = generate_application_ref();

            INSERT INTO applications (application_ref, citizen_id, service_id, status)
            VALUES (v_ref, p_citizen_id, p_service_id, 'Submitted');

            SET p_application_ref = v_ref;
            SET p_result_message = CONCAT('Application ', v_ref, ' submitted successfully.');
        END IF;
    END IF;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDURE: sp_update_application_status
-- Officers update application status. Validates transitions.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE PROCEDURE IF NOT EXISTS sp_update_application_status(
    IN p_application_id INT,
    IN p_officer_id INT,
    IN p_new_status VARCHAR(30),
    IN p_remarks TEXT,
    OUT p_result_message VARCHAR(255)
)
BEGIN
    DECLARE v_current_status VARCHAR(30);
    DECLARE v_app_exists INT DEFAULT 0;

    SELECT COUNT(*), status INTO v_app_exists, v_current_status
    FROM applications
    WHERE application_id = p_application_id
    GROUP BY status;

    IF v_app_exists = 0 THEN
        SET p_result_message = 'ERROR: Application not found.';
    ELSEIF v_current_status IN ('Approved', 'Rejected') THEN
        SET p_result_message = CONCAT('ERROR: Application already ', v_current_status, '. Cannot modify.');
    ELSE
        UPDATE applications
        SET status     = p_new_status,
            officer_id = p_officer_id,
            remarks    = p_remarks,
            completed_at = CASE
                WHEN p_new_status IN ('Approved', 'Rejected') THEN NOW()
                ELSE NULL
            END
        WHERE application_id = p_application_id;

        SET p_result_message = CONCAT('Application updated to ', p_new_status, '.');
    END IF;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDURE: sp_get_citizen_dashboard
-- Returns summary stats for a citizen.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE PROCEDURE IF NOT EXISTS sp_get_citizen_dashboard(
    IN p_citizen_id INT
)
BEGIN
    -- Summary counts
    SELECT
        COUNT(*)                                                    AS total_applications,
        SUM(CASE WHEN status = 'Submitted'    THEN 1 ELSE 0 END)  AS submitted,
        SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END)  AS under_review,
        SUM(CASE WHEN status = 'Approved'     THEN 1 ELSE 0 END)  AS approved,
        SUM(CASE WHEN status = 'Rejected'     THEN 1 ELSE 0 END)  AS rejected
    FROM applications
    WHERE citizen_id = p_citizen_id;

    -- Recent applications
    SELECT
        a.application_ref,
        s.name AS service_name,
        a.status,
        a.submitted_at,
        a.updated_at
    FROM applications a
        INNER JOIN services s ON a.service_id = s.service_id
    WHERE a.citizen_id = p_citizen_id
    ORDER BY a.submitted_at DESC
    LIMIT 10;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDURE: sp_generate_report
-- Generates overall system report with analytics.
-- Uses CTEs and aggregate functions.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE PROCEDURE IF NOT EXISTS sp_generate_report()
BEGIN
    -- 1. Overall statistics
    SELECT
        COUNT(*)                                                    AS total_applications,
        SUM(CASE WHEN status = 'Approved'     THEN 1 ELSE 0 END)  AS approved,
        SUM(CASE WHEN status = 'Rejected'     THEN 1 ELSE 0 END)  AS rejected,
        SUM(CASE WHEN status = 'Submitted'    THEN 1 ELSE 0 END)  AS pending,
        SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END)  AS under_review,
        ROUND(AVG(TIMESTAMPDIFF(DAY, submitted_at, COALESCE(completed_at, NOW()))), 1) AS avg_processing_days
    FROM applications;

    -- 2. Department-wise breakdown
    SELECT * FROM vw_department_summary;

    -- 3. Service popularity ranking
    SELECT * FROM vw_service_ranking;

    -- 4. Monthly trend (CTE usage)
    WITH monthly_apps AS (
        SELECT
            DATE_FORMAT(submitted_at, '%Y-%m') AS month,
            COUNT(*) AS applications_count
        FROM applications
        GROUP BY DATE_FORMAT(submitted_at, '%Y-%m')
    )
    SELECT * FROM monthly_apps ORDER BY month;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- PROCEDURE: sp_process_payment
-- Simulates payment processing for an application.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE PROCEDURE IF NOT EXISTS sp_process_payment(
    IN p_application_id INT,
    IN p_citizen_id INT,
    IN p_payment_method VARCHAR(20),
    OUT p_transaction_ref VARCHAR(50),
    OUT p_result_message VARCHAR(255)
)
BEGIN
    DECLARE v_fee DECIMAL(10, 2);
    DECLARE v_already_paid INT DEFAULT 0;
    DECLARE v_txn VARCHAR(50);

    -- Check if already paid
    SELECT COUNT(*) INTO v_already_paid
    FROM payments
    WHERE application_id = p_application_id AND status = 'Completed';

    IF v_already_paid > 0 THEN
        SET p_transaction_ref = NULL;
        SET p_result_message = 'ERROR: Payment already completed for this application.';
    ELSE
        -- Get fee
        SELECT s.fee INTO v_fee
        FROM applications a
            INNER JOIN services s ON a.service_id = s.service_id
        WHERE a.application_id = p_application_id;

        IF v_fee IS NULL THEN
            SET p_transaction_ref = NULL;
            SET p_result_message = 'ERROR: Application not found.';
        ELSE
            -- Generate transaction reference
            SET v_txn = CONCAT('TXN', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND() * 99999), 5, '0'));

            INSERT INTO payments (application_id, citizen_id, amount, payment_method, transaction_ref, status)
            VALUES (p_application_id, p_citizen_id, v_fee, p_payment_method, v_txn, 'Completed');

            SET p_transaction_ref = v_txn;
            SET p_result_message = CONCAT('Payment of ₹', v_fee, ' completed. Transaction: ', v_txn);
        END IF;
    END IF;
END //

DELIMITER ;
