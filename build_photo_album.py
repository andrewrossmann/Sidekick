#!/usr/bin/env python3
"""
Build docs/photo-album from Assets/LowRes with per-image rotation corrections.
Run from repo root: python3 build_photo_album.py
Requires: Pillow
"""
from __future__ import annotations

import glob
import os
import re
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
LOW = os.path.join(ROOT, "Assets", "LowRes")
OUT_DIR = os.path.join(ROOT, "docs", "photo-album", "images")
HTML_PATH = os.path.join(ROOT, "docs", "photo-album", "index.html")

# Per file (NNN in sidekick_photo_NNN.jpg): None = no rotation
# "cw" = 90° clockwise (PIL ROTATE_270), "ccw" = 90° counter-clockwise (PIL ROTATE_90)
# Based on visual review of LowRes exports (PDF had no EXIF).
ROTATION: dict[int, str | None] = {
    1: None,
    2: "cw",
    3: "cw",
    4: "cw",
    5: "cw",
    6: "cw",
    7: "cw",
    8: "cw",
    9: "cw",
    10: None,
    11: None,
    12: None,
    13: "cw",
    14: "cw",
    15: "cw",
    16: None,
    17: None,
    18: None,
    19: None,
    20: None,
    21: None,
}


def rotate(im: Image.Image, spec: str | None) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")
    if spec == "cw":
        return im.transpose(Image.Transpose.ROTATE_270)
    if spec == "ccw":
        return im.transpose(Image.Transpose.ROTATE_90)
    return im


def main() -> int:
    if not os.path.isdir(LOW):
        print(f"Missing {LOW}", file=sys.stderr)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(LOW, "sidekick_photo_*.jpg")))
    paths = [p for p in paths if os.path.dirname(p) == LOW]
    if not paths:
        print("No images in Assets/LowRes", file=sys.stderr)
        return 1

    entries: list[tuple[int, str, str]] = []
    for path in paths:
        m = re.search(r"sidekick_photo_(\d+)\.jpg$", os.path.basename(path))
        if not m:
            continue
        n = int(m.group(1))
        rot = ROTATION.get(n)
        im = Image.open(path)
        im = rotate(im, rot)
        out_name = f"sidekick_photo_{n:03d}.jpg"
        out_path = os.path.join(OUT_DIR, out_name)
        im.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
        entries.append((n, out_name, rot or "—"))
        print(out_path, rot or "straight")

    entries.sort(key=lambda x: x[0])
    _write_html(entries)
    print("Wrote", HTML_PATH)
    return 0


def _write_html(entries: list[tuple[int, str, str]]) -> None:
    items = []
    for n, fname, _ in entries:
        items.append(
            f"""    <figure class="shot">
      <a class="shot__link" href="images/{fname}" target="_blank" rel="noopener">
        <img src="images/{fname}" loading="lazy" alt="Sidekick photo {n}" />
      </a>
      <figcaption>Photo {n:02d}</figcaption>
    </figure>"""
        )
    blocks = "\n".join(items)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Sidekick — photo gallery of the mobile support bar in use." />
  <title>Sidekick — Photo album</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --ink: #0c1118;
      --muted: #475569;
      --accent: #0d9488;
      --accent2: #0f766e;
      --paper: #f1f5f4;
      --card: #fff;
      --line: #e2ddd4;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: "Outfit", system-ui, sans-serif;
      margin: 0;
      color: var(--ink);
      background: linear-gradient(180deg, #e0f2f1 0%, var(--paper) 35%, #faf9f6 100%);
      min-height: 100vh;
    }}
    header {{
      max-width: 72rem;
      margin: 0 auto;
      padding: clamp(1.5rem, 4vw, 2.5rem) 1.25rem 1rem;
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      justify-content: space-between;
      gap: 1rem;
    }}
    .wordmark {{ font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: #64748b; }}
    .wordmark span {{ color: var(--accent); }}
    h1 {{ font-size: clamp(1.6rem, 3.5vw, 2.1rem); font-weight: 700; letter-spacing: -0.03em; margin: 0.35rem 0 0.25rem; }}
    .lede {{ color: var(--muted); font-size: 1rem; line-height: 1.5; max-width: 32rem; margin: 0; }}
    .back {{ font-size: 0.9rem; font-weight: 600; }}
    .back a {{ color: var(--accent2); text-decoration: none; }}
    .back a:hover {{ text-decoration: underline; }}
    .gallery {{
      max-width: 72rem;
      margin: 0 auto;
      padding: 0.5rem 1.25rem 3rem;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
      gap: 1.25rem;
    }}
    .shot {{
      margin: 0;
      background: var(--card);
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid var(--line);
      box-shadow: 0 4px 20px rgba(20, 24, 33, 0.06);
    }}
    .shot__link {{ display: block; line-height: 0; background: #0a0a0a; }}
    .shot__link img {{
      width: 100%;
      height: auto;
      vertical-align: middle;
      object-fit: contain;
      max-height: 22rem;
    }}
    .shot figcaption {{
      padding: 0.65rem 0.9rem 0.85rem;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--muted);
      letter-spacing: 0.04em;
    }}
    footer {{
      text-align: center;
      font-size: 0.8rem;
      color: #94a3b8;
      padding: 0 1rem 2rem;
    }}
    @media print {{
      body {{ background: #fff; }}
      .shot {{ break-inside: avoid; box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <p class="wordmark">Side<span>kick</span></p>
      <h1>Photo album</h1>
      <p class="lede">When a cane is not enough and a rollator is too much — moments from development and use. Click an image to open the full file.</p>
    </div>
    <p class="back"><a href="../">← All documents</a></p>
  </header>
  <div class="gallery">
{blocks}
  </div>
  <footer>Patents pending · For discussion</footer>
</body>
</html>"""
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    raise SystemExit(main())
