"""Locate new tile-edge discontinuities; visual aid, not an art-quality score."""

import argparse, json
from pathlib import Path
import numpy as np
from PIL import Image


def audit(source, candidate, output):
    output.mkdir(parents=True, exist_ok=True)
    src = Image.open(source).convert("RGB")
    im = Image.open(candidate).convert("RGB")
    assert src.size == im.size
    s = np.rint(np.asarray(src, dtype=float) * 31 / 255) * 8
    c = np.asarray(im, dtype=float)
    h, w = s.shape[:2]
    residual = c - s
    heat = np.zeros((h, w))
    edges = []
    for axis in [0, 1]:
        for coord in range(8, s.shape[axis], 8):
            a = np.take(residual, coord - 1, axis=axis)
            b = np.take(residual, coord, axis=axis)
            # New contrast caused by quantization, above source contrast.
            delta = np.sqrt(((a - b) ** 2).mean(1))
            sa = np.take(s, coord - 1, axis=axis)
            sb = np.take(s, coord, axis=axis)
            ca = np.take(c, coord - 1, axis=axis)
            cb = np.take(c, coord, axis=axis)
            excess = np.maximum(
                0, np.sqrt(((ca - cb) ** 2).mean(1)) - np.sqrt(((sa - sb) ** 2).mean(1))
            )
            edges.append(
                {
                    "axis": "horizontal" if axis == 0 else "vertical",
                    "coordinate": coord,
                    "meanResidualJump": float(delta.mean()),
                    "meanAddedContrast": float(excess.mean()),
                    "worstPixel": int(excess.argmax()),
                }
            )
            if axis == 0:
                heat[coord] = excess
            else:
                heat[:, coord] = np.maximum(heat[:, coord], excess)
    view = np.asarray(im).copy()
    flag = heat > 12
    view[flag] = [255, 48, 192]
    Image.fromarray(view).resize((w * 4, h * 4), Image.Resampling.NEAREST).save(
        output / "seams-4x.png"
    )
    np.save(output / "added-contrast.npy", heat)
    report = {
        "candidate": str(candidate.resolve()),
        "flaggedBoundaryPixels": int(flag.sum()),
        "threshold": 12,
        "edges": sorted(edges, key=lambda v: v["meanAddedContrast"], reverse=True),
        "note": "Flags require visual interpretation; intentional stepped shading can also be flagged.",
    }
    (output / "seams.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    r = audit(a.source, a.candidate, a.output)
    print(json.dumps({"flaggedBoundaryPixels": r["flaggedBoundaryPixels"]}))
