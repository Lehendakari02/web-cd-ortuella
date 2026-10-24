# Flujo de n8n: publicaciones, avisos y noticias

`flujo.json` se importa en n8n (probado para la versión 2.44). Hace cuatro cosas, sin IA y sin coste:

1. **Publicaciones** (8:30 y 23:30, hora de Madrid): manda al grupo de Telegram cada pieza *lista*
   (ORDUTEGIA, EMAITZAK, SAILKAPENA, MATCH DAY A y B) **que aún no esté publicada esa semana**, y pide el texto.
   Si no se publica, vuelve a salir en la siguiente revisión (p. ej. el MATCH DAY, hasta el día del partido).
   Para que no salga más esa semana, botón **🚫 Esta semana no** de la foto (si luego cambias de idea,
   `/publicar …` la pide igual). Una vez publicada (desde la revisión o con `/publicar`), no vuelve a salir.
   Se contesta **respondiendo a la foto** (mantener pulsado → Responder). El bot enseña la foto con el texto
   y los botones *Publicar* / *Cancelar*. Al publicar, lo sube a Instagram, contesta con el enlace y pregunta si
   se sube también la historia. Si Instagram falla, lo dice con un botón *Reintentar*; antes de publicar comprueba
   que ese mismo texto no esté ya publicado (nunca sale dos veces).
2. **Avisos de cambios de partido**: manda al grupo los avisos nuevos de `cambios.json`.
3. **Comandos** en el grupo: `/estado`, `/horarios`, `/resultados`, `/matchday`, `/publicar <pieza>`,
   `/clasificacion`, `/amistoso`, `/resultado`, `/amistosos`, `/borrar amistoso`, `/revisar instagram`,
   `/instagram` (comprobar la conexión), `/probar noticia`, `/ayuda` (y `/ayuda amistosos`, `ver`, `publicar`…).
   **Amistosos**: el bot pide confirmación y lanza el robot de GitHub **Amistoso** (`amistoso.yml`), que los guarda en
   `datos-amistosos.js` y rehace imágenes y calendario. Usa la misma credencial de GitHub que las noticias.
   La clasificación es un **carrusel**: el bot manda antes sus imágenes y, al final, la portada a la que se responde.
   El resto de mensajes del grupo se ignora (el bot puede tener la privacidad de grupo activada).

4. **Noticias de la web desde Instagram**: **cada hora** (a y 7) lee las publicaciones nuevas de la cuenta
   (de los últimos 3 días) que no haya publicado el bot y las manda al grupo: la foto y, como respuesta a
   ella, «¿La ponemos como noticia en la web?» con *Sí* / *No*. Con *Sí* propone un título (la primera
   frase del pie; se cambia respondiendo a ese mensaje) y con *Poner en la web* lanza el robot de GitHub
   **Añadir noticia**, que guarda una copia de la foto y publica la noticia (`redes/anadir_noticia.py`).
   Para no esperar a la siguiente hora, `/revisar instagram` lo hace en el momento (y, si no hay nada
   nuevo, lo dice; la revisión programada no avisa cuando no hay nada).
   Lo que publica el propio bot no se ofrece como noticia, y cada publicación se ofrece una sola vez. `/probar noticia` hace el recorrido con una
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

## La memoria: tabla de datos `memoria_ortuella`

El flujo apunta lo ya hecho en una **tabla de datos** de n8n (*Data table*, menú **Overview → Data tables**), no
dentro del flujo: así **no se pierde al importar el flujo otra vez**. La crea el propio flujo la primera vez que
la necesita; los nodos la buscan por el nombre (*By Name*), así que no hay que elegirla en ninguno.
Cada fila tiene `clave` y `estado`:

| `clave` | `estado` | Qué es |
|---|---|---|
| `pieza:matchday-2026-10-19` | `publicada` o `descartada` | Pieza de esa semana publicada o con «🚫 Esta semana no»: no se vuelve a ofrecer |
| `aviso:c927ba0cfbea` | `enviado` | Aviso de cambio de partido ya mandado |
| `ig:1789…` | `ofrecida`, `del bot` o `vista` | Publicación de Instagram ya ofrecida como noticia, publicada por el bot o ya existente al estrenar la memoria |
| `ig:estreno` | `hecho` | La memoria de Instagram ya se ha estrenado |

- Si se borra una fila `pieza:…`, esa pieza se vuelve a ofrecer (y se puede publicar otra vez esa semana).
- Al estrenarla: las publicaciones de Instagram que ya hay se apuntan como `vista` sin ofrecerlas, y los avisos
  de más de 2 días no se mandan. Las piezas ya publicadas esa semana (antes de la memoria) saldrán una vez más:
  se pulsa 🚫 en cada una.

## Importarlo

1. Si el archivo trae `CHAT_ID_DEL_GRUPO`, cámbialo por el Chat ID del grupo (con el `-` delante) en todo el
   archivo (en un editor de texto: Buscar y reemplazar).
2. En n8n: **Create workflow → menú ⋯ (arriba a la derecha) → Import from File** y elige el archivo.
3. Abre cada nodo de Telegram (los que tienen el icono de Telegram) y en **Credential** elige la del bot.
4. **Importante**: Telegram solo permite **un disparador por bot**. Desactiva el flujo anterior del Ortuella
   (y cualquier otro con el Telegram Trigger de ese bot) antes de activar este.
5. Guarda y activa el flujo (interruptor **Active** arriba a la derecha).

## Probarlo

- En el grupo, escribe `/estado` o `/matchday`: el bot debe contestar.
- Para probar el recorrido completo: `/publicar matchday` → responder citando la foto → *Publicar*.

- `/estado` dice de cada pieza si está lista, publicada ✅ o descartada 🚫.

Ejecutar a mano «Revisar 8:30 y 23:30» no estropea nada: manda lo que esté pendiente, como la revisión de la
hora (los avisos que mande quedan apuntados como enviados).

El texto y la pieza no se guardan: en el pie de cada foto el bot escribe qué pieza es (`🆔 matchday`) y, en el
mensaje de confirmación, el texto va entre dos rayas. Al responder o pulsar un botón, lo lee de ahí. Lo único
que recuerda es lo de la tabla `memoria_ortuella`.

## Lista de comandos para @BotFather

`/setcommands` → el bot → pegar entera:

```
ayuda - Qué sabe hacer el bot (y /ayuda amistosos, ver, publicar…)
estado - Qué publicaciones están listas y qué falta
horarios - Ver la imagen de horarios (ORDUTEGIA)
resultados - Ver la imagen de resultados (EMAITZAK)
matchday - Ver las imágenes de MATCH DAY A y B
clasificacion - Ver la clasificación (carrusel)
publicar - Publicar una pieza: /publicar horarios, resultados, match day A o B, clasificacion
amistoso - Apuntar un amistoso: /amistoso infantil 24/10 10:30 Escolapios
resultado - Resultado de un amistoso: /resultado infantil 3-1
amistosos - Ver los amistosos apuntados
borrar - Borrar un amistoso: /borrar amistoso 2
revisar - Revisar Instagram ahora: /revisar instagram
instagram - Comprobar la conexión con Instagram
probar - Probar una noticia de Instagram: /probar noticia
```
