# Digital Legacy Vault – DA3

> **Graph-Native Digital Asset Succession and Estate Management System**  
> Built with Python, FastAPI, and Neo4j to demonstrate graph database design and relational-versus-graph querying for digital succession.

---

## 📌 Project Overview & Key Features

Digital Legacy Vault is an estate succession management platform designed to model and automate the distribution of digital assets upon specific life events or inactivity triggers.

- **Asset Cataloging:** Securely catalog crypto wallets, cloud archives, accounts, and intellectual property.
- **Beneficiaries & Executors:** Designate beneficiaries (`Nominee`) with proportional asset shares and appoint verified legal fiduciaries (`TrustedExecutor`).
- **Conditional Legacy Plans:** Establish succession plans triggered by verified legal events or inactivity thresholds.
- **Automated Releases:** Schedule time-delayed notifications and automated asset unlock protocols.
- **Interactive Graph Explorer:** Visualize graph topology with Vis.js, featuring real-time detection of orphaned (unallocated) assets.

---

## 💻 Technology Stack

- **Database:** Neo4j 5.x & Cypher Query Language
- **Backend:** Python 3.10+, FastAPI, Official Neo4j Driver (`neo4j`), Pydantic v2, Uvicorn
- **Frontend:** Single-page application using Vanilla HTML5, CSS3, JavaScript, and Vis.js
- **Testing & Tools:** Pytest, Docker Compose

---

## 🏛️ Project Architecture

The application uses a decoupled three-tier architecture:
1. **Frontend:** Lightweight browser UI with Vis.js interactive graph rendering.
2. **API & Logic:** FastAPI REST services handling data validation (Pydantic) and graph queries.
3. **Database:** Neo4j graph engine communicating over the binary Bolt protocol with schema uniqueness constraints and indexes.

---

## 📁 Project Structure

```
Digital_Legacy_Management_System/
├── app/                  # FastAPI backend (models, routes, database, config)
├── cypher/               # Cypher schema, seeds, and analytical queries
├── static/               # Frontend UI (HTML, CSS, JS, Vis.js visualizer)
├── tests/                # Automated pytest test suite
├── .env.example          # Environment variable template
├── docker-compose.yml    # Neo4j 5.x container configuration
├── requirements.txt      # Python dependencies
├── run.py                # Server launcher script
└── seed.py               # Standalone database seeding script
```

---

## ⚙️ Prerequisites

- **Python 3.10+** (`python --version`)
- **Docker Desktop** (or a local Neo4j Desktop 5.x instance / Neo4j AuraDB)

---

## 🚀 Windows PowerShell Setup & Run Instructions

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env from template
Copy-Item .env.example .env

# 4. Start Neo4j database container
docker compose up -d

# 5. Launch the application
python run.py
```

---

## 🔐 Neo4j Configuration (`.env.example`)

Set your database credentials in `.env` (copied from `.env.example`). Real credentials remain local and are never committed:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=neo4j
APP_HOST=127.0.0.1
APP_PORT=8000
```

---

## 🌱 Sample Data Seeding

Seed interconnected demonstration records into Neo4j:

- **Via PowerShell:**
  ```powershell
  python seed.py
  ```
- **Via Web Dashboard:** Click **"Seed Sample Data"** in the top navigation bar.

---

## 🌐 URLs & API Documentation

- **Web Dashboard:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474)

---

## 📊 Graph Schema & Main Relationships

### Entities (Nodes)
`User` (Owner), `DigitalAsset` (Asset), `Nominee` (Beneficiary), `TrustedExecutor` (Fiduciary), `LegacyPlan` (Rules), and `ScheduledRelease` (Trigger).

### Key Relationships
- `(:User)-[:HAS_ASSET]->(:DigitalAsset)`
- `(:User)-[:HAS_NOMINEE]->(:Nominee)`
- `(:User)-[:HAS_EXECUTOR]->(:TrustedExecutor)`
- `(:User)-[:HAS_PLAN]->(:LegacyPlan)`
- `(:Nominee)-[:DESIGNATED_FOR {share_pct}]->(:DigitalAsset)`
- `(:TrustedExecutor)-[:CAN_MANAGE]->(:DigitalAsset)`
- `(:LegacyPlan)-[:INCLUDES_ASSET]->(:DigitalAsset)`
- `(:LegacyPlan)-[:ASSIGNS_NOMINEE]->(:Nominee)`
- `(:LegacyPlan)-[:OVERSEEN_BY]->(:TrustedExecutor)`
- `(:LegacyPlan)-[:HAS_RELEASE]->(:ScheduledRelease)`

---

## 🧪 Automated Testing

Execute the test suite with pytest:

```powershell
pytest -v
```

*Verified: All 10 tests pass, validating endpoint routes, Pydantic schemas, Cypher scripts, and graph serialization.*

---

## 🛑 Stopping the Application

- **Stop Application:** Press `Ctrl + C` in the terminal running `run.py`.
- **Stop Neo4j Container:**
  ```powershell
  docker compose down
  ```
  *(Database state is safely persisted in the `neo4j_data` Docker volume).*

---

## 💡 Why Neo4j Over a Relational Database?

Digital succession involves highly interconnected, multi-hop relationships (*Owner → Plan → Asset → Nominee ← Executor*). In an RDBMS, querying multi-level inheritance chains requires recursive SQL `JOIN` operations that degrade with depth and scale.

Neo4j uses **index-free adjacency**, storing connections directly with nodes. This provides:
- **Fast Traversal:** Multi-hop inheritance paths resolve in milliseconds without expensive joins.
- **Expressive Queries:** Clean Cypher pattern-matching simplifies complex checks, such as finding unallocated orphan assets.
- **Schema Flexibility:** Easily adapt to new digital asset types and evolving succession rules.
