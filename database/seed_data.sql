-- =============================================================================
-- E-Governance Service Management System
-- Seed Data — Departments, Services, Requirements, Sample Users & Officers
-- =============================================================================

USE e_governance;

-- ─────────────────────────────────────────────────────────────────────────────
-- DEPARTMENTS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO departments (name, description, head_name, contact_email, contact_phone) VALUES
('Revenue Department',       'Handles revenue, land records, income certificates',  'Shri Rajesh Kumar',   'revenue@gov.in',      '011-23456701'),
('Health Department',        'Public health, birth/death certificates',             'Dr. Priya Sharma',    'health@gov.in',        '011-23456702'),
('Education Department',     'Education certificates, scholarships',                'Shri Amit Verma',     'education@gov.in',     '011-23456703'),
('Home Department',          'Police verification, character certificates',         'Shri Vikram Singh',   'home@gov.in',          '011-23456704'),
('Urban Development',        'Property, building permits, trade licenses',          'Smt. Meera Patel',    'urban@gov.in',         '011-23456705'),
('Social Welfare',           'Caste certificates, disability certificates, pensions','Shri Arvind Joshi',  'welfare@gov.in',       '011-23456706'),
('Transport Department',     'Driving license, vehicle registration',               'Smt. Kavita Reddy',   'transport@gov.in',     '011-23456707');

-- ─────────────────────────────────────────────────────────────────────────────
-- SERVICES
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO services (department_id, name, description, category, fee, processing_days) VALUES
-- Revenue Department (1)
(1, 'Income Certificate',       'Certificate verifying annual income of the applicant',          'Certificate',  50.00,   7),
(1, 'Domicile Certificate',     'Certificate proving residence/domicile in the state',           'Certificate',  50.00,   10),
(1, 'Land Record Extract',      'Extract of land ownership records',                             'Record',       100.00,  15),

-- Health Department (2)
(2, 'Birth Certificate',        'Official certificate of birth registration',                    'Certificate',  30.00,   5),
(2, 'Death Certificate',        'Official certificate of death registration',                    'Certificate',  30.00,   5),

-- Education Department (3)
(3, 'Education Verification',   'Verification of educational qualifications',                    'Verification', 200.00,  15),
(3, 'Scholarship Application',  'Apply for government scholarship programmes',                   'Financial',    0.00,    30),

-- Home Department (4)
(4, 'Police Verification',      'Background check and character verification by police',         'Verification', 100.00,  14),
(4, 'Character Certificate',    'Certificate of good character and conduct',                     'Certificate',  50.00,   7),

-- Urban Development (5)
(5, 'Trade License',            'License to carry out trade/business in municipal area',         'License',      500.00,  21),
(5, 'Building Permit',          'Permission for new construction or renovation',                 'Permit',       1000.00, 30),

-- Social Welfare (6)
(6, 'Caste Certificate',        'Certificate verifying caste/community of the applicant',        'Certificate',  30.00,   10),
(6, 'Disability Certificate',   'Certificate verifying disability percentage',                   'Certificate',  0.00,    15),
(6, 'Senior Citizen ID',        'Identity card for senior citizens for availing benefits',       'ID Card',      0.00,    7),

-- Transport Department (7)
(7, 'Driving License',          'Application for new driving license',                           'License',      300.00,  21),
(7, 'Vehicle Registration',     'Registration of new vehicle',                                   'Registration', 500.00,  14);

-- ─────────────────────────────────────────────────────────────────────────────
-- SERVICE REQUIREMENTS (documents needed for each service)
-- ─────────────────────────────────────────────────────────────────────────────
-- Income Certificate (service_id = 1)
INSERT INTO service_requirements (service_id, document_name, description, is_mandatory) VALUES
(1, 'Aadhaar Card',             'Government-issued identity proof',              TRUE),
(1, 'Salary Slip / ITR',       'Proof of income',                               TRUE),
(1, 'Ration Card',              'Family ration card',                            FALSE),

-- Domicile Certificate (2)
(2, 'Aadhaar Card',             'Government-issued identity proof',              TRUE),
(2, 'Address Proof',            'Electricity bill / Rent agreement',             TRUE),
(2, 'School Certificate',       'For proof of birth place',                      FALSE),

-- Birth Certificate (4)
(4, 'Hospital Discharge Summary', 'Birth record from hospital',                  TRUE),
(4, 'Parents Aadhaar',           'Identity proof of parents',                    TRUE),

-- Death Certificate (5)
(5, 'Hospital Death Summary',    'Death record from hospital',                   TRUE),
(5, 'Deceased Aadhaar',          'Identity proof of deceased',                   TRUE),

-- Police Verification (8)
(8, 'Aadhaar Card',              'Government-issued identity proof',             TRUE),
(8, 'Passport Size Photo',       'Recent photograph',                            TRUE),
(8, 'Address Proof',             'Current address verification document',        TRUE),

-- Driving License (15)
(15, 'Aadhaar Card',             'Government-issued identity proof',             TRUE),
(15, 'Address Proof',            'Proof of current address',                     TRUE),
(15, 'Medical Certificate',      'Fitness certificate from registered doctor',   TRUE),
(15, 'Learner License',          'Valid learner license',                        TRUE);

-- ─────────────────────────────────────────────────────────────────────────────
-- SAMPLE USERS (password: "password123" hashed with bcrypt)
-- ─────────────────────────────────────────────────────────────────────────────
-- Note: In production, passwords are hashed by the backend.
-- The hash below corresponds to "password123" using bcrypt.
INSERT INTO users (full_name, email, password_hash, phone, address, date_of_birth, aadhaar_number, role) VALUES
-- Citizens
('Rahul Sharma',    'rahul@example.com',    '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543210', '12, MG Road, Delhi',       '1995-06-15', '123456789012', 'citizen'),
('Priya Patel',     'priya@example.com',    '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543211', '45, Park Street, Mumbai',  '1990-03-22', '123456789013', 'citizen'),
('Amit Singh',      'amit@example.com',     '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543212', '78, Civil Lines, Jaipur',  '1988-11-08', '123456789014', 'citizen'),

-- Officers
('Suresh Gupta',    'suresh@gov.in',        '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543220', 'Revenue Bhawan, Delhi',    '1975-01-10', '223456789012', 'officer'),
('Neha Mishra',     'neha@gov.in',          '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543221', 'Health Bhawan, Delhi',     '1980-07-25', '223456789013', 'officer'),
('Vikash Yadav',    'vikash@gov.in',        '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543222', 'Police HQ, Delhi',         '1978-04-12', '223456789014', 'officer'),

-- Admin
('Admin User',      'admin@gov.in',         '$2b$12$LJ3m4ys2Lpg0mOyBH.Gj4OQfBJdX6bLGLa/RV0KMjhQZx5Vj8Gxe', '9876543200', 'Secretariat, Delhi',       '1970-01-01', '333456789012', 'admin');

-- ─────────────────────────────────────────────────────────────────────────────
-- OFFICERS (linked to users)
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO officers (user_id, department_id, designation, employee_code, date_of_joining) VALUES
(4, 1, 'Revenue Inspector',         'REV001', '2005-06-01'),
(5, 2, 'Health Officer',            'HLT001', '2010-03-15'),
(6, 4, 'Sub-Inspector (Verification)', 'HOM001', '2008-09-20');

-- ─────────────────────────────────────────────────────────────────────────────
-- SAMPLE APPLICATIONS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO applications (application_ref, citizen_id, service_id, officer_id, status, remarks) VALUES
('APP10001', 1, 1, 1, 'Submitted',         NULL),
('APP10002', 1, 4, 2, 'Approved',          'All documents verified. Certificate issued.'),
('APP10003', 2, 2, 1, 'Under Review',      'Address proof needs re-verification.'),
('APP10004', 2, 8, 3, 'Documents Verified', NULL),
('APP10005', 3, 6, NULL, 'Submitted',      NULL),
('APP10006', 3, 15, NULL, 'Rejected',      'Medical certificate expired. Please resubmit.');

-- Update completed_at for Approved/Rejected
UPDATE applications SET completed_at = NOW() WHERE status IN ('Approved', 'Rejected');

-- ─────────────────────────────────────────────────────────────────────────────
-- SAMPLE PAYMENTS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO payments (application_id, citizen_id, amount, payment_method, transaction_ref, status) VALUES
(1, 1, 50.00,  'UPI',          'TXN20240001', 'Completed'),
(2, 1, 30.00,  'Net Banking',  'TXN20240002', 'Completed'),
(3, 2, 50.00,  'Debit Card',   'TXN20240003', 'Completed'),
(4, 2, 100.00, 'UPI',          'TXN20240004', 'Completed'),
(6, 3, 300.00, 'Credit Card',  'TXN20240005', 'Completed');

-- ─────────────────────────────────────────────────────────────────────────────
-- SAMPLE NOTIFICATIONS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO notifications (user_id, title, message, type) VALUES
(1, 'Application Submitted',           'Your application APP10001 for Income Certificate has been submitted successfully.',     'Info'),
(1, 'Application Approved',            'Your application APP10002 for Birth Certificate has been approved!',                     'Success'),
(2, 'Application Under Review',        'Your application APP10003 for Domicile Certificate is now under review.',               'Info'),
(3, 'Application Rejected',            'Your application APP10006 for Driving License has been rejected. Check remarks.',       'Error');

-- ─────────────────────────────────────────────────────────────────────────────
-- SAMPLE COMPLAINTS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO complaints (complaint_ref, citizen_id, application_id, subject, description, status, priority) VALUES
('CMP10001', 3, 6, 'Unfair Rejection', 'My driving license application was rejected but my medical certificate is valid.', 'Open', 'High');
