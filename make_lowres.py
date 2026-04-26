#!/usr/bin/env python3
"""Build Assets/LowRes from Assets/sidekick_photo_*.jpg — max long edge 1280px, web JPEG."""
import glob
import os
import sys

from PIL import Image

ASSETS = os.path.join(os.path.dirname(__file__), "Assets")
LOW = os.path.join(ASSETS, "LowRes")
MAX_SIDE = 1280
QUALITY = 82


def main() -> int:
    os.makedirs(LOW, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(ASSETS, "sidekick_photo_*.jpg")))
    paths = [p for p in paths if os.path.dirname(p) == ASSETS]
    if not paths:
        print("No sidekick_photo_*.jpg in Assets/", file=sys.stderr)
        return 1
    for path in paths:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        if max(w, h) > MAX_SIDE:
            if w >= h:
                nw, nh = MAX_SIDE, max(1, int(round(h * MAX_SIDE / w)))
            else:
                nh, nw = MAX_SIDE, max(1, int(round(w * MAX_SIDE / h)))
            im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        out = os.path.join(LOW, os.path.basename(path))
        im.save(
            out,
            "JPEG",
            quality=QUALITY,
            optimize=True,
            progressive=True,
            subsampling=1,
        )
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
