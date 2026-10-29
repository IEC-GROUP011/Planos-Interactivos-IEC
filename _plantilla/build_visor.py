#!/usr/bin/env python3
"""Genera el visor de un proyecto a partir de la plantilla.

Uso:  python3 _plantilla/build_visor.py <carpeta_proyecto>

La carpeta debe contener `data.json` (zonas + `cfg`) y `img/` con los planos.
Escribe `<carpeta_proyecto>/index.html` con los datos y el checklist de
`_plantilla/checklists.json` según `cfg.kind` ("fotovoltaica" | "electrica").
"""
import json, sys, html
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def main(carpeta: str) -> None:
    proyecto = Path(carpeta).resolve()
    datos = json.loads((proyecto / "data.json").read_text(encoding="utf-8"))
    cfg = datos.setdefault("cfg", {})
    kind = cfg.get("kind")
    if kind not in ("fotovoltaica", "electrica"):
        sys.exit('data.json: cfg.kind debe ser "fotovoltaica" o "electrica"')

    if "checklist" not in cfg and cfg.get("checklist") is not False:
        cl = json.loads((AQUI / "checklists.json").read_text(encoding="utf-8"))[kind]
        cfg["checklist"] = [{"id": c["id"], "label": c["label"]} for c in cl["checks"]]
        cfg["checklistProvisional"] = bool(cl.get("provisional"))
    elif cfg.get("checklist") is False:
        cfg["checklist"] = []

    if cfg.get("modo") not in (None, "lectura", "demo"):
        sys.exit('data.json: cfg.modo debe ser "lectura" o "demo"')

    plantilla = (AQUI / "template.html").read_text(encoding="utf-8")
    if "__DATA__" not in plantilla:
        sys.exit("template.html no contiene el marcador __DATA__")
    salida = plantilla.replace("__DATA__", json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
    titulo = cfg.get("title")
    if titulo:
        salida = salida.replace("<title>Visor de planos Ónice</title>", f"<title>{html.escape(titulo)}</title>")
    # La plantilla es un fragmento: el publicado necesita documento completo
    if not salida.lstrip().lower().startswith("<!doctype"):
        salida = '<!doctype html>\n<html lang="es"><head><meta charset="utf-8">' \
                 '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + salida
        # el <title> y los <link>/<style> ya van al principio de la plantilla; cerramos <head> antes del <header>
        salida = salida.replace("</style>\n\n<header", "</style></head><body>\n<header", 1)
        salida += "\n</body></html>\n"
    (proyecto / "index.html").write_text(salida, encoding="utf-8")
    print(f"OK {proyecto/'index.html'}  ({kind}, {len(cfg.get('checklist', []))} checks)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
