document.addEventListener('DOMContentLoaded', function () {
  var mapEl = document.getElementById('dhpl-project-map');
  var dataEl = document.getElementById('project-locations-data');
  if (!mapEl || !dataEl) return;

  // Shown when Leaflet itself failed to load, or when the tile server
  // is unreachable (blocked network, offline, etc.) — otherwise a
  // failure here just leaves a silent blank box with no explanation.
  function showMapFallback(message) {
    mapEl.innerHTML =
      '<div class="dhpl-map-fallback">' +
      '<p>' + message + '</p>' +
      '<a href="https://www.openstreetmap.org/?mlat=27.7287&mlon=91.1364#map=10/27.5/91.15" target="_blank" rel="noopener">View project area on OpenStreetMap &#8599;</a>' +
      '</div>';
  }

  if (!window.L) {
    showMapFallback('The interactive map could not load.');
    return;
  }

  var locations;
  try {
    locations = JSON.parse(dataEl.textContent);
  } catch (e) {
    return;
  }
  if (!locations || !locations.length) return;

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  var PIN_COLORS = {
    dam_site: '#1fae7d',
    powerhouse: '#0a1f3d',
    main_office: '#d4af37',
    other: '#8792a3',
  };

  var map = L.map(mapEl, { scrollWheelZoom: false });

  // Free basemaps, tried in order. Each is a different provider on a
  // different domain, so a network that blocks one is unlikely to block
  // all — if a provider reports zero successfully-loaded tiles within
  // the grace period, we swap to the next one instead of leaving a
  // permanently blank map. (CARTO's basemaps.cartocdn.com used to be a
  // no-key free option but now silently serves a watermarked "API KEY
  // REQUIRED" tile with an HTTP 200 — which Leaflet can't detect as an
  // error — so it's deliberately not in this list.)
  var TILE_PROVIDERS = [
    {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
      attribution: 'Tiles &copy; Esri',
      maxZoom: 19,
    },
    {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    },
  ];

  var activeLayer = null;
  var tileErrorCount = 0;
  var fallbackTimer = null;

  function tryProvider(index) {
    if (index >= TILE_PROVIDERS.length) {
      showMapFallback('Map tiles could not load — this network may be blocking map services.');
      return;
    }
    if (activeLayer) {
      map.removeLayer(activeLayer);
    }
    tileErrorCount = 0;
    var provider = TILE_PROVIDERS[index];
    activeLayer = L.tileLayer(provider.url, {
      attribution: provider.attribution,
      subdomains: provider.subdomains || 'abc',
      maxZoom: provider.maxZoom,
    }).addTo(map);
    activeLayer.on('tileerror', function () {
      tileErrorCount++;
    });
    window.clearTimeout(fallbackTimer);
    fallbackTimer = window.setTimeout(function () {
      var loadedTiles = mapEl.querySelectorAll('.leaflet-tile-loaded').length;
      if (loadedTiles === 0 && tileErrorCount > 0) {
        tryProvider(index + 1);
      }
    }, 5000);
  }

  tryProvider(0);

  var bounds = [];
  locations.forEach(function (loc) {
    var color = PIN_COLORS[loc.type] || PIN_COLORS.other;
    var icon = L.divIcon({
      className: 'dhpl-map-pin',
      html: '<span style="background:' + color + '"></span>',
      iconSize: [20, 20],
      iconAnchor: [10, 20],
      popupAnchor: [0, -18],
    });
    var marker = L.marker([loc.lat, loc.lng], { icon: icon, title: loc.name }).addTo(map);
    var popupHtml =
      '<strong>' + escapeHtml(loc.name) + '</strong>' +
      (loc.description ? '<p>' + escapeHtml(loc.description) + '</p>' : '');
    marker.bindPopup(popupHtml);
    bounds.push([loc.lat, loc.lng]);
  });

  if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [36, 36] });
  } else {
    map.setView(bounds[0], 12);
  }

  // Let a click "enter" the map before it captures scroll — avoids
  // trapping the page scroll for anyone just scrolling past it.
  map.on('click', function () {
    map.scrollWheelZoom.enable();
  });
  mapEl.addEventListener('mouseleave', function () {
    map.scrollWheelZoom.disable();
  });
});
