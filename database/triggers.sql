-- =============================================================================
-- E-Governance Service Management System
-- Database Triggers
-- =============================================================================

USE e_governance;

DELIMITER //

-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER: trg_application_status_notification
-- After an application status is updated, automatically create a notification
-- for the citizen.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TRIGGER IF NOT EXISTS trg_application_status_notification
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    DECLARE v_service_name VARCHAR(200);
    DECLARE v_notif_type VARCHAR(10);
    DECLARE v_title VARCHAR(300);
    DECLARE v_message TEXT;

    -- Only fire if status actually changed
    IF OLD.status <> NEW.status THEN
        -- Get service name
        SELECT name INTO v_service_name
        FROM services WHERE service_id = NEW.service_id;

        -- Determine notification type
        SET v_notif_type = CASE
            WHEN NEW.status = 'Approved'  THEN 'Success'
            WHEN NEW.status = 'Rejected'  THEN 'Error'
            WHEN NEW.status = 'Returned'  THEN 'Warning'
            ELSE 'Info'
        END;

        SET v_title = CONCAT('Application ', NEW.application_ref, ' — ', NEW.status);
        SET v_message = CONCAT(
            'Your application ', NEW.application_ref,
            ' for "', v_service_name, '"',
            ' has been updated to: ', NEW.status, '.',
            CASE
                WHEN NEW.remarks IS NOT NULL
                THEN CONCAT(' Remarks: ', NEW.remarks)
                ELSE ''
            END
        );

        INSERT INTO notifications (user_id, title, message, type)
        VALUES (NEW.citizen_id, v_title, v_message, v_notif_type);
    END IF;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER: trg_complaint_resolved_notification
-- When a complaint is resolved, notify the citizen.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TRIGGER IF NOT EXISTS trg_complaint_resolved_notification
AFTER UPDATE ON complaints
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status AND NEW.status IN ('Resolved', 'Closed') THEN
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (
            NEW.citizen_id,
            CONCAT('Complaint ', NEW.complaint_ref, ' ', NEW.status),
            CONCAT('Your complaint "', NEW.subject, '" has been ', LOWER(NEW.status), '.'),
            'Success'
        );

        -- Also update resolved_at timestamp
        -- (Note: Cannot update same table in AFTER trigger in some MySQL versions,
        --  so this is handled in the application layer instead.)
    END IF;
END //

-- ─────────────────────────────────────────────────────────────────────────────
-- TRIGGER: trg_payment_notification
-- After a successful payment, notify the citizen.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TRIGGER IF NOT EXISTS trg_payment_notification
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE v_app_ref VARCHAR(20);

    IF NEW.status = 'Completed' THEN
        SELECT application_ref INTO v_app_ref
        FROM applications WHERE application_id = NEW.application_id;

        INSERT INTO notifications (user_id, title, message, type)
        VALUES (
            NEW.citizen_id,
            CONCAT('Payment Received — ', v_app_ref),
            CONCAT('Payment of ₹', NEW.amount, ' received for application ', v_app_ref,
                   '. Transaction ID: ', NEW.transaction_ref),
            'Success'
        );
    END IF;
END //

DELIMITER ;
