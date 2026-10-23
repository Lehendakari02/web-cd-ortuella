# Ideas para más adelante

Ideas que han salido y se quieren tener en cuenta. No están hechas. Casi todas se pueden hacer
sin IA, con el mismo sistema de ahora (robot de GitHub + generador + n8n + Telegram).

## Prioritaria

- **Aviso de cambios de partido a la directiva por Telegram.** Cuando la Federación publica la fecha
  u hora de un partido que aún no la tenía, la cambia, o cambia el campo, el bot lo avisa al grupo.
  Cómo: al actualizar, el robot compara los partidos nuevos con los anteriores, apunta los cambios
  (p. ej. `redes/salida/cambios.json`) y n8n los manda por Telegram.

## Decidida: noticias de la web desde Instagram (después de conectar Instagram)

Instagram es donde se crea el contenido; la web lo recoge. Necesita el token de Meta (lectura de las
publicaciones de la propia cuenta), así que va justo después de conectar la publicación en Instagram.

1. Dos veces al día, n8n lee las publicaciones nuevas de la cuenta del club.
2. **Primer filtro**: se descartan las que ha publicado el propio bot (horarios, resultados, match day).
3. Las demás se mandan al grupo de Telegram: «Nueva publicación en Instagram. ¿La ponemos como noticia
   en la web?» con los botones **Sí / No**. Si es «No», no se hace nada.
4. Si es «Sí»: título propuesto = primera frase del pie (se puede cambiar respondiendo al mensaje),
   y la noticia se publica en la web con foto (copia guardada en la web: las de Instagram caducan;
   carrusel → primera foto; vídeo/reel → portada), título, texto, fecha y enlace «Ver en Instagram».

Con lo aprendido en el flujo de publicaciones:
- Nada de la memoria interna de n8n: lo necesario va escrito en los propios mensajes y botones.
- Cada botón funciona una sola vez («Cada botón una sola vez», con *Sí* y *No* como un solo botón) y
  los botones desaparecen al pulsar, dejando marcado «✅ En la web» / «No es noticia».
- Cada publicación de Instagram se ofrece una sola vez (Remove Duplicates por su id).
- Disparador de Telegram 1.5 (filtro de grupo que reconoce los botones).

## Más publicaciones de Instagram (con el generador)

- Clasificación de cada categoría tras la jornada.
- Goleadores: top del equipo o de la liga.
- Cumpleaños de jugadores (con una lista de fechas).
- Rachas y estadísticas detectadas solas ("5 partidos sin perder", "portería a cero"…).
- Resumen del mes o de la temporada.
- Agradecimiento a los patrocinadores, rotando cada mes.
- **Llevar a la web desde Instagram** (cuando la web esté en `cdortuella.net`; anunciar la dirección de
  pruebas no tiene sentido). Que quien vea resultados, horarios, clasificación o MATCH DAY pueda ir a la web:
  - En el pie de un post los enlaces **no se pueden pulsar**: poner la web en el perfil de @cdortuella y
    terminar el texto con «Más información: enlace en la bio».
  - En la propia imagen: una línea fija «cdortuella.net» en las plantillas del generador (coste 0).
  - Historias: el sticker de enlace (*link sticker*) es lo único pulsable. Comprobar entonces si la API de
    Instagram permite ponerlo; si no, añadirlo a mano al subir la historia o dejar la dirección en la imagen.

## Bot de Telegram

- Comandos básicos (sin IA): `/estado`, `/ordutegia`, `/emaitzak`, `/matchday`, `/publicar …`.
- Más adelante, si se echa en falta: preguntas libres con IA ("nivel 2"), con coste por pregunta.

## Mantenimiento

- Alevín: añadir sus códigos a `EQUIPOS` en `actualizar_federacion.py` cuando la Federación publique su liga.
- Traspasar el repositorio al club (GitHub → Settings → Transfer ownership).
