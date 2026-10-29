---
name: "planos-interactivos-iec"
description: "Crear y publicar un visor web interactivo de planos de una instalación eléctrica o fotovoltaica de IEC (general → edificio/planta → cubierta/estancia), con checklists de avance diario a la izquierda, y subirlo a GitHub Pages."
---

# Visor de planos interactivos IEC

Usar cuando el usuario (IEC Group, habla español) pida un visor de planos de una instalación: plano general → clic en un edificio o planta → plano de ese nivel → clic en una cubierta o estancia → plano de detalle. Debe verse bien en móvil y compartirse con los trabajadores. A la izquierda lleva un panel de checks para llevar el registro diario de avance de la obra.

## Paso 0: preguntar el tipo de instalación (siempre lo primero)
Antes de pedir nada más, preguntar con AskUserQuestion: **«¿La instalación es eléctrica o fotovoltaica?»**. De la respuesta salen `cfg.kind`, los niveles, los textos y el checklist:

| | Fotovoltaica (`fotovoltaica`) | Eléctrica (`electrica`) |
|---|---|---|
| Niveles | Implantación → Edificio → Cubierta | Plano general → Planta → Estancia |
| Color de zona | Por tipo de edificio | Por planta |
| Checklist (nivel más concreto) | Cubierta | Estancia |

**Los nombres y el número de zonas (edificios, plantas, cubiertas, estancias) salen siempre de los planos que dé el usuario**; nunca asumir los de los ejemplos (Cine, Hall, P.S.…, que son solo ilustrativos).

Los checks son prácticamente idénticos entre instalaciones del mismo tipo; viven en `_plantilla/checklists.json` (fuente única, también para la App IEC). **Los checklists de ambos tipos están aún por determinar**: los actuales son provisionales (el eléctrico es un mock) y el visor muestra «Checklist provisional». Avisar al usuario cada vez que se use; si da la lista definitiva, actualizar `checklists.json` y poner `provisional: false`.

## Entradas que hay que pedir
Comunes: PDF del plano general; PDF con el plano de cada nivel intermedio; PDFs de detalle (una página por cubierta o estancia); cómo se nombran las zonas; si hay varios juegos (estructuras, strings), plantear un selector.
- **Fotovoltaica:** edificios marcados por colores (mismo color = mismo tipo, distinta colocación). Colores usados en Ónice: tipo 1 azul #2776BB, tipo 2 verde #129C47, tipo 3 rojo #E5242A, tipo 4 amarillo #E4C400.
- **Eléctrica:** plantas (o zonas) del plano general y las estancias de cada planta, con los nombres que figuren en los planos. Pedir también si hay plano de detalle por estancia; si no, usar la hoja de la planta.

## Dónde está el código
Repositorio GitHub `IEC-GROUP011/Planos-Interactivos-IEC` (si no está en la sesión, añadirlo con acceso de escritura):
- `_plantilla/template.html`: visor completo; marcador `__DATA__` para el JSON.
- `_plantilla/build_visor.py`: `python3 _plantilla/build_visor.py <carpeta>` genera `<carpeta>/index.html` desde `<carpeta>/data.json` e inyecta el checklist.
- `_plantilla/checklists.json`: checklists por tipo. `_plantilla/ESPECIFICACION_APP_IEC.md`: tabla de Airtable, lectura del avance y aviso diario. `_plantilla/LEEME.md`: formato de `data.json`.
- `_plantilla/ejemplo-onice/` (FV real) y `_plantilla/ejemplo-electrica-mock/` (eléctrica con planos inventados; `build_mock.py` lo regenera).
- Cada proyecto va en su carpeta (`onice/`, …) y se enlaza desde el `index.html` de la portada.
URL base: https://iec-group011.github.io/Planos-Interactivos-IEC/<carpeta>/

## Método
1. Hojas A3 de 1191×842 pt. Renderizar cada página a WebP (ligero, total < 5 MB) en `img/`: `general_1`, `edif_<tipo>`, `t<tipo>_<n>` (o el nombre que se ponga en `img` de cada zona).
2. Extraer zonas pulsables de los vectores del PDF con PyMuPDF (`get_drawings()`): polígonos del nivel 1 en el general y del nivel 2 en el plano de cada edificio/planta. Coordenadas en pt de la hoja. Si el PDF no trae vectores útiles, dibujar los polígonos a mano sobre la imagen.
3. Registrar planos entre sí (el plano de edificios puede estar ESPEJADO respecto a los minimapas): volteo horizontal, template matching con OpenCV, reglas de posición.
4. Comprobar que los detalles corresponden a la zona correcta por patrón (no por nombre de archivo). En Ónice TIPO1 y TIPO2 venían cruzados: se resuelve con `cfg.dt` (`{"1":2,"2":1}`).
5. Generar `data.json` con `cfg` (`kind`, `title`, `site`, `obraId`, `progressUrl`, `modo`), `buildings` (`{id,tipo,col,poly,lab}`) y `tipos` (`{cubs:[{id,n,img,poly,lab}]}`). Formato completo en `LEEME.md`. Ejecutar `build_visor.py`.
6. Probar con Playwright (Chromium instalado; no ejecutar `playwright install`): escritorio y móvil 390×780 táctil; recorrer general → nivel 1 → nivel 2; con y sin avance; en móvil desplegar el panel de checks; sin desbordamiento horizontal ni errores JS (los fallos de Google Fonts en el sandbox no cuentan). Revisar capturas.
7. Publicar: copiar a la carpeta del proyecto, actualizar la portada, `git commit` + `git push` a `main` (GitHub Pages publica solo). **Pedir confirmación antes de empujar a `main`**: el repositorio es público.

## Checks de avance diario
- **Panel izquierdo** (ocultable con «Ocultar checks»): en el último nivel muestra el checklist de la cubierta/estancia con quién y cuándo lo marcó; en los niveles superiores muestra el avance agregado (total y por check). Las zonas llevan una barra de avance bajo su etiqueta. En móvil el panel es un cajón plegable bajo el plano.
- **Quién escribe:** la App IEC (aviso a las 16:55 al responsable de obra, en días de obra) escribe en Airtable. El visor solo **lee** `cfg.progressUrl` (cada minuto). No poner nunca claves de Airtable en el visor. `cfg.modo: "demo"` permite marcar solo para pruebas (guarda en el navegador).
- **Clave de zona** del avance: `<id nivel 1>/<id nivel 2>` (p. ej. `1.1/1.4`, `P.S./CINE`). Las cubiertas con el mismo id en edificios distintos no se mezclan.
- Detalle (tabla «Avance de obra», formato del JSON, aviso 16:55 y pantalla en la App): `ESPECIFICACION_APP_IEC.md`.
- Cambiar el checklist: editar `checklists.json` y volver a ejecutar `build_visor.py`; no cambiar los `id` de checks con registros.

## Características del visor (mantener)
- Zoom animado, arrastre, pellizco, doble toque, rueda; teclado (Esc/atrás, flechas, +/−/0, F).
- Panel lateral derecho con lista (en móvil pasa a tira horizontal bajo el plano) y botón Mostrar/Ocultar panel.
- Pantalla completa (API real; en iPhone, pseudo-pantalla completa) con menú de navegación compacto arriba a la derecha (atrás + «Subir a» y lista).
- Sin texto de ayuda sobre el plano. Enlaces profundos `#e<nivel1>` y `#e<nivel1>_c<nivel2>`.
- Carga robusta (timeouts de decodificación, mensaje de error); si falla la lectura del avance el visor sigue funcionando.

## Avisos
- El repositorio y el visor son públicos: cualquiera con el enlace ve los planos y el avance. El avance publicado va con iniciales, sin nombres completos. Avisar si un proyecto es sensible.
- No se puede activar GitHub Pages ni crear repositorios desde la sesión; ya está hecho para este repositorio.
- Los recuadros y minimapas dentro de los PDFs conservan sus etiquetas/colores originales; avisar de ello.
- Entregar siempre al final el enlace público y pedir que lo prueben en un móvil real.
