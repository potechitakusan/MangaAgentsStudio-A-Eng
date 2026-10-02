"""Check panel geometry, overlaps, reading order, and all layout variants."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from validate_panel_plan import validate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "templates/manga-project/templates/panel-templates"
catalog = json.loads((OUT / "catalog.json").read_text(encoding="utf-8"))
policy = json.loads((ROOT / "templates/manga-project/config/panel-layout-policy.json").read_text(encoding="utf-8"))
errors = []


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


def overlaps(a, b):
    for poly in (a, b):
        for i, p in enumerate(poly):
            q = poly[(i + 1) % len(poly)]
            axis = (-(q[1] - p[1]), q[0] - p[0])
            x = [v[0] * axis[0] + v[1] * axis[1] for v in a]
            y = [v[0] * axis[0] + v[1] * axis[1] for v in b]
            if max(x) <= min(y) or max(y) <= min(x):
                return False
    return True


ids = [t["id"] for t in catalog["templates"]]
if len(ids) != len(set(ids)):
    errors.append("Duplicate template IDs.")

for t in catalog["templates"]:
    polygons = [p["polygon"] for p in t["panels"]]
    if len(polygons) != t["panelCount"]:
        errors.append(f'{t["id"]}: Panel count mismatch')
    if [p["order"] for p in t["panels"]] != list(range(1, t["panelCount"] + 1)):
        errors.append(f'{t["id"]}: Reading order mismatch')
    for i, p in enumerate(polygons):
        if not all(60 <= x <= 940 and 60 <= y <= 1440 for x, y in p):
            errors.append(f'{t["id"]}: Frame extends outside the allowed bounds')
        if not all(cross(p[j], p[(j + 1) % 4], p[(j + 2) % 4]) > 0 for j in range(4)):
            errors.append(f'{t["id"]}: Panel is not a convex quadrilateral')
        for q in polygons[i + 1:]:
            if overlaps(p, q):
                errors.append(f'{t["id"]}: Panels overlap')
    for key in ("svg", "guideSvg", "json", "transparentPng", "previewPng"):
        p_path = OUT / t["assets"][key]
        if not p_path.exists():
            errors.append(f'{p_path}: File does not exist')
            continue
        if key.endswith("Svg") or key == "svg":
            ET.parse(p_path)
        if key == "json" and json.loads(p_path.read_text(encoding="utf-8")) != t:
            errors.append(f'{t["id"]}: Individual JSON does not match the catalog')
    if t["panelCount"] == 5 and not t["extra"]:
        values = [s for n, s in zip(t["rows"], t["splitPositionsFromLeft"]) if n == 2]
        if values != [0.5, 0.5] and (values[0] - 0.5) * (values[1] - 0.5) >= 0:
            errors.append(f'{t["id"]}: Invalid five-panel width pattern')
    if t["panelCount"] == 6 and len(set(t["splitPositionsFromLeft"])) != 3:
        errors.append(f'{t["id"]}: Six-panel vertical dividers align')

five = [t for t in catalog["templates"] if t["panelCount"] == 5 and not t["extra"]]
if len(five) != 54:
    errors.append(f"Expected 54 five-panel base variants; found {len(five)}")

two = [t for t in catalog["templates"] if t["panelCount"] == 2]
if len(two) != 5:
    errors.append(f"Expected 5 two-panel templates; found {len(two)}")

# Validate the 20-page example plan
plan_result = validate(json.loads((OUT / "plan-example-20.json").read_text(encoding="utf-8")), catalog, policy)
errors.extend(plan_result["errors"])

# Boundary cases for three-tier spacing and rolling 20-page limits
def sample_plan(locations, total=40):
    rows = [{"page": p, "templateId": "P5-212-equal-normal-straight"} for p in range(1, total + 1)]
    for p in locations:
        rows[p - 1]["templateId"] = "P3-horizontal-up-right" if p % 2 else "P3-horizontal-straight"
    return {"pages": rows}


cases = [
    ("p1 and p5 with 3 intervening pages: invalid", [1, 5], False),
    ("p1 and p6 with 4 intervening pages: valid", [1, 6], True),
    ("4 uses in 20 consecutive pages: invalid", [1, 6, 11, 16], False),
    ("4 uses spanning a rolling window: invalid", [17, 22, 27, 32], False),
    ("3 uses in 20 pages: valid", [1, 6, 11], True),
    ("Additional use outside the 20-page window: valid", [1, 6, 11, 21], True)
]
boundary = []
for label, loc, expected in cases:
    actual = validate(sample_plan(loc), catalog, policy)["valid"]
    boundary.append({"case": label, "passed": actual == expected})
    if actual != expected:
        errors.append(f"Boundary case failed: {label}")

report = {
    "valid": not errors,
    "templateCount": len(ids),
    "twoPanelVariants": len(two),
    "fivePanelVariants": len(five),
    "geometryErrors": errors,
    "boundaryCases": boundary,
    "planExampleValid": plan_result["valid"]
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["valid"] else 1)
