# Plantilla del visor de planos IEC

- `template.html`: visor completo (HTML+CSS+JS). Placeholder `__DATA__` = JSON de zonas (ver `ejemplo-onice/data.json`).
  Cambiar el título, "Calle Ónice / Málaga · Autoconsumo FV" y la constante `DT` (cruce de planos detalle) por proyecto.
- Imágenes esperadas en `img/`: `general_1.webp`, `edif_<tipo>.webp`, `t<tipo>_<n>.webp` (hoja A3 1191x842 pt, coordenadas de zonas en esos puntos).
- `ejemplo-onice/build.py`: cómo se obtuvieron las zonas del proyecto Ónice (vectores del PDF con PyMuPDF; sirve de guía, tiene reglas propias de Ónice).
- Publicación: cada proyecto en su carpeta del repositorio + enlace en la portada `index.html`; GitHub Pages lo publica solo.
