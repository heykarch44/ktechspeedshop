# Ktech C10 front-view suspension geometry layout for Autodesk Fusion
#
# Install
#   1. Fusion -> Utilities -> Add-Ins -> Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_C10_FrontGeometry). Keep front_geometry_calc.py next to the .py.
#   4. Open KTECH_C10_CHASSIS (or a new Hybrid design) and Run.
#
# What it draws (sketch SK_FRONT_GEOMETRY, on the YZ plane at the front axle, X = 0)
#   Ground, ride-height lines (0 / 3 / 3.5 design / 4 / 7), vehicle CL, hub CL,
#   tire + wheel outlines, wheel CL, hub mounting face, spindle CL, Wilwood
#   831-14202 ball joints and steering axis extended to ground (scrub), tie-rod
#   height guide, upper + lower arms to locked inner pivots, flat 6 in front
#   rail at 10.07–16.07 (no arch) with ~1.8 in UCA tower + hanging LCA, cab
#   2x5 at 3.5 bottom, lower crossmember + oil pan guide, IC / RC lines.
#
# Workflow
#   Every number is an fg_* user parameter (Modify -> Change Parameters).
#   Change one, then Run this script again: it keeps your edited values and
#   redraws SK_FRONT_GEOMETRY. Comments that say ESTIMATE are not measured yet.
#   To go back to defaults, delete the fg_* parameter (or all of them) and re-run.
#
# Coordinates (same as KTECH_C10_Chassis_Setup)
#   Origin = front axle x ground x frame centerline. +X rear, +Y up, +Z passenger.
#   Driver side = -Z.

import math
import os
import sys
import traceback

import adsk.core
import adsk.fusion

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
except Exception:
    SCRIPT_DIR = os.getcwd()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import front_geometry_calc as fg  # noqa: E402  (shared with make_preview.py)

SKETCH_NAME = "SK_FRONT_GEOMETRY"
COMP_NAME = "05_IFS"
CM = 2.54  # Fusion internal length unit is cm
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
        try:
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        except Exception:
            pass
        try:
            design.fusionUnitsManager.defaultLengthUnits = "in"
        except Exception:
            pass

        added = add_parameters(design)
        v = read_values(design)
        g = fg.design_geometry(v)

        comp = find_or_add_component(design.rootComponent, COMP_NAME)
        delete_old_sketch(comp, SKETCH_NAME)
        sk = comp.sketches.add(comp.yZConstructionPlane)
        sk.name = SKETCH_NAME
        draw(sk, v, g)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        ic = g["ic"]
        ic_txt = ("{:.1f} in from CL ({} side), {:.2f} in high".format(
            abs(ic[0]), "opposite" if ic[0] < 0 else "same", ic[1]) if ic else "at infinity (arms parallel)")
        ui.messageBox(
            "SK_FRONT_GEOMETRY drawn in {} at design ride {:.2f} in.\n\n"
            "Scrub radius at ground: {:+.2f} in (target 0 to +1)\n"
            "Track: {:.2f} in   Offset: {:+.2f} in ({:+.0f} mm)\n"
            "UBJ {:.2f} high   LBJ {:.2f} high\n"
            "Upper arm {:.2f} in @ {:.1f} deg   Lower arm {:.2f} in @ {:.1f} deg\n"
            "Instant center: {}\n"
            "Roll center: {:.2f} in above ground\n\n"
            "{} new fg_* parameters added. Edit them in Change Parameters and re-run.\n"
            "View: look from the front (ViewCube FRONT/BACK shows the YZ plane edge-on;\n"
            "use RIGHT or LEFT to look down X).".format(
                comp.name, v["fg_rh_design"], g["scrub"], v["fg_track"], v["fg_offset"],
                v["fg_offset"] * 25.4, g["ubj"][1], g["lbj"][1], g["uca_len"], g["uca_ang"],
                g["lca_len"], g["lca_ang"], ic_txt, g["rc_y"], added))
    except Exception:
        if ui:
            ui.messageBox("KTECH_C10_FrontGeometry failed:\n{}".format(traceback.format_exc()))


# --- parameters ----------------------------------------------------------------

def add_parameters(design):
    """Create missing fg_* parameters. Existing ones keep the user's expression."""
    params = design.userParameters
    added = 0
    for name, expr, unit, comment in fg.PARAMS:
        try:
            existing = params.itemByName(name)
            if existing:
                existing.comment = comment
                continue
            params.add(name, adsk.core.ValueInput.createByString(expr), unit, comment)
            added += 1
        except Exception:
            continue
    return added


def read_values(design):
    """fg_* values in inches / degrees, the units front_geometry_calc expects."""
    params = design.userParameters
    v = {}
    for name, expr, unit, _c in fg.PARAMS:
        p = params.itemByName(name)
        if p is None:
            raise RuntimeError("Missing user parameter {} ({}).".format(name, expr))
        v[name] = math.degrees(p.value) if unit == "deg" else p.value / CM
    return v


def find_or_add_component(root, name):
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        if occ.component.name == name:
            return occ.component
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def delete_old_sketch(comp, name):
    for i in range(comp.sketches.count - 1, -1, -1):
        s = comp.sketches.item(i)
        if s.name == name:
            s.deleteMe()


# --- drawing helpers -------------------------------------------------------------

class Pen(object):
    """Front-view pen: (z_lateral_in, y_height_in) -> sketch point on the YZ plane."""

    def __init__(self, sk):
        self.sk = sk
        self.lines = sk.sketchCurves.sketchLines

    def pt(self, z, y):
        return self.sk.modelToSketchSpace(adsk.core.Point3D.create(0, y * CM, z * CM))

    def line(self, a, b, construction=False):
        ln = self.lines.addByTwoPoints(self.pt(*a), self.pt(*b))
        ln.isConstruction = construction
        return ln

    def rect(self, z0, y0, z1, y1, construction=False):
        pts = [(z0, y0), (z1, y0), (z1, y1), (z0, y1)]
        out = []
        for i in range(4):
            out.append(self.line(pts[i], pts[(i + 1) % 4], construction))
        return out

    def point(self, z, y):
        return self.sk.sketchPoints.add(self.pt(z, y))

    def arc(self, c, r, a0_deg, sweep_deg):
        start = (c[0] + r * math.cos(math.radians(a0_deg)), c[1] + r * math.sin(math.radians(a0_deg)))
        try:
            arc = self.sk.sketchCurves.sketchArcs.addByCenterStartSweep(
                self.pt(*c), self.pt(*start), math.radians(sweep_deg))
            arc.isConstruction = True
        except Exception:
            pass

    def text(self, z, y, s, h=0.35):
        try:
            texts = self.sk.sketchTexts
            ti = texts.createInput2(s, h * CM)
            ti.setAsMultiLine(self.pt(z, y), self.pt(z + max(len(l) for l in s.split("\n")) * h * 0.9, y + h * 1.6 * (s.count("\n") + 1)),
                              adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                              adsk.core.VerticalAlignments.BottomVerticalAlignment, 0)
            texts.add(ti)
        except Exception:
            try:
                ti = self.sk.sketchTexts.createInput(s, h * CM, self.pt(z, y))
                self.sk.sketchTexts.add(ti)
            except Exception:
                pass

    def dim(self, a, b, orient, text_at):
        """Driven (reference) dimension between two sketch points, so nothing fights."""
        try:
            self.sk.sketchDimensions.addDistanceDimension(
                a, b, orient, self.pt(*text_at), False)
        except Exception:
            pass


def draw(sk, v, g):
    sk.isComputeDeferred = True
    pen = Pen(sk)
    W = 45.0

    # ground, CL, hub CL, ride-height lines
    ground = pen.line((-W, 0), (W, 0))
    pen.line((0, -2), (0, 34), True)
    pen.line((-W, v["fg_hub_y"]), (W, v["fg_hub_y"]), True)
    for key, lab in (("fg_rh_lay", "LAID OUT"), ("fg_rh_a", "RH"), ("fg_rh_design", "DESIGN RH"),
                     ("fg_rh_b", "RH"), ("fg_rh_air", "AIRED UP")):
        y = v[key]
        if y > 0:
            pen.line((-W, y), (W, y), True)
        pen.text(-W, y + 0.1, "{} {:.1f}".format(lab, y), 0.3)

    for s in (1.0, -1.0):
        draw_side(pen, v, g, s)

    # crossmember + oil pan guide (centered)
    xm_half = v["fg_lca_pivot_z"] + 1.0
    pen.rect(-xm_half, v["fg_xm_bottom_y"], xm_half, v["fg_xm_bottom_y"] + v["fg_xm_h"])
    pan_y = v["fg_xm_bottom_y"] + v["fg_pan_clear"]
    pen.line((-6, pan_y), (6, pan_y), True)
    pen.text(-6, pan_y + 0.15, "OIL PAN BTM {:.2f} (EST)".format(pan_y), 0.3)

    # roll center
    rc = g["rc_y"]
    if rc is not None:
        pen.point(0, rc)
        pen.text(0.5, rc - 0.9, "ROLL CENTER {:.2f}".format(rc), 0.4)

    # summary block
    pen.text(-W, 31, (
        "KTECH C10 73-87 FRONT GEOMETRY  design RH {:.2f}\n"
        "Tire {:.1f} x {:.1f}  wheel {:g}x{:g}  BS {:.2f}  offset {:+.2f} in\n"
        "Track {:.2f}  scrub {:+.2f}  KPI {:.1f}  RC {:.2f}\n"
        "UCA {:.2f} in  LCA {:.2f} in  (stock est {:.1f} / {:.1f})").format(
        v["fg_rh_design"], v["fg_tire_od"], v["fg_tire_w"], v["fg_wheel_dia"], v["fg_wheel_w"],
        v["fg_backspace"], v["fg_offset"], v["fg_track"], g["scrub"], v["fg_kpi"], rc or 0.0,
        g["uca_len"], g["lca_len"], v["fg_uca_len_stock"], v["fg_lca_len_stock"]), 0.45)

    sk.isComputeDeferred = False

    # a few driven dimensions on the passenger side (reference only)
    gp = sk.sketchPoints
    try:
        o = pen.point(0, 0)
        ubj = pen.point(*g["ubj"])
        lbj = pen.point(*g["lbj"])
        upv = pen.point(*g["uca_pivot"])
        lpv = pen.point(*g["lca_pivot"])
        wc = pen.point(g["wheel_cl"], 0)
        ag = pen.point(*g["axis_ground"])
        pen.dim(o, ubj, DO.VerticalDimensionOrientation, (g["ubj"][0] + 3, g["ubj"][1] / 2 + 4))
        pen.dim(o, lbj, DO.VerticalDimensionOrientation, (g["lbj"][0] + 4, g["lbj"][1] / 2))
        pen.dim(o, upv, DO.VerticalDimensionOrientation, (g["uca_pivot"][0] - 2, g["uca_pivot"][1] / 2 + 6))
        pen.dim(o, lpv, DO.VerticalDimensionOrientation, (g["lca_pivot"][0] - 2, g["lca_pivot"][1] / 2))
        pen.dim(ag, wc, DO.HorizontalDimensionOrientation, ((g["wheel_cl"] + g["axis_ground"][0]) / 2, -1.5))
        pen.dim(upv, ubj, DO.AlignedDimensionOrientation, ((g["ubj"][0] + g["uca_pivot"][0]) / 2, g["ubj"][1] + 1.5))
        pen.dim(lpv, lbj, DO.AlignedDimensionOrientation, ((g["lbj"][0] + g["lca_pivot"][0]) / 2, g["lbj"][1] - 1.5))
        wcd = pen.point(-g["wheel_cl"], 0)
        pen.dim(wcd, wc, DO.HorizontalDimensionOrientation, (0, -3.5))
    except Exception:
        pass
    _ = gp


def draw_side(pen, v, g, s):
    m = lambda p: (s * p[0], p[1])
    hub_y = v["fg_hub_y"]
    wcl = s * g["wheel_cl"]

    # tire and wheel (front-view rectangles)
    pen.rect(wcl - v["fg_tire_w"] / 2, 0, wcl + v["fg_tire_w"] / 2, v["fg_tire_od"])
    pen.rect(wcl - v["fg_wheel_w"] / 2, hub_y - v["fg_wheel_dia"] / 2,
             wcl + v["fg_wheel_w"] / 2, hub_y + v["fg_wheel_dia"] / 2, True)
    pen.line((wcl, 0), (wcl, v["fg_tire_od"] + 1), True)  # wheel CL

    # hub mounting face (6.40 flange) and spindle CL
    fz = s * g["face_z"]
    pen.line((fz, hub_y - 3.2), (fz, hub_y + 3.2))
    pen.line(m(g["axis_cl"]), (fz, hub_y))

    # steering axis: BJ to BJ solid, extended to ground as construction
    u, l, ag = m(g["ubj"]), m(g["lbj"]), m(g["axis_ground"])
    pen.line(u, l)
    pen.line(l, ag, True)
    pen.point(*u)
    pen.point(*l)
    pen.point(*ag)
    pen.point(wcl, 0)  # contact patch center

    # tie-rod height guide
    pen.line((s * 20, g["tre"][1]), (s * 30, g["tre"][1]), True)

    # arms
    up, lp = m(g["uca_pivot"]), m(g["lca_pivot"])
    pen.line(up, u)
    pen.line(lp, l)
    pen.point(*up)
    pen.point(*lp)

    # rails: flat front clip at arms (10.07–16.07) + cab/center 2x5 at 3.5 (construction)
    rz, tw, th = s * v["fg_rail_cl"], v["fg_tube_w"], v["fg_tube_h"]
    yb = v["fg_front_rail_bottom"]
    pen.rect(rz - tw / 2, yb, rz + tw / 2, yb + th)
    cab_h = v.get("fg_cab_rail_h", 5.0)
    cab_b = v.get("fg_cab_rail_bottom", v["fg_rh_design"])
    pen.rect(rz - tw / 2, cab_b, rz + tw / 2, cab_b + cab_h, True)
    # UCA tower (no arch) + hanging LCA drop
    pen.line((up[0], yb + th), up, True)
    pen.line((lp[0], yb), lp, True)

    # stock-length reference arcs (where a stock-length arm's inner pivot would land)
    a0 = 150 if s > 0 else -30
    pen.arc(u, v["fg_uca_len_stock"], a0, 60)
    pen.arc(l, v["fg_lca_len_stock"], a0, 60)

    # instant center + roll center construction
    ic = g["ic"]
    if ic:
        icm = m(ic)
        if abs(icm[0]) < 400 and abs(icm[1]) < 400:
            pen.line(up, icm, True)
            pen.line(lp, icm, True)
            pen.line((wcl, 0), icm, True)

    if s > 0:
        pen.text(u[0] + 0.6, u[1] + 0.3, "UBJ {:.2f}".format(u[1]))
        pen.text(l[0] + 0.6, l[1] - 0.9, "LBJ {:.2f}".format(l[1]))
        pen.text(up[0] - 1.0, up[1] + 0.6, "UCA PIVOT {:.2f}".format(up[1]))
        pen.text(lp[0] - 1.0, lp[1] - 1.0, "LCA PIVOT {:.2f}".format(lp[1]))
        pen.text(fz + 0.4, hub_y + 3.4, "HUB FACE")
        pen.text(s * 20, g["tre"][1] - 0.7, "TIE ROD HT {:.2f}".format(g["tre"][1]), 0.3)
        pen.text(ag[0] - 1, -2.4, "SCRUB {:+.2f}".format(g["scrub"]), 0.45)
        tower = v.get("fg_uca_tower", up[1] - (yb + th))
        hang = v.get("fg_lca_hang", yb - lp[1])
        pen.text(rz + tw / 2 + 0.4, yb + th / 2, "FLAT RAIL 10.07-16.07", 0.3)
        pen.text(rz + tw / 2 + 0.4, yb + th + 0.4, "TOWER +{:.2f}".format(tower), 0.3)
        pen.text(rz + tw / 2 + 0.4, yb - 0.8, "HANG {:.2f}".format(hang), 0.3)
