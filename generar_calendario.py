#!/usr/bin/env python3
"""
Genera los calendarios de partidos (.ics) a partir de datos-federacion.js,
para que cualquiera pueda suscribirse desde el móvil (iPhone, Google Calendar...).

Crea la carpeta calendario/ con un archivo para todos los equipos (todos.ics)
y uno por equipo (senior-a.ics, senior-b.ics, juvenil.ics, cadete.ics).

Uso:  python3 generar_calendario.py
Se ejecuta solo después de actualizar_federacion.py. Solo usa la biblioteca estándar.
"""
import json
import os
import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "calendario")
APODO = {"primer": "Senior A", "b": "Senior B", "juvenil": "Juvenil", "cadete": "Cadete", "infantil": "Infantil", "alevin": "Alevín"}
SLUG = {"primer": "senior-a", "b": "senior-b", "juvenil": "juvenil", "cadete": "cadete", "infantil": "infantil", "alevin": "alevin"}
CAMPO = "Otxartaga Berri, Avenida de la Estación s/n, 48530 Ortuella (Bizkaia)"


def sitio():
    # La dirección pública está en generar_paginas.py, para cambiarla en un solo sitio
    texto = open(os.path.join(AQUI, "generar_paginas.py"), encoding="utf-8").read()
    return re.search(r'^SITIO = "([^"]+)"', texto, re.M).group(1)


def leer_datos():
    texto = open(os.path.join(AQUI, "datos-federacion.js"), encoding="utf-8").read()
    return json.loads(texto[texto.index("{"):texto.rindex("}") + 1])


def es_nuestro(nombre, equipo):
    return nombre.strip().lower() == equipo["nombreFederacion"].strip().lower()


def texto_ics(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def plegar(linea):
    # Las líneas de un .ics no pueden pasar de 75 bytes: se parten y se sigue con un espacio
    b = linea.encode("utf-8")
    if len(b) <= 75:
        return linea
    trozos, actual = [], b""
    for ch in linea:
        c = ch.encode("utf-8")
        if len(actual) + len(c) > (75 if not trozos else 74):
            trozos.append(actual.decode("utf-8"))
            actual = b""
        actual += c
    trozos.append(actual.decode("utf-8"))
    return "\r\n ".join(trozos)


def horario(dia, hora):
    """Con hora: evento de 2 horas (en hora UTC, que todos los calendarios entienden). Sin hora: día entero."""
    if not hora:
        return [f"DTSTART;VALUE=DATE:{dia:%Y%m%d}", f"DTEND;VALUE=DATE:{dia + timedelta(days=1):%Y%m%d}"]
    inicio = datetime.combine(dia, time.fromisoformat(hora), ZoneInfo("Europe/Madrid")).astimezone(timezone.utc)
    return [f"DTSTART:{inicio:%Y%m%dT%H%M%SZ}", f"DTEND:{inicio + timedelta(hours=2):%Y%m%dT%H%M%SZ}"]


def evento(equipo, p, sello, web):
    dia = date.fromisoformat(p["fecha"])
    en_casa = es_nuestro(p["local"], equipo)
    if p.get("gl") is not None:
        titulo = f"{p['local']} {p['gl']}-{p['gv']} {p['visitante']}"
    else:
        titulo = f"{p['local']} – {p['visitante']}"
    cual = "Amistoso" if p.get("amistoso") else f"Jornada {p['jornada']}"
    detalle = (f"{APODO[equipo['id']]} · {cual} · {equipo['categoria']}\n"
               f"{'En casa' if en_casa else 'Fuera'}. {'Hora: ' + p['hora'] if p.get('hora') else 'Hora por confirmar'}.\n"
               f"Más información: {web}/partidos.html")
    lineas = [
        "BEGIN:VEVENT",
        f"UID:cdortuella-{equipo['id']}-{'a-' + p['id'] if p.get('amistoso') else 'j' + str(p['jornada'])}@cdortuella",
        f"DTSTAMP:{sello}",
        *horario(dia, p.get("hora")),
        f"SUMMARY:{texto_ics('⚽ ' + APODO[equipo['id']] + ': ' + titulo)}",
        f"DESCRIPTION:{texto_ics(detalle)}",
        "TRANSP:TRANSPARENT",
    ]
    if en_casa:
        lineas.append(f"LOCATION:{texto_ics(CAMPO)}")
    elif p.get("campo"):
        lineas.append(f"LOCATION:{texto_ics(p['campo'])}")
    lineas.append("END:VEVENT")
    return lineas


def calendario(nombre, equipos, sello, web):
    lineas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CD Ortuella//Partidos//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{texto_ics(nombre)}",
        "X-WR-TIMEZONE:Europe/Madrid",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for eq in equipos:
        for p in eq["partidos"]:
            if p.get("fecha"):
                lineas += evento(eq, p, sello, web)
    lineas.append("END:VCALENDAR")
    return "\r\n".join(plegar(l) for l in lineas) + "\r\n"


def main():
    from amistosos import con_amistosos   # los amistosos apuntados por Telegram también van al calendario
    datos = con_amistosos(leer_datos())
    web = sitio()
    # Sello fijo (la hora de la última actualización), para que el archivo solo cambie si cambian los datos
    sello = re.sub(r"[-:]", "", datos["actualizado"][:16]) + "00Z"
    os.makedirs(CARPETA, exist_ok=True)
    archivos = {"todos.ics": ("CD Ortuella · Partidos", datos["equipos"])}
    for eq in datos["equipos"]:
        archivos[SLUG[eq["id"]] + ".ics"] = ("CD Ortuella · " + APODO[eq["id"]], [eq])
    for archivo, (nombre, equipos) in archivos.items():
        with open(os.path.join(CARPETA, archivo), "w", encoding="utf-8", newline="") as f:
            f.write(calendario(nombre, equipos, sello, web))
        print("ok calendario/" + archivo)


if __name__ == "__main__":
    main()
