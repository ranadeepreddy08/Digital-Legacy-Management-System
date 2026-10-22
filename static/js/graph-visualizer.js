/**
 * DIGITAL LEGACY VAULT – DA3
 * Interactive Graph Visualizer Module (Vis.js with Resilient Fallback)
 */

const GraphVisualizer = {
  network: null,
  container: null,
  nodesDataSet: null,
  edgesDataSet: null,
  currentData: { nodes: [], edges: [] },

  init(containerId = "graphCanvas") {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.bindEvents();
    this.loadTopology();
  },

  bindEvents() {
    const filterSelect = document.getElementById("graphFilterSelect");
    if (filterSelect) {
      filterSelect.addEventListener("change", (e) => {
        this.loadTopology(e.target.value);
      });
    }

    const refreshBtn = document.getElementById("graphRefreshBtn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => {
        const filter = document.getElementById("graphFilterSelect")?.value || "";
        this.loadTopology(filter);
      });
    }

    const fitBtn = document.getElementById("graphFitBtn");
    if (fitBtn) {
      fitBtn.addEventListener("click", () => {
        if (this.network) this.network.fit({ animation: { duration: 500 } });
      });
    }

    const orphansBtn = document.getElementById("graphOrphansBtn");
    if (orphansBtn) {
      orphansBtn.addEventListener("click", () => this.highlightOrphans());
    }
  },

  async loadTopology(labelFilter = "") {
    API.setLoading(true);
    try {
      const data = await API.getGraphTopology(labelFilter);
      this.currentData = data;
      this.render(data);
      this.updateGraphStats(data);
    } catch (err) {
      API.showToast("Failed to load graph topology: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  render(data) {
    if (!this.container) return;

    // Check if vis.js is available
    if (typeof vis !== "undefined" && vis.Network) {
      this.renderWithVis(data);
    } else {
      this.renderWithFallback(data);
    }
  },

  renderWithVis(data) {
    this.nodesDataSet = new vis.DataSet(data.nodes);
    this.edgesDataSet = new vis.DataSet(data.edges);

    const options = {
      nodes: {
        shape: "box",
        margin: 10,
        font: { face: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size: 12 },
        borderWidth: 1.5,
        shadow: false
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        color: { color: "#94a3b8", highlight: "#2563eb", hover: "#64748b" },
        font: { size: 10, align: "middle", color: "#64748b" },
        smooth: { type: "continuous", roundness: 0.2 }
      },
      physics: {
        solver: "forceAtlas2Based",
        forceAtlas2Based: {
          gravitationalConstant: -38,
          centralGravity: 0.008,
          springLength: 95,
          springConstant: 0.08,
          damping: 0.8
        },
        stabilization: { iterations: 120 }
      },
      interaction: {
        hover: true,
        tooltipDelay: 150,
        zoomView: true,
        dragView: true
      }
    };

    if (this.network) {
      this.network.destroy();
    }

    this.network = new vis.Network(this.container, { nodes: this.nodesDataSet, edges: this.edgesDataSet }, options);

    // Click event to inspect node
    this.network.on("click", (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const selectedNode = data.nodes.find(n => n.id === nodeId);
        if (selectedNode) this.inspectNode(selectedNode, data);
      } else {
        this.clearInspector();
      }
    });
  },

  renderWithFallback(data) {
    // Pure HTML5 Canvas / DOM visual representation if CDN is unavailable
    if (data.nodes.length === 0) {
      this.container.innerHTML = `
        <div class="empty-state">
          <p>No graph nodes found in the database. Click <b>Seed Sample Data</b> to populate records.</p>
        </div>
      `;
      return;
    }

    let html = `
      <div style="padding: 16px; overflow-y: auto; height: 100%;">
        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">
          Graph Explorer: Showing ${data.nodes.length} nodes and ${data.edges.length} relationships from Neo4j.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">
    `;

    data.nodes.forEach(node => {
      html += `
        <div class="stat-card" style="padding: 12px; cursor: pointer;" onclick="GraphVisualizer.inspectNodeById('${node.id}')">
          <span class="badge badge-active" style="margin-bottom: 6px;">${node.group}</span>
          <div style="font-weight: 600; font-size: 13px;">${node.raw?.name || node.raw?.title || node.id}</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">ID: ${node.id}</div>
        </div>
      `;
    });

    html += `</div></div>`;
    this.container.innerHTML = html;
  },

  inspectNodeById(nodeId) {
    const selected = this.currentData.nodes.find(n => n.id === nodeId);
    if (selected) this.inspectNode(selected, this.currentData);
  },

  inspectNode(node, fullData) {
    const inspector = document.getElementById("graphInspectorContent");
    if (!inspector) return;

    const raw = node.raw || {};
    const label = node.group || "Entity";
    const title = raw.name || raw.title || node.id;

    // Find connected edges
    const incoming = fullData.edges.filter(e => e.to === node.id);
    const outgoing = fullData.edges.filter(e => e.from === node.id);

    let html = `
      <div style="margin-bottom: 12px;">
        <span class="badge badge-scheduled" style="margin-bottom: 4px;">${label}</span>
        <h4 style="font-size: 16px; font-weight: 600; color: var(--text-main);">${title}</h4>
        <div style="font-size: 12px; color: var(--text-muted);">ID: <code>${node.id}</code></div>
      </div>
      <div class="detail-list" style="margin-bottom: 16px;">
    `;

    for (const [key, value] of Object.entries(raw)) {
      if (key !== "id" && key !== "name" && key !== "title") {
        html += `
          <div class="detail-item">
            <span class="detail-label">${key.replace(/_/g, " ")}</span>
            <span class="detail-value">${value || "—"}</span>
          </div>
        `;
      }
    }
    html += `</div>`;

    // Connected Relationships
    html += `<div style="font-size: 12px; font-weight: 600; margin-bottom: 6px; text-transform: uppercase; color: var(--text-muted);">Graph Connections</div>`;
    if (outgoing.length === 0 && incoming.length === 0) {
      html += `<p style="font-size: 12px; color: var(--text-muted);">Isolated node with no active relationships.</p>`;
    } else {
      html += `<div style="display: flex; flex-direction: column; gap: 6px; font-size: 12px;">`;
      outgoing.forEach(e => {
        const targetNode = fullData.nodes.find(n => n.id === e.to);
        const targetName = targetNode ? (targetNode.raw?.name || targetNode.raw?.title || e.to) : e.to;
        html += `
          <div style="padding: 6px 8px; background: var(--bg-secondary); border-radius: 4px; border: 1px solid var(--border-color);">
            <span style="color: var(--accent-blue); font-weight: 600;">→ -[:${e.label}]-></span> 
            <b>${targetName}</b>
          </div>
        `;
      });
      incoming.forEach(e => {
        const sourceNode = fullData.nodes.find(n => n.id === e.from);
        const sourceName = sourceNode ? (sourceNode.raw?.name || sourceNode.raw?.title || e.from) : e.from;
        html += `
          <div style="padding: 6px 8px; background: var(--bg-secondary); border-radius: 4px; border: 1px solid var(--border-color);">
            <span style="color: #16a34a; font-weight: 600;">← [:${e.label}]-</span> 
            <b>${sourceName}</b>
          </div>
        `;
      });
      html += `</div>`;
    }

    inspector.innerHTML = html;
  },

  clearInspector() {
    const inspector = document.getElementById("graphInspectorContent");
    if (inspector) {
      inspector.innerHTML = `
        <div class="empty-state" style="padding: 24px 0;">
          <p>Click any node or relationship on the canvas to inspect its properties and graph neighbors.</p>
        </div>
      `;
    }
  },

  updateGraphStats(data) {
    const statsEl = document.getElementById("graphNodeCountBadge");
    if (statsEl) {
      statsEl.innerText = `${data.nodes.length} Nodes • ${data.edges.length} Edges`;
    }
  },

  async highlightOrphans() {
    API.setLoading(true);
    try {
      const orphans = await API.getOrphanAssets();
      if (orphans.length === 0) {
        API.showToast("No orphaned assets found! All assets have designated beneficiaries or plans.", "success");
        return;
      }

      API.showToast(`Found ${orphans.length} orphaned assets without beneficiaries!`, "info");
      
      const orphanIds = new Set(orphans.map(o => o.asset_id));
      if (this.nodesDataSet) {
        const allNodes = this.nodesDataSet.get();
        allNodes.forEach(node => {
          if (orphanIds.has(node.id)) {
            this.nodesDataSet.update({
              id: node.id,
              color: { background: "#fef2f2", border: "#dc2626" },
              borderWidth: 3
            });
          }
        });
      }
    } catch (err) {
      API.showToast("Orphan detection error: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  }
};
