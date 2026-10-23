# Pendientes del proyecto (web del CD Ortuella)

Lo que queda por hacer en este proyecto. Lo común a todos los proyectos (servidor, cuentas, seguridad) está en
la bitácora (`Lehendakari02/bitacora`). Cuando algo se hace, pasa a «Hecho».

## Próximos pasos
1. **Leer la Federación sin que nos bloquee.** Comprobado el 23/10: la Federación bloquea a los centros de datos
   (desde Hetzner llega la página vacía; desde GitHub, casi siempre). Pedirle acceso no es posible.
   - Hecho: el robot de GitHub pasa 7 veces al día; cada pasada guarda lo que lee. Ver en las comprobaciones del 26 y
     29/10 si con eso basta.
   - Alternativas a probar: **Google Apps Script** (gratis, servidores de Google, sin aparatos: primero una prueba de
     10 minutos) o un **aparato en casa** (móvil Android viejo con Termux, o Raspberry Pi ~60-80 €).
   - Descartado: el servidor de Hetzner (bloqueado) y los *proxies* residenciales (sería saltarse el bloqueo).
2. **Publicación automática con veto.** El bot manda la pieza con un texto predeterminado (frases que rotan, con datos)
   y avisa: «se publicará sola a las 10:00; responde a la foto para cambiar el texto o pulsa Cancelar». Se puede
   decidir por pieza (p. ej. MATCH DAY con texto vuestro). Cambia la regla de la bitácora «nada se publica sin
   aprobación» por «nada se publica sin que la directiva haya podido verlo».

## Más adelante
- Reimportar el flujo de n8n cuando toque otro cambio (lleva el mensaje «⏳ Apuntando…» de los amistosos).
- Comprobaciones programadas del robot de la Federación: 26 y 29/10.
- Alevín: añadir sus códigos al robot cuando la Federación publique su liga.
- Enlace a la web en todas las imágenes («Toda la info del club → enlace en el perfil») al lanzar `cdortuella.net`
  (ver `redes/IDEAS.md`).
- Datos de la web que pone Julen: CIF, registro, precios, directiva, fotos de equipos, logos.

## Hecho
- 2026-10-23 — Instagram conectado (token de usuario del sistema «Nunca»); flujo definitivo de n8n con publicación real.
- 2026-10-23 — SAILKAPENA (clasificación) en carrusel + historia; ORDUTEGIA con diseño nuevo; los cinco patrocinadores en la clasificación.
- 2026-10-23 — Amistosos por Telegram (`/amistoso`, `/resultado`, `/amistosos`, `/borrar amistoso`) y `/ayuda` por bloques.
- 2026-10-23 — Robot de la Federación: actualiza a medias si falla una página y conserva hora y campo; robot de amistosos con reintentos.
