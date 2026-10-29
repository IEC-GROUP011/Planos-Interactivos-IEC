# Especificación para la App IEC: checks diarios de avance de obra

Estado: **propuesta** (29/10/2026). Los checklists de **ambos tipos (fotovoltaica y eléctrica) están aún por determinar**: los actuales son provisionales y se sustituirán por los definitivos. El visor ya lee el avance; falta implementar el resto en la App IEC (Claude Code) y en Airtable.

## Reparto de responsabilidades
- **App IEC**: avisa, muestra el checklist de la zona y **escribe** el avance en Airtable.
- **Airtable (base IEC)**: guarda el registro diario.
- **Visor de planos (GitHub Pages)**: solo **lee** el avance y lo pinta (panel izquierdo y barras sobre los planos). No lleva ninguna clave de Airtable.

## 1. Checklists (fuente única: `_plantilla/checklists.json`)
- Fotovoltaica (provisional, borrador de la pizarra): Replanteo, Perforaciones + pernos, Estructura, Cableado (optimizadores), Paneles. Pendiente confirmar el «opt» de la pizarra.
- Eléctrica (MOCK, provisional): Replanteo, Tubo y fijaciones, Cajas de distribución, Cajas de registro, Cableado.
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
- Hoy `Proyectos` no tiene un campo de **responsable de obra** (solo «Responsable de Oferta» y «Contacto de obra»). Hay que crear «Responsable de obra» (o definir de dónde sale: p. ej. de Asignaciones).
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
- Destinatario: el **Responsable de obra** del proyecto, por notificación de la App IEC.
- Texto propuesto: «Rellena los checks de hoy · <nombre del proyecto>». Al tocarla abre la pantalla de checks de esa obra.
- Abierto a decidir: recordatorio si a una hora fijada no hay ningún registro del día.

## 5. Pantalla de checks en la App
1. Elegir zona (cubierta o estancia) de la obra; mostrar su estado vigente.
2. Lista de checks del tipo de instalación, con casillas grandes (uso con guantes y al sol).
3. Al marcar o desmarcar, crear un registro en «Avance de obra» solo si el estado cambia respecto al vigente.
4. Poder cambiar de zona sin salir (siguiente/anterior), como el paginador del visor.

## Pendiente de confirmar
- Lista definitiva de checks, **fotovoltaica y eléctrica** (la eléctrica la pasa un compañero de obra). Incluye el significado de «Cableado : opt» de la pizarra.
- Si el responsable también marcará los checks **dentro del visor** (WebView en la App) además de en la pantalla propia. Hoy el visor es de solo lectura; `cfg.modo: "demo"` permite marcar pero solo guarda en el navegador (para pruebas).
- La «Tornillería gral» de la pizarra (6Ø, 8Ø, arandelas, tuercas, tirafondos, tacos): no se ha incluido; parece un listado de material por obra, no un check.
