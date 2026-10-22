# Publicaciones de Instagram automáticas

`generar_redes.py` dibuja cada semana, sin IA y sin coste, las tres publicaciones recurrentes del club
(post 1080×1350 e historia 1080×1920 de cada una) con los datos de `datos-federacion.js`:

| Pieza | Qué muestra | Semana |
|---|---|---|
| ORDUTEGIA | Rival, día, hora y 🏠/✈️ de cada categoría | La de mañana (el domingo ya muestra el finde siguiente) |
| EMAITZAK | Resultados jugados, cada equipo en su sitio (local / visitante) | La del último domingo |
| MATCH DAY | Partido de cada equipo de `config.json` (Senior A y Senior B): escudos, día en euskera, hora y campo | La de mañana |

Se ejecuta solo con el robot de la Federación (2 veces al día), justo después de actualizar los datos.
Deja el resultado en `redes/salida/`:

- `ordutegia-post.jpg`, `ordutegia-historia.jpg`, `emaitzak-…`, `matchday-…` (Senior A), `matchday-b-…` (Senior B)
- `ultimo.json`: la dirección pública de cada imagen. Es lo que lee n8n.

Si una pieza no tiene datos (no hay partidos o resultados esa semana), no aparece en `ultimo.json`.

## Qué se puede cambiar a mano (`config.json`)

- **categorias**: qué filas salen y cómo se llaman (p. ej. "SENIOR" en horarios y "SENIOR A" en resultados).
  Alevín sale con "—" hasta que se añada a `EQUIPOS` en `actualizar_federacion.py` (cuando la Federación publique su liga).
- **nombres_cortos**: solo para rivales que el club ya escribe de otra forma ("Union Sport B" → "UNIÓN B"). Los nombres no se acortan:
  si no está aquí, sale el nombre completo de la Federación, más pequeño si es largo.
- **campos_cortos**: igual para los campos de MATCH DAY.
- **fondos**: los fondos que van rotando cada semana; solo se usan los de estas listas, nunca otras fotos.
  - `tablas` (ORDUTEGIA y EMAITZAK): `"canva"` es el fondo de la plantilla de Canva; cualquier otra foto sale
    siempre con la misma receta: ampliada, difuminada y con velo azul marino, con el título y los patrocinadores encima.
  - `matchday`: la foto tal cual con un velo claro. `"velo": false` si la foto ya lo trae (las de Canva, en `redes/fondos/`)
    y `"diseno": 0` (MATCH DAY en vertical) o `1` (en horizontal) para fijar el diseño que mejor le va.
- **matchday**: qué equipos tienen MATCH DAY y cómo se escribe su nombre en la imagen.
- **categorias** y filas de EMAITZAK: con pocos resultados las filas se hacen más grandes solas.

Otros archivos:

- `canva/`: las plantillas exportadas de Canva. ORDUTEGIA y EMAITZAK usan su fondo, título y banda de
  patrocinadores tal cual. Si cambia algo en Canva (p. ej. un patrocinador), exportar en PNG 1080×1350,
  sustituir el archivo con el mismo nombre y ejecutar `python3 redes/preparar_fondos.py`: rehace los
  lienzos limpios de `plantillas/` (sin las filas de equipos, que las dibuja el generador).
- `plantillas/estilos.css`: el diseño (tamaños, colores, posiciones).
- `escudos/`: escudos de los rivales en buena calidad (se bajan solos de la Federación y se les quita el fondo blanco).
  Si uno sale mal, se puede poner a mano como `escudos/<Nombre exacto de la Federación>.png`. El nuestro,
  `escudos/Ortuella.png`, sale del escudo de `canva/`.
- `recursos/`: tipografía Montserrat e iconos (casa, avión, balón).

Probar en local (hacer como si hoy fuera otro día):

```
pip install playwright pillow && playwright install chromium
python3 redes/generar_redes.py --fecha 2026-10-22
```

## Publicar con n8n (con revisión por Telegram)

El pie de foto de cada publicación lo escribe una persona por Telegram, porque depende del momento
(empieza la liga, partido difícil, jornada importante…). No hay IA ni textos automáticos: coste 0.

`ultimo.json` (en `https://lehendakari02.github.io/web-cd-ortuella/redes/salida/ultimo.json`):

```json
{ "datos_actualizados": "2026-10-21T14:23+00:00",
  "piezas": {
    "ordutegia":  { "nombre": "ORDUTEGIA", "semana": "2026-10-19",
                    "post": "https://…/ordutegia-post.jpg?v=…", "historia": "https://…/ordutegia-historia.jpg?v=…" },
    "emaitzak":   { … }, "matchday": { … }, "matchday-b": { … } } }
```

Un flujo por pieza (por ejemplo ORDUTEGIA el jueves por la tarde, MATCH DAY el sábado por la mañana y
EMAITZAK el domingo por la noche):

1. **Schedule Trigger**: el día y la hora.
2. **HTTP Request** (GET) a `ultimo.json`.
3. **IF**: que exista la pieza (p. ej. `piezas.matchday`) y que su `semana` sea la actual, para no repetir una vieja.

**Post (lleva pie de foto):**

4. **Telegram → Send Photo** con la imagen `post` y el mensaje "MATCH DAY listo. ¿Qué texto pongo en la publicación?".
5. **Telegram → Send and Wait for Response**, respuesta de texto libre: n8n espera a que contestes con el texto.
6. **Telegram → Send Photo** de nuevo con la imagen y, como pie, el texto recibido: "¿Publico esto?".
7. **Telegram → Send and Wait for Response**, tipo aprobación (botones *Publicar* / *Cancelar*).
8. Si *Publicar*: **Instagram** (o HTTP Request a la API de Instagram Graph): crear el contenedor con
   `image_url` = `post` y `caption` = el texto recibido, publicarlo y avisar por Telegram: "Publicado ✅".
   Si *Cancelar*: avisar y terminar (o volver al paso 4 para escribir otro texto).

**Historia (sin pie de foto):**

9. **Telegram → Send Photo** con la imagen `historia`: "¿Subo esta historia?".
10. **Telegram → Send and Wait for Response**, aprobación.
11. Si *Publicar*: crear el contenedor con `image_url` = `historia` y `media_type` = `STORIES`, y publicarlo.

Coste: 0 €. El bot de Telegram se crea gratis con @BotFather y se conecta en n8n con su token; n8n está
en el servidor propio; la API de Instagram es gratuita. Mientras espera la respuesta, n8n no gasta nada.

La API de Instagram exige que la cuenta sea profesional (de empresa o creador) y esté vinculada a una página de Facebook.
Las imágenes son JPG y están en una dirección pública, que es lo que pide Instagram.
