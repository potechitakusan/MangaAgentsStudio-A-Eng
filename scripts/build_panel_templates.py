"""Build comic panel frames from coordinates: the shared source for SVG, JSON, and the picker."""
import argparse
import copy
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "templates/manga-project/templates/panel-templates"

W, H, M = 1000, 1500, 60
AW, AH = W - 2 * M, H - 2 * M
GX, GY = 0.022, 0.022


def points(poly):
    return [[round(M + x * AW, 3), round(M + y * AH, 3)] for x, y in poly]


def build_library():
    lib = []

    def add(identifier, name, desc, rows, heights=None, splits=None, tilt=0, horizontal_tilt=0,
            family=None, usage=None, frequency="Standard", wide=None, short=False, extra=False):
        h_list = heights or [1 / len(rows)] * len(rows)
        s_list = splits or [0.5] * len(rows)
        cursor, panels = 0, []
        split_index = 0
        for row, (count, height, split) in enumerate(zip(rows, h_list, s_list)):
            y0 = cursor + (GY / 2 if row else 0)
            y1 = cursor + height - (GY / 2 if row < len(rows) - 1 else 0)
            top_l = y0 - (horizontal_tilt / 2 if row else 0)
            top_r = y0 + (horizontal_tilt / 2 if row else 0)
            bot_l = y1 - (horizontal_tilt / 2 if row < len(rows) - 1 else 0)
            bot_r = y1 + (horizontal_tilt / 2 if row < len(rows) - 1 else 0)
            if count == 1:
                polys = [[(0, top_l), (1, top_r), (1, bot_r), (0, bot_l)]]
            else:
                direction = tilt * (1 if split_index % 2 == 0 else -1)
                a, b = split - direction / 2, split + direction / 2
                polys = [
                    [(a + GX / 2, y0), (1, y0), (1, y1), (b + GX / 2, y1)],
                    [(0, y0), (a - GX / 2, y0), (b - GX / 2, y1), (0, y1)],
                ]
                split_index += 1
            if count > 1:
                polys.reverse()  # Number panels left to right without mirroring their geometry.
            for col, poly in enumerate(polys):
                n = len(panels) + 1
                panels.append({
                    "id": f"panel-{n:02}",
                    "order": n,
                    "row": row + 1,
                    "position": "Full width" if count == 1 else "Left" if col == 0 else "Right",
                    "role": "Standard",
                    "polygon": points(poly)
                })
            cursor += height
        item = {
            "id": identifier,
            "name": name,
            "summary": desc,
            "panelCount": len(panels),
            "family": family or "-".join(map(str, rows)),
            "rows": rows,
            "rowHeightRatios": h_list,
            "splitPositionsFromLeft": s_list,
            "widthPattern": wide or "Equal width",
            "shortWidePanel": short,
            "verticalTilt": tilt,
            "horizontalTilt": horizontal_tilt,
            "diagonal": bool(tilt or horizontal_tilt),
            "frequency": frequency,
            "usage": usage or ["Dialogue", "Action and reaction"],
            "extra": extra,
            "restrictionGroup": "horizontal-three" if family == "horizontal-three" else None,
            "readingDirection": "Left to right within each row, then top to bottom",
            "panels": panels,
            "modifiers": [],
            "baseTemplateId": None
        }
        lib.append(item)
        return item

    # 3 panels
    for rows, key, label in [([2, 1], "21", "2+1"), ([1, 2], "12", "1+2")]:
        for tilt, suffix, word in [(0, "straight", "Straight"), (0.07, "lean-right", "Leans right"), (-0.07, "lean-left", "Leans left")]:
            add(f"P3-{key}-{suffix}", f"3 panels · {label} · {word}",
                label + ". Feature the character in the main panel. " + ("The bottom of the vertical divider leans right." if tilt > 0 else "The bottom of the vertical divider leans left." if tilt < 0 else ""),
                rows, tilt=tilt, usage=["Opening", "Key beat", "Tension" if tilt else "Afterbeat"], frequency="Use sparingly" if tilt else "Standard")
    for slope, suffix, word in [(0, "straight", "Straight"), (0.035, "down-right", "Slopes down right"), (-0.035, "up-right", "Slopes up right")]:
        add(f"P3-horizontal-{suffix}", f"3 panels · three tiers · {word}",
            "Three wide panels stacked vertically. Slanted variants count toward the same three-tier limit.",
            [1, 1, 1], horizontal_tilt=slope, family="horizontal-three",
            usage=["Quiet reaction" if not slope else "Action", "Time break"], frequency="Frequency limited")

    # 4 panels
    add("P4-22-stagger", "4 panels · staggered 2+2",
        "Wider left panel on top; wider right panel below. Offset the vertical dividers between rows.", [2, 2], splits=[0.57, 0.43], wide="Wider left above, wider right below")
    add("P4-22-stagger-reverse", "4 panels · reversed staggered 2+2",
        "Wider right panel on top; wider left panel below. Offset the vertical dividers between rows.", [2, 2], splits=[0.43, 0.57], wide="Wider right above, wider left below")
    add("P4-211", "4 panels · 2+1+1",
        "Split the top tier into two panels; use full-width panels in the middle and bottom tiers.", [2, 1, 1], usage=["Dialogue", "Context and reaction"])

    # 5 panels: 3 arrangements x 3 widths x 2 heights x 3 slopes = 54 variants
    for rows, key, label in [([2, 1, 2], "212", "Wide middle tier"), ([1, 2, 2], "122", "Wide top tier"), ([2, 2, 1], "221", "Wide bottom tier")]:
        for width_key, split_values, width_label in [
            ("equal", [0.5, 0.5], "Equal widths in split tiers"),
            ("rl", [0.43, 0.57], "First split tier wider right, next wider left"),
            ("lr", [0.57, 0.43], "First split tier wider left, next wider right")
        ]:
            splits = []
            it = iter(split_values)
            for row in rows:
                splits.append(next(it) if row == 2 else 0.5)
            for short in (False, True):
                heights = [(0.24 if n == 1 else 0.38) for n in rows] if short else [1 / 3] * 3
                for tilt, suffix, word in [(0, "straight", "Straight"), (0.064, "diag-r", "Diagonal A"), (-0.064, "diag-l", "Diagonal B")]:
                    height_key = "short" if short else "normal"
                    height_word = "Short wide tier" if short else "Three equal tiers"
                    desc = f"{label} · {width_label} · {height_word} · "
                    if tilt:
                        desc += "Slant the two vertical dividers in opposite directions. Use sparingly."
                    add(f"P5-{key}-{width_key}-{height_key}-{suffix}", f"5 panels · {label} · {width_label} · {height_word} · {word}",
                        desc, rows, heights, splits, tilt=tilt, wide=width_label, short=short,
                        usage=["Tension", "Sudden turn"] if tilt else ["Dialogue", "Action and reaction", "Everyday scene"], frequency="Use sparingly" if tilt else "Core layout")

    # 6 panels
    for idx, splits in enumerate(([0.43, 0.55, 0.47], [0.57, 0.45, 0.53], [0.47, 0.59, 0.41]), 1):
        add(f"P6-222-shift-{idx}", f"6 panels · offset dividers · {idx}",
            "Two panels in each of three tiers. Vary the widths so vertical dividers do not line up.", [2, 2, 2], splits=list(splits),
            wide="Varies by tier", usage=["Sequence", "Successive dialogue", "Small movements"], frequency="Use sparingly")

    # 1 panel
    add("P1-splash", "1 panel · splash", "One large image. For a two-page spread, coordinate the composition with the facing page.", [1], usage=["Major reveal", "Two-page spread"], frequency="Special use", extra=True)

    # 2 panels: square/wide pairs, equal halves, or unequal tiers
    h_top_square = round(880 / 1380 + 0.011, 4)
    h_top_rem = round(1.0 - h_top_square, 4)
    add("P2-top-square", "2 panels · square above, wide below",
        "A square panel above a wide panel. Feature a character or key subject above; place context or dialogue below.",
        [1, 1], [h_top_square, h_top_rem], usage=["Character emphasis", "Context and contrast"], frequency="Standard")
    add("P2-bottom-square", "2 panels · wide above, square below",
        "A wide panel above a square panel. Establish the setting above, then focus on emotion or a key image below.",
        [1, 1], [h_top_rem, h_top_square], usage=["Emotional response", "Establishing scenery"], frequency="Standard")
    add("P2-half", "2 panels · equal vertical split",
        "Two equally sized wide panels, stacked vertically. Contrast two scenes or convey a quiet passage of time.",
        [1, 1], [0.5, 0.5], usage=["Scene contrast", "Elapsed time", "Quiet afterbeat"], frequency="Standard")

    for key, heights, word in [("large-bottom", [0.30, 0.70], "Larger bottom"), ("large-top", [0.70, 0.30], "Larger top")]:
        add(f"P2-{key}", f"2 panels · {word}", "Two wide panels, one above the other. Use for a quiet afterbeat or a contrast in space.",
            [1, 1], heights, usage=["Afterbeat", "Strong contrast"], frequency="Special use", extra=True)

    # Expressive variants
    base_dict = {t["id"]: t for t in lib}
    for side, label in [("right", "right"), ("left", "left")]:
        base = base_dict["P5-212-rl-normal-straight"]
        t = copy.deepcopy(base)
        t.update(
            id=f"FX-breakout-{side}",
            name=f"Effect · character breakout on the {label}",
            summary=f"Retain the five-panel frames and reserve a region on the {label} for a figure crossing tiers, such as a full-length figure beside a building.",
            frequency="Special use", extra=True, baseTemplateId=base["id"],
            usage=["Character entrance", "Full-length figure at a doorway"],
            modifiers=[{
                "type": "character-breakout",
                "side": side,
                "sourcePanelOrder": 2 if side == "right" else 1,
                "role": "Overlay region for a character, not a separate chronological panel.",
                "region": points([(0.70, 0.05), (0.94, 0.05), (0.94, 0.96), (0.67, 0.96)]) if side == "right" else points([(0.06, 0.05), (0.30, 0.05), (0.33, 0.96), (0.06, 0.96)]),
                "frameMask": "Erase frame lines along the character silhouette during composition. Do not blank the entire guide region."
            }]
        )
        lib.append(t)

    for growing in (True, False):
        base = base_dict["P5-212-equal-short-straight"]
        t = copy.deepcopy(base)
        name = "grow" if growing else "shrink"
        label = "grow" if growing else "shrink"
        mid = t["panels"][2]
        y0 = mid["polygon"][0][1]
        y1 = mid["polygon"][2][1]
        sizes = [0.16, 0.26, 0.40] if growing else [0.40, 0.26, 0.16]
        cursor = M
        inserts = []
        for s in sizes:
            pw = s * AW
            ph = (y1 - y0) * (0.45 + s)
            cy = (y0 + y1) / 2
            inserts.append({
                "id": "", "order": 0, "row": 2, "position": "Time passage", "role": "White timing panel",
                "polygon": [
                    [round(cursor, 3), round(cy - ph / 2, 3)],
                    [round(cursor + pw, 3), round(cy - ph / 2, 3)],
                    [round(cursor + pw, 3), round(cy + ph / 2, 3)],
                    [round(cursor, 3), round(cy + ph / 2, 3)]
                ]
            })
            cursor += pw + GX * AW
        t["panels"] = t["panels"][:2] + inserts + t["panels"][3:]
        for n, p in enumerate(t["panels"], 1):
            p["id"] = f"panel-{n:02}"
            p["order"] = n
        t.update(
            id=f"FX-time-{name}",
            name=f"Effect · white panels {label}",
            summary=f"Replace the middle wide panel of a five-panel layout with three white panels that {label} from left to right. Use for elapsed time or a breath-held pause.",
            panelCount=7, rows=[2, 3, 2], family="time-passage", frequency="Special use", extra=True,
            baseTemplateId=base["id"], usage=["Time passage", "Breath-held pause"],
            modifiers=[{
                "type": "time-passage",
                "replacesPanelOrder": 3,
                "direction": name,
                "note": "These are separate panels, bringing the total to seven. The surrounding images establish the actual elapsed time."
            }]
        )
        lib.append(t)

    return lib


def svg(item, guide=False):
    title = html.escape(item["name"])
    contents = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}"><title>{title}</title>'
    ]
    if guide:
        contents.append(f'<rect width="{W}" height="{H}" fill="#f6f4ee"/>')
    contents.append('<g id="panels">')
    palette = ["#e8edf4", "#f2efe9", "#edf4eb", "#f4ebeb"]
    for p in item["panels"]:
        xy = " ".join(f"{x},{y}" for x, y in p["polygon"])
        if guide:
            fill = palette[(p["row"] - 1) % len(palette)]
            contents.append(f'<polygon points="{xy}" fill="{fill}" stroke="#111" stroke-width="5" stroke-linejoin="miter"/>')
        else:
            contents.append(f'<polygon id="{p["id"]}" points="{xy}" fill="none" stroke="#000" stroke-width="5" stroke-linejoin="miter"/>')
    contents.append('</g>')
    if guide and item.get("modifiers"):
        contents.append('<g id="effects-guide">')
        for mod in item["modifiers"]:
            if mod["type"] == "character-breakout":
                xy = " ".join(f"{x},{y}" for x, y in mod["region"])
                contents.append(f'<polygon points="{xy}" fill="#ce8749" fill-opacity=".20" stroke="#a85e27" stroke-width="4" stroke-dasharray="16 10"/>')
                x = sum(pt[0] for pt in mod["region"]) / 4
                contents.append(f'<text x="{x}" y="750" text-anchor="middle" fill="#8a491e" font-size="22" font-family="sans-serif">Character breakout</text>')
        contents.append('</g>')
    if guide:
        contents.append('<g id="reading-order" font-family="Arial,sans-serif" text-anchor="middle" dominant-baseline="central">')
        for p in item["panels"]:
            x = sum(v[0] for v in p["polygon"]) / 4
            y = sum(v[1] for v in p["polygon"]) / 4
            contents.append(f'<circle cx="{x}" cy="{y}" r="30" fill="#213c37"/><text x="{x}" y="{y}" fill="#fff" font-size="32">{p["order"]}</text>')
        contents.append('</g>')
    contents.append('</svg>')
    return ''.join(contents)


def generate_all(out_dir=DEFAULT_OUT):
    out_dir = Path(out_dir).resolve()
    for folder in ("svg", "guides", "png", "previews", "json"):
        (out_dir / folder).mkdir(parents=True, exist_ok=True)

    lib = build_library()

    for item in lib:
        ident = item["id"]
        item["coordinateSystem"] = {"width": W, "height": H, "origin": "Top left", "unit": "SVG user units", "pngScale": 2}
        item["assets"] = {
            "svg": f"svg/{ident}.svg",
            "guideSvg": f"guides/{ident}.svg",
            "transparentPng": f"png/{ident}.png",
            "previewPng": f"previews/{ident}.png",
            "json": f"json/{ident}.json"
        }
        (out_dir / item["assets"]["svg"]).write_text(svg(item, guide=False), encoding="utf-8", newline="\n")
        (out_dir / item["assets"]["guideSvg"]).write_text(svg(item, guide=True), encoding="utf-8", newline="\n")
        (out_dir / item["assets"]["json"]).write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    # Catalog JSON
    catalog = {
        "schemaVersion": 1,
        "name": "Comic panel layout library",
        "date": "2026-09-30",
        "locale": "en-US",
        "sourceDate": "2026-09-15",
        "canvas": {
            "width": W,
            "height": H,
            "coordinateUnit": "SVG user units",
            "origin": "Top left",
            "xDirection": "Right",
            "yDirection": "Down",
            "frameInset": M,
            "frameStroke": 5,
            "pngScale": 2,
            "pngSize": [2000, 3000],
            "printDpi": None
        },
        "readingDirection": "Left to right, then top to bottom. Numbers indicate reading order.",
        "tiltDefinition": "A right-leaning vertical divider has its bottom farther right. Five-panel layouts have opposing divider slopes; A and B reverse those slopes.",
        "notes": [
            "SVG files are editable frames; PNG files are transparent frame assets. Neither directly creates a CLIP STUDIO PAINT frame-border folder.",
            "Four-panel options include two staggered 2+2 layouts and a 2+1+1 layout.",
            "Two-panel options pair a square and a wide panel, divide the page equally, or use unequal sizes for an afterbeat.",
            "Seven-panel time-passage options are expressive variants of five-panel layouts."
        ],
        "policyPath": "../../config/panel-layout-policy.json",
        "templateCount": len(lib),
        "templates": lib
    }
    (out_dir / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    # 20-page example plan
    base_ids = [t["id"] for t in lib if t["panelCount"] == 5 and not t["diagonal"] and not t["extra"]]
    example = []
    five_idx = 0
    fixed20 = {
        1: "P3-horizontal-straight",
        4: "P4-22-stagger",
        7: "P6-222-shift-1",
        9: "P4-211",
        11: "P3-horizontal-up-right",
        14: "P4-22-stagger",
        17: "P6-222-shift-2",
        19: "P3-21-straight"
    }
    for p in range(1, 21):
        ident = fixed20.get(p)
        if not ident:
            ident = base_ids[five_idx % len(base_ids)]
            five_idx += 1
        example.append({"page": p, "templateId": ident})
    (out_dir / "plan-example-20.json").write_text(
        json.dumps({"status": "Example of proportions and limits, not an approved layout for a story.", "pages": example}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n"
    )

    # UI text
    ui = {
        "kicker": "Comic Production Kit · Production resources",
        "title": "Panel layout picker",
        "intro": "Plan reading order and page structure first. Start with five-panel layouts and vary pacing with quiet pauses.",
        "all": "All", "basic": "Standard", "diagonal": "Diagonal", "effects": "Effects",
        "count": "Panel count", "shape": "Shape", "search": "Search by use, name, or ID", "searchPlaceholder": "Try: afterbeat, wider right, 212, square",
        "results": "Results", "cards": "Templates", "plan": "20-page example", "policy": "Distribution defaults",
        "svg": "SVG frames", "png": "Transparent PNG", "json": "JSON", "preview": "Numbered PNG",
        "main": "Five panels are the default emphasis",
        "rule": "Leave at least four pages between three-tier wide layouts. Use no more than three in any rolling 20 pages, including slanted variants.",
        "rare": "Aim for no more than one diagonal five-panel layout per 20 pages.",
        "note": "Numbers show reading order. Edit the SVG files or overlay the transparent PNG frames on artwork.",
        "unapplied": "This example uses distribution defaults. Adjust proportions and limits for your project. Changes to project JSON settings do not automatically update this catalog.",
        "copy": "Copy ID", "copied": "Copied", "copyFail": "Copy failed. Select and copy the ID manually.",
        "empty": "No templates match these filters.",
        "ratio": "Guideline for 20 standard pages",
        "ratioText": "5 panels 60% · 4 panels 15% · 3 panels 15% · 6 panels 10%",
        "planText": "Example mix: 5 panels 60%, 4 panels 15%, 3 panels 15%, 6 panels 10%.",
        "downloadPlan": "Example plan JSON", "catalog": "Full catalog JSON", "close": "Close", "enlarge": "Enlarge"
    }
    (out_dir / "ui-text.json").write_text(json.dumps(ui, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    # HTML viewer
    html_content = generate_index_html(ui, lib, example)
    (out_dir / "index.html").write_text(html_content, encoding="utf-8", newline="\n")

    print(json.dumps({
        "templates": len(lib),
        "twoPanelCount": sum(t["panelCount"] == 2 for t in lib),
        "fivePanelBaseVariants": sum(t["panelCount"] == 5 and not t["extra"] for t in lib),
        "output": str(out_dir)
    }, ensure_ascii=False))


def generate_index_html(ui, lib, plan):
    ui_json = json.dumps(ui, ensure_ascii=False)
    data_json = json.dumps(lib, ensure_ascii=False)
    plan_json = json.dumps(plan, ensure_ascii=False)

    return f'''<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(ui["title"])}</title>
<style>
:root{{--bg:#f2efe9;--panel:#fff;--line:#d2cbbe;--text:#23201b;--sub:#6b6458;--accent:#244c44;--accent-sub:#e4eee9;--rare:#734b22;--rare-bg:#f5ece1;--chip:#e6e1d6}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
header{{padding:28px 24px 18px;max-width:1300px;margin:auto}}
.kicker{{font-size:12px;letter-spacing:.12em;color:var(--sub);font-weight:700;text-transform:uppercase}}
h1{{margin:4px 0 10px;font-size:28px;letter-spacing:.03em}}
header p{{margin:0 0 18px;color:var(--sub);max-width:800px}}
nav{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
nav button,nav a.button{{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:8px 18px;font-size:14px;color:inherit;text-decoration:none;cursor:pointer}}
nav button.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;max-width:1300px;margin:0 auto 16px;padding:0 24px}}
.summary>div{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 18px}}
.summary strong{{display:block;font-size:13px;letter-spacing:.08em;color:var(--accent);margin-bottom:6px}}
.summary p{{margin:4px 0;font-size:13px;color:var(--sub)}}
.toolbar{{position:sticky;top:0;z-index:20;background:rgba(242,239,233,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:10px 24px}}
.filters{{max-width:1300px;margin:auto;display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
.filters label{{font-size:13px;color:var(--sub);display:inline-flex;gap:6px;align-items:center}}
select,input[type=search]{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:14px;color:inherit}}
input[type=search]{{min-width:240px;flex:1}}
.content{{max-width:1300px;margin:18px auto 48px;padding:0 24px}}
.countline{{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--sub);margin-bottom:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:transform .12s ease,box-shadow .12s ease}}
.card:hover{{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.06)}}
.thumb{{background:#e9e5dc;border:none;padding:12px;display:flex;align-items:center;justify-content:center;cursor:pointer}}
.thumb img{{display:block;width:100%;max-width:240px;height:auto;aspect-ratio:1000/1500;border:1px solid var(--line);background:#fff;border-radius:4px}}
.body{{padding:14px 16px;flex:1;display:flex;flex-direction:column;gap:6px}}
.card .id{{font:700 12px/1.2 Consolas,monospace;color:var(--accent);letter-spacing:.04em}}
.card .name{{margin:0;font-size:15px;font-weight:700;line-height:1.4}}
.card .tags{{font-size:12px;color:var(--sub)}}
.tag{{display:inline-block;padding:2px 8px;border-radius:6px;background:var(--chip);color:var(--sub);font-size:11px;font-weight:600;align-self:flex-start}}
.tag.rare{{background:var(--rare-bg);color:var(--rare)}}
.copy{{background:none;border:1px dashed var(--line);border-radius:6px;padding:4px 8px;font-size:12px;color:var(--sub);cursor:pointer;align-self:flex-start;margin-top:4px}}
.copy:hover{{border-color:var(--accent);color:var(--accent)}}
.links{{border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:10px;flex-wrap:wrap;font-size:12px}}
.links a{{color:var(--accent);text-decoration:none}}
.links a:hover{{text-decoration:underline}}
.plan.hidden,.toolbar.hidden,#cards.hidden{{display:none}}
#empty.hidden{{display:none}}
dialog{{border:1px solid var(--line);border-radius:14px;padding:20px;max-width:920px;width:92vw;background:var(--panel)}}
dialog::backdrop{{background:rgba(20,18,15,.6)}}
.detail{{display:grid;grid-template-columns:minmax(240px,360px) 1fr;gap:20px;align-items:start}}
.detail img{{width:100%;height:auto;border:1px solid var(--line);border-radius:6px}}
.detail button#close{{float:right;background:none;border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}}
@media(max-width:680px){{.detail{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
<div class="kicker" data-text="kicker"></div>
<h1 data-text="title"></h1>
<p data-text="intro"></p>
<nav>
<button class="active" id="tab-cards" data-text="cards"></button>
<button id="tab-plan" data-text="plan"></button>
<a class="button" href="catalog.json" data-text="catalog"></a>
<a class="button" href="../../docs/production/PANEL-LAYOUT-POLICY.md" data-text="policy"></a>
</nav>
</header>
<section class="summary">
<div><strong data-text="main"></strong><p data-text="rule"></p><p data-text="rare"></p></div>
<div><strong data-text="ratio"></strong><p data-text="ratioText"></p><p data-text="note"></p></div>
</section>
<div class="toolbar" id="toolbar">
<div class="filters">
<label><span data-text="count"></span>
<select id="count">
<option value="all">All</option>
<option>1</option>
<option>2</option>
<option>3</option>
<option>4</option>
<option selected>5</option>
<option>6</option>
<option>7</option>
</select></label>
<label><span data-text="shape"></span>
<select id="shape">
<option value="all">All</option>
<option value="basic" selected>Standard</option>
<option value="diagonal">Diagonal</option>
<option value="effects">Effects</option>
</select></label>
<input id="search" type="search" aria-label="Search by use, name, or ID">
</div>
</div>
<main class="content">
<section id="cards">
<div class="countline"><span id="result"></span><span id="status" role="status"></span></div>
<div id="grid" class="grid"></div>
<p id="empty" class="hidden" data-text="empty"></p>
</section>
<section id="plan" class="plan hidden">
<h2 data-text="plan"></h2>
<p data-text="unapplied"></p>
<p data-text="planText"></p>
<p><a class="button" href="plan-example-20.json" data-text="downloadPlan"></a></p>
<div id="plan-grid" class="grid"></div>
</section>
</main>
<dialog id="dialog">
<div class="detail">
<img id="detail-image" alt="">
<div>
<button id="close" data-text="close"></button>
<p id="detail-id" class="id"></p>
<h2 id="detail-name" class="name"></h2>
<p id="detail-summary"></p>
<p id="detail-tags"></p>
<div id="detail-links"></div>
</div>
</div>
</dialog>
<script>
const UI = {ui_json};
const DATA = {data_json};
const PLAN = {plan_json};
document.querySelectorAll('[data-text]').forEach(e => e.textContent = UI[e.dataset.text]);
document.querySelector('#search').placeholder = UI.searchPlaceholder;
const $ = s => document.querySelector(s);
const files = t => [['svg', UI.svg], ['transparentPng', UI.png], ['json', UI.json], ['previewPng', UI.preview]];
function links(t, parent) {{
  for (const [key, label] of files(t)) {{
    const a = document.createElement('a');
    a.href = t.assets[key];
    a.textContent = label;
    a.download = '';
    parent.append(a);
  }}
}}
function detail(t) {{
  $('#detail-image').src = t.assets.guideSvg;
  $('#detail-image').alt = t.name;
  $('#detail-id').textContent = t.id;
  $('#detail-name').textContent = t.name;
  $('#detail-summary').textContent = t.summary;
  $('#detail-tags').textContent = t.usage.join('  ·  ');
  $('#detail-links').replaceChildren();
  links(t, $('#detail-links'));
  $('#dialog').showModal();
}}
function card(t, plan) {{
  const a = document.createElement('article');
  a.className = 'card';
  a.dataset.id = t.id;
  const b = document.createElement('button');
  b.className = 'thumb';
  b.setAttribute('aria-label', UI.enlarge + ': ' + t.name);
  const img = document.createElement('img');
  img.src = t.assets.guideSvg;
  img.alt = t.name;
  img.loading = 'lazy';
  b.append(img);
  b.onclick = () => detail(t);
  a.append(b);
  const body = document.createElement('div');
  body.className = 'body';
  const id = document.createElement('div');
  id.className = 'id';
  id.textContent = plan ? 'Page ' + String(plan.page).padStart(2, '0') : t.id;
  const n = document.createElement('h3');
  n.className = 'name';
  n.textContent = t.name;
  const tags = document.createElement('div');
  tags.className = 'tags';
  tags.textContent = plan ? t.id : t.usage.join('  ·  ');
  body.append(id, n, tags);
  if (!plan) {{
    const tag = document.createElement('span');
    tag.className = 'tag' + (t.diagonal ? ' rare' : '');
    tag.textContent = t.frequency;
    body.append(tag);
    const copy = document.createElement('button');
    copy.className = 'copy';
    copy.textContent = UI.copy;
    copy.onclick = async () => {{
      try {{
        await navigator.clipboard.writeText(t.id);
        $('#status').textContent = UI.copied + ': ' + t.id;
      }} catch(e) {{
        $('#status').textContent = UI.copyFail;
      }}
    }};
    body.append(copy);
  }}
  a.append(body);
  if (!plan) {{
    const l = document.createElement('div');
    l.className = 'links';
    links(t, l);
    a.append(l);
  }}
  return a;
}}
function render() {{
  const count = $('#count').value, shape = $('#shape').value, q = $('#search').value.trim().toLowerCase();
  const list = DATA.filter(t => (count === 'all' || t.panelCount === Number(count)) &&
    (shape === 'all' || (shape === 'basic' && !t.diagonal && !t.extra) || (shape === 'diagonal' && t.diagonal) || (shape === 'effects' && t.extra)) &&
    (!q || (t.id + ' ' + t.name + ' ' + t.summary + ' ' + t.usage.join(' ')).toLowerCase().includes(q)));
  $('#grid').replaceChildren(...list.map(t => card(t)));
  $('#result').textContent = UI.results + ' ' + list.length + ' / ' + DATA.length;
  $('#empty').classList.toggle('hidden', list.length > 0);
}}
for (const id of ['count', 'shape', 'search']) $('#' + id).addEventListener('input', render);
render();
$('#plan-grid').replaceChildren(...PLAN.map(p => card(DATA.find(t => t.id === p.templateId), p)));
function tab(plan) {{
  $('#cards').classList.toggle('hidden', plan);
  $('#plan').classList.toggle('hidden', !plan);
  $('#toolbar').classList.toggle('hidden', plan);
  $('#tab-plan').classList.toggle('active', plan);
  $('#tab-cards').classList.toggle('active', !plan);
}}
$('#tab-plan').onclick = () => tab(true);
$('#tab-cards').onclick = () => tab(false);
$('#close').onclick = () => $('#dialog').close();
$('#dialog').onclick = e => {{ if (e.target === $('#dialog')) $('#dialog').close(); }};
</script>
</body>
</html>
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    generate_all(args.output)
