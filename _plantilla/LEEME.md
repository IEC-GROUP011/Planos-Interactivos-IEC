# Plantilla del visor de planos IEC (v2: eléctrica o fotovoltaica + checks de avance)

- `template.html`: visor completo (HTML+CSS+JS). El marcador `__DATA__` se sustituye por el JSON del proyecto.
- `build_visor.py`: `python3 _plantilla/build_visor.py <carpeta_proyecto>` lee `<carpeta>/data.json` y escribe `<carpeta>/index.html` (inyecta el checklist de `checklists.json` según `cfg.kind`).
- `checklists.json`: checklist de cada tipo de instalación (fuente única; la App IEC debe leer los mismos `id`). Eléctrica: lista dada por IEC (tubo, caja, cable, mecanismos, embellecedores, luminarias, cajetines). Fotovoltaica: **aún por determinar (provisional)**; mientras lo sea, el panel muestra «Checklist provisional».
- `SKILL.md`: copia versionada de la skill `planos-interactivos-iec`.
- `ESPECIFICACION_APP_IEC.md`: tabla de Airtable, lectura del avance, aviso de las 16:55 y pantalla de checks.
- `ejemplo-onice/`: datos del proyecto fotovoltaico de Ónice (formato antiguo, sin `cfg`: sigue funcionando) y `build.py` con cómo se obtuvieron las zonas.
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
- `col` (1–4): color de la zona (`--t1`…`--t4`); si falta se usa `tipo`. `img` opcional en edificio y cubierta/estancia; si falta, nombres `edif_<tipo>.webp` y `t<tipo>_<n>.webp`.
- `dt`: cruce de planos de detalle por tipo (solo si los PDF vinieron cruzados). Sin `cfg` se aplica el cruce antiguo de Ónice.
- `modo`: `lectura` (por defecto; el visor solo lee el avance), `demo` (permite marcar y guarda en el navegador, para pruebas) o `escritura` (dentro de la App IEC: con `window.IEC_AUTH` inyectado por la App se puede marcar y cada cambio se envía por `POST` a `cfg.writeUrl`; sin él, solo lectura). Ver `ESPECIFICACION_APP_IEC.md` §3b.
- `writeUrl`: endpoint `POST` de la App (obligatorio con `modo: "escritura"`).
- `imgV`: versión de las imágenes (p. ej. `"20261027"`); se añade como `?v=` a las URL para que nadie vea planos viejos en caché. Cambiarla cada vez que se sustituyan planos.
- `checklist: false` desactiva el panel de checks. Sin `progressUrl` el panel se muestra sin avance.
- Imágenes: hoja A3 de 1191×842 (coordenadas de zonas en esos puntos), en `img/`.
- Enlaces profundos: `#e<nivel1>` y `#e<nivel1>_c<nivel2>` (p. ej. `#eP.S._cCINE`).

## Publicación
Cada proyecto en su carpeta del repositorio + enlace en la portada `index.html`; GitHub Pages lo publica solo. El repositorio es público: el avance que lea el visor también lo es.
