-- =============================================================================
-- DIGITAL LEGACY VAULT - ORACLE 11g XE SEED DATA
-- File: oracle_sql/02_seed.sql
-- Description: Synthetic demonstration dataset matching the Neo4j graph entities.
-- Inserts parent records first, followed by child records and associations.
-- =============================================================================

SET DEFINE OFF
SET ECHO ON
SET FEEDBACK ON
SET LINESIZE 150
SET PAGESIZE 50

PROMPT =========================================================================
PROMPT   DIGITAL LEGACY VAULT - Seeding Sample Relational Records
PROMPT =========================================================================

-- -----------------------------------------------------------------------------
-- 1. Insert Digital Estate Owners (USERS)
-- -----------------------------------------------------------------------------
PROMPT Inserting USERS...

INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('usr_001', 'Eleanor Vance', 'eleanor.vance@legacyvault.io', '+1-555-0101', 'Active', TO_DATE('2026-01-15', 'YYYY-MM-DD'));

INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('usr_002', 'Marcus Chen', 'marcus.chen@techcorp.com', '+1-555-0102', 'Active', TO_DATE('2026-02-10', 'YYYY-MM-DD'));

INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('usr_003', 'Sophia Rodriguez', 'sophia.r@bioresearch.org', '+1-555-0103', 'Active', TO_DATE('2026-03-01', 'YYYY-MM-DD'));

INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('usr_004', 'Dr. Arvind Kumar', 'arvind.kumar@univ.edu', '+91-98765-43210', 'Active', TO_DATE('2026-03-12', 'YYYY-MM-DD'));

INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('usr_005', 'Chloe Bennet', 'chloe.bennet@artstudio.design', '+44-20-7946-0912', 'Inactive', TO_DATE('2026-04-05', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 2. Insert DIGITAL_ASSETS
-- -----------------------------------------------------------------------------
PROMPT Inserting DIGITAL_ASSETS...

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_001', 'usr_001', 'Cold Storage Bitcoin Wallet', 'Cryptocurrency', 'Hardware Ledger seed phrase stored in Safe Deposit Box #402', 'Critical', 125000.00, TO_DATE('2026-01-16', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_002', 'usr_001', 'Family Photo Archive (NextCloud)', 'Cloud Storage', 'Encrypted volume credentials in 1Password shared family vault', 'High', 5000.00, TO_DATE('2026-01-16', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_003', 'usr_002', 'GitHub Pro Repositories & Patents', 'Intellectual Property', 'GPG signing key backup stored on YubiKey 5C NFC', 'High', 50000.00, TO_DATE('2026-02-12', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_004', 'usr_002', 'E-Trade Investment Portfolio', 'Financial Account', 'Account ending in 8841; Transfer on Death verified', 'Critical', 340000.00, TO_DATE('2026-02-12', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_005', 'usr_003', 'Genomics Research Data Vault', 'Research Archive', 'AWS S3 bucket with Glacier vault lock and MFA delete policy', 'High', 75000.00, TO_DATE('2026-03-02', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_006', 'usr_004', 'Primary Domain Portfolio (.ai & .io)', 'Domain Portfolio', 'Cloudflare Registrar account with hardware security key', 'Medium', 18000.00, TO_DATE('2026-03-15', 'YYYY-MM-DD'));

INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_007', 'usr_005', 'YouTube Creator Channel Archive', 'Social Media', 'Google Brand Account legacy contact set to executor email', 'Medium', 24000.00, TO_DATE('2026-04-06', 'YYYY-MM-DD'));

-- ast_008 intentionally has NO nominee allocation and NO plan assigned (Orphan Asset demo)
INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('ast_008', 'usr_005', 'Personal Memoir & Journals', 'Personal Document', 'VeraCrypt encrypted archive on backup USB Drive #2', 'High', 1500.00, TO_DATE('2026-04-06', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 3. Insert NOMINEES (Beneficiaries)
-- -----------------------------------------------------------------------------
PROMPT Inserting NOMINEES...

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_001', 'usr_001', 'Julian Vance', 'Spouse', 'julian.vance@gmail.com', '+1-555-0201', TO_DATE('2026-01-17', 'YYYY-MM-DD'));

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_002', 'usr_001', 'Clara Vance', 'Daughter', 'clara.vance@stanford.edu', '+1-555-0202', TO_DATE('2026-01-17', 'YYYY-MM-DD'));

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_003', 'usr_002', 'David Chen', 'Brother', 'david.chen@technova.co', '+1-555-0203', TO_DATE('2026-02-14', 'YYYY-MM-DD'));

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_004', 'usr_003', 'Open Science Foundation', 'Institutional Beneficiary', 'grants@openscience.org', '+1-800-555-0199', TO_DATE('2026-03-05', 'YYYY-MM-DD'));

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_005', 'usr_004', 'Priya Kumar', 'Sister', 'priya.k@delhi.ac.in', '+91-98111-22334', TO_DATE('2026-03-18', 'YYYY-MM-DD'));

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('nom_006', 'usr_005', 'Leo Bennet-Hall', 'Nephew', 'leo.b@londonart.ac.uk', '+44-20-7946-0111', TO_DATE('2026-04-07', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 4. Insert TRUSTED_EXECUTORS (Legal Fiduciaries)
-- -----------------------------------------------------------------------------
PROMPT Inserting TRUSTED_EXECUTORS...

INSERT INTO TRUSTED_EXECUTORS (executor_id, user_id, name, email, phone, verification_status, role_description, created_at)
VALUES ('exe_001', 'usr_001', 'Robert Sterling, Esq.', 'sterling@heritage-law.com', '+1-555-0301', 'Verified Notary & Attorney', 'Legal Executor & Estate Counsel', TO_DATE('2026-01-18', 'YYYY-MM-DD'));

INSERT INTO TRUSTED_EXECUTORS (executor_id, user_id, name, email, phone, verification_status, role_description, created_at)
VALUES ('exe_002', 'usr_002', 'Apex Trust & Fiduciary Services', 'digitalestates@apextrust.com', '+1-888-555-0400', 'Licensed Corporate Fiduciary', 'Institutional Digital Asset Trustee', TO_DATE('2026-02-15', 'YYYY-MM-DD'));

INSERT INTO TRUSTED_EXECUTORS (executor_id, user_id, name, email, phone, verification_status, role_description, created_at)
VALUES ('exe_003', 'usr_003', 'Prof. Vikram Sen', 'vikram.sen@univ-dean.edu', '+91-99887-66554', 'Academic Peer Verified', 'Scientific Data Custodian', TO_DATE('2026-03-19', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 5. Insert LEGACY_PLANS (Succession Protocols)
-- -----------------------------------------------------------------------------
PROMPT Inserting LEGACY_PLANS...

INSERT INTO LEGACY_PLANS (plan_id, user_id, executor_id, title, trigger_condition, status, notes, created_at)
VALUES ('pln_001', 'usr_001', 'exe_001', 'Comprehensive Digital Asset & Crypto Succession Plan', 'Legal Death Certificate Verification', 'Active', 'Release Bitcoin keys to Julian and Photo Archive to Clara via Attorney Sterling.', TO_DATE('2026-01-20', 'YYYY-MM-DD'));

INSERT INTO LEGACY_PLANS (plan_id, user_id, executor_id, title, trigger_condition, status, notes, created_at)
VALUES ('pln_002', 'usr_002', 'exe_002', 'Tech Founder Intellectual Property & Equity Plan', 'Inactivity > 180 Days with Dual Notary Confirmation', 'Active', 'Transfer repository access and investment funds to David Chen.', TO_DATE('2026-02-20', 'YYYY-MM-DD'));

INSERT INTO LEGACY_PLANS (plan_id, user_id, executor_id, title, trigger_condition, status, notes, created_at)
VALUES ('pln_003', 'usr_003', 'exe_003', 'Open Science Public Archive Donation Plan', 'Certified Incapacitation or Death', 'Pending Review', 'Publish genomics data under Creative Commons 4.0 via Open Science Foundation.', TO_DATE('2026-03-22', 'YYYY-MM-DD'));

INSERT INTO LEGACY_PLANS (plan_id, user_id, executor_id, title, trigger_condition, status, notes, created_at)
VALUES ('pln_004', 'usr_005', NULL, 'Family Memoirs & Memorial Social Plan', 'Executor Verification and Request', 'Draft', 'Convert YouTube to memorial channel and send memoirs to nephew Leo.', TO_DATE('2026-04-08', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 6. Insert ASSET_ALLOCATIONS (Nominee <-> Asset M:N with Share %)
-- -----------------------------------------------------------------------------
PROMPT Inserting ASSET_ALLOCATIONS...

-- Eleanor Vance: Julian Vance gets 100% of Bitcoin Wallet
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_001', 'nom_001', 100, 'Primary Beneficiary', TO_DATE('2026-01-21', 'YYYY-MM-DD'));

-- Eleanor Vance: Clara Vance gets 100% of Family Photo Archive
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_002', 'nom_002', 100, 'Family Custodian', TO_DATE('2026-01-21', 'YYYY-MM-DD'));

-- Marcus Chen: David Chen gets 50% of GitHub Repos & Patents
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_003', 'nom_003', 50, 'Co-Beneficiary', TO_DATE('2026-02-21', 'YYYY-MM-DD'));

-- Marcus Chen: David Chen gets 100% of E-Trade Portfolio
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_004', 'nom_003', 100, 'Sole Beneficiary', TO_DATE('2026-02-21', 'YYYY-MM-DD'));

-- Sophia Rodriguez: Open Science Foundation gets 100% of Genomics Research Vault
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_005', 'nom_004', 100, 'Public Trust', TO_DATE('2026-03-23', 'YYYY-MM-DD'));

-- Dr. Arvind Kumar: Priya Kumar gets 100% of Domain Portfolio
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_006', 'nom_005', 100, 'Primary Beneficiary', TO_DATE('2026-03-24', 'YYYY-MM-DD'));

-- Chloe Bennet: Leo Bennet-Hall gets 100% of YouTube Creator Archive
INSERT INTO ASSET_ALLOCATIONS (asset_id, nominee_id, share_pct, designation_type, assigned_at)
VALUES ('ast_007', 'nom_006', 100, 'Beneficiary', TO_DATE('2026-04-09', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 7. Insert PLAN_ASSETS (Legacy Plan <-> Digital Asset Associations)
-- -----------------------------------------------------------------------------
PROMPT Inserting PLAN_ASSETS...

INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_001', 'ast_001', TO_DATE('2026-01-21', 'YYYY-MM-DD'));
INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_001', 'ast_002', TO_DATE('2026-01-21', 'YYYY-MM-DD'));
INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_002', 'ast_003', TO_DATE('2026-02-21', 'YYYY-MM-DD'));
INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_002', 'ast_004', TO_DATE('2026-02-21', 'YYYY-MM-DD'));
INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_003', 'ast_005', TO_DATE('2026-03-23', 'YYYY-MM-DD'));
INSERT INTO PLAN_ASSETS (plan_id, asset_id, added_at) VALUES ('pln_004', 'ast_007', TO_DATE('2026-04-09', 'YYYY-MM-DD'));


-- -----------------------------------------------------------------------------
-- 8. Insert SCHEDULED_RELEASES (Execution Timeline)
-- -----------------------------------------------------------------------------
PROMPT Inserting SCHEDULED_RELEASES...

INSERT INTO SCHEDULED_RELEASES (release_id, plan_id, asset_id, release_date, status, notification_method, notes, created_at)
VALUES ('rel_001', 'pln_001', 'ast_001', TO_DATE('2026-12-01', 'YYYY-MM-DD'), 'Scheduled', 'Encrypted Email + SMS OTP', 'Automated transfer trigger upon non-response to annual heartbeat ping', TO_DATE('2026-01-22', 'YYYY-MM-DD'));

INSERT INTO SCHEDULED_RELEASES (release_id, plan_id, asset_id, release_date, status, notification_method, notes, created_at)
VALUES ('rel_002', 'pln_002', 'ast_004', TO_DATE('2027-01-15', 'YYYY-MM-DD'), 'Scheduled', 'Notary In-Person Verification', 'Crypto and investment account multi-sig key disclosure', TO_DATE('2026-02-25', 'YYYY-MM-DD'));

INSERT INTO SCHEDULED_RELEASES (release_id, plan_id, asset_id, release_date, status, notification_method, notes, created_at)
VALUES ('rel_003', 'pln_003', 'ast_005', TO_DATE('2026-11-15', 'YYYY-MM-DD'), 'In Review', 'Institutional Grant Portal Notice', 'Pending peer review approval before open-sourcing genomic vault', TO_DATE('2026-03-25', 'YYYY-MM-DD'));

INSERT INTO SCHEDULED_RELEASES (release_id, plan_id, asset_id, release_date, status, notification_method, notes, created_at)
VALUES ('rel_004', NULL, 'ast_006', TO_DATE('2026-05-01', 'YYYY-MM-DD'), 'Released', 'Automated Webhook & Archival Dispatch', 'Initial public domain name DNS redirection executed', TO_DATE('2026-04-10', 'YYYY-MM-DD'));

-- Commit transaction
COMMIT;

PROMPT
PROMPT =========================================================================
PROMPT   Seed Data Successfully Inserted & Committed. Record Counts:
PROMPT =========================================================================

SELECT 'USERS' AS entity, COUNT(*) AS total FROM USERS
UNION ALL
SELECT 'DIGITAL_ASSETS', COUNT(*) FROM DIGITAL_ASSETS
UNION ALL
SELECT 'NOMINEES', COUNT(*) FROM NOMINEES
UNION ALL
SELECT 'TRUSTED_EXECUTORS', COUNT(*) FROM TRUSTED_EXECUTORS
UNION ALL
SELECT 'LEGACY_PLANS', COUNT(*) FROM LEGACY_PLANS
UNION ALL
SELECT 'ASSET_ALLOCATIONS', COUNT(*) FROM ASSET_ALLOCATIONS
UNION ALL
SELECT 'PLAN_ASSETS', COUNT(*) FROM PLAN_ASSETS
UNION ALL
SELECT 'SCHEDULED_RELEASES', COUNT(*) FROM SCHEDULED_RELEASES;

PROMPT
PROMPT Seeding complete. Proceed to execute: @oracle_sql/03_queries.sql
