/* Research Ledger — small, dependency-free behaviours. */
(function () {
  var root = document.documentElement;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  var saved = store("rl-theme"); if (saved) root.setAttribute("data-theme", saved);

  document.addEventListener("DOMContentLoaded", function () {
    // theme
    var tb = document.getElementById("theme");
    if (tb) tb.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark"; root.setAttribute("data-theme", next); store("rl-theme", next);
      document.dispatchEvent(new Event("themechange"));
    });
    // mobile menu
    var mb = document.getElementById("menu"), nav = document.getElementById("nav");
    if (mb) mb.addEventListener("click", function () { var o = nav.classList.toggle("open"); mb.setAttribute("aria-expanded", o); });

    // TOC scrollspy
    var toc = document.querySelector(".toc");
    if (toc && "IntersectionObserver" in window) {
      var links = {}; toc.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting && links[e.target.id]) {
            toc.querySelectorAll("a.on").forEach(function (x) { x.classList.remove("on"); });
            links[e.target.id].classList.add("on");
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      Object.keys(links).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
    }

    // filterable lists: [data-filter-list] with buttons [data-f=group][data-v=value] and input[data-search]
    document.querySelectorAll("[data-filter-scope]").forEach(function (scope) {
      var items = scope.querySelectorAll("[data-item]"), state = {}, q = "";
      var cnt = scope.querySelector(".count"), empty = scope.querySelector(".empty");
      function apply() {
        var n = 0;
        items.forEach(function (it) {
          var ok = Object.keys(state).every(function (g) { return state[g] === "all" || (it.getAttribute("data-" + g) || "").split(" ").indexOf(state[g]) >= 0; });
          if (ok && q) ok = it.textContent.toLowerCase().indexOf(q) >= 0;
          it.style.display = ok ? "" : "none"; if (ok) n++;
        });
        if (cnt) cnt.textContent = n + (document.documentElement.lang === "fr" ? " sur " : " of ") + items.length;
        if (empty) empty.style.display = n ? "none" : "block";
      }
      scope.querySelectorAll("[data-f]").forEach(function (b) {
        var g = b.getAttribute("data-f"); if (!(g in state)) state[g] = "all";
        b.addEventListener("click", function () {
          scope.querySelectorAll('[data-f="' + g + '"]').forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
          b.setAttribute("aria-pressed", "true"); state[g] = b.getAttribute("data-v"); apply();
        });
      });
      var s = scope.querySelector("[data-search]");
      if (s) s.addEventListener("input", function () { q = s.value.trim().toLowerCase(); apply(); });
      apply();
    });

    // sortable tables
    document.querySelectorAll("table.t[data-sortable]").forEach(function (t) {
      t.querySelectorAll("th").forEach(function (th, i) {
        th.setAttribute("data-sort", ""); var asc = true;
        th.addEventListener("click", function () {
          var body = t.tBodies[0], rows = Array.prototype.slice.call(body.rows);
          rows.sort(function (a, b) {
            var x = a.cells[i].getAttribute("data-v") || a.cells[i].textContent, y = b.cells[i].getAttribute("data-v") || b.cells[i].textContent;
            var nx = parseFloat(x), ny = parseFloat(y);
            var r = (!isNaN(nx) && !isNaN(ny)) ? nx - ny : x.localeCompare(y);
            return asc ? r : -r;
          });
          asc = !asc; rows.forEach(function (r) { body.appendChild(r); });
        });
      });
    });

    // NAV chart
    var el = document.getElementById("navchart");
    if (el && window.NAV) navChart(el, window.NAV);
    var el2 = document.getElementById("navchart2");
    if (el2 && window.NAV2) navChart(el2, window.NAV2);
  });

  function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

  function navChart(box, D) {
    var svgNS = "http://www.w3.org/2000/svg";
    var colors = D.colors || {};
    var on = {}; Object.keys(D.series).forEach(function (k) { on[k] = true; });
    var range = "all", mode = "nav";
    var tip = box.querySelector(".tip"), host = box.querySelector(".plot");
    var W = 900, H = 340, m = { l: 46, r: 16, t: 12, b: 28 };

    box.querySelectorAll("[data-range]").forEach(function (b) {
      b.addEventListener("click", function () {
        box.querySelectorAll("[data-range]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true"); range = b.getAttribute("data-range"); draw();
      });
    });
    box.querySelectorAll("[data-mode]").forEach(function (b) {
      b.addEventListener("click", function () {
        box.querySelectorAll("[data-mode]").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true"); mode = b.getAttribute("data-mode"); draw();
      });
    });
    box.querySelectorAll("input[data-s]").forEach(function (c) {
      c.addEventListener("change", function () { on[c.getAttribute("data-s")] = c.checked; draw(); });
    });
    document.addEventListener("themechange", draw);

    function draw() {
      var n = D.dates.length, start = 0;
      if (range !== "all") {
        var yrs = +range, last = new Date(D.dates[n - 1]); last.setFullYear(last.getFullYear() - yrs);
        while (start < n - 1 && new Date(D.dates[start]) < last) start++;
      }
      var dates = D.dates.slice(start), keys = Object.keys(D.series).filter(function (k) { return on[k]; });
      var series = {};
      keys.forEach(function (k) {
        var s = D.series[k].slice(start), base = s[0];
        if (mode === "nav") series[k] = s.map(function (v) { return v / base * 100; });
        else { var pk = -1e9; series[k] = s.map(function (v) { pk = Math.max(pk, v); return (v / pk - 1) * 100; }); }
      });
      var lo = 1e9, hi = -1e9;
      keys.forEach(function (k) { series[k].forEach(function (v) { lo = Math.min(lo, v); hi = Math.max(hi, v); }); });
      if (!keys.length) { lo = 0; hi = 1; }
      if (mode === "dd") hi = 0;
      var pad = (hi - lo) * 0.06; lo -= pad; hi += mode === "dd" ? 0 : pad;
      var step = niceStep((hi - lo) / 5), y0 = Math.floor(lo / step) * step, y1 = Math.ceil(hi / step) * step;
      var X = function (i) { return m.l + i / (dates.length - 1) * (W - m.l - m.r); };
      var Y = function (v) { return m.t + (1 - (v - y0) / (y1 - y0)) * (H - m.t - m.b); };
      var g = '<g class="grid">';
      for (var v = y0; v <= y1 + 1e-9; v += step) g += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (m.l - 8) + '" y="' + (Y(v) + 4) + '" text-anchor="end">' + (Math.round(v * 10) / 10) + (mode === "dd" ? "%" : "") + "</text>";
      g += "</g>";
      var lastY = null;
      dates.forEach(function (d, i) {
        var y = d.slice(0, 4), step = dates.length > 150 ? (dates.length > 400 ? 5 : 2) : 1;
        if (y !== lastY && i > 0 && d.slice(5, 7) <= "01" && (+y % step === 0)) g += '<line class="axis" x1="' + X(i) + '" x2="' + X(i) + '" y1="' + (H - m.b) + '" y2="' + (H - m.b + 5) + '"/><text x="' + X(i) + '" y="' + (H - 8) + '" text-anchor="middle">' + y + "</text>";
        lastY = y;
      });
      if (mode === "nav") g += '<line stroke-dasharray="3 3" class="axis" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(100) + '" y2="' + Y(100) + '"/>';
      keys.slice().reverse().forEach(function (k) {
        var p = series[k].map(function (v, i) { return (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1); }).join("");
        var bench = (D.bench || []).indexOf(k) >= 0;
        g += '<path d="' + p + '" fill="none" stroke="' + css(colors[k]) + '" stroke-width="' + (k === D.main ? 2.4 : 1.6) + '"' + (bench ? ' stroke-dasharray="5 3"' : "") + "/>";
      });
      g += '<line id="cx" class="axis" style="opacity:0" y1="' + m.t + '" y2="' + (H - m.b) + '" x1="-10" x2="-10"/><g id="dots"></g>';
      host.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Cumulative performance">' + g + '<rect x="' + m.l + '" y="' + m.t + '" width="' + (W - m.l - m.r) + '" height="' + (H - m.t - m.b) + '" fill="transparent" id="hit"/></svg>';
      var svg = host.querySelector("svg"), hit = svg.querySelector("#hit"), cx = svg.querySelector("#cx"), dots = svg.querySelector("#dots");
      function move(ev) {
        var r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * W;
        var i = Math.round((px - m.l) / (W - m.l - m.r) * (dates.length - 1)); i = Math.max(0, Math.min(dates.length - 1, i));
        cx.setAttribute("x1", X(i)); cx.setAttribute("x2", X(i)); cx.style.opacity = 1;
        var h = "<b>" + dates[i] + "</b>", dd = "";
        keys.forEach(function (k) {
          var v = series[k][i]; h += '<br><span style="color:' + css(colors[k]) + '">■</span> ' + k + "  " + (mode === "nav" ? v.toFixed(1) : v.toFixed(1) + "%");
          dd += '<circle r="3.5" cx="' + X(i) + '" cy="' + Y(v) + '" fill="' + css(colors[k]) + '"/>';
        });
        dots.innerHTML = dd; tip.innerHTML = h; tip.style.opacity = 1;
        var left = X(i) / W * r.width; tip.style.left = (left > r.width * 0.6 ? left - tip.offsetWidth - 14 : left + 14) + "px"; tip.style.top = "10px";
      }
      hit.addEventListener("mousemove", move);
      hit.addEventListener("mouseleave", function () { tip.style.opacity = 0; dots.innerHTML = ""; cx.style.opacity = 0; });
    }
    function niceStep(x) { var p = Math.pow(10, Math.floor(Math.log10(x))), f = x / p; return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * p; }
    draw();
  }
})();
