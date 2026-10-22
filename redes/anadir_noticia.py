#!/usr/bin/env python3
"""
Añade a la web una noticia que viene de una publicación de Instagram (lo pide n8n cuando alguien
pulsa «Sí, ponerla en la web» en el grupo de Telegram).

- Guarda una COPIA de la foto en img/noticias/ (las fotos de Instagram caducan a los pocos días),
  reducida al ancho que usa la web.
- Añade la noticia a datos-noticias.js, que la web junta con las noticias escritas a mano.
- Si esa publicación ya está en la web, no hace nada: nunca hay dos veces la misma noticia.

Uso:  python3 redes/anadir_noticia.py --id 1789… --titulo "…" --texto "…" --fecha 2026-10-22 \
                                      --foto-url https://… --enlace https://www.instagram.com/p/… [--prueba]
      --prueba: lo hace todo (bajar y reducir la foto, preparar la noticia) pero no cambia la web.
Necesita Pillow.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import urllib.request
from io import BytesIO

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO = os.path.join(RAIZ, "datos-noticias.js")
FOTOS = os.path.join(RAIZ, "img", "noticias")
CABECERA = "/* Archivo generado automáticamente por redes/anadir_noticia.py (noticias que llegan de Instagram). No editar a mano. */\n"
ANCHO = 1200   # la foto más grande de la sección de noticias


def leer_noticias():
    try:
        texto = open(ARCHIVO, encoding="utf-8").read()
        return json.loads(texto[texto.index("["):texto.rindex("]") + 1])
    except (OSError, ValueError):
        return []


def limpiar_texto(texto):
    """El pie de Instagram, sin las líneas que solo son hashtags ni los espacios de sobra."""
    lineas = [l.rstrip() for l in texto.replace("\r", "").split("\n")]
    lineas = [l for l in lineas if not re.fullmatch(r"\s*(#\S+\s*)+", l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


def bajar_foto(url, destino):
    pet = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; CDOrtuellaWeb/1.0)"})
    with urllib.request.urlopen(pet, timeout=60) as r:
        img = Image.open(BytesIO(r.read())).convert("RGB")
    if img.width > ANCHO:
        img = img.resize((ANCHO, round(img.height * ANCHO / img.width)), Image.LANCZOS)
    img.save(destino, "WEBP", quality=82, method=6)
    return img.size


def main():
    o = argparse.ArgumentParser()
    for campo in ("id", "titulo", "texto", "fecha", "foto-url", "enlace"):
        o.add_argument("--" + campo, required=campo in ("id", "titulo", "fecha", "foto-url"), default="")
    o.add_argument("--prueba", action="store_true")
    a = o.parse_args()

    ident = re.sub(r"[^A-Za-z0-9_-]", "", a.id)
    fecha = a.fecha[:10]
    if not ident or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
        sys.exit("Falta el id de la publicación o la fecha no es AAAA-MM-DD")
    noticias = leer_noticias()
    if any(n.get("id") == ident for n in noticias):
        print(f"La publicación {ident} ya está en la web: no se añade otra vez")
        return

    nombre = f"{fecha}-{ident}.webp"
    carpeta = tempfile.mkdtemp() if a.prueba else FOTOS
    os.makedirs(carpeta, exist_ok=True)
    tam = bajar_foto(a.foto_url, os.path.join(carpeta, nombre))
    noticia = {"id": ident, "fecha": fecha, "etiqueta": "Club", "foto": f"img/noticias/{nombre}",
               "titulo": a.titulo.strip(), "texto": limpiar_texto(a.texto), "enlace": a.enlace.strip() or None}
    print(f"Foto: {tam[0]}×{tam[1]} px · Noticia: {json.dumps(noticia, ensure_ascii=False)}")
    if a.prueba:
        print("PRUEBA: todo correcto; no se cambia la web")
        return

    noticias.insert(0, noticia)
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(CABECERA + "window.NOTICIAS = " + json.dumps(noticias, ensure_ascii=False, indent=1) + ";\n")
    print(f"Añadida a la web: {noticia['titulo']}")


if __name__ == "__main__":
    main()
