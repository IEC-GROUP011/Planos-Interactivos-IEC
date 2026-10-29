# Encargo para Claude Code: checks diarios de avance de obra en la App IEC

Contexto técnico: la App IEC son dos repositorios: la app Android (Kotlin, Compose, Room, WorkManager) y el backend BFF (Ktor en Cloud Run, Firebase Auth/FCM, Cloud Storage), que es lo único que habla con Airtable (campos por ID). Lee primero `CONTEXTO_PROYECTO.md` de cada repositorio y respeta sus reglas de trabajo. Haz esto en **dos sesiones**: primero el backend (tareas 1, 2, 3 y 5) y después la app (tarea 4).

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
2. **Endpoint de escritura** `POST /avance` (sección 3b) en el BFF: verifica el token de Firebase con el mecanismo actual, deduce usuario e iniciales (`Usuarios` → `Trabajador`), crea el registro en «Avance de obra», idempotente por `external_id`. Añade CORS para `https://iec-group011.github.io` (con `Authorization`) solo en estas rutas. Servicio nuevo (`AvanceService`), no dentro de `AirtableService`.
3. **Endpoint de lectura** `GET /avance?obra=<id>` con el JSON de la sección 3 (estado vigente = último registro por Proyecto + Zona + Check; `by` con `Trabajadores.Iniciales`; CORS abierto solo a `https://iec-group011.github.io`).
4. **WebView del plano en la App Android:** pantalla nueva que abre la URL del visor de la obra, en horizontal, inyectando antes de cargar la página `window.IEC_AUTH = {getToken, iniciales}` donde `getToken()` devuelve el ID token vigente de Firebase (el que ya usa Retrofit). Solo para el origen `https://iec-group011.github.io`, sin permitir navegar a otros sitios, y sin borrar los datos del WebView entre sesiones (la cola sin conexión vive ahí). Valora si compensa que el visor pase los cambios a la App y estos vayan por Room + WorkManager como el resto (ver §3b, «Alternativa futura»).
5. **Aviso de las 16:55:** Cloud Scheduler (Europe/Madrid) que llama a una ruta de administración protegida del BFF, que lee los `Días de obra` de hoy, toma el «Responsable del día» (si está vacío, todos los trabajadores de ese día), busca su usuario y envía push (FCM) a `Usuarios.TokenNotificaciones`. Texto: «Rellena los checks de hoy · <proyecto>»; al tocarla abre el plano de esa obra.
6. **Calendario de obra (opcional, aparte):** poder elegir el «Responsable del día» desde la interfaz «Calendario de obra».

## Comprobaciones al terminar
- Marcar un check sobre el plano en la App aparece en Airtable y en el visor (otro móvil) en menos de un minuto.
- Sin cobertura, el panel muestra «Sin enviar» y los cambios suben al volver la conexión, con su hora real.
- Con el token caducado el visor avisa y no pierde los cambios.
- Fuera de la App, el visor es de solo lectura.
- Un día sin obra no genera aviso; un día con obra y responsable distinto avisa solo a ese responsable.
- El JSON público no contiene nombres completos.
