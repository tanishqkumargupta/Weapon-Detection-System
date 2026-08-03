/* =============================================================
   WDS Camera Configuration JS
   Purely presentational: shows/hides the IP camera URL field,
   and gives the existing /video_feed <img> stream a friendly
   placeholder if it fails to load (e.g. no webcam available in
   this environment). The stream mechanism itself is untouched.
============================================================= */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var radios = document.querySelectorAll('input[name="camera_type"]');
    var ipField = document.querySelector("[data-ip-field]");
    var radioCards = document.querySelectorAll(".radio-card");

    function syncIpField() {
      var selected = document.querySelector('input[name="camera_type"]:checked');
      var isIp = selected && selected.value === "ip";
      if (ipField) ipField.classList.toggle("is-visible", !!isIp);

      radioCards.forEach(function (card) {
        var input = card.querySelector("input");
        card.classList.toggle("is-active", input && input.checked);
      });
    }

    radios.forEach(function (radio) {
      radio.addEventListener("change", syncIpField);
    });
    syncIpField();

    var feedImg = document.querySelector("[data-feed-img]");
    var placeholder = document.querySelector("[data-feed-placeholder]");
    var toggleBtn = document.querySelector("[data-feed-toggle]");
    var feedSrc = feedImg ? feedImg.getAttribute("data-src") : null;
    var isRunning = false;

    function showPlaceholder(show) {
      if (placeholder) placeholder.classList.toggle("is-visible", show);
      if (feedImg) feedImg.style.display = show ? "none" : "";
    }

    if (feedImg) {
      feedImg.addEventListener("error", function () {
        showPlaceholder(true);
        isRunning = false;
        if (toggleBtn) toggleBtn.textContent = "Start Live Feed";
      });
    }

    if (toggleBtn && feedImg && feedSrc) {
      showPlaceholder(true);
      toggleBtn.addEventListener("click", function () {
        if (!isRunning) {
          feedImg.src = feedSrc + (feedSrc.indexOf("?") === -1 ? "?" : "&") + "t=" + Date.now();
          showPlaceholder(false);
          toggleBtn.textContent = "Stop Live Feed";
          isRunning = true;
        } else {
          feedImg.src = "";
          showPlaceholder(true);
          toggleBtn.textContent = "Start Live Feed";
          isRunning = false;
        }
      });
    }
  });
})();
