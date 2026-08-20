# -*- coding: utf-8 -*-
"""Construye plan.json leyendo las carpetas de contenido y sus CAPTION.txt.

Aqui la fuente de verdad son las carpetas, no un Excel: cada una trae sus
imagenes numeradas en orden de subida y el texto listo. El formato se deduce
de cuantas imagenes hay, porque el conteo escrito en los CAPTION.txt viene
desfasado en la mayoria de las publicaciones.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONTENIDO = RAIZ / "contenido"
SALIDA = RAIZ / "plan.json"

MAX_CARRUSEL = 10

RE_CAPTION = re.compile(
    r"CAPTION\s*[—-]\s*copiar[^\n]*\n-+\n(.*?)\n-+\nFIN DEL CAPTION",
    re.S,
)
RE_TITULO = re.compile(r"^POST\s+\d+\s+de\s+\d+[^\n]*\n(.+)$", re.M)
RE_PILAR = re.compile(r"^Pilar:\s*(.+)$", re.M)
RE_CTA = re.compile(r"^CTA:\s*(.+)$", re.M)
RE_SEMANA = re.compile(r"^(Semana\s+.+)$", re.M)
RE_STORIES = re.compile(r"^STORIES DEL D[IÍ]A:\s*\n(.*?)(?:\n\s*\n|\Z)", re.M | re.S)
RE_CARPETA = re.compile(r"^(\d+)_(\d{4}-\d{2}-\d{2})_(.+)$")


def leer(carpeta):
    texto = (carpeta / "CAPTION.txt").read_text(encoding="utf-8")

    m = RE_CAPTION.search(texto)
    if not m:
        raise ValueError(f"{carpeta.name}: no encuentro el bloque CAPTION")

    def uno(rx):
        r = rx.search(texto)
        return r.group(1).strip() if r else None

    stories = uno(RE_STORIES)
    if stories:
        stories = " ".join(l.strip() for l in stories.splitlines() if l.strip())

    return {
        "caption": m.group(1).strip(),
        "tema": uno(RE_TITULO),
        "pilar": uno(RE_PILAR),
        "cta": uno(RE_CTA),
        "semana": uno(RE_SEMANA),
        "stories": stories,
    }


def main():
    publicaciones = []
    for carpeta in sorted(CONTENIDO.iterdir()):
        if not carpeta.is_dir():
            continue
        m = RE_CARPETA.match(carpeta.name)
        if not m:
            print(f"  aviso: '{carpeta.name}' no sigue el patron NN_fecha_tema, la salto")
            continue
        numero, fecha, _ = m.groups()

        imagenes = sorted(carpeta.glob("*.jpg"))
        datos = leer(carpeta)

        item = {
            "fecha": fecha,
            "numero": int(numero),
            "formato": "carrusel" if len(imagenes) > 1 else "imagen",
            "pilar": datos["pilar"],
            "semana": datos["semana"],
            "cta": datos["cta"],
            "tema": datos["tema"],
            "stories": datos["stories"],
            "carpeta": carpeta.name,
            "caption": datos["caption"],
            # El paquete no trae texto alternativo; el publicador lo omite.
            "alt_text": None,
            "medios": [f"medios/{carpeta.name}/{i.name}" for i in imagenes],
            "portada": None,
            "listo": True,
            "motivo": None,
        }

        if not imagenes:
            item.update(listo=False, motivo="la carpeta no tiene imagenes")
        elif len(imagenes) > MAX_CARRUSEL:
            item.update(listo=False,
                        motivo=f"un carrusel admite {MAX_CARRUSEL} laminas, hay {len(imagenes)}")

        publicaciones.append(item)

    publicaciones.sort(key=lambda p: p["fecha"])
    plan = {
        "cuenta": "eFactil",
        "zona": "America/Santo_Domingo",
        "hora": "18:00",
        "total": len(publicaciones),
        "listas": sum(1 for p in publicaciones if p["listo"]),
        "publicaciones": publicaciones,
    }
    SALIDA.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"plan.json escrito · {plan['total']} publicaciones · {plan['listas']} publicables")
    print(f"  del {publicaciones[0]['fecha']} al {publicaciones[-1]['fecha']}")
    formatos = {}
    for p in publicaciones:
        formatos[p["formato"]] = formatos.get(p["formato"], 0) + 1
    print(f"  formatos: {formatos}")
    for p in publicaciones:
        if not p["listo"]:
            print(f"  NO PUBLICABLE {p['fecha']} · {p['motivo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
