#!/usr/bin/env python3
"""One-off: extract images from sidekickpics.pdf into Assets/*.jpg"""
import io
import os
import sys

import fitz
from PIL import Image

PDF = os.path.join(os.path.dirname(__file__), "sidekickpics.pdf")
OUT = os.path.join(os.path.dirname(__file__), "Assets")


def pil_from_fitz_image(doc, xref: int) -> Image.Image:
    base = doc.extract_image(xref)
    raw = base["image"]
    im = Image.open(io.BytesIO(raw))
    if im.mode == "CMYK":
        im = im.convert("RGB")
    elif im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        im = bg
    elif im.mode == "P":
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if "transparency" in im.info or im.mode == "RGBA":
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[3])
        else:
            bg.paste(im)
        im = bg
    else:
        im = im.convert("RGB")
    return im


def main() -> int:
    if not os.path.isfile(PDF):
        print(f"Missing: {PDF}", file=sys.stderr)
        return 1
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(PDF)
    n = 0
    for pno in range(len(doc)):
        page = doc[pno]
        for img in page.get_images():
            n += 1
            xref = img[0]
            im = pil_from_fitz_image(doc, xref)
            path = os.path.join(OUT, f"sidekick_photo_{n:03d}.jpg")
            im.save(path, "JPEG", quality=92, optimize=True)
            print(path, "—", im.size[0], "×", im.size[1])

    # Page 3 had no Image XObjects; export full page render if present
    for pno, dpi in ((2, 200),):
        if len(doc) <= pno:
            break
        page = doc[pno]
        if page.get_images():
            continue
        pm = page.get_pixmap(dpi=dpi, alpha=False)
        im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
        n += 1
        path = os.path.join(OUT, f"sidekick_photo_{n:03d}.jpg")
        im.save(path, "JPEG", quality=90, optimize=True)
        print(path, f"— (rendered p.{pno + 1} @ {dpi}dpi)", im.size[0], "×", im.size[1])
    print(f"Done. {n} file(s) in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
