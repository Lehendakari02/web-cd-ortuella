# Pendientes del proyecto (web del CD Ortuella)

Lo que queda por hacer en este proyecto. Lo común a todos los proyectos (servidor, cuentas, seguridad) está en
la bitácora (`Lehendakari02/bitacora`). Cuando algo se hace, pasa a «Hecho».

## Próximos pasos
1. **Leer la Federación sin que nos bloquee.** Comprobado el 23/10: la Federación bloquea a los centros de datos
   (desde Hetzner llega la página vacía; desde GitHub, casi siempre). Pedirle acceso no es posible.
   - Probadas 7 pasadas al día con una máquina: los primeros equipos se leen y los últimos casi nunca (la Federación
     corta a cada máquina tras unas cuantas páginas). Ahora: **un robot (máquina) por equipo** y otro que junta, 2
     pasadas al día. Ver en las comprobaciones del 26 y 29/10 si con eso basta.
   - Alternativas a probar: **Google Apps Script** (gratis, servidores de Google, sin aparatos: primero una prueba de
     10 minutos) o un **aparato en casa** (móvil Android viejo con Termux, o Raspberry Pi ~60-80 €).
   - Descartado: el servidor de Hetzner (bloqueado) y los *proxies* residenciales (sería saltarse el bloqueo).

## Más adelante
- **Revisar 2 ramas con arreglos del flujo de n8n sin fusionar** (24/10): `claude/arreglo-memoria-n8n` («Subir historia»/«No» valen una sola vez) y `claude/guia-n8n` (avisar si se responde a una foto que el bot no tiene en memoria). Ver si el `flujo.json` actual ya lo hace; si no, rehacerlo en una PR. Después se pueden borrar.
- **Tests del lector de la Federación**: guardar páginas de ejemplo con datos conocidos y comprobar que el lector los saca bien; y antes de publicar, si lo leído sale vacío o raro, mantener los datos de ayer y avisar por Telegram.
- **Entorno de pruebas**: flujo de n8n y grupo de Telegram de pruebas para probar cada cambio del flujo antes de importarlo en el real.
- Comprobaciones programadas del robot de la Federación: 26 y 29/10.
- Alevín: comprobación semanal programada (lunes) de si la Federación ya publica su liga. Cuando salga: añadir sus
  códigos a `EQUIPOS` en `actualizar_federacion.py` (sale solo un sexto robot) y **comprobar toda la cadena** con él
  (robot, web, calendario, imágenes, avisos, amistosos y bot de Telegram) antes de darlo por bueno.
- Lanzamiento en Cloudflare Pages + `cdortuella.net` (el repositorio sigue público).
- **Justo después del lanzamiento en Cloudflare: poner el repositorio privado** (regla de la bitácora: repos privados por defecto). En privado, GitHub Actions da 2.000 minutos gratis al mes. Medido el 24/10: el robot de la Federación gasta 7 minutos por pasada (7 máquinas de menos de 1 minuto), unos 420 al mes con 2 pasadas al día; amistosos y noticias, 1 minuto cada uno; y la publicación en GitHub Pages (unos 235 minutos en la última semana) desaparece al pasar a Cloudflare. Total esperado: unos 450 al mes, la cuarta parte del límite.
- Enlace a la web en todas las imágenes («Toda la info del club → enlace en el perfil»): **justo después** del
  lanzamiento, nunca antes (ahora el enlace llevaría a GitHub). Ver `redes/IDEAS.md`.
- **Ficha de Google del club** (Google Maps), el día del lanzamiento: reclamarla con el Gmail del club
  (`cdortuella1949@gmail.com`) y ponerla al día: web nueva, dirección y foto del campo (Otxartaga), teléfono,
  categoría, descripción, logo y fotos. La usan sobre todo los equipos de fuera para llegar. Junto con **Google Search
  Console** (alta de la web y su mapa), para que al buscar «CD Ortuella» salga la web nueva y no la antigua.
- **Temporada 2027/28** (y cada temporada nueva): revisar el primer MATCH DAY de cada rival nuevo, por si su escudo
  de la Federación viene raro (ver «escudos/» en `redes/README.md`).
- Datos de la web que pone Julen: CIF, registro, precios, directiva, fotos de equipos, logos.

## Aparcado
- **Publicación automática con veto** (el bot publica solo a una hora salvo que se cancele). A la directiva le gusta
  como está ahora (se publica al pulsar «Publicar»); la idea se guarda por si se quiere más adelante.

## Hecho
- 2026-10-24 — MATCH DAY: el escudo de La Arboleda salía encogido por una raya de 1 píxel en el borde; el recorte de escudos ya no cuenta las rayas sueltas, y en el MATCH DAY todos los escudos ocupan la misma superficie y dejan aire con el texto.
- 2026-10-24 — Amistosos: el bot espera a que el robot de GitHub termine y entonces contesta «✅ Amistoso apuntado» (o avisa si falla).
- 2026-10-24 — Flujo de n8n con memoria en la tabla `memoria_ortuella` (no repite lo publicado aunque se importe de nuevo) y botón «🚫 Esta semana no».
- 2026-10-23 — Un robot de GitHub por equipo y otro que junta (PR #55): primera pasada con los 5 equipos leídos sin fallos.
- 2026-10-23 — Instagram conectado (token de usuario del sistema «Nunca»); flujo definitivo de n8n con publicación real.
- 2026-10-23 — SAILKAPENA (clasificación) en carrusel + historia; ORDUTEGIA con diseño nuevo; los cinco patrocinadores en la clasificación.
- 2026-10-23 — Amistosos por Telegram (`/amistoso`, `/resultado`, `/amistosos`, `/borrar amistoso`) y `/ayuda` por bloques.
- 2026-10-23 — Robot de la Federación: actualiza a medias si falla una página y conserva hora y campo; robot de amistosos con reintentos.
