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

Generar no es publicar: las imágenes se rehacen cada vez que se actualiza la web, pero cada pieza lleva
`"lista": true` solo cuando tiene todos sus datos, y n8n publica cada una **una sola vez por fin de semana**:

- ORDUTEGIA: cuando todos los equipos que juegan tienen fecha y hora. Un equipo sin partido (p. ej. el alevín
  sin liga) sale con "—" y no bloquea; un partido sin hora todavía, sí.
- EMAITZAK: cuando todos los partidos del fin de semana tienen resultado. Si el martes sigue faltando alguno
  (un partido aplazado), se ofrece igualmente sin él, con `"faltan"` diciendo cuál, para decidir si se publica.
- MATCH DAY (cada equipo por separado): cuando se sabe el día, la hora y el campo.

Si falta algo, `"faltan"` dice qué. Si una pieza no tiene ningún dato (no hay partidos esa semana), no aparece.

## Avisos de cambios de partido

`detectar_cambios.py` compara, en cada actualización, los datos de antes y de después y apunta en
`redes/salida/cambios.json` los cambios en los **próximos partidos** de nuestros equipos, para que n8n
los mande al grupo de Telegram de la directiva:

- 📅 un partido recibe su hora (y su día real);
- ⚠️ cambia el día, la hora o el campo de un partido (con el antes y el después);
- 🆕 aparece un partido nuevo en el calendario.
- ❌ un partido por jugar desaparece del calendario (anulado o retirado).

Los partidos ya jugados no avisan, y cuando un equipo carga su calendario por primera vez (p. ej. el
alevín al empezar su liga) tampoco: sería todo el calendario de golpe. Se guardan los 50 últimos
avisos, cada uno con un `id` para que n8n no mande dos veces el mismo:

```json
{ "avisos": [ { "id": "1a2b3c4d5e6f", "detectado": "2026-10-23T08:04+02:00",
                "texto": "📅 JUVENIL · J4: Ortuella – Zuazo B\nYa tiene hora: LARUNBATA 24/10 16:15 · OTXARTAGA BERRI" } ] }
```

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

**Flujo listo para importar:** [`n8n/flujo-ensayo.json`](n8n/flujo-ensayo.json), con instrucciones en
[`n8n/README.md`](n8n/README.md). Lo de abajo explica cómo funciona por dentro.

El pie de foto de cada publicación lo escribe una persona por Telegram, porque depende del momento
(empieza la liga, partido difícil, jornada importante…). No hay IA ni textos automáticos: coste 0.

`ultimo.json` (en `https://lehendakari02.github.io/web-cd-ortuella/redes/salida/ultimo.json`):

```json
{ "datos_actualizados": "2026-10-21T14:23+00:00",
  "piezas": {
    "ordutegia":  { "tipo": "ordutegia", "nombre": "ORDUTEGIA", "semana": "2026-10-19", "lista": true, "faltan": [],
                    "post": "https://…/ordutegia-post.jpg?v=…", "historia": "https://…/ordutegia-historia.jpg?v=…" },
    "emaitzak":   { … }, "matchday": { … }, "matchday-b": { … } } }
```

Un solo flujo para todas las piezas:

1. **Schedule Trigger**: poco después de cada actualización de la web (p. ej. 8:30 y 23:30), o cada pocas horas.
2. **HTTP Request** (GET) a `ultimo.json` y separar las piezas (una por elemento).
3. **Filter**: solo las que tienen `lista` = true.
4. **Remove Duplicates**, modo "eliminar los ya procesados en ejecuciones anteriores", con la clave
   `{{tipo}}-{{semana}}`: así cada pieza se ofrece **una sola vez por semana**, aunque el flujo se ejecute muchas veces.

**Post (lleva pie de foto):**

5. **Telegram → Send Photo** con la imagen `post` y el mensaje "{{nombre}} listo. ¿Qué texto pongo en la publicación?".
   Si `faltan` no está vacío (p. ej. un partido aplazado), añadir al mensaje: "Ojo, falta: {{faltan}}".
6. **Telegram → Send and Wait for Response**, respuesta de texto libre: n8n espera a que contestes con el texto.
7. **Telegram → Send Photo** de nuevo con la imagen y, como pie, el texto recibido: "¿Publico esto?".
8. **Telegram → Send and Wait for Response**, tipo aprobación (botones *Publicar* / *Cancelar*).
9. Si *Publicar*: **Instagram** (o HTTP Request a la API de Instagram Graph): crear el contenedor con
   `image_url` = `post` y `caption` = el texto recibido, publicarlo y avisar por Telegram: "Publicado ✅".
   Si *Cancelar*: avisar y terminar (o volver al paso 5 para escribir otro texto).

**Historia (sin pie de foto):**

10. **Telegram → Send Photo** con la imagen `historia`: "¿Subo esta historia?".
11. **Telegram → Send and Wait for Response**, aprobación.
12. Si *Publicar*: crear el contenedor con `image_url` = `historia` y `media_type` = `STORIES`, y publicarlo.

Coste: 0 €. El bot de Telegram se crea gratis con @BotFather y se conecta en n8n con su token; n8n está
en el servidor propio; la API de Instagram es gratuita. Mientras espera la respuesta, n8n no gasta nada.

La API de Instagram exige que la cuenta sea profesional (de empresa o creador) y esté vinculada a una página de Facebook.
Las imágenes son JPG y están en una dirección pública, que es lo que pide Instagram.
