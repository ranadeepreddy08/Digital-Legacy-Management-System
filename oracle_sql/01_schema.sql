-- =============================================================================
-- DIGITAL LEGACY VAULT - ORACLE 11g XE RELATIONAL SCHEMA
-- File: oracle_sql/01_schema.sql
-- Description: DDL definitions for tables, constraints, sequences, and triggers.
-- Compatible with: Oracle Database 11g Express Edition (Release 11.2.0.2.0)
-- =============================================================================

SET DEFINE OFF
SET ECHO ON
SET FEEDBACK ON
SET LINESIZE 150
SET PAGESIZE 50

PROMPT =========================================================================
PROMPT   DIGITAL LEGACY VAULT - Initializing Relational Schema
PROMPT =========================================================================

-- -----------------------------------------------------------------------------
-- Step 1: Drop existing tables and sequences cleanly (if they exist)
-- -----------------------------------------------------------------------------
PROMPT Dropping any pre-existing tables and sequences...

BEGIN
    -- Drop tables in child-to-parent order using CASCADE CONSTRAINTS
    FOR t IN (
        SELECT table_name 
        FROM all_tables 
        WHERE owner = SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')
          AND table_name IN (
            'SCHEDULED_RELEASES',
            'PLAN_ASSETS',
            'ASSET_ALLOCATIONS',
            'LEGACY_PLANS',
            'TRUSTED_EXECUTORS',
            'NOMINEES',
            'DIGITAL_ASSETS',
            'USERS'
        )
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
    END LOOP;

    -- Drop sequences if present
    FOR s IN (
        SELECT sequence_name 
        FROM all_sequences 
        WHERE sequence_owner = SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')
          AND sequence_name IN ('SEQ_ALLOCATION_ID')
    ) LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
END;
/

-- -----------------------------------------------------------------------------
-- Step 2: Create Core Tables (Parent Tables First)
-- -----------------------------------------------------------------------------

PROMPT Creating Table: USERS (Digital Estate Owners)...
CREATE TABLE USERS (
    user_id       VARCHAR2(20)  NOT NULL,
    name          VARCHAR2(100) NOT NULL,
    email         VARCHAR2(120) NOT NULL,
    phone         VARCHAR2(25),
    status        VARCHAR2(20)  DEFAULT 'Active' NOT NULL,
    created_at    DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_status CHECK (status IN ('Active', 'Inactive', 'Suspended'))
);

COMMENT ON TABLE USERS IS 'Registered digital estate owners managing their digital legacy assets.';
COMMENT ON COLUMN USERS.user_id IS 'Unique identifier for estate owner (e.g., usr_001).';
COMMENT ON COLUMN USERS.status IS 'Account status: Active, Inactive, or Suspended.';


PROMPT Creating Table: DIGITAL_ASSETS...
CREATE TABLE DIGITAL_ASSETS (
    asset_id          VARCHAR2(20)   NOT NULL,
    user_id           VARCHAR2(20)   NOT NULL,
    title             VARCHAR2(150)  NOT NULL,
    asset_type        VARCHAR2(50)   NOT NULL,
    access_info_hint  VARCHAR2(255),
    priority          VARCHAR2(20)   DEFAULT 'Medium' NOT NULL,
    estimated_value   NUMBER(12, 2)  DEFAULT 0 NOT NULL,
    created_at        DATE           DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_digital_assets PRIMARY KEY (asset_id),
    CONSTRAINT fk_assets_user FOREIGN KEY (user_id) 
        REFERENCES USERS(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_assets_priority CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT chk_assets_value CHECK (estimated_value >= 0)
);

COMMENT ON TABLE DIGITAL_ASSETS IS 'Catalog of user digital assets (crypto wallets, cloud storage, IP, accounts).';
COMMENT ON COLUMN DIGITAL_ASSETS.access_info_hint IS 'Secure encrypted location hint (e.g. Safe deposit box, 1Password vault).';


PROMPT Creating Table: NOMINEES (Beneficiaries)...
CREATE TABLE NOMINEES (
    nominee_id    VARCHAR2(20)  NOT NULL,
    user_id       VARCHAR2(20)  NOT NULL,
    name          VARCHAR2(100) NOT NULL,
    relationship  VARCHAR2(50)  NOT NULL,
    email         VARCHAR2(120) NOT NULL,
    phone         VARCHAR2(25),
    created_at    DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_nominees PRIMARY KEY (nominee_id),
    CONSTRAINT fk_nominees_user FOREIGN KEY (user_id) 
        REFERENCES USERS(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE NOMINEES IS 'Designated beneficiaries eligible to inherit digital assets.';


PROMPT Creating Table: TRUSTED_EXECUTORS (Legal Fiduciaries)...
CREATE TABLE TRUSTED_EXECUTORS (
    executor_id         VARCHAR2(20)  NOT NULL,
    user_id             VARCHAR2(20)  NOT NULL,
    name                VARCHAR2(100) NOT NULL,
    email               VARCHAR2(120) NOT NULL,
    phone               VARCHAR2(25),
    verification_status VARCHAR2(60)  DEFAULT 'Verified Notary' NOT NULL,
    role_description    VARCHAR2(150),
    created_at          DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_executors PRIMARY KEY (executor_id),
    CONSTRAINT fk_executors_user FOREIGN KEY (user_id) 
        REFERENCES USERS(user_id) ON DELETE CASCADE
);

COMMENT ON TABLE TRUSTED_EXECUTORS IS 'Certified notaries, attorneys, or corporate fiduciaries supervising execution.';


PROMPT Creating Table: LEGACY_PLANS (Succession Protocols)...
CREATE TABLE LEGACY_PLANS (
    plan_id           VARCHAR2(20)   NOT NULL,
    user_id           VARCHAR2(20)   NOT NULL,
    executor_id       VARCHAR2(20),
    title             VARCHAR2(150)  NOT NULL,
    trigger_condition VARCHAR2(150)  NOT NULL,
    status            VARCHAR2(30)   DEFAULT 'Active' NOT NULL,
    notes             VARCHAR2(500),
    created_at        DATE           DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_legacy_plans PRIMARY KEY (plan_id),
    CONSTRAINT fk_plans_user FOREIGN KEY (user_id) 
        REFERENCES USERS(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_plans_executor FOREIGN KEY (executor_id) 
        REFERENCES TRUSTED_EXECUTORS(executor_id) ON DELETE SET NULL,
    CONSTRAINT chk_plans_status CHECK (status IN ('Draft', 'Active', 'Pending Review', 'Executed', 'Cancelled'))
);

COMMENT ON TABLE LEGACY_PLANS IS 'Rules and legal conditions governing asset release upon life events or inactivity.';


-- -----------------------------------------------------------------------------
-- Step 3: Create Association & Junction Tables
-- -----------------------------------------------------------------------------

PROMPT Creating Sequence and Table: ASSET_ALLOCATIONS...
CREATE SEQUENCE SEQ_ALLOCATION_ID
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE TABLE ASSET_ALLOCATIONS (
    allocation_id     NUMBER        NOT NULL,
    asset_id          VARCHAR2(20)  NOT NULL,
    nominee_id        VARCHAR2(20)  NOT NULL,
    share_pct         NUMBER(3)     DEFAULT 100 NOT NULL,
    designation_type  VARCHAR2(50)  DEFAULT 'Primary Beneficiary' NOT NULL,
    assigned_at       DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_asset_allocations PRIMARY KEY (allocation_id),
    CONSTRAINT fk_alloc_asset FOREIGN KEY (asset_id) 
        REFERENCES DIGITAL_ASSETS(asset_id) ON DELETE CASCADE,
    CONSTRAINT fk_alloc_nominee FOREIGN KEY (nominee_id) 
        REFERENCES NOMINEES(nominee_id) ON DELETE CASCADE,
    CONSTRAINT uq_asset_nominee UNIQUE (asset_id, nominee_id),
    CONSTRAINT chk_alloc_share CHECK (share_pct BETWEEN 1 AND 100)
);

-- Trigger for Oracle 11g auto-populating allocation_id if omitted
CREATE OR REPLACE TRIGGER trg_alloc_id
BEFORE INSERT ON ASSET_ALLOCATIONS
FOR EACH ROW
WHEN (NEW.allocation_id IS NULL)
BEGIN
    SELECT SEQ_ALLOCATION_ID.NEXTVAL INTO :NEW.allocation_id FROM dual;
END;
/

COMMENT ON TABLE ASSET_ALLOCATIONS IS 'M:N relationship linking Nominees to Digital Assets with percentage distribution.';


PROMPT Creating Table: PLAN_ASSETS (M:N Legacy Plan <-> Digital Assets)...
CREATE TABLE PLAN_ASSETS (
    plan_id     VARCHAR2(20) NOT NULL,
    asset_id    VARCHAR2(20) NOT NULL,
    added_at    DATE         DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_plan_assets PRIMARY KEY (plan_id, asset_id),
    CONSTRAINT fk_pa_plan FOREIGN KEY (plan_id) 
        REFERENCES LEGACY_PLANS(plan_id) ON DELETE CASCADE,
    CONSTRAINT fk_pa_asset FOREIGN KEY (asset_id) 
        REFERENCES DIGITAL_ASSETS(asset_id) ON DELETE CASCADE
);

COMMENT ON TABLE PLAN_ASSETS IS 'Associates which digital assets are included under each succession plan.';


PROMPT Creating Table: SCHEDULED_RELEASES (Execution Schedule)...
CREATE TABLE SCHEDULED_RELEASES (
    release_id           VARCHAR2(20)  NOT NULL,
    plan_id              VARCHAR2(20),
    asset_id             VARCHAR2(20),
    release_date         DATE          NOT NULL,
    status               VARCHAR2(30)  DEFAULT 'Scheduled' NOT NULL,
    notification_method  VARCHAR2(100) NOT NULL,
    notes                VARCHAR2(500),
    created_at           DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_scheduled_releases PRIMARY KEY (release_id),
    CONSTRAINT fk_releases_plan FOREIGN KEY (plan_id) 
        REFERENCES LEGACY_PLANS(plan_id) ON DELETE SET NULL,
    CONSTRAINT fk_releases_asset FOREIGN KEY (asset_id) 
        REFERENCES DIGITAL_ASSETS(asset_id) ON DELETE CASCADE,
    CONSTRAINT chk_releases_status CHECK (status IN ('Scheduled', 'In Review', 'Released', 'Cancelled'))
);

COMMENT ON TABLE SCHEDULED_RELEASES IS 'Timeline of trigger events, notifications, and unlock dispatches.';

-- -----------------------------------------------------------------------------
-- Step 4: Verification of Created Schema
-- -----------------------------------------------------------------------------
PROMPT
PROMPT =========================================================================
PROMPT   Schema Creation Complete. Verifying Created Tables:
PROMPT =========================================================================

COLUMN table_name FORMAT A25
COLUMN status FORMAT A10

SELECT table_name, status 
FROM user_tables 
ORDER BY table_name;

PROMPT
PROMPT Schema is ready. Proceed to execute: @oracle_sql/02_seed.sql
