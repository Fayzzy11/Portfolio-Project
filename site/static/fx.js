/* Thoth Ledger — motion layer: 3D allocation scene, scenario columns, card tilt, scroll reveal.
   Everything here is progressive: without JS or with reduced motion the page is complete and static. */
(function () {
  var d = document, root = d.documentElement;
  var rm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  root.classList.add("js");
  function ready(f) { d.readyState !== "loading" ? f() : d.addEventListener("DOMContentLoaded", f); }
  ready(function () {
    /* 1. allocation scene */
    var sc = d.querySelector("[data-scene]");
    if (sc) {
      var tilt = sc.querySelector(".tilt"), now = sc.querySelector(".now"), idle = now ? now.innerHTML : "";
      requestAnimationFrame(function () { setTimeout(function () { sc.classList.add("in"); }, 120); });
      var cur = null;
      function show(b) {
        if (cur) cur.classList.remove("on");
        cur = b; if (b) { b.classList.add("on"); now.innerHTML = b.getAttribute("data-cap"); } else now.innerHTML = idle;
      }
      sc.querySelectorAll(".blk").forEach(function (b) {
        b.addEventListener("mouseenter", function () { show(b); });
        b.addEventListener("click", function (e) { e.stopPropagation(); show(cur === b && !fine ? null : b); });
      });
      sc.addEventListener("mouseleave", function () { show(null); });
      if (!rm) {
        var tx = 0, tz = 0, gx = 0, gz = 0, raf = 0;
        function step() {
          tx += (gx - tx) * 0.08; tz += (gz - tz) * 0.08;
          tilt.style.setProperty("--tx", tx.toFixed(2) + "deg"); tilt.style.setProperty("--tz", tz.toFixed(2) + "deg");
          raf = Math.abs(gx - tx) + Math.abs(gz - tz) > 0.02 ? requestAnimationFrame(step) : 0;
        }
        if (fine) {
          var hero = sc.closest("section") || sc;
          hero.addEventListener("pointermove", function (e) {
            var r = sc.getBoundingClientRect();
            gz = Math.max(-1, Math.min(1, (e.clientX - r.left - r.width / 2) / r.width)) * 12;
            gx = Math.max(-1, Math.min(1, (e.clientY - r.top - r.height / 2) / r.height)) * -6;
            if (!raf) raf = requestAnimationFrame(step);
          });
          hero.addEventListener("pointerleave", function () { gx = gz = 0; if (!raf) raf = requestAnimationFrame(step); });
        }
        var tick = false;
        function onScroll() {
          if (tick) return; tick = true;
          requestAnimationFrame(function () {
            var r = sc.getBoundingClientRect(), p = Math.max(0, Math.min(1, -r.top / (r.height * 0.9) + 0.12));
            tilt.style.setProperty("--sp", p.toFixed(3)); tick = false;
          });
        }
        window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
      }
    }
    /* 2. scenario columns */
    d.querySelectorAll(".sc3d").forEach(function (el) { setTimeout(function () { el.classList.add("in"); }, 250); });
    /* 3. tilt on cards */
    if (fine && !rm) {
      d.querySelectorAll(".grid > .card, .panel.call").forEach(function (c) {
        c.classList.add("tiltable");
        c.addEventListener("pointermove", function (e) {
          var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
          c.style.transform = "perspective(1100px) rotateX(" + (-y * 3.2).toFixed(2) + "deg) rotateY(" + (x * 4).toFixed(2) + "deg) translateY(-3px)";
        });
        c.addEventListener("pointerleave", function () { c.style.transform = ""; });
      });
    }
    /* 4. reveal on scroll */
    var els = d.querySelectorAll(".sec .shead, .grid > .card, .notes > .noteitem, .stats > *, .numlist > .box, .kstrip .kpi, .horus");
    if (!rm && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -6% 0px" });
      els.forEach(function (el) {
        var i = 0, s = el; while ((s = s.previousElementSibling)) i++;
        el.style.setProperty("--d", Math.min(i, 5)); el.classList.add("rv"); io.observe(el);
      });
    }
  });
})();
