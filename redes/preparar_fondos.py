#!/usr/bin/env python3
"""
Prepara, a partir de las exportaciones de Canva (redes/canva/), los lienzos fijos que usa
generar_redes.py. Solo hay que volver a ejecutarlo si se cambia la plantilla en Canva
(por ejemplo, un patrocinador nuevo): exportar en PNG 1080×1350 con el mismo nombre y ejecutar.

  plantillas/fondo-ordutegia-post.png / -historia.png   fondo + título + patrocinadores
  plantillas/fondo-emaitzak-post.png  / -historia.png
  plantillas/fila-emaitzak.png    la cinta de un resultado (LOCAL ⚽ VISITANTE) con transparencia
  escudos/Ortuella.png            nuestro escudo en buena calidad

Las plantillas de Canva traen filas de equipos de otros años; aquí se quitan y se deja el
fondo limpio, porque las filas las dibuja siempre el generador (las que haga falta cada semana).

Uso:  python3 redes/preparar_fondos.py      (necesita Pillow)
"""
import os

from PIL import Image, ImageDraw

REDES = os.path.dirname(os.path.abspath(__file__))
CANVA = os.path.join(REDES, "canva")
PLANTILLAS = os.path.join(REDES, "plantillas")

HORARIOS = os.path.join(CANVA, "Horarios", "3.png")     # el que menos filas tiene: deja mucho fondo limpio
RESULTADOS = os.path.join(CANVA, "Resultados", "1.png")  # la plantilla vacía de resultados
ESCUDO = os.path.join(CANVA, "ESCUDO ORTUELLA COLOR CMYK.png")

FONDO_LIMPIO = (560, 1085)   # franja de Horarios/3.png sin filas ni patrocinadores (y desde, y hasta)
FUNDIDO = 40                 # px de transición suave al pegar unas franjas sobre otras

# Qué franja se copia de cada plantilla (y desde, y hasta) y dónde va en el post y en la historia.
# En la historia se deja aire arriba y abajo, donde Instagram pone su barra y la caja de respuesta.
PIEZAS = {
    "ordutegia": {"origen": HORARIOS, "titulo": (120, 270), "banda": (1070, 1262),
                  "post": (120, 1070), "historia": (370, 1560)},
    "emaitzak": {"origen": RESULTADOS, "titulo": (110, 262), "banda": (1165, 1350),
                 "post": (110, 1165), "historia": (360, 1580)},
}
ALTO = {"post": 1350, "historia": 1920}


def mascara_fundido(ancho, alto, arriba=True, abajo=True):
    """Opaca en el centro y transparente en los bordes de arriba y abajo, para que no se noten las uniones."""
    m = Image.new("L", (ancho, alto), 255)
    d = ImageDraw.Draw(m)
    for i in range(FUNDIDO):
        v = int(255 * i / FUNDIDO)
        if arriba:
            d.line([(0, i), (ancho, i)], fill=v)
        if abajo:
            d.line([(0, alto - 1 - i), (ancho, alto - 1 - i)], fill=v)
    return m


def fondo_continuo(alto):
    """Rellena la altura pedida con la franja limpia repetida, fundiendo cada copia con la anterior."""
    franja = Image.open(HORARIOS).convert("RGB").crop((0, FONDO_LIMPIO[0], 1080, FONDO_LIMPIO[1]))
    lienzo = Image.new("RGB", (1080, alto))
    y = 0
    while y < alto:
        lienzo.paste(franja, (0, y), mascara_fundido(1080, franja.height, arriba=y > 0, abajo=False))
        y += franja.height - FUNDIDO
    return lienzo


def lienzo(pieza, formato):
    p = PIEZAS[pieza]
    origen = Image.open(p["origen"]).convert("RGB")
    fondo = fondo_continuo(ALTO[formato])
    y_titulo, y_banda = p[formato]
    for (desde, hasta), y in ((p["titulo"], y_titulo), (p["banda"], y_banda)):
        trozo = origen.crop((0, desde, 1080, hasta))
        fondo.paste(trozo, (0, y), mascara_fundido(1080, trozo.height, abajo=y + trozo.height < ALTO[formato]))
    return fondo


def fila_emaitzak():
    """Recorta la cinta del primer resultado de la plantilla vacía y deja transparente lo de alrededor."""
    x0, y0, x1, y1 = 104, 264, 982, 368
    trozo = Image.open(RESULTADOS).convert("RGBA").crop((x0, y0, x1, y1))
    m = Image.new("L", trozo.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(110 - x0, 291 - y0), (976 - x0, 291 - y0), (941 - x0, 351 - y0), (144 - x0, 351 - y0)], fill=255)   # cinta azul
    d.polygon([(392 - x0, 283 - y0), (691 - x0, 283 - y0), (653 - x0, 364 - y0), (430 - x0, 364 - y0)], fill=255)   # pieza blanca
    d.ellipse([(509 - x0, y0 - y0 + 3), (573 - x0, 334 - y0)], fill=255)   # el balón, que sobresale por arriba
    trozo.putalpha(m)
    return trozo


def main():
    for pieza in PIEZAS:
        for formato in ALTO:
            lienzo(pieza, formato).save(os.path.join(PLANTILLAS, f"fondo-{pieza}-{formato}.png"), optimize=True)
    fila_emaitzak().save(os.path.join(PLANTILLAS, "fila-emaitzak.png"), optimize=True)
    escudo = Image.open(ESCUDO).convert("RGBA")
    escudo = escudo.crop(escudo.getbbox())
    escudo.thumbnail((600, 600))
    os.makedirs(os.path.join(REDES, "escudos"), exist_ok=True)
    escudo.save(os.path.join(REDES, "escudos", "Ortuella.png"), optimize=True)
    print("Lienzos preparados en redes/plantillas/ y escudo en redes/escudos/Ortuella.png")


if __name__ == "__main__":
    main()
