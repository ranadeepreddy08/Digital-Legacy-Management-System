from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query

router = APIRouter()

# Clean, professional color palette for graph node categories
LABEL_COLORS = {
    "User": {"background": "#eff6ff", "border": "#2563eb", "text": "#1e40af"},            # Subtle Blue
    "DigitalAsset": {"background": "#f0fdf4", "border": "#16a34a", "text": "#166534"},    # Subtle Green
    "Nominee": {"background": "#fdf4ff", "border": "#c026d3", "text": "#86198f"},         # Subtle Purple
    "TrustedExecutor": {"background": "#fffbeb", "border": "#d97706", "text": "#92400e"}, # Subtle Amber
    "LegacyPlan": {"background": "#f8fafc", "border": "#475569", "text": "#1e293b"},      # Slate
    "ScheduledRelease": {"background": "#fef2f2", "border": "#dc2626", "text": "#991b1b"} # Subtle Red
}

@router.get("/topology", summary="Get Full Graph Topology for Interactive Visualization")
def get_graph_topology(
    label: Optional[str] = Query(None, description="Filter by node label"),
    limit: int = Query(200, ge=10, le=1000, description="Max nodes to fetch")
):
    """
    Extracts nodes and edges formatted for Vis.js / Canvas visualization.
    Includes node labels, custom styles, edge types, and properties.
    """
    label_filter = f":{label}" if label else ""
    query = f"""
    MATCH (n{label_filter})
    WITH n LIMIT $limit
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN collect(DISTINCT {{
             id: n.id,
             label: head(labels(n)),
             name: coalesce(n.title, n.name, n.id),
             properties: properties(n)
           }}) AS nodes,
           collect(DISTINCT CASE WHEN m IS NOT NULL THEN {{
             id: id(r),
             from: n.id,
             to: m.id,
             label: type(r),
             properties: properties(r)
           }} ELSE NULL END) AS edges
    """
    results = run_query(query, {"limit": limit})
    if not results:
        return {"nodes": [], "edges": []}

    raw_nodes = results[0].get("nodes", [])
    raw_edges = [e for e in results[0].get("edges", []) if e is not None]

    # Format nodes for Vis.js with clean minimalist colors
    formatted_nodes = []
    seen_ids = set()
    for node in raw_nodes:
        nid = node.get("id")
        if not nid or nid in seen_ids:
            continue
        seen_ids.add(nid)
        lbl = node.get("label", "Node")
        palette = LABEL_COLORS.get(lbl, {"background": "#f1f5f9", "border": "#64748b", "text": "#0f172a"})
        formatted_nodes.append({
            "id": nid,
            "label": f"{node.get('name')}\n[{lbl}]",
            "title": f"<b>{lbl}: {node.get('name')}</b><br>ID: {nid}",
            "group": lbl,
            "color": {
                "background": palette["background"],
                "border": palette["border"],
                "highlight": {"background": "#ffffff", "border": palette["border"]}
            },
            "font": {"color": palette["text"], "size": 12, "face": "system-ui, sans-serif"},
            "shape": "box",
            "margin": 10,
            "borderWidth": 1.5,
            "raw": node.get("properties", {})
        })

    # Format edges for Vis.js with clean arrows
    formatted_edges = []
    for edge in raw_edges:
        formatted_edges.append({
            "id": f"{edge.get('from')}->{edge.get('to')}:{edge.get('label')}",
            "from": edge.get("from"),
            "to": edge.get("to"),
            "label": edge.get("label"),
            "arrows": "to",
            "color": {"color": "#94a3b8", "highlight": "#2563eb"},
            "font": {"size": 10, "align": "middle", "color": "#64748b"},
            "smooth": {"type": "curvedCW", "roundness": 0.15},
            "properties": edge.get("properties", {})
        })

    return {"nodes": formatted_nodes, "edges": formatted_edges}

@router.get("/user/{user_id}", summary="Get Subgraph Centered on a Specific User")
def get_user_subgraph(user_id: str):
    """
    Returns ego-network around a user up to 3 hops deep.
    """
    query = """
    MATCH (u:User {id: $user_id})
    OPTIONAL MATCH path = (u)-[*1..3]-(connected)
    WITH u, collect(path) AS paths
    RETURN u, paths
    """
    # Alternative direct traversal for high reliability
    traversal_query = """
    MATCH (u:User {id: $user_id})
    OPTIONAL MATCH (u)-[r1:HAS_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (u)-[r2:HAS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (u)-[r3:HAS_EXECUTOR]->(e:TrustedExecutor)
    OPTIONAL MATCH (u)-[r4:HAS_PLAN]->(p:LegacyPlan)
    OPTIONAL MATCH (n)-[r5:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (e)-[r6:CAN_MANAGE]->(a)
    OPTIONAL MATCH (p)-[r7:INCLUDES_ASSET]->(a)
    OPTIONAL MATCH (p)-[r8:ASSIGNS_NOMINEE]->(n)
    OPTIONAL MATCH (p)-[r9:OVERSEEN_BY]->(e)
    OPTIONAL MATCH (p)-[r10:HAS_RELEASE]->(rel:ScheduledRelease)
    RETURN {
      user: properties(u),
      assets: collect(DISTINCT properties(a)),
      nominees: collect(DISTINCT properties(n)),
      executors: collect(DISTINCT properties(e)),
      plans: collect(DISTINCT properties(p)),
      releases: collect(DISTINCT properties(rel))
    } AS ego_network
    """
    results = run_query(traversal_query, {"user_id": user_id})
    if not results or not results[0].get("ego_network", {}).get("user"):
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found.")
    return results[0]["ego_network"]

@router.get("/orphans", summary="Detect Orphaned Digital Assets (Anti-Pattern Query)")
def detect_orphaned_assets():
    """
    Identifies digital assets without any designated beneficiary nominee
    or included in any legacy plan.
    """
    query = """
    MATCH (u:User)-[:HAS_ASSET]->(a:DigitalAsset)
    WHERE NOT ( ()-[:DESIGNATED_FOR]->(a) )
      AND NOT ( ()-[:INCLUDES_ASSET]->(a) )
    RETURN u.id AS owner_id,
           u.name AS owner_name,
           a.id AS asset_id,
           a.title AS asset_title,
           a.asset_type AS asset_type,
           a.priority AS priority,
           a.estimated_value AS estimated_value,
           'High Risk: No Nominee Designated & No Plan Assigned' AS risk_alert
    """
    return run_query(query)

@router.get("/traversals/inheritance", summary="Full Multi-Hop Inheritance Chain Traversal")
def get_inheritance_chains():
    """
    Multi-hop graph query demonstrating path traversal:
    (User)-[:HAS_PLAN]->(Plan)-[:INCLUDES_ASSET]->(Asset)<-[:DESIGNATED_FOR]-(Nominee)
    """
    query = """
    MATCH (u:User)-[:HAS_PLAN]->(p:LegacyPlan)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN u.name AS owner,
           p.title AS plan_title,
           p.trigger_condition AS trigger_condition,
           a.title AS asset_title,
           a.asset_type AS asset_type,
           coalesce(n.name, 'Unassigned') AS beneficiary,
           coalesce(n.relationship, 'N/A') AS relationship,
           coalesce(des.share_pct, 100) AS share_pct,
           coalesce(e.name, 'None Assigned') AS executor,
           coalesce(r.release_date, 'Not Scheduled') AS release_date
    ORDER BY u.name, p.title
    """
    return run_query(query)

@router.get("/traversals/executors", summary="Executor Authorization & Oversight Matrix")
def get_executor_oversight_matrix():
    """
    Queries executor management authority links and cross-user oversight.
    """
    query = """
    MATCH (e:TrustedExecutor)-[m:CAN_MANAGE]->(a:DigitalAsset)<-[:HAS_ASSET]-(u:User)
    OPTIONAL MATCH (p:LegacyPlan)-[:OVERSEEN_BY]->(e)
    RETURN e.id AS executor_id,
           e.name AS executor_name,
           e.verification_status AS verification_status,
           m.auth_level AS authorization_level,
           a.id AS asset_id,
           a.title AS asset_title,
           a.asset_type AS asset_type,
           u.name AS asset_owner,
           collect(DISTINCT p.title) AS overseen_plans
    """
    return run_query(query)
