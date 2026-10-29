#!/usr/bin/env python3
"""Genera el EJEMPLO ELÉCTRICO (planos inventados) para probar el visor.

Estructura de la pizarra del 29/10/2026: plano general -> plantas (P.B., P.A., P.S., Anexo)
-> estancias (Cine, Hall, Sauna, Salón, CGMP en P.S.). Los planos son rectángulos de prueba.
Uso: python3 build_mock.py   (escribe img/, data.json y progress.json junto al script)
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
(AQUI / "img").mkdir(exist_ok=True)
W, H = 1191, 842


def font(n):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, n)
        except OSError:
            pass
    return ImageFont.load_default()


def hoja(titulo):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, W - 20, H - 20], outline="#444", width=3)
    d.text((40, 32), titulo, fill="#444", font=font(22))
    d.text((W - 360, H - 56), "PLANO DE EJEMPLO (inventado)", fill="#999", font=font(18))
    return im, d


def caja(d, r, texto, relleno="#F3F5F8", t=26):
    d.rectangle(r, fill=relleno, outline="#222", width=3)
    d.text((r[0] + 14, r[1] + 10), texto, fill="#222", font=font(t), anchor="la")


def poly(r):
    x0, y0, x1, y1 = r
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def centro(r):
    return [round((r[0] + r[2]) / 2, 1), round((r[1] + r[3]) / 2, 1)]


# Plano general: cuatro bloques
BLOQUES = [("P.B.", "PB", 1, (140, 130, 560, 330)), ("P.A.", "PA", 2, (640, 130, 1060, 330)),
           ("P.S.", "PS", 3, (140, 450, 560, 650)), ("Anexo", "AN", 4, (640, 450, 1060, 650))]
# Estancias por planta (rectángulos en la hoja de la planta)
ESTANCIAS = {
    "PS": [("CINE", (400, 150, 800, 300)), ("HALL", (330, 300, 870, 440)), ("SAUNA", (140, 440, 560, 640)),
           ("SALON", (560, 440, 930, 640)), ("CGMP", (930, 520, 1080, 720))],
    "PB": [("RECIBIDOR", (140, 160, 480, 640)), ("COCINA", (480, 160, 820, 640)), ("GARAJE", (820, 160, 1060, 640))],
    "PA": [("DORM1", (140, 160, 480, 640)), ("DORM2", (480, 160, 820, 640)), ("BANO", (820, 160, 1060, 640))],
    "AN": [("TRASTERO", (140, 160, 600, 640)), ("TALLER", (600, 160, 1060, 640))],
}

im, d = hoja("PLANO GENERAL")
for ident, key, col, r in BLOQUES:
    caja(d, r, ident, t=34)
im.save(AQUI / "img" / "general_1.webp", quality=80)

buildings, tipos = [], {}
for ident, key, col, r in BLOQUES:
    buildings.append({"id": ident, "tipo": key, "col": col, "poly": poly(r), "lab": centro(r)})
    im, d = hoja(f"PLANTA {ident}")
    cubs = []
    for eid, er in ESTANCIAS[key]:
        caja(d, er, eid, t=24)
        cubs.append({"id": eid, "img": f"img/{key}_{eid}.webp", "poly": poly(er), "lab": centro(er)})
        im2, d2 = hoja(f"{ident} · {eid}")
        d2.rectangle([160, 140, W - 160, H - 140], outline="#222", width=4)
        d2.text((W / 2, H / 2), eid, fill="#222", font=font(64), anchor="mm")
        for i, nombre in enumerate(("Tubo", "Caja", "Cable")):
            d2.text((190, 170 + i * 34), "• " + nombre, fill="#777", font=font(20))
        im2.save(AQUI / "img" / f"{key}_{eid}.webp", quality=80)
    im.save(AQUI / "img" / f"edif_{key}.webp", quality=80)
    tipos[key] = {"cubs": cubs}

datos = {
    "cfg": {
        "kind": "electrica",
        "title": "Visor de planos · Ejemplo eléctrico",
        "site": {"name": "Ejemplo eléctrico", "sub": "Instalación eléctrica · planos inventados"},
        "obraId": "EJEMPLO-ELECTRICA",
        "progressUrl": "progress.json",
        "modo": "demo",
    },
    "buildings": buildings,
    "tipos": tipos,
}
(AQUI / "data.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")

progreso = {
    "obra": "EJEMPLO-ELECTRICA",
    "updated": "2026-10-29T16:58:00+01:00",
    "zones": {
        "P.S./CINE": {c: {"done": True, "by": "J.", "date": "2026-10-29"} for c in ("tubo", "caja", "cable")},
        "P.S./HALL": {"tubo": {"done": True, "by": "J.", "date": "2026-10-28"}},
        "P.S./SAUNA": {c: {"done": True, "by": "A.", "date": "2026-10-29"} for c in ("tubo", "caja", "cable", "mecanismos", "embellecedores", "luminarias", "cajetines")},
        "P.B./COCINA": {c: {"done": True, "by": "A.", "date": "2026-10-27"} for c in ("tubo", "caja")},
    },
}
(AQUI / "progress.json").write_text(json.dumps(progreso, ensure_ascii=False, indent=1), encoding="utf-8")
print("OK ejemplo eléctrico generado en", AQUI)
