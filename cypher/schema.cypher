// ==============================================================================
// DIGITAL LEGACY VAULT - NEO4J SCHEMA DEFINITION
// Uniqueness Constraints and Performance Indexes
// ==============================================================================

// 1. Uniqueness Constraints on Entity Identifiers
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT asset_id_unique IF NOT EXISTS
FOR (a:DigitalAsset) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT nominee_id_unique IF NOT EXISTS
FOR (n:Nominee) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT executor_id_unique IF NOT EXISTS
FOR (e:TrustedExecutor) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT plan_id_unique IF NOT EXISTS
FOR (p:LegacyPlan) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT release_id_unique IF NOT EXISTS
FOR (r:ScheduledRelease) REQUIRE r.id IS UNIQUE;

// 2. Performance & Search Indexes
CREATE INDEX user_email_idx IF NOT EXISTS
FOR (u:User) ON (u.email);

CREATE INDEX asset_type_idx IF NOT EXISTS
FOR (a:DigitalAsset) ON (a.asset_type);

CREATE INDEX asset_title_idx IF NOT EXISTS
FOR (a:DigitalAsset) ON (a.title);

CREATE INDEX release_date_idx IF NOT EXISTS
FOR (r:ScheduledRelease) ON (r.release_date);

CREATE INDEX release_status_idx IF NOT EXISTS
FOR (r:ScheduledRelease) ON (r.status);
