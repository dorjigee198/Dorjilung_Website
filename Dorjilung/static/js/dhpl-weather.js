document.addEventListener('DOMContentLoaded', function () {
  var widget = document.getElementById('dhpl-weather-widget');
  if (!widget) return;

  var lat = widget.dataset.lat;
  var lng = widget.dataset.lng;

  // Open-Meteo — free, keyless weather API. No signup, no billing.
  var url =
    'https://api.open-meteo.com/v1/forecast' +
    '?latitude=' + encodeURIComponent(lat) +
    '&longitude=' + encodeURIComponent(lng) +
    '&current=temperature_2m,precipitation,wind_speed_10m,wind_direction_10m,weather_code' +
    '&daily=precipitation_probability_max' +
    '&timezone=Asia%2FThimphu';

  var COMPASS = [
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW',
  ];

  function degToCompass(deg) {
    return COMPASS[Math.round(deg / 22.5) % 16];
  }

  // WMO weather codes (used by Open-Meteo) collapsed into icon families.
  function weatherCondition(code) {
    if (code === 0) return { label: 'Clear Sky', icon: 'sun' };
    if (code === 1 || code === 2) return { label: 'Partly Cloudy', icon: 'cloud-sun' };
    if (code === 3) return { label: 'Overcast', icon: 'cloud' };
    if (code === 45 || code === 48) return { label: 'Foggy', icon: 'fog' };
    if (code >= 51 && code <= 57) return { label: 'Drizzle', icon: 'rain-light' };
    if (code >= 61 && code <= 67) return { label: 'Rain', icon: 'rain' };
    if (code >= 71 && code <= 77) return { label: 'Snow', icon: 'snow' };
    if (code >= 80 && code <= 82) return { label: 'Rain Showers', icon: 'rain' };
    if (code >= 85 && code <= 86) return { label: 'Snow Showers', icon: 'snow' };
    if (code >= 95) return { label: 'Thunderstorm', icon: 'storm' };
    return { label: 'Conditions Unavailable', icon: 'cloud' };
  }

  var WEATHER_ICONS = {
    sun:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon dhpl-wicon-sun">' +
      '<g class="dhpl-sun-rays" stroke="#e8a93c" stroke-width="4" stroke-linecap="round">' +
      '<line x1="50" y1="6" x2="50" y2="18"/><line x1="50" y1="82" x2="50" y2="94"/>' +
      '<line x1="6" y1="50" x2="18" y2="50"/><line x1="82" y1="50" x2="94" y2="50"/>' +
      '<line x1="19" y1="19" x2="27" y2="27"/><line x1="73" y1="73" x2="81" y2="81"/>' +
      '<line x1="19" y1="81" x2="27" y2="73"/><line x1="73" y1="27" x2="81" y2="19"/>' +
      '</g><circle cx="50" cy="50" r="20" fill="#f5b942"/></svg>',
    'cloud-sun':
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<g class="dhpl-sun-rays" stroke="#e8a93c" stroke-width="4" stroke-linecap="round" opacity="0.85">' +
      '<line x1="34" y1="8" x2="34" y2="18"/><line x1="10" y1="32" x2="18" y2="32"/>' +
      '<line x1="15" y1="13" x2="21" y2="19"/></g>' +
      '<circle cx="34" cy="32" r="15" fill="#f5b942"/>' +
      '<g class="dhpl-cloud-drift"><ellipse cx="52" cy="62" rx="24" ry="15" fill="#cbd5e1"/>' +
      '<ellipse cx="70" cy="56" rx="18" ry="15" fill="#e2e8f0"/></g></svg>',
    cloud:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<g class="dhpl-cloud-drift"><ellipse cx="42" cy="55" rx="24" ry="15" fill="#cbd5e1"/>' +
      '<ellipse cx="62" cy="48" rx="19" ry="17" fill="#e2e8f0"/>' +
      '<ellipse cx="68" cy="60" rx="17" ry="13" fill="#cbd5e1"/></g></svg>',
    fog:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<g class="dhpl-fog-lines" stroke="#a8b3c4" stroke-width="5" stroke-linecap="round">' +
      '<line x1="18" y1="38" x2="82" y2="38"/><line x1="12" y1="52" x2="88" y2="52"/>' +
      '<line x1="20" y1="66" x2="80" y2="66"/></g></svg>',
    'rain-light':
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<ellipse cx="50" cy="42" rx="26" ry="16" fill="#9aa9bd"/>' +
      '<g class="dhpl-rain-drops" stroke="#4a90d9" stroke-width="3" stroke-linecap="round">' +
      '<line class="dhpl-drop dhpl-drop-1" x1="42" y1="66" x2="40" y2="76"/>' +
      '<line class="dhpl-drop dhpl-drop-2" x1="58" y1="66" x2="56" y2="76"/></g></svg>',
    rain:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<ellipse cx="50" cy="38" rx="28" ry="17" fill="#8b9bb0"/>' +
      '<g class="dhpl-rain-drops" stroke="#4a90d9" stroke-width="3.5" stroke-linecap="round">' +
      '<line class="dhpl-drop dhpl-drop-1" x1="32" y1="62" x2="29" y2="74"/>' +
      '<line class="dhpl-drop dhpl-drop-2" x1="50" y1="62" x2="47" y2="74"/>' +
      '<line class="dhpl-drop dhpl-drop-3" x1="68" y1="62" x2="65" y2="74"/></g></svg>',
    snow:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<ellipse cx="50" cy="38" rx="26" ry="16" fill="#b6c0cf"/>' +
      '<g class="dhpl-snow-flakes" fill="#cfe0f0">' +
      '<circle class="dhpl-flake dhpl-flake-1" cx="36" cy="66" r="3"/>' +
      '<circle class="dhpl-flake dhpl-flake-2" cx="50" cy="70" r="3"/>' +
      '<circle class="dhpl-flake dhpl-flake-3" cx="64" cy="66" r="3"/></g></svg>',
    storm:
      '<svg viewBox="0 0 100 100" class="dhpl-wicon">' +
      '<ellipse cx="50" cy="36" rx="27" ry="16" fill="#6b7688"/>' +
      '<polygon class="dhpl-lightning" points="52,54 40,74 48,74 44,90 62,66 52,66" fill="#f5c343"/></svg>',
  };

  function stat(label, value) {
    return (
      '<div class="dhpl-weather-stat">' +
      '<span class="dhpl-weather-stat-label">' + label + '</span>' +
      '<span class="dhpl-weather-stat-value">' + value + '</span>' +
      '</div>'
    );
  }

  fetch(url)
    .then(function (res) {
      if (!res.ok) throw new Error('Weather request failed');
      return res.json();
    })
    .then(function (data) {
      var current = data.current || {};
      var rainProb =
        data.daily &&
        data.daily.precipitation_probability_max &&
        data.daily.precipitation_probability_max.length
          ? data.daily.precipitation_probability_max[0]
          : null;

      var condition = weatherCondition(current.weather_code);
      var windDeg = typeof current.wind_direction_10m === 'number' ? current.wind_direction_10m : 0;
      var windDir = degToCompass(windDeg);

      var html =
        '<div class="dhpl-weather-hero">' +
        '<div class="dhpl-weather-hero-icon">' + (WEATHER_ICONS[condition.icon] || WEATHER_ICONS.cloud) + '</div>' +
        '<div class="dhpl-weather-hero-text">' +
        '<span class="dhpl-weather-hero-temp">' + Math.round(current.temperature_2m) + '°C</span>' +
        '<span class="dhpl-weather-hero-label">' + condition.label + '</span>' +
        '</div>' +
        '<div class="dhpl-wind-compass" aria-hidden="true">' +
        '<svg viewBox="0 0 100 100">' +
        '<circle cx="50" cy="50" r="44" fill="none" stroke="#e2e8f0" stroke-width="2"/>' +
        '<text x="50" y="16" text-anchor="middle">N</text>' +
        '<text x="88" y="54" text-anchor="middle">E</text>' +
        '<text x="50" y="96" text-anchor="middle">S</text>' +
        '<text x="12" y="54" text-anchor="middle">W</text>' +
        '<g class="dhpl-wind-needle" style="transform: rotate(' + windDeg + 'deg)">' +
        '<line x1="50" y1="50" x2="50" y2="20" stroke="#d4af37" stroke-width="4" stroke-linecap="round"/>' +
        '<circle cx="50" cy="20" r="4" fill="#d4af37"/>' +
        '</g>' +
        '</svg>' +
        '<span class="dhpl-wind-compass-label">' + windDir + '</span>' +
        '</div>' +
        '</div>' +
        '<div class="dhpl-weather-grid">' +
        stat('Wind Speed', Math.round(current.wind_speed_10m) + ' km/h') +
        stat('Wind Direction', windDir + ' (' + Math.round(windDeg) + '°)') +
        stat('Current Rainfall', current.precipitation + ' mm') +
        stat('Rain Chance Today', rainProb !== null ? rainProb + '%' : '—') +
        '</div>' +
        '<p class="dhpl-weather-source">Live conditions near the dam site, via ' +
        '<a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a>. ' +
        'Updated ' + new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) + '.</p>';

      widget.innerHTML = html;
    })
    .catch(function () {
      widget.innerHTML =
        '<div class="dhpl-weather-placeholder">' +
        '<p>Live weather data is temporarily unavailable. Please try again shortly.</p>' +
        '</div>';
    });
});
