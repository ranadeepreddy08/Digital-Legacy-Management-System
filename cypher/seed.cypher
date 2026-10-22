// ==============================================================================
// DIGITAL LEGACY VAULT - SEED SCRIPT (CYPHER)
// Idempotent data seeding using MERGE statements
// ==============================================================================

// 1. Create Users
MERGE (u1:User {id: 'usr_001'})
ON CREATE SET u1.name = 'Eleanor Vance',
              u1.email = 'eleanor.vance@legacyvault.io',
              u1.phone = '+1-555-0101',
              u1.status = 'Active',
              u1.created_at = '2026-01-15T09:30:00Z';

MERGE (u2:User {id: 'usr_002'})
ON CREATE SET u2.name = 'Marcus Chen',
              u2.email = 'marcus.chen@techcorp.com',
              u2.phone = '+1-555-0102',
              u2.status = 'Active',
              u2.created_at = '2026-02-10T14:20:00Z';

MERGE (u3:User {id: 'usr_003'})
ON CREATE SET u3.name = 'Sophia Rodriguez',
              u3.email = 'sophia.r@bioresearch.org',
              u3.phone = '+1-555-0103',
              u3.status = 'Active',
              u3.created_at = '2026-03-01T11:15:00Z';

MERGE (u4:User {id: 'usr_004'})
ON CREATE SET u4.name = 'Dr. Arvind Kumar',
              u4.email = 'arvind.kumar@univ.edu',
              u4.phone = '+91-98765-43210',
              u4.status = 'Active',
              u4.created_at = '2026-03-12T16:45:00Z';

MERGE (u5:User {id: 'usr_005'})
ON CREATE SET u5.name = 'Chloe Bennet',
              u5.email = 'chloe.bennet@artstudio.design',
              u5.phone = '+44-20-7946-0912',
              u5.status = 'Inactive',
              u5.created_at = '2026-04-05T08:00:00Z';

// 2. Create Digital Assets
MERGE (a1:DigitalAsset {id: 'ast_001'})
ON CREATE SET a1.title = 'Cold Storage Bitcoin Wallet',
              a1.asset_type = 'Cryptocurrency',
              a1.access_info_encrypted_hint = 'Hardware Ledger seed phrase stored in Safe Deposit Box #402',
              a1.priority = 'Critical',
              a1.estimated_value = '$125,000 USD',
              a1.created_at = '2026-01-16T10:00:00Z';

MERGE (a2:DigitalAsset {id: 'ast_002'})
ON CREATE SET a2.title = 'Family Photo Archive (NextCloud)',
              a2.asset_type = 'Cloud Storage',
              a2.access_info_encrypted_hint = 'Encrypted volume credentials in 1Password shared family vault',
              a2.priority = 'High',
              a2.estimated_value = 'Priceless / Sentimental',
              a2.created_at = '2026-01-16T10:15:00Z';

MERGE (a3:DigitalAsset {id: 'ast_003'})
ON CREATE SET a3.title = 'GitHub Pro Repositories & Patents',
              a3.asset_type = 'Intellectual Property',
              a3.access_info_encrypted_hint = 'GPG signing key backup stored on YubiKey 5C NFC',
              a3.priority = 'High',
              a3.estimated_value = '$50,000 USD',
              a3.created_at = '2026-02-12T11:00:00Z';

MERGE (a4:DigitalAsset {id: 'ast_004'})
ON CREATE SET a4.title = 'E-Trade Investment Portfolio',
              a4.asset_type = 'Financial Account',
              a4.access_info_encrypted_hint = 'Account number ending in 8841; Transfer on Death verified',
              a4.priority = 'Critical',
              a4.estimated_value = '$340,000 USD',
              a4.created_at = '2026-02-12T11:30:00Z';

MERGE (a5:DigitalAsset {id: 'ast_005'})
ON CREATE SET a5.title = 'Genomics Research Data Vault',
              a5.asset_type = 'Research Archive',
              a5.access_info_encrypted_hint = 'AWS S3 bucket with Glacier vault lock and MFA delete policy',
              a5.priority = 'High',
              a5.estimated_value = 'Academic Heritage',
              a5.created_at = '2026-03-02T12:00:00Z';

MERGE (a6:DigitalAsset {id: 'ast_006'})
ON CREATE SET a6.title = 'Primary Domain Portfolio (.ai & .io)',
              a6.asset_type = 'Domain Portfolio',
              a6.access_info_encrypted_hint = 'Cloudflare Registrar account with hardware security key',
              a6.priority = 'Medium',
              a6.estimated_value = '$18,000 USD',
              a6.created_at = '2026-03-15T09:00:00Z';

MERGE (a7:DigitalAsset {id: 'ast_007'})
ON CREATE SET a7.title = 'YouTube Creator Channel Archive',
              a7.asset_type = 'Social Media',
              a7.access_info_encrypted_hint = 'Google Brand Account legacy contact set to executor email',
              a7.priority = 'Medium',
              a7.estimated_value = '$24,000 Annual Revenue',
              a7.created_at = '2026-04-06T10:00:00Z';

MERGE (a8:DigitalAsset {id: 'ast_008'})
ON CREATE SET a8.title = 'Personal Memoir & Journals',
              a8.asset_type = 'Personal Document',
              a8.access_info_encrypted_hint = 'VeraCrypt encrypted archive on backup USB Drive #2',
              a8.priority = 'High',
              a8.estimated_value = 'Sentimental',
              a8.created_at = '2026-04-06T10:30:00Z';

// 3. Create Nominees
MERGE (n1:Nominee {id: 'nom_001'})
ON CREATE SET n1.name = 'Julian Vance',
              n1.relationship = 'Spouse',
              n1.email = 'julian.vance@gmail.com',
              n1.phone = '+1-555-0201',
              n1.allocation_percentage = 60,
              n1.created_at = '2026-01-17T09:00:00Z';

MERGE (n2:Nominee {id: 'nom_002'})
ON CREATE SET n2.name = 'Clara Vance',
              n2.relationship = 'Daughter',
              n2.email = 'clara.vance@stanford.edu',
              n2.phone = '+1-555-0202',
              n2.allocation_percentage = 40,
              n2.created_at = '2026-01-17T09:15:00Z';

MERGE (n3:Nominee {id: 'nom_003'})
ON CREATE SET n3.name = 'David Chen',
              n3.relationship = 'Brother',
              n3.email = 'david.chen@technova.co',
              n3.phone = '+1-555-0203',
              n3.allocation_percentage = 100,
              n3.created_at = '2026-02-14T10:00:00Z';

MERGE (n4:Nominee {id: 'nom_004'})
ON CREATE SET n4.name = 'Open Science Foundation',
              n4.relationship = 'Institutional Beneficiary',
              n4.email = 'grants@openscience.org',
              n4.phone = '+1-800-555-0199',
              n4.allocation_percentage = 100,
              n4.created_at = '2026-03-05T14:00:00Z';

MERGE (n5:Nominee {id: 'nom_005'})
ON CREATE SET n5.name = 'Priya Kumar',
              n5.relationship = 'Sister',
              n5.email = 'priya.k@delhi.ac.in',
              n5.phone = '+91-98111-22334',
              n5.allocation_percentage = 100,
              n5.created_at = '2026-03-18T11:00:00Z';

MERGE (n6:Nominee {id: 'nom_006'})
ON CREATE SET n6.name = 'Leo Bennet-Hall',
              n6.relationship = 'Nephew',
              n6.email = 'leo.b@londonart.ac.uk',
              n6.phone = '+44-20-7946-0111',
              n6.allocation_percentage = 100,
              n6.created_at = '2026-04-07T12:00:00Z';

// 4. Create Trusted Executors
MERGE (e1:TrustedExecutor {id: 'exe_001'})
ON CREATE SET e1.name = 'Robert Sterling, Esq.',
              e1.email = 'sterling@heritage-law.com',
              e1.phone = '+1-555-0301',
              e1.verification_status = 'Verified Notary & Attorney',
              e1.role_description = 'Legal Executor & Estate Counsel',
              e1.created_at = '2026-01-18T10:00:00Z';

MERGE (e2:TrustedExecutor {id: 'exe_002'})
ON CREATE SET e2.name = 'Apex Trust & Fiduciary Services',
              e2.email = 'digitalestates@apextrust.com',
              e2.phone = '+1-888-555-0400',
              e2.verification_status = 'Licensed Corporate Fiduciary',
              e2.role_description = 'Institutional Digital Asset Trustee',
              e2.created_at = '2026-02-15T11:00:00Z';

MERGE (e3:TrustedExecutor {id: 'exe_003'})
ON CREATE SET e3.name = 'Prof. Vikram Sen',
              e3.email = 'vikram.sen@univ-dean.edu',
              e3.phone = '+91-99887-66554',
              e3.verification_status = 'Academic Peer Verified',
              e3.role_description = 'Scientific Data Custodian',
              e3.created_at = '2026-03-19T14:00:00Z';

// 5. Create Legacy Plans
MERGE (p1:LegacyPlan {id: 'pln_001'})
ON CREATE SET p1.title = 'Comprehensive Digital Asset & Crypto Succession Plan',
              p1.trigger_condition = 'Legal Death Certificate Verification',
              p1.status = 'Active',
              p1.notes = 'Release Bitcoin keys to Julian and Photo Archive to Clara via Attorney Sterling.',
              p1.created_at = '2026-01-20T10:00:00Z';

MERGE (p2:LegacyPlan {id: 'pln_002'})
ON CREATE SET p2.title = 'Tech Founder Intellectual Property & Equity Plan',
              p2.trigger_condition = 'Inactivity > 180 Days with Dual Notary Confirmation',
              p2.status = 'Active',
              p2.notes = 'Transfer repository access and investment funds to David Chen.',
              p2.created_at = '2026-02-20T15:00:00Z';

MERGE (p3:LegacyPlan {id: 'pln_003'})
ON CREATE SET p3.title = 'Open Science Public Archive Donation Plan',
              p3.trigger_condition = 'Certified Incapacitation or Death',
              p3.status = 'Pending Review',
              p3.notes = 'Publish genomics data under Creative Commons 4.0 via Open Science Foundation.',
              p3.created_at = '2026-03-22T09:30:00Z';

MERGE (p4:LegacyPlan {id: 'pln_004'})
ON CREATE SET p4.title = 'Family Memoirs & Memorial Social Plan',
              p4.trigger_condition = 'Executor Verification and Request',
              p4.status = 'Draft',
              p4.notes = 'Convert YouTube to memorial channel and send memoirs to nephew Leo.',
              p4.created_at = '2026-04-08T14:00:00Z';

// 6. Create Scheduled Releases
MERGE (r1:ScheduledRelease {id: 'rel_001'})
ON CREATE SET r1.release_date = '2026-12-01T00:00:00Z',
              r1.status = 'Scheduled',
              r1.notification_method = 'Encrypted Email + SMS OTP',
              r1.notes = 'Automated transfer trigger upon non-response to annual heartbeat ping',
              r1.created_at = '2026-01-22T11:00:00Z';

MERGE (r2:ScheduledRelease {id: 'rel_002'})
ON CREATE SET r2.release_date = '2027-01-15T00:00:00Z',
              r2.status = 'Scheduled',
              r2.notification_method = 'Notary In-Person Verification',
              r2.notes = 'Crypto cold wallet multi-sig key disclosure',
              r2.created_at = '2026-02-25T14:00:00Z';

MERGE (r3:ScheduledRelease {id: 'rel_003'})
ON CREATE SET r3.release_date = '2026-11-15T00:00:00Z',
              r3.status = 'In Review',
              r3.notification_method = 'Institutional Grant Portal Notice',
              r3.notes = 'Pending peer review approval before open-sourcing genomic vault',
              r3.created_at = '2026-03-25T16:00:00Z';

MERGE (r4:ScheduledRelease {id: 'rel_004'})
ON CREATE SET r4.release_date = '2026-05-01T00:00:00Z',
              r4.status = 'Released',
              r4.notification_method = 'Automated Webhook & Archival Dispatch',
              r4.notes = 'Initial public domain name DNS redirection executed',
              r4.created_at = '2026-04-10T11:00:00Z';

// ==============================================================================
// 7. Establish Relationships Between Entities
// ==============================================================================

// User 1 Relationships (Eleanor Vance)
MATCH (u:User {id: 'usr_001'}), (a:DigitalAsset {id: 'ast_001'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_001'}), (a:DigitalAsset {id: 'ast_002'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_001'}), (n:Nominee {id: 'nom_001'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (u:User {id: 'usr_001'}), (n:Nominee {id: 'nom_002'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (u:User {id: 'usr_001'}), (e:TrustedExecutor {id: 'exe_001'}) MERGE (u)-[:HAS_EXECUTOR]->(e);
MATCH (u:User {id: 'usr_001'}), (p:LegacyPlan {id: 'pln_001'}) MERGE (u)-[:HAS_PLAN]->(p);

// Nominee Beneficiary Designations for User 1
MATCH (n:Nominee {id: 'nom_001'}), (a:DigitalAsset {id: 'ast_001'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 100, designation_type: 'Primary Beneficiary'}]->(a);

MATCH (n:Nominee {id: 'nom_002'}), (a:DigitalAsset {id: 'ast_002'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 100, designation_type: 'Family Custodian'}]->(a);

// Executor Authority for User 1
MATCH (e:TrustedExecutor {id: 'exe_001'}), (a:DigitalAsset {id: 'ast_001'})
MERGE (e)-[:CAN_MANAGE {auth_level: 'Full Administration', verified: true}]->(a);

MATCH (e:TrustedExecutor {id: 'exe_001'}), (a:DigitalAsset {id: 'ast_002'})
MERGE (e)-[:CAN_MANAGE {auth_level: 'Auditing & Transfer', verified: true}]->(a);

// Plan Associations for Plan 1
MATCH (p:LegacyPlan {id: 'pln_001'}), (a:DigitalAsset {id: 'ast_001'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
MATCH (p:LegacyPlan {id: 'pln_001'}), (a:DigitalAsset {id: 'ast_002'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
MATCH (p:LegacyPlan {id: 'pln_001'}), (n:Nominee {id: 'nom_001'}) MERGE (p)-[:ASSIGNS_NOMINEE]->(n);
MATCH (p:LegacyPlan {id: 'pln_001'}), (n:Nominee {id: 'nom_002'}) MERGE (p)-[:ASSIGNS_NOMINEE]->(n);
MATCH (p:LegacyPlan {id: 'pln_001'}), (e:TrustedExecutor {id: 'exe_001'}) MERGE (p)-[:OVERSEEN_BY]->(e);
MATCH (p:LegacyPlan {id: 'pln_001'}), (r:ScheduledRelease {id: 'rel_001'}) MERGE (p)-[:HAS_RELEASE]->(r);
MATCH (a:DigitalAsset {id: 'ast_001'}), (r:ScheduledRelease {id: 'rel_001'}) MERGE (a)-[:HAS_RELEASE]->(r);

// User 2 Relationships (Marcus Chen)
MATCH (u:User {id: 'usr_002'}), (a:DigitalAsset {id: 'ast_003'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_002'}), (a:DigitalAsset {id: 'ast_004'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_002'}), (n:Nominee {id: 'nom_003'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (u:User {id: 'usr_002'}), (e:TrustedExecutor {id: 'exe_002'}) MERGE (u)-[:HAS_EXECUTOR]->(e);
MATCH (u:User {id: 'usr_002'}), (p:LegacyPlan {id: 'pln_002'}) MERGE (u)-[:HAS_PLAN]->(p);

MATCH (n:Nominee {id: 'nom_003'}), (a:DigitalAsset {id: 'ast_003'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 50, designation_type: 'Co-Beneficiary'}]->(a);

MATCH (n:Nominee {id: 'nom_003'}), (a:DigitalAsset {id: 'ast_004'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 100, designation_type: 'Sole Beneficiary'}]->(a);

MATCH (e:TrustedExecutor {id: 'exe_002'}), (a:DigitalAsset {id: 'ast_004'})
MERGE (e)-[:CAN_MANAGE {auth_level: 'Financial Fiduciary', verified: true}]->(a);

MATCH (p:LegacyPlan {id: 'pln_002'}), (a:DigitalAsset {id: 'ast_003'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
MATCH (p:LegacyPlan {id: 'pln_002'}), (a:DigitalAsset {id: 'ast_004'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
MATCH (p:LegacyPlan {id: 'pln_002'}), (n:Nominee {id: 'nom_003'}) MERGE (p)-[:ASSIGNS_NOMINEE]->(n);
MATCH (p:LegacyPlan {id: 'pln_002'}), (e:TrustedExecutor {id: 'exe_002'}) MERGE (p)-[:OVERSEEN_BY]->(e);
MATCH (p:LegacyPlan {id: 'pln_002'}), (r:ScheduledRelease {id: 'rel_002'}) MERGE (p)-[:HAS_RELEASE]->(r);

// User 3 Relationships (Sophia Rodriguez)
MATCH (u:User {id: 'usr_003'}), (a:DigitalAsset {id: 'ast_005'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_003'}), (n:Nominee {id: 'nom_004'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (u:User {id: 'usr_003'}), (e:TrustedExecutor {id: 'exe_003'}) MERGE (u)-[:HAS_EXECUTOR]->(e);
MATCH (u:User {id: 'usr_003'}), (p:LegacyPlan {id: 'pln_003'}) MERGE (u)-[:HAS_PLAN]->(p);

MATCH (n:Nominee {id: 'nom_004'}), (a:DigitalAsset {id: 'ast_005'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 100, designation_type: 'Public Trust'}]->(a);

MATCH (e:TrustedExecutor {id: 'exe_003'}), (a:DigitalAsset {id: 'ast_005'})
MERGE (e)-[:CAN_MANAGE {auth_level: 'Scientific Peer Custody', verified: true}]->(a);

MATCH (p:LegacyPlan {id: 'pln_003'}), (a:DigitalAsset {id: 'ast_005'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
MATCH (p:LegacyPlan {id: 'pln_003'}), (n:Nominee {id: 'nom_004'}) MERGE (p)-[:ASSIGNS_NOMINEE]->(n);
MATCH (p:LegacyPlan {id: 'pln_003'}), (e:TrustedExecutor {id: 'exe_003'}) MERGE (p)-[:OVERSEEN_BY]->(e);
MATCH (p:LegacyPlan {id: 'pln_003'}), (r:ScheduledRelease {id: 'rel_003'}) MERGE (p)-[:HAS_RELEASE]->(r);

// User 4 Relationships (Dr. Arvind Kumar)
MATCH (u:User {id: 'usr_004'}), (a:DigitalAsset {id: 'ast_006'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_004'}), (n:Nominee {id: 'nom_005'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (n:Nominee {id: 'nom_005'}), (a:DigitalAsset {id: 'ast_006'})
MERGE (n)-[:DESIGNATED_FOR {share_pct: 100, designation_type: 'Primary Beneficiary'}]->(a);
MATCH (a:DigitalAsset {id: 'ast_006'}), (r:ScheduledRelease {id: 'rel_004'}) MERGE (a)-[:HAS_RELEASE]->(r);

// User 5 Relationships (Chloe Bennet - intentional orphan asset demo)
MATCH (u:User {id: 'usr_005'}), (a:DigitalAsset {id: 'ast_007'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_005'}), (a:DigitalAsset {id: 'ast_008'}) MERGE (u)-[:HAS_ASSET]->(a);
MATCH (u:User {id: 'usr_005'}), (n:Nominee {id: 'nom_006'}) MERGE (u)-[:HAS_NOMINEE]->(n);
MATCH (u:User {id: 'usr_005'}), (p:LegacyPlan {id: 'pln_004'}) MERGE (u)-[:HAS_PLAN]->(p);
MATCH (p:LegacyPlan {id: 'pln_004'}), (a:DigitalAsset {id: 'ast_007'}) MERGE (p)-[:INCLUDES_ASSET]->(a);
// Note: ast_008 has no nominee designated and no plan, demonstrating an orphaned asset for detection!
