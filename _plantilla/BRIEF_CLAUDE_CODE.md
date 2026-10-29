# Encargo para Claude Code: checks diarios de avance de obra en la App IEC

Lee primero `_plantilla/ESPECIFICACION_APP_IEC.md` (rama `checklists-obra` de IEC-GROUP011/Planos-Interactivos-IEC) y `_plantilla/checklists.json`. Esta es la parte de la App y de Airtable; el visor de planos ya está hecho y solo lee.

## Decisiones ya tomadas
- Los checks los marca el **instalador sobre el plano interactivo**, con el visor abierto **dentro de la App IEC** (WebView). No hay pantalla de checks aparte. Se marca en el nivel más concreto: estancia (eléctrica) o cubierta (fotovoltaica).
- A las **16:55 (Europe/Madrid)**, en días de obra, la App manda una notificación push al **responsable del día**, que **cambia cada día** según quién vaya a la obra.
- El avance se guarda en Airtable (base IEC, `app8fKFbJcGwBqDMY`). El visor ya está hecho: lee el avance y, dentro de la App, envía cada cambio por POST (contrato en la sección 3b de la especificación).

## Tareas
1. **Airtable**
   - Tabla nueva «Avance de obra»: Proyecto (enlace a Proyectos), Fecha, Zona (texto, `<nivel1>/<nivel2>`), Check (texto, id de `checklists.json`), Hecho (casilla), Responsable (enlace a Usuarios), Registrado el (fecha de creación).
   - Campo nuevo en `Días de obra`: «Responsable del día» (enlace a un solo Trabajador, elegido entre «Trabajadores disponibles» de ese día).
   - Comprobar qué valor de «Tipo proyecto» o «Tipo Instalación» distingue eléctrica de fotovoltaica y usarlo para elegir el checklist.
2. **Endpoint de escritura** `POST /avance` (sección 3b): valida el token, deduce usuario e iniciales del token, crea el registro en «Avance de obra» (idempotente por obra+zona+check+ts), CORS para `https://iec-group011.github.io` con `Authorization`.
3. **Endpoint de lectura** `GET /avance?obra=<id>` con el JSON de la sección 3 (estado vigente = último registro por Proyecto + Zona + Check; `by` con `Trabajadores.Iniciales`; CORS abierto solo a `https://iec-group011.github.io`).
4. **WebView del plano en la App:** abrir la URL del visor de la obra inyectando `window.IEC_AUTH = {token, iniciales}` antes de cargar la página (token corto, solo para escribir avance), con el móvil en horizontal y sin borrar los datos del WebView entre sesiones (la cola sin conexión vive ahí).
5. **Aviso de las 16:55:** tarea programada (o Automation de Airtable que llame a la App; elige lo que encaje con el backend actual y dime cuál) que lee los `Días de obra` de hoy, toma el «Responsable del día» (si está vacío, todos los trabajadores de ese día), busca su usuario y envía push (FCM) a `Usuarios.TokenNotificaciones`. Texto: «Rellena los checks de hoy · <proyecto>»; al tocarla abre el plano de esa obra.
6. **Calendario de obra (opcional, aparte):** poder elegir el «Responsable del día» desde la interfaz «Calendario de obra».

## Comprobaciones al terminar
- Marcar un check sobre el plano en la App aparece en Airtable y en el visor (otro móvil) en menos de un minuto.
- Sin cobertura, el panel muestra «Sin enviar» y los cambios suben al volver la conexión, con su hora real.
- Con el token caducado el visor avisa y no pierde los cambios.
- Fuera de la App, el visor es de solo lectura.
- Un día sin obra no genera aviso; un día con obra y responsable distinto avisa solo a ese responsable.
- El JSON público no contiene nombres completos.
