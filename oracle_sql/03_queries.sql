-- =============================================================================
-- DIGITAL LEGACY VAULT - ORACLE 11g XE QUERIES
-- File: oracle_sql/03_queries.sql
-- Description: Practical SQL demonstrations for DBMS coursework and evaluation.
-- Covers: Filters, Multi-Table INNER/LEFT JOINs, GROUP BY Aggregations,
-- Orphan Asset Detection, and Comparative Academic Reports.
-- =============================================================================

SET DEFINE OFF
SET ECHO ON
SET FEEDBACK ON
SET LINESIZE 160
SET PAGESIZE 60

PROMPT =========================================================================
PROMPT   DIGITAL LEGACY VAULT - Analytical & Relational SQL Queries
PROMPT =========================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Basic SELECT with WHERE & ORDER BY
-- Description: Retrieves all high-priority or critical digital assets, ordered
-- by their estimated value in descending order.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 1] High and Critical Priority Assets Ordered by Value
PROMPT -------------------------------------------------------------------------

COLUMN asset_id FORMAT A10
COLUMN title FORMAT A35
COLUMN asset_type FORMAT A22
COLUMN priority FORMAT A10
COLUMN estimated_value FORMAT $999,999.99

SELECT 
    asset_id,
    title,
    asset_type,
    priority,
    estimated_value
FROM DIGITAL_ASSETS
WHERE priority IN ('High', 'Critical')
ORDER BY estimated_value DESC;


-- -----------------------------------------------------------------------------
-- QUERY 2: Multi-Table INNER JOIN (4-Way Relational Walk)
-- Description: Demonstrates relational traversal across USERS, DIGITAL_ASSETS,
-- ASSET_ALLOCATIONS, and NOMINEES to identify which beneficiary receives which
-- asset and their allocated share percentage.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 2] Multi-Table INNER JOIN: Asset Distribution to Beneficiaries
PROMPT -------------------------------------------------------------------------

COLUMN owner_name FORMAT A18
COLUMN asset_title FORMAT A30
COLUMN nominee_name FORMAT A20
COLUMN relationship FORMAT A15
COLUMN share_pct FORMAT 999
COLUMN designation_type FORMAT A20

SELECT 
    u.name AS owner_name,
    a.title AS asset_title,
    n.name AS nominee_name,
    n.relationship,
    al.share_pct,
    al.designation_type
FROM USERS u
    JOIN DIGITAL_ASSETS a ON u.user_id = a.user_id
    JOIN ASSET_ALLOCATIONS al ON a.asset_id = al.asset_id
    JOIN NOMINEES n ON al.nominee_id = n.nominee_id
ORDER BY u.name, al.share_pct DESC;


-- -----------------------------------------------------------------------------
-- QUERY 3: Aggregations with COUNT, SUM, AVG, and GROUP BY
-- Description: Summarizes each user's digital estate portfolio (total assets,
-- total portfolio value, and average asset value).
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 3] GROUP BY Aggregates: Digital Estate Summary Per Owner
PROMPT -------------------------------------------------------------------------

COLUMN user_name FORMAT A20
COLUMN total_assets FORMAT 9999
COLUMN total_portfolio_value FORMAT $999,999.99
COLUMN avg_asset_value FORMAT $999,999.99

SELECT 
    u.name AS user_name,
    u.status,
    COUNT(a.asset_id) AS total_assets,
    SUM(a.estimated_value) AS total_portfolio_value,
    AVG(a.estimated_value) AS avg_asset_value
FROM USERS u
    LEFT JOIN DIGITAL_ASSETS a ON u.user_id = a.user_id
GROUP BY u.name, u.status
ORDER BY total_portfolio_value DESC;


-- -----------------------------------------------------------------------------
-- QUERY 4: Orphan Digital Asset Detection (LEFT JOIN with NULL Check)
-- Description: Anti-pattern query finding digital assets that have NO nominee
-- allocated to inherit them. Demonstrates how relational SQL uses a LEFT JOIN
-- with a WHERE IS NULL condition, directly comparable to Cypher's WHERE NOT ().
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 4] Orphan Asset Detection: Assets Without Any Nominee Allocation
PROMPT -------------------------------------------------------------------------

COLUMN owner_id FORMAT A10
COLUMN owner_name FORMAT A18
COLUMN asset_id FORMAT A10
COLUMN asset_title FORMAT A30
COLUMN asset_type FORMAT A20
COLUMN priority FORMAT A10
COLUMN allocation_risk FORMAT A35

SELECT 
    u.user_id AS owner_id,
    u.name AS owner_name,
    a.asset_id,
    a.title AS asset_title,
    a.asset_type,
    a.priority,
    'AT RISK: No Nominee Allocated' AS allocation_risk
FROM DIGITAL_ASSETS a
    JOIN USERS u ON a.user_id = u.user_id
    LEFT JOIN ASSET_ALLOCATIONS al ON a.asset_id = al.asset_id
WHERE al.allocation_id IS NULL;


-- -----------------------------------------------------------------------------
-- QUERY 5: Fiduciary Oversight & Plan Governance Audit
-- Description: Displays which certified Trusted Executors supervise which
-- Legacy Plans, including trigger conditions and active status.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 5] Fiduciary Audit: Legal Executors and Supervised Plans
PROMPT -------------------------------------------------------------------------

COLUMN executor_name FORMAT A25
COLUMN verification_status FORMAT A26
COLUMN plan_title FORMAT A35
COLUMN trigger_condition FORMAT A35
COLUMN plan_status FORMAT A15

SELECT 
    e.name AS executor_name,
    e.verification_status,
    p.title AS plan_title,
    p.trigger_condition,
    p.status AS plan_status
FROM TRUSTED_EXECUTORS e
    JOIN LEGACY_PLANS p ON e.executor_id = p.executor_id
ORDER BY e.name;


-- -----------------------------------------------------------------------------
-- QUERY 6: Scheduled Execution Timeline & Notification Dispatch
-- Description: Chronological timeline of upcoming releases, associated plans,
-- asset titles, and secure notification channels.
-- -----------------------------------------------------------------------------
PROMPT
PROMPT -------------------------------------------------------------------------
PROMPT [Query 6] Execution Schedule: Chronological Asset Release Timeline
PROMPT -------------------------------------------------------------------------

COLUMN release_id FORMAT A10
COLUMN release_date FORMAT A12
COLUMN release_status FORMAT A12
COLUMN notification_method FORMAT A28
COLUMN asset_title FORMAT A30

SELECT 
    r.release_id,
    TO_CHAR(r.release_date, 'YYYY-MM-DD') AS release_date,
    r.status AS release_status,
    r.notification_method,
    a.title AS asset_title,
    NVL(p.title, 'Direct Asset Trigger') AS associated_plan
FROM SCHEDULED_RELEASES r
    LEFT JOIN DIGITAL_ASSETS a ON r.asset_id = a.asset_id
    LEFT JOIN LEGACY_PLANS p ON r.plan_id = p.plan_id
ORDER BY r.release_date ASC;

PROMPT
PROMPT =========================================================================
PROMPT   All Queries Executed Successfully.
PROMPT =========================================================================
