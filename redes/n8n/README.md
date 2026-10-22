# Flujo de n8n: publicaciones y avisos (modo ensayo)

`flujo-ensayo.json` se importa en n8n (probado para la versión 2.44). Hace tres cosas, sin IA y sin coste:

1. **Publicaciones** (8:30 y 23:30, hora de Madrid): manda al grupo de Telegram cada pieza *lista*
   (ORDUTEGIA, EMAITZAK, MATCH DAY A y B), **una sola vez por semana**, y pide el texto de la publicación.
   Se contesta **respondiendo a la foto** (mantener pulsado → Responder). El bot enseña la foto con el texto
   y los botones *Publicar* / *Cancelar*; después pregunta si se sube también la historia.
2. **Avisos de cambios de partido**: manda al grupo los avisos nuevos de `cambios.json`.
3. **Comandos** en el grupo: `/estado`, `/ordutegia`, `/emaitzak`, `/matchday`, `/publicar <pieza>`, `/ayuda`.
   El resto de mensajes del grupo se ignora (el bot puede tener la privacidad de grupo activada).

🧪 **Modo ensayo**: al pulsar *Publicar* no publica en Instagram, contesta «(ensayo) Se habría publicado…».
Cuando haya token de Instagram, se cambian esos dos puntos (marcados con `🧪 ENSAYO` en el nodo
*Interpretar*) por la publicación real.

## Importarlo

1. Si el archivo trae `CHAT_ID_DEL_GRUPO`, cámbialo por el Chat ID del grupo (con el `-` delante) en todo el
   archivo (en un editor de texto: Buscar y reemplazar).
2. En n8n: **Create workflow → menú ⋯ (arriba a la derecha) → Import from File** y elige el archivo.
3. Abre cada nodo de Telegram (los que tienen el icono de Telegram) y en **Credential** elige la del bot.
4. **Importante**: Telegram solo permite **un disparador por bot**. Desactiva el flujo de prueba que tenías
   con el Telegram Trigger de ese bot antes de activar este.
5. Guarda y activa el flujo (interruptor **Active** arriba a la derecha).

## Probarlo

- En el grupo, escribe `/estado` o `/matchday`: el bot debe contestar.
- Para probar el recorrido completo: `/publicar matchday` → responder citando la foto → *Publicar*.

**No ejecutes a mano la parte programada** («Revisar 8:30 y 23:30»): los nodos *No repetir piezas* y
*No repetir avisos* apuntan lo que se manda y luego ya no lo volverían a mandar. Para probar, usa los
comandos en el grupo (`/publicar matchday`…).

El bot no necesita recordar nada: en el pie de cada foto escribe qué pieza es (`🆔 matchday`) y, en el
mensaje de confirmación, el texto va entre dos rayas. Al responder o pulsar un botón, lo lee de ahí.
