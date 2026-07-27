// =============================================================
// DEMO-ONLY script for the redesign preview.
// It just toggles between the required visual states so you can
// see them all. NONE of this belongs in your real Django app —
// your existing home.js / Leaflet logic drives these elements
// for real. This only shows/hides them for the mockup.
// =============================================================

const els = {
  sidebar: document.getElementById("sidebar"),
  backdrop: document.getElementById("backdrop"),
  routeList: document.getElementById("routeList"),
  routeEmpty: document.getElementById("routeEmpty"),
  routeCount: document.getElementById("routeCount"),

  mapView: document.getElementById("mapView"),
  adminView: document.getElementById("adminView"),
  viewTitle: document.getElementById("viewTitle"),
  mapTabBtn: document.getElementById("mapTabBtn"),
  adminTabBtn: document.getElementById("adminTabBtn"),

  drawingToolbar: document.getElementById("drawingToolbar"),
  drawStats: document.getElementById("drawStats"),
  activeRoute: document.getElementById("activeRoute"),
  editPoints: document.getElementById("editPoints"),
  mapEmptyHint: document.getElementById("mapEmptyHint"),

  detailPanel: document.getElementById("detailPanel"),
  detailTitle: document.getElementById("detailTitle"),
  detailDate: document.getElementById("detailDate"),
  detailBadge: document.getElementById("detailBadge"),
  detailDistance: document.getElementById("detailDistance"),
  detailReason: document.getElementById("detailReason"),
  detailReasonText: document.getElementById("detailReasonText"),
};

const DETAIL = {
  approved: {
    title: "Riverside Connector",
    date: "Submitted Feb 18, 2026",
    badge: "Approved",
    badgeClass: "map-badge map-badge--approved",
    distance: "2.4 km",
    reason: null,
  },
  pending: {
    title: "Hillcrest Loop",
    date: "Submitted Feb 22, 2026",
    badge: "Pending Approval",
    badgeClass: "map-badge map-badge--pending",
    distance: "1.1 km",
    reason: null,
  },
  rejected: {
    title: "Old Mill Path",
    date: "Submitted Feb 15, 2026",
    badge: "Rejected",
    badgeClass: "map-badge map-badge--rejected",
    distance: "3.7 km",
    reason:
      "Route overlaps a private property boundary. Please redraw along the public easement and resubmit.",
  },
};

function showAdmin(isAdmin) {
  els.adminView.hidden = !isAdmin;
  els.mapView.hidden = isAdmin;
  els.viewTitle.textContent = isAdmin ? "Admin Review" : "Map";
  // tab styles
  els.adminTabBtn.className = isAdmin
    ? "rounded-lg px-3 py-1.5 text-sm font-medium text-white bg-accent"
    : "rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100";
  els.mapTabBtn.className = isAdmin
    ? "rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
    : "rounded-lg px-3 py-1.5 text-sm font-medium text-white bg-accent";
}

function resetMap() {
  els.drawingToolbar.hidden = true;
  els.drawStats.hidden = true;
  els.detailPanel.hidden = true;
  els.mapEmptyHint.hidden = true;
  els.activeRoute.style.display = "none";
  els.editPoints.style.display = "none";
}

function fillDetail(key) {
  const d = DETAIL[key];
  els.detailTitle.textContent = d.title;
  els.detailDate.textContent = d.date;
  els.detailBadge.className = d.badgeClass;
  els.detailBadge.textContent = d.badge;
  els.detailDistance.textContent = d.distance;
  if (d.reason) {
    els.detailReason.hidden = false;
    els.detailReasonText.textContent = d.reason;
  } else {
    els.detailReason.hidden = true;
  }
}

function setActiveRouteItem(key) {
  document.querySelectorAll(".route-item").forEach((item) => {
    const on = item.getAttribute("data-route") === key;
    item.classList.toggle("bg-slate-50", on);
    item.classList.toggle("border-slate-200", on);
  });
}

function setState(state) {
  resetMap();

  switch (state) {
    case "empty":
      showAdmin(false);
      els.routeList.hidden = true;
      els.routeEmpty.hidden = false;
      els.routeCount.textContent = "0";
      els.mapEmptyHint.hidden = false;
      setActiveRouteItem(null);
      break;

    case "empty-map": // saved routes exist, none selected
      showAdmin(false);
      els.routeList.hidden = false;
      els.routeEmpty.hidden = true;
      els.routeCount.textContent = "4";
      setActiveRouteItem(null);
      break;

    case "drawing":
      showAdmin(false);
      els.routeList.hidden = false;
      els.routeEmpty.hidden = true;
      els.drawingToolbar.hidden = false;
      els.drawStats.hidden = false;
      els.activeRoute.style.display = "";
      els.editPoints.style.display = "";
      setActiveRouteItem("draft");
      break;

    case "approved":
    case "pending":
    case "rejected":
      showAdmin(false);
      els.routeList.hidden = false;
      els.routeEmpty.hidden = true;
      els.activeRoute.style.display = "";
      els.detailPanel.hidden = false;
      fillDetail(state);
      setActiveRouteItem(state);
      break;

    case "admin":
      showAdmin(true);
      setActiveRouteItem(null);
      break;
  }

  // close mobile sidebar after choosing on small screens
  if (window.innerWidth < 768) toggleSidebar(false);
}

function toggleSidebar(open) {
  els.sidebar.classList.toggle("-translate-x-full", !open);
  els.backdrop.hidden = !open;
}

// expose for inline handlers
window.setState = setState;
window.toggleSidebar = toggleSidebar;

// initial state
setState("approved");
