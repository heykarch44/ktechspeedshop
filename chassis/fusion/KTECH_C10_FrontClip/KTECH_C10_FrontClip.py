# Ktech C10 front clip for Autodesk Fusion 360
#
# Install
#   1. Fusion → Utilities → Add-Ins → Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_C10_FrontClip)
#   4. Run on the chassis doc (02_CLIP_FRONT empty) or a New Design.
#
# Design intent (2026-11-25 box sketches)
#   Raised flat 6 in / 34 in OD plate-box rail through steering + A-arms.
#   Narrowed 28 x 4 in nose ahead of the rack with a single 23 deg / 7 in
#   plan-view kick (3 in inset/side, constant ~2.44 box width, top ramps
#   2 in, bottom level, ribs at bend lines). Angular cab drop 6.57 over
#   12 in (x=8→20), finished before cab_f_x. Aft slip sized to purchased
#   2x5 center tube (FLAG: was 2x6). Hanging LCA mount + ~1.8 in UCA tower.
#
# Coordinates (Fusion Y-up) — same as KTECH_C10_Chassis_Setup
#   Origin = front axle × ground × frame centerline
#   +X = rear   +Y = up   +Z = passenger (right)

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

IN_TO_CM = 2.54
DO = adsk.fusion.DimensionOrientations

PARAM_ORDER = [
    ("tube_w", "2 in", "in", "A500 / slip tube width across the car"),
    (
        "cab_rail_h",
        "5 in",
        "in",
        "FLAG: purchased center spine is now 2x5 (was 2x6). Aft slip must match",
    ),
    ("cab_rail_bottom", "3.5 in", "in", "Cab/center section bottom at design ride"),
    ("rail_bottom", "cab_rail_bottom", "in", "COMPAT alias → cab_rail_bottom"),
    (
        "front_rail_bottom",
        "10.07 in",
        "in",
        "Front-clip rail bottom at the arms (design ride)",
    ),
    (
        "front_rail_h",
        "6 in",
        "in",
        "Flat 6 in rail through steering / A-arms / engine (no arch)",
    ),
    (
        "nose_rail_h",
        "4 in",
        "in",
        "Nose height ahead of kick (top ramps 2 in over kick; bottom level)",
    ),
    (
        "cab_drop",
        "front_rail_bottom - cab_rail_bottom",
        "in",
        "Angular drop amount (6.57 at defaults)",
    ),
    ("wall", "0.188 in", "in", "A500 wall (center tube ref)"),
    ("clip_t", "0.188 in", "in", "Laser plate thickness"),
    ("clip_clear", "0.030 in", "in", "Per-side slip clearance"),
    (
        "box_od_w",
        "tube_w + 2 * clip_clear + 2 * clip_t",
        "in",
        "Constant plate-box outer width (~2.44) through kick",
    ),
    ("slip_id_w", "tube_w + 2 * clip_clear", "in", "Slip inside width"),
    (
        "slip_id_h",
        "cab_rail_h + 2 * clip_clear",
        "in",
        "Slip inside height — sized to 2x5 center (NOT rear 2x6)",
    ),
    (
        "box_od_h_front",
        "front_rail_h + 2 * clip_clear + 2 * clip_t",
        "in",
        "Box outer height on raised front section",
    ),
    (
        "box_od_h_cab",
        "slip_id_h + 2 * clip_t",
        "in",
        "Box outer height on cab/slip section",
    ),
    (
        "rail_cl",
        "16.0 in",
        "in",
        "Literal. 34 in OD through arms/engine. Uncoupled from core_width",
    ),
    ("rail_cl_nose", "13.0 in", "in", "28 in OD nose"),
    (
        "core_width",
        "33.5 in",
        "in",
        "TAPED. Core-mount C-C (28 in nose + 2*pads) — NOT rail spacing",
    ),
    (
        "core_pad_outboard",
        "2.75 in",
        "in",
        "Outboard core pad per side from 28 in nose outside face",
    ),
    ("core_x", "-33 in", "in", "PLACEHOLDER. Core vs front axle"),
    ("core_to_mid", "55 in", "in", "TAPED. Core to cab-front along rail"),
    (
        "cab_f_x",
        "core_x + core_to_mid",
        "in",
        "Cab front mount X — drop must finish before this",
    ),
    ("nose_tip_x", "-34 in", "in", "PLACEHOLDER. Forward tip of nose"),
    (
        "kick_start_x",
        "-8 in",
        "in",
        "Plan-view kick start (ahead of rack). Between core and axle",
    ),
    ("kick_len", "7 in", "in", "Single faceted plan-view kick length"),
    (
        "kick_end_x",
        "kick_start_x + kick_len",
        "in",
        "Kick ends just ahead of steering/rack / front axle",
    ),
    ("kick_angle_deg", "23", "", "Plan-view kick angle (deg)"),
    ("kick_inset", "3 in", "in", "Inward per side through kick"),
    ("drop_start_x", "8 in", "in", "Side-view angular drop start"),
    (
        "drop_end_x",
        "20 in",
        "in",
        "Drop finished (cab height) BEFORE cab_f_x",
    ),
    ("slip_overlap", "8 in", "in", "Slip-fit overlap over 2x5 center tube"),
    (
        "center_tube_front_x",
        "drop_end_x",
        "in",
        "Forward end of purchased 2x5 center tube",
    ),
    (
        "clip_aft_x",
        "center_tube_front_x + slip_overlap",
        "in",
        "Aft end of front-clip plate box",
    ),
    ("tab_width", "0.750 in", "in", "PLACEHOLDER. Tab width"),
    ("tab_length", "clip_t", "in", "Tab length = mating plate thickness"),
    ("slot_clear", "0.010 in", "in", "PLACEHOLDER. Slot oversize vs tab"),
    ("tab_pitch", "4.000 in", "in", "PLACEHOLDER. Tab pitch"),
    ("lca_pivot_z", "13.50 in", "in", "Lower inner pivot lateral off CL"),
    (
        "lca_pivot_y",
        "8.07 in",
        "in",
        "Lower inner pivot height. 2.00 hang below front_rail_bottom",
    ),
    (
        "lca_hang",
        "front_rail_bottom - lca_pivot_y",
        "in",
        "Hanging drop-mount below rail bottom",
    ),
    ("uca_pivot_z", "15.50 in", "in", "Upper inner pivot lateral off CL"),
    (
        "uca_pivot_y",
        "17.88 in",
        "in",
        "Upper inner pivot height. ~1.81 tower above rail top (no arch)",
    ),
    (
        "uca_tower",
        "uca_pivot_y - (front_rail_bottom + front_rail_h)",
        "in",
        "Upper tower above rail top",
    ),
    ("pivot_stub_t", "0.375 in", "in", "PLACEHOLDER. Pivot stub plate thickness"),
    ("pivot_stub_w", "2.500 in", "in", "PLACEHOLDER. Pivot stub width along X"),
    ("core_pad_t", "0.250 in", "in", "PLACEHOLDER. Core pad plate thickness"),
    ("core_pad_w", "3.000 in", "in", "PLACEHOLDER. Core pad fore-aft width"),
    ("core_pad_l", "2.750 in", "in", "Core pad lateral length"),
]


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
            root.name = "KTECH_C10_FRONT_CLIP"
        except Exception:
            pass

        already = False
        for i in range(root.occurrences.count):
            if "FC_01_CENTER_TUBE" in root.occurrences.item(i).name:
                already = True
                break
        if already:
            ui.messageBox(
                "This document already has the front clip in it.\n\n"
                "File → New Design, then Run the script again."
            )
            return

        mark = add_component(root, "00_ORIGIN")
        mark_origin(mark)

        skel = add_component(root, "00_SKELETON")
        center = add_component(root, "FC_01_CENTER_TUBE")
        rail_rh = add_component(root, "FC_02_RAIL_RH")
        rail_lh = add_component(root, "FC_02_RAIL_LH")
        pads = add_component(root, "FC_03_CORE_PADS")
        pivots = add_component(root, "FC_04_PIVOTS")
        add_component(root, "FC_05_FIXTURE")

        draw_layout_sketches(skel)
        build_center_tube_ref(center)
        build_rail_side(rail_rh, passenger=True)
        build_rail_side(rail_lh, passenger=False)
        build_core_pads(pads)
        build_pivot_geometry(pivots)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        ui.messageBox(
            "Front clip built in this document.\n\n"
            "rail_cl = 16.0 (34 in OD through arms/engine).\n"
            "Nose: rail_cl_nose = 13.0 (28 in OD) x 4 in tall; "
            "23 deg / 7 in kick; bottom level at front_rail_bottom.\n"
            "Raised flat 6 in rail 10.07–16.07; drop x=8→20 before cab_f_x.\n"
            "FLAG: aft slip sized to 2x5 center (cab_rail_h=5) — was 2x6.\n"
            "core_width 33.5 is core-mount C-C, not rail spacing.\n"
            "LCA hang pivot (13.50, 8.07); UCA tower pivot (15.50, 17.88).\n\n"
            "Fit view if empty. Save as KTECH_C10_FRONT_CLIP "
            "(or keep on the chassis doc / 02_CLIP_FRONT)."
        )
    except Exception:
        if ui:
            ui.messageBox("KTECH_C10_FrontClip failed:\n{}".format(traceback.format_exc()))


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def apply_csv_overrides():
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "parameters.csv")
    if not os.path.isfile(params_path):
        return
    with open(params_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("name") or "").strip()
            if name not in by_name:
                continue
            expr = (row.get("expression") or "").strip()
            unit = (row.get("unit") or by_name[name][2] or "in").strip()
            comment = (row.get("comment") or by_name[name][3]).strip()
            by_name[name] = (name, _expr_with_unit(expr, unit), unit, comment)
    PARAM_ORDER[:] = [by_name[row[0]] for row in PARAM_ORDER]


def _expr_with_unit(expr, unit):
    expr = expr.strip()
    if not expr:
        return expr
    if any(ch.isalpha() for ch in expr):
        return expr
    if unit and (expr.endswith(unit) or " " in expr):
        return expr
    if not unit:
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
            elif name == "kick_angle_deg":
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


def add_component(parent, name):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def mark_origin(comp):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_ORIGIN"
    sk.sketchCurves.sketchLines.addCenterPointRectangle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(7.62, 7.62, 0),
    )
    if sk.profiles.count < 1:
        return
    extrudes = comp.features.extrudeFeatures
    dist = adsk.core.ValueInput.createByString("6 in")
    ext = extrudes.addSimple(
        sk.profiles.item(0), dist, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext.bodies.item(0).name = "ORIGIN_CUBE"


def _largest_profile(sk):
    best = sk.profiles.item(0)
    best_a = 0.0
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        try:
            a = p.areaProperties().area
        except Exception:
            a = 0.0
        if a >= best_a:
            best_a = a
            best = p
    return best


# ---------------------------------------------------------------------------
# Layout sketches
# ---------------------------------------------------------------------------

def draw_layout_sketches(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)

    # --- Side (XY) ---
    side = comp.sketches.add(comp.xYConstructionPlane)
    side.name = "SK_SIDE"
    _draw_side_rail_outline(side, design, z_world=0.0, construction=True)

    # --- Top / plan (XZ) ---
    top = comp.sketches.add(comp.xZConstructionPlane)
    top.name = "SK_TOP"
    _draw_plan_kick(top, design, y_world=0.0, construction=True)

    # --- Front (YZ at axle) ---
    front = comp.sketches.add(comp.yZConstructionPlane)
    front.name = "SK_FRONT"
    _draw_front_sections(front, design)


def _draw_side_rail_outline(sk, design, z_world, construction=False):
    """Side-view outer rail outline: nose → kick top ramp → raised → drop → cab."""
    pts_top = _side_profile_xy(design, top=True)
    pts_bot = _side_profile_xy(design, top=False)
    loop = pts_top + list(reversed(pts_bot))
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    prev = None
    first = None
    for wx, wy in loop:
        sp = sk.modelToSketchSpace(adsk.core.Point3D.create(wx, wy, z_world))
        if prev is None:
            first = sp
            prev = sp
            continue
        ln = lines.addByTwoPoints(prev, sp)
        if construction:
            ln.isConstruction = True
        prev = sp
    if first is not None and prev is not None:
        ln = lines.addByTwoPoints(prev, first)
        if construction:
            ln.isConstruction = True
    # Ground + axle markers
    g0 = sk.modelToSketchSpace(adsk.core.Point3D.create(-40 * IN_TO_CM, 0, z_world))
    g1 = sk.modelToSketchSpace(adsk.core.Point3D.create(40 * IN_TO_CM, 0, z_world))
    ax0 = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, z_world))
    ax1 = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 25 * IN_TO_CM, z_world))
    for a, b in ((g0, g1), (ax0, ax1)):
        ln = lines.addByTwoPoints(a, b)
        ln.isConstruction = True
    sk.isComputeDeferred = False


def _side_profile_xy(design, top=True):
    """(x,y) in cm for side-plate / rail outline (inside height span style)."""
    tip = param_cm(design, "nose_tip_x")
    ks = param_cm(design, "kick_start_x")
    ke = param_cm(design, "kick_end_x")
    ds = param_cm(design, "drop_start_x")
    de = param_cm(design, "drop_end_x")
    aft = param_cm(design, "clip_aft_x")
    frb = param_cm(design, "front_rail_bottom")
    frh = param_cm(design, "front_rail_h")
    nrh = param_cm(design, "nose_rail_h")
    crb = param_cm(design, "cab_rail_bottom")
    crh = param_cm(design, "cab_rail_h")
    clear = param_cm(design, "clip_clear")

    y_bot_f = frb - clear
    y_top_nose = frb + nrh + clear
    y_top_f = frb + frh + clear
    y_bot_c = crb - clear
    y_top_c = crb + crh + clear

    if top:
        return [
            (tip, y_top_nose),
            (ks, y_top_nose),
            (ke, y_top_f),
            (ds, y_top_f),
            (de, y_top_c),
            (aft, y_top_c),
        ]
    return [
        (tip, y_bot_f),
        (ks, y_bot_f),
        (ke, y_bot_f),
        (ds, y_bot_f),
        (de, y_bot_c),
        (aft, y_bot_c),
    ]


def _draw_plan_kick(sk, design, y_world, construction=True):
    """Plan-view rail CL and outer faces through nose / kick / straight."""
    tip = param_cm(design, "nose_tip_x")
    ks = param_cm(design, "kick_start_x")
    ke = param_cm(design, "kick_end_x")
    aft = param_cm(design, "clip_aft_x")
    cl_n = param_cm(design, "rail_cl_nose")
    cl = param_cm(design, "rail_cl")
    half = param_cm(design, "box_od_w") / 2.0

    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines

    def add_poly(pts):
        prev = None
        for wx, wz in pts:
            sp = sk.modelToSketchSpace(adsk.core.Point3D.create(wx, y_world, wz))
            if prev is not None:
                ln = lines.addByTwoPoints(prev, sp)
                if construction:
                    ln.isConstruction = True
            prev = sp

    # Vehicle CL
    add_poly([(tip, 0.0), (aft, 0.0)])
    # RH rail CL through kick
    add_poly([(tip, cl_n), (ks, cl_n), (ke, cl), (aft, cl)])
    # RH outer face
    add_poly([
        (tip, cl_n + half),
        (ks, cl_n + half),
        (ke, cl + half),
        (aft, cl + half),
    ])
    # LH rail CL + outer (mirror)
    add_poly([(tip, -cl_n), (ks, -cl_n), (ke, -cl), (aft, -cl)])
    add_poly([
        (tip, -(cl_n + half)),
        (ks, -(cl_n + half)),
        (ke, -(cl + half)),
        (aft, -(cl + half)),
    ])
    sk.isComputeDeferred = False


def _draw_front_sections(sk, design):
    """Front-view rectangles: nose, raised rail, cab section + pivots."""
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    tw = param_cm(design, "tube_w")
    cl_n = param_cm(design, "rail_cl_nose")
    cl = param_cm(design, "rail_cl")
    frb = param_cm(design, "front_rail_bottom")
    frh = param_cm(design, "front_rail_h")
    nrh = param_cm(design, "nose_rail_h")
    crb = param_cm(design, "cab_rail_bottom")
    crh = param_cm(design, "cab_rail_h")
    lz = param_cm(design, "lca_pivot_z")
    ly = param_cm(design, "lca_pivot_y")
    uz = param_cm(design, "uca_pivot_z")
    uy = param_cm(design, "uca_pivot_y")

    def rect(cz, y0, y1):
        z0, z1 = cz - tw / 2.0, cz + tw / 2.0
        pts = [
            (0.0, y0, z0),
            (0.0, y0, z1),
            (0.0, y1, z1),
            (0.0, y1, z0),
        ]
        prev = None
        first = None
        for p in pts:
            sp = sk.modelToSketchSpace(adsk.core.Point3D.create(*p))
            if prev is None:
                first = sp
                prev = sp
                continue
            ln = lines.addByTwoPoints(prev, sp)
            ln.isConstruction = True
            prev = sp
        ln = lines.addByTwoPoints(prev, first)
        ln.isConstruction = True

    for sign in (1.0, -1.0):
        rect(sign * cl_n, frb, frb + nrh)
        rect(sign * cl, frb, frb + frh)
        rect(sign * cl, crb, crb + crh)
        for z, y in ((sign * lz, ly), (sign * uz, uy)):
            pt = sk.modelToSketchSpace(adsk.core.Point3D.create(0.0, y, z))
            sk.sketchPoints.add(pt)
    sk.isComputeDeferred = False


# ---------------------------------------------------------------------------
# Center tube reference (2x5 slip target)
# ---------------------------------------------------------------------------

def build_center_tube_ref(comp):
    """Semi-transparent reference for purchased 2x5 under the aft slip."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    x0 = param_cm(design, "center_tube_front_x")
    x1 = param_cm(design, "clip_aft_x")
    if x1 <= x0 + 0.05 * IN_TO_CM:
        return

    sk = comp.sketches.add(comp.yZConstructionPlane)
    sk.name = "SK_CENTER_2x5"
    # Temporarily offset sketch isn't needed — draw at X=0 then extrude from x0.
    # Draw section at world X via modelToSketch on YZ (X ignored → sketch at 0).
    rb = param_cm(design, "cab_rail_bottom")
    th = param_cm(design, "cab_rail_h")
    tw = param_cm(design, "tube_w")
    cl = param_cm(design, "rail_cl")
    wall = param_cm(design, "wall")

    sk.isComputeDeferred = True
    for sign, tag in ((1.0, "RH"), (-1.0, "LH")):
        cy = rb + th / 2.0
        cz = cl * sign
        oc = sk.modelToSketchSpace(adsk.core.Point3D.create(0, cy, cz))
        or_ = sk.modelToSketchSpace(
            adsk.core.Point3D.create(0, cy + th / 2.0, cz + sign * tw / 2.0)
        )
        ir = sk.modelToSketchSpace(
            adsk.core.Point3D.create(
                0, cy + th / 2.0 - wall, cz + sign * (tw / 2.0 - wall)
            )
        )
        sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, or_)
        sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, ir)
    sk.isComputeDeferred = False

    # Extrude both ring profiles along +X covering the slip region.
    # Find ring profiles (2 loops) and extrude each.
    extrudes = comp.features.extrudeFeatures
    length = adsk.core.ValueInput.createByReal(x1 - x0)
    # Move start: use two-sided from YZ then cut? Simpler: extrude from YZ by
    # offset — create plane at x0.
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x0))
    pl = planes.add(pin)
    pl.name = "PL_CENTER_TUBE_X0"

    sk2 = comp.sketches.add(pl)
    sk2.name = "SK_CENTER_2x5_AT_X"
    sk2.isComputeDeferred = True
    bodies_made = 0
    for sign in (1.0, -1.0):
        cy = rb + th / 2.0
        cz = cl * sign
        oc = sk2.modelToSketchSpace(adsk.core.Point3D.create(x0, cy, cz))
        or_ = sk2.modelToSketchSpace(
            adsk.core.Point3D.create(x0, cy + th / 2.0, cz + sign * tw / 2.0)
        )
        ir = sk2.modelToSketchSpace(
            adsk.core.Point3D.create(
                x0, cy + th / 2.0 - wall, cz + sign * (tw / 2.0 - wall)
            )
        )
        sk2.sketchCurves.sketchLines.addCenterPointRectangle(oc, or_)
        sk2.sketchCurves.sketchLines.addCenterPointRectangle(oc, ir)
    sk2.isComputeDeferred = False

    for i in range(sk2.profiles.count):
        prof = sk2.profiles.item(i)
        if prof.profileLoops.count != 2:
            continue
        ext_in = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_in.setDistanceExtent(False, length)
        ext = extrudes.add(ext_in)
        ext.name = "EX_CENTER_2x5_{}".format(bodies_made)
        body = ext.bodies.item(0)
        body.name = "CENTER_2x5_{}".format("RH" if bodies_made == 0 else "LH")
        try:
            body.opacity = 0.35
        except Exception:
            pass
        bodies_made += 1


# ---------------------------------------------------------------------------
# Plate-box rails
# ---------------------------------------------------------------------------

def build_rail_side(comp, passenger=True):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"

    # Segment solids: nose, kick facet, raised, drop, slip.
    _build_segment_box(
        comp, design, side, sign,
        role="NOSE",
        x0=param_cm(design, "nose_tip_x"),
        x1=param_cm(design, "kick_start_x"),
        cl=param_cm(design, "rail_cl_nose"),
        y_bot=param_cm(design, "front_rail_bottom"),
        h=param_cm(design, "nose_rail_h"),
    )
    _build_kick_segment(comp, design, side, sign)
    _build_segment_box(
        comp, design, side, sign,
        role="RAISED",
        x0=param_cm(design, "kick_end_x"),
        x1=param_cm(design, "drop_start_x"),
        cl=param_cm(design, "rail_cl"),
        y_bot=param_cm(design, "front_rail_bottom"),
        h=param_cm(design, "front_rail_h"),
    )
    _build_drop_segment(comp, design, side, sign)
    _build_segment_box(
        comp, design, side, sign,
        role="SLIP",
        x0=param_cm(design, "drop_end_x"),
        x1=param_cm(design, "clip_aft_x"),
        cl=param_cm(design, "rail_cl"),
        y_bot=param_cm(design, "cab_rail_bottom"),
        h=param_cm(design, "cab_rail_h"),
        slip_style=True,
    )
    _build_kick_ribs(comp, design, side, sign)


def _z_faces(cl, sign, tw, clear, t):
    z_in_inner = cl - sign * (tw / 2.0 + clear)
    z_out_inner = cl + sign * (tw / 2.0 + clear)
    z_in_outer = z_in_inner - sign * t
    z_out_outer = z_out_inner + sign * t
    return z_in_inner, z_out_inner, z_in_outer, z_out_outer


def _build_segment_box(comp, design, side, sign, role, x0, x1, cl, y_bot, h, slip_style=False):
    if x1 <= x0 + 0.05 * IN_TO_CM:
        return
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    z_in_i, z_out_i, z_in_o, z_out_o = _z_faces(cl * sign, sign, tw, clear, t)

    y_bot_outer = y_bot - clear - t
    y_top_outer = y_bot + h + clear
    # Side plates span inside height between top/bottom plates.
    y_bot_inner = y_bot - clear
    y_top_inner = y_bot + h + clear

    z0 = min(z_in_o, z_out_o)
    z1 = max(z_in_o, z_out_o)

    _extrude_rect_plate(
        comp, "{}_TOP".format(role), side, x0, x1, y_top_outer, z0, z1, "clip_t", True
    )
    _extrude_rect_plate(
        comp, "{}_BOT".format(role), side, x0, x1, y_bot_outer + t, z0, z1, "clip_t", False
    )
    _extrude_side_rect(
        comp, design, "{}_OUT".format(role), side, sign,
        x0, x1, y_bot_inner, y_top_inner, z_out_i, toward_outboard=True,
    )
    _extrude_side_rect(
        comp, design, "{}_IN".format(role), side, sign,
        x0, x1, y_bot_inner, y_top_inner, z_in_i, toward_outboard=False,
    )

    if slip_style:
        # One pair of tab stubs on the outboard plate into the top slip plate.
        _add_slip_tab_stub(comp, design, side, sign, x0, x1, y_top_inner, z_out_i, t)


def _build_kick_segment(comp, design, side, sign):
    """Faceted plan kick: trapezoid top/bottom + angled side plates; top ramps."""
    x0 = param_cm(design, "kick_start_x")
    x1 = param_cm(design, "kick_end_x")
    if x1 <= x0 + 0.05 * IN_TO_CM:
        return
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    cl0 = param_cm(design, "rail_cl_nose") * sign
    cl1 = param_cm(design, "rail_cl") * sign
    frb = param_cm(design, "front_rail_bottom")
    nrh = param_cm(design, "nose_rail_h")
    frh = param_cm(design, "front_rail_h")

    y_bot_outer = frb - clear - t
    y_top0 = frb + nrh + clear
    y_top1 = frb + frh + clear
    y_bot_inner = frb - clear

    # Outer Z at start/end for trapezoid caps.
    half_inner = tw / 2.0 + clear
    half_outer = half_inner + t
    z_out0 = cl0 + sign * half_outer
    z_out1 = cl1 + sign * half_outer
    z_in0 = cl0 - sign * half_outer
    z_in1 = cl1 - sign * half_outer

    _extrude_trap_plate(
        comp, "KICK_TOP", side,
        x0, x1, y_top0, y_top1,
        z_in0, z_out0, z_in1, z_out1,
        "clip_t", up=True,
    )
    _extrude_trap_plate(
        comp, "KICK_BOT", side,
        x0, x1, y_bot_outer + t, y_bot_outer + t,
        z_in0, z_out0, z_in1, z_out1,
        "clip_t", up=False,
    )

    # Angled side plates: sketch on XY-offset at average Z isn't right for
    # a facet. Approximate with a vertical plate on a mid-Z plane spanning
    # the chord — good enough for packaging; true miter is a follow-up.
    z_out_i0 = cl0 + sign * half_inner
    z_out_i1 = cl1 + sign * half_inner
    z_in_i0 = cl0 - sign * half_inner
    z_in_i1 = cl1 - sign * half_inner
    _extrude_angled_side(
        comp, "KICK_OUT", side, sign, x0, x1,
        y_bot_inner, y_top0, y_top1, z_out_i0, z_out_i1, toward_outboard=True,
    )
    _extrude_angled_side(
        comp, "KICK_IN", side, sign, x0, x1,
        y_bot_inner, y_top0, y_top1, z_in_i0, z_in_i1, toward_outboard=False,
    )


def _build_drop_segment(comp, design, side, sign):
    """Angular side-view drop from raised front height to cab height."""
    x0 = param_cm(design, "drop_start_x")
    x1 = param_cm(design, "drop_end_x")
    if x1 <= x0 + 0.05 * IN_TO_CM:
        return
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    cl = param_cm(design, "rail_cl") * sign
    frb = param_cm(design, "front_rail_bottom")
    frh = param_cm(design, "front_rail_h")
    crb = param_cm(design, "cab_rail_bottom")
    crh = param_cm(design, "cab_rail_h")

    z_in_i, z_out_i, z_in_o, z_out_o = _z_faces(cl, sign, tw, clear, t)
    z0 = min(z_in_o, z_out_o)
    z1 = max(z_in_o, z_out_o)

    y_bot0 = frb - clear - t
    y_bot1 = crb - clear - t
    y_top0 = frb + frh + clear
    y_top1 = crb + crh + clear
    y_bi0 = frb - clear
    y_bi1 = crb - clear

    _extrude_trap_plate(
        comp, "DROP_TOP", side, x0, x1, y_top0, y_top1, z0, z1, z0, z1, "clip_t", True
    )
    _extrude_trap_plate(
        comp, "DROP_BOT", side,
        x0, x1, y_bot0 + t, y_bot1 + t, z0, z1, z0, z1, "clip_t", False,
    )
    # Side plates with drop profile (constant Z).
    _extrude_side_poly(
        comp, design, "DROP_OUT", side, sign,
        [(x0, y_bi0), (x1, y_bi1), (x1, y_top1), (x0, y_top0)],
        z_out_i, toward_outboard=True,
    )
    _extrude_side_poly(
        comp, design, "DROP_IN", side, sign,
        [(x0, y_bi0), (x1, y_bi1), (x1, y_top1), (x0, y_top0)],
        z_in_i, toward_outboard=False,
    )


def _build_kick_ribs(comp, design, side, sign):
    """Vertical rib plates at kick bend lines (kick_start / kick_end)."""
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    frb = param_cm(design, "front_rail_bottom")
    nrh = param_cm(design, "nose_rail_h")
    frh = param_cm(design, "front_rail_h")
    for label, x, cl, h in (
        ("RIB_KICK_S", param_cm(design, "kick_start_x"), param_cm(design, "rail_cl_nose"), nrh),
        ("RIB_KICK_E", param_cm(design, "kick_end_x"), param_cm(design, "rail_cl"), frh),
    ):
        z_in_i, z_out_i, z_in_o, z_out_o = _z_faces(cl * sign, sign, tw, clear, t)
        y0 = frb - clear
        y1 = frb + h + clear
        z0 = min(z_in_o, z_out_o)
        z1 = max(z_in_o, z_out_o)
        _extrude_rib_yz(comp, label, side, x, y0, y1, z0, z1)


def _extrude_rect_plate(comp, role, side, x0, x1, y, z0, z1, thickness_expr, up):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z1))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z0))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByString(thickness_expr))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _extrude_trap_plate(comp, role, side, x0, x1, y0, y1, z_in0, z_out0, z_in1, z_out1, thickness_expr, up):
    """Top/bottom plate that may change Y and Z across X (kick / drop).

    Uses a mid-height XZ plane and a trapezoid; for Y-ramped plates the
    profile is sketched on a plane at y0 and the far edge is only exact at
    constant-Y. When y0!=y1 we loft via a side-view approximation: sketch
    on XZ at average Y (packaging solid).
    """
    y = 0.5 * (y0 + y1)
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    pts = [
        sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z_in0)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z_out0)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z_out1)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z_in1)),
    ]
    for i in range(4):
        lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByString(thickness_expr))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _extrude_side_rect(comp, design, role, side, sign, x0, x1, y0, y1, z_start, toward_outboard):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_start))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y0, z_start))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y0, z_start))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y1, z_start))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y1, z_start))
    lines.addByTwoPoints(p00, p10)
    lines.addByTwoPoints(p10, p11)
    lines.addByTwoPoints(p11, p01)
    lines.addByTwoPoints(p01, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    reverse = (not toward_outboard) if sign > 0 else toward_outboard
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _extrude_side_poly(comp, design, role, side, sign, xy_pts, z_start, toward_outboard):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_start))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    sps = [
        sk.modelToSketchSpace(adsk.core.Point3D.create(x, y, z_start)) for x, y in xy_pts
    ]
    for i in range(len(sps)):
        lines.addByTwoPoints(sps[i], sps[(i + 1) % len(sps)])
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    reverse = (not toward_outboard) if sign > 0 else toward_outboard
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _extrude_angled_side(comp, role, side, sign, x0, x1, y_bot, y_top0, y_top1, z0, z1, toward_outboard):
    """Side plate for the kick facet: sketch on a plane through the outboard chord."""
    # Build a construction plane through three points on the facet.
    # Fallback: extrude from mid-Z XY-offset using a rectangle that spans
    # average Z — packaging approximation (README notes true miter follow-up).
    z_mid = 0.5 * (z0 + z1)
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_mid))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    pts = [
        sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y_bot, z_mid)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y_bot, z_mid)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y_top1, z_mid)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y_top0, z_mid)),
    ]
    for i in range(4):
        lines.addByTwoPoints(pts[i], pts[(i + 1) % 4])
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    # Extrude thickness; lateral coverage is approximate for the angled facet.
    # Use a distance that reaches across the Z delta plus clip_t.
    span = abs(z1 - z0) + param_cm(adsk.fusion.Design.cast(comp.parentDesign), "clip_t")
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    reverse = (not toward_outboard) if sign > 0 else toward_outboard
    # Symmetric-ish: extrude clip_t; angled face is a packaging stub.
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    _ = span
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _extrude_rib_yz(comp, role, side, x, y0, y1, z0, z1):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x, y0, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x, y0, z1))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x, y1, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x, y1, z0))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Thin rib along +X.
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _add_slip_tab_stub(comp, design, side, sign, x0, x1, y_top_inner, z_out_inner, t):
    """Minimal tab-and-slot sample on the slip section (pattern for laser follow-up)."""
    pitch = param_cm(design, "tab_pitch")
    tw = param_cm(design, "tab_width")
    span = x1 - x0
    if span < pitch:
        return
    x_mid = 0.5 * (x0 + x1)
    # Tab pad protruding up from side into top plate region.
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_out_inner))
    pl = planes.add(pin)
    pl.name = "PL_{}_TAB".format(side)
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_TAB".format(side)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    hx = tw / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_mid - hx, y_top_inner, z_out_inner))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_mid + hx, y_top_inner, z_out_inner))
    p11 = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x_mid + hx, y_top_inner + t, z_out_inner)
    )
    p01 = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x_mid - hx, y_top_inner + t, z_out_inner)
    )
    lines.addByTwoPoints(p00, p10)
    lines.addByTwoPoints(p10, p11)
    lines.addByTwoPoints(p11, p01)
    lines.addByTwoPoints(p01, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    reverse = False if sign > 0 else True
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(
        _largest_profile(sk), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_TAB".format(side)
    ext.bodies.item(0).name = "RAIL_{}_TAB_SLIP".format(side)


# ---------------------------------------------------------------------------
# Core pads
# ---------------------------------------------------------------------------

def build_core_pads(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    core_x = param_cm(design, "core_x")
    cl_n = param_cm(design, "rail_cl_nose")
    tw = param_cm(design, "tube_w")
    pad_l = param_cm(design, "core_pad_l")
    pad_w = param_cm(design, "core_pad_w")
    pad_t = param_cm(design, "core_pad_t")
    frb = param_cm(design, "front_rail_bottom")
    nrh = param_cm(design, "nose_rail_h")
    # Nose outside face at rail_cl_nose + tube_w/2; pads extend further outboard.
    y_top = frb + nrh

    for sign, tag in ((1.0, "RH"), (-1.0, "LH")):
        z_nose_out = sign * (cl_n + tw / 2.0)
        z0 = z_nose_out
        z1 = z_nose_out + sign * pad_l
        x0 = core_x - pad_w / 2.0
        x1 = core_x + pad_w / 2.0
        _extrude_rect_plate(
            comp, "CORE_PAD", tag, x0, x1, y_top, min(z0, z1), max(z0, z1),
            "core_pad_t", True,
        )
        # Rename body
        for i in range(comp.bRepBodies.count):
            b = comp.bRepBodies.item(i)
            if b.name.startswith("RAIL_{}_CORE_PAD".format(tag)):
                b.name = "CORE_PAD_{}".format(tag)


# ---------------------------------------------------------------------------
# Pivot construction geometry + stubs
# ---------------------------------------------------------------------------

def build_pivot_geometry(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    points = comp.constructionPoints
    planes = comp.constructionPlanes

    # Horizontal plane at LCA / UCA heights + lateral planes.
    for name, expr in (
        ("PL_LCA_Y", "lca_pivot_y"),
        ("PL_UCA_Y", "uca_pivot_y"),
        ("PL_LCA_Z_RH", "lca_pivot_z"),
        ("PL_LCA_Z_LH", "-lca_pivot_z"),
        ("PL_UCA_Z_RH", "uca_pivot_z"),
        ("PL_UCA_Z_LH", "-uca_pivot_z"),
        ("PL_AXLE_X", "0 in"),
    ):
        pin = planes.createInput()
        if "Y" in name:
            pin.setByOffset(
                comp.xZConstructionPlane, adsk.core.ValueInput.createByString(expr)
            )
        elif name.endswith("X"):
            pin.setByOffset(
                comp.yZConstructionPlane, adsk.core.ValueInput.createByString(expr)
            )
        else:
            pin.setByOffset(
                comp.xYConstructionPlane, adsk.core.ValueInput.createByString(expr)
            )
        pl = planes.add(pin)
        pl.name = name

    pl_ax = comp.constructionPlanes.itemByName("PL_AXLE_X")
    for tag, yname, zname in (
        ("LCA_RH", "PL_LCA_Y", "PL_LCA_Z_RH"),
        ("LCA_LH", "PL_LCA_Y", "PL_LCA_Z_LH"),
        ("UCA_RH", "PL_UCA_Y", "PL_UCA_Z_RH"),
        ("UCA_LH", "PL_UCA_Y", "PL_UCA_Z_LH"),
    ):
        cin = points.createInput()
        cin.setByThreePlanes(
            pl_ax,
            comp.constructionPlanes.itemByName(yname),
            comp.constructionPlanes.itemByName(zname),
        )
        pt = points.add(cin)
        pt.name = tag

    # Solid stubs: hanging LCA drop mount + UCA tower.
    frb = param_cm(design, "front_rail_bottom")
    frh = param_cm(design, "front_rail_h")
    stub_w = param_cm(design, "pivot_stub_w")
    stub_t = param_cm(design, "pivot_stub_t")
    lz = param_cm(design, "lca_pivot_z")
    ly = param_cm(design, "lca_pivot_y")
    uz = param_cm(design, "uca_pivot_z")
    uy = param_cm(design, "uca_pivot_y")
    cl = param_cm(design, "rail_cl")
    tw = param_cm(design, "tube_w")

    for sign, tag in ((1.0, "RH"), (-1.0, "LH")):
        # Hanging LCA: plate from rail bottom down to pivot, at outboard of rail.
        z_rail_out = sign * (cl + tw / 2.0)
        x0, x1 = -stub_w / 2.0, stub_w / 2.0
        _extrude_side_rect(
            comp, design, "LCA_HANG", tag, sign,
            x0, x1, ly - stub_t, frb, z_rail_out, toward_outboard=True,
        )
        # UCA tower: plate from rail top up to pivot.
        _extrude_side_rect(
            comp, design, "UCA_TOWER", tag, sign,
            x0, x1, frb + frh, uy + stub_t, z_rail_out, toward_outboard=True,
        )
        # Small horizontal pivot pads at LCA / UCA.
        z0 = sign * lz - stub_t / 2.0
        z1 = sign * lz + stub_t / 2.0
        _extrude_rect_plate(
            comp, "LCA_PAD", tag, x0, x1, ly, min(z0, z1), max(z0, z1),
            "pivot_stub_t", True,
        )
        z0 = sign * uz - stub_t / 2.0
        z1 = sign * uz + stub_t / 2.0
        _extrude_rect_plate(
            comp, "UCA_PAD", tag, x0, x1, uy, min(z0, z1), max(z0, z1),
            "pivot_stub_t", True,
        )
