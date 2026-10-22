-- =============================================================================
-- DIGITAL LEGACY VAULT - ORACLE 11g XE TRANSACTION MANAGEMENT
-- File: oracle_sql/04_transactions.sql
-- Description: Practical demonstration of ACID transaction control statements:
-- COMMIT, SAVEPOINT, and ROLLBACK.
-- Uses isolated demo records (demo_usr_999 / demo_ast_999) so real records
-- are never disturbed.
-- =============================================================================

SET DEFINE OFF
SET ECHO ON
SET FEEDBACK ON
SET LINESIZE 140
SET PAGESIZE 50

PROMPT =========================================================================
PROMPT   DIGITAL LEGACY VAULT - Transaction Management Demonstration
PROMPT =========================================================================

-- -----------------------------------------------------------------------------
-- SCENARIO A: Atomic Multi-Table Insertion with COMMIT
-- Demonstrates registering a new test user and their initial digital asset,
-- then committing the transaction permanently to the database.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Transaction 1] Atomic Insertion: User + Asset (Permanent COMMIT)
PROMPT -------------------------------------------------------------------------

-- 1. Insert temporary demo user
INSERT INTO USERS (user_id, name, email, phone, status, created_at)
VALUES ('demo_usr_999', 'Transaction Test User', 'txn.demo@legacyvault.io', '+1-555-9999', 'Active', SYSDATE);

-- 2. Insert corresponding digital asset for demo user
INSERT INTO DIGITAL_ASSETS (asset_id, user_id, title, asset_type, access_info_hint, priority, estimated_value, created_at)
VALUES ('demo_ast_999', 'demo_usr_999', 'Demo Hardware Seed Wallet', 'Cryptocurrency', 'Encrypted seed in safe #99', 'Critical', 50000.00, SYSDATE);

-- 3. Verify uncommitted records exist in current session
PROMPT Verifying uncommitted demo records in current transaction:
SELECT user_id, name, email, status FROM USERS WHERE user_id = 'demo_usr_999';
SELECT asset_id, user_id, title, estimated_value FROM DIGITAL_ASSETS WHERE asset_id = 'demo_ast_999';

-- 4. Explicitly COMMIT the transaction
PROMPT Committing Transaction 1 permanently...
COMMIT;

PROMPT Transaction 1 successfully committed to database.


-- -----------------------------------------------------------------------------
-- SCENARIO B: Safe UPDATE and Partial ROLLBACK Using SAVEPOINT
-- Demonstrates updating asset valuation, setting a SAVEPOINT, performing a
-- mistaken deletion, and rolling back specifically to the SAVEPOINT.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Transaction 2] Demonstrating SAVEPOINT and Partial ROLLBACK
PROMPT -------------------------------------------------------------------------

-- Step 1: Update the demo asset's valuation
UPDATE DIGITAL_ASSETS
SET estimated_value = 75000.00,
    priority = 'Critical'
WHERE asset_id = 'demo_ast_999';

PROMPT Updated asset value to $75,000. Checking current uncommitted state:
SELECT asset_id, title, estimated_value FROM DIGITAL_ASSETS WHERE asset_id = 'demo_ast_999';

-- Step 2: Create a named savepoint
SAVEPOINT sp_after_valuation_update;
PROMPT SAVEPOINT 'sp_after_valuation_update' established.

-- Step 3: Simulate an accidental erroneous delete of the asset
DELETE FROM DIGITAL_ASSETS
WHERE asset_id = 'demo_ast_999';

PROMPT Asset deleted in current transaction. Verifying row count:
SELECT COUNT(*) AS asset_count_after_delete 
FROM DIGITAL_ASSETS 
WHERE asset_id = 'demo_ast_999';

-- Step 4: Undo the accidental deletion by rolling back to the savepoint!
PROMPT Rolling back to SAVEPOINT 'sp_after_valuation_update'...
ROLLBACK TO SAVEPOINT sp_after_valuation_update;

PROMPT Rollback to savepoint completed! Verifying asset was safely restored:
SELECT asset_id, title, estimated_value 
FROM DIGITAL_ASSETS 
WHERE asset_id = 'demo_ast_999';


-- -----------------------------------------------------------------------------
-- SCENARIO C: Complete ROLLBACK
-- Demonstrates inserting an invalid nominee, deciding to cancel the entire
-- transaction, and restoring previous consistent state.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Transaction 3] Full Transaction ROLLBACK
PROMPT -------------------------------------------------------------------------

INSERT INTO NOMINEES (nominee_id, user_id, name, relationship, email, phone, created_at)
VALUES ('demo_nom_999', 'demo_usr_999', 'Temporary Test Nominee', 'Friend', 'temp@example.com', '+1-555-0000', SYSDATE);

PROMPT Temporary nominee inserted. Verifying uncommitted row exists:
SELECT nominee_id, name, email FROM NOMINEES WHERE nominee_id = 'demo_nom_999';

PROMPT Deciding to cancel this entire transaction...
ROLLBACK;

PROMPT Full ROLLBACK executed. Verifying nominee was discarded:
SELECT COUNT(*) AS nominee_exists 
FROM NOMINEES 
WHERE nominee_id = 'demo_nom_999';


-- -----------------------------------------------------------------------------
-- SCENARIO D: Clean Cleanup of Demo Records
-- Removes the demo user and demo asset created in Scenario A, then commits.
-- Real project records (usr_001 to usr_005) remain completely intact!
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Cleanup] Safely removing demo test records
PROMPT -------------------------------------------------------------------------

DELETE FROM DIGITAL_ASSETS WHERE asset_id = 'demo_ast_999';
DELETE FROM USERS WHERE user_id = 'demo_usr_999';
COMMIT;

PROMPT Cleanup finished. Verifying no demo records remain:
SELECT COUNT(*) AS remaining_demo_users FROM USERS WHERE user_id = 'demo_usr_999';
SELECT COUNT(*) AS remaining_demo_assets FROM DIGITAL_ASSETS WHERE asset_id = 'demo_ast_999';

PROMPT
PROMPT =========================================================================
PROMPT   Transaction Demonstration Finished. All Tests Passed.
PROMPT =========================================================================
