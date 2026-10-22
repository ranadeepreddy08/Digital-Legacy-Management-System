# Demonstration & Viva Checklist: Digital Legacy Vault – DA3

Use this checklist to ensure a flawless live demonstration during your DBMS mini-project presentation or viva.

---

## Pre-Demo Setup (2 Minutes Before Demo)

1. **Verify Environment Configuration:**
   - Ensure `.env` exists in the project root with your Neo4j credentials.
2. **Start the Neo4j Database:**
   - *Option A (Docker):* Double-click `start_neo4j.bat` or run `docker-compose up -d`.
   - *Option B (Neo4j Desktop):* Open Neo4j Desktop and click **Start** on your project database.
   - *Option C (AuraDB):* Ensure your cloud instance is active and connected in `.env`.
3. **Launch the FastAPI Server:**
   - Run `python run.py` (or double-click `start_app.bat`).
   - Confirm server prints: `Server URL: http://127.0.0.1:8000`.
4. **Open Application in Browser:**
   - Open Chrome / Edge at `http://localhost:8000`.
   - Open a second tab at `http://localhost:8000/docs` (Swagger UI).
   - If using local Neo4j, open a third tab at `http://localhost:7474` (Neo4j Browser).

---

## Live Demonstration Script (Step-by-Step)

### Step 1: Neo4j Health Check & Connection Status
- **Action:** Show the top-right database status badge on the dashboard.
- **Talking Point:** *"The system connects directly to Neo4j via the official Python driver. As you can see, our `/api/health` endpoint confirms an active Bolt connection on port 7687 with Neo4j 5.x Community edition."*

### Step 2: One-Click Graph Seeding
- **Action:** Click the blue **"Seed Sample Data"** button in the header or quick action bar.
- **Talking Point:** *"This executes an idempotent Cypher script using `MERGE` statements and uniqueness constraints. It populates 5 users, 8 digital assets, 6 nominees, 3 executors, 4 legacy plans, and 4 scheduled releases along with over 30 directed relationships without creating duplicates."*
- **Verify:** Watch the toast notification show "Sample data seeded successfully!" and the 6 dashboard statistic cards immediately update to reflect the graph counts.

### Step 3: Dashboard Overview & Real-Time Stats
- **Action:** Walk through the 6 metric cards:
  - Users (5)
  - Digital Assets (8)
  - Nominees (6)
  - Trusted Executors (3)
  - Legacy Plans (4)
  - Scheduled Releases (4)
- **Action:** Point out the **Recent Additions** and **Upcoming Scheduled Releases** tables below the cards.
- **Talking Point:** *"Notice that every count and table is dynamically queried from Neo4j in real time—no hardcoded values or fake records."*

### Step 4: Digital Asset Management & Owner Linking
- **Action:** Navigate to **Digital Assets** in the sidebar.
- **Action:** Click **"+ Add Asset"** and fill out the modal form:
  - Title: `Solana NFT Portfolio`
  - Category: `Cryptocurrency`
  - Access Hint: `Phantom wallet seed in safe box B`
  - Priority: `High`
  - Value: `$15,000 USD`
  - Owner: Select `Eleanor Vance`
- **Action:** Click **Create Asset**.
- **Talking Point:** *"When we create this asset, Neo4j doesn't just create a node; it executes a Cypher `MERGE (u:User {id: $uid})-[:HAS_ASSET]->(a:DigitalAsset)` transaction, physically wiring the edge in the graph."*

### Step 5: Nominees & Beneficiary Designation
- **Action:** Click **View** on any asset to display its provenance modal.
- **Talking Point:** *"Notice how viewing an asset immediately displays its owner, designated beneficiary, and authorized legal executor in one single graph read."*
- **Action:** Navigate to **Nominees** and show the search filter by typing `Julian` or `Spouse`.

### Step 6: Legacy Plans & Conditional Trigger Protocols
- **Action:** Navigate to **Legacy Plans** in the sidebar.
- **Talking Point:** *"A Legacy Plan represents the legal and technical succession protocol. It binds together the owner, protected assets, beneficiaries, overseeing executors, and conditional release triggers."*
- **Action:** Click **View** on `Comprehensive Digital Asset & Crypto Succession Plan` to show the full governance subgraph.

### Step 7: Scheduled Release Pipeline & Status Transitions
- **Action:** Navigate to **Scheduled Releases**.
- **Action:** Click **Edit** on a release with status `Scheduled`.
- **Action:** Change status to `In Review` or `Released` and save.
- **Talking Point:** *"This allows estate executors to transition releases through legal review gates before assets are dispatched to beneficiaries."*

### Step 8: The Graph Explorer (Key Viva Highlight!)
- **Action:** Click **Graph Explorer** in the sidebar.
- **Talking Point:** *"Here is the full graph topology rendered with Vis.js directly from our `/api/graph/topology` endpoint."*
- **Demonstrate:**
  1. **Zoom & Pan:** Scroll to zoom in on clusters.
  2. **Node Click Inspection:** Click on `usr_001` (Eleanor Vance). Show the right-hand **Node Inspector** displaying all node properties and all incoming/outgoing graph connections (`-[:HAS_ASSET]->`, `-[:HAS_PLAN]->`).
  3. **Node Filter:** Filter by `DigitalAsset` or `Nominee` using the dropdown.
  4. **Detect Orphans Button:** Click the red **"Detect Orphans"** button.
     - **Explain:** *"This runs an anti-pattern Cypher query `MATCH (u)-[:HAS_ASSET]->(a) WHERE NOT ()-[:DESIGNATED_FOR]->(a)` to identify assets at risk. It instantly highlights `Personal Memoir & Journals` in red because it has no beneficiary assigned!"*

### Step 9: FastAPI Swagger Documentation (`/docs`)
- **Action:** Switch to the `/docs` browser tab.
- **Talking Point:** *"FastAPI automatically generates interactive OpenAPI documentation for all 25+ CRUD and graph endpoints. We can execute queries directly here with schema validation."*
- **Action:** Expand `GET /api/graph/orphans` and click **Try it out** -> **Execute**. Show the clean JSON response.

### Step 10: Safe Reset / Clear Database
- **Action:** Return to Dashboard and click **"Reset Database"** (with confirmation dialog).
- **Talking Point:** *"This executes `MATCH (n) DETACH DELETE n`, safely wiping nodes and edges for clean demonstration testing. We can click 'Seed Sample Data' again to immediately re-seed."*

---

## Quick Viva Preparation Answers

| Question | Short Answer |
|---|---|
| **What database engine is used?** | Neo4j Graph Database version 5.x via official `neo4j` Python driver and Bolt protocol. |
| **Why not MongoDB?** | MongoDB is a document store with no native graph relationship handling; traversing multi-hop inheritance requires multiple slow queries or heavy manual aggregation pipelines. Neo4j has index-free adjacency. |
| **How are relationships created?** | Using Cypher `MERGE (u)-[:HAS_ASSET]->(a)` with parameters to ensure idempotency. |
| **How are deletions safe?** | Using `MATCH (n {id: $id}) DETACH DELETE n`, which removes connected relationships before deleting the node to prevent orphan edge corruption. |
