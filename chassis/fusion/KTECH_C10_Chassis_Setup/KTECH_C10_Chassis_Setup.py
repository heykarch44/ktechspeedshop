# Ktech C10 chassis setup for Autodesk Fusion 360
#
# Install
#   1. Fusion → Utilities → Add-Ins → Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_C10_Chassis_Setup)
#   4. Run it. It opens a NEW document. Save as KTECH_C10_CHASSIS.
#
# After it runs
#   Tape is in mount_points.csv: three widths + two spans (measured 2026-09-01).
#
# Front knuckle (locked)
#   Wilwood ProSpindle 831-14202, 2.5" drop, 1971-1987 C10
#   Same knuckle on 67-72 and 73-87. 73-87 ball joints in the new A-arms.
#   Forged aluminum, modular hub, 5x4.75 and 5x5. Drawing: wilwood-831-14202.png
#
# Coordinates (Fusion Y-up)
#   Origin = front axle × ground × frame centerline
#   +X = rear   +Y = up   +Z = passenger (right)

import csv
import os
import traceback

import adsk.core
import adsk.fusion

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
except Exception:
    SCRIPT_DIR = os.getcwd()

PARAM_ORDER = [
    ("tube_w", "2 in", "in", "A500 width across the car"),
    ("tube_h", "6 in", "in", "A500 height"),
    ("wall", "0.188 in", "in", "A500 wall"),
    ("rail_bottom", "8 in", "in", "Bottom of tube off ground"),
    ("front_overhang", "34 in", "in", "Tube ahead of front axle"),
    ("wb", "117.5 in", "in", "Wheelbase"),
    ("rear_overhang", "42 in", "in", "Tube behind rear axle"),
    ("overlap", "14 in", "in", "Clip socket on the tube"),
    ("clip_t", "0.188 in", "in", "Clip plate thickness"),
    ("clip_clear", "0.030 in", "in", "C-socket clearance per side"),
    ("tire_od", "32 in", "in", "Lay-out tire"),
    ("bag_stroke", "11 in", "in", "Bag travel target"),
    ("spindle_drop", "2.5 in", "in", "Wilwood 831-14202 2.5 drop. Locked."),
    ("bj_spread", "9.06 in", "in", "Upper to lower BJ hole centers along kingpin"),
    ("kpi_to_hub", "3.68 in", "in", "Hub face to BJ axis"),
    ("kingpin_deg", "82", "", "BJ axis vs hub face, degrees. Drawing."),
    ("tre_reach", "4.09 in", "in", "Hub center to tie-rod hole, plan"),
    ("tre_drop", "2.35 in", "in", "Tie-rod hole below spindle CL"),
    ("spine_length", "front_overhang + wb + rear_overhang", "in", "Computed"),
    ("core_width", "33.5 in", "in", "TAPED. Core support C-C"),
    ("mid_width", "42.5 in", "in", "TAPED. Mid / cab-front mount C-C"),
    ("rear_cab_width", "23.5 in", "in", "TAPED. Back of cab mount C-C"),
    ("core_to_mid", "55 in", "in", "TAPED. Core to mid mount along the rail"),
    ("mid_to_rear", "43 in", "in", "TAPED. Mid to back-of-cab along the rail"),
    ("mount_y", "rail_bottom + tube_h", "in", "Mounts on top of rail"),
    ("core_half", "core_width / 2", "in", "Computed"),
    ("mid_half", "mid_width / 2", "in", "Computed"),
    ("rear_half", "rear_cab_width / 2", "in", "Computed"),
    ("rail_cl", "core_width / 2", "in", "2x6 follows core. Mid/rear mounts are hats."),
    ("core_x", "-33 in", "in", "Core vs front axle. Set when IFS is placed."),
    ("cab_f_x", "core_x + core_to_mid", "in", "Computed"),
    ("cab_r_x", "cab_f_x + mid_to_rear", "in", "Computed"),
]

STATIONS = (
    ("core", "core_x", "CORE", "core"),
    ("cab_f", "cab_f_x", "CAB_F", "mid"),
    ("cab_r", "cab_r_x", "CAB_R", "rear"),
)

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
            root.name = "KTECH_C10_CHASSIS"
        except Exception:
            pass

        already = False
        for i in range(root.occurrences.count):
            if "01_SPINE_2x6" in root.occurrences.item(i).name:
                already = True
                break
        if already:
            ui.messageBox(
                "This document already has the chassis in it.\n\n"
                "File → New Design, then Run the script again."
            )
            return

        mark = add_component(root, "00_ORIGIN")
        mark_origin(mark)

        skel = add_component(root, "00_SKELETON")
        spine = add_component(root, "01_SPINE_2x6")
        add_component(root, "02_CLIP_FRONT")
        add_component(root, "03_CLIP_REAR")
        mounts = add_component(root, "04_MOUNTS_73_87")
        add_component(root, "04_MOUNTS_67_72")
        add_component(root, "05_IFS")
        add_component(root, "06_REAR")
        add_component(root, "07_FIXTURE")

        draw_layout_sketches(skel)
        build_spine(spine)
        build_mount_points(mounts)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        ui.messageBox(
            "Rails are in this Untitled document.\n\n"
            "If you still see a blank cube: click the canvas and press the Home / Fit view.\n"
            "The 2x6s sit 16 in off centerline — not on the origin.\n\n"
            "Browser (left) should list 00_SKELETON and 01_SPINE_2x6.\n"
            "Save as KTECH_C10_CHASSIS."
        )
    except Exception:
        if ui:
            ui.messageBox("KTECH_C10_Chassis_Setup failed:\n{}".format(traceback.format_exc()))


def apply_csv_overrides():
    """Load parameters.csv then mount_points.csv into PARAM_ORDER expressions."""
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "parameters.csv")
    if os.path.isfile(params_path):
        with open(params_path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                name = (row.get("name") or "").strip()
                if name not in by_name:
                    continue
                expr = (row.get("expression") or "").strip()
                unit = (row.get("unit") or "in").strip()
                comment = (row.get("comment") or by_name[name][3]).strip()
                by_name[name] = (name, _expr_with_unit(expr, unit), unit, comment)

    mounts_path = os.path.join(SCRIPT_DIR, "mount_points.csv")
    if os.path.isfile(mounts_path):
        with open(mounts_path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                name = (row.get("name") or "").strip()
                inches = (row.get("inches") or "").strip()
                if name not in by_name or not inches:
                    continue
                note = (row.get("note") or by_name[name][3]).strip()
                by_name[name] = (name, _expr_with_unit(inches, "in"), "in", note)

    PARAM_ORDER[:] = [by_name[row[0]] for row in PARAM_ORDER]


def _expr_with_unit(expr, unit):
    expr = expr.strip()
    if not expr:
        return expr
    if any(ch.isalpha() for ch in expr):
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
            elif name == "kingpin_deg":
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


def add_component(parent, name):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def mark_origin(comp):
    """6 in cube on the origin so a successful run is obvious before Fit."""
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


def param_cm(design, name):
    return design.userParameters.itemByName(name).value


def draw_layout_sketches(comp):
    # Side view lives on XY (Z = 0, the centerline).
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
    side.isComputeDeferred = False
    dims = side.sketchDimensions
    ground.isConstruction = True
    axle_f.isConstruction = True
    axle_r.isConstruction = True
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
    g_dim.parameter.expression = "spine_length + 0 in"

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
    cl_len.parameter.expression = "spine_length + 0 in"
    rail_dim = tdims.addDistanceDimension(
        cl.startSketchPoint,
        rh.startSketchPoint,
        DO.VerticalDimensionOrientation,
        adsk.core.Point3D.create(-10, 5, 0),
    )
    rail_dim.parameter.expression = "rail_cl + 0 in"


def build_spine(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    sk = comp.sketches.add(comp.yZConstructionPlane)
    sk.name = "SK_RAIL_RH_SECTION"
    _tube_section(sk, design, x_world=0.0)

    ring = None
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        if prof.profileLoops.count == 2:
            ring = prof
            break
    if not ring:
        raise RuntimeError("Could not find the 2x6 tube ring profile.")

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    try:
        ext_in.setTwoSidesDistanceExtent(
            adsk.core.ValueInput.createByString("wb + rear_overhang"),
            adsk.core.ValueInput.createByString("front_overhang"),
        )
    except Exception:
        ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("spine_length"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_RAIL_RH"
    ext.bodies.item(0).name = "RAIL_RH"

    bodies = adsk.core.ObjectCollection.create()
    bodies.add(ext.bodies.item(0))
    mirror_in = comp.features.mirrorFeatures.createInput(bodies, comp.xYConstructionPlane)
    mirror = comp.features.mirrorFeatures.add(mirror_in)
    mirror.name = "MIR_RAIL_LH"
    if mirror.bodies.count:
        mirror.bodies.item(0).name = "RAIL_LH"


def _tube_section(sk, design, x_world):
    rb = param_cm(design, "rail_bottom")
    th = param_cm(design, "tube_h")
    tw = param_cm(design, "tube_w")
    cl = param_cm(design, "rail_cl")
    wall = param_cm(design, "wall")

    x = x_world
    cy = rb + th / 2.0
    cz = cl
    outer_c = sk.modelToSketchSpace(adsk.core.Point3D.create(x, cy, cz))
    outer_r = sk.modelToSketchSpace(adsk.core.Point3D.create(x, cy + th / 2.0, cz + tw / 2.0))
    inner_r = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x, cy + th / 2.0 - wall, cz + tw / 2.0 - wall)
    )

    sk.isComputeDeferred = True
    outer = sk.sketchCurves.sketchLines.addCenterPointRectangle(outer_c, outer_r)
    inner = sk.sketchCurves.sketchLines.addCenterPointRectangle(outer_c, inner_r)
    sk.isComputeDeferred = False

    _dim_two_sides(sk, outer, "tube_w", "tube_h")
    _dim_two_sides(sk, inner, "tube_w - 2 * wall", "tube_h - 2 * wall")


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


def build_mount_points(comp):
    planes = comp.constructionPlanes
    points = comp.constructionPoints

    y_in = planes.createInput()
    y_in.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByString("mount_y"))
    pl_y = planes.add(y_in)
    pl_y.name = "PL_MOUNT_Y"

    z_planes = {}
    for key, expr, name in (
        ("core_rh", "core_half", "PL_CORE_Z_RH"),
        ("core_lh", "-core_half", "PL_CORE_Z_LH"),
        ("mid_rh", "mid_half", "PL_MID_Z_RH"),
        ("mid_lh", "-mid_half", "PL_MID_Z_LH"),
        ("rear_rh", "rear_half", "PL_REAR_Z_RH"),
        ("rear_lh", "-rear_half", "PL_REAR_Z_LH"),
    ):
        zin = planes.createInput()
        zin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByString(expr))
        pl = planes.add(zin)
        pl.name = name
        z_planes[key] = pl

    for _station, x_param, label, side in STATIONS:
        xin = planes.createInput()
        xin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByString(x_param))
        pl_x = planes.add(xin)
        pl_x.name = "PL_{}".format(label)

        rh_in = points.createInput()
        rh_in.setByThreePlanes(pl_x, pl_y, z_planes[side + "_rh"])
        rh = points.add(rh_in)
        rh.name = "{}_RH".format(label)

        lh_in = points.createInput()
        lh_in.setByThreePlanes(pl_x, pl_y, z_planes[side + "_lh"])
        lh = points.add(lh_in)
        lh.name = "{}_LH".format(label)
