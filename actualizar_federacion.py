#!/usr/bin/env python3
"""
Actualiza los datos de la web del CD Ortuella con la información pública de la
Federación Vizcaína de Fútbol (www.fvf-bff.eus).

Genera el archivo datos-federacion.js con, para cada equipo:
clasificación, calendario, resultados, goleadores y porteros del club, y las actas de
nuestros partidos (goles, tarjetas, alineaciones, cambios), el campo de cada rival y sus escudos.
Después regenera los calendarios del móvil (carpeta calendario/).

Uso:  python3 actualizar_federacion.py
Solo usa la biblioteca estándar de Python, para que funcione en cualquier sitio.

Para no cargar el servidor de la Federación:
- espera un poco entre peticiones
- solo descarga los resultados de las jornadas que aún no tenemos guardadas
"""
import html
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

import generar_calendario

BASE = "https://www.fvf-bff.eus/pnfg/NPcd/"
TEMPORADA = 22            # 22 = temporada 2026-2027 en la web de la Federación
TEMPORADA_TEXTO = "2026/27"
PAUSA = 1.5               # segundos entre peticiones

# Equipos del club. codequipo/codcompeticion/codgrupo salen de las direcciones
# de la web de la Federación. Si un equipo cambia de grupo, se cambia aquí.
EQUIPOS = [
    {"id": "primer", "nombre": "CD Ortuella", "categoria": "Segunda División (2A) · Grupo 1",
     "codequipo": 13460, "codcompeticion": 24058476, "codgrupo": 24109531},
    {"id": "b", "nombre": "CD Ortuella B", "categoria": "Tercera División (3A) · Grupo 1",
     "codequipo": 24025460, "codcompeticion": 24058477, "codgrupo": 24217592},
    {"id": "juvenil", "nombre": "Juvenil", "categoria": "Juvenil Segunda División (2J) · Grupo 1",
     "codequipo": 13458, "codcompeticion": 24058483, "codgrupo": 24155611},
    {"id": "cadete", "nombre": "Cadete", "categoria": "Cadete Tercera División (3C) · Grupo 1",
     "codequipo": 13456, "codcompeticion": 24247513, "codgrupo": 24249031},
    # Fútbol base (deporte escolar): página propia como los demás, pero fuera de la portada.
    # Antes de empezar la liga no hay clasificación; por eso se da el nombre que usa la Federación.
    {"id": "infantil", "nombre": "Infantil", "categoria": "Infantil Liga D (Bizkaia) · Grupo 1", "base": True,
     "nombre_fed": "Ortuella2013-14", "nombre_web": "Ortuella",
     "codequipo": 25186751, "codcompeticion": 25093697, "codgrupo": 25189413},
]

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "datos-federacion.js")

_cookies = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
_opener = urllib.request.build_opener(_cookies)
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (compatible; CDOrtuellaWeb/1.0; web del CD Ortuella)"),
                      ("Accept-Language", "es-ES,es;q=0.9")]


# Algunas páginas de la Federación están siempre vacías (está mal hecha): esperar no sirve de nada.
# Cada página se intenta 3 veces en poco tiempo y, si no hay manera, se salta y se sigue con lo demás.
ESPERAS = [5, 15]               # segundos antes de cada reintento (antes eran ~4 minutos por página vacía)
VACIAS = set()                  # páginas ya dadas por perdidas en esta pasada: no se vuelven a esperar
LIMITE = 20 * 60                # pasados 20 minutos ya no se reintenta nada, para terminar y guardar a tiempo
INICIO = time.monotonic()       # (GitHub corta el robot a los 30 minutos y entonces no se guarda nada)


def descargar(ruta):
    if ruta in VACIAS:
        raise RuntimeError(f"No se pudo leer {ruta} (vacía antes en esta pasada)")
    esperas = ESPERAS if time.monotonic() - INICIO < LIMITE else []
    for intento in range(len(esperas) + 1):
        try:
            with _opener.open(BASE + ruta, timeout=30) as r:
                datos = r.read().decode("iso-8859-15", errors="replace")
            time.sleep(PAUSA)
            if len(datos) > 5000 and "Sarbide datuak" not in datos and "Datos de acceso" not in datos:
                return datos
            # A veces la Federación devuelve una página vacía o pide la cookie otra vez
            print(f"  aviso: respuesta vacía en {ruta}", file=sys.stderr)
        except Exception as e:  # red caída, servidor lento...
            print(f"  aviso: fallo al leer {ruta} ({e})", file=sys.stderr)
        if intento < len(esperas):
            time.sleep(esperas[intento])
    VACIAS.add(ruta)
    raise RuntimeError(f"No se pudo leer {ruta}")


def limpio(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def nombre_bonito(s):
    """ORTUELLA -> Ortuella, ABANTO "B" -> Abanto B"""
    s = s.replace('"', "").strip()
    return " ".join(w if w in ("B", "C", "D") or "." in w else w.capitalize() for w in s.split())


def url_clasificacion(eq, jornada=None):
    if jornada:
        # Para una jornada concreta hay que usar la misma dirección que la propia web de la
        # Federación (codjornada en minúsculas y sin codtemporada); si no, devuelve la última jornada.
        return (f"NFG_VisClasificacion?cod_primaria=1000120&codgrupo={eq['codgrupo']}"
                f"&codcompeticion={eq['codcompeticion']}&codjornada={jornada}")
    return (f"NFG_VisClasificacion?cod_primaria=1000120&codcompeticion={eq['codcompeticion']}"
            f"&codgrupo={eq['codgrupo']}&codtemporada={TEMPORADA}")


def leer_clasificacion(pagina):
    """Primera tabla de la página: posición, equipo y estadísticas (casa + fuera)."""
    filas = []
    for tr in re.findall(r"<tr>(.*?)</tr>", pagina, re.S):
        m = re.search(r"codequipo=(\d+)&codgrupo=\d+\">(.*?)</a>", tr, re.S)
        if not m:
            continue
        celdas = [limpio(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        nums = [c for c in celdas if re.fullmatch(r"-?\d+", c)]
        # nums: posición, puntos, J/G/E/P en casa, J/G/E/P fuera, GF, GC
        if len(nums) < 12:
            continue
        pos, pts, jc, gc_, ec, pc, jf, gf_, ef, pf, gf, gc = map(int, nums[:12])
        codequipo = int(m.group(1))
        if any(f["codequipo"] == codequipo for f in filas):
            break  # la página repite la tabla en versión resumida
        filas.append({"pos": pos, "equipo": nombre_bonito(limpio(m.group(2))), "codequipo": codequipo,
                      "pts": pts, "pj": jc + jf, "g": gc_ + gf_, "e": ec + ef, "p": pc + pf, "gf": gf, "gc": gc})
    return filas


def leer_resultados_jornada(pagina, jornada):
    """Bloque 'Jardunaldia N (fecha)' con los resultados de esa jornada."""
    m = re.search(r"Jardunaldia\s+%d\s*\((\d\d-\d\d-\d{4})\)" % jornada, limpio(pagina))
    if not m:
        return []   # la página trae otra jornada: mejor nada que guardar resultados en la jornada equivocada
    fecha = datetime.strptime(m.group(1), "%d-%m-%Y").date().isoformat()
    partidos = []
    patron = (r"Codigo_Equipo=(\d+)\">(.*?)</a>.*?<b>\s*(\d+)\s*</b>\s*-\s*<b>\s*(\d+)\s*</b>.*?"
              r"CodActa=(\d+).*?Codigo_Equipo=(\d+)\">(.*?)</a>")
    for l_id, l_nom, gl, gv, acta, v_id, v_nom in re.findall(patron, pagina, re.S):
        partidos.append({"jornada": jornada, "fecha": fecha, "local": nombre_bonito(limpio(l_nom)),
                         "visitante": nombre_bonito(limpio(v_nom)), "codlocal": int(l_id), "codvisitante": int(v_id),
                         "gl": int(gl), "gv": int(gv), "acta": int(acta)})
    return partidos


def leer_calendario(pagina):
    """Todas las jornadas con fecha y emparejamientos (sin goles: esos salen de la clasificación)."""
    partidos = []
    for bloque in re.split(r"<th colspan=4>", pagina)[1:]:
        m = re.match(r"\s*Jardunaldia\s+(\d+)\s*<span[^>]*>\((\d\d-\d\d-\d{4})\)", bloque)
        if not m:
            continue
        jornada = int(m.group(1))
        fecha = datetime.strptime(m.group(2), "%d-%m-%Y").date().isoformat()
        bloque = bloque.split("</table>")[0]
        for tr in re.findall(r"<tr>(.*?)</tr>", bloque, re.S):
            equipos = re.findall(r"<td width=\"47%\" align=(?:right|left)>(.*?)</td>", tr, re.S)
            if len(equipos) == 2:
                partidos.append({"jornada": jornada, "fecha": fecha,
                                 "local": nombre_bonito(limpio(equipos[0])), "visitante": nombre_bonito(limpio(equipos[1]))})
    return partidos


def leer_goleadores(pagina, equipo_fed):
    goles = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, re.S):
        c = [limpio(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(c) >= 5 and c[1].replace('"', "").strip().upper() == equipo_fed.upper():
            m = re.match(r"(\d+)", c[4])
            if m:
                apellidos, _, nombre = c[0].partition(",")
                goles.append({"nombre": f"{nombre.strip().title()} {apellidos.strip().title()}".strip(),
                              "partidos": int(c[3]) if c[3].isdigit() else None, "goles": int(m.group(1))})
    return sorted(goles, key=lambda g: -g["goles"])


MINUTO = r"\((\d+)'(?:\s*\+\s*(\d+))?\)"   # (28') o, en el descuento, (45'+2)


def minuto(m):
    """Minuto de un evento del acta; el descuento va aparte para poder ordenar."""
    if not m:
        return {"min": None}
    return {"min": int(m.group(1)), **({"mas": int(m.group(2))} if m.group(2) else {})}


def titulo(s):
    """'OTXARTAGA-BERRI' -> 'Otxartaga-Berri', 'EL MORTUERO' -> 'El Mortuero', 'CAMPO DE LA PAZ' -> 'Campo de la Paz'"""
    menores = {"de", "del", "la", "las", "los", "el", "y"}
    s = re.sub(r"-?\b\d{5}\b", "", s)          # sin código postal ("Balmaseda-48800")
    return " ".join(w.upper() if "." in w else w.lower() if i and w.lower() in menores
                    else "-".join(x.capitalize() for x in w.split("-")) for i, w in enumerate(s.split()))


def nombre_persona(s):
    """'CEA MUÑOZ, MIKEL' -> 'Mikel Cea Muñoz' (con 'de', 'del', 'la'... en minúscula)."""
    apellidos, _, nombre = limpio(s).partition(",")
    menores = {"de", "del", "la", "las", "los", "y", "da", "dos", "van"}
    palabras = f"{nombre.strip()} {apellidos.strip()}".split()
    return " ".join(w.lower() if i and w.lower() in menores else "-".join(x.capitalize() for x in w.split("-"))
                    for i, w in enumerate(palabras))


def leer_porteros(pagina, equipo_fed):
    """Tabla pública de porteros: minutos jugados y goles encajados."""
    porteros = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, re.S):
        c = [limpio(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(c) >= 5 and c[1].replace('"', "").strip().upper() == equipo_fed.upper() and c[3].isdigit() and c[4].isdigit():
            porteros.append({"nombre": nombre_persona(c[0]), "minutos": int(c[3]), "goles": int(c[4])})
    return sorted(porteros, key=lambda g: -g["minutos"])


def _lista_jugadores(tabla):
    return [{"dorsal": int(d) if d.isdigit() else None, "nombre": nombre_persona(n)}
            for d, n in re.findall(r"<tr[^>]*>\s*<td[^>]*>\s*(\d*)\s*</td>\s*<td[^>]*>(.*?)</td>\s*</tr>", tabla, re.S)]


def leer_acta(pagina):
    """Acta de un partido: campo, escudos, alineaciones, goles, tarjetas y cambios.
    El marcador del acta está ofuscado (la Federación pone números falsos); el resultado
    bueno sale de la clasificación. Aquí el lado de cada gol se saca de las alineaciones."""
    acta = {}
    m = re.search(r"Futbol Zelaia:</strong>\s*<a[^>]*Codigo_Campo=(\d+)[^>]*>(.*?)</a>", pagina, re.S)
    ciudad = re.search(r"Hiria:\s*([^<]+)<", pagina)
    if m:
        campo = titulo(limpio(m.group(2)).replace('"', ""))
        ciudad = titulo(limpio(ciudad.group(1))) if ciudad else ""
        acta["campo"] = campo + (", " + ciudad if ciudad and ciudad.lower() not in campo.lower() else "")
        acta["codcampo"] = int(m.group(1))
    acta["escudos"] = [ruta_escudo(x) for x in re.findall(r'<img src="([^"]*/pimg/[^"]*(?:_grande\.png|_Escudo[^"]*))"', pagina)][:2]

    # Cada equipo tiene su bloque: Titularrak (titulares), Ordezkoak (suplentes),
    # Ordezkapenak (cambios) y Txartelak (tarjetas). El primero es el local.
    bloques = pagina.split("<strong>Titularrak</strong>")[1:3]
    if len(bloques) < 2:
        return acta
    alineaciones, cambios, tarjetas, quien = {}, [], [], {}
    for lado, b in zip(("local", "visitante"), bloques):
        b = b.split("dashboard-stat")[0] if lado == "local" else b
        titulares, _, resto = b.partition("<strong>Ordezkoak</strong>")
        suplentes = resto.split("Langile Teknikoak")[0] if resto else ""
        alineaciones[lado] = {"titulares": _lista_jugadores(titulares.split("</table>")[0]),
                              "suplentes": _lista_jugadores(suplentes.split("</table>")[0])}
        for j in alineaciones[lado]["titulares"] + alineaciones[lado]["suplentes"]:
            quien[j["nombre"]] = lado
        cam = b.split("<h4>Ordezkapenak</h4>")[1].split("<h4>")[0] if "<h4>Ordezkapenak</h4>" in b else ""
        for t in re.findall(r"<table[^>]*>(.*?)</table>", cam, re.S):
            filas = re.findall(r"<tr>(.*?)</tr>", t, re.S)
            if len(filas) != 2:
                continue
            entra = limpio(re.findall(r"<td[^>]*>(.*?)</td>", filas[0], re.S)[1])
            sale_td = re.findall(r"<td[^>]*>(.*?)</td>", filas[1], re.S)[1]
            mm = re.search(MINUTO, sale_td)
            cambios.append({**minuto(mm), "lado": lado,
                            "sale": nombre_persona(re.sub(MINUTO, "", sale_td)), "entra": nombre_persona(entra)})
        tar = b.split("<h4>Txartelak</h4>")[1].split("</table>")[0] if "<h4>Txartelak</h4>" in b else ""
        for img, texto in re.findall(r"<img[^>]*src=\"[^\"]*/(tarj_[a-z_]+)\.gif\"[^>]*>.*?<td[^>]*>(.*?)</td>", tar, re.S):
            mm = re.search(MINUTO, texto)
            tipo = "doble" if "dob" in img or "2am" in img else "roja" if "roj" in img else "amarilla"
            nombre = nombre_persona(re.sub(MINUTO, "", texto))
            t = {**minuto(mm), "lado": lado, "jugador": nombre, "tipo": tipo}
            if nombre not in quien:
                t["tecnico"] = True     # tarjeta a un entrenador o delegado: no cuenta como jugador
            tarjetas.append(t)

    goles = []
    seccion = pagina.split(">Golak</div>")[1].split("</table>")[0] if ">Golak</div>" in pagina else ""
    for tr in re.findall(r"<tr>(.*?)</tr>", seccion, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 2:
            continue
        mm = re.search(MINUTO, tds[1])
        jugador = nombre_persona(re.sub(MINUTO, "", tds[1]))
        color = re.search(r"fa-futbol\" style=\"color:\s*([^;\"]+)", tds[0])
        color = color.group(1).strip().lower() if color else ""
        tipo = "pen" if "21, 114" in color or "blue" in color else "pp" if color == "red" else None
        lado = quien.get(jugador)
        if tipo == "pp" and lado:
            lado = "visitante" if lado == "local" else "local"   # en propia puerta cuenta para el otro
        g = {**minuto(mm), "lado": lado, "jugador": jugador}
        if tipo:
            g["tipo"] = tipo
        goles.append(g)
    acta.update({"goles": goles, "tarjetas": tarjetas, "alineaciones": alineaciones, "cambios": cambios})
    return acta


def cargar_anterior():
    try:
        with open(SALIDA, encoding="utf-8") as f:
            texto = f.read()
        return json.loads(texto[texto.index("{"): texto.rindex("}") + 1])
    except Exception:
        return {}


def ruta_escudo(url):
    """De la dirección de un escudo saca (ruta, código). Hay dos formatos en la Federación:
    .../escudosFVF/1055_grande.png (código 1055) y .../Clubes/00100_0010163127_Escudo_3.png (código c10163127)."""
    ruta = re.sub(r"^https?://[^/]+", "", url)
    m = re.search(r"/(\d+)_grande\.png$", ruta)
    if m:
        return ruta, m.group(1)
    m = re.search(r"_0*(\d+)_Escudo", ruta)
    return ruta, "c" + (m.group(1) if m else re.sub(r"\W", "", ruta)[-12:])


def leer_jornada(pagina):
    """Página de una jornada (NFG_CmpJornada): de cada partido, los equipos, sus escudos,
    la fecha y HORA (cuando ya está fijada) y el campo con su código."""
    partidos = []
    for fila in pagina.split('<tr style="background-color: #ffffff00;">')[1:]:
        fila = re.sub(r"<style>.*?</style>", "", fila, flags=re.S)
        nombres = [n for n in (limpio(x) for x in re.findall(r"<h4>(.*?)</h4>", fila, re.S)) if n]
        if len(nombres) < 2:
            continue
        escudos = [ruta_escudo(x) for x in re.findall(r'<img src="([^"]+)"[^>]*class=escudo_widget', fila)]
        horario = " ".join(limpio(x) for x in re.findall(r"<span class=horario[^>]*>(.*?)</span>", fila, re.S))
        cuando = re.search(r"(\d\d-\d\d-\d{4})(?:\s+(\d\d:\d\d))?", horario)
        campo = re.search(r'href="[^"]*(NFG_VisCampos\?[^"]*Codigo_Campo=(\d+))">(.*?)</a>', fila, re.S)
        partidos.append({"local": nombre_bonito(nombres[0]), "visitante": nombre_bonito(nombres[1]),
                         "escudos": escudos,
                         "fecha": datetime.strptime(cuando.group(1), "%d-%m-%Y").date().isoformat() if cuando else None,
                         "hora": cuando.group(2) if cuando and cuando.group(2) not in (None, "00:00") else None,
                         "codcampo": html.unescape(campo.group(1)) if campo else None,   # dirección de la ficha del campo
                         "nombre_campo": limpio(campo.group(3)) if campo else ""})
    return partidos


def leer_campo(codigo, comun, nombre_esperado=""):
    """Ficha de un campo (una sola vez por campo): nombre con su pueblo y coordenadas exactas para el mapa.
    'codigo' es el número del campo o la dirección completa de su ficha tal como viene en la Federación."""
    ruta = codigo if str(codigo).startswith("NFG_") else f"NFG_VisCampos?cod_primaria=1000122&Codigo_Campo={codigo}"
    clave = ruta.split("Codigo_Campo=")[-1] + ("" if "1000122" in ruta else "@" + ruta)
    if clave in comun["fichas_campo"]:
        return comun["fichas_campo"][clave]
    pagina = descargar(ruta)
    nombre = re.search(r"<h4 class=la_roja_regular_titulo1>(.*?)</h4>", pagina, re.S)
    pueblo = re.search(r"<b>Herria:</b>\s*([^<]+)<", pagina)
    loc = re.search(r"q=loc:(-?\d+\.\d+)\+(-?\d+\.\d+)", pagina)
    nombre = titulo(limpio(nombre.group(1)).replace('"', "")) if nombre else ""
    pueblo = titulo(limpio(pueblo.group(1))) if pueblo else ""
    # Comprobación: la ficha tiene que ser del mismo campo que dice la jornada; si no, no se usa
    comparar = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    if nombre_esperado and comparar(titulo(nombre_esperado))[:6] not in comparar(nombre):
        print(f"  aviso: la ficha del campo {clave} ({nombre}) no coincide con «{nombre_esperado}»; no se usa", file=sys.stderr)
        return {"nombre": titulo(nombre_esperado)}
    if loc and abs(float(loc.group(1))) > 1:      # algunas fichas traen 0,0 o están a medio rellenar
        ficha = {"nombre": nombre + (", " + pueblo if pueblo and pueblo.lower() not in nombre.lower() else ""),
                 "mapa": f"{float(loc.group(1)):.6f},{float(loc.group(2)):.6f}"}
    else:                                         # sin coordenadas no nos fiamos del pueblo: solo el nombre
        ficha = {"nombre": nombre}
    comun["fichas_campo"][clave] = ficha
    return ficha


def escudo_ligero(datos, destino_sin_ext):
    """Los escudos de la Federación llegan a pesar 300 KB; en la web se ven pequeños.
    Si está Pillow, se guardan en WebP de 96 px (unos 4 KB); si no, tal cual en PNG."""
    try:
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(datos)).convert("RGBA")
        img.thumbnail((96, 96))
        img.save(destino_sin_ext + ".webp", "WEBP", quality=88, method=6)
        return ".webp"
    except ImportError:
        ext = ".png" if datos.startswith(b"\x89PNG") else ".jpg"
        with open(destino_sin_ext + ext, "wb") as f:
            f.write(datos)
        return ext


def descargar_escudo(ruta, codigo):
    """Guarda el escudo de un club en img/escudos/ (solo la primera vez)."""
    carpeta = os.path.join(AQUI, "img", "escudos")
    for ext in (".webp", ".png", ".jpg"):
        if os.path.exists(os.path.join(carpeta, f"{codigo}{ext}")):
            return f"{codigo}{ext}"
    try:
        with _opener.open(("https://www.fvf-bff.eus" if ruta.startswith("/") else "") + ruta, timeout=40) as r:
            datos = r.read()
        time.sleep(PAUSA)
    except Exception as e:
        print(f"  aviso: no se pudo bajar el escudo {codigo} ({e})", file=sys.stderr)
        return None
    if not (datos.startswith(b"\x89PNG") or datos.startswith(b"\xff\xd8")):   # PNG o JPG
        return None
    os.makedirs(carpeta, exist_ok=True)
    return f"{codigo}" + escudo_ligero(datos, os.path.join(carpeta, str(codigo)))


def leer_acta_partido(codacta, local, visitante, comun):
    """Lee un acta y apunta, de paso, el campo del equipo local y los escudos de los dos."""
    acta = leer_acta(descargar(f"NFG_CmpPartido?cod_primaria=1000120&CodActa={codacta}"))
    if acta.get("campo"):
        comun["campos"][local] = acta["campo"]
    guardar_escudos(zip((local, visitante), acta.pop("escudos", [])), comun)
    codcampo = acta.pop("codcampo", None)
    if codcampo:
        try:
            ficha = leer_campo(codcampo, comun)
            if ficha.get("mapa") and acta.get("campo"):
                comun["mapas"][acta["campo"]] = ficha["mapa"]
        except RuntimeError:
            pass
    return acta


def guardar_escudos(pares, comun):
    for nombre, (ruta, codigo) in pares:
        if codigo != "1047" and nombre not in comun["escudos"]:   # 1047 = CD Ortuella: ya tenemos el nuestro
            archivo = descargar_escudo(ruta, codigo)
            if archivo:
                comun["escudos"][nombre] = archivo


def actualizar_equipo(eq, anterior, comun):
    print(f"- {eq['nombre']}")
    try:
        clasificacion = leer_clasificacion(descargar(url_clasificacion(eq)))
    except RuntimeError:
        if not eq.get("base"):
            raise
        clasificacion = []   # fútbol base antes de empezar la liga: su clasificación llega siempre vacía
    if not clasificacion and not eq.get("base"):
        raise RuntimeError("clasificación vacía: puede que la Federación haya cambiado su web")
    nuestra = next((f for f in clasificacion if f["codequipo"] == eq["codequipo"]), None)
    nombre_fed = nuestra["equipo"] if nuestra else eq.get("nombre_fed", "Ortuella")
    jugadas = max((f["pj"] for f in clasificacion), default=0)

    calendario = leer_calendario(descargar(
        f"NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada={TEMPORADA}"
        f"&codcompeticion={eq['codcompeticion']}&codgrupo={eq['codgrupo']}"))

    # Resultados: reutilizamos los que ya teníamos y solo pedimos las jornadas nuevas
    resultados = {(r["jornada"], r["local"], r["visitante"]): r
                  for r in anterior.get("resultados", []) if r.get("gl") is not None}
    ya = {r["jornada"] for r in resultados.values()}
    for j in range(1, jugadas + 1):
        if j in ya and j < jugadas:   # la última jornada se vuelve a mirar por si hay correcciones
            continue
        for r in leer_resultados_jornada(descargar(url_clasificacion(eq, j)), j):
            resultados[(r["jornada"], r["local"], r["visitante"])] = r

    nuestros = lambda p: nombre_fed in (p["local"], p["visitante"])
    partidos = []
    for p in calendario:
        if not nuestros(p):
            continue
        r = resultados.get((p["jornada"], p["local"], p["visitante"]))
        partidos.append({**p, "gl": r["gl"] if r else None, "gv": r["gv"] if r else None,
                         "acta": r["acta"] if r else None})

    # Actas de nuestros partidos jugados (solo las que aún no tenemos)
    for p in partidos:
        clave = str(p["acta"]) if p["acta"] else None
        if not clave or clave in comun["actas"]:
            continue
        try:
            acta = leer_acta_partido(p["acta"], p["local"], p["visitante"], comun)
        except RuntimeError as e:
            print(f"  aviso: acta {clave} sin leer ({e})", file=sys.stderr)
            continue
        cuenta = lambda lado: sum(1 for g in acta.get("goles", []) if g["lado"] == lado)
        if (cuenta("local"), cuenta("visitante")) != (p["gl"], p["gv"]):
            print(f"  aviso: los goles del acta {clave} no cuadran con el resultado; no se ponen", file=sys.stderr)
            acta["goles"] = []
        comun["actas"][clave] = acta

    # Campo de cada partido fuera: en los ya jugados, el del acta de ese mismo partido; en los
    # próximos, el de la página de la jornada (abajo). No se supone el campo "de siempre" del rival:
    # algunos equipos juegan en campos distintos según la jornada.
    for p in partidos:
        a = comun["actas"].get(str(p["acta"])) if p["acta"] else None
        if p["local"] != nombre_fed and a and a.get("campo"):
            p["campo"] = a["campo"]

    # Próximas 3 jornadas: la página de la jornada trae la hora (cuando ya está fijada), el campo
    # exacto y los escudos de todos los equipos del grupo. Así faltan pocos escudos tras un par de semanas.
    hoy = datetime.now(timezone.utc).date().isoformat()
    proximas = [p for p in partidos if p["fecha"] >= hoy][:3]
    for p in proximas:
        try:
            jornada = leer_jornada(descargar(
                f"NFG_CmpJornada?cod_primaria=1000120&CodCompeticion={eq['codcompeticion']}"
                f"&CodGrupo={eq['codgrupo']}&CodTemporada={TEMPORADA}&CodJornada={p['jornada']}"))
        except RuntimeError as e:
            print(f"  aviso: jornada {p['jornada']} sin leer ({e})", file=sys.stderr)
            continue
        for x in jornada:
            guardar_escudos(zip((x["local"], x["visitante"]), x["escudos"]), comun)
            if (x["local"], x["visitante"]) != (p["local"], p["visitante"]):
                continue
            if x["hora"]:
                p["hora"] = x["hora"]
            if x["fecha"]:
                p["fecha"] = x["fecha"]       # por si la Federación cambia el día
            if x["codcampo"]:
                try:
                    ficha = leer_campo(x["codcampo"], comun, x["nombre_campo"])
                except RuntimeError:
                    ficha = {"nombre": titulo(x["nombre_campo"])}
                if p["local"] != nombre_fed and ficha.get("nombre"):
                    p["campo"] = ficha["nombre"]
                if ficha.get("mapa"):
                    comun["mapas"][p.get("campo") or ficha["nombre"]] = ficha["mapa"]

    try:
        porteros = leer_porteros(descargar(
            f"NFG_CMP_Porteros?cod_primaria=1000120&codcompeticion={eq['codcompeticion']}"
            f"&codtemporada={TEMPORADA}&codgrupo={eq['codgrupo']}"), nombre_fed.upper())
    except RuntimeError:
        porteros = anterior.get("porteros", [])

    try:
        goleadores = leer_goleadores(descargar(
            f"NFG_CMP_Goleadores?cod_primaria=1000120&codcompeticion={eq['codcompeticion']}"
            f"&codtemporada={TEMPORADA}&codgrupo={eq['codgrupo']}"), nombre_fed.upper())
    except RuntimeError:
        if not eq.get("base"):
            raise
        goleadores = anterior.get("goleadores", [])   # en el fútbol base la tabla llega vacía hasta que hay goles

    # En la web se ve "Ortuella" aunque la Federación lo llame, por ejemplo, "Ortuella2013-14".
    # Los resultados internos se guardan con el nombre de la Federación, que es con el que se buscan.
    if eq.get("nombre_web"):
        web = lambda n: eq["nombre_web"] if n == nombre_fed else n
        partidos = [{**p, "local": web(p["local"]), "visitante": web(p["visitante"])} for p in partidos]
        clasificacion = [{**f, "equipo": web(f["equipo"])} for f in clasificacion]
        nombre_fed = eq["nombre_web"]

    return {
        "id": eq["id"], "nombre": eq["nombre"], "categoria": eq["categoria"], "nombreFederacion": nombre_fed,
        **({"base": True} if eq.get("base") else {}),
        "clasificacion": [{k: v for k, v in f.items() if k != "codequipo"} for f in clasificacion],
        "partidos": partidos,
        "goleadores": goleadores,
        "porteros": porteros,
        "resultados": list(resultados.values()),   # copia interna, para no volver a pedirlos
        "enlace": "https://www.fvf-bff.eus/pnfg/NPcd/" + url_clasificacion(eq),
    }


def main():
    # Antes se hacía aquí una "primera visita" a NFG_VisClasificacion sin equipo para coger la
    # cookie, pero esa página siempre llega vacía y paraba todo. La cookie se coge en la primera
    # página de verdad.
    anterior = cargar_anterior()
    previos = {e["id"]: e for e in anterior.get("equipos", [])}
    # Datos compartidos por todos los equipos: actas leídas, escudos de los rivales y su campo
    comun = {"actas": anterior.get("actas", {}), "escudos": anterior.get("escudos", {}),
             "campos": anterior.get("campos", {}), "mapas": anterior.get("mapas", {}),
             "fichas_campo": anterior.get("fichas_campo", {})}
    leidos, pendientes = {}, list(EQUIPOS)
    # Si un equipo falla, se vuelve a intentar al final, tras una pausa larga
    for vuelta in range(2):
        if vuelta:
            if time.monotonic() - INICIO > LIMITE:
                break                   # no hay tiempo: se guarda lo leído y se reintenta en la próxima pasada
            print(f"  Reintentando {len(pendientes)} equipo(s) dentro de 2 minutos", file=sys.stderr)
            time.sleep(120)
            VACIAS.clear()              # en la segunda vuelta, cada página tiene una oportunidad más
        fallidos = []
        for eq in pendientes:
            try:
                leidos[eq["id"]] = actualizar_equipo(eq, previos.get(eq["id"], {}), comun)
            except Exception as e:
                fallidos.append((eq, e))
                print(f"  ERROR en {eq['nombre']}: {e}", file=sys.stderr)
        pendientes = [eq for eq, _ in fallidos]
        if not pendientes:
            break
    errores = [f"{eq['nombre']}: {e}" for eq, e in fallidos]
    equipos = []
    for eq in EQUIPOS:                   # mismo orden de siempre
        if eq["id"] in leidos:
            equipos.append(leidos[eq["id"]])
        elif eq["id"] in previos:        # si falla, la web sigue mostrando los últimos datos buenos
            equipos.append(previos[eq["id"]])
    if not equipos:
        sys.exit("No se ha podido leer nada de la Federación. No se cambia nada.")
    datos = {"temporada": TEMPORADA_TEXTO,
             "actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
             "equipos": equipos, "actas": comun["actas"], "escudos": comun["escudos"],
             "campos": comun["campos"], "mapas": comun["mapas"], "fichas_campo": comun["fichas_campo"]}
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("/* Archivo generado automáticamente por actualizar_federacion.py. No editar a mano. */\n")
        f.write("window.FEDERACION = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n")
    print(f"Guardado {SALIDA}")
    generar_calendario.main()           # calendarios .ics para el móvil, con los datos recién guardados
    if errores:
        sys.exit("Algunos equipos no se pudieron actualizar:\n" + "\n".join(errores))


if __name__ == "__main__":
    main()
