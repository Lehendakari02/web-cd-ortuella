# Flujo de n8n: publicaciones, avisos y noticias

`flujo.json` se importa en n8n (probado para la versión 2.44). Hace cuatro cosas, sin IA y sin coste:

1. **Publicaciones** (8:30 y 23:30, hora de Madrid): manda al grupo de Telegram cada pieza *lista*
   (ORDUTEGIA, EMAITZAK, MATCH DAY A y B), **una sola vez por semana**, y pide el texto de la publicación.
   Se contesta **respondiendo a la foto** (mantener pulsado → Responder). El bot enseña la foto con el texto
   y los botones *Publicar* / *Cancelar*. Al publicar, lo sube a Instagram, contesta con el enlace y pregunta si
   se sube también la historia. Si Instagram falla, lo dice con un botón *Reintentar*; antes de publicar comprueba
   que ese mismo texto no esté ya publicado (nunca sale dos veces).
2. **Avisos de cambios de partido**: manda al grupo los avisos nuevos de `cambios.json`.
3. **Comandos** en el grupo: `/estado`, `/horarios`, `/resultados`, `/matchday`, `/publicar <pieza>`,
   `/revisar instagram`, `/instagram` (comprobar la conexión), `/probar noticia`, `/ayuda`.
   El resto de mensajes del grupo se ignora (el bot puede tener la privacidad de grupo activada).

4. **Noticias de la web desde Instagram**: **cada hora** (a y 7) lee las publicaciones nuevas de la cuenta
   (de los últimos 3 días) que no haya publicado el bot y las manda al grupo: la foto y, como respuesta a
   ella, «¿La ponemos como noticia en la web?» con *Sí* / *No*. Con *Sí* propone un título (la primera
   frase del pie; se cambia respondiendo a ese mensaje) y con *Poner en la web* lanza el robot de GitHub
   **Añadir noticia**, que guarda una copia de la foto y publica la noticia (`redes/anadir_noticia.py`).
   Para no esperar a la siguiente hora, `/revisar instagram` lo hace en el momento (y, si no hay nada
   nuevo, lo dice; la revisión programada no avisa cuando no hay nada).
   Lo que publica el propio bot no se ofrece como noticia. `/probar noticia` hace el recorrido con una
   publicación de ejemplo (llega hasta GitHub en modo prueba, sin cambiar la web).

### Credenciales

- **GitHub** (se puede poner ya): en GitHub → Settings → Developer settings → *Fine-grained tokens* →
  *Generate new token*: solo el repositorio `web-cd-ortuella`, permiso **Actions: Read and write**.
  En n8n, nodo **Enviar a la web (GitHub)** → *Credential* → nueva **Header Auth** con
  Name `Authorization` y Value `Bearer <el token>`.
- **Instagram**: token de **usuario del sistema** del portfolio de empresa del club (Meta Business Suite →
  Usuarios del sistema → Generar token, caducidad **Nunca**, permisos `instagram_basic`,
  `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`).
  En n8n, una **Query Auth** con Name `access_token` y Value el token, elegida en los 10 nodos de Instagram:
  *Cuenta de Instagram (noticias)*, *Leer publicaciones de Instagram*, *Leer una publicación*,
  *Cuenta de Instagram (publicar)*, *Últimas publicaciones*, *Crear en Instagram*, *Publicar en Instagram*,
  *Enlace de la publicación*, *Cuenta de Instagram (comprobar)* y *Cuenta de Instagram (vigilancia)*. La cuenta de Instagram se busca sola a
  partir de la página de Facebook del club; la versión de la API está en `GRAPH`, al principio del constructor.
  `/instagram` en el grupo dice si la conexión funciona, y cada día a las 9:13 el flujo lo comprueba solo:
  si el token deja de valer, avisa en el grupo (cada día, hasta que se arregle).

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

**No ejecutes a mano la parte programada** («Revisar 8:30 y 23:30» y «Revisar Instagram cada hora»): los nodos *No repetir piezas* y
*No repetir avisos* apuntan lo que se manda y luego ya no lo volverían a mandar. Para probar, usa los
comandos en el grupo (`/publicar matchday`…).

El bot no necesita recordar nada: en el pie de cada foto escribe qué pieza es (`🆔 matchday`) y, en el
mensaje de confirmación, el texto va entre dos rayas. Al responder o pulsar un botón, lo lee de ahí.
