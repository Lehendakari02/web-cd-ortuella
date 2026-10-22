#!/usr/bin/env python3
"""
Genera las publicaciones de Instagram del club (post e historia) a partir de datos-federacion.js:

  ORDUTEGIA  horarios del próximo fin de semana
  EMAITZAK   resultados del último fin de semana
  MATCH DAY  partido del próximo fin de semana de cada equipo de config.json (Senior A y B)

Deja en redes/salida/ las imágenes (JPG, que es lo que acepta Instagram) y ultimo.json con la
dirección pública de cada imagen, para que n8n las publique (el texto del pie lo escribe una persona por Telegram).
Sin IA y sin coste: las imágenes se dibujan con plantillas HTML y un navegador sin ventana.

Uso:  python3 redes/generar_redes.py [--fecha AAAA-MM-DD]
      --fecha: hacer como si hoy fuera ese día (para probar). Por defecto, hoy.
Necesita:  pip install playwright && playwright install chromium   (y Pillow para los escudos)
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

REDES = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(REDES)
SALIDA = os.path.join(REDES, "salida")
ESCUDOS_GRANDES = os.path.join(REDES, "escudos")
TAMANOS = {"post": (1080, 1350), "historia": (1080, 1920)}
DIAS = ["ASTELEHENA", "ASTEARTEA", "ASTEAZKENA", "OSTEGUNA", "OSTIRALA", "LARUNBATA", "IGANDEA"]
ESCUDO_FED = "https://www.fvf-bff.eus/pnfg/pimg/MigracionPV/escudosFVF/{}_grande.png"


# ---------------------------------------------------------------- datos

def leer_datos():
    texto = open(os.path.join(RAIZ, "datos-federacion.js"), encoding="utf-8").read()
    return json.loads(texto[texto.index("{"):texto.rindex("}") + 1])


def leer_config():
    return json.load(open(os.path.join(REDES, "config.json"), encoding="utf-8"))


def sitio():
    # La dirección pública está en generar_paginas.py, para cambiarla en un solo sitio
    texto = open(os.path.join(RAIZ, "generar_paginas.py"), encoding="utf-8").read()
    return re.search(r'^SITIO = "([^"]+)"', texto, re.M).group(1)


def semana(dia):
    """Lunes y domingo de la semana de ese día."""
    lunes = dia - timedelta(days=dia.weekday())
    return lunes, lunes + timedelta(days=6)


def partidos_de_semana(equipo, lunes, domingo):
    return [p for p in equipo["partidos"] if lunes <= date.fromisoformat(p["fecha"]) <= domingo]


def en_casa(p, equipo):
    return p["local"].strip().lower() == equipo["nombreFederacion"].strip().lower()


def rival(p, equipo):
    return p["visitante"] if en_casa(p, equipo) else p["local"]


def corto(nombre, config):
    return config["nombres_cortos"].get(nombre, nombre.upper())


def campo_corto(campo, config):
    if campo in config["campos_cortos"]:
        return config["campos_cortos"][campo]
    return campo.split(",")[0].replace("-", " ").strip().upper()


# ---------------------------------------------------------------- recursos

def uri(ruta):
    return "file://" + os.path.abspath(ruta)


def sin_fondo_blanco(img):
    """Muchos escudos llegan sobre un cuadrado blanco: se vuelve transparente el blanco que toca los bordes."""
    from PIL import ImageDraw
    img = img.convert("RGBA")
    ancho, alto = img.size
    for esquina in ((0, 0), (ancho - 1, 0), (0, alto - 1), (ancho - 1, alto - 1)):
        r, g, b, a = img.getpixel(esquina)
        if a > 0 and min(r, g, b) > 225:
            ImageDraw.floodfill(img, esquina, (255, 255, 255, 0), thresh=40)
    return img


def escudo_rival(nombre, datos):
    """Escudo en la mejor calidad posible: primero redes/escudos/<nombre>.png (puesto a mano); si no,
    el "grande" de la Federación o el de la web, sin fondo blanco. Se guarda en redes/escudos/ la primera vez."""
    for ext in (".png", ".webp", ".jpg"):
        a_mano = os.path.join(ESCUDOS_GRANDES, nombre + ext)
        if os.path.exists(a_mano):
            return a_mano
    pequeno = datos["escudos"].get(nombre)
    if not pequeno:
        return None
    codigo = os.path.splitext(pequeno)[0]
    listo = os.path.join(ESCUDOS_GRANDES, codigo + ".png")
    if os.path.exists(listo):
        return listo
    from PIL import Image
    img = Image.open(os.path.join(RAIZ, "img", "escudos", pequeno))
    if codigo.isdigit():
        try:
            from io import BytesIO
            pet = urllib.request.Request(ESCUDO_FED.format(codigo), headers={"User-Agent": "Mozilla/5.0 (compatible; CDOrtuellaWeb/1.0)"})
            with urllib.request.urlopen(pet, timeout=40) as r:
                grande = Image.open(BytesIO(r.read()))
            if max(grande.size) > max(img.size):
                img = grande
        except Exception as e:
            print(f"  aviso: no se pudo bajar el escudo grande de {nombre} ({e})", file=sys.stderr)
    img = sin_fondo_blanco(img)
    img.thumbnail((500, 500))
    os.makedirs(ESCUDOS_GRANDES, exist_ok=True)
    img.save(listo, optimize=True)
    return listo


def escudo_ortuella():
    for ext in (".png", ".webp"):
        ruta = os.path.join(ESCUDOS_GRANDES, "Ortuella" + ext)
        if os.path.exists(ruta):
            return ruta
    return os.path.join(RAIZ, "img", "escudo.webp")


# ---------------------------------------------------------------- plantillas

# Los textos que no caben (rivales con nombre largo) se hacen más pequeños hasta que caben
AJUSTAR = """document.fonts.ready.then(() => document.querySelectorAll('.ajustar').forEach(el => {
  let t = parseFloat(getComputedStyle(el).fontSize);
  while (el.scrollWidth > el.clientWidth + 1 && t > 12) el.style.fontSize = (t -= 1) + 'px';
}));"""


def pagina(cuerpo, formato, clase):
    ancho, alto = TAMANOS[formato]
    css = os.path.join(REDES, "plantillas", "estilos.css")
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<link rel="stylesheet" href="{uri(css)}">'
            f'<style>@font-face{{font-family:Montserrat;font-weight:100 900;src:url("{uri(os.path.join(REDES, "recursos", "montserrat.woff2"))}")}}'
            f':root{{--ancho:{ancho}px;--alto:{alto}px}}</style>'
            f'</head><body class="{clase} {formato}">{cuerpo}<script>{AJUSTAR}</script></body></html>')


# Dónde van las filas sobre los lienzos de Canva (preparar_fondos.py), en px desde arriba.
# Son las medidas de las plantillas de Canva; en la historia, desplazadas como el título.
# Las filas se reparten por toda la zona entre el título y los patrocinadores (más separadas si hay pocas).
ZONA_ORDUTEGIA = {"post": (300, 1045), "historia": (520, 1530)}
ZONA_EMAITZAK = {"post": (308, 1000), "historia": (534, 1560)}
ALTO_FILA = {"ordutegia": 66, "emaitzak": 86}
PASO_MAXIMO = {"ordutegia": 125, "emaitzak": 200}


def escala_emaitzak(n):
    """Con pocos resultados, las filas se hacen más grandes para que la imagen no quede vacía
    (1,22 es lo máximo para que la cinta no se salga por los lados)."""
    return {1: 1.22, 2: 1.2, 3: 1.14}.get(n, 1.08)


def repartir(pieza, formato, n):
    """Posición (px desde arriba) de cada fila: repartidas por la zona y centradas."""
    desde, hasta = (ZONA_ORDUTEGIA if pieza == "ordutegia" else ZONA_EMAITZAK)[formato]
    alto = ALTO_FILA[pieza] * (escala_emaitzak(n) / 1.08 if pieza == "emaitzak" else 1)
    paso = min(PASO_MAXIMO[pieza], (hasta - desde - alto) / max(n - 1, 1))
    primera = desde + (hasta - desde - alto - paso * (n - 1)) / 2
    return [round(primera + paso * i) for i in range(n)]


def fondo_de_la_semana(lista, lunes, desfase=0):
    """Elige de la lista el fondo que toca esta semana (van rotando). Cada fondo puede ser solo la ruta
    de la foto o {"foto": ..., "velo": false, "diseno": 0}."""
    elegido = lista[(lunes.isocalendar()[1] + desfase) % len(lista)]
    return elegido if isinstance(elegido, dict) else {"foto": elegido}


def lienzo(pieza, formato, fondo):
    """Fondo de Canva tal cual, o una foto ampliada, muy difuminada y con velo azul marino
    con el título y los patrocinadores de Canva encima. Siempre la misma receta: no se elige nada."""
    plantillas = os.path.join(REDES, "plantillas")
    if fondo["foto"] == "canva":
        return f'<img class="lienzo" src="{uri(os.path.join(plantillas, f"fondo-{pieza}-{formato}.png"))}">'
    return (f'<div class="fondo difuminado" style="background-image:url(\'{uri(os.path.join(RAIZ, fondo["foto"]))}\')"></div>'
            f'<img class="lienzo" src="{uri(os.path.join(plantillas, f"capa-{pieza}-{formato}.png"))}">')


def icono(nombre):
    return f'<img class="icono" src="{uri(os.path.join(REDES, "recursos", nombre + ".png"))}">'


def html_ordutegia(filas, config, formato, fondo):
    lineas = ""
    posiciones = repartir("ordutegia", formato, len(filas))
    for i, (cat, p, equipo) in enumerate(filas):
        if p:
            hora = f" {p['hora']}" if p.get("hora") else ""
            dato = f'<span class="texto ajustar">{html.escape(corto(rival(p, equipo), config))} {date.fromisoformat(p["fecha"]):%d/%m}{hora}</span>'
            dato += icono("casa" if en_casa(p, equipo) else "avion")
        else:
            dato = '<span class="texto">—</span>'
        lineas += f'<div class="fila" style="top:{posiciones[i]}px"><div class="cat">{html.escape(cat)}</div><div class="dato">{dato}</div></div>'
    return pagina(lienzo("ordutegia", formato, fondo) + lineas, formato, "ordutegia")


def gol(n, lado):
    return f'<span class="gol {lado}{" dos" if n > 9 else ""}">{n}</span>'


def html_emaitzak(filas, config, formato, fondo):
    posiciones = repartir("emaitzak", formato, len(filas))
    fila = uri(os.path.join(REDES, "plantillas", "fila-emaitzak.png"))
    lineas = ""
    for i, (cat, p, equipo) in enumerate(filas):
        nuestro, otro = html.escape(cat), html.escape(corto(rival(p, equipo), config))
        local, visitante = (nuestro, otro) if en_casa(p, equipo) else (otro, nuestro)
        lineas += (f'<div class="partido" style="top:{posiciones[i]}px;transform:scale({escala_emaitzak(len(filas))})"><img src="{fila}">'
                   f'<span class="equipo local ajustar">{local}</span><span class="equipo visitante ajustar">{visitante}</span>'
                   f'{gol(p["gl"], "l")}{gol(p["gv"], "v")}</div>')
    return pagina(lienzo("emaitzak", formato, fondo) + lineas, formato, "emaitzak")


def html_matchday(p, equipo, datos, config, formato, variante, fondo, club):
    variante = fondo.get("diseno", variante)   # algunas fotos van mejor con un diseño concreto
    casa = en_casa(p, equipo)
    otro = rival(p, equipo)
    escudos = [escudo_ortuella(), escudo_rival(otro, datos)]
    if not casa:
        escudos.reverse()
    escudos_html = "".join(f'<img src="{uri(e)}">' for e in escudos if e)
    dia = DIAS[date.fromisoformat(p["fecha"]).weekday()]
    cuando = f"{dia} {p['hora']}" if p.get("hora") else dia
    # En casa, todos nuestros equipos juegan en Otxartaga, aunque la web solo lo apunte para "Ortuella"
    campo = datos["campos"].get(p["local"]) or p.get("campo") or (datos["campos"].get("Ortuella", "") if casa else "")
    campo = campo_corto(campo, config)
    if variante == 0:
        textos = (f'<div class="vertical"><span class="grande">MATCH DAY</span><span class="club">{club}</span></div>'
                  f'<div class="lado"><div class="escudos">{escudos_html}</div>'
                  f'<p class="cuando">{cuando}</p><p class="donde ajustar">{html.escape(campo)}</p></div>')
    else:
        textos = (f'<div class="cabecera"><p class="cuando">{cuando.replace(" ", "<br>", 1)}</p>'
                  f'<p class="club">{club}</p><p class="grande">MATCH DAY</p>'
                  f'<p class="donde ajustar">{html.escape(campo)}</p><div class="escudos">{escudos_html}</div></div>')
    velo = '<div class="velo"></div>' if fondo.get("velo", True) else ""   # las fotos de Canva ya traen el suyo
    cuerpo = (f'<div class="fondo" style="background-image:url(\'{uri(os.path.join(RAIZ, fondo["foto"]))}\')"></div>'
              f'{velo}<main>{textos}</main>')
    return pagina(cuerpo, formato, f"matchday v{variante}")


# ---------------------------------------------------------------- dibujar

class Dibujante:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        # En la nube de Claude hay un Chromium ya instalado; en GitHub Actions se usa el de Playwright
        ruta = os.environ.get("CHROMIUM")
        self._nav = self._pw.chromium.launch(executable_path=ruta) if ruta else self._pw.chromium.launch()

    def jpg(self, codigo_html, formato, destino):
        ancho, alto = TAMANOS[formato]
        temporal = destino + ".html"
        with open(temporal, "w", encoding="utf-8") as f:
            f.write(codigo_html)
        pag = self._nav.new_page(viewport={"width": ancho, "height": alto})
        pag.goto(uri(temporal))
        pag.evaluate("document.fonts.ready")
        pag.wait_for_load_state("networkidle")
        datos = pag.screenshot(type="jpeg", quality=92)
        pag.close()
        os.remove(temporal)
        # Solo se reescribe si cambia, para no llenar el historial de git de imágenes iguales
        if not os.path.exists(destino) or open(destino, "rb").read() != datos:
            with open(destino, "wb") as f:
                f.write(datos)
        return hashlib.sha1(datos).hexdigest()[:10]

    def cerrar(self):
        self._nav.close()
        self._pw.stop()


# ---------------------------------------------------------------- principal

def main():
    opciones = argparse.ArgumentParser()
    opciones.add_argument("--fecha", help="hacer como si hoy fuera este día (AAAA-MM-DD)")
    fecha = opciones.parse_args().fecha
    hoy = date.fromisoformat(fecha) if fecha else datetime.now(ZoneInfo("Europe/Madrid")).date()

    datos, config = leer_datos(), leer_config()
    equipos = {e["id"]: e for e in datos["equipos"]}
    os.makedirs(SALIDA, exist_ok=True)

    # Horarios y match day: la semana de mañana (el domingo ya se piensa en el finde siguiente).
    # Resultados: la semana del último domingo (el lunes todavía se ven los del fin de semana).
    prox_lunes, prox_domingo = semana(hoy + timedelta(days=1))
    ult_lunes, ult_domingo = semana(hoy - timedelta(days=(hoy.weekday() + 1) % 7))

    horarios, resultados = [], []
    for c in config["categorias"]:
        eq = equipos.get(c["id"])
        prox = partidos_de_semana(eq, prox_lunes, prox_domingo) if eq else []
        horarios.append((c["ordutegia"], prox[0] if prox else None, eq))
        if eq:
            for p in partidos_de_semana(eq, ult_lunes, ult_domingo):
                if p.get("gl") is not None:
                    resultados.append((c["emaitzak"], p, eq))

    piezas = {}
    base = sitio() + "/redes/salida/"
    dib = Dibujante()
    try:
        def guardar(tipo, nombre, hacer_html, lunes):
            piezas[tipo] = {"nombre": nombre, "semana": f"{lunes:%Y-%m-%d}"}
            for formato in TAMANOS:
                archivo = f"{tipo}-{formato}.jpg"
                huella = dib.jpg(hacer_html(formato), formato, os.path.join(SALIDA, archivo))
                piezas[tipo][formato] = f"{base}{archivo}?v={huella}"   # ?v= para que Instagram no use una copia vieja

        if any(p for _, p, _ in horarios):
            fondo = fondo_de_la_semana(config["fondos"]["tablas"], prox_lunes)
            guardar("ordutegia", "ORDUTEGIA", lambda f: html_ordutegia(horarios, config, f, fondo), prox_lunes)
        if resultados:
            fondo_r = fondo_de_la_semana(config["fondos"]["tablas"], ult_lunes)
            guardar("emaitzak", "EMAITZAK", lambda f: html_emaitzak(resultados, config, f, fondo_r), ult_lunes)

        # Un MATCH DAY por cada equipo de config["matchday"] que juegue ese fin de semana
        n = prox_lunes.isocalendar()[1]
        for orden, md in enumerate(config["matchday"]):
            eq = equipos.get(md["id"])
            partido = (partidos_de_semana(eq, prox_lunes, prox_domingo) or [None])[0] if eq else None
            if not partido:
                continue
            fondo_m = fondo_de_la_semana(config["fondos"]["matchday"], prox_lunes, orden)   # cada equipo, una foto distinta
            tipo = "matchday" if md["id"] == "primer" else f"matchday-{md['id']}"
            guardar(tipo, f"MATCH DAY {md['club']}",
                    lambda f, partido=partido, eq=eq, fondo_m=fondo_m, md=md, orden=orden:
                        html_matchday(partido, eq, datos, config, f, (n + orden) % 2, fondo_m, md["club"]),
                    prox_lunes)
    finally:
        dib.cerrar()

    resumen = {"datos_actualizados": datos.get("actualizado"), "piezas": piezas}
    with open(os.path.join(SALIDA, "ultimo.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=1)
    for tipo, pieza in piezas.items():
        print(f"{tipo}: {pieza['post']}")
    if not piezas:
        print("Nada que publicar esta semana")


if __name__ == "__main__":
    main()
