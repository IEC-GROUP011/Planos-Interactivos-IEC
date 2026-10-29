# Encargo para Claude Code: checks diarios de avance de obra en la App IEC

Lee primero `_plantilla/ESPECIFICACION_APP_IEC.md` (rama `checklists-obra` de IEC-GROUP011/Planos-Interactivos-IEC) y `_plantilla/checklists.json`. Esta es la parte de la App y de Airtable; el visor de planos ya está hecho y solo lee.

## Decisiones ya tomadas
- Los checks los marca el **instalador** en la App IEC (no en el visor), en el nivel más concreto: estancia (eléctrica) o cubierta (fotovoltaica).
- A las **16:55 (Europe/Madrid)**, en días de obra, la App manda una notificación push al **responsable del día**, que **cambia cada día** según quién vaya a la obra.
- El avance se guarda en Airtable (base IEC, `app8fKFbJcGwBqDMY`); la App escribe, el visor lee.

## Tareas
1. **Airtable**
   - Tabla nueva «Avance de obra»: Proyecto (enlace a Proyectos), Fecha, Zona (texto, `<nivel1>/<nivel2>`), Check (texto, id de `checklists.json`), Hecho (casilla), Responsable (enlace a Usuarios), Registrado el (fecha de creación).
   - Campo nuevo en `Días de obra`: «Responsable del día» (enlace a un solo Trabajador, elegido entre «Trabajadores disponibles» de ese día).
   - Comprobar qué valor de «Tipo proyecto» o «Tipo Instalación» distingue eléctrica de fotovoltaica y usarlo para elegir el checklist.
2. **Pantalla de checks en la App** (pensada para móvil en horizontal y con guantes): lista de zonas de la obra, fichas grandes de 44 px o más por check, «Marcar todo», botón «Guardar N cambios». Solo crea registro si el estado cambia respecto al vigente. Guardar en local (Room) y sincronizar al recuperar cobertura, con la hora real de marcado.
3. **Endpoint de lectura** `GET /avance?obra=<id>` con el JSON de la sección 3 de la especificación (estado vigente = último registro por Proyecto + Zona + Check; `by` con iniciales de `Trabajadores.Iniciales`; CORS abierto solo a `https://iec-group011.github.io`).
4. **Aviso de las 16:55:** tarea programada (o Automation de Airtable que llame a la App; elige lo que encaje con el backend actual y dime cuál) que lee los `Días de obra` de hoy, toma el «Responsable del día» (si está vacío, todos los trabajadores de ese día), busca su usuario y envía push (FCM) a `Usuarios.TokenNotificaciones`. Texto: «Rellena los checks de hoy · <proyecto>»; al tocarla abre los checks de esa obra.
5. **Calendario de obra (opcional, aparte):** poder elegir el «Responsable del día» desde la interfaz «Calendario de obra».

## Comprobaciones al terminar
- Marcar un check en la App aparece en el visor en menos de un minuto.
- Sin cobertura, los cambios se guardan y suben después.
- Un día sin obra no genera aviso; un día con obra y responsable distinto avisa solo a ese responsable.
- El JSON público no contiene nombres completos.
