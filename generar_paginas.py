# Genera las páginas HTML (index, partidos, equipos...) a partir de una plantilla común.
# Uso: python3 generar_paginas.py  (sobrescribe los .html de esta carpeta)
import os
D = os.path.dirname(os.path.abspath(__file__))

HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<!-- Mientras la web esté en pruebas, que no salga en Google -->
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="img/escudo.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Big+Shoulders+Display:wght@700;800;900&display=swap">
<link rel="stylesheet" href="estilos.css">
</head>
<body data-page="{page}">
<div id="cabecera"></div>
<main>
"""
FOOT = """</main>
<div id="pie"></div>
<script src="datos.js"></script>
<script src="datos-federacion.js"></script>
<script src="comun.js"></script>
<script>
{script}
</script>
</body>
</html>
"""

def hero(title, text, crumb, img=None):
    style = ' style="--hero-img:url(\'img/%s\')"' % img if img else ""
    return """<section class="page-hero"%s>
  <div class="wrap">
    <div class="crumbs"><a href="./">Inicio</a> / %s</div>
    <h1>%s</h1>
    <p>%s</p>
  </div>
</section>
""" % (style, crumb, title, text)

PAGES = {}

# ---------------------------------------------------------------- INICIO
PAGES["index"] = dict(
 title="CD Ortuella", desc="Club Deportivo Ortuella: partidos, resultados, clasificaciones, noticias y equipos. Desde 1949 en Otxartaga Berri.",
 body="""<section class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow">Otxartaga Berri · Ortuella · Desde 1949</span>
      <h1>Club Deportivo <span>Ortuella</span></h1>
      <p class="lead">Más de 75 años de fútbol en Ortuella. Primer equipo, filial y cantera, todos de azul y blanco.</p>
      <div class="btns">
        <a class="btn" href="partidos.html">Partidos y resultados</a>
        <a class="btn ghost" href="socios.html">Hazte socio</a>
      </div>
    </div>
    <div class="next" id="nextMatches" aria-label="Próximos partidos"></div>
  </div>
</section>

<div class="strip" aria-label="Últimos resultados"><div class="wrap" id="strip"></div></div>

<section class="block">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="kicker">Temporada <span class="season"></span></span><h2>Cómo vamos</h2></div>
      <a class="more" href="partidos.html">Todos los partidos</a>
    </div>
    <div class="home-grid" id="standings"></div>
    <p class="source" id="source"></p>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="kicker">Actualidad</span><h2>Noticias</h2></div>
      <a class="more" href="noticias.html">Todas las noticias</a>
    </div>
    <div class="news" id="newsList"></div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="kicker">Apoya al club</span><h2>Ser del Ortuella</h2></div>
    </div>
    <div class="quick" id="quick"></div>
  </div>
</section>

<section class="block dark">
  <div class="wrap ig-band">
    <div><span class="kicker">@cdortuella</span><h2>Síguenos en Instagram</h2><p>Fotos de los partidos, convocatorias y todo lo que pasa en Otxartaga.</p></div>
    <a class="btn" href="https://www.instagram.com/cdortuella/" target="_blank" rel="noopener">Abrir Instagram</a>
  </div>
</section>
""",
 script="""(function () {
  var X = window.CDO, C = X.C, esc = X.esc;
  // Próximo partido del Senior A y del Senior B
  document.getElementById("nextMatches").innerHTML = ["primer", "b"].map(function (id) { var t = X.team(id); return t ? X.matchCard(t) : ""; }).join("");
  document.getElementById("strip").innerHTML = X.resultsStrip();

  // Clasificación resumida del Senior A y del Senior B
  document.getElementById("standings").innerHTML = ["primer", "b"].map(function (id) {
    var t = X.team(id); if (!t) return "";
    var r = X.ourRow(t), last = X.played(t).slice(-1)[0];
    return '<div class="panel"><h3>' + X.APODO[id] + '</h3><div class="sub">' + esc(t.categoria) + (r ? " · <b>" + r.pos + "º con " + r.pts + " puntos</b>" : "") + "</div>" +
      '<div class="table-scroll"><table>' + X.TABLE_HEAD + "<tbody>" + X.tableRows(t, true) + "</tbody></table></div>" +
      '<div class="panel-foot">' + (last ? "Último: " + esc(last.local) + " <b>" + last.gl + "-" + last.gv + "</b> " + esc(last.visitante) + " · " : "") +
      '<a class="more" href="equipos.html#' + X.SLUG[id] + '">Ver equipo</a></div></div>';
  }).join("");
  document.getElementById("source").innerHTML = X.sourceNote();

  document.getElementById("newsList").innerHTML = C.noticias.slice(0, 4).map(X.newsCard).join("");

  // Avisos: socio, tienda e inscripciones
  var price = function (name) { var it = (C.tienda || []).filter(function (x) { return x.nombre.indexOf(name) === 0; })[0]; return it && it.precio ? it.precio : ""; };
  document.getElementById("quick").innerHTML = [
    ["socios.html", "Hazte socio", C.socio.precio + " " + C.socio.periodo + ". Apoya al primer equipo y a la cantera."],
    ["socios.html#tienda", "Camiseta 75 aniversario", price("Camiseta") + ". Edición especial por los 75 años del club."],
    ["socios.html#tienda", "Bufanda del club", price("Bufanda") + ". Azul y blanca, para la grada de Otxartaga."],
    ["contacto.html", "Juega en el Ortuella", "Inscripciones abiertas para la temporada. Llama al 696 51 24 69."]
  ].map(function (q) { return '<a href="' + q[0] + '"><b>' + q[1] + "</b><span>" + esc(q[2]) + "</span></a>"; }).join("");
})();""")

# ---------------------------------------------------------------- PARTIDOS
PAGES["partidos"] = dict(
 title="Partidos · CD Ortuella", desc="Próximos partidos y resultados de todos los equipos del CD Ortuella.",
 body=hero("Partidos", "Próximos partidos y resultados de todos nuestros equipos. Se actualizan solos con los datos de la Federación.", "Partidos") + """
<section class="block">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="kicker">Temporada <span class="season"></span></span><h2 id="listTitle">Próximos partidos</h2></div>
      <div class="tabs" role="tablist" style="border:0;padding:0">
        <button role="tab" id="tabNext" aria-selected="true">Próximos</button>
        <button role="tab" id="tabRes" aria-selected="false">Resultados</button>
      </div>
    </div>
    <div class="agenda" id="agenda"></div>
    <p class="source" id="source"></p>
  </div>
</section>
""",
 script="""(function () {
  var X = window.CDO, F = X.F, esc = X.esc;
  var DIAL = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
  var MESL = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var showResults = location.hash === "#resultados";

  function render() {
    document.getElementById("tabNext").setAttribute("aria-selected", !showResults);
    document.getElementById("tabRes").setAttribute("aria-selected", showResults);
    document.getElementById("listTitle").textContent = showResults ? "Resultados" : "Próximos partidos";
    // Juntar los partidos de todos los equipos y agrupar por fin de semana (fecha)
    var all = [];
    F.equipos.forEach(function (t, i) { t.partidos.forEach(function (p) { all.push({ p: p, t: t, i: i }); }); });
    all = all.filter(function (x) { var past = X.day(x.p.fecha) < today; return showResults ? past : !past; });
    all.sort(function (a, b) { if (a.p.fecha === b.p.fecha) return a.i - b.i; return showResults ? (a.p.fecha < b.p.fecha ? 1 : -1) : (a.p.fecha > b.p.fecha ? 1 : -1); });
    var groups = [], seen = {};
    all.forEach(function (x) { if (!seen[x.p.fecha]) { seen[x.p.fecha] = []; groups.push(x.p.fecha); } seen[x.p.fecha].push(x); });
    groups = groups.slice(0, showResults ? 8 : 6);
    if (!groups.length) { document.getElementById("agenda").innerHTML = '<p class="empty">' + (showResults ? "Todavía no hay resultados." : "No hay partidos en el calendario.") + "</p>"; return; }
    document.getElementById("agenda").innerHTML = groups.map(function (f) {
      var d = X.day(f);
      return '<div class="agenda-day"><h3>' + DIAL[d.getDay()] + " " + d.getDate() + " de " + MESL[d.getMonth()] + '</h3><div class="panel"><ul class="games">' + seen[f].map(function (x) {
        var p = x.p, t = x.t, right;
        var name = function (n) { return X.isUs(n, t) ? '<span class="us">' + esc(n) + "</span>" : esc(n); };
        if (p.gl != null) { var o = X.outcome(p, t); right = '<span class="score ' + o + '">' + p.gl + "-" + p.gv + "</span>"; }
        else if (showResults) right = '<span class="score na">Sin cargar</span>';
        else right = '<span class="hour tbc">Hora por confirmar</span>';
        return '<li><div class="d">Jornada ' + p.jornada + '<b><a href="equipos.html#' + X.SLUG[t.id] + '" style="text-decoration:none">' + X.APODO[t.id] + '</a></b></div><div class="m">' + name(p.local) + " – " + name(p.visitante) + "<small>" + (X.isUs(p.local, t) ? "En casa · Otxartaga Berri" : "Fuera") + "</small></div>" + right + "</li>";
      }).join("") + "</ul></div></div>";
    }).join("");
  }
  document.getElementById("tabNext").addEventListener("click", function () { showResults = false; render(); });
  document.getElementById("tabRes").addEventListener("click", function () { showResults = true; render(); });
  document.getElementById("source").innerHTML = X.sourceNote();
  render();
})();""")

# ---------------------------------------------------------------- EQUIPOS
PAGES["equipos"] = dict(
 title="Equipos · CD Ortuella", desc="Clasificación, partidos, goleadores y plantilla de cada equipo del CD Ortuella.",
 body="""<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="./">Inicio</a> / <a href="equipos.html">Equipos</a><span id="crumb"></span></div>
    <h1 id="teamName">Nuestros equipos</h1>
    <p id="teamSub">Del fútbol base al primer equipo.</p>
  </div>
</section>
<nav class="subnav" aria-label="Elegir equipo"><div class="wrap" id="subnav"></div></nav>
<div id="teamView"></div>
""",
 script="""(function () {
  var X = window.CDO, C = X.C, F = X.F, esc = X.esc;
  var BY_SLUG = {}; F.equipos.forEach(function (t) { BY_SLUG[X.SLUG[t.id]] = t; });
  var $ = function (id) { return document.getElementById(id); };

  function nav(cur) {
    $("subnav").innerHTML = '<a class="chip" href="equipos.html"' + (!cur ? ' aria-current="page"' : "") + ">Todos</a>" +
      F.equipos.map(function (t) { var s = X.SLUG[t.id]; return '<a class="chip" href="#' + s + '"' + (cur === s ? ' aria-current="page"' : "") + ">" + X.APODO[t.id] + "</a>"; }).join("") +
      '<a class="chip" href="#base"' + (cur === "base" ? ' aria-current="page"' : "") + ">Fútbol base</a>";
  }
  function heading(name, sub, crumb) { $("teamName").textContent = name; $("teamSub").textContent = sub; $("crumb").textContent = crumb ? " / " + crumb : ""; document.title = (crumb || "Equipos") + " · CD Ortuella"; }

  function overview() {
    heading("Nuestros equipos", "Del fútbol base al primer equipo. Elige uno para ver su clasificación, partidos y goleadores.", "");
    $("teamView").innerHTML = '<section class="block"><div class="wrap"><div class="teams-grid">' + F.equipos.map(function (t) {
      var r = X.ourRow(t);
      return '<a class="team-card" href="#' + X.SLUG[t.id] + '"><svg width="40" height="40" aria-hidden="true"><use href="#shirt"/></svg><h3>' + X.APODO[t.id] + "</h3><p>" + esc(t.categoria) + "</p>" +
        (r ? '<div class="pos-line">' + r.pos + "º · " + r.pts + " puntos</div>" : "") + '<span class="go">Ver equipo</span></a>';
    }).join("") + '<a class="team-card" href="#base"><svg width="40" height="40" aria-hidden="true"><use href="#shirt"/></svg><h3>Fútbol base</h3><p>Infantil, alevín y benjamín</p><span class="go">Ver equipos</span></a></div></div></section>';
  }

  function base() {
    heading("Fútbol base", "La cantera del Ortuella. Inscripciones en el 696 51 24 69.", "Fútbol base");
    $("teamView").innerHTML = '<section class="block"><div class="wrap"><div class="teams-grid">' + C.equiposBase.map(function (t) {
      return '<div class="team-card"><svg width="40" height="40" aria-hidden="true"><use href="#shirt"/></svg><h3>' + esc(t.nombre) + "</h3><p>" + esc(t.categoria) + "</p>" + (t.pendiente ? '<div class="pos-line"><span class="pending">Pendiente de confirmar</span></div>' : "") + "</div>";
    }).join("") + '</div><p class="source">Juvenil y cadete compiten en la Federación: los tienes arriba con su clasificación.</p></div></section>';
  }

  function squad() {
    var pe = C.primerEquipo; if (!pe) return "";
    var pl = function (p) { return '<div class="player"><span class="dorsal">' + p[0] + "</span><b>" + esc(p[1]) + "</b></div>"; };
    return '<section class="block alt"><div class="wrap"><div class="sec-head"><div><span class="kicker">Plantilla</span><h2>Convocatoria</h2></div><p>Último partido: ' + esc(pe.partido) + ". La plantilla completa, con fotos, llegará pronto.</p></div>" +
      '<div class="squad-wrap"><div class="squad"><div class="squad-label">Titulares</div>' + pe.titulares.map(pl).join("") + '<div class="squad-label">Suplentes</div>' + pe.suplentes.map(pl).join("") + "</div>" +
      '<aside class="staff"><h3>Cuerpo técnico</h3><dl>' + pe.cuerpoTecnico.map(function (s) { return "<div><dt>" + esc(s[0]) + "</dt><dd>" + esc(s[1]) + "</dd></div>"; }).join("") + "</dl></aside></div></div></section>";
  }

  function teamPage(t) {
    var r = X.ourRow(t), showResults = false;
    heading(X.APODO[t.id], t.categoria, X.APODO[t.id]);
    var goals = t.goleadores.reduce(function (a, g) { return a + g.goles; }, 0);
    $("teamView").innerHTML = '<section class="block"><div class="wrap">' +
      '<div class="stats">' +
        '<div class="stat"><b>' + (r ? r.pos + "º" : "–") + "</b><small>Posición</small></div>" +
        '<div class="stat"><b>' + (r ? r.pts : "–") + "</b><small>Puntos</small></div>" +
        '<div class="stat"><b>' + (r ? r.gf + "-" + r.gc : "–") + "</b><small>Goles a favor y en contra</small></div>" +
        '<div class="stat"><small>Últimos partidos</small>' + X.formDots(t) + "</div>" +
      "</div>" +
      '<div class="comp"><div><div class="panel"><h3>Clasificación</h3><div class="sub">' + esc(t.categoria) + '</div><div class="table-scroll"><table>' + X.TABLE_HEAD + "<tbody>" + X.tableRows(t) + "</tbody></table></div></div></div>" +
      '<div><div class="panel"><h3>Partidos</h3><div class="tabs" role="tablist"><button role="tab" id="tabNext" aria-selected="true">Próximos</button><button role="tab" id="tabRes" aria-selected="false">Resultados</button></div><ul class="games" id="games"></ul></div>' +
      '<div class="panel"><h3>Goleadores</h3><ul class="scorers">' + X.scorersList(t) + "</ul></div></div></div>" +
      '<p class="source">' + X.sourceNote(t) + "</p></div></section>" + (t.id === "primer" ? squad() : "");
    var games = function () {
      $("tabNext").setAttribute("aria-selected", !showResults); $("tabRes").setAttribute("aria-selected", showResults);
      $("games").innerHTML = X.gamesList(t, showResults, showResults ? 0 : 8);
    };
    $("tabNext").addEventListener("click", function () { showResults = false; games(); });
    $("tabRes").addEventListener("click", function () { showResults = true; games(); });
    games();
  }

  function route() {
    var s = location.hash.slice(1);
    nav(s);
    if (BY_SLUG[s]) teamPage(BY_SLUG[s]); else if (s === "base") base(); else overview();
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);
  route();
})();""")

# ---------------------------------------------------------------- NOTICIAS
PAGES["noticias"] = dict(
 title="Noticias · CD Ortuella", desc="Noticias del CD Ortuella: primer equipo, fútbol base y vida del club.",
 body=hero("Noticias", "Lo último del club, del primer equipo y del fútbol base.", "Noticias", "campo.jpg") + """
<section class="block alt">
  <div class="wrap"><div class="news" id="newsList"></div></div>
</section>
""",
 script="""document.getElementById("newsList").innerHTML = window.CDO.C.noticias.map(window.CDO.newsCard).join("");""")

# ---------------------------------------------------------------- HISTORIA
PAGES["historia"] = dict(
 title="Historia · CD Ortuella", desc="Historia, palmarés, colores y escudo del Club Deportivo Ortuella desde 1949.",
 body=hero("Historia", "Nacido en 1949 en la cocina de la casa parroquial, el Ortuella ha jugado en todas las categorías regionales y llegó a la Tercera División.", "Club / Historia") + """
<section class="block">
  <div class="wrap">
    <ol class="timeline">
      <li><div class="y num">1949</div><h3>Nace el club</h3><p>En agosto se funda el Club Deportivo Ortuella. Juan Antonio Ipiña, jugador del Real Madrid, forma el primer equipo.</p></li>
      <li><div class="y num">1951</div><h3>Campo de Otxartaga</h3><p>Tras jugar en el Malecón de Muskiz y en la balsa de Bañales, el club estrena campo propio en la campa de Otxartaga.</p></li>
      <li><div class="y num">1984</div><h3>Otxartaga Berri</h3><p>El 29 de agosto se inaugura el nuevo campo con un partido ante el Bilbao Athletic (0-3).</p></li>
      <li><div class="y num">1985</div><h3>Tercera División</h3><p>Tras ascender en la promoción, el Ortuella juega la temporada 1985/86 en Tercera División.</p></li>
      <li><div class="y num">2024</div><h3>75 aniversario</h3><p>Exposición en la Kultur Etxea: «Un paseo por la historia del Club y del fútbol regional vizcaíno».</p></li>
    </ol>
    <div class="story">
      <div class="prose">
        <p>Después de la guerra, el fútbol vivía un momento de enorme afición en Ortuella, animada por los éxitos de un vecino del pueblo, Juan Antonio Ipiña, que jugaba en el Real Madrid y en la selección española. En 1949, cuando Ortuella tenía 5.530 habitantes, un grupo de aficionados vinculados a Acción Católica empezó a reunirse en la cocina de la casa parroquial, con el párroco José María Sukia, para crear un club federado.</p>
        <p>En agosto de 1949 nació el Club Deportivo Ortuella. Ipiña, que pasaba el verano en el pueblo, seleccionó y preparó al primer equipo, dirigido por Federico Cavia Ansola, que era a la vez entrenador y jugador. La primera sede estuvo en el bar del directivo Julián Melgosa, en la calle Catalina Gibaja.</p>
        <p>En 1977 el club compró su sede actual, en Catalina Gibaja 1, con los directivos avalando el crédito con su propio patrimonio. Tras la conmoción del 23 de octubre de 1980, el equipo se quedó sin campo a mitad de temporada y jugó como local en Gallarta, hasta que en 1984 se inauguró Otxartaga Berri. El césped artificial llegó en 2005 y se renovó por completo en 2018, junto con los banquillos, el marcador, la cubierta de la tribuna y los vestuarios.</p>
      </div>
      <aside class="founders">
        <h3>Junta fundadora (1949)</h3>
        <p><strong>Presidente:</strong> Pedro Mariscal Arana</p>
        <p><strong>Vicepresidente:</strong> Santiago Fernández Ruiz</p>
        <p><strong>Secretario:</strong> José Ángel Múgica García</p>
        <p><strong>Tesorero:</strong> Francisco Ibáñez Elizburu</p>
        <p><strong>Vocales:</strong> Iñaki Atxa González, José Mª Ipiña Iza, Julián Melgosa Sacristán, Valentín Ruiz Soria, José Torróntegi Aiestarán y Eugenio Zubimendi Marcé</p>
      </aside>
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="sec-head"><div><span class="kicker">Palmarés</span><h2>Lo que hemos ganado</h2></div></div>
    <div class="honours" style="margin-top:0">
      <div class="honour"><b>1985/86</b><span>Tercera División estatal</span></div>
      <div class="honour"><b>3 temporadas</b><span>en División de Honor (2007-2010)</span></div>
      <div class="honour"><b>2006/07</b><span>Campeón de Preferente</span></div>
      <div class="honour"><b>1955/56</b><span>Campeón de la Copa Bizkaia</span></div>
    </div>
  </div>
</section>

<section class="block" id="escudo">
  <div class="wrap">
    <div class="crest-block">
      <img src="img/escudo.webp" alt="Escudo del Club Deportivo Ortuella">
      <div>
        <span class="kicker">Identidad</span>
        <h2 style="font-size:clamp(40px,6vw,62px);font-weight:900">Colores y escudo</h2>
        <p style="max-width:60ch">El azul y el blanco visten al Ortuella desde su fundación. El escudo es el que luce la camiseta en cada partido en Otxartaga Berri.</p>
        <div class="swatches">
          <div class="swatch"><i style="background:#1757c2"></i><span>Azul</span></div>
          <div class="swatch"><i style="background:#0b2a5b"></i><span>Azul marino</span></div>
          <div class="swatch"><i style="background:#ffffff"></i><span>Blanco</span></div>
        </div>
      </div>
    </div>
  </div>
</section>
""", script="")

# ---------------------------------------------------------------- DIRECTIVA
PAGES["directiva"] = dict(
 title="Directiva · CD Ortuella", desc="Junta directiva del Club Deportivo Ortuella.",
 body=hero("Directiva", "Las personas que sacan adelante el club.", "Club / Directiva") + """
<section class="block">
  <div class="wrap">
    <div class="notice">Datos de la web antigua. Pendiente de confirmar que siguen al día.</div>
    <div class="board" id="boardList" style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))"></div>
    <p class="source">¿Quieres echar una mano en el club? <a href="contacto.html">Escríbenos</a>.</p>
  </div>
</section>
""",
 script="""document.getElementById("boardList").innerHTML = window.CDO.C.directiva.map(function (d) { return "<div><small>" + window.CDO.esc(d[0]) + "</small><b>" + window.CDO.esc(d[1]) + "</b></div>"; }).join("");""")

# ---------------------------------------------------------------- CAMPO
PAGES["campo"] = dict(
 title="Otxartaga Berri · CD Ortuella", desc="Campo de fútbol Otxartaga Berri, en Ortuella: cómo llegar, aforo y entradas.",
 body=hero("Otxartaga Berri", "Nuestra casa desde 1984, en la Avenida de la Estación de Ortuella.", "Club / Otxartaga Berri", "campo.jpg") + """
<section class="block">
  <div class="wrap club-grid">
    <div class="ground">
      <img src="img/campo.jpg" alt="Campo de Otxartaga Berri con la tribuna y los montes al fondo">
      <div class="facts">
        <div><b class="num">100×60</b><small>metros</small></div>
        <div><b class="num">512</b><small>asientos en grada</small></div>
        <div><b>1984</b><small>inaugurado</small></div>
      </div>
      <p>Hierba artificial renovada en 2018. Aforo máximo en partidos: 644 personas.</p>
    </div>
    <div class="prose">
      <h3 style="margin-top:0">Cómo llegar</h3>
      <p><strong>Dirección:</strong> Avenida de la Estación s/n, 48530 Ortuella (Bizkaia).</p>
      <p><a href="https://www.google.com/maps/search/?api=1&query=Campo+de+f%C3%BAtbol+Otxartaga+Ortuella" target="_blank" rel="noopener">Abrir en Google Maps</a>.</p>
      <h3>Entradas</h3>
      <div class="tickets" id="ticketList"></div>
      <p class="source">Precios de la web antigua, pendientes de confirmar.</p>
      <h3>La tribuna</h3>
      <img src="img/entrada.jpg" alt="Entrada al campo de Otxartaga Berri" style="border-radius:6px;display:block;width:100%;max-width:100%;aspect-ratio:16/9;object-fit:cover">
    </div>
  </div>
</section>
""",
 script="""document.getElementById("ticketList").innerHTML = (window.CDO.C.entradas || []).map(function (e) { return "<div><small>" + window.CDO.esc(e[0]) + "</small><b>" + window.CDO.esc(e[1]) + "</b></div>"; }).join("");""")

# ---------------------------------------------------------------- SOCIOS
PAGES["socios"] = dict(
 title="Socios y tienda · CD Ortuella", desc="Hazte socio del CD Ortuella, compra la camiseta del 75 aniversario y patrocina al club.",
 body=hero("Hazte socio", "Cada carnet y cada bufanda ayudan a que el Ortuella siga adelante.", "Socios y tienda") + """
<section class="block">
  <div class="wrap support">
    <div class="card-socio">
      <h3>Carnet de socio</h3>
      <div class="price" id="socioPrice"></div>
      <p class="socio-other" id="socioOther"></p>
      <ul>
        <li>Apoyas al primer equipo y a toda la cantera.</li>
        <li>Formas parte de la vida del club.</li>
      </ul>
      <a class="btn" href="contacto.html">Quiero hacerme socio</a>
    </div>
    <div id="tienda">
      <h3 class="mini">Tienda del club</h3>
      <div class="shop" id="shopList"></div>
      <p class="source">Para comprar, pásate por la oficina del club o escríbenos por redes sociales.</p>
    </div>
  </div>
</section>

<section class="block alt" id="patrocina">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="kicker">Empresas</span><h2>Patrocinadores</h2></div>
      <p>Gracias a quienes apoyan al Ortuella. ¿Tienes un negocio en la zona? Hay sitio para ti.</p>
    </div>
    <div class="sponsor-row" id="sponsorList"></div>
    <div class="helpers" id="helpersList"></div>
  </div>
</section>
""",
 script="""(function () {
  var X = window.CDO, C = X.C, esc = X.esc;
  document.getElementById("socioPrice").innerHTML = esc(C.socio.precio) + "<small>" + esc(C.socio.periodo) + "</small>";
  document.getElementById("socioOther").textContent = (C.socio.otros || []).map(function (o) { return o[0] + ": " + o[1] + " " + C.socio.periodo; }).join(" · ");
  document.getElementById("shopList").innerHTML = C.tienda.map(function (it) {
    var icon = /bufanda/i.test(it.nombre) ? "scarf" : "shirt";
    return '<div class="item"><div class="ph">' + (it.foto ? '<img src="' + esc(it.foto) + '" alt="" loading="lazy">' : '<svg aria-hidden="true" viewBox="0 0 48 48"><use href="#' + icon + '"/></svg>') + '</div><div class="t"><b>' + esc(it.nombre) + "</b><small>" + (it.precio ? esc(it.precio) : "Precio por confirmar") + "</small></div></div>";
  }).join("");
  var slots = C.patrocinadores.map(function (s) { return '<div class="logo">' + (s.logo ? '<img src="' + esc(s.logo) + '" alt="' + esc(s.nombre) + '">' : esc(s.nombre)) + "</div>"; });
  while (slots.length < 4) slots.push('<a class="free" href="contacto.html"><div>¿Tu negocio aquí?<br>Patrocina al Ortuella</div></a>');
  document.getElementById("sponsorList").innerHTML = slots.join("");
  document.getElementById("helpersList").innerHTML = "<strong>Con el apoyo de:</strong>" + C.colaboradores.map(function (c) { return "<span>" + esc(c) + "</span>"; }).join("");
})();""")

# ---------------------------------------------------------------- CONTACTO
PAGES["contacto"] = dict(
 title="Contacto · CD Ortuella", desc="Teléfono, email, dirección y redes sociales del CD Ortuella.",
 body=hero("Contacto", "¿Quieres jugar en el Ortuella, hacerte socio o patrocinar al club? Escríbenos o llámanos.", "Contacto", "entrada.jpg") + """
<section class="block dark">
  <div class="wrap contact">
    <dl>
      <dt>Campo</dt><dd>Avda. de la Estación s/n, 48530 Ortuella (Bizkaia)</dd>
      <dt>Sede</dt><dd>Catalina Gibaja 1, Ortuella</dd>
      <dt>Oficina</dt><dd><span class="num">946 353 598</span><button class="copy" data-copy="946353598">Copiar</button></dd>
      <dt>Inscripciones</dt><dd><span class="num">696 51 24 69</span><button class="copy" data-copy="696512469">Copiar</button></dd>
      <dt>Email</dt><dd>cdortuella@cdortuella.net<button class="copy" data-copy="cdortuella@cdortuella.net">Copiar</button></dd>
    </dl>
    <div class="social">
      <a href="https://www.instagram.com/cdortuella/" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>
        <span><b>Instagram</b><small>@cdortuella</small></span>
      </a>
      <a href="https://www.facebook.com/cdortuella1945/" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8h3V4h-3c-2.8 0-4 1.8-4 4.3V10H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/></svg>
        <span><b>Facebook</b><small>Club Deportivo Ortuella</small></span>
      </a>
      <a href="https://x.com/CD_Ortuella" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.8 3h3.3l-7.2 8.2L22.4 21h-6.6l-5.2-6.8L4.7 21H1.4l7.7-8.8L1 3h6.8l4.7 6.2zm-1.2 16h1.8L6.5 4.9H4.6z"/></svg>
        <span><b>X (Twitter)</b><small>@CD_Ortuella</small></span>
      </a>
    </div>
  </div>
</section>
""",
 script="""window.CDO.copyButtons();""")

for name, p in PAGES.items():
    html = HEAD.format(title=p["title"], desc=p["desc"], page=name) + p["body"] + FOOT.format(script=p["script"])
    open(os.path.join(D, name + ".html"), "w").write(html)
    print("ok", name)

open(os.path.join(D, "robots.txt"), "w").write("# Web en pruebas: que no la indexe ningún buscador\nUser-agent: *\nDisallow: /\n")
open(os.path.join(D, ".nojekyll"), "w").write("")
