/* ============================================================
   Freelancino — main frontend script
   ============================================================ */

(function () {
  "use strict";

  // --- Mobile navigation toggle -----------------------------------------
  var navToggle = document.getElementById("navToggle");
  var mainNav = document.getElementById("mainNav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", function () {
      mainNav.classList.toggle("open");
    });
  }

  // --- Auto-dismiss flash messages --------------------------------------
  document.querySelectorAll(".flash").forEach(function (flash) {
    var close = flash.querySelector(".flash-close");
    if (close) {
      close.addEventListener("click", function () {
        flash.remove();
      });
    }
    setTimeout(function () {
      flash.style.transition = "opacity .4s ease";
      flash.style.opacity = "0";
      setTimeout(function () { flash.remove(); }, 400);
    }, 6000);
  });

  // --- Smooth scroll for in-page anchors --------------------------------
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var target = document.querySelector(link.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // --- Confirm destructive actions --------------------------------------
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });
})();
