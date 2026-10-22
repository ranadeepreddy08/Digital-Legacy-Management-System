# Digital Legacy Vault – Oracle SQL & SQL*Plus Guide

This directory contains relational database scripts for **Digital Legacy Vault (DA3)**, designed for and tested on **Oracle Database 11g Express Edition (XE)** using **SQL*Plus**.

---

## 📁 File Manifest

| File | Purpose | Key Concepts |
|---|---|---|
| [`01_schema.sql`](file:///c:/Users/N%20Ranadeep%20Reddy/Desktop/Projects/Digital_Legacy_Management_System/oracle_sql/01_schema.sql) | DDL schema creation | 8 tables, Primary Keys, Foreign Keys (`ON DELETE CASCADE`/`SET NULL`), Unique constraints, Check constraints, Sequence, Trigger |
| [`02_seed.sql`](file:///c:/Users/N%20Ranadeep%20Reddy/Desktop/Projects/Digital_Legacy_Management_System/oracle_sql/02_seed.sql) | Synthetic seed data | Realistic sample estate records matching the Neo4j entities; explicit `COMMIT` |
| [`03_queries.sql`](file:///c:/Users/N%20Ranadeep%20Reddy/Desktop/Projects/Digital_Legacy_Management_System/oracle_sql/03_queries.sql) | Analytical queries | Multi-table `INNER JOIN` (4-way), `LEFT JOIN`, `GROUP BY` aggregations, and orphan asset detection |
| [`04_transactions.sql`](file:///c:/Users/N%20Ranadeep%20Reddy/Desktop/Projects/Digital_Legacy_Management_System/oracle_sql/04_transactions.sql) | Transaction control | Atomic multi-table `INSERT`, `UPDATE`, `SAVEPOINT`, partial `ROLLBACK`, full `ROLLBACK`, and `COMMIT` |

---

## 🚀 Execution Instructions (Windows PowerShell)

### Step 1: Open PowerShell at Project Root
Open Windows PowerShell and navigate to the root directory of the project:

```powershell
cd "C:\Users\N Ranadeep Reddy\Desktop\Projects\Digital_Legacy_Management_System"
```

### Step 2: Launch SQL*Plus
Connect to your local Oracle database instance using your `LEGACY_USER` account:

```powershell
sqlplus LEGACY_USER
```
*(SQL\*Plus will securely prompt you to enter your password without displaying it on the screen).*

Alternatively, if connecting via TNS connection string:
```powershell
sqlplus LEGACY_USER@localhost:1521/XE
```

---

## 📜 Script Execution Order

Always execute the scripts in the following numbered order.

> **Windows Path Note:** In SQL*Plus, always use forward slashes (`/`) even on Windows. This prevents backslash escape issues.

### 1. Create Schema Tables & Constraints
```sql
@oracle_sql/01_schema.sql
```
*Creates all 8 relational tables (`USERS`, `DIGITAL_ASSETS`, `NOMINEES`, `TRUSTED_EXECUTORS`, `LEGACY_PLANS`, `ASSET_ALLOCATIONS`, `PLAN_ASSETS`, `SCHEDULED_RELEASES`), primary keys, foreign keys, sequences, and triggers.*

### 2. Populate Sample Records
```sql
@oracle_sql/02_seed.sql
```
*Inserts realistic parent and child records (matching the 5 users and 8 assets from the Neo4j dataset) and commits them.*

### 3. Run Analytical Queries & Reports
```sql
@oracle_sql/03_queries.sql
```
*Executes queries including multi-table joins, portfolio value aggregations, fiduciary oversight audits, and orphan asset detection.*

### 4. Run Transaction ACID Demonstrations
```sql
@oracle_sql/04_transactions.sql
```
*Tests atomic insertions, savepoints, partial rollbacks, and clean rollback/commit workflows using isolated test IDs (`demo_usr_999`).*

---

## 🔍 Verification Commands

Inside SQL*Plus, you can verify your database state anytime with these quick commands:

```sql
-- List all tables in your schema:
SELECT table_name FROM user_tables ORDER BY table_name;

-- Verify record counts:
SELECT 'USERS' AS tbl, COUNT(*) AS total FROM USERS
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
```

---

## 🚪 Exiting SQL*Plus

When you are done, exit SQL*Plus and return to PowerShell:
```sql
EXIT;
```
