#!/usr/bin/env python3
"""
Amistosos: partidos que la Federación no publica (pretemporada, fin de liga, torneos…) y que la directiva
apunta con el bot de Telegram (/amistoso, /resultado, /borrar amistoso). n8n lanza el robot «Amistoso» de
GitHub, que llama a este programa y luego rehace las imágenes y el calendario.

Se guardan en datos-amistosos.js (la web los junta con los de la Federación). Salen en ORDUTEGIA, MATCH DAY,
EMAITZAK, la web y el calendario del móvil como cualquier partido, pero no cuentan para la clasificación.

Uso:  python3 amistosos.py anadir --equipo infantil --fecha 2026-10-24 --hora 10:30 --rival Escolapios [--fuera] [--campo "…"]
      python3 amistosos.py resultado --id <id> --gl 3 --gv 1      (goles del local y del visitante)
      python3 amistosos.py borrar --id <id>
"""
import argparse
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(AQUI, "datos-amistosos.js")
CABECERA = "/* Archivo generado automáticamente por amistosos.py (partidos amistosos apuntados por Telegram). No editar a mano. */\n"
EQUIPOS = ["primer", "b", "juvenil", "cadete", "infantil", "alevin"]
NOMBRES = {"primer": "CD Ortuella", "b": "CD Ortuella B", "juvenil": "Juvenil", "cadete": "Cadete",
           "infantil": "Infantil", "alevin": "Alevín"}


def leer():
    try:
        texto = open(ARCHIVO, encoding="utf-8").read()
        return json.loads(texto[texto.index("["):texto.rindex("]") + 1])
    except (OSError, ValueError):
        return []


def guardar(lista):
    lista.sort(key=lambda a: (a["fecha"], a.get("hora") or ""))
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(CABECERA + "window.AMISTOSOS = " + json.dumps(lista, ensure_ascii=False, indent=1) + ";\n")


def como_partido(a, nuestro):
    """El amistoso con la misma forma que un partido de la Federación (local, visitante, goles…)."""
    return {"jornada": None, "amistoso": True, "id": a["id"], "fecha": a["fecha"], "hora": a.get("hora"),
            "local": nuestro if a["casa"] else a["rival"], "visitante": a["rival"] if a["casa"] else nuestro,
            "campo": None if a["casa"] else (a.get("campo") or None), "gl": a.get("gl"), "gv": a.get("gv"), "acta": None}


def con_amistosos(datos):
    """Añade los amistosos a los partidos de cada equipo (y crea el equipo si la Federación aún no lo tiene,
    como el alevín antes de empezar su liga). No cambia el archivo de la Federación."""
    amistosos = leer()
    if not amistosos:
        return datos
    equipos = {e["id"]: e for e in datos["equipos"]}
    for a in amistosos:
        eq = equipos.get(a["equipo"])
        if not eq:
            eq = equipos[a["equipo"]] = {"id": a["equipo"], "nombre": NOMBRES.get(a["equipo"], a["equipo"]), "base": True,
                                         "categoria": "Amistosos", "nombreFederacion": "Ortuella", "partidos": [],
                                         "clasificacion": [], "goleadores": [], "porteros": [], "resultados": []}
            datos["equipos"].append(eq)
        eq["partidos"] = eq["partidos"] + [como_partido(a, eq["nombreFederacion"])]
    for eq in datos["equipos"]:
        eq["partidos"].sort(key=lambda p: p["fecha"])
    return datos


def main():
    o = argparse.ArgumentParser()
    o.add_argument("accion", choices=["anadir", "resultado", "borrar"])
    for campo in ("equipo", "fecha", "hora", "rival", "campo", "id"):
        o.add_argument("--" + campo, default="")
    o.add_argument("--fuera", action="store_true")
    o.add_argument("--gl", type=int)
    o.add_argument("--gv", type=int)
    a = o.parse_args()
    lista = leer()

    if a.accion == "anadir":
        if a.equipo not in EQUIPOS or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.fecha) or not a.rival.strip():
            sys.exit("Faltan datos: equipo, fecha (AAAA-MM-DD) y rival")
        rival = " ".join(a.rival.split())
        ident = f"{a.fecha}-{a.equipo}-" + re.sub(r"[^a-z0-9]+", "-", rival.lower()).strip("-")
        if any(x["id"] == ident for x in lista):
            print(f"Ya estaba apuntado: {ident}")
            return
        nuevo = {"id": ident, "equipo": a.equipo, "fecha": a.fecha, "hora": a.hora or None, "rival": rival,
                 "casa": not a.fuera, "campo": a.campo.strip() or None, "gl": None, "gv": None}
        lista.append(nuevo)
        print("Apuntado:", json.dumps(nuevo, ensure_ascii=False))
    else:
        x = next((x for x in lista if x["id"] == a.id), None)
        if not x:
            sys.exit(f"No hay ningún amistoso con id {a.id}")
        if a.accion == "borrar":
            lista.remove(x)
            print("Borrado:", a.id)
        else:
            if a.gl is None or a.gv is None:
                sys.exit("Faltan los goles (--gl y --gv)")
            x["gl"], x["gv"] = a.gl, a.gv
            print(f"Resultado: {a.id} {a.gl}-{a.gv}")
    guardar(lista)


if __name__ == "__main__":
    main()
