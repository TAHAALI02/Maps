// ===================== home.js ============================

const isAuthenticated = window.MAP_CONFIG.isAuthenticated;

function requireLogin() {
    if (!isAuthenticated) {
        window.location.href = window.MAP_CONFIG.urls.login;
        return false;
    }
    return true;
}

const lat = window.MAP_CONFIG.lat;
const lng = window.MAP_CONFIG.lng;
const zoom = window.MAP_CONFIG.zoom;

// Create the map
const map = L.map('map').setView([lat, lng], zoom);

map.on("click", function(e) {
    if (!requireLogin()) return;
});

// ==========================================
// Per-feature-type field configuration
// ==========================================
const FEATURE_FIELD_CONFIG = {
    polyline: {
        label: 'Style Polyline',
        showFields: [],
        buildStyle: function () {
            return {
                color: polyColor.value,
                stroke_width: parseInt(polyWidth.value),
                opacity: parseInt(polyOpacity.value) / 100,
                line_style: currentLineStyle,
            };
        },
        buildGeometry: function (layer) {
            return {
                type: 'LineString',
                coordinates: layer.getLatLngs().map(ll => [ll.lat, ll.lng]),
            };
        },
    },
    polygon: {
        label: 'Style Polygon',
        showFields: ['polygonOnlyFields'],
        buildStyle: function () {
            return {
                color: polyColor.value,
                fill_color: polyFillColor.value,
                stroke_width: parseInt(polyWidth.value),
                opacity: parseInt(polyOpacity.value) / 100,
                fill_opacity: parseInt(polyFillOpacity.value) / 100,
                line_style: currentLineStyle,
            };
        },
        buildGeometry: function (layer) {
            const ring = layer.getLatLngs()[0];
            return {
                type: 'Polygon',
                coordinates: ring.map(ll => [ll.lat, ll.lng]),
            };
        },
    },
};

function applyFieldVisibility(featureType) {
    const config = FEATURE_FIELD_CONFIG[featureType];
    const allBlocks = ['polygonOnlyFields'];
    allBlocks.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = config.showFields.includes(id) ? 'block' : 'none';
    });
}

let currentFeatureType = 'polyline';

// ==================== Add a marker ====================
var myIcon = L.icon({
    iconUrl: window.MAP_CONFIG.icons.pointer,
    iconSize: [38, 45],
});
var myIcon2 = L.icon({
    iconUrl: window.MAP_CONFIG.icons.marker,
    iconSize: [38, 45],
});

var marker = L.marker([lat, lng], { draggable: true });

marker.on("dragend", function(e){
    var position = marker.getLatLng();
    fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.lat}&lon=${position.lng}`
    ).then(response => response.json())
     .then(data => {
        let place = data.address.city ||
                    data.address.town ||
                    data.address.village ||
                    data.address.state ||
                    "unknown Location";
        marker.bindPopup(place).openPopup();
     });
});

// ======================= Tiles =====================
const apiKey = window.MAP_CONFIG.apiKey;

var maptiler = L.tileLayer(
    `https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=${apiKey}`,
    { tileSize: 512, zoomOffset: -1, attribution: '&copy; MapTiler &copy; OpenStreetMap contributors' }
);
maptiler.addTo(map);

var maptilerSatellite = L.tileLayer(
    `https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key=${apiKey}`,
    { tileSize: 512, zoomOffset: -1, attribution: '&copy; MapTiler' }
);

var maptilerBlack = L.tileLayer(
    `https://api.maptiler.com/maps/streets-v4-dark/{z}/{x}/{y}.png?key=${apiKey}`,
    { tileSize: 512, zoomOffset: -1, attribution: '&copy; MapTiler' }
);

var baseLayers = {
    "Streets": maptiler,
    "Satellite": maptilerSatellite,
    "Night": maptilerBlack
};
L.control.layers(baseLayers, null, { position: 'bottomleft', collapsed: true }).addTo(map);

// ==================== Layer Groups =====================
var noLabelsBasemap = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
});
var withLabelsBasemap = maptiler;

var approvedRoadsLayer = new L.FeatureGroup();
var approvedPropertiesLayer = new L.FeatureGroup();
var pendingRoadsLayer = new L.FeatureGroup();
var pendingPropertiesLayer = new L.FeatureGroup();

map.addLayer(approvedRoadsLayer);
map.addLayer(approvedPropertiesLayer);
map.addLayer(pendingRoadsLayer);
map.addLayer(pendingPropertiesLayer);

// MapLayerToggles control
var MapLayerToggles = L.Control.extend({
    options: { position: 'bottomleft' },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'leaflet-bar');
        L.DomEvent.disableClickPropagation(container);
        L.DomEvent.disableScrollPropagation(container);

        var btn = L.DomUtil.create('button', 'map-layer-toggle-btn', container);
        btn.title = 'Layer Options';
        btn.type = 'button';
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              <polyline points="2 17 12 22 22 17"/>
              <polyline points="2 12 12 17 22 12"/>
            </svg>`;

        var panel = L.DomUtil.create('div', 'map-layer-toggle-panel', container);

        var lblLabel = L.DomUtil.create('label', '', panel);
        var cbLabels = L.DomUtil.create('input', '', lblLabel);
        cbLabels.type = 'checkbox'; cbLabels.checked = true;
        cbLabels.id = 'toggleBasemapLabels';
        lblLabel.appendChild(document.createTextNode(' Basemap Labels'));

        var roadsLabel = L.DomUtil.create('label', '', panel);
        var cbRoads = L.DomUtil.create('input', '', roadsLabel);
        cbRoads.type = 'checkbox'; cbRoads.checked = true;
        cbRoads.id = 'togglePendingRoads';
        roadsLabel.appendChild(document.createTextNode(' Pending Roads'));

        var propsLabel = L.DomUtil.create('label', '', panel);
        var cbProps = L.DomUtil.create('input', '', propsLabel);
        cbProps.type = 'checkbox'; cbProps.checked = true;
        cbProps.id = 'togglePendingProperties';
        propsLabel.appendChild(document.createTextNode(' Pending Properties'));

        L.DomEvent.on(btn, 'click', function (e) {
            L.DomEvent.stopPropagation(e);
            panel.classList.toggle('open');
        });

        L.DomEvent.on(document, 'click', function () {
            panel.classList.remove('open');
        });

        L.DomEvent.on(cbLabels, 'change', function () {
            if (cbLabels.checked) {
                map.removeLayer(noLabelsBasemap);
                withLabelsBasemap.addTo(map);
            } else {
                map.removeLayer(withLabelsBasemap);
                noLabelsBasemap.addTo(map);
            }
        });
        L.DomEvent.on(cbRoads, 'change', function () {
            if (cbRoads.checked) map.addLayer(pendingRoadsLayer);
            else map.removeLayer(pendingRoadsLayer);
        });
        L.DomEvent.on(cbProps, 'change', function () {
            if (cbProps.checked) map.addLayer(pendingPropertiesLayer);
            else map.removeLayer(pendingPropertiesLayer);
        });

        return container;
    }
});
map.addControl(new MapLayerToggles());

// ===================== Label visibility (zoom-based) =====================
const LABEL_MIN_ZOOM = 17;

function updateLabelVisibility() {
    const show = map.getZoom() >= LABEL_MIN_ZOOM;
    [approvedRoadsLayer, approvedPropertiesLayer].forEach(group => {
        group.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                const el = layer.getElement();
                if (el) el.style.display = show ? '' : 'none';
            }
        });
    });
}

map.on('zoomend', updateLabelVisibility);

// -========================================================
// In that we can add or remove extra features
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    draw: {
        polyline: { shapeOptions: { color: '#181a1a', weight: 4 } },
        polygon:  { shapeOptions: { color: '#181a1a', weight: 4 } },
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false
    },
    edit: {
        featureGroup: drawnItems,
        edit: false,
        remove: false
    }
});

if (isAuthenticated) {
    map.addControl(drawControl);
}

//=============================================================
let currentUserId = null;
let editingRequestId = null;
let canEditRoads = false;
let canDeleteRoads = false;
let canEditProperties = false;
let canDeleteProperties = false;
let myDraftFeatures = [];
let cachedApprovedFeatures = [];

fetch(window.MAP_CONFIG.urls.getApprovedFeatures)
    .then(r => { if (!r.ok) throw new Error("Unauthorized or server error"); return r.json(); })
    .then(data => {
        currentUserId = data.current_user_id;
        canEditRoads = data.can_edit_roads;
        canDeleteRoads = data.can_delete_roads;
        canEditProperties = data.can_edit_properties;
        canDeleteProperties = data.can_delete_properties;

        cachedApprovedFeatures = data.features;
        data.features.forEach(f => renderFeature(f, 'published'));
        return fetch(window.MAP_CONFIG.urls.getMyDraftFeatures);
    })
    .then(r => r.json())
    .then(data => {
        myDraftFeatures = data.features;
        data.features.forEach(f => renderFeature(f, 'draft'));
        requestAnimationFrame(updateLabelVisibility);
    })
    .catch(err => console.error("Could not load features", err));

// =========================================================
const FEATURE_TYPE_LABELS = {
    polyline: 'Road',
    polygon: 'Property',
};

function showFeaturePopup(layer, feature, isMine, hasEditInProgress) {
    const template = document.getElementById('featurePopupTemplate');
    const node = template.content.cloneNode(true);
    const typeLabel = FEATURE_TYPE_LABELS[feature.feature_type] || 'Feature';

    const avatarImg = node.querySelector('.road-popup-avatar');
    const avatarFallback = node.querySelector('.road-popup-avatar-fallback');
    const editBtn = node.querySelector('.road-popup-edit-btn');
    const deleteBtn = node.querySelector('.road-popup-delete-btn');
    const isSuperuser = window.MAP_CONFIG.isSuperuser;

    if (feature.creator_profile_image) {
        avatarImg.src = feature.creator_profile_image;
        avatarImg.style.display = 'block';
    } else {
        avatarFallback.textContent = feature.creator_name.charAt(0).toUpperCase();
        avatarFallback.style.display = 'flex';
    }

    node.querySelector('.road-popup-name').textContent = feature.creator_name;
    node.querySelector('.road-popup-username').textContent = '@' + feature.creator_username;
    node.querySelector('.road-popup-title').textContent = feature.name || ('Unnamed ' + typeLabel);

    const descEl = node.querySelector('.road-popup-description');
    if (feature.description) {
        descEl.textContent = feature.description;
        descEl.style.display = 'block';
    }

    node.querySelector('.road-popup-meta').textContent = 'Approved: ' + (feature.published_at || 'Unknown');

    const isLine = feature.feature_type === 'polyline';
    const typeCanEdit = isLine ? canEditRoads : canEditProperties;
    const typeCanDelete = isLine ? canDeleteRoads : canDeleteProperties;
    // const canDelete = isSuperuser || (isMine && typeCanDelete);
    // const canEdit   = isSuperuser || (isMine && typeCanDelete);
    const canEdit = isSuperuser || (isMine && typeCanEdit);
    const canDelete = isSuperuser || (isMine && typeCanDelete);

    if (canEdit) {
        editBtn.textContent = hasEditInProgress ? 'View pending edit' : ('Edit ' + typeLabel.toLowerCase());
        editBtn.style.display = 'block';
        editBtn.addEventListener('click', () => {
            layer.closePopup();
            const pendingEdit = hasEditInProgress
                            ? myDraftFeatures.find(d => d.original_feature_id === feature.id)
                            : null;
            openEditPanel(layer, pendingEdit || feature, hasEditInProgress ? 'pending' : 'approved');
        });
    } else {
        editBtn.style.display = 'none';
    }

    if (canDelete) {
        deleteBtn.textContent = 'Delete ' + typeLabel;
        deleteBtn.style.display = 'block';
        deleteBtn.addEventListener('click', () => {
            const confirmMsg = isSuperuser
                ? `Permanently delete "${feature.name || ('this ' + typeLabel.toLowerCase())}"? This cannot be undone.`
                : `Send a deletion request for "${feature.name || ('this ' + typeLabel.toLowerCase())}"? An admin will need to approve it.`;
            if (!confirm(confirmMsg)) return;

            deleteBtn.disabled = true;
            deleteBtn.textContent = 'Processing...';

            fetch(`/features/${feature.id}/delete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() }
            })
            .then(r => r.json())
            .then(data => {
                layer.closePopup();
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message || 'Something went wrong.');
                    deleteBtn.disabled = false;
                    deleteBtn.textContent = isSuperuser ? ('Delete ' + typeLabel) : 'Request Deletion';
                }
            })
            .catch(() => {
                alert('A network error occurred.');
                deleteBtn.disabled = false;
                deleteBtn.textContent = isSuperuser ? 'Delete Road' : 'Request Deletion';
            });
        });
    } else {
        deleteBtn.style.display = 'none';
    }

    const wrapper = document.createElement('div');
    wrapper.appendChild(node);
    layer.bindPopup(wrapper).openPopup();
}

// ==========================================
// Generic feature rendering (this for all feature polyline or polygon ot etc)
// ==========================================
function buildLeafletLayer(feature, style) {
    switch (feature.feature_type) {
        case 'polygon':
            return L.polygon(feature.geometry.coordinates, style);
        case 'polyline':
        default: {
            let coords = feature.geometry.coordinates;
            if (feature.feature_type === 'polyline' && coords.length > 1) {
                const first = coords[0];
                const last = coords[coords.length - 1];
                if (last[1] < first[1]) {
                    coords = coords.slice().reverse();
                }
            }
            return L.polyline(coords, style);
        }
    }
}

// function getPolygonCentroid(pts) {
//     let first = pts[0], last = pts[pts.length - 1];
//     if (first.lat !== last.lat || first.lng !== last.lng) pts.push(first);
//     let twicearea = 0, x = 0, y = 0, nPts = pts.length, p1, p2, f;
//     for (let i = 0, j = nPts - 1; i < nPts; j = i++) {
//         p1 = pts[i]; p2 = pts[j];
//         f = (p1.lng * p2.lat - p2.lng * p1.lat);
//         twicearea += f;
//         x += (p1.lng + p2.lng) * f;
//         y += (p1.lat + p2.lat) * f;
//     }
//     f = twicearea * 3;
//     if (f === 0) return L.latLng(pts[0].lat, pts[0].lng);
//     return L.latLng(y / f, x / f);
// }

function getPolylineMidpoint(latlngs) {
    const mid = Math.floor((latlngs.length - 1) / 2);
    if (latlngs.length % 2 === 1) {
        return latlngs[mid];
    }
    const a = latlngs[mid], b = latlngs[mid + 1];
    return L.latLng((a.lat + b.lat) / 2, (a.lng + b.lng) / 2);
}


// function getVertexAverage(latlngs) {
//     const pts = latlngs[0] && Array.isArray(latlngs[0]) ? latlngs[0] : latlngs;
//     let sumLat = 0, sumLng = 0;
//     pts.forEach(p => { sumLat += p.lat; sumLng += p.lng; });
//     return L.latLng(sumLat / pts.length, sumLng / pts.length);
// }


function renderFeature(feature, mode) {
    const s = feature.style || {};
    const style = getLeafletStyle(s.color, s.stroke_width, s.opacity, s.line_style);
    if (feature.feature_type === 'polygon') {
        style.fillColor = s.fill_color;
        style.fillOpacity = s.fill_opacity;
    }

    if (mode === 'draft') {
        if (feature.delete_requested) {
            style.color = '#dc2626';
            style.dashArray = '4, 4';
            style.opacity = 0.5;
        } else {
            style.dashArray = feature.status === 'rejected' ? '2, 6' : '6, 6';
            if (feature.status === 'rejected') style.opacity = 0.35;
        }
    }

    const layer = buildLeafletLayer(feature, style);

    if (mode === 'published' && feature.name) {
        const isLine = feature.feature_type === 'polyline';
        const anchor = isLine
            ? getPolylineMidpoint(feature.geometry.coordinates.map(c => L.latLng(c[0], c[1])))
            : layer.getBounds().getCenter();
            // : getVertexAverage(feature.geometry.coordinates.map(c => L.latLng(c[0], c[1])));
            
        const targetGroup = isLine ? approvedRoadsLayer : approvedPropertiesLayer;

        targetGroup.addLayer(L.marker(anchor, {
            icon: L.divIcon({
                className: 'feature-label-marker',
                html: `<div>${feature.name}</div>`,
                iconSize: [0, 0]
            }),
            interactive: false
        }));
    }

    let targetLayerGroup;
    if (feature.feature_type === 'polygon') {
        targetLayerGroup = (mode === 'published') ? approvedPropertiesLayer : pendingPropertiesLayer;
    } else {
        targetLayerGroup = (mode === 'published') ? approvedRoadsLayer : pendingRoadsLayer;
    }
    

    if (mode === 'published') {
        const isMine = feature.creator_id === currentUserId;
        const hasEditInProgress = feature.current_status !== 'approved';
        layer.on('click', function () {
            showFeaturePopup(layer, feature, isMine, hasEditInProgress);
        });
        layer.on('popupopen', function () {
            if (layer.setStyle) layer.setStyle({ color: '#00ffff', fillColor: '#00ffff' });
        });
        layer.on('popupclose', function () {
            if (layer.setStyle) layer.setStyle(style);
        });
    } else {
        if (feature.delete_requested) {
            layer.bindTooltip('Deletion pending approval', { sticky: true, className: 'road-tooltip-pending' });
        } else {
            const tooltipClass = feature.status === 'rejected' ? 'road-tooltip-rejected' : 'road-tooltip-pending';
            layer.bindTooltip(`${feature.status} — click to edit`, { sticky: true, className: tooltipClass });
            layer.on('click', () => {
                layer._realStyle = { color: style.color, fillColor: style.fillColor };
                if (layer.setStyle) layer.setStyle({ color: '#00ffff', fillColor: '#00ffff' });
                openEditPanel(layer, feature, feature.status);
            });
        }
    }

    targetLayerGroup.addLayer(layer);
}

map.on('zoomend', () => {
    // placedLabelBoxes = [];
    approvedRoadsLayer.clearLayers();
    approvedPropertiesLayer.clearLayers();
    cachedApprovedFeatures.forEach(f => renderFeature(f, 'published'));
    // updateLabelVisibility();
    requestAnimationFrame(updateLabelVisibility);
});

// ==========================================
// Polyline Drawing & Live Editing Workflow
// ==========================================
let currentPolyline = null;
let currentLineStyle = 'solid';

function getLeafletStyle(color, weight, opacity, styleType) {
    let dashArray = null;
    if (styleType === 'dashed') dashArray = '10, 10';
    if (styleType === 'dotted') dashArray = '2, 8';

    return {
        color: color,
        weight: weight,
        opacity: opacity,
        dashArray: dashArray,
        lineCap: 'round',
        lineJoin: 'round'
    };
}

map.on(L.Draw.Event.CREATED, function (e) {
    const layer = e.layer;
    drawnItems.addLayer(layer);

    if (e.layerType === "polyline" || e.layerType === "polygon") {
        currentPolyline = layer;
        currentFeatureType = e.layerType;

        document.getElementById("stylePanelTitle").textContent =
            `Style ${FEATURE_TYPE_LABELS[currentFeatureType]}`;

        applyFieldVisibility(currentFeatureType);
        updatePolylineFromPanel();

        const panel = document.getElementById("stylePanel");
        panel.classList.add("open");

        document.getElementById("polyName").value = '';
        document.getElementById("polyDesc").value = '';
        document.getElementById("polylineStatusBadge").style.display = "none";
        document.getElementById("polylineErrors").style.display = "none";
        document.getElementById("saveStyleBtn").disabled = false;
        document.getElementById("saveStyleBtn").textContent = (currentFeatureType === 'polyline') ? "Submit Request" : "Save Request";

        setPanelFieldsReadOnly(false);
        if (currentPolyline.editing) currentPolyline.editing.enable();
    } else {
        drawnItems.removeLayer(layer);
        alert("This shape type isn't supported yet.");
    }
});

const polyColor = document.getElementById("polyColor");
const polyColorHex = document.getElementById("polyColorHex");
const polyWidth = document.getElementById("polyWidth");
const polyWidthVal = document.getElementById("polyWidthVal");
const polyOpacity = document.getElementById("polyOpacity");
const polyOpacityVal = document.getElementById("polyOpacityVal");
const typeBtns = document.querySelectorAll("#polyLineType .toggle-btn");

const polyFillColor = document.getElementById("polyFillColor");
const polyFillColorHex = document.getElementById("polyFillColorHex");
const polyFillOpacity = document.getElementById("polyFillOpacity");
const polyFillOpacityVal = document.getElementById("polyFillOpacityVal");

function updatePolylineFromPanel() {
    if (!currentPolyline) return;
    polyColorHex.textContent = polyColor.value.toUpperCase();
    polyWidthVal.textContent = polyWidth.value + "px";
    polyOpacityVal.textContent = polyOpacity.value + "%";

    const style = getLeafletStyle(
        polyColor.value,
        parseInt(polyWidth.value),
        parseInt(polyOpacity.value) / 100,
        currentLineStyle
    );

    if (currentFeatureType === 'polygon') {
        polyFillColorHex.textContent = polyFillColor.value.toUpperCase();
        polyFillOpacityVal.textContent = polyFillOpacity.value + "%";
        style.fillColor = polyFillColor.value;
        style.fillOpacity = parseInt(polyFillOpacity.value) / 100;
    }

    currentPolyline.setStyle(style);

    if (currentFeatureType === 'polyline') {
        const roadName = document.getElementById("polyName").value;
        if (roadName && currentPolyline.setText) {
            currentPolyline.setText(roadName, {
                center: true, offset: 0,
                attributes: { fill: '#1a1a1a', 'font-weight': 'bold', 'font-size': '14',
                    style: 'text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;' }
            });
        } else if (!roadName && currentPolyline.setText) {
            currentPolyline.setText(null);
        }
    }
}

document.getElementById("polyName").addEventListener('input', updatePolylineFromPanel);
polyColor.addEventListener('input', updatePolylineFromPanel);
polyWidth.addEventListener('input', updatePolylineFromPanel);
polyOpacity.addEventListener('input', updatePolylineFromPanel);
polyFillColor.addEventListener('input', updatePolylineFromPanel);
polyFillOpacity.addEventListener('input', updatePolylineFromPanel);

function openEditPanel(featureLayer, feature, status) {
    editingRequestId = feature.id;
    currentFeatureType = feature.feature_type || 'polyline';

    document.getElementById("stylePanelTitle").textContent =
        `Style ${FEATURE_TYPE_LABELS[currentFeatureType]}`;

    applyFieldVisibility(currentFeatureType);
    currentPolyline = featureLayer;

    const s = feature.style || {};

    document.getElementById("polyName").value = feature.name || '';
    document.getElementById("polyDesc").value = feature.description || '';
    polyColor.value = s.color;
    polyColorHex.textContent = s.color.toUpperCase();
    polyWidth.value = s.stroke_width;
    polyWidthVal.textContent = s.stroke_width + "px";
    polyOpacity.value = Math.round(s.opacity * 100);
    polyOpacityVal.textContent = Math.round(s.opacity * 100) + "%";
    currentLineStyle = s.line_style;
    typeBtns.forEach(b => b.classList.toggle('active', b.dataset.style === s.line_style));

    if (currentFeatureType === 'polygon') {
        polyFillColor.value = s.fill_color;
        polyFillColorHex.textContent = s.fill_color.toUpperCase();
        polyFillOpacity.value = Math.round((s.fill_opacity || 0) * 100);
        polyFillOpacityVal.textContent = Math.round((s.fill_opacity || 0) * 100) + "%";
    }

    const readOnly = status === "pending";

    document.getElementById("polylineStatusBadge").style.display = readOnly ? "flex" : "none";
    document.getElementById("polylineErrors").style.display = "none";

    setPanelFieldsReadOnly(readOnly);

    if (!readOnly && currentPolyline.editing) {
        currentPolyline.editing.enable();
    }

    document.getElementById("stylePanel").classList.add("open");
}

function setPanelFieldsReadOnly(readOnly) {
    document.getElementById("polyName").readOnly = readOnly;
    document.getElementById("polyDesc").readOnly = readOnly;
    polyColor.disabled = readOnly;
    polyWidth.disabled = readOnly;
    polyOpacity.disabled = readOnly;
    polyFillColor.disabled = readOnly;
    polyFillOpacity.disabled = readOnly;
    typeBtns.forEach(btn => { btn.disabled = readOnly; });

    const saveBtn = document.getElementById("saveStyleBtn");
    saveBtn.disabled = readOnly;
    saveBtn.textContent = readOnly ? "Waiting for Admin Approval" : (currentFeatureType === 'polyline' ? "Submit Changes" : "Save Changes");

    document.getElementById("stylePanel").classList.toggle("read-only-mode", readOnly);
}

map.on('draw:editvertex', function(e) {
    if (currentPolyline) {
        updatePolylineFromPanel();
    }
});

polyColor.addEventListener('input', updatePolylineFromPanel);
polyWidth.addEventListener('input', updatePolylineFromPanel);
polyOpacity.addEventListener('input', updatePolylineFromPanel);

typeBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        typeBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentLineStyle = e.target.dataset.style;
        updatePolylineFromPanel();
    });
});

function closePolylinePanel() {
    document.getElementById("stylePanel").classList.remove("open");

    if (editingRequestId && currentPolyline) {
        if (currentPolyline.editing && currentPolyline.editing.enabled()) {
            currentPolyline.editing.disable();
        }
        if (currentPolyline._originalLatLngs) {
            currentPolyline.setLatLngs(currentPolyline._originalLatLngs);
        }
        if (currentPolyline._realStyle && currentPolyline.setStyle) {
            currentPolyline.setStyle(currentPolyline._realStyle);
        }
    } else if (!editingRequestId && document.getElementById("polylineStatusBadge").style.display === "none") {
        if (currentPolyline) drawnItems.removeLayer(currentPolyline);
    }

    currentPolyline = null;
    editingRequestId = null;
}
document.getElementById("closePanel").addEventListener("click", closePolylinePanel);
document.getElementById("cancelStyleBtn").addEventListener("click", closePolylinePanel);

function getCsrfToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

document.getElementById("saveStyleBtn").addEventListener("click", function() {
    if (!currentPolyline) return;

    if (editingRequestId && currentPolyline.editing.enabled()) {
        currentPolyline.editing.disable();
    }

    const btn = this;
    btn.disabled = true;
    btn.textContent = "Saving...";
    document.getElementById("polylineErrors").style.display = "none";

    const config = FEATURE_FIELD_CONFIG[currentFeatureType];
    const geometry = config.buildGeometry(currentPolyline);
    const style = config.buildStyle();

    const payload = {
        feature_type: currentFeatureType,
        name: document.getElementById("polyName").value,
        description: document.getElementById("polyDesc").value,
        geometry: geometry,
        style: style
    };

    const url = editingRequestId
        ? `/features/${editingRequestId}/edit/`
        : window.MAP_CONFIG.urls.submitFeatureRequest;

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
        body: JSON.stringify(payload)
    })
    .then(async response => {
        const data = await response.json();
        if (!response.ok) {
            btn.disabled = false;
            btn.textContent = currentFeatureType === 'polyline' ? "Submit Changes" : "Save Changes";
            const errDiv = document.getElementById("polylineErrors");
            errDiv.style.display = "block";
            try {
                const errors = JSON.parse(data.errors);
                let html = '<ul>';
                for (const field in errors) errors[field].forEach(e => html += `<li>${e.message}</li>`);
                html += '</ul>';
                errDiv.innerHTML = html;
            } catch(e) { errDiv.textContent = "Validation failed. Check your inputs."; }
        } else {
            document.getElementById("stylePanel").classList.remove("open");
            editingRequestId = null;
            currentPolyline = null;
            location.reload();
        }
    })
    .catch(error => {
        console.error("Error:", error);
        btn.disabled = false;
        btn.textContent = currentFeatureType === 'polyline' ? "Submit Changes" : "Save Changes";
        alert("A network error occurred.");
    });
});