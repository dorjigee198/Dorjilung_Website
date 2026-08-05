(function () {
  var track = document.querySelector(".dhpl-announce-track");
  if (!track) return;

  var PX_PER_SECOND = 55;
  var MIN_DURATION = 14;

  function setDistance() {
    var singleSetWidth = track.scrollWidth / 2;
    var duration = Math.max(singleSetWidth / PX_PER_SECOND, MIN_DURATION);
    track.style.setProperty("--dhpl-ticker-distance", singleSetWidth + "px");
    track.style.setProperty("--dhpl-ticker-duration", duration + "s");
  }

  setDistance();
  window.addEventListener("resize", setDistance);
})();
