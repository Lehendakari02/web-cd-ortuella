# Web del CD Ortuella

Web estática (solo HTML, CSS y JavaScript), sin servidor ni base de datos.

| Archivo | Qué es | ¿Se toca a mano? |
|---|---|---|
| `datos.js` | Noticias, convocatoria, directiva, socios, tienda, patrocinadores | Sí |
| `datos-federacion.js` | Partidos, resultados, clasificaciones y goleadores | No: lo genera `actualizar_federacion.py` |
| `calendario/*.ics` | Calendarios de partidos para suscribirse desde el móvil | No: los genera `generar_calendario.py`, que se ejecuta solo después de `actualizar_federacion.py` |
| `estilos.css` | Diseño (colores, tipos de letra) | Rara vez |
| `comun.js` | Menú, pie de página y piezas comunes | Rara vez |
| `*.html` | Una página por sección | No: las genera `generar_paginas.py` |
| `img/` | Fotos y logos | Al añadir fotos |
| `manifest.webmanifest`, `img/icono-*.png` | Nombre e icono al guardar la web en la pantalla de inicio del móvil | No |

`404.html` es la página que sale con un enlace roto. Usa la dirección `SITIO` de `generar_paginas.py`, así que al cambiar de dominio basta con cambiarla allí y regenerar.

Mientras la web está en pruebas no aparece en buscadores: con `PUBLICADA = False` en `generar_paginas.py`, cada página lleva `<meta name="robots" content="noindex">` y `robots.txt` lo prohíbe. `sitemap.xml` (la lista de páginas para Google) se genera siempre, pero no sirve de nada hasta el lanzamiento.

## Lanzamiento

1. En `generar_paginas.py`: `SITIO = "https://cdortuella.net"` y `PUBLICADA = True`. Ejecutar `python3 generar_paginas.py`.
2. Crear el archivo `CNAME` con una sola línea: `cdortuella.net`. Solo ese día: con él, GitHub empieza a servir la web en el dominio.
3. En el proveedor del dominio, cambiar solo los registros de la web (`A` de `cdortuella.net` a las IP de GitHub Pages y `www` como `CNAME` a `lehendakari02.github.io`). Los del correo (`MX`) no se tocan.
4. En GitHub → Settings → Pages: escribir `cdortuella.net` como dominio y, cuando lo permita, marcar «Enforce HTTPS».
5. Dar de alta la web en Google Search Console y enviar `https://cdortuella.net/sitemap.xml`.

Después de cambiar `estilos.css`, `comun.js` o `datos.js`, ejecuta `python3 generar_paginas.py`: actualiza la marca `?v=` de las páginas para que los navegadores no sigan mostrando la versión antigua guardada.
