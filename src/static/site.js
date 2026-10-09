/* Grace Woodwork: menu, EN/ES toggle, homepage photo rotation, tap-to-play videos and the
   Cloudinary shop photos on the gallery. Every page works without this file. */
(function () {
  "use strict";

  // ---- header menu ----
  var header = document.querySelector(".site-header");
  if (header) {
    var toggle = header.querySelector(".nav-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var open = header.classList.toggle("nav-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    var subToggles = header.querySelectorAll(".sub-toggle");
    var closeAll = function (except) {
      subToggles.forEach(function (b) {
        if (b === except) return;
        b.setAttribute("aria-expanded", "false");
        b.closest(".has-sub").classList.remove("sub-open");
      });
    };
    subToggles.forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var li = btn.closest(".has-sub");
        var open = !li.classList.contains("sub-open");
        closeAll(btn);
        li.classList.toggle("sub-open", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
    document.addEventListener("click", function (e) { if (!header.contains(e.target)) closeAll(null); });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var openBtn = header.querySelector('.sub-toggle[aria-expanded="true"]');
      closeAll(null);
      if (openBtn) openBtn.focus();
      if (header.classList.contains("nav-open") && toggle) {
        header.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // ---- EN / ES through Google Translate (loaded only when Spanish is chosen) ----
  var host = location.hostname;
  function setCookie(val) {
    var exp = val ? "" : "; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "googtrans=" + val + "; path=/" + exp;
    if (host.indexOf(".") > -1) {
      var root = host.split(".").slice(-2).join(".");
      document.cookie = "googtrans=" + val + "; path=/; domain=." + root + exp;
    }
  }
  function currentLang() { return /googtrans=\/en\/es/.test(document.cookie) ? "es" : "en"; }
  function loadTranslate() {
    if (window.__gtLoaded) return;
    window.__gtLoaded = true;
    window.googleTranslateElementInit = function () {
      /* global google */
      new google.translate.TranslateElement({ pageLanguage: "en", includedLanguages: "es", autoDisplay: false },
        "google_translate_element");
    };
    var s = document.createElement("script");
    s.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    s.async = true;
    document.body.appendChild(s);
  }
  var lang = currentLang();
  document.querySelectorAll(".lang__btn").forEach(function (b) {
    b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
    b.addEventListener("click", function () {
      var want = b.getAttribute("data-lang");
      if (want === currentLang()) return;
      setCookie(want === "es" ? "/en/es" : "");
      location.reload();
    });
  });
  if (lang === "es") { document.documentElement.lang = "es"; loadTranslate(); }

  // ---- homepage hero: the first photo loads with the page, the rest after it ----
  var slides = Array.prototype.slice.call(document.querySelectorAll(".hero__media img.slide"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".hero-dots button"));
  if (slides.length > 1) {
    var i = 0, timer = null;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var show = function (n) {
      slides[i].classList.remove("on"); if (dots[i]) dots[i].removeAttribute("aria-current");
      i = (n + slides.length) % slides.length;
      var guard = 0;
      while (slides[i].dataset.bad === "1" && guard++ < slides.length) i = (i + 1) % slides.length;
      slides[i].classList.add("on"); if (dots[i]) dots[i].setAttribute("aria-current", "true");
    };
    var start = function () { clearInterval(timer); if (!reduce) timer = setInterval(function () { show(i + 1); }, 5500); };
    slides.forEach(function (im) { im.addEventListener("error", function () { im.dataset.bad = "1"; }); });
    dots.forEach(function (b) {
      b.addEventListener("click", function () { clearInterval(timer); show(+b.dataset.i); start(); });
    });
    var hydrate = function () {
      slides.forEach(function (im) {
        var pic = im.parentNode;
        if (pic && pic.tagName === "PICTURE") {
          pic.querySelectorAll("source[data-srcset]").forEach(function (s) { s.srcset = s.dataset.srcset; s.removeAttribute("data-srcset"); });
        }
        if (im.dataset.src) { im.src = im.dataset.src; im.removeAttribute("data-src"); }
      });
      start();
    };
    if (document.readyState === "complete") setTimeout(hydrate, 600);
    else window.addEventListener("load", function () { setTimeout(hydrate, 600); });
    document.addEventListener("visibilitychange", function () { if (document.hidden) clearInterval(timer); else start(); });
  }

  // ---- Facebook videos: the heavy player loads only when someone taps ----
  document.querySelectorAll(".reel").forEach(function (card) {
    card.addEventListener("click", function () {
      var href = "https://www.facebook.com/reel/" + card.dataset.id + "/";
      var f = document.createElement("iframe");
      f.src = "https://www.facebook.com/plugins/video.php?height=476&href=" + encodeURIComponent(href) + "&show_text=false&width=267&t=0";
      f.title = card.getAttribute("aria-label").replace("Play video: ", "");
      f.setAttribute("allowfullscreen", "true");
      f.setAttribute("allow", "autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share");
      card.innerHTML = "";
      card.appendChild(f);
      card.style.cursor = "default";
    }, { once: true });
  });

  // ---- gallery: Grace's newest shop photos from Cloudinary go in front of the built-in ones.
  //      If anything fails, the built-in photos are already on the page. ----
  var box = document.getElementById("shots");
  if (box && window.fetch) {
    var CLOUD = "rxnz5l6u", TAG = "grace-shop";
    fetch("https://res.cloudinary.com/" + CLOUD + "/image/list/" + TAG + ".json")
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (d) {
        var res = (d.resources || []).sort(function (a, b) { return (b.version || 0) - (a.version || 0); });
        if (!res.length) return;
        var frag = document.createDocumentFragment();
        res.forEach(function (x, n) {
          var cap = (x.context && x.context.custom && x.context.custom.caption) || "";
          var url = "https://res.cloudinary.com/" + CLOUD + "/image/upload/f_auto,q_auto,w_1000,c_fill,ar_4:3/v" + x.version + "/" + x.public_id;
          var fig = document.createElement("figure");
          fig.className = "shot" + (n < 2 ? " wide" : "");
          var img = document.createElement("img");
          img.src = url; img.alt = cap || "Finished piece by Grace Woodwork";
          img.width = 1000; img.height = 750; img.decoding = "async"; img.loading = "lazy";
          fig.appendChild(img);
          if (cap) { var c = document.createElement("figcaption"); c.textContent = cap; fig.appendChild(c); }
          frag.appendChild(fig);
        });
        box.insertBefore(frag, box.firstChild);
      })
      .catch(function () { /* built-in gallery already on the page */ });
  }
})();
