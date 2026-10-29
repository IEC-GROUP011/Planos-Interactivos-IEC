# Especificación para la App IEC: checks diarios de avance de obra

Estado: **propuesta** (29/10/2026). El checklist **eléctrico** es el dado por IEC (29/10/2026); el **fotovoltaico** está aún por determinar y es provisional. El visor ya lee el avance; falta implementar el resto en la App IEC (Claude Code) y en Airtable.

## Reparto de responsabilidades
- **App IEC**: avisa, muestra el checklist de la zona y **escribe** el avance en Airtable.
- **Airtable (base IEC)**: guarda el registro diario.
- **Visor de planos (GitHub Pages)**: solo **lee** el avance y lo pinta (panel izquierdo y barras sobre los planos). No lleva ninguna clave de Airtable.

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
- **Quién marca:** el **instalador**, desde la App IEC (decidido 29/10/2026). El visor es solo de lectura. Cualquier trabajador asignado a la obra ese día puede abrir la pantalla de checks; `Responsable` guarda el usuario que inició sesión.
- **Responsable del día** (quien recibe el aviso de las 16:55): hoy no existe en la base (`Proyectos` solo tiene «Responsable de Oferta» y «Contacto de obra»). Propuesta: campo «Responsable del día» (enlace a Trabajadores) en `Días de obra`, que se rellena por defecto con un «Responsable de obra» del proyecto (campo nuevo en `Proyectos`). Si queda vacío, el aviso va a todos los trabajadores de ese día de obra.
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
- Texto propuesto: «Rellena los checks de hoy · <nombre del proyecto>». Al tocarla abre la pantalla de checks de esa obra.
- Abierto a decidir: recordatorio si a una hora fijada no hay ningún registro del día.

## 5. Pantalla de checks en la App
1. Elegir zona (cubierta o estancia) de la obra; mostrar su estado vigente.
2. Lista de checks del tipo de instalación, con casillas grandes (uso con guantes y al sol).
3. Al marcar o desmarcar, crear un registro en «Avance de obra» solo si el estado cambia respecto al vigente.
4. Poder cambiar de zona sin salir (siguiente/anterior), como el paginador del visor.
5. **Sin cobertura:** guardar los cambios en el móvil (el proyecto Android ya usa Room) y sincronizar con Airtable al recuperar conexión; cada registro lleva su fecha y hora reales de marcado.

## Pendiente de confirmar
- Lista definitiva de checks **fotovoltaicos**, incluido el significado de «Cableado : opt» de la pizarra. En eléctrica, confirmar si la lista dada («en general») es la definitiva o puede variar por obra.
- Resuelto: los checks los marca el instalador en la **pantalla de la App**, no en el visor (que es de solo lectura; `cfg.modo: "demo"` solo es para pruebas).
- Si el «Responsable del día» es fijo por proyecto o cambia cada día (propuesta: campo por día con valor por defecto del proyecto).
- La «Tornillería gral» de la pizarra (6Ø, 8Ø, arandelas, tuercas, tirafondos, tacos): no se ha incluido; parece un listado de material por obra, no un check.
