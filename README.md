# eFactil · Publicador automático de Instagram

Publica una pieza al día, sola, a las **6:00 PM hora de República Dominicana**,
de lunes a viernes, del 20 de agosto al 23 de octubre de 2026.

Es el mismo sistema que corre para Hipocratech, en repositorio aparte: cada
cuenta de Instagram necesita su propio token, su propio calendario y su propio
alojamiento de medios.

---

## El material

| | |
|---|---|
| Publicaciones | **47**, del 20 ago al 23 oct |
| Cadencia | lunes a viernes, sin fines de semana |
| Formatos | 33 carruseles (6 a 10 láminas) + 14 imágenes únicas |
| Imágenes | 248, todas 1080×1350 y ya en JPEG |
| Videos | ninguno |

Las 1080×1350 dan exactamente 4:5, el límite del rango que acepta Instagram.
No las recortes más.

### Dos cosas que conviene saber

**El conteo de láminas escrito en los `CAPTION.txt` viene desfasado.** Casi
todos declaran una lámina menos de las que hay. La línea `Imágenes (N)` sí
coincide con los archivos reales en las 47, así que el plan se construye
contando los archivos, no leyendo el formato declarado.

**No hay texto alternativo.** El paquete no lo trae. Se publica sin él, que es
una pérdida de accesibilidad y de SEO. Se puede añadir después: cada
`CAPTION.txt` incluye el texto de cada lámina, que es buena materia prima.

---

## Cómo está organizado

```
plan.json                       las 47 publicaciones normalizadas
estado.json                     qué se publicó y cuándo (evita republicar)
medios/                         los JPEG servidos a Instagram por Pages
contenido/                      material fuente (no se sube al repo)

herramientas/construir_plan.py   carpetas + CAPTION.txt  →  plan.json
herramientas/revisar_token.py    avisa si el token está por caducar
herramientas/obtener_cuenta_id.py  averigua el IG_CUENTA_ID desde el token

publicador/api.py                cliente de la API de Instagram
publicador/publicar.py           publica lo que toca hoy

.github/workflows/publicar.yml   el cron diario
```

El plan se construye **solo desde las carpetas**, sin depender del Excel. La
fuente de verdad son los archivos.

---

## Las historias van a mano

La historia que enlaza a la publicación no se puede publicar por API: Meta no
permite elementos interactivos —sticker de publicación, enlaces, encuestas—
desde herramientas externas.

Al terminar de publicar, el sistema imprime el enlace, los pasos para
compartirla desde la app, **y la nota de «Stories del día» que trae el plan de
ese post**, que suele pedir una caja de preguntas o una encuesta concreta.

---

## Puesta en marcha

Necesitas el token y el ID de **esta** cuenta, no los de Hipocratech.

1. Genera el token en el [Explorador de la API de Graph](https://developers.facebook.com/tools/explorer/)
   con `instagram_basic`, `instagram_content_publish` y `pages_read_engagement`.
2. Saca el ID:

   ```bash
   python herramientas/obtener_cuenta_id.py
   ```

3. En **Settings → Secrets and variables → Actions**, los secrets `IG_TOKEN` e
   `IG_CUENTA_ID`, y la variable `URL_MEDIOS` con la URL de Pages.
4. Prueba desde **Actions → Run workflow** con `simular` en `true`.

El publicador detecta solo si el token es de Instagram Login (`IGA…`) o de
Facebook Login (`EAA…`) y habla con el host que corresponda.

---

## Cuando cambie el contenido

```bash
python herramientas/construir_plan.py
```

Luego copia las imágenes nuevas a `medios/` y haz commit.
