# Ktech template bracket for Autodesk Fusion 360
#
# Install
#   1. Fusion → Utilities → Add-Ins → Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_Template_Bracket)
#   4. Run it. It opens / uses a Design document. Save as KTECH_TEMPLATE_BRACKET.
#
# What it builds
#   A 3/16 in laser / waterjet plate traced from a paper template:
#   boot / bottle-opener outline, rounded left tab with one 1/2 in hole,
#   two 21/32 in clearance holes (for 5/8 bolts) in the wide end. Exports a flat DXF of the face to
#   dxf_out/ next to the script.
#
# Source of the numbers
#   plate_t and the 1/2 in hole are as specified. The two large holes are
#   21/32 in (0.65625) clearance for 5/8 bolts, 1.000 in C-C MEASURED from
#   the mating bracket (0.66 dia, 0.322 edge gap, 1.666 outside). The pair
#   stays centered on the original photo-trace midpoint (X 3.33125, Y 1.05).
#   Remaining outline and the 1/2 in hole location are PHOTO ESTIMATES from
#   a paper template photographed with a tape in frame, roughly +/- 1/8 in. Caliper the
#   paper (or a first article), edit the named user parameters or the CSV,
#   then New Design and re-run before a production cut. Kerf is not
#   compensated.
#
# Coordinates (standalone flat pattern — not chassis coordinates)
#   Origin = far left of the rounded tab × straight bottom edge
#   +X = toward the wide end    +Y = up the plate    +Z = thickness

import csv
import math
import os
import traceback

import adsk.core
import adsk.fusion

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
except Exception:
    SCRIPT_DIR = os.getcwd()

# Bodies whose top-face outline is exported as flat DXF for laser / waterjet.
PLATE_BODY_NAMES = ("TEMPLATE_BRACKET",)

# Fusion API lengths are always centimeters.
IN_TO_CM = 2.54
BEZIER_SEGMENTS = 24

PARAM_ORDER = [
    ("plate_t", "0.1875 in", "in", "Specified. Plate thickness — 3/16 in"),
    (
        "overall_length",
        "4.90 in",
        "in",
        "PHOTO EST. +/- 1/8 in. Overall length; left of tab to right end",
    ),
    (
        "wide_end_height",
        "2.40 in",
        "in",
        "PHOTO EST. +/- 1/8 in. Right / wide end height",
    ),
    ("corner_r", "0.06 in", "in", "PHOTO EST. Right-end outside corner radius"),
    (
        "tab_r",
        "0.875 in",
        "in",
        "PHOTO EST. +/- 1/8 in. Left ear / tab radius",
    ),
    (
        "tab_cx",
        "0.875 in",
        "in",
        "PHOTO EST. Tab arc center X (left tip at tab_cx - tab_r)",
    ),
    (
        "tab_cy",
        "2.00 in",
        "in",
        "PHOTO EST. Tab arc center Y (tab top at tab_cy + tab_r)",
    ),
    (
        "tab_arc_start_deg",
        "240",
        "",
        "PHOTO EST. Tab arc start angle; deg from +X CCW; bottom blend meets here",
    ),
    (
        "tab_arc_end_deg",
        "80",
        "",
        "PHOTO EST. Tab arc end angle; deg from +X CCW; top spline starts here",
    ),
    (
        "bottom_blend_x",
        "1.50 in",
        "in",
        "PHOTO EST. X where the straight bottom starts curving up into the tab",
    ),
    (
        "bottom_handle",
        "0.80 in",
        "in",
        "PHOTO EST. Bottom blend Bezier handle length",
    ),
    (
        "top_straight_x",
        "4.00 in",
        "in",
        "PHOTO EST. X where the top S-curve meets the wide-end top",
    ),
    (
        "top_handle",
        "1.00 in",
        "in",
        "PHOTO EST. Top S-curve Bezier handle length",
    ),
    (
        "hole_half_d",
        "0.500 in",
        "in",
        "Specified. Single 1/2 in hole in the left tab",
    ),
    (
        "hole_half_x",
        "0.90 in",
        "in",
        "PHOTO EST. +/- 1/8 in. 1/2 in hole center X",
    ),
    (
        "hole_half_y",
        "2.15 in",
        "in",
        "PHOTO EST. +/- 1/8 in. 1/2 in hole center Y",
    ),
    (
        "hole_58_d",
        "0.65625 in",
        "in",
        "MEASURED mate ~0.66 in; set to 21/32 (0.65625) clearance for 5/8 bolt",
    ),
    (
        "hole_58_y",
        "1.05 in",
        "in",
        "PHOTO EST. +/- 1/8 in. Bolt-hole pair center Y (both holes)",
    ),
    (
        "hole_58_mid_x",
        "3.33125 in",
        "in",
        "PHOTO EST. Bolt-hole pair midpoint X (held from the original photo-trace pair)",
    ),
    (
        "hole_58_spacing",
        "1.000 in",
        "in",
        "MEASURED. Mate hole C-C from 0.66 dia, 0.322 edge gap, 1.666 outside",
    ),
    (
        "hole_58_left_x",
        "hole_58_mid_x - hole_58_spacing / 2",
        "in",
        "Computed. Left 21/32 hole center X",
    ),
    (
        "hole_58_right_x",
        "hole_58_mid_x + hole_58_spacing / 2",
        "in",
        "Computed. Right 21/32 hole center X",
    ),
    ("tab_top_y", "tab_cy + tab_r", "in", "Computed. Top of left tab"),
]

DO = adsk.fusion.DimensionOrientations


def run(_context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Switch to the Design workspace (not Render/Drawings) and run again.")
            return

        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        try:
            design.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType
        except Exception:
            try:
                design.designIntent = adsk.fusion.DesignIntentTypes.AssemblyDesignIntentType
            except Exception:
                pass
        try:
            design.fusionUnitsManager.defaultLengthUnits = "in"
        except Exception:
            pass

        apply_csv_overrides()
        add_parameters(design)

        root = design.rootComponent
        try:
            root.name = "KTECH_TEMPLATE_BRACKET"
        except Exception:
            pass

        already = False
        for i in range(root.occurrences.count):
            if "01_TEMPLATE_BRACKET" in root.occurrences.item(i).name:
                already = True
                break
        if already:
            ui.messageBox(
                "This document already has the template bracket in it.\n\n"
                "File → New Design, then Run the script again after you edit parameters."
            )
            return

        plate = add_component(root, "01_TEMPLATE_BRACKET")
        build_bracket(plate, design)

        dxf_dir = os.path.join(SCRIPT_DIR, "dxf_out")
        n_dxf = export_plate_dxfs(design, dxf_dir)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        p = design.userParameters
        def _in(name):
            try:
                return p.itemByName(name).value / IN_TO_CM
            except Exception:
                return float("nan")

        ui.messageBox(
            "Template bracket is in this document.\n\n"
            "3/16 in plate (plate_t = {:.4f} in)\n"
            "Holes: one 1/2 in at ({:.3f}, {:.3f}), "
            "two 21/32 in (5/8 bolt clearance) at ({:.3f}, {:.3f}) and ({:.3f}, {:.3f})\n"
            "Overall {:.3f} in long × {:.3f} in wide-end / {:.3f} in tab top\n\n"
            "Exported {} plate DXF(s) to:\n{}\n\n"
            "OUTLINE AND HOLE LOCATIONS ARE PHOTO ESTIMATES (about +/- 1/8 in) "
            "from a paper template. Caliper the paper, edit the named user "
            "parameters (or the CSV), then New Design and re-run before a "
            "production cut. Kerf is not compensated.\n\n"
            "Save as KTECH_TEMPLATE_BRACKET.".format(
                _in("plate_t"),
                _in("hole_half_x"),
                _in("hole_half_y"),
                _in("hole_58_left_x"),
                _in("hole_58_y"),
                _in("hole_58_right_x"),
                _in("hole_58_y"),
                _in("overall_length"),
                _in("wide_end_height"),
                _in("tab_top_y"),
                n_dxf,
                dxf_dir,
            )
        )
    except Exception:
        if ui:
            ui.messageBox("KTECH_Template_Bracket failed:\n{}".format(traceback.format_exc()))


def apply_csv_overrides():
    """Load KTECH_Template_Bracket_parameters.csv into PARAM_ORDER expressions."""
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "KTECH_Template_Bracket_parameters.csv")
    if not os.path.isfile(params_path):
        return
    with open(params_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("name") or "").strip()
            expr = (row.get("expression") or "").strip()
            unit = (row.get("unit") or "").strip()
            comment = (row.get("comment") or "").strip()
            if name not in by_name:
                continue
            unit = unit or by_name[name][2] or "in"
            comment = comment or by_name[name][3]
            by_name[name] = (name, _expr_with_unit(expr, unit), unit, comment)
    PARAM_ORDER[:] = [by_name[row[0]] for row in PARAM_ORDER]


def _expr_with_unit(expr, unit):
    expr = expr.strip()
    if not expr:
        return expr
    if any(ch.isalpha() for ch in expr):
        return expr
    if not unit:
        return expr
    if expr.endswith(unit) or " " in expr:
        return expr
    return "{} {}".format(expr, unit)


def add_parameters(design):
    params = design.userParameters
    for name, expr, unit, comment in PARAM_ORDER:
        try:
            existing = params.itemByName(name)
            value = adsk.core.ValueInput.createByString(expr)
            if existing:
                existing.expression = expr
                existing.comment = comment
            elif unit == "":
                params.add(
                    name,
                    adsk.core.ValueInput.createByReal(float(str(expr).split()[0])),
                    "",
                    comment,
                )
            else:
                params.add(name, value, unit if unit else "in", comment)
        except Exception:
            continue


def param_cm(design, name):
    return design.userParameters.itemByName(name).value


def param_in(design, name):
    return param_cm(design, name) / IN_TO_CM


def add_component(parent, name):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def _pt(x_in, y_in):
    return adsk.core.Point3D.create(x_in * IN_TO_CM, y_in * IN_TO_CM, 0)


def _unit(vx, vy):
    n = math.hypot(vx, vy)
    if n < 1e-12:
        return (0.0, 0.0)
    return (vx / n, vy / n)


def _cw_tangent(deg):
    a = math.radians(deg)
    return (math.sin(a), -math.cos(a))


def _polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _bezier(p0, p1, p2, p3, n):
    pts = []
    for i in range(n + 1):
        t = float(i) / n
        u = 1.0 - t
        x = (
            u * u * u * p0[0]
            + 3.0 * u * u * t * p1[0]
            + 3.0 * u * t * t * p2[0]
            + t * t * t * p3[0]
        )
        y = (
            u * u * u * p0[1]
            + 3.0 * u * u * t * p1[1]
            + 3.0 * u * t * t * p2[1]
            + t * t * t * p3[1]
        )
        pts.append((x, y))
    return pts


def _add_fitted_spline(sk, pts_in):
    col = adsk.core.ObjectCollection.create()
    for x, y in pts_in:
        col.add(_pt(x, y))
    return sk.sketchCurves.sketchFittedSplines.add(col)


def build_bracket(comp, design):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_TEMPLATE_BRACKET"
    sk.isComputeDeferred = True
    _draw_outline(sk, design)
    _draw_holes(sk, design)
    sk.isComputeDeferred = False

    _dimension_holes(sk, design)

    prof = _cut_profile(sk)
    if not prof:
        raise RuntimeError("Could not find the bracket profile (outline + 3 holes).")

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("plate_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_TEMPLATE_BRACKET"
    ext.bodies.item(0).name = "TEMPLATE_BRACKET"


def _draw_outline(sk, design):
    L = param_in(design, "overall_length")
    H = param_in(design, "wide_end_height")
    r = param_in(design, "corner_r")
    if r < 0:
        r = 0.0
    if r > min(L, H) / 2.0:
        r = min(L, H) / 2.0

    tab_r = param_in(design, "tab_r")
    tab_cx = param_in(design, "tab_cx")
    tab_cy = param_in(design, "tab_cy")
    # Unitless user parameters: .value is the raw degree number (do not use param_in).
    start_deg = design.userParameters.itemByName("tab_arc_start_deg").value
    end_deg = design.userParameters.itemByName("tab_arc_end_deg").value

    bottom_blend_x = param_in(design, "bottom_blend_x")
    bottom_handle = param_in(design, "bottom_handle")
    top_straight_x = param_in(design, "top_straight_x")
    top_handle = param_in(design, "top_handle")

    tab_start = _polar(tab_cx, tab_cy, tab_r, start_deg)
    tab_end = _polar(tab_cx, tab_cy, tab_r, end_deg)

    # Bottom Bezier: (bottom_blend_x, 0) heading left, into tab_start along CW tangent.
    t0 = (-1.0, 0.0)
    t3 = _cw_tangent(start_deg)
    p0 = (bottom_blend_x, 0.0)
    p3 = tab_start
    p1 = (p0[0] + bottom_handle * t0[0], p0[1] + bottom_handle * t0[1])
    p2 = (p3[0] - bottom_handle * t3[0], p3[1] - bottom_handle * t3[1])
    _add_fitted_spline(sk, _bezier(p0, p1, p2, p3, BEZIER_SEGMENTS))

    # Tab arc, clockwise from start_deg to end_deg.
    sweep_cw = (start_deg - end_deg) % 360.0
    if sweep_cw <= 1e-9:
        sweep_cw = 360.0
    sk.sketchCurves.sketchArcs.addByCenterStartSweep(
        _pt(tab_cx, tab_cy),
        _pt(tab_start[0], tab_start[1]),
        -math.radians(sweep_cw),
    )

    # Top S-curve Bezier: tab_end heading along CW tangent, to (top_straight_x, H) horizontal.
    t0 = _cw_tangent(end_deg)
    t3 = (1.0, 0.0)
    p0 = tab_end
    p3 = (top_straight_x, H)
    p1 = (p0[0] + top_handle * t0[0], p0[1] + top_handle * t0[1])
    p2 = (p3[0] - top_handle * t3[0], p3[1] - top_handle * t3[1])
    _add_fitted_spline(sk, _bezier(p0, p1, p2, p3, BEZIER_SEGMENTS))

    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs

    # Top straight to the start of the top-right fillet.
    lines.addByTwoPoints(_pt(top_straight_x, H), _pt(L - r, H))
    if r > 1e-6:
        # Top-right fillet, CW 90° from (L-r, H) to (L, H-r).
        arcs.addByCenterStartSweep(_pt(L - r, H - r), _pt(L - r, H), -math.pi / 2.0)
        # Right edge.
        lines.addByTwoPoints(_pt(L, H - r), _pt(L, r))
        # Bottom-right fillet, CW 90° from (L, r) to (L-r, 0).
        arcs.addByCenterStartSweep(_pt(L - r, r), _pt(L, r), -math.pi / 2.0)
        # Bottom straight back to the blend start.
        lines.addByTwoPoints(_pt(L - r, 0.0), _pt(bottom_blend_x, 0.0))
    else:
        lines.addByTwoPoints(_pt(L - r, H), _pt(L, H))
        lines.addByTwoPoints(_pt(L, H), _pt(L, 0.0))
        lines.addByTwoPoints(_pt(L, 0.0), _pt(bottom_blend_x, 0.0))


def _draw_holes(sk, design):
    circles = sk.sketchCurves.sketchCircles
    circles.addByCenterRadius(
        _pt(param_in(design, "hole_half_x"), param_in(design, "hole_half_y")),
        param_cm(design, "hole_half_d") / 2.0,
    )
    circles.addByCenterRadius(
        _pt(param_in(design, "hole_58_left_x"), param_in(design, "hole_58_y")),
        param_cm(design, "hole_58_d") / 2.0,
    )
    circles.addByCenterRadius(
        _pt(param_in(design, "hole_58_right_x"), param_in(design, "hole_58_y")),
        param_cm(design, "hole_58_d") / 2.0,
    )


def _dimension_holes(sk, design):
    """Drive hole diameters and center locations with named user parameters."""
    origin = None
    try:
        origin = sk.originPoint
    except Exception:
        origin = None
    if origin is None:
        return

    holes = []
    for i in range(sk.sketchCurves.sketchCircles.count):
        holes.append(sk.sketchCurves.sketchCircles.item(i))
    if len(holes) < 3:
        return

    # Identify by center X (1/2 in hole is the leftmost).
    holes_sorted = sorted(holes, key=lambda c: c.centerSketchPoint.geometry.x)
    half_circ = holes_sorted[0]
    left_58 = holes_sorted[1]
    right_58 = holes_sorted[2]

    dims = sk.sketchDimensions

    def _dia(circ, expr, tx, ty):
        try:
            d = dims.addDiameterDimension(circ, _pt(tx, ty))
            d.parameter.expression = expr
        except Exception:
            pass

    def _hv(circ, hexpr, vexpr, tx, ty):
        try:
            dh = dims.addDistanceDimension(
                origin,
                circ.centerSketchPoint,
                DO.HorizontalDimensionOrientation,
                _pt(tx, ty),
            )
            dh.parameter.expression = hexpr
        except Exception:
            pass
        try:
            dv = dims.addDistanceDimension(
                origin,
                circ.centerSketchPoint,
                DO.VerticalDimensionOrientation,
                _pt(tx + 0.3, ty + 0.3),
            )
            dv.parameter.expression = vexpr
        except Exception:
            pass

    _dia(half_circ, "hole_half_d", param_in(design, "hole_half_x") + 0.45, param_in(design, "hole_half_y") + 0.35)
    _hv(half_circ, "hole_half_x", "hole_half_y", param_in(design, "hole_half_x") / 2.0, -0.35)

    _dia(left_58, "hole_58_d", param_in(design, "hole_58_left_x") - 0.15, param_in(design, "hole_58_y") - 0.55)
    _hv(left_58, "hole_58_left_x", "hole_58_y", param_in(design, "hole_58_left_x") / 2.0, -0.70)

    _dia(right_58, "hole_58_d", param_in(design, "hole_58_right_x") + 0.45, param_in(design, "hole_58_y") - 0.55)
    _hv(right_58, "hole_58_right_x", "hole_58_y", param_in(design, "hole_58_right_x") + 0.4, -0.70)


def _cut_profile(sk):
    """Prefer the profile with an outer loop plus three hole loops."""
    best = None
    best_score = (-1, -1.0)
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        n_loops = prof.profileLoops.count
        area = 0.0
        try:
            area = abs(prof.area)
        except Exception:
            area = 0.0
        # 4 loops = outline + 3 holes. Fall back to the largest 1-loop profile.
        score = (1 if n_loops == 4 else 0, n_loops, area)
        if score > best_score:
            best_score = score
            best = prof
    return best


# ---------------------------------------------------------------------------
# DXF export — top-face profile sketch (same pattern as rear clip)
# ---------------------------------------------------------------------------

def export_plate_dxfs(design, out_dir):
    """Create a flat sketch of each plate body's largest planar face and save as DXF."""
    if not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir)
        except Exception:
            return 0

    root = design.rootComponent
    bodies_by_name = {}
    _collect_bodies(root, bodies_by_name)

    count = 0
    for name in PLATE_BODY_NAMES:
        entry = bodies_by_name.get(name)
        if not entry:
            continue
        body, owner = entry
        try:
            path = os.path.join(out_dir, "{}.dxf".format(name))
            if _export_body_top_dxf(owner, body, name, path):
                count += 1
        except Exception:
            continue
    return count


def _collect_bodies(comp, out):
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        if b.name:
            out[b.name] = (b, comp)
    for i in range(comp.occurrences.count):
        _collect_bodies(comp.occurrences.item(i).component, out)


def _export_body_top_dxf(comp, body, name, path):
    """Sketch the largest planar face outline and saveAsDXF (laser flat pattern)."""
    face = _largest_planar_face(body)
    if not face:
        return False

    try:
        sk = comp.sketches.add(face)
    except Exception:
        try:
            sk = comp.sketches.add(comp.xYConstructionPlane)
            entities = adsk.core.ObjectCollection.create()
            entities.add(face)
            sk.project(entities)
        except Exception:
            return False

    sk.name = "SK_DXF_{}".format(name)

    try:
        sk.saveAsDXF(path)
        return True
    except Exception:
        pass
    try:
        em = adsk.fusion.Design.cast(comp.parentDesign).exportManager
        opts = em.createDXF2DExportOptions(sk, path)
        em.execute(opts)
        return True
    except Exception:
        return False


def _largest_planar_face(body):
    best = None
    best_a = -1.0
    for i in range(body.faces.count):
        face = body.faces.item(i)
        try:
            if face.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
                continue
        except Exception:
            continue
        try:
            a = face.area
        except Exception:
            a = 0.0
        if a > best_a:
            best_a = a
            best = face
    return best
