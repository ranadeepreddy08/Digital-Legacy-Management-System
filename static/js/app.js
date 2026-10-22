/**
 * DIGITAL LEGACY VAULT – DA3
 * Main Application Controller (Routing, CRUD Modals, State Management)
 */

const App = {
  activeView: "dashboard",
  cachedUsers: [],
  cachedAssets: [],
  cachedNominees: [],
  cachedExecutors: [],
  cachedPlans: [],
  cachedReleases: [],

  init() {
    this.bindNavigation();
    this.bindGlobalModals();
    this.checkHealth();
    this.loadView("dashboard");

    // Auto-refresh health every 30s
    setInterval(() => this.checkHealth(), 30000);
  },

  // 1. Navigation & View Routing
  bindNavigation() {
    const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
    navItems.forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const targetView = item.getAttribute("data-view");
        this.loadView(targetView);
      });
    });

    // Stat card quick navigation
    document.querySelectorAll("[data-nav-view]").forEach(card => {
      card.addEventListener("click", () => {
        const view = card.getAttribute("data-nav-view");
        this.loadView(view);
      });
    });
  },

  loadView(viewName) {
    this.activeView = viewName;

    // Update active nav item
    document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Switch view section
    document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
    const activeSection = document.getElementById(`view-${viewName}`);
    if (activeSection) {
      activeSection.classList.add("active");
    }

    // Load data specific to view
    switch (viewName) {
      case "dashboard":
        this.loadDashboard();
        break;
      case "users":
        this.loadUsers();
        break;
      case "assets":
        this.loadAssets();
        break;
      case "nominees":
        this.loadNominees();
        break;
      case "executors":
        this.loadExecutors();
        break;
      case "plans":
        this.loadPlans();
        break;
      case "releases":
        this.loadReleases();
        break;
      case "graph":
        GraphVisualizer.init();
        break;
    }
  },

  // 2. Health & Status Check
  async checkHealth() {
    const statusPill = document.getElementById("dbStatusPill");
    const statusText = document.getElementById("dbStatusText");

    try {
      const health = await API.getHealth();
      if (health.connected) {
        statusPill.className = "db-status-pill online";
        statusText.innerText = `Neo4j: Connected (${health.version || "5.x"})`;
        statusPill.title = `URI: ${health.uri} | DB: ${health.database}`;
      } else {
        statusPill.className = "db-status-pill offline";
        statusText.innerText = "Neo4j: Disconnected";
        statusPill.title = health.message || "Database offline";
      }
    } catch (err) {
      statusPill.className = "db-status-pill offline";
      statusText.innerText = "Neo4j: Unreachable";
    }
  },

  // 3. Dashboard Loading
  async loadDashboard() {
    API.setLoading(true);
    try {
      const [stats, activity, upcoming] = await Promise.all([
        API.getDashboardStats().catch(() => ({})),
        API.getDashboardActivity().catch(() => []),
        API.getUpcomingReleases().catch(() => [])
      ]);

      // Update 6 Stat Cards
      document.getElementById("statUsers").innerText = stats.users ?? "0";
      document.getElementById("statAssets").innerText = stats.assets ?? "0";
      document.getElementById("statNominees").innerText = stats.nominees ?? "0";
      document.getElementById("statExecutors").innerText = stats.executors ?? "0";
      document.getElementById("statPlans").innerText = stats.plans ?? "0";
      document.getElementById("statReleases").innerText = stats.releases ?? "0";

      // Render Recent Activity Table
      const activityTbody = document.getElementById("dashboardActivityTable");
      if (activityTbody) {
        if (!activity || activity.length === 0) {
          activityTbody.innerHTML = `<tr><td colspan="4" class="empty-state" style="padding: 20px;">No recent records found. Seed sample data to view activity.</td></tr>`;
        } else {
          activityTbody.innerHTML = activity.map(item => `
            <tr>
              <td><b>${this.escape(item.title)}</b></td>
              <td><span class="badge badge-neutral">${item.type}</span></td>
              <td><span class="badge badge-active">${item.status || "Active"}</span></td>
              <td style="color: var(--text-muted); font-size: 11px;">${this.formatDate(item.timestamp)}</td>
            </tr>
          `).join("");
        }
      }

      // Render Upcoming Releases Table
      const releasesTbody = document.getElementById("dashboardReleasesTable");
      if (releasesTbody) {
        if (!upcoming || upcoming.length === 0) {
          releasesTbody.innerHTML = `<tr><td colspan="4" class="empty-state" style="padding: 20px;">No upcoming releases scheduled.</td></tr>`;
        } else {
          releasesTbody.innerHTML = upcoming.map(rel => `
            <tr>
              <td><b>${this.formatDate(rel.release_date)}</b></td>
              <td>${this.escape(rel.plan_title || "Direct Release")}</td>
              <td><span class="badge badge-scheduled">${rel.status}</span></td>
              <td style="font-size: 12px;">${rel.nominees && rel.nominees.length ? rel.nominees.join(", ") : "—"}</td>
            </tr>
          `).join("");
        }
      }
    } catch (err) {
      API.showToast("Failed to load dashboard: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 4. Users View & CRUD
  async loadUsers(search = "") {
    API.setLoading(true);
    try {
      const users = await API.getUsers(search);
      this.cachedUsers = users;
      const tbody = document.getElementById("usersTableBody");
      if (!tbody) return;

      if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No users found. Click 'Add User' or 'Seed Sample Data'.</td></tr>`;
        return;
      }

      tbody.innerHTML = users.map(u => `
        <tr>
          <td><code>${u.id}</code></td>
          <td><b>${this.escape(u.name)}</b></td>
          <td>${this.escape(u.email)}</td>
          <td>${u.phone || "—"}</td>
          <td><span class="badge ${u.status === 'Active' ? 'badge-active' : 'badge-neutral'}">${u.status}</span></td>
          <td>
            <span title="Assets" style="margin-right: 6px;">📦 ${u.asset_count || 0}</span>
            <span title="Nominees" style="margin-right: 6px;">👥 ${u.nominee_count || 0}</span>
            <span title="Plans">📋 ${u.plan_count || 0}</span>
          </td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewUser('${u.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editUser('${u.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('User', '${u.id}', '${this.escape(u.name)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load users: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewUser(id) {
    API.setLoading(true);
    try {
      const u = await API.getUser(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">User ID</span><span class="detail-value"><code>${u.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Full Name</span><span class="detail-value"><b>${this.escape(u.name)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Email Address</span><span class="detail-value">${this.escape(u.email)}</span></div>
          <div class="detail-item"><span class="detail-label">Phone</span><span class="detail-value">${u.phone || "—"}</span></div>
          <div class="detail-item"><span class="detail-label">Account Status</span><span class="detail-value"><span class="badge badge-active">${u.status}</span></span></div>
          <div class="detail-item"><span class="detail-label">Created At</span><span class="detail-value">${this.formatDate(u.created_at)}</span></div>
          
          <div class="detail-item">
            <span class="detail-label">Owned Digital Assets (${u.assets?.length || 0})</span>
            <span class="detail-value">${u.assets && u.assets.length ? u.assets.map(a => `• ${this.escape(a.title)} (${a.type})`).join("<br>") : "None registered"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Designated Nominees (${u.nominees?.length || 0})</span>
            <span class="detail-value">${u.nominees && u.nominees.length ? u.nominees.map(n => `• ${this.escape(n.name)} (${n.relationship})`).join("<br>") : "None appointed"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Trusted Executors (${u.executors?.length || 0})</span>
            <span class="detail-value">${u.executors && u.executors.length ? u.executors.map(e => `• ${this.escape(e.name)} (${e.status})`).join("<br>") : "None appointed"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Legacy Plans (${u.plans?.length || 0})</span>
            <span class="detail-value">${u.plans && u.plans.length ? u.plans.map(p => `• ${this.escape(p.title)} [${p.status}]`).join("<br>") : "None established"}</span>
          </div>
        </div>
      `;
      this.openModal("User Details", html);
    } catch (err) {
      API.showToast("Could not fetch user details: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  openAddUserModal() {
    const html = `
      <form id="addUserForm" onsubmit="App.submitCreateUser(event)">
        <div class="form-group">
          <label>Full Name *</label>
          <input type="text" class="form-control" name="name" required placeholder="e.g. John Doe">
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" required placeholder="e.g. john@example.com">
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" placeholder="e.g. +1-555-0199">
        </div>
        <div class="form-group">
          <label>Account Status</label>
          <select class="form-control" name="status">
            <option value="Active" selected>Active</option>
            <option value="Inactive">Inactive</option>
            <option value="Suspended">Suspended</option>
          </select>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Create User</button>
        </div>
      </form>
    `;
    this.openModal("Add New User", html);
  },

  async submitCreateUser(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      status: form.status.value
    };
    try {
      API.setLoading(true);
      await API.createUser(data);
      API.showToast("User created successfully!", "success");
      this.closeModal();
      this.loadUsers();
    } catch (err) {
      API.showToast("Error creating user: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editUser(id) {
    const user = this.cachedUsers.find(u => u.id === id);
    if (!user) return;

    const html = `
      <form id="editUserForm" onsubmit="App.submitUpdateUser(event, '${id}')">
        <div class="form-group">
          <label>Full Name *</label>
          <input type="text" class="form-control" name="name" value="${this.escape(user.name)}" required>
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" value="${this.escape(user.email)}" required>
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" value="${this.escape(user.phone || '')}">
        </div>
        <div class="form-group">
          <label>Account Status</label>
          <select class="form-control" name="status">
            <option value="Active" ${user.status === 'Active' ? 'selected' : ''}>Active</option>
            <option value="Inactive" ${user.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
            <option value="Suspended" ${user.status === 'Suspended' ? 'selected' : ''}>Suspended</option>
          </select>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    this.openModal(`Edit User (${id})`, html);
  },

  async submitUpdateUser(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      status: form.status.value
    };
    try {
      API.setLoading(true);
      await API.updateUser(id, data);
      API.showToast("User updated successfully!", "success");
      this.closeModal();
      this.loadUsers();
    } catch (err) {
      API.showToast("Error updating user: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 5. Assets View & CRUD
  async loadAssets(params = {}) {
    API.setLoading(true);
    try {
      const assets = await API.getAssets(params);
      this.cachedAssets = assets;
      const tbody = document.getElementById("assetsTableBody");
      if (!tbody) return;

      if (assets.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No digital assets found matching filters.</td></tr>`;
        return;
      }

      tbody.innerHTML = assets.map(a => `
        <tr>
          <td><code>${a.id}</code></td>
          <td><b>${this.escape(a.title)}</b></td>
          <td><span class="badge badge-neutral">${a.asset_type}</span></td>
          <td><span class="badge ${this.getPriorityBadgeClass(a.priority)}">${a.priority}</span></td>
          <td>${a.owner_name ? `<b>${this.escape(a.owner_name)}</b>` : `<span style="color:var(--state-danger-text);">Unassigned</span>`}</td>
          <td>${a.designated_nominee_name ? `${this.escape(a.designated_nominee_name)} (${a.nominee_share_pct || 100}%)` : `<span style="color:var(--text-light);">None</span>`}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewAsset('${a.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editAsset('${a.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('Asset', '${a.id}', '${this.escape(a.title)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load assets: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewAsset(id) {
    API.setLoading(true);
    try {
      const a = await API.getAsset(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">Asset ID</span><span class="detail-value"><code>${a.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Title</span><span class="detail-value"><b>${this.escape(a.title)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Asset Type</span><span class="detail-value"><span class="badge badge-neutral">${a.asset_type}</span></span></div>
          <div class="detail-item"><span class="detail-label">Priority Level</span><span class="detail-value"><span class="badge ${this.getPriorityBadgeClass(a.priority)}">${a.priority}</span></span></div>
          <div class="detail-item"><span class="detail-label">Estimated Value</span><span class="detail-value">${this.escape(a.estimated_value || 'Not Specified')}</span></div>
          <div class="detail-item"><span class="detail-label">Access Hint (Encrypted/Location)</span><span class="detail-value"><i>${this.escape(a.access_info_encrypted_hint)}</i></span></div>
          <div class="detail-item"><span class="detail-label">Owner</span><span class="detail-value">${a.owner ? `<b>${this.escape(a.owner.name)}</b> (${a.owner.email})` : "Unassigned"}</span></div>
          
          <div class="detail-item">
            <span class="detail-label">Designated Beneficiary Nominees</span>
            <span class="detail-value">${a.nominees && a.nominees.length ? a.nominees.map(n => `• ${this.escape(n.name)} (${n.relationship}) - Share: ${n.share_pct}%`).join("<br>") : "No nominee assigned"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Authorized Executors</span>
            <span class="detail-value">${a.executors && a.executors.length ? a.executors.map(e => `• ${this.escape(e.name)} [Auth: ${e.auth_level || 'Standard'}]`).join("<br>") : "No executor assigned"}</span>
          </div>
        </div>
      `;
      this.openModal("Digital Asset Provenance", html);
    } catch (err) {
      API.showToast("Could not fetch asset details: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async openAddAssetModal() {
    // Fetch users, nominees, executors for select options
    const [users, nominees, executors] = await Promise.all([
      API.getUsers().catch(() => []),
      API.getNominees().catch(() => []),
      API.getExecutors().catch(() => [])
    ]);

    const userOptions = users.map(u => `<option value="${u.id}">${this.escape(u.name)} (${u.email})</option>`).join("");
    const nomineeOptions = `<option value="">-- Optional: Designate Nominee --</option>` + 
      nominees.map(n => `<option value="${n.id}">${this.escape(n.name)} (${n.relationship})</option>`).join("");
    const executorOptions = `<option value="">-- Optional: Authorize Executor --</option>` + 
      executors.map(e => `<option value="${e.id}">${this.escape(e.name)}</option>`).join("");

    const html = `
      <form id="addAssetForm" onsubmit="App.submitCreateAsset(event)">
        <div class="form-group">
          <label>Asset Title *</label>
          <input type="text" class="form-control" name="title" required placeholder="e.g. Ledger Bitcoin Cold Wallet">
        </div>
        <div class="form-group">
          <label>Asset Category *</label>
          <select class="form-control" name="asset_type" required>
            <option value="Cryptocurrency">Cryptocurrency</option>
            <option value="Financial Account">Financial Account</option>
            <option value="Cloud Storage">Cloud Storage</option>
            <option value="Social Media">Social Media</option>
            <option value="Intellectual Property">Intellectual Property</option>
            <option value="Personal Document">Personal Document</option>
            <option value="Domain Portfolio">Domain Portfolio</option>
          </select>
        </div>
        <div class="form-group">
          <label>Access Info Encrypted Hint *</label>
          <textarea class="form-control" name="access_hint" required placeholder="e.g. Recovery seed in safe deposit box #402"></textarea>
          <div class="form-hint">Do not enter raw passwords. Store secure physical or vault hints only.</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div class="form-group">
            <label>Priority</label>
            <select class="form-control" name="priority">
              <option value="Critical">Critical</option>
              <option value="High" selected>High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
          <div class="form-group">
            <label>Estimated Value</label>
            <input type="text" class="form-control" name="estimated_value" placeholder="e.g. $50,000 USD">
          </div>
        </div>
        <div class="form-group">
          <label>Asset Owner *</label>
          <select class="form-control" name="owner_id" required>
            <option value="">-- Select Owner --</option>
            ${userOptions}
          </select>
        </div>
        <div class="form-group">
          <label>Designated Nominee (Beneficiary)</label>
          <select class="form-control" name="nominee_id">${nomineeOptions}</select>
        </div>
        <div class="form-group">
          <label>Managing Executor</label>
          <select class="form-control" name="executor_id">${executorOptions}</select>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Create Asset</button>
        </div>
      </form>
    `;
    this.openModal("Register Digital Asset", html);
  },

  async submitCreateAsset(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
      title: form.title.value.trim(),
      asset_type: form.asset_type.value,
      access_info_encrypted_hint: form.access_hint.value.trim(),
      priority: form.priority.value,
      estimated_value: form.estimated_value.value.trim(),
      owner_id: form.owner_id.value || null,
      designated_nominee_id: form.nominee_id.value || null,
      managing_executor_id: form.executor_id.value || null
    };
    try {
      API.setLoading(true);
      await API.createAsset(data);
      API.showToast("Digital asset created and linked successfully!", "success");
      this.closeModal();
      this.loadAssets();
    } catch (err) {
      API.showToast("Error creating asset: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editAsset(id) {
    const asset = this.cachedAssets.find(a => a.id === id);
    if (!asset) return;

    const users = await API.getUsers().catch(() => []);
    const userOptions = users.map(u => `<option value="${u.id}" ${u.id === asset.owner_id ? 'selected' : ''}>${this.escape(u.name)}</option>`).join("");

    const html = `
      <form id="editAssetForm" onsubmit="App.submitUpdateAsset(event, '${id}')">
        <div class="form-group">
          <label>Asset Title *</label>
          <input type="text" class="form-control" name="title" value="${this.escape(asset.title)}" required>
        </div>
        <div class="form-group">
          <label>Asset Category *</label>
          <select class="form-control" name="asset_type">
            <option value="Cryptocurrency" ${asset.asset_type === 'Cryptocurrency' ? 'selected' : ''}>Cryptocurrency</option>
            <option value="Financial Account" ${asset.asset_type === 'Financial Account' ? 'selected' : ''}>Financial Account</option>
            <option value="Cloud Storage" ${asset.asset_type === 'Cloud Storage' ? 'selected' : ''}>Cloud Storage</option>
            <option value="Social Media" ${asset.asset_type === 'Social Media' ? 'selected' : ''}>Social Media</option>
            <option value="Intellectual Property" ${asset.asset_type === 'Intellectual Property' ? 'selected' : ''}>Intellectual Property</option>
            <option value="Personal Document" ${asset.asset_type === 'Personal Document' ? 'selected' : ''}>Personal Document</option>
            <option value="Domain Portfolio" ${asset.asset_type === 'Domain Portfolio' ? 'selected' : ''}>Domain Portfolio</option>
          </select>
        </div>
        <div class="form-group">
          <label>Access Info Encrypted Hint *</label>
          <textarea class="form-control" name="access_hint" required>${this.escape(asset.access_info_encrypted_hint || '')}</textarea>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div class="form-group">
            <label>Priority</label>
            <select class="form-control" name="priority">
              <option value="Critical" ${asset.priority === 'Critical' ? 'selected' : ''}>Critical</option>
              <option value="High" ${asset.priority === 'High' ? 'selected' : ''}>High</option>
              <option value="Medium" ${asset.priority === 'Medium' ? 'selected' : ''}>Medium</option>
              <option value="Low" ${asset.priority === 'Low' ? 'selected' : ''}>Low</option>
            </select>
          </div>
          <div class="form-group">
            <label>Estimated Value</label>
            <input type="text" class="form-control" name="estimated_value" value="${this.escape(asset.estimated_value || '')}">
          </div>
        </div>
        <div class="form-group">
          <label>Asset Owner</label>
          <select class="form-control" name="owner_id">${userOptions}</select>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Asset</button>
        </div>
      </form>
    `;
    this.openModal(`Edit Asset (${id})`, html);
  },

  async submitUpdateAsset(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      title: form.title.value.trim(),
      asset_type: form.asset_type.value,
      access_info_encrypted_hint: form.access_hint.value.trim(),
      priority: form.priority.value,
      estimated_value: form.estimated_value.value.trim(),
      owner_id: form.owner_id.value || null
    };
    try {
      API.setLoading(true);
      await API.updateAsset(id, data);
      API.showToast("Asset updated successfully!", "success");
      this.closeModal();
      this.loadAssets();
    } catch (err) {
      API.showToast("Error updating asset: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 6. Nominees View & CRUD
  async loadNominees(search = "") {
    API.setLoading(true);
    try {
      const nominees = await API.getNominees(search);
      this.cachedNominees = nominees;
      const tbody = document.getElementById("nomineesTableBody");
      if (!tbody) return;

      if (nominees.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No nominees found.</td></tr>`;
        return;
      }

      tbody.innerHTML = nominees.map(n => `
        <tr>
          <td><code>${n.id}</code></td>
          <td><b>${this.escape(n.name)}</b></td>
          <td><span class="badge badge-neutral">${n.relationship}</span></td>
          <td>${this.escape(n.email)}</td>
          <td>${n.user_name ? `<b>${this.escape(n.user_name)}</b>` : "—"}</td>
          <td>${n.designated_assets && n.designated_assets.length ? n.designated_assets.join(", ") : "—"}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewNominee('${n.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editNominee('${n.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('Nominee', '${n.id}', '${this.escape(n.name)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load nominees: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewNominee(id) {
    API.setLoading(true);
    try {
      const n = await API.getNominee(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">Nominee ID</span><span class="detail-value"><code>${n.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Full Name</span><span class="detail-value"><b>${this.escape(n.name)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Relationship</span><span class="detail-value"><span class="badge badge-neutral">${n.relationship}</span></span></div>
          <div class="detail-item"><span class="detail-label">Email</span><span class="detail-value">${this.escape(n.email)}</span></div>
          <div class="detail-item"><span class="detail-label">Phone</span><span class="detail-value">${n.phone || "—"}</span></div>
          <div class="detail-item"><span class="detail-label">Allocation Share</span><span class="detail-value">${n.allocation_percentage}%</span></div>
          <div class="detail-item"><span class="detail-label">Appointing User</span><span class="detail-value">${n.user ? `<b>${this.escape(n.user.name)}</b> (${n.user.email})` : "Unassigned"}</span></div>
          <div class="detail-item">
            <span class="detail-label">Designated Digital Assets</span>
            <span class="detail-value">${n.designated_assets && n.designated_assets.length ? n.designated_assets.map(a => `• ${this.escape(a.title)} (${a.share}%)`).join("<br>") : "None currently designated"}</span>
          </div>
        </div>
      `;
      this.openModal("Nominee Beneficiary Details", html);
    } catch (err) {
      API.showToast("Could not fetch nominee: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async openAddNomineeModal() {
    const [users, assets] = await Promise.all([
      API.getUsers().catch(() => []),
      API.getAssets().catch(() => [])
    ]);

    const userOptions = users.map(u => `<option value="${u.id}">${this.escape(u.name)}</option>`).join("");
    const assetOptions = `<option value="">-- Optional: Designate Asset --</option>` +
      assets.map(a => `<option value="${a.id}">${this.escape(a.title)} (${a.asset_type})</option>`).join("");

    const html = `
      <form id="addNomineeForm" onsubmit="App.submitCreateNominee(event)">
        <div class="form-group">
          <label>Nominee Name *</label>
          <input type="text" class="form-control" name="name" required placeholder="e.g. Julian Vance">
        </div>
        <div class="form-group">
          <label>Relationship *</label>
          <select class="form-control" name="relationship" required>
            <option value="Spouse">Spouse</option>
            <option value="Child">Child</option>
            <option value="Sibling">Sibling</option>
            <option value="Parent">Parent</option>
            <option value="Trusted Friend">Trusted Friend</option>
            <option value="Institutional Beneficiary">Institutional Beneficiary</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" required placeholder="e.g. julian@example.com">
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" placeholder="e.g. +1-555-0201">
        </div>
        <div class="form-group">
          <label>Appointing User *</label>
          <select class="form-control" name="user_id" required>
            <option value="">-- Select Appointing User --</option>
            ${userOptions}
          </select>
        </div>
        <div class="form-group">
          <label>Designated Digital Asset</label>
          <select class="form-control" name="asset_id">${assetOptions}</select>
        </div>
        <div class="form-group">
          <label>Allocation Share (%)</label>
          <input type="number" class="form-control" name="allocation" min="1" max="100" value="100">
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Create Nominee</button>
        </div>
      </form>
    `;
    this.openModal("Add Nominee Beneficiary", html);
  },

  async submitCreateNominee(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      relationship: form.relationship.value,
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      allocation_percentage: parseInt(form.allocation.value) || 100,
      user_id: form.user_id.value || null,
      designated_asset_id: form.asset_id.value || null
    };
    try {
      API.setLoading(true);
      await API.createNominee(data);
      API.showToast("Nominee beneficiary created successfully!", "success");
      this.closeModal();
      this.loadNominees();
    } catch (err) {
      API.showToast("Error creating nominee: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editNominee(id) {
    const nominee = this.cachedNominees.find(n => n.id === id);
    if (!nominee) return;

    const html = `
      <form id="editNomineeForm" onsubmit="App.submitUpdateNominee(event, '${id}')">
        <div class="form-group">
          <label>Nominee Name *</label>
          <input type="text" class="form-control" name="name" value="${this.escape(nominee.name)}" required>
        </div>
        <div class="form-group">
          <label>Relationship *</label>
          <input type="text" class="form-control" name="relationship" value="${this.escape(nominee.relationship)}" required>
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" value="${this.escape(nominee.email)}" required>
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" value="${this.escape(nominee.phone || '')}">
        </div>
        <div class="form-group">
          <label>Allocation Share (%)</label>
          <input type="number" class="form-control" name="allocation" min="1" max="100" value="${nominee.allocation_percentage || 100}">
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    this.openModal(`Edit Nominee (${id})`, html);
  },

  async submitUpdateNominee(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      relationship: form.relationship.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      allocation_percentage: parseInt(form.allocation.value) || 100
    };
    try {
      API.setLoading(true);
      await API.updateNominee(id, data);
      API.showToast("Nominee updated successfully!", "success");
      this.closeModal();
      this.loadNominees();
    } catch (err) {
      API.showToast("Error updating nominee: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 7. Trusted Executors View & CRUD
  async loadExecutors(search = "") {
    API.setLoading(true);
    try {
      const executors = await API.getExecutors(search);
      this.cachedExecutors = executors;
      const tbody = document.getElementById("executorsTableBody");
      if (!tbody) return;

      if (executors.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No trusted executors found.</td></tr>`;
        return;
      }

      tbody.innerHTML = executors.map(e => `
        <tr>
          <td><code>${e.id}</code></td>
          <td><b>${this.escape(e.name)}</b></td>
          <td><span class="badge badge-active">${e.verification_status}</span></td>
          <td>${this.escape(e.email)}</td>
          <td>${e.user_name ? `<b>${this.escape(e.user_name)}</b>` : "—"}</td>
          <td>${e.managed_assets && e.managed_assets.length ? e.managed_assets.join(", ") : "—"}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewExecutor('${e.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editExecutor('${e.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('Executor', '${e.id}', '${this.escape(e.name)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load executors: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewExecutor(id) {
    API.setLoading(true);
    try {
      const e = await API.getExecutor(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">Executor ID</span><span class="detail-value"><code>${e.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Name</span><span class="detail-value"><b>${this.escape(e.name)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Verification</span><span class="detail-value"><span class="badge badge-active">${e.verification_status}</span></span></div>
          <div class="detail-item"><span class="detail-label">Role Description</span><span class="detail-value">${this.escape(e.role_description || 'Digital Estate Custodian')}</span></div>
          <div class="detail-item"><span class="detail-label">Email</span><span class="detail-value">${this.escape(e.email)}</span></div>
          <div class="detail-item"><span class="detail-label">Phone</span><span class="detail-value">${e.phone || "—"}</span></div>
          <div class="detail-item"><span class="detail-label">Appointing User</span><span class="detail-value">${e.user ? `<b>${this.escape(e.user.name)}</b>` : "Unassigned"}</span></div>
          <div class="detail-item">
            <span class="detail-label">Authorized Assets</span>
            <span class="detail-value">${e.managed_assets && e.managed_assets.length ? e.managed_assets.map(a => `• ${this.escape(a.title)} [${a.auth_level || 'Full'}]`).join("<br>") : "None currently authorized"}</span>
          </div>
        </div>
      `;
      this.openModal("Trusted Executor Credentials", html);
    } catch (err) {
      API.showToast("Could not fetch executor: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async openAddExecutorModal() {
    const users = await API.getUsers().catch(() => []);
    const userOptions = users.map(u => `<option value="${u.id}">${this.escape(u.name)}</option>`).join("");

    const html = `
      <form id="addExecutorForm" onsubmit="App.submitCreateExecutor(event)">
        <div class="form-group">
          <label>Executor Name *</label>
          <input type="text" class="form-control" name="name" required placeholder="e.g. Robert Sterling, Esq.">
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" required placeholder="e.g. sterling@law.com">
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" placeholder="e.g. +1-555-0301">
        </div>
        <div class="form-group">
          <label>Verification Status</label>
          <select class="form-control" name="verification_status">
            <option value="Verified Notary & Attorney" selected>Verified Notary & Attorney</option>
            <option value="Licensed Corporate Fiduciary">Licensed Corporate Fiduciary</option>
            <option value="Academic Peer Verified">Academic Peer Verified</option>
            <option value="Family Designated Trustee">Family Designated Trustee</option>
          </select>
        </div>
        <div class="form-group">
          <label>Role Description</label>
          <input type="text" class="form-control" name="role_desc" placeholder="e.g. Legal Estate Counsel">
        </div>
        <div class="form-group">
          <label>Appointing User *</label>
          <select class="form-control" name="user_id" required>
            <option value="">-- Select User --</option>
            ${userOptions}
          </select>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Appoint Executor</button>
        </div>
      </form>
    `;
    this.openModal("Appoint Trusted Executor", html);
  },

  async submitCreateExecutor(e) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      verification_status: form.verification_status.value,
      role_description: form.role_desc.value.trim(),
      user_id: form.user_id.value || null
    };
    try {
      API.setLoading(true);
      await API.createExecutor(data);
      API.showToast("Trusted executor appointed successfully!", "success");
      this.closeModal();
      this.loadExecutors();
    } catch (err) {
      API.showToast("Error appointing executor: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editExecutor(id) {
    const executor = this.cachedExecutors.find(e => e.id === id);
    if (!executor) return;

    const html = `
      <form id="editExecutorForm" onsubmit="App.submitUpdateExecutor(event, '${id}')">
        <div class="form-group">
          <label>Executor Name *</label>
          <input type="text" class="form-control" name="name" value="${this.escape(executor.name)}" required>
        </div>
        <div class="form-group">
          <label>Email Address *</label>
          <input type="email" class="form-control" name="email" value="${this.escape(executor.email)}" required>
        </div>
        <div class="form-group">
          <label>Phone Number</label>
          <input type="text" class="form-control" name="phone" value="${this.escape(executor.phone || '')}">
        </div>
        <div class="form-group">
          <label>Verification Status</label>
          <input type="text" class="form-control" name="verification_status" value="${this.escape(executor.verification_status || '')}">
        </div>
        <div class="form-group">
          <label>Role Description</label>
          <input type="text" class="form-control" name="role_desc" value="${this.escape(executor.role_description || '')}">
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    this.openModal(`Edit Executor (${id})`, html);
  },

  async submitUpdateExecutor(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      phone: form.phone.value.trim(),
      verification_status: form.verification_status.value.trim(),
      role_description: form.role_desc.value.trim()
    };
    try {
      API.setLoading(true);
      await API.updateExecutor(id, data);
      API.showToast("Executor updated successfully!", "success");
      this.closeModal();
      this.loadExecutors();
    } catch (err) {
      API.showToast("Error updating executor: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 8. Legacy Plans View & CRUD
  async loadPlans(search = "") {
    API.setLoading(true);
    try {
      const plans = await API.getPlans(search);
      this.cachedPlans = plans;
      const tbody = document.getElementById("plansTableBody");
      if (!tbody) return;

      if (plans.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No legacy plans found.</td></tr>`;
        return;
      }

      tbody.innerHTML = plans.map(p => `
        <tr>
          <td><code>${p.id}</code></td>
          <td><b>${this.escape(p.title)}</b></td>
          <td><span class="badge ${p.status === 'Active' ? 'badge-active' : 'badge-neutral'}">${p.status}</span></td>
          <td>${this.escape(p.trigger_condition)}</td>
          <td>${p.user_name ? `<b>${this.escape(p.user_name)}</b>` : "—"}</td>
          <td>📦 ${p.included_assets?.length || 0} assets • 👥 ${p.assigned_nominees?.length || 0}</td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewPlan('${p.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editPlan('${p.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('Plan', '${p.id}', '${this.escape(p.title)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load plans: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewPlan(id) {
    API.setLoading(true);
    try {
      const p = await API.getPlan(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">Plan ID</span><span class="detail-value"><code>${p.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Title</span><span class="detail-value"><b>${this.escape(p.title)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Status</span><span class="detail-value"><span class="badge badge-active">${p.status}</span></span></div>
          <div class="detail-item"><span class="detail-label">Trigger Condition</span><span class="detail-value"><b>${this.escape(p.trigger_condition)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Execution Notes</span><span class="detail-value">${this.escape(p.notes || 'None')}</span></div>
          <div class="detail-item"><span class="detail-label">Plan Owner</span><span class="detail-value">${p.user ? `<b>${this.escape(p.user.name)}</b> (${p.user.email})` : "Unassigned"}</span></div>
          <div class="detail-item">
            <span class="detail-label">Assets Governed by Plan</span>
            <span class="detail-value">${p.assets && p.assets.length ? p.assets.map(a => `• ${this.escape(a.title)} (${a.type})`).join("<br>") : "No assets attached"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Beneficiary Nominees</span>
            <span class="detail-value">${p.nominees && p.nominees.length ? p.nominees.map(n => `• ${this.escape(n.name)} (${n.relationship})`).join("<br>") : "None"}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Supervising Executors</span>
            <span class="detail-value">${p.executors && p.executors.length ? p.executors.map(e => `• ${this.escape(e.name)}`).join("<br>") : "None"}</span>
          </div>
        </div>
      `;
      this.openModal("Legacy Plan Governance Graph", html);
    } catch (err) {
      API.showToast("Could not fetch plan: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async openAddPlanModal() {
    const [users, assets, nominees, executors] = await Promise.all([
      API.getUsers().catch(() => []),
      API.getAssets().catch(() => []),
      API.getNominees().catch(() => []),
      API.getExecutors().catch(() => [])
    ]);

    const userOptions = users.map(u => `<option value="${u.id}">${this.escape(u.name)}</option>`).join("");
    const assetOptions = assets.map(a => `<option value="${a.id}">${this.escape(a.title)} (${a.asset_type})</option>`).join("");
    const nomineeOptions = nominees.map(n => `<option value="${n.id}">${this.escape(n.name)} (${n.relationship})</option>`).join("");
    const executorOptions = executors.map(e => `<option value="${e.id}">${this.escape(e.name)}</option>`).join("");

    const html = `
      <form id="addPlanForm" onsubmit="App.submitCreatePlan(event)">
        <div class="form-group">
          <label>Plan Title *</label>
          <input type="text" class="form-control" name="title" required placeholder="e.g. Digital Assets & IP Succession Plan">
        </div>
        <div class="form-group">
          <label>Release Trigger Condition *</label>
          <select class="form-control" name="trigger_condition" required>
            <option value="Legal Death Certificate Verification">Legal Death Certificate Verification</option>
            <option value="Inactivity > 180 Days with Dual Notary Confirmation">Inactivity > 180 Days with Dual Notary Confirmation</option>
            <option value="Certified Incapacitation or Medical Disability">Certified Incapacitation or Medical Disability</option>
            <option value="Executor Discretionary Activation">Executor Discretionary Activation</option>
          </select>
        </div>
        <div class="form-group">
          <label>Status</label>
          <select class="form-control" name="status">
            <option value="Active" selected>Active</option>
            <option value="Pending Review">Pending Review</option>
            <option value="Draft">Draft</option>
          </select>
        </div>
        <div class="form-group">
          <label>Plan Owner *</label>
          <select class="form-control" name="user_id" required>
            <option value="">-- Select Owner --</option>
            ${userOptions}
          </select>
        </div>
        <div class="form-group">
          <label>Included Digital Assets (Hold Ctrl/Cmd to select multiple)</label>
          <select class="form-control" name="asset_ids" multiple style="height: 80px;">${assetOptions}</select>
        </div>
        <div class="form-group">
          <label>Designated Nominees</label>
          <select class="form-control" name="nominee_ids" multiple style="height: 70px;">${nomineeOptions}</select>
        </div>
        <div class="form-group">
          <label>Overseeing Executor</label>
          <select class="form-control" name="executor_ids" multiple style="height: 70px;">${executorOptions}</select>
        </div>
        <div class="form-group">
          <label>Execution Notes</label>
          <textarea class="form-control" name="notes" placeholder="Specific handling instructions for nominees and executors..."></textarea>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Create Plan</button>
        </div>
      </form>
    `;
    this.openModal("Establish Legacy Plan", html);
  },

  async submitCreatePlan(e) {
    e.preventDefault();
    const form = e.target;
    const selectedAssets = Array.from(form.asset_ids.selectedOptions).map(o => o.value);
    const selectedNominees = Array.from(form.nominee_ids.selectedOptions).map(o => o.value);
    const selectedExecutors = Array.from(form.executor_ids.selectedOptions).map(o => o.value);

    const data = {
      title: form.title.value.trim(),
      trigger_condition: form.trigger_condition.value,
      status: form.status.value,
      user_id: form.user_id.value || null,
      asset_ids: selectedAssets,
      nominee_ids: selectedNominees,
      executor_ids: selectedExecutors,
      notes: form.notes.value.trim()
    };
    try {
      API.setLoading(true);
      await API.createPlan(data);
      API.showToast("Legacy plan established successfully!", "success");
      this.closeModal();
      this.loadPlans();
    } catch (err) {
      API.showToast("Error establishing plan: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editPlan(id) {
    const plan = this.cachedPlans.find(p => p.id === id);
    if (!plan) return;

    const html = `
      <form id="editPlanForm" onsubmit="App.submitUpdatePlan(event, '${id}')">
        <div class="form-group">
          <label>Plan Title *</label>
          <input type="text" class="form-control" name="title" value="${this.escape(plan.title)}" required>
        </div>
        <div class="form-group">
          <label>Release Trigger Condition *</label>
          <input type="text" class="form-control" name="trigger_condition" value="${this.escape(plan.trigger_condition)}" required>
        </div>
        <div class="form-group">
          <label>Status</label>
          <select class="form-control" name="status">
            <option value="Active" ${plan.status === 'Active' ? 'selected' : ''}>Active</option>
            <option value="Pending Review" ${plan.status === 'Pending Review' ? 'selected' : ''}>Pending Review</option>
            <option value="Draft" ${plan.status === 'Draft' ? 'selected' : ''}>Draft</option>
            <option value="Executed" ${plan.status === 'Executed' ? 'selected' : ''}>Executed</option>
          </select>
        </div>
        <div class="form-group">
          <label>Execution Notes</label>
          <textarea class="form-control" name="notes">${this.escape(plan.notes || '')}</textarea>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    this.openModal(`Edit Legacy Plan (${id})`, html);
  },

  async submitUpdatePlan(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      title: form.title.value.trim(),
      trigger_condition: form.trigger_condition.value.trim(),
      status: form.status.value,
      notes: form.notes.value.trim()
    };
    try {
      API.setLoading(true);
      await API.updatePlan(id, data);
      API.showToast("Legacy plan updated successfully!", "success");
      this.closeModal();
      this.loadPlans();
    } catch (err) {
      API.showToast("Error updating plan: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 9. Scheduled Releases View & CRUD
  async loadReleases(params = {}) {
    API.setLoading(true);
    try {
      const releases = await API.getReleases(params);
      this.cachedReleases = releases;
      const tbody = document.getElementById("releasesTableBody");
      if (!tbody) return;

      if (releases.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No scheduled releases found.</td></tr>`;
        return;
      }

      tbody.innerHTML = releases.map(r => `
        <tr>
          <td><code>${r.id}</code></td>
          <td><b>${this.formatDate(r.release_date)}</b></td>
          <td><span class="badge ${r.status === 'Released' ? 'badge-active' : (r.status === 'Scheduled' ? 'badge-scheduled' : 'badge-neutral')}">${r.status}</span></td>
          <td>${this.escape(r.notification_method)}</td>
          <td>${r.plan_title ? `<b>${this.escape(r.plan_title)}</b>` : (r.asset_title ? `Asset: ${this.escape(r.asset_title)}` : "—")}</td>
          <td><span style="font-size: 12px; color: var(--text-muted);">${this.escape(r.notes || "—")}</span></td>
          <td>
            <div class="table-actions">
              <button class="btn btn-sm" onclick="App.viewRelease('${r.id}')">View</button>
              <button class="btn btn-sm" onclick="App.editRelease('${r.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="App.confirmDelete('Release', '${r.id}', 'Release on ${this.formatDate(r.release_date)}')">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      API.showToast("Failed to load releases: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async viewRelease(id) {
    API.setLoading(true);
    try {
      const r = await API.getRelease(id);
      let html = `
        <div class="detail-list">
          <div class="detail-item"><span class="detail-label">Release ID</span><span class="detail-value"><code>${r.id}</code></span></div>
          <div class="detail-item"><span class="detail-label">Release Date</span><span class="detail-value"><b>${this.formatDate(r.release_date)}</b></span></div>
          <div class="detail-item"><span class="detail-label">Status</span><span class="detail-value"><span class="badge badge-scheduled">${r.status}</span></span></div>
          <div class="detail-item"><span class="detail-label">Notification Dispatch</span><span class="detail-value">${this.escape(r.notification_method)}</span></div>
          <div class="detail-item"><span class="detail-label">Associated Legacy Plan</span><span class="detail-value">${r.plan ? `<b>${this.escape(r.plan.title)}</b>` : "None"}</span></div>
          <div class="detail-item"><span class="detail-label">Owner</span><span class="detail-value">${r.owner ? `<b>${this.escape(r.owner.name)}</b>` : "—"}</span></div>
          <div class="detail-item"><span class="detail-label">Protected Assets</span><span class="detail-value">${r.assets && r.assets.length ? r.assets.map(a => `• ${this.escape(a.title)}`).join("<br>") : "None"}</span></div>
          <div class="detail-item"><span class="detail-label">Recipients (Nominees)</span><span class="detail-value">${r.nominees && r.nominees.length ? r.nominees.map(n => `• ${this.escape(n.name)}`).join("<br>") : "None"}</span></div>
        </div>
      `;
      this.openModal("Scheduled Release Details", html);
    } catch (err) {
      API.showToast("Could not fetch release: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async openAddReleaseModal() {
    const plans = await API.getPlans().catch(() => []);
    const planOptions = plans.map(p => `<option value="${p.id}">${this.escape(p.title)}</option>`).join("");

    const html = `
      <form id="addReleaseForm" onsubmit="App.submitCreateRelease(event)">
        <div class="form-group">
          <label>Target Release Date *</label>
          <input type="date" class="form-control" name="release_date" required>
        </div>
        <div class="form-group">
          <label>Status</label>
          <select class="form-control" name="status">
            <option value="Scheduled" selected>Scheduled</option>
            <option value="In Review">In Review</option>
            <option value="Released">Released</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>
        <div class="form-group">
          <label>Notification Dispatch Method</label>
          <select class="form-control" name="method">
            <option value="Encrypted Email + SMS OTP" selected>Encrypted Email + SMS OTP</option>
            <option value="Notary In-Person Verification">Notary In-Person Verification</option>
            <option value="Automated Webhook & Archival Dispatch">Automated Webhook & Archival Dispatch</option>
          </select>
        </div>
        <div class="form-group">
          <label>Associated Legacy Plan *</label>
          <select class="form-control" name="plan_id" required>
            <option value="">-- Select Plan --</option>
            ${planOptions}
          </select>
        </div>
        <div class="form-group">
          <label>Notes</label>
          <textarea class="form-control" name="notes" placeholder="Release execution prerequisites..."></textarea>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Schedule Release</button>
        </div>
      </form>
    `;
    this.openModal("Create Scheduled Release", html);
  },

  async submitCreateRelease(e) {
    e.preventDefault();
    const form = e.target;
    const releaseDate = new Date(form.release_date.value).toISOString();

    const data = {
      release_date: releaseDate,
      status: form.status.value,
      notification_method: form.method.value,
      plan_id: form.plan_id.value || null,
      notes: form.notes.value.trim()
    };
    try {
      API.setLoading(true);
      await API.createRelease(data);
      API.showToast("Release scheduled successfully!", "success");
      this.closeModal();
      this.loadReleases();
    } catch (err) {
      API.showToast("Error scheduling release: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async editRelease(id) {
    const release = this.cachedReleases.find(r => r.id === id);
    if (!release) return;

    const html = `
      <form id="editReleaseForm" onsubmit="App.submitUpdateRelease(event, '${id}')">
        <div class="form-group">
          <label>Status Workflow Transition *</label>
          <select class="form-control" name="status">
            <option value="Scheduled" ${release.status === 'Scheduled' ? 'selected' : ''}>Scheduled</option>
            <option value="In Review" ${release.status === 'In Review' ? 'selected' : ''}>In Review</option>
            <option value="Released" ${release.status === 'Released' ? 'selected' : ''}>Released</option>
            <option value="Cancelled" ${release.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
          </select>
        </div>
        <div class="form-group">
          <label>Notification Dispatch Method</label>
          <input type="text" class="form-control" name="method" value="${this.escape(release.notification_method || '')}">
        </div>
        <div class="form-group">
          <label>Notes</label>
          <textarea class="form-control" name="notes">${this.escape(release.notes || '')}</textarea>
        </div>
        <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
          <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    this.openModal(`Update Scheduled Release (${id})`, html);
  },

  async submitUpdateRelease(e, id) {
    e.preventDefault();
    const form = e.target;
    const data = {
      status: form.status.value,
      notification_method: form.method.value.trim(),
      notes: form.notes.value.trim()
    };
    try {
      API.setLoading(true);
      await API.updateRelease(id, data);
      API.showToast("Release updated successfully!", "success");
      this.closeModal();
      this.loadReleases();
    } catch (err) {
      API.showToast("Error updating release: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 10. Seeding & Database Actions
  async handleSeedData() {
    if (!confirm("Seed Neo4j database with interconnected sample records (Users, Assets, Nominees, Executors, Plans, Releases)?")) {
      return;
    }
    API.setLoading(true);
    try {
      const res = await API.seedSampleData();
      API.showToast(res.message || "Sample data seeded successfully!", "success");
      this.checkHealth();
      this.loadView(this.activeView);
    } catch (err) {
      API.showToast("Seeding failed: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  async handleClearDatabase() {
    if (!confirm("WARNING: This will permanently delete ALL nodes and relationships from the Neo4j database. Are you sure you want to proceed?")) {
      return;
    }
    API.setLoading(true);
    try {
      const res = await API.clearDatabase();
      API.showToast(res.message || "Database cleared.", "info");
      this.checkHealth();
      this.loadView(this.activeView);
    } catch (err) {
      API.showToast("Failed to clear database: " + err.message, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 11. Modal Dialog Helper
  bindGlobalModals() {
    const overlay = document.getElementById("globalModalOverlay");
    if (overlay) {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) this.closeModal();
      });
    }
  },

  openModal(title, bodyHtml) {
    const overlay = document.getElementById("globalModalOverlay");
    const titleEl = document.getElementById("globalModalTitle");
    const bodyEl = document.getElementById("globalModalBody");

    if (overlay && titleEl && bodyEl) {
      titleEl.innerText = title;
      bodyEl.innerHTML = bodyHtml;
      overlay.classList.add("active");
    }
  },

  closeModal() {
    const overlay = document.getElementById("globalModalOverlay");
    if (overlay) overlay.classList.remove("active");
  },

  // 12. Delete Confirmation Dialog
  confirmDelete(entityType, id, displayName) {
    const html = `
      <p style="margin-bottom: 16px; font-size: 14px;">
        Are you sure you want to delete ${entityType} <b>${this.escape(displayName)}</b> (<code>${id}</code>)?
      </p>
      <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 20px;">
        This will execute a safe Cypher <code>DETACH DELETE</code> in Neo4j, removing this node and detaching all its graph relationships.
      </p>
      <div class="modal-footer" style="padding-right:0; padding-left:0; margin-bottom:-10px;">
        <button type="button" class="btn" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn btn-danger" onclick="App.executeDelete('${entityType}', '${id}')">Confirm Delete</button>
      </div>
    `;
    this.openModal(`Delete ${entityType}`, html);
  },

  async executeDelete(entityType, id) {
    API.setLoading(true);
    try {
      switch (entityType) {
        case "User":
          await API.deleteUser(id);
          this.loadUsers();
          break;
        case "Asset":
          await API.deleteAsset(id);
          this.loadAssets();
          break;
        case "Nominee":
          await API.deleteNominee(id);
          this.loadNominees();
          break;
        case "Executor":
          await API.deleteExecutor(id);
          this.loadExecutors();
          break;
        case "Plan":
          await API.deletePlan(id);
          this.loadPlans();
          break;
        case "Release":
          await API.deleteRelease(id);
          this.loadReleases();
          break;
      }
      API.showToast(`${entityType} deleted successfully.`, "success");
      this.closeModal();
    } catch (err) {
      API.showToast(`Delete failed: ${err.message}`, "error");
    } finally {
      API.setLoading(false);
    }
  },

  // 13. String & Date Utility Functions
  escape(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  formatDate(dateStr) {
    if (!dateStr) return "—";
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return dateStr;
    }
  },

  getPriorityBadgeClass(priority) {
    switch (priority) {
      case "Critical": return "badge-danger";
      case "High": return "badge-warning";
      case "Medium": return "badge-neutral";
      default: return "badge-neutral";
    }
  }
};

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
