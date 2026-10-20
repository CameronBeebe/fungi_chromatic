"""Bounded, reviewed gameplay contract for the existing Heartwood renderer.

This first adapter supports one fixed encoded harvest site. New art/node types
need an adapter and budget checks, not arbitrary model-supplied executable code.
"""

from collections import deque
import hashlib
import json


def identity(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def neighbours(cell):
    x, y = cell % 20, cell // 20
    return [
        ny * 20 + nx
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        if 0 <= nx < 20 and 0 <= ny < 18
    ]


def point(value, name):
    if not isinstance(value, list) or len(value) != 2 or any(type(n) != int for n in value):
        raise ValueError(name + " must be two integer tile coordinates")
    if not 0 <= value[0] < 20 or not 0 <= value[1] < 17:
        raise ValueError(name + " outside visible scene")
    return value[1] * 20 + value[0]


def validate(spec, candidate_revision):
    if not isinstance(spec, dict) or set(spec) != {
        "candidateRevision",
        "walkable",
        "spawn",
        "approach",
        "workTicks",
        "yield",
        "cost",
        "startSupplies",
    }:
        raise ValueError("Unexpected scene contract fields")
    if spec["candidateRevision"] != candidate_revision:
        raise ValueError("Stale candidate; reopen the current review")
    walk = spec["walkable"]
    if (
        not isinstance(walk, list)
        or len(walk) != 360
        or any(type(n) != int or n not in (0, 1) for n in walk)
    ):
        raise ValueError("Walk mask must contain 360 zero/one cells")
    if not 2 <= sum(walk) <= 120:
        raise ValueError("This renderer supports 2–120 walkable cells within its route bank budget")
    if any(walk[340:]):
        raise ValueError("The HUD row cannot be walkable")
    resource = {y * 20 + x for y in range(10, 13) for x in range(13, 17)}
    if any(walk[c] for c in resource):
        raise ValueError("The fixed harvest artwork must remain blocked")
    spawn = point(spec["spawn"], "Spawn")
    work = point(spec["approach"], "Work position")
    if not walk[spawn] or not walk[work]:
        raise ValueError("Spawn and work position must be walkable")
    if not any(n in resource for n in neighbours(work)):
        raise ValueError("Work position must touch the resource footprint")
    seen = {spawn}
    queue = deque([spawn])
    while queue:
        for n in neighbours(queue.popleft()):
            if walk[n] and n not in seen:
                seen.add(n)
                queue.append(n)
    if len(seen) != sum(walk):
        raise ValueError("Walkable cells must form one connected area reachable from spawn")
    for key, lo, hi in [
        ("workTicks", 1, 240),
        ("yield", 1, 99),
        ("cost", 0, 99),
        ("startSupplies", 0, 99),
    ]:
        if type(spec[key]) != int or not lo <= spec[key] <= hi:
            raise ValueError(f"{key} must be an integer from {lo} to {hi}")
    return {
        "walkableCells": sum(walk),
        "routeBytes": sum(walk) ** 2 + 360,
        "spawnReachesWork": True,
        "initiallyAffordable": spec["startSupplies"] >= spec["cost"],
        "limits": [
            "Foot-cell connectivity only; actor clearance, heights and occlusion require human review.",
            "One fixed harvest patch, one supply currency and one loot counter; no saving or extraction yet.",
        ],
    }


def array(name, values):
    return "const uint8_t " + name + "[] = {" + ",".join(str(n) for n in values) + "};\n"


def routes(walk):
    cells = [i for i, n in enumerate(walk) if n]
    index = {c: i for i, c in enumerate(cells)}
    directions = [255] * (len(cells) ** 2)
    for start in cells:
        seen = {start: 4}
        queue = deque([start])
        while queue:
            c = queue.popleft()
            for direction, n in enumerate((c - 1, c + 1, c - 20, c + 20)):
                if (
                    n not in index
                    or n in seen
                    or abs(n % 20 - c % 20) + abs(n // 20 - c // 20) != 1
                ):
                    continue
                seen[n] = direction if c == start else seen[c]
                queue.append(n)
        for end, direction in seen.items():
            directions[index[start] * len(cells) + index[end]] = direction
    code = (
        "#pragma bank 3\n#include <gbdk/platform.h>\n"
        + array("cell_index", [index.get(c, 255) for c in range(360)])
        + array("directions", directions)
    )
    code += (
        "uint8_t route_step(uint8_t sx,uint8_t sy,uint8_t tx,uint8_t ty) BANKED { uint8_t a=cell_index[(uint16_t)sy*20+sx],b=cell_index[(uint16_t)ty*20+tx]; if(a==255||b==255)return 255; return directions[(uint16_t)a*"
        + str(len(cells))
        + "+b]; }\n"
    )
    return code


def header(spec):
    mapping = {
        "SPAWN_X": spec["spawn"][0],
        "SPAWN_Y": spec["spawn"][1],
        "WORK_X": spec["approach"][0],
        "WORK_Y": spec["approach"][1],
        "WORK_TICKS": spec["workTicks"],
        "HARVEST_YIELD": spec["yield"],
        "START_SUPPLIES": spec["startSupplies"],
        "HARVEST_COST": spec["cost"],
    }
    return (
        "".join(f"#define SCENE_{key} {value}\n" for key, value in mapping.items())
        + f'#define SCENE_REWARD_MESSAGE "GATHERED +{spec["yield"]}"\n'
    )
