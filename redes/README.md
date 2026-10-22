# Publicaciones de Instagram automáticas

`generar_redes.py` dibuja cada semana, sin IA y sin coste, las tres publicaciones recurrentes del club
(post 1080×1350 e historia 1080×1920 de cada una) con los datos de `datos-federacion.js`:

| Pieza | Qué muestra | Semana |
|---|---|---|
| ORDUTEGIA | Rival, día, hora y 🏠/✈️ de cada categoría | La de mañana (el domingo ya muestra el finde siguiente) |
| EMAITZAK | Resultados jugados, cada equipo en su sitio (local / visitante) | La del último domingo |
| MATCH DAY | Partido del primer equipo: escudos, día en euskera, hora y campo | La de mañana |

Se ejecuta solo con el robot de la Federación (2 veces al día), justo después de actualizar los datos.
Deja el resultado en `redes/salida/`:

- `ordutegia-post.jpg`, `ordutegia-historia.jpg`, `emaitzak-…`, `matchday-…`
- `ultimo.json`: la dirección pública de cada imagen y el texto que la acompaña. Es lo que lee n8n.

Si una pieza no tiene datos (no hay partidos o resultados esa semana), no aparece en `ultimo.json`.

## Qué se puede cambiar a mano (`config.json`)

- **categorias**: qué filas salen y cómo se llaman (p. ej. "SENIOR" en horarios y "SENIOR A" en resultados).
  Alevín sale con "—" hasta que se añada a `EQUIPOS` en `actualizar_federacion.py` (cuando la Federación publique su liga).
- **nombres_cortos**: cómo se escribe un rival ("Union Sport B" → "UNIÓN B"). Si no está, sale el nombre de la Federación.
- **campos_cortos**: igual para los campos de MATCH DAY.
- **fondos**: lista de fotos de MATCH DAY (van rotando cada semana; solo se usan las de esta lista).
- **textos**: frases para acompañar cada publicación (van rotando cada semana).

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

## Publicar con n8n

`ultimo.json` (en `https://lehendakari02.github.io/web-cd-ortuella/redes/salida/ultimo.json`) tiene esta forma:

```json
{ "datos_actualizados": "2026-10-21T14:23+00:00",
  "piezas": {
    "ordutegia": { "semana": "2026-10-19", "texto": "Asteburuko ordutegia 💙🤍 #aupaortuella",
                   "post": "https://…/ordutegia-post.jpg?v=…", "historia": "https://…/ordutegia-historia.jpg?v=…" },
    "emaitzak":  { … }, "matchday": { … } } }
```

Un flujo por pieza (por ejemplo ORDUTEGIA el jueves por la tarde, MATCH DAY el sábado por la mañana y EMAITZAK el domingo por la noche):

1. **Schedule Trigger**: el día y la hora de la publicación.
2. **HTTP Request** (GET) a `ultimo.json`.
3. **IF**: que exista la pieza (`piezas.ordutegia`) y que su `semana` sea la actual, para no repetir una publicación vieja.
4. **Instagram** (o HTTP Request a la API de Instagram Graph):
   - Post: crear el contenedor con `image_url` = `post` y `caption` = `texto`, y publicarlo.
   - Historia: crear el contenedor con `image_url` = `historia` y `media_type` = `STORIES`, y publicarlo.

La API de Instagram exige que la cuenta sea profesional (de empresa o creador) y esté vinculada a una página de Facebook.
Las imágenes son JPG y están en una dirección pública, que es lo que pide Instagram.
