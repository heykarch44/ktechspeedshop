# Ktech C10 rear clip for Autodesk Fusion 360
#
# Install
#   1. Fusion → Utilities → Add-Ins → Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_C10_RearClip)
#   4. Run it. It opens / uses a Design document. Save as KTECH_C10_REAR_CLIP.
#
# Design intent (overrides older C-socket notes in DESIGN.md)
#   Purchased 2x6 A500 center tube = reference body only.
#   Rear clip = four-piece laser plate box rail per side (top / bottom /
#   inboard / outboard) that slip-fits over the tube for length adjust,
#   then welds. Tab-and-slot keys locate subassemblies into the rails.
#   Prototype: 73-87 short (wb = wb_73_87_short). Switch to wb_67_72_short
#   for 67-72. Rear: triangulated 4-link, Currie 9-inch, bag OR coilover.
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

# Bodies whose top-face outline is exported as flat DXF for laser.
PLATE_BODY_NAMES = (
    "RAIL_RH_TOP_FWD",
    "RAIL_RH_TOP_AFT",
    "RAIL_RH_BOT_FWD",
    "RAIL_RH_BOT_AFT",
    "RAIL_RH_OUTBOARD",
    "RAIL_RH_INBOARD",
    "RAIL_LH_TOP_FWD",
    "RAIL_LH_TOP_AFT",
    "RAIL_LH_BOT_FWD",
    "RAIL_LH_BOT_AFT",
    "RAIL_LH_OUTBOARD",
    "RAIL_LH_INBOARD",
    "XMEMBER_UPPER",
    "BRACKET_LOWER_RH",
    "BRACKET_LOWER_LH",
    "BRACKET_UPPER_RH",
    "BRACKET_UPPER_LH",
    "MOUNT_BAG_RH",
    "MOUNT_BAG_LH",
    "MOUNT_COILOVER_RH",
    "MOUNT_COILOVER_LH",
)

PARAM_ORDER = [
    # Shared spine / tape names (match KTECH_C10_Chassis_Setup)
    ("tube_w", "2 in", "in", "A500 width across the car"),
    ("tube_h", "6 in", "in", "A500 height"),
    ("wall", "0.188 in", "in", "A500 wall"),
    ("rail_bottom", "8 in", "in", "Bottom of tube off ground"),
    ("wb_73_87_short", "117.5 in", "in", "73-87 shortbed WB — first prototype"),
    ("wb_67_72_short", "115.0 in", "in", "67-72 shortbed WB — switch wb to this"),
    ("wb", "wb_73_87_short", "in", "Active wheelbase"),
    ("rear_overhang", "42 in", "in", "PLACEHOLDER. Clip aft of rear axle"),
    ("core_width", "33.5 in", "in", "TAPED. Core support C-C"),
    ("rail_cl", "core_width / 2", "in", "2x6 CL from vehicle CL"),
    ("core_x", "-33 in", "in", "PLACEHOLDER. Core vs front axle"),
    ("core_to_mid", "55 in", "in", "TAPED. Core to mid along rail"),
    ("mid_to_rear", "43 in", "in", "TAPED. Mid to cab-rear along rail"),
    ("cab_f_x", "core_x + core_to_mid", "in", "Computed"),
    ("cab_r_x", "cab_f_x + mid_to_rear", "in", "Computed"),
    # Rear clip / slip-fit
    ("splice_aft", "3 in", "in", "PLACEHOLDER. Split aft of cab_r"),
    ("slip_overlap", "8 in", "in", "Slip-fit overlap of plate box on tube"),
    ("clip_t", "0.188 in", "in", "Laser plate thickness"),
    ("clip_clear", "0.030 in", "in", "Per-side slip clearance"),
    ("center_tube_end_x", "cab_r_x + splice_aft", "in", "Aft end of purchased 2x6"),
    ("clip_front_x", "center_tube_end_x - slip_overlap", "in", "Forward end of plate box"),
    ("clip_rear_x", "wb + rear_overhang", "in", "Aft end of rear clip"),
    ("slip_id_w", "tube_w + 2 * clip_clear", "in", "Slip inside width"),
    ("slip_id_h", "tube_h + 2 * clip_clear", "in", "Slip inside height"),
    ("box_od_w", "slip_id_w + 2 * clip_t", "in", "Box outer width"),
    ("box_od_h", "slip_id_h + 2 * clip_t", "in", "Box outer height straight"),
    # Tab-and-slot
    ("tab_width", "0.750 in", "in", "PLACEHOLDER. Tab width"),
    ("tab_length", "clip_t", "in", "Tab length = mating plate thickness"),
    ("slot_clear", "0.010 in", "in", "PLACEHOLDER. Slot oversize vs tab"),
    ("tab_pitch", "4.000 in", "in", "PLACEHOLDER. Tab pitch along edges"),
    # Kickup / tire envelope
    ("tire_od", "32 in", "in", "Lay-out tire"),
    ("bag_stroke", "11 in", "in", "Bag travel target"),
    ("kickup_ahead", "10 in", "in", "PLACEHOLDER. Kickup start ahead of axle"),
    ("kickup_aft", "8 in", "in", "PLACEHOLDER. Kickup end aft of axle"),
    ("kickup_rise", "4 in", "in", "PLACEHOLDER. Rail top rise over axle"),
    ("kickup_ramp", "4 in", "in", "PLACEHOLDER. Kickup ramp length"),
    # Triangulated 4-link
    ("lower_link_len", "23 in", "in", "PLACEHOLDER. Lower bar length"),
    ("upper_link_len", "22 in", "in", "PLACEHOLDER. Upper bar length"),
    ("lower_pickup_x", "cab_r_x + 2 in", "in", "PLACEHOLDER. Frame lower pickup X"),
    ("upper_pickup_x", "cab_r_x + 6 in", "in", "PLACEHOLDER. Frame upper pickup X"),
    ("lower_pickup_y", "rail_bottom + 1 in", "in", "PLACEHOLDER. Lower pickup Y"),
    ("upper_pickup_y", "rail_bottom + tube_h - 1 in", "in", "PLACEHOLDER. Upper pickup Y"),
    ("axle_link_spread_z", "18 in", "in", "PLACEHOLDER. Axle lower half-spread"),
    ("frame_link_spread_z", "rail_cl", "in", "Frame lower pickups at rail CL"),
    ("upper_xmember_w", "2.000 in", "in", "PLACEHOLDER. Upper xmember width along X"),
    ("upper_xmember_h", "4.000 in", "in", "PLACEHOLDER. Upper xmember height"),
    ("bracket_plate_w", "4.000 in", "in", "PLACEHOLDER. Link bracket width"),
    ("bracket_plate_h", "3.500 in", "in", "PLACEHOLDER. Link bracket height"),
    ("bracket_hole_d", "0.625 in", "in", "PLACEHOLDER. Link bolt hole dia"),
    # Suspension mode: 1 = airbag, 0 = coilover (evaluated at run)
    ("suspension_mode", "1", "", "1=airbag upper mount, 0=coilover"),
    ("bag_mount_w", "6.000 in", "in", "PLACEHOLDER. Bag mount plate width along X"),
    ("bag_mount_l", "8.000 in", "in", "PLACEHOLDER. Bag mount plate length"),
    ("bag_mount_z_off", "2.000 in", "in", "PLACEHOLDER. Pad inset from outboard"),
    ("coilover_mount_w", "3.000 in", "in", "PLACEHOLDER. Coilover mount width along X"),
    ("coilover_mount_l", "4.000 in", "in", "PLACEHOLDER. Coilover mount length"),
    # Currie 9-inch axle mockup
    ("axle_wms_a", "63.625 in", "in", "WMS width A — set by wheel/tire combo"),
    ("brake_space", "2.500 in", "in", "Torino late big bearing space per side"),
    ("housing_end_b", "axle_wms_a - 2 * brake_space", "in", "Housing end-to-end B"),
    ("axle_tube_od", "3.000 in", "in", "Axle tube OD"),
    ("axle_tube_wall", "0.188 in", "in", "Axle tube wall"),
    ("pinion_offset", "0.940 in", "in", "Pinion offset toward passenger (+Z)"),
    (
        "cs_width",
        "11.250 in",
        "in",
        "PLACEHOLDER UNVERIFIED — Currie CS width. Awaiting Currie CAD.",
    ),
    (
        "cs_height",
        "9.500 in",
        "in",
        "PLACEHOLDER UNVERIFIED — Currie CS height. Awaiting Currie CAD.",
    ),
    (
        "cs_depth",
        "8.000 in",
        "in",
        "PLACEHOLDER UNVERIFIED — Currie CS depth along X. Awaiting Currie CAD.",
    ),
    (
        "tube_insert",
        "2.500 in",
        "in",
        "PLACEHOLDER UNVERIFIED — Tube insert into CS. Awaiting Currie CAD.",
    ),
    (
        "axle_tube_len",
        "(housing_end_b - cs_width) / 2 + tube_insert",
        "in",
        "Derived axle tube length each side",
    ),
    ("axle_cl_y", "rail_bottom + tube_h / 2", "in", "PLACEHOLDER. Axle CL height at ride"),
    ("mount_y", "rail_bottom + tube_h", "in", "Top of straight tube / slip section"),
]

DO = adsk.fusion.DimensionOrientations
IN_TO_CM = 2.54


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
            ui.messageBox("Switch to the Design workspace and run again.")
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
            root.name = "KTECH_C10_REAR_CLIP"
        except Exception:
            pass

        already = False
        for i in range(root.occurrences.count):
            if "01_CENTER_TUBE" in root.occurrences.item(i).name:
                already = True
                break
        if already:
            ui.messageBox(
                "This document already has the rear clip in it.\n\n"
                "File → New Design, then Run the script again."
            )
            return

        mark = add_component(root, "00_ORIGIN")
        mark_origin(mark)

        skel = add_component(root, "00_SKELETON")
        center = add_component(root, "01_CENTER_TUBE")
        rail_rh = add_component(root, "02_RAIL_RH")
        rail_lh = add_component(root, "02_RAIL_LH")
        xmembers = add_component(root, "03_CROSSMEMBERS")
        links = add_component(root, "04_FOUR_LINK")
        axle = add_component(root, "05_AXLE_REF")
        mounts = add_component(root, "06_BAG_SHOCK")
        add_component(root, "07_FIXTURE")

        draw_layout_sketches(skel)
        build_center_tube_ref(center)
        build_rail_side(rail_rh, passenger=True)
        build_rail_side(rail_lh, passenger=False)
        build_upper_crossmember(xmembers)
        build_four_link_brackets(links)
        build_axle_ref(axle)
        build_suspension_mounts(mounts)

        dxf_dir = os.path.join(SCRIPT_DIR, "dxf_out")
        n_dxf = export_plate_dxfs(design, dxf_dir)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        mode = suspension_mode_value(design)
        mode_txt = "airbag" if mode >= 0.5 else "coilover"
        ui.messageBox(
            "Rear clip built in this document.\n\n"
            "Prototype WB = wb_73_87_short (117.5). For 67-72 set wb = wb_67_72_short.\n"
            "Suspension mount mode: {} (suspension_mode user param).\n"
            "Exported {} plate DXFs to:\n{}\n\n"
            "Fit view if the canvas looks empty. Rails sit at rail_cl off CL.\n"
            "Save as KTECH_C10_REAR_CLIP.".format(mode_txt, n_dxf, dxf_dir)
        )
    except Exception:
        if ui:
            ui.messageBox("KTECH_C10_RearClip failed:\n{}".format(traceback.format_exc()))


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def apply_csv_overrides():
    """Load rear_clip_parameters.csv into PARAM_ORDER expressions."""
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "rear_clip_parameters.csv")
    if not os.path.isfile(params_path):
        return
    with open(params_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("name") or "").strip()
            if name not in by_name:
                continue
            expr = (row.get("expression") or "").strip()
            unit = (row.get("unit") or "in").strip()
            comment = (row.get("comment") or by_name[name][3]).strip()
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


def suspension_mode_value(design):
    try:
        return design.userParameters.itemByName("suspension_mode").value
    except Exception:
        return 1.0


# ---------------------------------------------------------------------------
# Components / origin
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Skeleton
# ---------------------------------------------------------------------------

def draw_layout_sketches(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)

    side = comp.sketches.add(comp.xYConstructionPlane)
    side.name = "SK_SIDE"
    side.isComputeDeferred = True
    lines = side.sketchCurves.sketchLines
    p0 = adsk.core.Point3D.create(0, 0, 0)
    ground = lines.addByTwoPoints(p0, adsk.core.Point3D.create(50, 0, 0))
    axle_f = lines.addByTwoPoints(p0, adsk.core.Point3D.create(0, 20, 0))
    axle_r = lines.addByTwoPoints(
        adsk.core.Point3D.create(40, 0, 0), adsk.core.Point3D.create(40, 20, 0)
    )
    clip_f = lines.addByTwoPoints(
        adsk.core.Point3D.create(30, 0, 0), adsk.core.Point3D.create(30, 15, 0)
    )
    side.isComputeDeferred = False
    dims = side.sketchDimensions
    for ln in (ground, axle_f, axle_r, clip_f):
        ln.isConstruction = True
    wb_dim = dims.addDistanceDimension(
        axle_f.startSketchPoint,
        axle_r.startSketchPoint,
        DO.HorizontalDimensionOrientation,
        adsk.core.Point3D.create(20, -8, 0),
    )
    wb_dim.parameter.expression = "wb + 0 in"
    g_dim = dims.addDistanceDimension(
        ground.startSketchPoint,
        ground.endSketchPoint,
        DO.HorizontalDimensionOrientation,
        adsk.core.Point3D.create(20, -15, 0),
    )
    g_dim.parameter.expression = "clip_rear_x + 0 in"
    cf_dim = dims.addDistanceDimension(
        axle_f.startSketchPoint,
        clip_f.startSketchPoint,
        DO.HorizontalDimensionOrientation,
        adsk.core.Point3D.create(15, -20, 0),
    )
    cf_dim.parameter.expression = "clip_front_x + 0 in"

    top = comp.sketches.add(comp.xZConstructionPlane)
    top.name = "SK_TOP"
    top.isComputeDeferred = True
    tlines = top.sketchCurves.sketchLines
    cl = tlines.addByTwoPoints(
        adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(50, 0, 0)
    )
    rh = tlines.addByTwoPoints(
        adsk.core.Point3D.create(0, 10, 0), adsk.core.Point3D.create(50, 10, 0)
    )
    top.isComputeDeferred = False
    cl.isConstruction = True
    rh.isConstruction = True
    tdims = top.sketchDimensions
    cl_len = tdims.addDistanceDimension(
        cl.startSketchPoint,
        cl.endSketchPoint,
        DO.HorizontalDimensionOrientation,
        adsk.core.Point3D.create(20, -5, 0),
    )
    cl_len.parameter.expression = "clip_rear_x + 0 in"
    rail_dim = tdims.addDistanceDimension(
        cl.startSketchPoint,
        rh.startSketchPoint,
        DO.VerticalDimensionOrientation,
        adsk.core.Point3D.create(-10, 5, 0),
    )
    rail_dim.parameter.expression = "rail_cl + 0 in"

    # Side-view kickup construction polyline (reference only).
    kick = comp.sketches.add(comp.xYConstructionPlane)
    kick.name = "SK_KICKUP_REF"
    _draw_kickup_polyline(kick, design, z_world=0.0, construction=True)


def _draw_kickup_polyline(sk, design, z_world, construction=False):
    """Outer top outline of the RH/LH side plate in world XY at given Z."""
    pts = _kickup_world_points(design, top=True)
    bot = _kickup_world_points(design, top=False)
    # Close loop: top forward→aft, then bottom aft→forward.
    loop = pts + list(reversed(bot))
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
    sk.isComputeDeferred = False


def _kickup_world_points(design, top=True):
    """Return list of (x,y) inches-as-cm model values for side-plate outline."""
    # Values are already cm from userParameters.value
    xf = param_cm(design, "clip_front_x")
    xr = param_cm(design, "clip_rear_x")
    wb = param_cm(design, "wb")
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    th = param_cm(design, "tube_h")
    ahead = param_cm(design, "kickup_ahead")
    aft = param_cm(design, "kickup_aft")
    rise = param_cm(design, "kickup_rise")
    ramp = param_cm(design, "kickup_ramp")

    # Slip box outer: bottom at rail_bottom - clear - t? 
    # Inside bottom = tube bottom - clear = rail_bottom - clear
    # Outer bottom plate sits below that by clip_t for top/bottom wrap style,
    # but side plates span the INSIDE height only (between top and bottom plates).
    # Side plate vertical span = slip_id_h = tube_h + 2*clear
    y_bot = rb - clear
    y_top = rb + th + clear
    y_top_hi = y_top + rise
    y_bot_hi = y_bot + rise

    x_k0 = wb - ahead
    x_k1 = x_k0 + ramp
    x_k2 = wb + aft - ramp
    x_k3 = wb + aft

    if top:
        return [
            (xf, y_top),
            (x_k0, y_top),
            (x_k1, y_top_hi),
            (x_k2, y_top_hi),
            (x_k3, y_top_hi),
            (xr, y_top_hi),
        ]
    return [
        (xf, y_bot),
        (x_k0, y_bot),
        (x_k1, y_bot_hi),
        (x_k2, y_bot_hi),
        (x_k3, y_bot_hi),
        (xr, y_bot_hi),
    ]


# ---------------------------------------------------------------------------
# Center tube reference (purchased A500 — do not build from plate)
# ---------------------------------------------------------------------------

def build_center_tube_ref(comp):
    """Purchased A500 stub through the slip region — reference body only."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(
        comp.yZConstructionPlane,
        adsk.core.ValueInput.createByString("clip_front_x"),
    )
    pl = planes.add(pin)
    pl.name = "PL_CLIP_FRONT"

    sk = comp.sketches.add(pl)
    sk.name = "SK_CENTER_TUBE_AT_CLIP"
    _tube_section_at_rail(sk, design)
    ring = _find_ring_profile(sk)
    if not ring:
        raise RuntimeError("Could not find center-tube profile at clip front.")

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(
        False, adsk.core.ValueInput.createByString("slip_overlap")
    )
    ext = extrudes.add(ext_in)
    ext.name = "EX_CENTER_TUBE_REF"
    body = ext.bodies.item(0)
    body.name = "CENTER_TUBE_REF_RH"
    try:
        body.opacity = 0.35
    except Exception:
        pass

    bodies = adsk.core.ObjectCollection.create()
    bodies.add(body)
    mirror_in = comp.features.mirrorFeatures.createInput(bodies, comp.xYConstructionPlane)
    mirror = comp.features.mirrorFeatures.add(mirror_in)
    mirror.name = "MIR_CENTER_TUBE_REF"
    if mirror.bodies.count:
        mb = mirror.bodies.item(0)
        mb.name = "CENTER_TUBE_REF_LH"
        try:
            mb.opacity = 0.35
        except Exception:
            pass


def _tube_section_at_rail(sk, design):
    rb = param_cm(design, "rail_bottom")
    th = param_cm(design, "tube_h")
    tw = param_cm(design, "tube_w")
    cl = param_cm(design, "rail_cl")
    wall = param_cm(design, "wall")

    cy = rb + th / 2.0
    cz = cl
    outer_c = sk.modelToSketchSpace(adsk.core.Point3D.create(0, cy, cz))
    outer_r = sk.modelToSketchSpace(
        adsk.core.Point3D.create(0, cy + th / 2.0, cz + tw / 2.0)
    )
    inner_r = sk.modelToSketchSpace(
        adsk.core.Point3D.create(0, cy + th / 2.0 - wall, cz + tw / 2.0 - wall)
    )

    sk.isComputeDeferred = True
    outer = sk.sketchCurves.sketchLines.addCenterPointRectangle(outer_c, outer_r)
    inner = sk.sketchCurves.sketchLines.addCenterPointRectangle(outer_c, inner_r)
    sk.isComputeDeferred = False
    _dim_two_sides(sk, outer, "tube_w", "tube_h")
    _dim_two_sides(sk, inner, "tube_w - 2 * wall", "tube_h - 2 * wall")


def _find_ring_profile(sk):
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        if prof.profileLoops.count == 2:
            return prof
    return None


# ---------------------------------------------------------------------------
# Four-piece plate rails
# ---------------------------------------------------------------------------

def build_rail_side(comp, passenger=True):
    """Build TOP/BOTTOM/INBOARD/OUTBOARD plate bodies for one rail."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    cl = param_cm(design, "rail_cl") * sign
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    tw = param_cm(design, "tube_w")

    # Z faces of slip cavity and outer box (passenger +Z outboard).
    z_in_inner = cl - sign * (tw / 2.0 + clear)
    z_out_inner = cl + sign * (tw / 2.0 + clear)
    z_in_outer = z_in_inner - sign * t
    z_out_outer = z_out_inner + sign * t

    # --- Outboard + inboard side plates (full kickup profile, thickness clip_t) ---
    _extrude_side_plate(
        comp, design, "OUTBOARD", side, z_start=z_out_inner, toward_outboard=True, sign=sign
    )
    _extrude_side_plate(
        comp, design, "INBOARD", side, z_start=z_in_inner, toward_outboard=False, sign=sign
    )

    # --- Top / bottom forward (straight slip + approach) and aft (raised) plates ---
    _build_cap_plates(comp, design, side, sign, z_in_outer, z_out_outer)

    # Tab-and-slot keys along long edges of the forward box section.
    _add_rail_tabs_and_slots(comp, design, side, sign, z_in_inner, z_out_inner, t)

    # Key slots in outboard plate for lower/upper link brackets (fixture role).
    _add_bracket_key_slots(comp, design, side, sign)


def _extrude_side_plate(comp, design, role, side, z_start, toward_outboard, sign):
    # Offset plane at the inner face of this side plate; extrude by clip_t
    # outward (outboard) or inward (inboard) depending on role.
    planes = comp.constructionPlanes
    pin = planes.createInput()
    # Construction plane parallel to XY at Z = z_start (world).
    # Use offset from XY by z_start — but XY offset is along Z, yes.
    pin.setByOffset(
        comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(z_start),
    )
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    _draw_kickup_polyline(sk, design, z_world=z_start, construction=False)

    if sk.profiles.count < 1:
        raise RuntimeError("No profile for {} {} side plate".format(side, role))

    # Pick largest-area profile (outer loop).
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Extrude direction: toward_outboard means +sign * clip_t from inner face.
    # setDistanceExtent(False) = positive sketch normal. Sketch on XY-offset
    # plane: normal is +Z. For RH outboard (z_start = out_inner, want +Z): good.
    # For RH inboard (z_start = in_inner, want -Z): reverse.
    # passenger outboard: toward_outboard True, sign +1 → positive OK
    # passenger inboard: toward_outboard False, sign +1 → reverse
    # LH outboard: toward_outboard True, sign -1, z_start more negative → want -Z = reverse of +Z
    reverse = False
    if sign > 0:
        reverse = not toward_outboard
    else:
        reverse = toward_outboard
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


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


def _build_cap_plates(comp, design, side, sign, z_in_outer, z_out_outer):
    """Flat top/bottom plates: forward (pre-kickup) and aft (raised) segments."""
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
    th = param_cm(design, "tube_h")
    t = param_cm(design, "clip_t")
    rise = param_cm(design, "kickup_rise")
    xf = param_cm(design, "clip_front_x")
    xr = param_cm(design, "clip_rear_x")
    wb = param_cm(design, "wb")
    ahead = param_cm(design, "kickup_ahead")
    aft = param_cm(design, "kickup_aft")
    ramp = param_cm(design, "kickup_ramp")

    x_k0 = wb - ahead
    x_k3 = wb + aft
    # Forward segment ends at start of kickup ramp; aft starts after kickup.
    x_fwd_end = x_k0
    x_aft_start = x_k3

    y_bot_outer = rb - clear - t
    y_top_outer = rb + th + clear
    y_bot_aft = y_bot_outer + rise
    y_top_aft = y_top_outer + rise

    z0 = min(z_in_outer, z_out_outer)
    z1 = max(z_in_outer, z_out_outer)

    _extrude_rect_plate(
        comp,
        "TOP_FWD",
        side,
        x0=xf,
        x1=x_fwd_end,
        y=y_top_outer,
        z0=z0,
        z1=z1,
        thickness_expr="clip_t",
        up=True,
    )
    _extrude_rect_plate(
        comp,
        "BOT_FWD",
        side,
        x0=xf,
        x1=x_fwd_end,
        y=y_bot_outer + t,
        z0=z0,
        z1=z1,
        thickness_expr="clip_t",
        up=False,
    )
    if x_aft_start < xr - 0.1 * IN_TO_CM:
        _extrude_rect_plate(
            comp,
            "TOP_AFT",
            side,
            x0=x_aft_start,
            x1=xr,
            y=y_top_aft,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=True,
        )
        _extrude_rect_plate(
            comp,
            "BOT_AFT",
            side,
            x0=x_aft_start,
            x1=xr,
            y=y_bot_aft + t,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=False,
        )


def _extrude_rect_plate(comp, role, side, x0, x1, y, z0, z1, thickness_expr, up):
    """Create a horizontal plate by sketching on XZ at height y and extruding ±Y."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, role)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, role)
    sk.isComputeDeferred = True
    # XZ plane: sketch x→X, y→Z
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, z1))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, z0))
    lines = sk.sketchCurves.sketchLines
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
    # XZ plane normal is +Y. up=True → +Y; up=False → reverse (−Y).
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByString(thickness_expr))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}_{}".format(side, role)
    body = ext.bodies.item(0)
    body.name = "RAIL_{}_{}".format(side, role)
    return body


def _add_rail_tabs_and_slots(comp, design, side, sign, z_in_inner, z_out_inner, t):
    """Tab protrusions from side plates into top/bottom, plus mating slot cuts.

    Tabs are modeled as small rectangular pads on the outboard plate top edge
    into the top-forward plate region. Slots are cut in TOP_FWD / BOT_FWD.
    """
    xf = param_cm(design, "clip_front_x")
    wb = param_cm(design, "wb")
    ahead = param_cm(design, "kickup_ahead")
    pitch = param_cm(design, "tab_pitch")
    tw = param_cm(design, "tab_width")
    tl = param_cm(design, "tab_length")
    sc = param_cm(design, "slot_clear")
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
    th = param_cm(design, "tube_h")

    x_end = wb - ahead
    span = x_end - xf
    if span <= pitch:
        return

    n_tabs = max(1, int(math.floor(span / pitch)))
    y_top_inner = rb + th + clear
    y_bot_inner = rb - clear

    for i in range(n_tabs):
        xc = xf + (i + 0.5) * pitch
        if xc + tw / 2.0 > x_end:
            break
        # Slot cut in top-forward plate (through clip_t).
        _cut_slot_horizontal(
            comp,
            design,
            name="SLOT_TOP_{}_{}".format(side, i),
            xc=xc,
            y=y_top_inner,
            z0=min(z_in_inner, z_out_inner),
            z1=max(z_in_inner, z_out_inner),
            tab_w=tw,
            slot_clear=sc,
            up=True,
        )
        _cut_slot_horizontal(
            comp,
            design,
            name="SLOT_BOT_{}_{}".format(side, i),
            xc=xc,
            y=y_bot_inner - t,
            z0=min(z_in_inner, z_out_inner),
            z1=max(z_in_inner, z_out_inner),
            tab_w=tw,
            slot_clear=sc,
            up=False,
        )
        # Tabs on outboard plate protruding +Y into top plate / −Y into bottom.
        z_out = z_out_inner
        _add_tab_on_side(
            comp,
            name="TAB_TOP_{}_{}".format(side, i),
            xc=xc,
            y=y_top_inner,
            z=z_out,
            sign=sign,
            tab_w=tw,
            tab_l=tl,
            upward=True,
        )
        _add_tab_on_side(
            comp,
            name="TAB_BOT_{}_{}".format(side, i),
            xc=xc,
            y=y_bot_inner,
            z=z_out,
            sign=sign,
            tab_w=tw,
            tab_l=tl,
            upward=False,
        )


def _cut_slot_horizontal(comp, design, name, xc, y, z0, z1, tab_w, slot_clear, up):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    half = tab_w / 2.0 + slot_clear
    # Slot in top/bottom plate: X = tab_w+2*slot_clear, Z ≈ clip_t+2*slot_clear,
    # adjacent to the outboard edge where the side-plate tab enters.
    t = param_cm(design, "clip_t")
    if abs(z1) >= abs(z0):
        z_a, z_b = z1 - math.copysign(t + 2 * slot_clear, z1), z1
    else:
        z_a, z_b = z0, z0 + math.copysign(t + 2 * slot_clear, z0 if z0 != 0 else 1)

    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - half, y, min(z_a, z_b)))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - half, y, max(z_a, z_b)))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + half, y, max(z_a, z_b)))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + half, y, min(z_a, z_b)))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByString("clip_t"))
    try:
        ext = extrudes.add(ext_in)
        ext.name = "EX_{}".format(name)
    except Exception:
        # Cut may miss if plate naming/order differs; non-fatal for layout.
        pass


def _add_tab_on_side(comp, name, xc, y, z, sign, tab_w, tab_l, upward):
    """Small rectangular tab body keyed from side plate into cap plate."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    # Tab footprint on side plate face: width along X, height along Y = tab_l.
    y0 = y
    y1 = y + tab_l if upward else y - tab_l
    half = tab_w / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - half, min(y0, y1), z))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - half, max(y0, y1), z))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + half, max(y0, y1), z))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + half, min(y0, y1), z))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Extrude into the side plate thickness (toward rail center from outboard).
    reverse = sign > 0  # RH outboard face normal +Z; tab should go −Z into plate
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    try:
        ext = extrudes.add(ext_in)
        ext.name = "EX_{}".format(name)
        ext.bodies.item(0).name = name
    except Exception:
        pass


def _add_bracket_key_slots(comp, design, side, sign):
    """Rectangular key slots in the outboard plate for 4-link bracket plates."""
    lower_x = param_cm(design, "lower_pickup_x")
    upper_x = param_cm(design, "upper_pickup_x")
    lower_y = param_cm(design, "lower_pickup_y")
    upper_y = param_cm(design, "upper_pickup_y")
    bw = param_cm(design, "bracket_plate_w")
    bh = param_cm(design, "bracket_plate_h")
    sc = param_cm(design, "slot_clear")
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")

    z_out_inner = cl + sign * (tw / 2.0 + clear)

    for label, xc, yc in (
        ("KEY_LOWER", lower_x, lower_y),
        ("KEY_UPPER", upper_x, upper_y),
    ):
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_out_inner))
        pl = planes.add(pin)
        pl.name = "PL_{}_{}".format(side, label)

        sk = comp.sketches.add(pl)
        sk.name = "SK_{}_{}".format(side, label)
        sk.isComputeDeferred = True
        hx = bw / 2.0 + sc
        hy = bh / 2.0 + sc
        # Key pocket: slightly oversized bracket footprint.
        p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc - hy, z_out_inner))
        p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc + hy, z_out_inner))
        p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc + hy, z_out_inner))
        p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc - hy, z_out_inner))
        lines = sk.sketchCurves.sketchLines
        lines.addByTwoPoints(p00, p01)
        lines.addByTwoPoints(p01, p11)
        lines.addByTwoPoints(p11, p10)
        lines.addByTwoPoints(p10, p00)
        sk.isComputeDeferred = False
        if sk.profiles.count < 1:
            continue
        prof = _largest_profile(sk)
        extrudes = comp.features.extrudeFeatures
        ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
        reverse = sign > 0
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}_{}".format(side, label)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Upper crossmember + 4-link brackets
# ---------------------------------------------------------------------------

def build_upper_crossmember(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    ux = param_cm(design, "upper_pickup_x")
    uy = param_cm(design, "upper_pickup_y")
    uw = param_cm(design, "upper_xmember_w")
    uh = param_cm(design, "upper_xmember_h")
    cl = param_cm(design, "rail_cl")
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")

    # Crossmember spans between inboard faces of LH/RH rails.
    z0 = -(cl - (tw / 2.0 + clear))
    z1 = cl - (tw / 2.0 + clear)
    # Plate sits on XY at upper pickup, extruded clip_t along X (fore-aft thickness).
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(
        comp.yZConstructionPlane,
        adsk.core.ValueInput.createByReal(ux - uw / 2.0),
    )
    pl = planes.add(pin)
    pl.name = "PL_XMEMBER_UPPER"

    sk = comp.sketches.add(pl)
    sk.name = "SK_XMEMBER_UPPER"
    sk.isComputeDeferred = True
    # YZ sketch: x→Z, y→Y
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(ux, uy - uh / 2.0, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(ux, uy + uh / 2.0, z0))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(ux, uy + uh / 2.0, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(ux, uy - uh / 2.0, z1))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("upper_xmember_w"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_XMEMBER_UPPER"
    ext.bodies.item(0).name = "XMEMBER_UPPER"


def build_four_link_brackets(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        _build_link_bracket(comp, design, side, sign, upper=False)
        _build_link_bracket(comp, design, side, sign, upper=True)
        _draw_link_ref(comp, design, side, sign)


def _build_link_bracket(comp, design, side, sign, upper):
    xc = param_cm(design, "upper_pickup_x" if upper else "lower_pickup_x")
    yc = param_cm(design, "upper_pickup_y" if upper else "lower_pickup_y")
    bw = param_cm(design, "bracket_plate_w")
    bh = param_cm(design, "bracket_plate_h")
    hole = param_cm(design, "bracket_hole_d")
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    clip_t = param_cm(design, "clip_t")

    # Bracket plate keys into outboard plate from outside.
    z_face = cl + sign * (tw / 2.0 + clear + clip_t)

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
    label = "UPPER" if upper else "LOWER"
    pl = planes.add(pin)
    pl.name = "PL_BRACKET_{}_{}".format(label, side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_BRACKET_{}_{}".format(label, side)
    sk.isComputeDeferred = True
    hx = bw / 2.0
    hy = bh / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc - hy, z_face))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc + hy, z_face))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc + hy, z_face))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc - hy, z_face))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, yc, z_face))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, hole / 2.0)
    sk.isComputeDeferred = False

    # Profile with hole = ring (2 loops); use that if present.
    prof = None
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        if p.profileLoops.count == 2:
            prof = p
            break
    if prof is None and sk.profiles.count:
        prof = _largest_profile(sk)
    if prof is None:
        return

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Extrude toward vehicle CL so the plate seats into the key slot.
    reverse = sign > 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_BRACKET_{}_{}".format(label, side)
    ext.bodies.item(0).name = "BRACKET_{}_{}".format(label, side)


def _draw_link_ref(comp, design, side, sign):
    """Construction lines for triangulated lower + upper bars (reference)."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_LINK_REF_{}".format(side)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines

    lx = param_cm(design, "lower_pickup_x")
    ly = param_cm(design, "lower_pickup_y")
    ux = param_cm(design, "upper_pickup_x")
    uy = param_cm(design, "upper_pickup_y")
    wb = param_cm(design, "wb")
    ay = param_cm(design, "axle_cl_y")
    az = param_cm(design, "axle_link_spread_z") * sign
    fz = param_cm(design, "frame_link_spread_z") * sign

    # Project to XY (ignore Z for side-view ref).
    lower = lines.addByTwoPoints(
        sk.modelToSketchSpace(adsk.core.Point3D.create(lx, ly, fz)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(wb, ay - 2.54, az)),
    )
    upper = lines.addByTwoPoints(
        sk.modelToSketchSpace(adsk.core.Point3D.create(ux, uy, fz * 0.5)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(wb, ay + 5.08, az * 0.4)),
    )
    lower.isConstruction = True
    upper.isConstruction = True
    sk.isComputeDeferred = False


# ---------------------------------------------------------------------------
# Axle reference mockup (Currie 9-inch parametric — not detailed CAD)
# ---------------------------------------------------------------------------

def build_axle_ref(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    wb = param_cm(design, "wb")
    ay = param_cm(design, "axle_cl_y")
    po = param_cm(design, "pinion_offset")
    csw = param_cm(design, "cs_width")
    csh = param_cm(design, "cs_height")
    csd = param_cm(design, "cs_depth")
    b = param_cm(design, "housing_end_b")

    # Center section box — PLACEHOLDER geometry awaiting Currie data.
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(wb - csd / 2.0))
    pl = planes.add(pin)
    pl.name = "PL_AXLE_CS"

    sk = comp.sketches.add(pl)
    sk.name = "SK_AXLE_CS"
    sk.isComputeDeferred = True
    # Centered on axle CL in Y, offset by pinion_offset in Z (passenger).
    cy, cz = ay, po
    half_w = csw / 2.0
    half_h = csh / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(wb, cy - half_h, cz - half_w))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(wb, cy + half_h, cz - half_w))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(wb, cy + half_h, cz + half_w))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(wb, cy - half_h, cz + half_w))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count:
        prof = _largest_profile(sk)
        extrudes = comp.features.extrudeFeatures
        ext_in = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("cs_depth"))
        ext = extrudes.add(ext_in)
        ext.name = "EX_AXLE_CS"
        body = ext.bodies.item(0)
        body.name = "AXLE_CS_REF"
        try:
            body.opacity = 0.4
        except Exception:
            pass

    # Axle tubes — hollow cylinders along Z from CS faces to housing ends.
    _axle_tube(comp, design, passenger=True)
    _axle_tube(comp, design, passenger=False)

    # WMS / housing-end markers on axle centerline height.
    a = param_cm(design, "axle_wms_a")
    planes2 = comp.constructionPlanes
    pin2 = planes2.createInput()
    pin2.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByString("axle_cl_y"))
    pl2 = planes2.add(pin2)
    pl2.name = "PL_AXLE_CL"
    skw = comp.sketches.add(pl2)
    skw.name = "SK_WMS"
    skw.isComputeDeferred = True
    for z in (a / 2.0, -a / 2.0, b / 2.0, -b / 2.0):
        pt = skw.modelToSketchSpace(adsk.core.Point3D.create(wb, ay, z))
        skw.sketchPoints.add(pt)
    skw.isComputeDeferred = False


def _axle_tube(comp, design, passenger=True):
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    wb = param_cm(design, "wb")
    ay = param_cm(design, "axle_cl_y")
    po = param_cm(design, "pinion_offset")
    csw = param_cm(design, "cs_width")
    tube_od = param_cm(design, "axle_tube_od")
    tube_wall = param_cm(design, "axle_tube_wall")

    # Tube starts at CS outer face in Z and extends outward.
    z0 = po + sign * (csw / 2.0)

    planes = comp.constructionPlanes
    # Plane parallel to XY at z0.
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z0))
    pl = planes.add(pin)
    pl.name = "PL_AXLE_TUBE_{}".format(side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_AXLE_TUBE_{}".format(side)
    sk.isComputeDeferred = True
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(wb, ay, z0))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, tube_od / 2.0)
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, tube_od / 2.0 - tube_wall)
    sk.isComputeDeferred = False

    ring = _find_ring_profile(sk)
    if not ring:
        # Fall back to outer circle only.
        if sk.profiles.count < 1:
            return
        ring = _largest_profile(sk)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    reverse = sign < 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("axle_tube_len"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_AXLE_TUBE_{}".format(side)
    body = ext.bodies.item(0)
    body.name = "AXLE_TUBE_{}".format(side)
    try:
        body.opacity = 0.45
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Bag / coilover upper mounts
# ---------------------------------------------------------------------------

def build_suspension_mounts(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    mode = suspension_mode_value(design)
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        if mode >= 0.5:
            _build_bag_mount(comp, design, side, sign)
        else:
            _build_coilover_mount(comp, design, side, sign)


def _build_bag_mount(comp, design, side, sign):
    wb = param_cm(design, "wb")
    rise = param_cm(design, "kickup_rise")
    rb = param_cm(design, "rail_bottom")
    th = param_cm(design, "tube_h")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    mw = param_cm(design, "bag_mount_w")
    ml = param_cm(design, "bag_mount_l")
    z_off = param_cm(design, "bag_mount_z_off")
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")

    # Sit on raised rail top near axle.
    y = rb + th + clear + rise
    z_out = cl + sign * (tw / 2.0 + clear + t)
    z_inner = z_out - sign * z_off
    z0 = min(z_inner, z_inner - sign * ml)
    z1 = max(z_inner, z_inner - sign * ml)
    x0 = wb - mw / 2.0
    x1 = wb + mw / 2.0

    body = _extrude_rect_plate(
        comp, "BAG", side, x0=x0, x1=x1, y=y, z0=z0, z1=z1,
        thickness_expr="clip_t", up=True,
    )
    if body:
        body.name = "MOUNT_BAG_{}".format(side)


def _build_coilover_mount(comp, design, side, sign):
    wb = param_cm(design, "wb")
    rise = param_cm(design, "kickup_rise")
    rb = param_cm(design, "rail_bottom")
    th = param_cm(design, "tube_h")
    clear = param_cm(design, "clip_clear")
    t = param_cm(design, "clip_t")
    mw = param_cm(design, "coilover_mount_w")
    ml = param_cm(design, "coilover_mount_l")
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")

    y = rb + th + clear + rise
    z_out = cl + sign * (tw / 2.0 + clear + t)
    z0 = min(z_out, z_out - sign * ml)
    z1 = max(z_out, z_out - sign * ml)
    x0 = wb - mw / 2.0
    x1 = wb + mw / 2.0

    body = _extrude_rect_plate(
        comp, "COILOVER", side, x0=x0, x1=x1, y=y, z0=z0, z1=z1,
        thickness_expr="clip_t", up=True,
    )
    if body:
        body.name = "MOUNT_COILOVER_{}".format(side)


# ---------------------------------------------------------------------------
# DXF export — top-face profile sketch per plate body
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


# ---------------------------------------------------------------------------
# Sketch helpers (shared with chassis-setup conventions)
# ---------------------------------------------------------------------------

def _line_mid(line):
    g = line.geometry
    return adsk.core.Point3D.create(
        (g.startPoint.x + g.endPoint.x) / 2.0,
        (g.startPoint.y + g.endPoint.y) / 2.0,
        0,
    )


def _dim_two_sides(sk, rect, expr_a, expr_b):
    line0 = rect.item(0)
    line1 = rect.item(1)
    d0 = sk.sketchDimensions.addDistanceDimension(
        line0.startSketchPoint,
        line0.endSketchPoint,
        DO.AlignedDimensionOrientation,
        _line_mid(line0),
    )
    d1 = sk.sketchDimensions.addDistanceDimension(
        line1.startSketchPoint,
        line1.endSketchPoint,
        DO.AlignedDimensionOrientation,
        _line_mid(line1),
    )
    len0 = line0.length
    len1 = line1.length
    if len0 >= len1:
        d0.parameter.expression = "({}) + 0 in".format(expr_b)
        d1.parameter.expression = "({}) + 0 in".format(expr_a)
    else:
        d0.parameter.expression = "({}) + 0 in".format(expr_a)
        d1.parameter.expression = "({}) + 0 in".format(expr_b)
