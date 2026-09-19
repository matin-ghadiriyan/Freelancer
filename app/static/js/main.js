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

  // --- User avatar dropdowns (click to open/close) -----------------------
  var userMenus = document.querySelectorAll(".user-menu");
  var closeAllMenus = function () {
    userMenus.forEach(function (menu) {
      menu.classList.remove("open");
      var btn = menu.querySelector(".avatar-btn, .avatar-btn-xl");
      if (btn) { btn.setAttribute("aria-expanded", "false"); }
    });
  };

  userMenus.forEach(function (menu) {
    var btn = menu.querySelector(".avatar-btn, .avatar-btn-xl");
    if (!btn) { return; }

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = !menu.classList.contains("open");
      closeAllMenus();
      menu.classList.toggle("open", willOpen);
      btn.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });
  });

  document.addEventListener("click", function (e) {
    var inside = e.target.closest && e.target.closest(".user-menu");
    if (!inside) { closeAllMenus(); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeAllMenus(); }
  });

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
