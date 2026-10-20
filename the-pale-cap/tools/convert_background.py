"""Offline candidate conversion: RGB555 palettes with tile-boundary continuity.

Never writes game assets. Requires Pillow and NumPy. Supply a native-size RGB
source, output directory, and optional --continuity (default 1).
"""

import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

WEIGHTS = np.array([0.8, 1.3, 0.7])
UI = np.array([[8, 8, 24], [24, 64, 80], [48, 192, 200], [248, 232, 192]], dtype=float)


def rgb555(c):
    return np.clip(np.rint(c / 8), 0, 31) * 8


def fit_colors(pixels, count, seed=None):
    colors, counts = np.unique(pixels, axis=0, return_counts=True)
    if seed is None:
        centers = [colors[np.argmax(counts)]]
        while len(centers) < count:
            distances = ((colors[:, None] - np.array(centers)) ** 2 * WEIGHTS).sum(2).min(1)
            centers.append(colors[np.argmax(distances * counts)])
        centers = np.array(centers, dtype=float)
    else:
        centers = seed.copy()
    for _ in range(20):
        nearest = ((colors[:, None] - centers) ** 2 * WEIGHTS).sum(2).argmin(1)
        updated = centers.copy()
        for k in range(count):
            m = nearest == k
            if m.any():
                updated[k] = np.average(colors[m], axis=0, weights=counts[m])
        updated = rgb555(updated)
        if np.array_equal(centers, updated):
            break
        centers = updated
    return centers[np.argsort(centers @ np.array([0.2126, 0.7152, 0.0722]))]


def candidates(tiles, palettes):
    distances = ((tiles[:, None, :, None, :] - palettes[None, :, None, :, :]) ** 2 * WEIGHTS).sum(4)
    indices = distances.argmin(3)
    renders = palettes[np.arange(len(palettes))[None, :, None], indices]
    unary = distances.min(3).mean(2)
    return indices, renders, unary


def assign(tiles, palettes, tw, th, strength, locked=None):
    indices, renders, unary = candidates(tiles, palettes)
    if locked is not None:
        for i, k in enumerate(locked):
            if k >= 0:
                unary[i, np.arange(8) != k] = np.inf
    labels = unary.argmin(1)
    residual = (renders - tiles[:, None]).reshape(-1, 8, 8, 8, 3)
    # Penalize a new color discontinuity, not an edge already in the concept.
    for _ in range(12):
        changes = 0
        for order in [range(len(tiles)), range(len(tiles) - 1, -1, -1)]:
            for i in order:
                x, y = i % tw, i // tw
                cost = unary[i].copy()
                neighbors = []
                if x:
                    neighbors.append(
                        (i - 1, residual[i, :, :, 0], residual[i - 1, labels[i - 1], :, -1])
                    )
                if x + 1 < tw:
                    neighbors.append(
                        (i + 1, residual[i, :, :, -1], residual[i + 1, labels[i + 1], :, 0])
                    )
                if y:
                    neighbors.append(
                        (i - tw, residual[i, :, 0, :], residual[i - tw, labels[i - tw], -1, :])
                    )
                if y + 1 < th:
                    neighbors.append(
                        (i + tw, residual[i, :, -1, :], residual[i + tw, labels[i + tw], 0, :])
                    )
                for _, a, b in neighbors:
                    cost += strength * ((a - b) ** 2 * WEIGHTS).sum(2).mean(1)
                chosen = int(cost.argmin())
                changes += chosen != labels[i]
                labels[i] = chosen
        if not changes:
            break
    return indices[np.arange(len(tiles)), labels], labels, renders[np.arange(len(tiles)), labels]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--continuity", type=float, default=1)
    parser.add_argument("--pixel-continuity", type=float, default=0.25)
    parser.add_argument(
        "--palettes", type=Path, help="Reuse paletteRGB555 from a previous audit JSON"
    )
    parser.add_argument(
        "--regions", type=Path, help="Native-pixel polygons with shared palette-slot constraints"
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    image = Image.open(args.source).convert("RGB")
    w, h = image.size
    assert w % 8 == h % 8 == 0, "Source must already be on the target pixel grid"
    source = np.rint(np.array(image, dtype=float) * 31 / 255) * 8
    tw, th = w // 8, h // 8
    tiles = source.reshape(th, 8, tw, 8, 3).transpose(0, 2, 1, 3, 4).reshape(-1, 64, 3)
    # Cluster tiles by material distribution, then learn four-color families.
    summaries = np.concatenate([tiles.mean(1), tiles.std(1)], axis=1)
    seeds = [int(np.argmax(summaries[:, 0]))]
    while len(seeds) < 7:
        ds = ((summaries[:, None] - summaries[seeds]) ** 2).sum(2).min(1)
        seeds.append(int(ds.argmax()))
    centers = summaries[seeds].copy()
    for _ in range(20):
        group = ((summaries[:, None] - centers) ** 2).sum(2).argmin(1)
        for k in range(7):
            if (group == k).any():
                centers[k] = summaries[group == k].mean(0)
    palettes = np.array(
        [
            fit_colors((tiles[group == k] if (group == k).any() else tiles).reshape(-1, 3), 4)
            for k in range(7)
        ]
        + [UI]
    )
    if args.palettes:
        packed = np.array(json.loads(args.palettes.read_text())["paletteRGB555"], dtype="uint16")
        assert packed.shape == (8, 4)
        palettes = np.stack([packed & 31, (packed >> 5) & 31, (packed >> 10) & 31], axis=2) * 8.0
        assert np.array_equal(
            palettes[7], UI
        ), "Palette slot eight must retain the shared UI colors"
    locked = np.full(len(tiles), -1, dtype=int)
    fixed_slots = set()
    regions = []
    if args.regions:
        regions = json.loads(args.regions.read_text())["regions"]
        for region in regions:
            slot = region["slot"]
            assert isinstance(slot, int) and 0 <= slot < 7, "Region cannot use reserved UI slot"
            assert 0 < region.get("coverage", 0.5) <= 1, "Region coverage must be in (0,1]"
            mask = Image.new("L", (w, h))
            ImageDraw.Draw(mask).polygon([tuple(v) for v in region["polygon"]], fill=255)
            coverage = (
                np.asarray(mask).reshape(th, 8, tw, 8).transpose(0, 2, 1, 3).reshape(-1, 64).mean(1)
                / 255
            )
            selected = coverage >= region.get("coverage", 0.5)
            assert selected.any(), "Region covers no tiles"
            assert np.all(
                (locked[selected] < 0) | (locked[selected] == slot)
            ), "Conflicting region palette locks"
            locked[selected] = slot
            if "colors" in region:
                assert len(region["colors"]) == 4
                colors = np.array(
                    [[int(c[i : i + 2], 16) for i in (0, 2, 4)] for c in region["colors"]],
                    dtype=float,
                )
                palettes[slot] = np.rint(colors * 31 / 255) * 8
                fixed_slots.add(slot)
        # Learn a region's ramp from all its tiles together, never individually.
        for slot in set(locked[locked >= 0]) - fixed_slots:
            if not args.palettes:
                palettes[slot] = fit_colors(tiles[locked == slot].reshape(-1, 3), 4)
        fixed_slots.update(locked[locked >= 0])
        locks = Image.new("RGB", (tw, th))
        swatches = [
            (224, 88, 56),
            (240, 184, 72),
            (80, 184, 224),
            (136, 112, 208),
            (88, 192, 144),
            (192, 112, 152),
            (152, 160, 176),
        ]
        locks.putdata([swatches[v] if v >= 0 else (24, 24, 32) for v in locked])
        locks.resize((w * 4, h * 4), Image.Resampling.NEAREST).save(
            args.output / "region-locks-4x.png"
        )
    # Alternate tile assignment and palette fitting: every family is shared
    # globally, and continuity participates in its final assignment.
    for _ in range(0 if args.palettes else 8):
        indices, labels, _ = assign(tiles, palettes, tw, th, args.continuity, locked)
        for k in range(7):
            if k not in fixed_slots and (labels == k).any():
                palettes[k] = fit_colors(tiles[labels == k].reshape(-1, 3), 4, palettes[k])
    indices, labels, renders = assign(tiles, palettes, tw, th, args.continuity, locked)

    def flatten(a):
        return a.reshape(th, tw, 8, 8, -1).transpose(0, 2, 1, 3, 4).reshape(h, w, -1)

    # Clean quantization speckle using the four legal choices at each pixel.
    # Compare quantization residuals, so real material/lighting edges survive.
    choices = palettes[labels].reshape(th, tw, 4, 3).repeat(8, 0).repeat(8, 1)
    native = flatten(indices[..., None])[..., 0]
    yy, xx = np.indices((h, w))
    costs = ((choices - source[:, :, None]) ** 2 * WEIGHTS).sum(3)
    for _ in range(8):
        changes = 0
        for parity in [0, 1]:
            residual = choices - source[:, :, None]
            selected = residual[yy, xx, native]
            total = costs.copy()
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = np.roll(selected, (dy, dx), (0, 1))
                penalty = ((residual - neighbor[:, :, None]) ** 2 * WEIGHTS).sum(3)
                if dy == -1:
                    penalty[-1] = 0
                if dy == 1:
                    penalty[0] = 0
                if dx == -1:
                    penalty[:, -1] = 0
                if dx == 1:
                    penalty[:, 0] = 0
                total += args.pixel_continuity * penalty
            chosen = total.argmin(2)
            mask = (yy + xx) % 2 == parity
            changes += np.count_nonzero(chosen[mask] != native[mask])
            native[mask] = chosen[mask]
        if not changes:
            break
    indices = native.reshape(th, 8, tw, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    renders = palettes[labels[:, None], indices]
    unique = len({bytes(t) for t in indices})
    assert unique <= 384, "Exceeds ordinary color-only background tile budget"
    rendered = flatten(renders).astype("uint8")
    native = flatten(indices[..., None])[..., 0]
    Image.fromarray(rendered).save(args.output / "candidate.png")
    Image.fromarray(rendered).resize((w * 4, h * 4), Image.Resampling.NEAREST).save(
        args.output / "candidate-4x.png"
    )
    dmg = np.array([[224, 248, 207], [134, 192, 108], [48, 104, 80], [7, 24, 33]], dtype="uint8")
    Image.fromarray(dmg[native]).save(args.output / "native-index-source.png")
    # Hardware encoding, independent of the editor's preview color expansion.
    binary = bytearray()
    for tile in indices:
        for row in tile.reshape(8, 8):
            binary.extend(
                [
                    sum(int(v & 1) << (7 - x) for x, v in enumerate(row)),
                    sum(int(v >> 1) << (7 - x) for x, v in enumerate(row)),
                ]
            )
    (args.output / "tiles.2bpp").write_bytes(binary)
    (args.output / "attributes.bin").write_bytes(bytes(labels))
    pal = np.array(palettes / 8, dtype="uint16")
    packed = pal[:, :, 0] | (pal[:, :, 1] << 5) | (pal[:, :, 2] << 10)
    (args.output / "palettes.rgb555").write_bytes(packed.astype("<u2").tobytes())
    # Independent decode validates encoded output equals the candidate exactly.
    encoded = np.frombuffer(binary, dtype="uint8").reshape(-1, 8, 2)
    decoded = ((encoded[:, :, 0, None] >> np.arange(7, -1, -1)) & 1) | (
        ((encoded[:, :, 1, None] >> np.arange(7, -1, -1)) & 1) << 1
    )
    restored = palettes[labels[:, None], decoded.reshape(-1, 64)]
    assert np.array_equal(flatten(restored).astype("uint8"), rendered)
    report = {
        "source": str(args.source.resolve()),
        "sourceSHA256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "size": [w, h],
        "continuity": args.continuity,
        "pixelContinuity": args.pixel_continuity,
        "uniqueTiles": unique,
        "maxColorsPerTile": max(len(set(t)) for t in indices),
        "paletteCount": 8,
        "uiSlotReserved": True,
        "encodedRoundTripMatches": True,
        "paletteRGB555": packed.tolist(),
        "attributes": labels.tolist(),
        "pixelRMSE": float(np.sqrt(((rendered - source) ** 2).mean())),
        "integrated": False,
        "note": "Candidate conversion, not hand-authored pixel reconstruction or a gameplay capture.",
    }
    report["regions"] = regions
    report["regionConfigSHA256"] = (
        hashlib.sha256(args.regions.read_bytes()).hexdigest() if args.regions else None
    )
    (args.output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in [
                    "continuity",
                    "uniqueTiles",
                    "maxColorsPerTile",
                    "encodedRoundTripMatches",
                    "pixelRMSE",
                ]
            }
        )
    )


if __name__ == "__main__":
    main()
