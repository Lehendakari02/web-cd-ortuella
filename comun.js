/* ==========================================================================
   PIEZAS COMUNES A TODAS LAS PÁGINAS
   Cabecera con menú, pie de página y funciones para pintar partidos,
   clasificaciones y goleadores. Cada página llama a lo que necesita.
   ========================================================================== */
(function () {
  var C = window.CLUB || {}, F = window.FEDERACION || { equipos: [] };

  // ---- utilidades -----------------------------------------------------------
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"];
  var DIA = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  var DIAL = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  var day = function (iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); };
  var fdate = function (iso, year) { var x = day(iso); return x.getDate() + " " + MES[x.getMonth()] + (year ? " " + x.getFullYear() : ""); };
  var today = new Date(); today.setHours(0, 0, 0, 0);

  // Nombre corto y enlace de cada equipo
  var APODO = { primer: "Senior A", b: "Senior B", juvenil: "Juvenil", cadete: "Cadete" };
  var SLUG = { primer: "senior-a", b: "senior-b", juvenil: "juvenil", cadete: "cadete" };
  var team = function (id) { return F.equipos.filter(function (t) { return t.id === id; })[0]; };
  var isUs = function (name, t) { return name === t.nombreFederacion; };
  var played = function (t) { return t.partidos.filter(function (p) { return p.gl != null; }); };
  var upcoming = function (t) { return t.partidos.filter(function (p) { return p.gl == null && day(p.fecha) >= today; }); };
  var outcome = function (p, t) { var us = isUs(p.local, t) ? p.gl : p.gv, them = isUs(p.local, t) ? p.gv : p.gl; return us > them ? "w" : us === them ? "d" : "l"; };
  var initials = function (n) { return n.split(/\s+/).filter(function (w) { return w.length > 1; }).map(function (w) { return w[0]; }).join("").slice(0, 2).toUpperCase(); };
  var crest = function (name, t) { return isUs(name, t) ? '<img class="crest-mini" src="img/escudo.webp" alt="">' : '<span class="crest-other" aria-hidden="true">' + esc(initials(name)) + "</span>"; };
  var ourRow = function (t) { return t.clasificacion.filter(function (r) { return isUs(r.equipo, t); })[0]; };

  // ---- cabecera y pie -------------------------------------------------------
  var MENU = [
    { t: "Inicio", h: "./" },
    { t: "Partidos", h: "partidos.html" },
    { t: "Equipos", sub: [
      { t: "Senior A", h: "equipos.html#senior-a", d: "Segunda División · Grupo 1" },
      { t: "Senior B", h: "equipos.html#senior-b", d: "Tercera División · Grupo 1" },
      { t: "Juvenil", h: "equipos.html#juvenil", d: "Juvenil Segunda División" },
      { t: "Cadete", h: "equipos.html#cadete", d: "Cadete Tercera División" },
      { t: "Fútbol base", h: "equipos.html#base", d: "Infantil, alevín y benjamín" }
    ] },
    { t: "Noticias", h: "noticias.html" },
    { t: "Club", sub: [
      { t: "Historia y palmarés", h: "historia.html", d: "Desde 1949" },
      { t: "Directiva", h: "directiva.html", d: "Quién es quién en el club" },
      { t: "Otxartaga Berri", h: "campo.html", d: "Nuestro campo" }
    ] },
    { t: "Contacto", h: "contacto.html" }
  ];
  var page = document.body.getAttribute("data-page");
  var isCurrent = function (h) { return h.split("#")[0] === page + ".html" || (h === "./" && page === "index"); };

  function renderHeader() {
    var el = document.getElementById("cabecera"); if (!el) return;
    var items = MENU.map(function (m, i) {
      if (!m.sub) return '<li><a href="' + m.h + '"' + (isCurrent(m.h) ? ' aria-current="page"' : "") + ">" + m.t + "</a></li>";
      var cur = m.sub.some(function (s) { return isCurrent(s.h); });
      return '<li><button class="drop-btn' + (cur ? " current" : "") + '" aria-expanded="false" aria-controls="sub' + i + '">' + m.t + '</button><ul class="sub" id="sub' + i + '">' +
        m.sub.map(function (s) { return '<li><a href="' + s.h + '"' + (isCurrent(s.h) ? ' aria-current="page"' : "") + ">" + s.t + "<small>" + s.d + "</small></a></li>"; }).join("") + "</ul></li>";
    }).join("");
    el.innerHTML =
      '<div class="topbar"><div class="wrap"><span class="hide-sm">Avda. de la Estación s/n · Ortuella · <span class="num">946 353 598</span></span>' +
      '<span class="socials"><a href="https://www.instagram.com/cdortuella/" target="_blank" rel="noopener">Instagram</a><a href="https://www.facebook.com/cdortuella1945/" target="_blank" rel="noopener">Facebook</a><a href="https://x.com/CD_Ortuella" target="_blank" rel="noopener">X</a></span></div></div>' +
      '<header class="top"><div class="wrap">' +
      '<a class="brand" href="./" aria-label="Club Deportivo Ortuella, inicio"><img src="img/escudo.webp" alt=""><span><b>CD Ortuella</b><small>Desde 1949</small></span></a>' +
      '<button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="menu"><i></i>Menú</button>' +
      '<nav class="menu" id="menu" aria-label="Menú principal"><ul>' + items + '</ul><a class="cta" href="socios.html"' + (page === "socios" ? ' aria-current="page"' : "") + ">Hazte socio</a></nav>" +
      "</div></header>";

    var menu = document.getElementById("menu"), btn = document.getElementById("menuBtn");
    btn.addEventListener("click", function () { var o = menu.classList.toggle("open"); btn.setAttribute("aria-expanded", o); });
    var closeAll = function (except) {
      menu.querySelectorAll("li.open").forEach(function (li) { if (li !== except) { li.classList.remove("open"); li.querySelector(".drop-btn").setAttribute("aria-expanded", "false"); } });
    };
    menu.querySelectorAll(".drop-btn").forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var li = b.parentNode; closeAll(li);
        var o = li.classList.toggle("open"); b.setAttribute("aria-expanded", o);
      });
    });
    document.addEventListener("click", function (e) { if (!menu.contains(e.target)) closeAll(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeAll(); });
    // Al ir a otro equipo dentro de la misma página, cerrar el menú
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) { closeAll(); menu.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); } });
  }

  function renderFooter() {
    var el = document.getElementById("pie"); if (!el) return;
    var sp = (C.patrocinadores || []).map(function (s) { return '<span class="foot-sponsor">' + (s.logo ? '<img src="' + esc(s.logo) + '" alt="' + esc(s.nombre) + '">' : esc(s.nombre)) + "</span>"; }).join("");
    el.innerHTML = '<footer>' +
      (sp && page !== "socios" ? '<div class="foot-sponsors"><div class="wrap"><span>Patrocinan</span>' + sp + '<a href="contacto.html">¿Tu negocio aquí?</a></div></div>' : "") +
      '<div class="wrap foot-main">' +
      '<div><img src="img/escudo.webp" alt=""><b>Club Deportivo Ortuella</b><p>Fundado en 1949 · Otxartaga Berri, Ortuella (Bizkaia)</p></div>' +
      '<ul><li><a href="partidos.html">Partidos</a></li><li><a href="equipos.html">Equipos</a></li><li><a href="noticias.html">Noticias</a></li><li><a href="historia.html">Historia</a></li></ul>' +
      '<ul><li><a href="socios.html">Socios y tienda</a></li><li><a href="directiva.html">Directiva</a></li><li><a href="campo.html">Otxartaga Berri</a></li><li><a href="contacto.html">Contacto</a></li></ul>' +
      '<div class="foot-contact"><span>cdortuella@cdortuella.net</span><span class="num">946 353 598</span></div>' +
      '</div><div class="wrap foot-legal">© ' + new Date().getFullYear() + ' CD Ortuella · Datos de competición: Federación Vizcaína de Fútbol<span class="legal-links"><a href="aviso-legal.html">Aviso legal</a><a href="privacidad.html">Privacidad y cookies</a></span></div></footer>';
  }

  // ---- piezas de partidos ----------------------------------------------------
  function matchCard(t) {
    var p = upcoming(t)[0];
    if (!p) return "";
    var d = day(p.fecha), days = Math.round((d - today) / 864e5);
    var when = days === 0 ? "Hoy" : days === 1 ? "Mañana" : "Faltan " + days + " días";
    return '<article class="match"><div class="head"><span><b>' + APODO[t.id] + "</b> · Jornada " + p.jornada + '</span><span class="days">' + when + "</span></div>" +
      '<div class="teams"><div class="team">' + crest(p.local, t) + "<b>" + esc(p.local) + '</b></div><div class="vs">VS</div><div class="team">' + crest(p.visitante, t) + "<b>" + esc(p.visitante) + "</b></div></div>" +
      '<div class="info"><span><strong>' + DIAL[d.getDay()] + " " + fdate(p.fecha) + "</strong></span><span>" + (isUs(p.local, t) ? "Otxartaga Berri" : "Fuera de casa") + "</span><span>Hora por confirmar</span></div>" +
      '<div class="share-row">' + shareLink(matchShareText(p, t), "Compartir por WhatsApp") + "</div></article>";
  }

  // Cada resultado como un marcador de dos filas: equipo a la izquierda, goles a la derecha
  function resultsStrip() {
    var WORD = { w: "Victoria", d: "Empate", l: "Derrota" };
    return '<div class="lbl">Últimos resultados</div>' + F.equipos.map(function (t) {
      var p = played(t).slice(-1)[0];
      if (!p) return '<div class="res"><small>' + APODO[t.id] + '</small><div class="none">Sin partidos todavía</div></div>';
      var o = outcome(p, t);
      var row = function (n, g) { return '<div class="row' + (isUs(n, t) ? " us" : "") + '"><span title="' + esc(n) + '">' + esc(n) + "</span><b>" + g + "</b></div>"; };
      return '<div class="res"><small>' + APODO[t.id] + " · J" + p.jornada + '<em class="o ' + o + '">' + WORD[o] + "</em></small>" + row(p.local, p.gl) + row(p.visitante, p.gv) + "</div>";
    }).join("");
  }

  // compact: solo las filas alrededor de nuestra posición
  function tableRows(t, compact) {
    var rows = t.clasificacion.filter(function (r) { return r.pos > 0; });
    if (compact) {
      var i = rows.findIndex(function (r) { return isUs(r.equipo, t); });
      var from = Math.max(0, Math.min(i - 2, rows.length - 5));
      rows = rows.slice(from, from + 5);
    }
    return rows.map(function (r) {
      return '<tr class="' + (isUs(r.equipo, t) ? "us " : "") + (r.pos === 1 ? "first" : "") + '"><td><span class="pos">' + r.pos + '</span></td><td class="t">' + esc(r.equipo) + "</td><td>" + r.pj + '</td><td class="x">' + r.g + '</td><td class="x">' + r.e + '</td><td class="x">' + r.p + '</td><td class="x">' + r.gf + '</td><td class="x">' + r.gc + '</td><td class="pts">' + r.pts + "</td></tr>";
    }).join("");
  }
  var TABLE_HEAD = '<thead><tr><th>#</th><th class="t">Equipo</th><th title="Partidos jugados">PJ</th><th class="x" title="Ganados">G</th><th class="x" title="Empatados">E</th><th class="x" title="Perdidos">P</th><th class="x" title="Goles a favor">GF</th><th class="x" title="Goles en contra">GC</th><th title="Puntos">Pts</th></tr></thead>';

  function gamesList(t, results, limit) {
    var list = results ? t.partidos.filter(function (p) { return day(p.fecha) < today; }).reverse() : upcoming(t);
    if (limit) list = list.slice(0, limit);
    if (!list.length) return '<li class="empty">' + (results ? "Todavía no se ha jugado ningún partido." : "No hay más partidos en el calendario.") + "</li>";
    var name = function (n) { return isUs(n, t) ? '<span class="us">' + esc(n) + "</span>" : esc(n); };
    return list.map(function (p) {
      var x = day(p.fecha), right;
      if (p.gl != null) { var o = outcome(p, t); right = '<span class="score ' + o + '" aria-label="' + { w: "Victoria", d: "Empate", l: "Derrota" }[o] + " " + p.gl + " a " + p.gv + '">' + p.gl + "-" + p.gv + "</span>"; }
      else if (results) right = '<span class="score na">Sin cargar</span>';
      else right = '<span class="hour tbc">Hora por confirmar</span>';
      return '<li><div class="d">' + DIA[x.getDay()] + '<b class="num">' + x.getDate() + " " + MES[x.getMonth()] + '</b></div><div class="m">' + name(p.local) + " – " + name(p.visitante) + "<small>Jornada " + p.jornada + " · " + (isUs(p.local, t) ? "En casa" : "Fuera") + "</small></div>" + right + "</li>";
    }).join("");
  }

  function scorersList(t, limit) {
    var g = t.goleadores, max = g.length ? g[0].goles : 1;
    if (!g.length) return '<li class="empty">Todavía no hay goleadores registrados en la Federación.</li>';
    return g.slice(0, limit || 8).map(function (x) {
      return "<li><b>" + esc(x.nombre) + '</b><span class="g">' + x.goles + '</span><span class="bar"><i style="width:' + (x.goles / max * 100) + '%"></i></span></li>';
    }).join("");
  }

  function sourceNote(t) {
    var u = F.actualizado ? new Date(F.actualizado) : null;
    return "Datos de la Federación Vizcaína de Fútbol" + (u ? ", actualizados el " + u.getDate() + " " + MES[u.getMonth()] + " a las " + String(u.getHours()).padStart(2, "0") + ":" + String(u.getMinutes()).padStart(2, "0") : "") +
      (t ? '. <a href="' + esc(t.enlace) + '" target="_blank" rel="noopener">Ver en la web de la Federación</a>' : ".");
  }

  function newsCard(n) {
    return "<article>" + (n.foto ? '<img class="pic" src="' + esc(n.foto) + '" alt="" loading="lazy">' : "") + '<div class="body">' +
      '<div class="meta"><span class="cat">' + esc(n.etiqueta) + "</span><span>" + esc(n.fechaTexto || fdate(n.fecha, true)) + "</span></div>" +
      "<h3>" + esc(n.titulo) + "</h3><p>" + esc(n.texto) + "</p></div></article>";
  }

  function copyButtons() {
    document.querySelectorAll(".copy").forEach(function (b) {
      b.addEventListener("click", function () {
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(b.dataset.copy).then(function () { b.textContent = "Copiado"; setTimeout(function () { b.textContent = "Copiar"; }, 1500); }, function () {});
      });
    });
  }

  // Dibujos de camiseta y bufanda (se usan con <use href="#shirt">)
  function sprite() {
    var d = document.createElement("div");
    d.innerHTML = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' +
      '<symbol id="shirt" viewBox="0 0 48 48"><path d="M16 4 L8 8 L2 18 L9 22 L12 18 V44 H36 V18 L39 22 L46 18 L40 8 L32 4 C30 8 18 8 16 4Z" fill="#ffffff" stroke="#0b2a5b" stroke-width="2"/><path d="M17 6 V44 M24 8 V44 M31 6 V44" stroke="#1757c2" stroke-width="4"/></symbol>' +
      '<symbol id="scarf" viewBox="0 0 48 48"><path d="M6 10 h36 v10 h-36z" fill="#1757c2"/><path d="M6 20 h36 v10 h-36z" fill="#ffffff" stroke="#0b2a5b" stroke-width="1"/><path d="M6 30 h36 v10 h-36z" fill="#1757c2"/><path d="M6 40 v5 M12 40 v5 M18 40 v5 M24 40 v5 M30 40 v5 M36 40 v5 M42 40 v5" stroke="#0b2a5b" stroke-width="2"/></symbol>' +
      "</defs></svg>";
    document.body.insertBefore(d.firstChild, document.body.firstChild);
  }

  // Racha: últimos 5 resultados como cuadritos V/E/D
  // ---- compartir y calendario -------------------------------------------------
  var DIAL_MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  var longDate = function (iso) { var x = day(iso), d = DIAL[x.getDay()]; return d.charAt(0).toUpperCase() + d.slice(1) + " " + x.getDate() + " de " + DIAL_MES[x.getMonth()]; };
  var webUrl = function (path) { return new URL(path, location.href).href.split("#")[0]; };
  var BUBBLE = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.6 0-3.1-.4-4.4-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.4.1-.7.3-.2.3-.9.9-.9 2.2s.9 2.5 1 2.7c.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.6-.3z"/></svg>';
  // Enlace que abre WhatsApp con el mensaje ya escrito (en el móvil, la app; en el ordenador, WhatsApp Web)
  function shareLink(text, label) {
    return '<a class="share" href="https://wa.me/?text=' + encodeURIComponent(text) + '" target="_blank" rel="noopener">' + BUBBLE + (label || "Compartir") + "</a>";
  }
  function matchLine(p, t) {
    if (p.gl != null) return APODO[t.id] + ": " + p.local + " " + p.gl + "-" + p.gv + " " + p.visitante;
    return APODO[t.id] + ": " + p.local + " – " + p.visitante + (isUs(p.local, t) ? " (en casa, Otxartaga Berri)" : " (fuera)");
  }
  function matchShareText(p, t) {
    return "⚽ " + APODO[t.id] + " · Jornada " + p.jornada + "\n" + p.local + " – " + p.visitante + "\n📅 " + longDate(p.fecha) + (isUs(p.local, t) ? " · Otxartaga Berri" : " · Fuera de casa") + "\nHora por confirmar\n\n" + webUrl("partidos.html");
  }
  // Enlaces para suscribirse al calendario .ics de un equipo (o "todos")
  function calHrefs(slug) {
    var url = webUrl("calendario/" + slug + ".ics"), webcal = url.replace(/^https?:/, "webcal:");
    return { url: url, apple: webcal, google: "https://calendar.google.com/calendar/render?cid=" + encodeURIComponent(webcal) };
  }

  function formDots(t) {
    return '<div class="form-dots">' + played(t).slice(-5).map(function (p) { var o = outcome(p, t); return '<i class="' + o + '" title="' + esc(p.local + " " + p.gl + "-" + p.gv + " " + p.visitante) + '">' + { w: "V", d: "E", l: "D" }[o] + "</i>"; }).join("") + "</div>";
  }

  sprite();
  renderHeader();
  renderFooter();
  document.querySelectorAll(".season").forEach(function (el) { el.textContent = F.temporada || "2026/27"; });

  window.CDO = { C: C, SLUG: SLUG, formDots: formDots, crest: crest, F: F, esc: esc, fdate: fdate, day: day, APODO: APODO, team: team, isUs: isUs, played: played, upcoming: upcoming, outcome: outcome, ourRow: ourRow,
    matchCard: matchCard, resultsStrip: resultsStrip, tableRows: tableRows, TABLE_HEAD: TABLE_HEAD, gamesList: gamesList, scorersList: scorersList, sourceNote: sourceNote, newsCard: newsCard, copyButtons: copyButtons, shareLink: shareLink, matchLine: matchLine, longDate: longDate, webUrl: webUrl, calHrefs: calHrefs };
})();
