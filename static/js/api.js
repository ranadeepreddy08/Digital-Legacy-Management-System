/**
 * DIGITAL LEGACY VAULT – DA3
 * API Client & Network Service Layer
 */

const API = {
  baseUrl: "/api",

  // Generic Request Helper
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      const contentType = response.headers.get("content-type");
      const isJson = contentType && contentType.includes("application/json");
      const data = isJson ? await response.json() : await response.text();

      if (!response.ok) {
        const errorMsg = (data && data.detail) ? data.detail : `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, err);
      throw err;
    }
  },

  // UI Toast Notification
  showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "toastContainer";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerText = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  // Loading Indicator
  setLoading(isLoading) {
    const spinner = document.getElementById("globalSpinner");
    if (spinner) {
      if (isLoading) spinner.classList.add("active");
      else spinner.classList.remove("active");
    }
  },

  // Health & Database Status
  getHealth: () => API.request("/health"),
  initSchema: () => API.request("/health/init-schema", { method: "POST" }),

  // Dashboard Endpoints
  getDashboardStats: () => API.request("/dashboard/stats"),
  getDashboardActivity: () => API.request("/dashboard/activity"),
  getUpcomingReleases: () => API.request("/dashboard/upcoming-releases"),

  // Users CRUD
  getUsers: (search = "") => API.request(`/users${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getUser: (id) => API.request(`/users/${encodeURIComponent(id)}`),
  createUser: (data) => API.request("/users", { method: "POST", body: JSON.stringify(data) }),
  updateUser: (id, data) => API.request(`/users/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteUser: (id) => API.request(`/users/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Digital Assets CRUD
  getAssets: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/assets${query ? `?${query}` : ""}`);
  },
  getAsset: (id) => API.request(`/assets/${encodeURIComponent(id)}`),
  createAsset: (data) => API.request("/assets", { method: "POST", body: JSON.stringify(data) }),
  updateAsset: (id, data) => API.request(`/assets/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteAsset: (id) => API.request(`/assets/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Nominees CRUD
  getNominees: (search = "") => API.request(`/nominees${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getNominee: (id) => API.request(`/nominees/${encodeURIComponent(id)}`),
  createNominee: (data) => API.request("/nominees", { method: "POST", body: JSON.stringify(data) }),
  updateNominee: (id, data) => API.request(`/nominees/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteNominee: (id) => API.request(`/nominees/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Trusted Executors CRUD
  getExecutors: (search = "") => API.request(`/executors${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getExecutor: (id) => API.request(`/executors/${encodeURIComponent(id)}`),
  createExecutor: (data) => API.request("/executors", { method: "POST", body: JSON.stringify(data) }),
  updateExecutor: (id, data) => API.request(`/executors/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteExecutor: (id) => API.request(`/executors/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Legacy Plans CRUD
  getPlans: (search = "") => API.request(`/plans${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getPlan: (id) => API.request(`/plans/${encodeURIComponent(id)}`),
  createPlan: (data) => API.request("/plans", { method: "POST", body: JSON.stringify(data) }),
  updatePlan: (id, data) => API.request(`/plans/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deletePlan: (id) => API.request(`/plans/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Scheduled Releases CRUD
  getReleases: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return API.request(`/releases${query ? `?${query}` : ""}`);
  },
  getRelease: (id) => API.request(`/releases/${encodeURIComponent(id)}`),
  createRelease: (data) => API.request("/releases", { method: "POST", body: JSON.stringify(data) }),
  updateRelease: (id, data) => API.request(`/releases/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteRelease: (id) => API.request(`/releases/${encodeURIComponent(id)}`, { method: "DELETE" }),

  // Graph Endpoints
  getGraphTopology: (label = "") => API.request(`/graph/topology${label ? `?label=${encodeURIComponent(label)}` : ""}`),
  getUserGraph: (userId) => API.request(`/graph/user/${encodeURIComponent(userId)}`),
  getOrphanAssets: () => API.request("/graph/orphans"),
  getInheritanceChains: () => API.request("/graph/traversals/inheritance"),
  getExecutorMatrix: () => API.request("/graph/traversals/executors"),

  // Seeding & Reset
  seedSampleData: () => API.request("/seed/sample-data", { method: "POST" }),
  clearDatabase: () => API.request("/seed/clear-database", { method: "POST" })
};
