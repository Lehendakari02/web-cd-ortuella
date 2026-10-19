#!/usr/bin/env python3
"""
Actualiza los datos de la web del CD Ortuella con la información pública de la
Federación Vizcaína de Fútbol (www.fvf-bff.eus).

Genera el archivo datos-federacion.js con, para cada equipo:
clasificación, calendario, resultados y goleadores del club.

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
]

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "datos-federacion.js")

_cookies = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
_opener = urllib.request.build_opener(_cookies)
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (compatible; CDOrtuellaWeb/1.0; web del CD Ortuella)"),
                      ("Accept-Language", "es-ES,es;q=0.9")]


def descargar(ruta):
    for intento in range(4):
        try:
            with _opener.open(BASE + ruta, timeout=40) as r:
                datos = r.read().decode("iso-8859-15", errors="replace")
            time.sleep(PAUSA)
            if len(datos) > 5000 and "Sarbide datuak" not in datos and "Datos de acceso" not in datos:
                return datos
            # A veces la Federación devuelve una página vacía o pide la cookie otra vez
            print(f"  aviso: respuesta vacía en {ruta}, reintento", file=sys.stderr)
            time.sleep(3 * (intento + 1))
        except Exception as e:  # red caída, servidor lento...
            print(f"  aviso: fallo al leer {ruta} ({e}), reintento", file=sys.stderr)
            time.sleep(5 * (intento + 1))
    raise RuntimeError(f"No se pudo leer {ruta}")


def limpio(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def nombre_bonito(s):
    """ORTUELLA -> Ortuella, ABANTO "B" -> Abanto B"""
    s = s.replace('"', "").strip()
    return " ".join(w if w in ("B", "C", "D") or "." in w else w.capitalize() for w in s.split())


def url_clasificacion(eq, jornada=None):
    u = (f"NFG_VisClasificacion?cod_primaria=1000120&codcompeticion={eq['codcompeticion']}"
         f"&codgrupo={eq['codgrupo']}&codtemporada={TEMPORADA}")
    return u + (f"&CodJornada={jornada}" if jornada else "")


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
    fecha = datetime.strptime(m.group(1), "%d-%m-%Y").date().isoformat() if m else None
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


def cargar_anterior():
    try:
        with open(SALIDA, encoding="utf-8") as f:
            texto = f.read()
        return json.loads(texto[texto.index("{"): texto.rindex("}") + 1])
    except Exception:
        return {}


def actualizar_equipo(eq, anterior):
    print(f"- {eq['nombre']}")
    pagina = descargar(url_clasificacion(eq))
    clasificacion = leer_clasificacion(pagina)
    if not clasificacion:
        raise RuntimeError("clasificación vacía: puede que la Federación haya cambiado su web")
    nuestra = next((f for f in clasificacion if f["codequipo"] == eq["codequipo"]), None)
    nombre_fed = nuestra["equipo"] if nuestra else "Ortuella"
    jugadas = max(f["pj"] for f in clasificacion)

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

    goleadores = leer_goleadores(descargar(
        f"NFG_CMP_Goleadores?cod_primaria=1000120&codcompeticion={eq['codcompeticion']}"
        f"&codtemporada={TEMPORADA}&codgrupo={eq['codgrupo']}"), nombre_fed.upper())

    return {
        "id": eq["id"], "nombre": eq["nombre"], "categoria": eq["categoria"], "nombreFederacion": nombre_fed,
        "clasificacion": [{k: v for k, v in f.items() if k != "codequipo"} for f in clasificacion],
        "partidos": partidos,
        "goleadores": goleadores,
        "resultados": list(resultados.values()),   # copia interna, para no volver a pedirlos
        "enlace": "https://www.fvf-bff.eus/pnfg/NPcd/" + url_clasificacion(eq),
    }


def main():
    descargar("NFG_VisClasificacion?cod_primaria=1000120")  # primera visita: la Federación pone su cookie
    anterior = cargar_anterior()
    previos = {e["id"]: e for e in anterior.get("equipos", [])}
    equipos, errores = [], []
    for eq in EQUIPOS:
        try:
            equipos.append(actualizar_equipo(eq, previos.get(eq["id"], {})))
        except Exception as e:
            errores.append(f"{eq['nombre']}: {e}")
            print(f"  ERROR: {e}", file=sys.stderr)
            if eq["id"] in previos:      # si falla, la web sigue mostrando los últimos datos buenos
                equipos.append(previos[eq["id"]])
    if not equipos:
        sys.exit("No se ha podido leer nada de la Federación. No se cambia nada.")
    datos = {"temporada": TEMPORADA_TEXTO,
             "actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
             "equipos": equipos}
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("/* Archivo generado automáticamente por actualizar_federacion.py. No editar a mano. */\n")
        f.write("window.FEDERACION = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n")
    print(f"Guardado {SALIDA}")
    if errores:
        sys.exit("Algunos equipos no se pudieron actualizar:\n" + "\n".join(errores))


if __name__ == "__main__":
    main()
