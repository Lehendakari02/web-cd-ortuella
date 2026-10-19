# Web del CD Ortuella

Web estática (solo HTML, CSS y JavaScript), sin servidor ni base de datos.

| Archivo | Qué es | ¿Se toca a mano? |
|---|---|---|
| `datos.js` | Noticias, convocatoria, directiva, socios, tienda, patrocinadores | Sí |
| `datos-federacion.js` | Partidos, resultados, clasificaciones y goleadores | No: lo genera `actualizar_federacion.py` |
| `estilos.css` | Diseño (colores, tipos de letra) | Rara vez |
| `comun.js` | Menú, pie de página y piezas comunes | Rara vez |
| `*.html` | Una página por sección | No: las genera `generar_paginas.py` |
| `img/` | Fotos y logos | Al añadir fotos |

Mientras la web está en pruebas no aparece en buscadores: cada página lleva `<meta name="robots" content="noindex">` y `robots.txt` lo prohíbe. Para el lanzamiento se quitan las dos cosas.
