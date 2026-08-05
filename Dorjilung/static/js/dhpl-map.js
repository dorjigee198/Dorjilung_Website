document.addEventListener('DOMContentLoaded', function () {
  var mapEl = document.getElementById('dhpl-project-map');
  var dataEl = document.getElementById('project-locations-data');
  if (!mapEl || !dataEl || !window.L) return;

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

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
  }).addTo(map);

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
