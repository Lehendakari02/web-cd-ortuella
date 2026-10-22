# Ideas para más adelante

Ideas que han salido y se quieren tener en cuenta. No están hechas. Casi todas se pueden hacer
sin IA, con el mismo sistema de ahora (robot de GitHub + generador + n8n + Telegram).

## Prioritaria

- **Aviso de cambios de partido a la directiva por Telegram.** Cuando la Federación publica la fecha
  u hora de un partido que aún no la tenía, la cambia, o cambia el campo, el bot lo avisa al grupo.
  Cómo: al actualizar, el robot compara los partidos nuevos con los anteriores, apunta los cambios
  (p. ej. `redes/salida/cambios.json`) y n8n los manda por Telegram.

## Más publicaciones de Instagram (con el generador)

- Clasificación de cada categoría tras la jornada.
- Goleadores: top del equipo o de la liga.
- Cumpleaños de jugadores (con una lista de fechas).
- Rachas y estadísticas detectadas solas ("5 partidos sin perder", "portería a cero"…).
- Resumen del mes o de la temporada.
- Agradecimiento a los patrocinadores, rotando cada mes.

## Bot de Telegram

- Comandos básicos (sin IA): `/estado`, `/ordutegia`, `/emaitzak`, `/matchday`, `/publicar …`.
- Más adelante, si se echa en falta: preguntas libres con IA ("nivel 2"), con coste por pregunta.

## Mantenimiento

- Alevín: añadir sus códigos a `EQUIPOS` en `actualizar_federacion.py` cuando la Federación publique su liga.
- Traspasar el repositorio al club (GitHub → Settings → Transfer ownership).
