# Especificación para la App IEC: checks diarios de avance de obra

Estado: **propuesta** (29/10/2026). El checklist **eléctrico** es el dado por IEC (29/10/2026); el **fotovoltaico** está aún por determinar y es provisional. El visor ya lee el avance; falta implementar el resto en la App IEC (Claude Code) y en Airtable.

## Reparto de responsabilidades
- **App IEC**: avisa a las 16:55, abre el visor de planos de la obra identificando al usuario, y **escribe** el avance en Airtable (a través de un endpoint propio; el visor nunca lleva claves de Airtable).
- **Airtable (base IEC)**: guarda el registro diario.
- **Visor de planos (GitHub Pages)**: **lee** el avance y lo pinta (panel izquierdo y barras sobre los planos). Dentro de la App (con token) el instalador **marca los checks sobre el plano** y el visor envía cada cambio a la App. Fuera de la App es de solo lectura.

## 1. Checklists (fuente única: `_plantilla/checklists.json`)
- Fotovoltaica (provisional, borrador de la pizarra): Replanteo, Perforaciones + pernos, Estructura, Cableado (optimizadores), Paneles. Pendiente confirmar el «opt» de la pizarra.
- Eléctrica (dada por IEC, 29/10/2026): Tubo, Caja, Cable, Mecanismos, Embellecedores, Luminarias, Cajetines.
- Se marcan en el **nivel más concreto**: cubierta (FV) o estancia (eléctrica). El avance de edificio/planta y el total de la obra se calculan sumando.
- Los nombres de zona (edificios, plantas, cubiertas, estancias) **no están fijados aquí**: salen de los planos de cada proyecto. Los de los ejemplos (Cine, Hall…) son solo ilustrativos.
- Mientras el checklist esté por determinar, se puede cambiar libremente; una vez haya registros en Airtable, los `id` de los checks no se cambian (solo se añaden o se renombran etiquetas).

## 2. Tabla nueva «Avance de obra» (registro, un registro por cambio)
| Campo | Tipo | Notas |
|---|---|---|
| Proyecto | Enlace a Proyectos | La obra |
| Fecha | Fecha | Día al que corresponde el registro |
| Zona | Texto | `<nivel 1>/<nivel 2>`: `1.1/1.4` (edificio/cubierta) o `P.S./CINE` (planta/estancia) |
| Check | Texto | `id` de `checklists.json` (`replanteo`, `tubo`…) |
| Hecho | Casilla | Marcado o desmarcado |
| Responsable | Enlace a Usuarios o Trabajadores | Quien rellena (el que use la App para iniciar sesión) |
| Registrado el | Fecha de creación | Automático |

- **Estado vigente** de un check = último registro por (Proyecto, Zona, Check). Así se conserva el historial diario y el visor siempre ve lo último.
- **Quién marca:** el **instalador**, **sobre el plano interactivo abierto dentro de la App IEC** (decidido 29/10/2026; no hay pantalla de checks aparte). Fuera de la App el visor es solo de lectura. Cualquier trabajador asignado a la obra ese día puede abrir la pantalla de checks; `Responsable` guarda el usuario que inició sesión.
- **Responsable del día** (quien recibe el aviso de las 16:55; decidido 29/10/2026: **cambia según el día**, porque a la obra van personas distintas): campo nuevo «Responsable del día» (enlace a un solo Trabajador) en `Días de obra`. Se elige entre los trabajadores de ese día (`Trabajadores disponibles`) y se puede fijar desde la interfaz «Calendario de obra» al asignar trabajadores. No hay responsable fijo en `Proyectos`. Si el campo queda vacío, el aviso va a todos los trabajadores de ese día de obra.
- Para decidir el checklist (eléctrica o fotovoltaica) se puede usar «Tipo proyecto» de Proyectos (o «Tipo Instalación» de Días de obra, que ya viene de Proyecto). Hay que confirmar sus valores.

## 3. Lectura para el visor
`GET <URL de la App>/avance?obra=<id>` → JSON (sin autenticación, con CORS abierto a `https://iec-group011.github.io`):

```json
{
  "obra": "EJEMPLO-ELECTRICA",
  "updated": "2026-10-29T16:58:00+01:00",
  "zones": {
    "P.S./CINE": {
      "replanteo": {"done": true, "by": "J.", "date": "2026-10-29"},
      "tubo": {"done": false}
    }
  }
}
```
- En `data.json` del proyecto: `cfg.progressUrl` apunta a ese endpoint (en los ejemplos es un `progress.json` estático).
- **Privacidad:** el visor es público. `by` debe ir con iniciales o vacío, nunca el nombre completo ni datos personales.
- El visor vuelve a leer cada minuto y al volver a la pestaña.

## 4. Aviso diario a las 16:55
- Tarea programada diaria a las **16:55, zona horaria Europe/Madrid** (no UTC, para que respete el cambio de hora).
- Solo se envía si el proyecto tiene un **Día de obra** ese día (tabla «Días de obra»: Proyecto + «Día de obra») y su tipo de instalación tiene checklist.
- Destinatario: el **Responsable del día** (ver §2); si no hay, los trabajadores asignados a ese día de obra. Notificación push de la App IEC.
- Cómo llega: `Usuarios` ya tiene `FirebaseUid` y `TokenNotificaciones`, así que la App usa Firebase. El aviso lo manda una tarea programada en el backend de la App (p. ej. Cloud Scheduler + Cloud Function, Europe/Madrid) que lee `Días de obra` de hoy, busca el usuario del responsable (`Usuarios` → `Trabajador`) y envía el push (FCM) a su `TokenNotificaciones`. Alternativa: una Automation de Airtable programada a las 16:55 que llame a un endpoint de la App. Claude Code debe comprobar cuál encaja con el backend actual.
- Un solo token por usuario (`TokenNotificaciones` es un texto): si cambia de móvil, se actualiza al iniciar sesión.
- Texto propuesto: «Rellena los checks de hoy · <nombre del proyecto>». Al tocarla abre el plano de esa obra dentro de la App.
- Abierto a decidir: recordatorio si a una hora fijada no hay ningún registro del día.

## 3b. Escritura desde el visor (dentro de la App)
El visor ya está preparado (rama `checklists-obra`). En `data.json`: `cfg.modo: "escritura"`, `cfg.writeUrl: "<URL de la App>/avance"` y `cfg.progressUrl` (lectura).
- **Identificación:** la App abre el visor en un WebView e **inyecta antes de cargar la página** `window.IEC_AUTH = {token: "<token corto del usuario>", iniciales: "J."}` (en Android, p. ej. `WebViewCompat.addDocumentStartJavaScript`). Sin `IEC_AUTH` el visor es de solo lectura y avisa «abre el plano desde la App IEC». El token debe ser de corta duración y limitado a escribir avance; nunca la clave de Airtable.
- **Qué envía** (un `POST` JSON por cambio, con `Authorization: Bearer <token>`):
  ```json
  {"obra": "EJEMPLO-ELECTRICA", "zona": "P.S./CINE", "check": "tubo", "done": true, "ts": "2026-10-29T13:36:17.031Z"}
  ```
  `ts` es la hora real del marcado (en el móvil). La App responde `200` si lo acepta. El servidor **no debe fiarse de nada más que del token** para saber quién es: el `Responsable` y las iniciales salen del usuario del token. Debe ser idempotente (mismo `obra`+`zona`+`check`+`ts` no duplica).
- **Códigos:** `401/403` → el visor muestra «la sesión ha caducado» y conserva los cambios; `5xx`, `429` o sin conexión → los cambios quedan en una cola en el móvil y se reintentan cada 20 s, al volver la conexión y al volver a la app; otro `4xx` → se descarta ese cambio (datos inválidos).
- **Cola sin conexión:** se guarda en el almacenamiento del WebView (`localStorage`). La App no debe borrar los datos del WebView entre sesiones. El panel muestra «Sin enviar» en cada check pendiente y cuántos faltan.
- **CORS:** el endpoint debe aceptar `POST` con `Authorization` desde `https://iec-group011.github.io` (preflight `OPTIONS`).
- **Aviso 16:55 → abrir el plano:** la notificación abre el visor de esa obra, preferiblemente en la estancia o planta que toque (`#e<nivel1>_c<nivel2>`).

## 5. Marcar sobre el plano (uso en obra)
1. El instalador abre el plano de la obra desde la App, en el móvil en horizontal, y toca la estancia (o la cubierta).
2. A la izquierda aparecen los checks de esa zona con casillas de 44 px; los marca tocándolos. Cada toque se envía solo, sin botón «Guardar».
3. En pantalla completa, los checks salen en un cajón a la izquierda del plano.
4. El avance de planta/edificio y el total de la obra se actualizan al momento.

## Pendiente de confirmar
- Lista definitiva de checks **fotovoltaicos**, incluido el significado de «Cableado : opt» de la pizarra. En eléctrica, confirmar si la lista dada («en general») es la definitiva o puede variar por obra.
- Resuelto: los checks los marca el instalador **sobre el plano**, dentro de la App (WebView con token). No hay pantalla de checks separada.
- Resuelto: el responsable cambia cada día (campo en `Días de obra`). Falta decidir si la interfaz «Calendario de obra» lo pide al crear el día o se rellena a posteriori.
- La «Tornillería gral» de la pizarra (6Ø, 8Ø, arandelas, tuercas, tirafondos, tacos): no se ha incluido; parece un listado de material por obra, no un check.
