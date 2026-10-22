// ==============================================================================
// DIGITAL LEGACY VAULT - GRAPH TRAVERSAL & ANALYTICAL CYPHER QUERIES
// For DA3 Academic Evaluation & Technology Comparison
// ==============================================================================

// ------------------------------------------------------------------------------
// QUERY 1: Complete User Legacy Graph Traversal (3-Hop Deep Inheritance Walk)
// Demonstrates: Multi-hop graph traversal without costly SQL JOIN tables.
// Finds all assets, designated nominees, executors, and active release triggers for a user.
// ------------------------------------------------------------------------------
MATCH (u:User {id: $user_id})-[:HAS_PLAN]->(p:LegacyPlan)
OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
RETURN u.name AS Owner,
       p.title AS PlanTitle,
       p.trigger_condition AS TriggerCondition,
       collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type, value: a.estimated_value}) AS Assets,
       collect(DISTINCT {id: n.id, name: n.name, relation: n.relationship, share: des.share_pct}) AS Beneficiaries,
       collect(DISTINCT {id: e.id, name: e.name, status: e.verification_status}) AS Executors,
       collect(DISTINCT {id: r.id, date: r.release_date, status: r.status}) AS Releases;

// ------------------------------------------------------------------------------
// QUERY 2: Orphaned Digital Asset Detection (Anti-Pattern Query)
// Demonstrates: Graph pattern matching with WHERE NOT ()
// Finds high-priority assets that have no designated beneficiary or legacy plan.
// ------------------------------------------------------------------------------
MATCH (u:User)-[:HAS_ASSET]->(a:DigitalAsset)
WHERE NOT ( ()-[:DESIGNATED_FOR]->(a) )
  AND NOT ( ()-[:INCLUDES_ASSET]->(a) )
RETURN u.id AS OwnerId,
       u.name AS OwnerName,
       a.id AS AssetId,
       a.title AS AssetTitle,
       a.asset_type AS AssetType,
       a.priority AS Priority,
       'At Risk: No Beneficiary or Plan Assigned' AS RiskAssessment;

// ------------------------------------------------------------------------------
// QUERY 3: Executor Management Authority & Responsibility Matrix
// Demonstrates: Relationship property filtering and cross-entity auditing
// ------------------------------------------------------------------------------
MATCH (e:TrustedExecutor)-[m:CAN_MANAGE]->(a:DigitalAsset)<-[:HAS_ASSET]-(u:User)
RETURN e.id AS ExecutorId,
       e.name AS ExecutorName,
       e.verification_status AS VerificationStatus,
       m.auth_level AS AuthLevel,
       a.id AS AssetId,
       a.title AS AssetTitle,
       a.asset_type AS AssetType,
       u.name AS AssetOwner;

// ------------------------------------------------------------------------------
// QUERY 4: Nominee Inheritance Allocation Breakdown Across All Assets
// Demonstrates: Graph aggregation across heterogeneous relationship paths
// ------------------------------------------------------------------------------
MATCH (n:Nominee)-[d:DESIGNATED_FOR]->(a:DigitalAsset)<-[:HAS_ASSET]-(u:User)
RETURN n.id AS NomineeId,
       n.name AS NomineeName,
       n.relationship AS Relationship,
       u.name AS Owner,
       a.title AS AssetTitle,
       a.asset_type AS AssetType,
       d.share_pct AS SharePercentage,
       d.designation_type AS DesignationType;

// ------------------------------------------------------------------------------
// QUERY 5: Scheduled Release Pipeline Timeline
// Demonstrates: Temporal filtering and multi-node provenance
// ------------------------------------------------------------------------------
MATCH (r:ScheduledRelease)
OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
RETURN r.id AS ReleaseId,
       r.release_date AS ReleaseDate,
       r.status AS Status,
       r.notification_method AS NotificationMethod,
       p.title AS AssociatedPlan,
       u.name AS Owner,
       collect(DISTINCT a.title) AS ProtectedAssets,
       collect(DISTINCT n.name) AS DesignatedRecipients
ORDER BY r.release_date ASC;

// ------------------------------------------------------------------------------
// QUERY 6: Full Graph Schema Summary (For Interactive Visualization & Exploration)
// Demonstrates: Global node & relationship extraction with metadata
// ------------------------------------------------------------------------------
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN collect(DISTINCT {
         id: n.id,
         label: head(labels(n)),
         name: coalesce(n.name, n.title, n.id),
         details: n
       }) AS nodes,
       collect(DISTINCT {
         source: n.id,
         target: m.id,
         type: type(r),
         properties: properties(r)
       }) AS edges;
