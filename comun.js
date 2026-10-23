/* ==========================================================================
   PIEZAS COMUNES A TODAS LAS PÁGINAS
   Cabecera con menú, pie de página y funciones para pintar partidos,
   clasificaciones y goleadores. Cada página llama a lo que necesita.
   ========================================================================== */
(function () {
  var C = window.CLUB || {}, F = window.FEDERACION || { equipos: [] };
  // Noticias: las escritas a mano (datos.js) + las que llegan de Instagram (datos-noticias.js), las más nuevas primero
  C.noticias = (window.NOTICIAS || []).concat(C.noticias || []).sort(function (a, b) { return a.fecha < b.fecha ? 1 : a.fecha > b.fecha ? -1 : 0; });

  // ---- utilidades -----------------------------------------------------------
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"];
  var DIA = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  var DIAL = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  var day = function (iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); };
  var fdate = function (iso, year) { var x = day(iso); return x.getDate() + " " + MES[x.getMonth()] + (year ? " " + x.getFullYear() : ""); };
  var today = new Date(); today.setHours(0, 0, 0, 0);

  // Nombre corto y enlace de cada equipo
  var APODO = { primer: "Senior A", b: "Senior B", juvenil: "Juvenil", cadete: "Cadete", infantil: "Infantil", alevin: "Alevín" };
  var SLUG = { primer: "senior-a", b: "senior-b", juvenil: "juvenil", cadete: "cadete", infantil: "infantil", alevin: "alevin" };
  // Fútbol base (Infantil y alevín): tienen su página, pero no salen en la portada
  var federados = function () { return F.equipos.filter(function (t) { return !t.base; }); };
  var team = function (id) { return F.equipos.filter(function (t) { return t.id === id; })[0]; };
  var isUs = function (name, t) { return name === t.nombreFederacion; };
  var played = function (t) { return t.partidos.filter(function (p) { return p.gl != null; }); };
  var upcoming = function (t) { return t.partidos.filter(function (p) { return p.gl == null && day(p.fecha) >= today; }); };
  var outcome = function (p, t) { var us = isUs(p.local, t) ? p.gl : p.gv, them = isUs(p.local, t) ? p.gv : p.gl; return us > them ? "w" : us === them ? "d" : "l"; };
  var initials = function (n) { return n.split(/\s+/).filter(function (w) { return w.length > 1; }).map(function (w) { return w[0]; }).join("").slice(0, 2).toUpperCase(); };
  // Escudo de cada equipo: el nuestro, el del rival si lo tenemos en img/escudos/ (F.escudos) y, si no hay ninguno, sus iniciales
  var crest = function (name, t) {
    if (isUs(name, t)) return '<img class="crest-mini" src="img/escudo.webp" alt="">';
    var f = (F.escudos || {})[name];
    return f ? '<img class="crest-mini" src="img/escudos/' + esc(f) + '" alt="" loading="lazy" decoding="async">' : '<span class="crest-other" aria-hidden="true">' + esc(initials(name)) + "</span>";
  };
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
      { t: "Fútbol base", h: "equipos.html#base", d: "Infantil y alevín" }
    ] },
    { t: "Noticias", h: "noticias.html" },
    { t: "Club", sub: [
      { t: "Historia y palmarés", h: "historia.html", d: "Desde 1949" },
      { t: "Directiva", h: "directiva.html", d: "Quién es quién en el club" },
      { t: "Otxartaga Berri", h: "campo.html", d: "Nuestro campo" }
    ] },
    { t: "Tienda", h: "tienda.html" },
    { t: "Patrocinadores", h: "patrocinadores.html" },
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
      '<div class="topbar" role="region" aria-label="Contacto y redes sociales"><div class="wrap"><span class="hide-sm">Avda. de la Estación s/n · Ortuella · <span class="num">946 353 598</span></span>' +
      '<span class="socials"><a href="https://www.instagram.com/cdortuella/" target="_blank" rel="noopener">Instagram</a><a href="https://www.facebook.com/cdortuella1945/" target="_blank" rel="noopener">Facebook</a><a href="https://x.com/CD_Ortuella" target="_blank" rel="noopener">X</a></span></div></div>' +
      '<header class="top"><div class="wrap">' +
      '<a class="brand" href="./"><img src="img/escudo.webp" alt=""><span><b>CD Ortuella</b><small>Desde 1949</small></span><span class="sr-only">, ir al inicio</span></a>' +
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
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var open = menu.querySelector("li.open");
      if (open && open.contains(document.activeElement)) open.querySelector(".drop-btn").focus();
      closeAll();
      if (menu.classList.contains("open")) { menu.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); btn.focus(); }
    });
    // Al salir con el tabulador de un desplegable, se cierra para que no tape lo de debajo
    menu.addEventListener("focusout", function (e) { var li = e.target.closest("li.open"); if (li && !li.contains(e.relatedTarget)) closeAll(); });
    // Al ir a otro equipo dentro de la misma página, cerrar el menú
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) { closeAll(); menu.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); } });
  }

  function renderFooter() {
    var el = document.getElementById("pie"); if (!el) return;
    var todos = (C.patrocinadores || []).concat(C.colaboradores || []);
    var sp = todos.map(function (s) { return '<span class="foot-sponsor' + (s.logo ? "" : " txt") + '">' + (s.logo ? '<img src="' + esc(s.logo) + '" alt="' + esc(s.nombre) + '" loading="lazy" decoding="async">' : esc(s.nombre)) + "</span>"; }).join("");
    el.innerHTML = '<footer>' +
      (sp && page !== "patrocinadores" ? '<div class="foot-sponsors"><div class="wrap"><span>Patrocinan y colaboran</span><div class="foot-logos">' + sp + '</div><a href="patrocinadores.html">Ver todos</a></div></div>' : "") +
      '<div class="wrap foot-main">' +
      '<div><img src="img/escudo.webp" alt="" loading="lazy" decoding="async"><b>Club Deportivo Ortuella</b><p>Fundado en 1949 · Otxartaga Berri, Ortuella (Bizkaia)</p></div>' +
      '<ul><li><a href="partidos.html">Partidos</a></li><li><a href="equipos.html">Equipos</a></li><li><a href="noticias.html">Noticias</a></li><li><a href="historia.html">Historia</a></li></ul>' +
      '<ul><li><a href="socios.html">Hazte socio</a></li><li><a href="tienda.html">Tienda</a></li><li><a href="patrocinadores.html">Patrocinadores</a></li><li><a href="directiva.html">Directiva</a></li><li><a href="campo.html">Otxartaga Berri</a></li><li><a href="contacto.html">Contacto</a></li></ul>' +
      '<div class="foot-contact"><span>cdortuella@cdortuella.net</span><span class="num">946 353 598</span></div>' +
      '</div><div class="wrap foot-legal">© ' + new Date().getFullYear() + ' CD Ortuella · Datos de competición: Federación Vizcaína de Fútbol<span class="legal-links"><a href="aviso-legal.html">Aviso legal</a><a href="privacidad.html">Privacidad y cookies</a></span></div></footer>';
  }

  // ---- piezas de partidos ----------------------------------------------------
  // Enlace a Google Maps con el campo del rival, para los partidos fuera
  var PIN = '<svg width="17" height="17" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>';
  function mapsLink(p, campo) {
    campo = campo || p.campo;
    if (!campo) return "";   // sin campo confirmado por la Federación no se pone mapa (sale unas semanas antes)
    var exacto = (F.mapas || {})[campo];   // coordenadas del campo, de la ficha de la Federación
    return '<a class="maps" href="https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(exacto || campo) + '" target="_blank" rel="noopener" title="Cómo llegar" aria-label="Cómo llegar a ' + esc(campo) + '">' + PIN + "</a>";
  }

  function matchCard(t) {
    var p = upcoming(t)[0];
    if (!p) return "";
    var d = day(p.fecha), days = Math.round((d - today) / 864e5);
    var when = days === 0 ? "Hoy" : days === 1 ? "Mañana" : "Faltan " + days + " días";
    return '<article class="match"><div class="head"><span><b>' + APODO[t.id] + "</b> · Jornada " + p.jornada + '</span><span class="days">' + when + "</span></div>" +
      '<div class="teams"><div class="team">' + crest(p.local, t) + "<b>" + esc(p.local) + '</b></div><div class="vs">VS</div><div class="team">' + crest(p.visitante, t) + "<b>" + esc(p.visitante) + "</b></div></div>" +
      '<div class="info"><span><strong>' + DIAL[d.getDay()] + " " + fdate(p.fecha) + "</strong></span><span>" + (isUs(p.local, t) ? "Otxartaga Berri" : esc(p.campo || "Fuera de casa")) + "</span><span>" + (p.hora ? "<strong>" + p.hora + " h</strong>" : "Hora por confirmar") + "</span></div>" +
      (isUs(p.local, t) ? "" : mapsLink(p)) + shareLink(matchShareText(p, t), "Compartir este partido por WhatsApp") + "</article>";
  }

  // Cada resultado como un marcador de dos filas: equipo a la izquierda, goles a la derecha
  function resultsStrip() {
    var WORD = { w: "Victoria", d: "Empate", l: "Derrota" };
    return '<div class="lbl">Últimos resultados</div>' + federados().map(function (t) {
      var p = played(t).slice(-1)[0];
      if (!p) return '<div class="res"><small>' + APODO[t.id] + '</small><div class="none">Sin partidos todavía</div></div>';
      var o = outcome(p, t);
      var row = function (n, g) { return '<div class="row' + (isUs(n, t) ? " us" : "") + '"><span title="' + esc(n) + '">' + esc(n) + "</span><b>" + g + "</b></div>"; };
      return '<a class="res" href="' + fichaUrl(t, p) + '" title="Ver la ficha del partido"><small>' + APODO[t.id] + " · J" + p.jornada + '<em class="o ' + o + '">' + WORD[o] + "</em></small>" + row(p.local, p.gl) + row(p.visitante, p.gv) + "</a>";
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
  var abbr = function (a, full, cls) { return "<th" + (cls ? ' class="' + cls + '"' : "") + ' title="' + full + '"><span aria-hidden="true">' + a + '</span><span class="sr-only">' + full + "</span></th>"; };
  var TABLE_HEAD = "<thead><tr>" + abbr("#", "Posición") + '<th class="t">Equipo</th>' + abbr("PJ", "Partidos jugados") + abbr("G", "Ganados", "x") + abbr("E", "Empatados", "x") + abbr("P", "Perdidos", "x") +
    abbr("GF", "Goles a favor", "x") + abbr("GC", "Goles en contra", "x") + abbr("Pts", "Puntos") + "</tr></thead>";

  var fichaUrl = function (t, p) { return "partido.html?e=" + t.id + "&j=" + p.jornada; };

  function gamesList(t, results, limit) {
    var list = results ? t.partidos.filter(function (p) { return day(p.fecha) < today; }).reverse() : upcoming(t);
    if (limit) list = list.slice(0, limit);
    if (!list.length) return '<li class="empty">' + (results ? "Todavía no se ha jugado ningún partido." : "No hay más partidos en el calendario.") + "</li>";
    var name = function (n) { return isUs(n, t) ? '<span class="us">' + esc(n) + "</span>" : esc(n); };
    return list.map(function (p) {
      var x = day(p.fecha), right;
      if (p.gl != null) { var o = outcome(p, t); right = '<a class="score ' + o + '" href="' + fichaUrl(t, p) + '" title="Ver la ficha del partido" aria-label="' + { w: "Victoria", d: "Empate", l: "Derrota" }[o] + " " + p.gl + " a " + p.gv + ". Ver la ficha del partido" + '">' + p.gl + "-" + p.gv + "</a>"; }
      else if (results) right = '<span class="score na">Sin cargar</span>';
      else right = p.hora ? '<span class="hour">' + p.hora + "</span>" : '<span class="hour tbc">Hora por confirmar</span>';
      return '<li><div class="d">' + DIA[x.getDay()] + '<b class="num">' + x.getDate() + " " + MES[x.getMonth()] + '</b></div><div class="m">' + name(p.local) + " – " + name(p.visitante) + "<small>Jornada " + p.jornada + " · " + (isUs(p.local, t) ? "En casa" : "Fuera" + (p.campo ? " · " + esc(p.campo) : "") + (results ? "" : " " + mapsLink(p))) + "</small></div>" + right + "</li>";
    }).join("");
  }

  function cardsList(t) {
    var n = {};
    played(t).forEach(function (p) {
      var a = (F.actas || {})[p.acta]; if (!a) return;
      var lado = isUs(p.local, t) ? "local" : "visitante";
      (a.tarjetas || []).forEach(function (c) {
        if (c.lado !== lado || c.tecnico) return;   // las del banquillo no cuentan como de jugador
        var x = n[c.jugador] = n[c.jugador] || { nombre: c.jugador, y: 0, r: 0 };
        if (c.tipo === "amarilla") x.y++; else x.r++;  // roja directa o segunda amarilla
      });
    });
    var list = Object.keys(n).map(function (k) { return n[k]; }).sort(function (a, b) { return b.r - a.r || b.y - a.y || a.nombre.localeCompare(b.nombre); });
    if (!list.length) return "";
    return '<ul class="cards-list">' + list.map(function (x) {
      return "<li><b>" + esc(x.nombre) + '</b><span class="cnt"><i class="card y" aria-hidden="true"></i>' + x.y + '<span class="sr-only"> amarillas</span>' + (x.r ? ' <i class="card r" aria-hidden="true"></i>' + x.r + '<span class="sr-only"> rojas</span>' : "") + "</span></li>";
    }).join("") + "</ul>";
  }

  function scorersList(t, limit) {
    var g = t.goleadores, max = g.length ? g[0].goles : 1;
    if (!g.length) return '<li class="empty">Todavía no hay goleadores registrados en la Federación.</li>';
    return g.slice(0, limit || 8).map(function (x) {
      return "<li><b>" + esc(x.nombre) + '</b><span class="g">' + x.goles + '</span><span class="bar"><i style="width:' + (x.goles / max * 100) + '%"></i></span></li>';
    }).join("");
  }

  // Porteros: goles encajados y minutos jugados (tabla pública de la Federación)
  function keepersList(t) {
    var g = t.porteros || [], max = g.length ? g[0].minutos : 1;
    if (!g.length) return '<li class="empty">Todavía no hay datos de porteros en la Federación.</li>';
    return '<li class="cap">Goles encajados · minutos jugados</li>' + g.map(function (x) {
      var media = x.minutos ? (x.goles / x.minutos * 90).toFixed(1).replace(".", ",") : "–";
      return "<li><b>" + esc(x.nombre) + "<small>" + x.minutos + " min · " + media + " por partido</small></b>" +
        '<span class="g">' + x.goles + '</span><span class="bar"><i style="width:' + (x.minutos / max * 100) + '%"></i></span></li>';
    }).join("");
  }

  function sourceNote(t) {
    var u = F.actualizado ? new Date(F.actualizado) : null;
    return "Datos de la Federación Vizcaína de Fútbol" + (u ? ", actualizados el " + u.getDate() + " " + MES[u.getMonth()] + " a las " + String(u.getHours()).padStart(2, "0") + ":" + String(u.getMinutes()).padStart(2, "0") : "") +
      (t ? '. <a href="' + esc(t.enlace) + '" target="_blank" rel="noopener">Ver en la web de la Federación</a>' : ".");
  }

  function newsCard(n, nivel) {
    var h = "h" + (nivel || 3);
    return "<article>" + (n.foto ? '<img class="pic" src="' + esc(n.foto) + '" alt="" loading="lazy">' : "") + '<div class="body">' +
      '<div class="meta"><span class="cat">' + esc(n.etiqueta) + "</span><span>" + esc(n.fechaTexto || fdate(n.fecha, true)) + "</span></div>" +
      "<" + h + ">" + esc(n.titulo) + "</" + h + "><p>" + esc(n.texto) + "</p>" +
      (n.enlace ? '<a class="more" href="' + esc(n.enlace) + '" target="_blank" rel="noopener">Ver en Instagram</a>' : "") + "</div></article>";
  }

  function copyButtons() {
    document.querySelectorAll(".copy").forEach(function (b) {
      b.setAttribute("aria-live", "polite");
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
      '<symbol id="shirt" viewBox="0 0 48 48"><path d="M16 4 L8 8 L2 18 L9 22 L12 18 V44 H36 V18 L39 22 L46 18 L40 8 L32 4 C30 8 18 8 16 4Z" fill="#1757c2" stroke="#0b2a5b" stroke-width="2"/><path d="M17 5.5 C20 8.5 28 8.5 31 5.5" fill="none" stroke="#ffffff" stroke-width="2"/></symbol>' +
      '<symbol id="scarf" viewBox="0 0 48 48"><path d="M6 10 h36 v10 h-36z" fill="#1757c2"/><path d="M6 20 h36 v10 h-36z" fill="#ffffff" stroke="#0b2a5b" stroke-width="1"/><path d="M6 30 h36 v10 h-36z" fill="#1757c2"/><path d="M6 40 v5 M12 40 v5 M18 40 v5 M24 40 v5 M30 40 v5 M36 40 v5 M42 40 v5" stroke="#0b2a5b" stroke-width="2"/></symbol>' +
      '<symbol id="ball" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#fff" stroke="currentColor" stroke-width="1.6"/><path d="M12 7.2l4.3 3.1-1.6 5h-5.4l-1.6-5z" fill="currentColor"/><path d="M12 7.2V2.3M16.3 10.3l4.6-1.5M14.7 15.3l2.9 4M9.3 15.3l-2.9 4M7.7 10.3L3.1 8.8" stroke="currentColor" stroke-width="1.4" fill="none"/></symbol>' +
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
    label = label || "Compartir por WhatsApp";
    return '<a class="share" href="https://wa.me/?text=' + encodeURIComponent(text) + '" target="_blank" rel="noopener" title="' + label + '" aria-label="' + label + '">' + BUBBLE + "</a>";
  }
  function matchLine(p, t) {
    if (p.gl != null) return APODO[t.id] + ": " + p.local + " " + p.gl + "-" + p.gv + " " + p.visitante;
    return APODO[t.id] + ": " + p.local + " – " + p.visitante + (p.hora ? ", " + p.hora + " h" : "") + (isUs(p.local, t) ? " (en casa, Otxartaga Berri)" : " (fuera)");
  }
  function matchShareText(p, t) {
    return "⚽ " + APODO[t.id] + " · Jornada " + p.jornada + "\n" + p.local + " – " + p.visitante + "\n📅 " + longDate(p.fecha) + (isUs(p.local, t) ? " · Otxartaga Berri" : " · Fuera de casa" + (p.campo ? " (" + p.campo + ")" : "")) + "\n" + (p.hora ? "🕐 " + p.hora + " h" : "Hora por confirmar") + "\n\n" + webUrl("partidos.html");
  }
  // Enlaces para suscribirse al calendario .ics de un equipo (o "todos")
  function calHrefs(slug) {
    var url = webUrl("calendario/" + slug + ".ics"), webcal = url.replace(/^https?:/, "webcal:");
    return { url: url, apple: webcal, google: "https://calendar.google.com/calendar/render?cid=" + encodeURIComponent(webcal) };
  }

  function formDots(t) {
    var WORD = { w: "victoria", d: "empate", l: "derrota" };
    var label = "Últimos resultados: " + played(t).slice(-5).map(function (p) { return WORD[outcome(p, t)]; }).join(", ");
    return '<div class="form-dots" role="img" aria-label="' + label + '">' + played(t).slice(-5).map(function (p) { var o = outcome(p, t); return '<i class="' + o + '" title="' + esc(p.local + " " + p.gl + "-" + p.gv + " " + p.visitante) + '">' + { w: "V", d: "E", l: "D" }[o] + "</i>"; }).join("") + "</div>";
  }

  sprite();
  renderHeader();
  renderFooter();
  document.querySelectorAll(".season").forEach(function (el) { el.textContent = F.temporada || "2026/27"; });

  // Ficha de patrocinador o colaborador: logo si lo hay; si no, el nombre
  function sponsorCard(s) {
    var inner = s.logo ? '<img src="' + esc(s.logo) + '" alt="' + esc(s.nombre) + '" loading="lazy" decoding="async">'
      : '<b>' + esc(s.nombre) + '</b>';
    var cap = '<span class="sp-cap">' + (s.logo ? '<b>' + esc(s.nombre) + '</b>' : "") + (s.detalle ? '<small>' + esc(s.detalle) + '</small>' : "") + '</span>';
    var box = '<span class="sp-box' + (s.logo ? "" : " txt") + '">' + inner + '</span>' + cap;
    return s.web ? '<a class="sp" href="' + esc(s.web) + '" target="_blank" rel="noopener">' + box + '</a>' : '<div class="sp">' + box + '</div>';
  }

  // Cerrar el desplegable «Al calendario» al tocar fuera o pulsar Escape
  document.addEventListener("click", function (e) {
    [].forEach.call(document.querySelectorAll("details.cal-pop[open]"), function (d) { if (!d.contains(e.target)) d.open = false; });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") [].forEach.call(document.querySelectorAll("details.cal-pop[open]"), function (d) { d.open = false; });
  });

  // Pestañas (Próximos / Resultados, Goleadores / Porteros, alineaciones): se cambia con las flechas, como en cualquier programa
  document.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    var tab = e.target.closest && e.target.closest('[role="tab"]'); if (!tab) return;
    var tabs = [].slice.call(tab.parentNode.querySelectorAll('[role="tab"]')), i = tabs.indexOf(tab);
    var next = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
    e.preventDefault(); next.focus(); next.click();
  });

  window.CDO = { sponsorCard: sponsorCard, C: C, SLUG: SLUG, formDots: formDots, crest: crest, F: F, esc: esc, fdate: fdate, day: day, APODO: APODO, team: team, isUs: isUs, played: played, upcoming: upcoming, outcome: outcome, ourRow: ourRow,
    matchCard: matchCard, resultsStrip: resultsStrip, tableRows: tableRows, TABLE_HEAD: TABLE_HEAD, gamesList: gamesList, scorersList: scorersList, keepersList: keepersList, sourceNote: sourceNote, newsCard: newsCard, copyButtons: copyButtons, shareLink: shareLink, mapsLink: mapsLink, fichaUrl: fichaUrl, cardsList: cardsList, federados: federados, matchLine: matchLine, longDate: longDate, webUrl: webUrl, calHrefs: calHrefs };
})();
