#!/usr/bin/env python3
"""
Compara los datos de la Federación de antes y de después de una actualización y apunta los cambios
en los próximos partidos de nuestros equipos, para avisar a la directiva por Telegram (lo hace n8n):

  📅 un partido recibe fecha u hora     ⚠️ cambia el día, la hora o el campo     🆕 aparece un partido nuevo

Solo mira partidos que aún no se han jugado: al jugarse uno, la Federación le quita la hora y le
vuelve a poner la fecha de la jornada, y eso no es un cambio que haya que avisar.

Deja los avisos en redes/salida/cambios.json (los 50 últimos). Cada uno tiene un "id" único para que
n8n no mande dos veces el mismo. Sin IA y sin coste.

Uso:  python3 redes/detectar_cambios.py <datos de antes> <datos de después> [--hoy AAAA-MM-DD]
(los dos archivos son datos-federacion.js; el robot guarda una copia del de antes al empezar)
"""
import argparse
import hashlib
import json
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

from generar_redes import DIAS, SALIDA, campo_corto, en_casa, leer_config

GUARDADOS = 50   # avisos que se conservan en cambios.json


def leer(ruta):
    texto = open(ruta, encoding="utf-8").read()
    return json.loads(texto[texto.index("{"):texto.rindex("}") + 1])


def cuando(p):
    """«LARUNBATA 24/10 16:15», o «sin hora» si aún no la tiene."""
    dia = date.fromisoformat(p["fecha"])
    return f"{DIAS[dia.weekday()]} {dia:%d/%m} {p['hora']}" if p.get("hora") else f"{DIAS[dia.weekday()]} {dia:%d/%m}, sin hora"


def campo(p, equipo, datos, config):
    """En casa, siempre Otxartaga (la web solo lo apunta para «Ortuella»); fuera, el del partido."""
    nombre = p.get("campo") or datos["campos"].get(p["local"]) or ""
    if en_casa(p, equipo):
        nombre = datos["campos"].get("Ortuella", nombre)
    return campo_corto(nombre, config) if nombre else ""


def partidos_futuros(datos, hoy):
    """{(equipo, jornada, local, visitante): (partido, equipo)} de los partidos aún por jugar."""
    futuros = {}
    for eq in datos.get("equipos", []):
        for p in eq["partidos"]:
            if p.get("gl") is None and p["fecha"] >= hoy.isoformat():
                futuros[(eq["id"], p["jornada"], p["local"], p["visitante"])] = (p, eq)
    return futuros


def detectar(antes, despues, config, hoy):
    nombres = {c["id"]: c["emaitzak"] for c in config["categorias"]}
    viejos = partidos_futuros(antes, hoy)
    con_datos_antes = {eq["id"] for eq in antes.get("equipos", []) if eq["partidos"]}
    avisos = []
    for clave, (p, eq) in partidos_futuros(despues, hoy).items():
        partido = f"{nombres.get(eq['id'], eq['nombre'].upper())} · J{p['jornada']}: {p['local']} – {p['visitante']}"
        ahora = f"{cuando(p)} · {campo(p, eq, despues, config)}".rstrip(" ·")
        if clave not in viejos:
            # Un equipo que aún no tenía partidos (p. ej. el alevín al empezar su liga) traería todo el
            # calendario de golpe: eso no son avisos, es el calendario nuevo
            if eq["id"] not in con_datos_antes:
                continue
            avisos.append(("🆕", f"{partido}\nPartido nuevo: {ahora}", clave, ahora))
            continue
        v, _ = viejos[clave]
        antes_txt = f"{cuando(v)} · {campo(v, eq, antes, config)}".rstrip(" ·")
        cambia_dia = v["fecha"] != p["fecha"]
        cambia_hora = v.get("hora") != p.get("hora")
        campo_v, campo_p = campo(v, eq, antes, config), campo(p, eq, despues, config)
        cambia_campo = bool(campo_v and campo_p and campo_v != campo_p)
        if not (cambia_dia or cambia_hora or cambia_campo):
            continue
        if not v.get("hora") and p.get("hora") and not cambia_campo:
            avisos.append(("📅", f"{partido}\nYa tiene hora: {ahora}", clave, ahora))
        elif v.get("hora") and not p.get("hora") and not cambia_dia and not cambia_campo:
            avisos.append(("⚠️", f"{partido}\nLa Federación ha quitado la hora (pendiente de fijar): {ahora}", clave, ahora))
        else:
            avisos.append(("⚠️", f"{partido}\nAntes: {antes_txt}\nAhora: {ahora}", clave, ahora))
    return avisos


def main():
    opciones = argparse.ArgumentParser()
    opciones.add_argument("antes")
    opciones.add_argument("despues")
    opciones.add_argument("--hoy", help="hacer como si hoy fuera este día (AAAA-MM-DD)")
    args = opciones.parse_args()
    hoy = date.fromisoformat(args.hoy) if args.hoy else datetime.now(ZoneInfo("Europe/Madrid")).date()

    try:
        antes = leer(args.antes)
    except (OSError, ValueError):
        print("No hay datos de antes con los que comparar: no se avisa de nada")
        return
    nuevos = detectar(antes, leer(args.despues), leer_config(), hoy)

    archivo = os.path.join(SALIDA, "cambios.json")
    try:
        guardados = json.load(open(archivo, encoding="utf-8"))["avisos"]
    except (OSError, ValueError, KeyError):
        guardados = []
    detectado = datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="minutes")
    for icono, texto, clave, estado in nuevos:
        # El id depende del partido y de cómo queda: el mismo cambio no se avisa dos veces
        ident = hashlib.sha1(json.dumps([clave, estado], ensure_ascii=False).encode()).hexdigest()[:12]
        if not any(a["id"] == ident for a in guardados):
            guardados.append({"id": ident, "detectado": detectado, "texto": f"{icono} {texto}"})
    os.makedirs(SALIDA, exist_ok=True)
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump({"avisos": guardados[-GUARDADOS:]}, f, ensure_ascii=False, indent=1)
    for _, texto, _, _ in nuevos:
        print(texto.replace("\n", " | "))
    print(f"{len(nuevos)} aviso(s) de cambios")


if __name__ == "__main__":
    main()
