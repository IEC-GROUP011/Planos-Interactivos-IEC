# Plantilla del visor de planos IEC (v2: eléctrica o fotovoltaica + checks de avance)

- `template.html`: visor completo (HTML+CSS+JS). El marcador `__DATA__` se sustituye por el JSON del proyecto.
- `build_visor.py`: `python3 _plantilla/build_visor.py <carpeta_proyecto>` lee `<carpeta>/data.json` y escribe `<carpeta>/index.html` (inyecta el checklist de `checklists.json` según `cfg.kind`).
- `checklists.json`: checklist de cada tipo de instalación (fuente única; la App IEC debe leer los mismos `id`). Eléctrica: lista dada por IEC (replanteo, tubo, caja, cable, mecanismos, embellecedores, luminarias, cajetines). Fotovoltaica: **aún por determinar (provisional)**; mientras lo sea, el panel muestra «Checklist provisional».
- `SKILL.md`: copia versionada de la skill `planos-interactivos-iec`.
- `ESPECIFICACION_APP_IEC.md`: tabla de Airtable, lectura del avance, aviso de las 16:55 y pantalla de checks.
- `ejemplo-onice/`: datos del proyecto fotovoltaico de Ónice (formato con **capas**, ver abajo) y `build_onice.py` + `geo.py`, que sacan bloques, cubiertas y strings del PDF (`python3 build_onice.py <salida>`; rutas del PDF dentro de `geo.py`).
- `ejemplo-electrica-mock/`: ejemplo eléctrico con planos y nombres de zona inventados (los nombres reales salen de los planos de cada proyecto) (`build_mock.py` lo regenera) y `progress.json` de prueba.

## `data.json`
```json
{"cfg": {"kind": "electrica", "title": "…", "site": {"name": "…", "sub": "…"},
         "obraId": "…", "progressUrl": "progress.json", "modo": "lectura",
         "dt": {"1": 2, "2": 1}},
 "buildings": [{"id": "P.S.", "tipo": "PS", "col": 3, "poly": [[x, y], …], "lab": [x, y]}],
 "tipos": {"PS": {"panels": 40, "cubs": [{"id": "CINE", "n": 8, "img": "img/PS_CINE.webp", "poly": […], "lab": […]}]}}}
```
- `kind`: `fotovoltaica` o `electrica` (cambia textos y checklist). Niveles: Implantación → Edificio → Cubierta (FV) o Plano general → Planta → Estancia (eléctrica).
- `col` (1–5): color de la zona (`--t1`…`--t5`); si falta se usa `tipo`. `img` opcional en edificio y cubierta/estancia; si falta, nombres `edif_<tipo>.webp` y `t<tipo>_<n>.webp`.
- `dt`: cruce de planos de detalle por tipo (solo si los PDF vinieron cruzados). Sin `cfg` se aplica el cruce antiguo de Ónice.
- `modo`: `lectura` (por defecto; el visor solo lee el avance), `demo` (permite marcar y guarda en el navegador, para pruebas) o `escritura` (dentro de la App IEC: con `window.IEC_AUTH` inyectado por la App se puede marcar y cada cambio se envía por `POST` a `cfg.writeUrl`; sin él, solo lectura). Ver `ESPECIFICACION_APP_IEC.md` §3b.
- `writeUrl`: endpoint `POST` de la App (obligatorio con `modo: "escritura"`).
  - Cada marca lleva `ts` (momento en que se pulsa) y `fecha` (`AAAA-MM-DD`, el **día del trabajo**). Por defecto es hoy; el selector «Día del trabajo» del panel permite elegir hasta 30 días atrás (nunca futuro) y avisa en color mientras está en un día pasado («… Hoy es 4 de noviembre.»); para volver, se elige hoy en el selector. No se guarda: al abrir el plano vuelve a hoy. El backend guarda `fecha` en «Fecha» de Avance de obra; manda la última marca por `ts`.
  - Mientras una marca se está enviando sale «Enviando…» con una rueda; «Sin enviar» solo si el último intento falló (sin conexión o servidor caído).
  - **Varias zonas a la vez:** en el nivel de bloque o planta, mantener pulsada una zona (medio segundo; en el ordenador, Ctrl/Mayús + clic) la selecciona; con la selección abierta, cada toque añade o quita zonas. El panel enseña cada check una vez con su estado en todas («2 de 3», casilla a medias) y al tocarlo se marca en las que falta, o se desmarca en todas si ya estaba en todas (una marca por zona, con el día del trabajo elegido). Para quitar una zona se vuelve a tocar; cambiar de plano (o Esc) borra la selección. El título del panel lo indica en azul («2 zonas seleccionadas»). No en la vista de strings.
  - **Con la App IEC 1.6.6 o posterior** (`IEC_AUTH.entregar` y `IEC_AUTH.pendientes`), el visor no envía: entrega cada marca a la App, que la guarda en su base de datos y la sube con WorkManager aunque se bloquee el móvil o se cierre el plano. El visor pregunta a la App qué tiene pendiente de la obra (cada 3 s mientras quede algo) y lo pinta encima del avance del servidor: «Enviando…» o «Guardado en el móvil · se subirá solo» (sin cobertura). Con apps anteriores, el visor sigue enviando él mismo.
- `imgV`: versión de las imágenes (p. ej. `"20261027"`); se añade como `?v=` a las URL para que nadie vea planos viejos en caché. Cambiarla cada vez que se sustituyan planos.
- `nm` (opcional, en cada edificio/planta): nombre visible (p. ej. `"nm": "Planta baja"` con `id: "PB"`); sin él se muestra `<l1> <id>`.
- Checks con `soloEn` (p. ej. `{"id": "cuadro", "label": "Cuadro eléctrico", "soloEn": ["PB/3"]}`): solo salen y cuentan en esas zonas (`<planta>/<zona>`).
- `detalleZoom: true` (solo sin capas): el último nivel no usa una imagen de detalle por zona; amplía la hoja de la planta sobre la zona (que queda marcada). Pensado para planos de alta resolución (p. ej. 3000 px renderizados desde el DXF) con zonas por estancia; en la planta las etiquetas que se pisan se ocultan hasta acercar el plano o pasar el ratón. Los ids de zona (nombre de la estancia) son la clave de los checks: no renombrarlos una vez haya avance registrado.
- `checklist: false` desactiva el panel de checks. Sin `progressUrl` el panel se muestra sin avance.
- Imágenes: hoja A3 de 1191×842 (coordenadas de zonas en esos puntos), en `img/`.
- Enlaces profundos: `#e<nivel1>` y `#e<nivel1>_c<nivel2>` (p. ej. `#eP.S._cCINE`).

## Capas (varios juegos de planos: Estructura / Paneles / Strings)
Cuando el PDF trae varios juegos de planos del mismo bloque, `cfg.capas` añade un selector sobre el plano y cambia qué hoja se ve en cada nivel:
```json
"cfg": {"capas": [{"id": "estructura", "label": "Estructura", "nivel": "cubierta"},
                  {"id": "paneles", "label": "Paneles", "nivel": "cubierta"},
                  {"id": "strings", "label": "Strings", "nivel": "string"}],
        "labels": {"l1": "Bloque", "l1p": "Bloques", "a1": "un bloque", "intro0": "Cada color es un edificio."},
        "marcos0": true},
"buildings": [{"id": "E1-1", "ed": "E1", "col": 1, "poly": […], "lab": […],
  "hojas": {"estructura": {"img": "img/est_E1-1.webp"},
            "paneles": {"img": "img/disp_E1.webp", "tf": [0.6, dx, dy]},
            "strings": {"img": "img/str_E1-1.webp", "items": ["S1", "S4", "S5", "S6"]}},
  "cubs": [{"id": "1", "n": 6, "poly": […], "lab": […], "det": {"estructura": "img/det_E1-1_1.webp"}}]}],
"strings": {"E1": [{"id": "S1", "n": 18}, …]}
```
- Las zonas de cubierta van en coordenadas de la hoja de estructura; `tf` = `[escala, dx, dy]` las lleva a otra hoja (p. ej. la disposición del edificio entero). Al abrir un bloque en esa capa, el plano se encuadra en sus cubiertas.
- Nivel cubierta: si la cubierta tiene `det[capa]`, se ve ese plano de detalle; si no, la hoja del bloque ampliada sobre la cubierta.
- Checks: un único «Completado» (con fecha y quién) por capa de nivel `cubierta`, con clave `<bloque>/<cubierta>` y check `<id de capa>` (p. ej. `E1-1/3` + `estructura`). Las capas de nivel `string` se marcan por string en el nivel del bloque, con clave `<edificio>/<string>` y check `string` para la capa `strings` o el id de la capa para las demás (p. ej. `E1/S4` + `cableado_cc`); un string que aparece en dos bloques es el mismo check. Las capas de nivel `edificio` se marcan una vez por edificio en el nivel del bloque (clave `<edificio>/edificio`, p. ej. `E1/edificio` + `inversor`) y las de nivel `obra` una sola vez en la implantación (clave `obra/general`). Qué capas lleva cada obra y a qué nivel depende de sus planos (p. ej. «Conexión vertido» va por inversor: por edificio si cada edificio tiene el suyo). Los ids no deben cambiar cuando ya hay registros en Airtable.
- `build_visor.py` genera `cfg.checklist` a partir de las capas de nivel `cubierta`.
- Una capa con `"plano": false` es solo un check (no sale en el selector), p. ej. `{"id": "optimizadores", "label": "Optimizadores", "nivel": "cubierta", "plano": false, "porPanel": true}`. `porPanel` muestra las unidades de la cubierta (una por panel).
- `marcos0`: dibuja el contorno de cada bloque en la implantación (cuando se han quitado los contornos de color del PDF).
- Enlaces profundos con capa: `#eE1-1_c3~paneles`.

## Publicación
Cada proyecto en su carpeta del repositorio + enlace en la portada `index.html`; GitHub Pages lo publica solo. El repositorio es público: el avance que lea el visor también lo es.
