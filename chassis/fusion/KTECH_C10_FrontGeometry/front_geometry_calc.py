# Ktech C10 front-view suspension geometry math.
# Pure Python (no Fusion imports). Shared by KTECH_C10_FrontGeometry.py (Fusion)
# and make_preview.py (matplotlib PNG) so both draw the same numbers.
#
# 2D front view, inches. z = lateral from vehicle centerline (+ = outboard),
# y = height above ground. One side is computed; the other is a mirror.
#
# Design pose: inner pivots and rail locked to the 2026-11-25 package.
#   Tire is now 27.5 OD (275/35/20, both ends; was 29.0 on 22x9).
#   Hub at ride ~13.75 (was 14.50). Inner pivots were NOT moved:
#   LCA (13.50, 8.07), UCA (15.50, 17.88), front rail 10.07–15.07.
#   Wilwood 831-14202 BJ math is unchanged (relative to the hub).
#   FLAG: with the 27.5 tire the lower arm is no longer level at ride;
#   ride LBJ ~7.34 (was 8.07). Arm still clears the rail at ride and layout.

import math

# name, default expression, unit, comment.
# "ESTIMATE" in a comment = not measured on the truck or not printed on a drawing.
PARAMS = [
    # --- Tire / wheel --------------------------------------------------------
    ("fg_tire_od", "27.5 in", "in", "275/35/20 both ends (2026-11-27). Hub at ride = OD/2 ≈ 13.75 (was 29 in / 14.50 on 22x9). Inner pivots and rail were not moved."),
    ("fg_tire_w", "10.83 in", "in", "275 mm section (275/35/20). Was 10.0 on the 22x9 package. FLAG: fender lip gap shrinks ~3.10 to ~2.69 if BS/offset stay."),
    ("fg_wheel_dia", "20 in", "in", "275/35R20 wheel. Was 22. Width and backspace were not retaped (still fg_wheel_w=9 / fg_backspace=7)."),
    ("fg_wheel_w", "9 in", "in", "Wheel width (bead seat)"),
    ("fg_hub_y", "fg_tire_od / 2", "in", "Hub centerline above ground = tire OD / 2"),
    ("fg_backspace", "7.0 in", "in", "Wheel backspacing. 5.0 = zero offset on a 9 in wheel. 7.0 cuts scrub to ~1.6 in"),
    ("fg_offset", "fg_backspace - (fg_wheel_w + 1 in) / 2", "in", "Computed. + = hub face outboard of wheel CL. 1 in = 25.4 mm"),
    # --- Track / hub face location ----------------------------------------
    ("fg_track_ref", "65.8 in", "in", "ESTIMATE. Stock 73-87 C10 front track 65.8 in (GM spec, HAMB thread 911283, center of tread). Wilwood says 14202 keeps OE track"),
    ("fg_ref_offset", "0 in", "in", "ESTIMATE. Offset of the stock wheel that the 65.8 track was measured on (assumed zero)"),
    ("fg_hub_face_z", "fg_track_ref / 2 + fg_ref_offset", "in", "Computed. Hub mounting face from vehicle CL (fixed by spindle + arms). 32.90 with defaults"),
    ("fg_track", "2 * (fg_hub_face_z - fg_offset)", "in", "Computed. Track width with the chosen backspacing (61.80 at 7.0 BS)"),
    # --- Wilwood 831-14202 spindle ----------------------------------------
    ("fg_kpi", "8 deg", "deg", "Steering axis 82 deg to spindle axis on 14202 and 15932 prints = 8 deg KPI"),
    ("fg_bj_spread", "9.06 in", "in", "14202 print: taper large-end face to face along steering axis"),
    ("fg_ubj_face_above", "3.55 in", "in", "ESTIMATE (scaled off 14202 print). Upper taper large end above spindle CL, vertical"),
    ("fg_lbj_face_below", "5.44 in", "in", "ESTIMATE (scaled off 14202 print; iron 15932 print shows 4.92). Lower taper large end below spindle CL, vertical"),
    ("fg_ubj_ball", "1.0 in", "in", "ESTIMATE. Upper ball-joint ball center beyond the taper large end, along axis (73-87 upper BJ)"),
    ("fg_lbj_ball", "1.0 in", "in", "ESTIMATE. Lower ball-joint ball center beyond the taper large end, along axis (73-87 lower BJ)"),
    ("fg_axis_to_face", "5.7 in", "in", "Per Wilwood (Bryan 11/20): LBJ 1.23 in inboard of caliper lug + 3.68 lug-to-hub face + 8 deg KPI over drop. Same for 14202 and iron 15932"),
    ("fg_tre_drop", "2.35 in", "in", "14202 print: tie-rod hole below spindle CL"),
    # --- Ride heights (cab / frame bottom to ground) ----------------------
    ("fg_rh_design", "3.5 in", "in", "Design ride: cab/center rail bottom to ground. Sketch is drawn here"),
    ("fg_rh_lay", "0 in", "in", "Laid out (frame down 3.5 so cab rails sit on the ground)"),
    ("fg_rh_a", "3 in", "in", "Ride-height guide line"),
    ("fg_rh_b", "4 in", "in", "Ride-height guide line"),
    ("fg_rh_air", "7 in", "in", "Aired up (cab bottom ~7; front rail 13.57–18.57)"),
    # --- Frame (flat front clip + 2x5 cab; no arch) -----------------------
    ("fg_tube_w", "2 in", "in", "Rail / tube width across the car"),
    ("fg_tube_h", "5 in", "in", "Front-clip rail height at the arms (flat 5 in; was 6; no arch)"),
    ("fg_cab_rail_h", "5 in", "in", "Purchased center spine 2x5"),
    ("fg_front_rail_bottom", "10.07 in", "in", "Front-clip rail bottom at arms (design ride). Top = 15.07"),
    ("fg_cab_rail_bottom", "3.5 in", "in", "Cab/center section bottom at design ride (= fg_rh_design)"),
    ("fg_rail_cl", "16.0 in", "in", "Rail CL from vehicle CL through arms/engine (34 in OD). Literal — NOT core_width/2"),
    # --- Inner pivots (locked) + derived hang / tower -----------------------
    ("fg_lca_pivot_y", "8.07 in", "in", "LOCKED lower inner pivot height. Was = LBJ and level at the 29 in ride. With 27.5 tire, ride LBJ ~7.34 and the lower arm droops ~2.9 deg — pivot was not moved."),
    ("fg_lca_pivot_z", "13.50 in", "in", "Lower inner pivot from vehicle CL (locked)"),
    ("fg_uca_pivot_y", "17.88 in", "in", "Upper inner pivot height at design ride (locked; ~2.81 tower above rail top)"),
    ("fg_uca_pivot_z", "15.50 in", "in", "Upper inner pivot lateral off CL (locked; not rail_cl - tube_w/4)"),
    ("fg_uca_tower", "fg_uca_pivot_y - (fg_front_rail_bottom + fg_tube_h)", "in", "Upper tower above flat rail top (~2.81). Replaces arch"),
    ("fg_lca_hang", "fg_front_rail_bottom - fg_lca_pivot_y", "in", "Hanging lower mount below rail bottom (2.00 at defaults)"),
    # --- Lower crossmember / pan guide --------------------------------------
    ("fg_xm_bottom_y", "5.0 in", "in", "ESTIMATE. Crossmember bottom above ground at design ride"),
    ("fg_xm_h", "3.5 in", "in", "ESTIMATE. Crossmember depth"),
    ("fg_pan_clear", "0.75 in", "in", "ESTIMATE. Oil pan bottom above crossmember bottom"),
    # --- Stock reference arm lengths (for comparison only) ----------------
    ("fg_uca_len_stock", "10.0 in", "in", "ESTIMATE. Stock 73-87 C10 upper arm, pivot axis to BJ, front view. No reliable published number"),
    ("fg_lca_len_stock", "15.5 in", "in", "ESTIMATE. Stock 73-87 C10 lower arm, pivot axis to BJ, front view. No reliable published number"),
]


def _line_intersect(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / den, (a * (y3 - y4) - (y1 - y2) * b) / den)


def default_values():
    """Evaluate the defaults in plain Python (inches / degrees) for the preview."""
    v = {}
    for name, expr, _unit, _c in PARAMS:
        e = expr.replace(" in", "").replace(" deg", "")
        e = e.replace("cos(fg_kpi)", "math.cos(math.radians(fg_kpi))")
        v[name] = float(eval(e, {"math": math}, dict(v)))
    return v


def design_geometry(v):
    """Points at design ride height. z outboard (+), y up. Inches.

    Wilwood BJ math is relative to the hub. At the frozen 29 in hub 14.50, UBJ≈(26.56, 19.04), LBJ≈(28.10, 8.07). With fg_tire_od=27.5 the hub is 13.75; if this function is evaluated at that hub without a pose solve, BJ Y values drop 0.75. The locked inner pivots stay at 8.07 / 17.88 — do not re-derive them from the new LBJ.
    """
    k = math.radians(v["fg_kpi"])
    hub_y = v["fg_hub_y"]
    face_z = v["fg_hub_face_z"]
    axis_z_cl = face_z - v["fg_axis_to_face"]            # steering axis at spindle CL height
    up_dy = v["fg_ubj_face_above"] + v["fg_ubj_ball"] * math.cos(k)
    lo_dy = v["fg_lbj_face_below"] + v["fg_lbj_ball"] * math.cos(k)
    ubj = (axis_z_cl - up_dy * math.tan(k), hub_y + up_dy)
    lbj = (axis_z_cl + lo_dy * math.tan(k), hub_y - lo_dy)
    axis_ground = (axis_z_cl + hub_y * math.tan(k), 0.0)
    wheel_cl = face_z - v["fg_offset"]
    contact = (wheel_cl, 0.0)
    g = dict(ubj=ubj, lbj=lbj, axis_ground=axis_ground, axis_cl=(axis_z_cl, hub_y),
             wheel_cl=wheel_cl, contact=contact, hub=(face_z, hub_y), face_z=face_z,
             uca_pivot=(v["fg_uca_pivot_z"], v["fg_uca_pivot_y"]),
             lca_pivot=(v["fg_lca_pivot_z"], v["fg_lca_pivot_y"]),
             tre=(None, hub_y - v["fg_tre_drop"]))
    g["scrub"] = wheel_cl - axis_ground[0]               # + = axis hits ground inboard of patch
    g["uca_len"] = math.dist(g["uca_pivot"], ubj)
    g["lca_len"] = math.dist(g["lca_pivot"], lbj)
    g["uca_ang"] = math.degrees(math.atan2(ubj[1] - g["uca_pivot"][1], ubj[0] - g["uca_pivot"][0]))
    g["lca_ang"] = math.degrees(math.atan2(lbj[1] - g["lca_pivot"][1], lbj[0] - g["lca_pivot"][0]))
    g["ic"] = _line_intersect(g["uca_pivot"], ubj, g["lca_pivot"], lbj)
    g["rc_y"] = _roll_center(contact, g["ic"])
    g["bj_center_spread"] = math.dist(ubj, lbj)
    g["camber"] = 0.0
    # Flat rail top at the arms (no arch). Tower is above this.
    g["rail_top"] = v["fg_front_rail_bottom"] + v["fg_tube_h"]
    g["rail_bottom_front"] = v["fg_front_rail_bottom"]
    g["uca_tower"] = v.get("fg_uca_tower", g["uca_pivot"][1] - g["rail_top"])
    g["lca_hang"] = v.get("fg_lca_hang", v["fg_front_rail_bottom"] - v["fg_lca_pivot_y"])
    return g


def _roll_center(contact, ic):
    if ic is None:
        return contact[1]  # parallel arms: RC at ground plane line parallel -> handle simply
    cz, cy = contact
    iz, iy = ic
    if abs(iz - cz) < 1e-9:
        return None
    return cy + (iy - cy) * (0 - cz) / (iz - cz)


def _rot(p, c, a):
    s, co = math.sin(a), math.cos(a)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * co - y * s, c[1] + x * s + y * co)


def solve_ride_height(v, rh):
    """Frame fixed, wheel moves. Returns geometry relative to the ground at ride height rh."""
    g0 = design_geometry(v)
    P_l, P_u = g0["lca_pivot"], g0["uca_pivot"]
    L_l, L_u, d = g0["lca_len"], g0["uca_len"], g0["bj_center_spread"]
    th0 = math.atan2(g0["lbj"][1] - P_l[1], g0["lbj"][0] - P_l[0])
    # Upright body points, in design pose
    body = dict(ubj=g0["ubj"], lbj=g0["lbj"], contact=g0["contact"], axis_ground=g0["axis_ground"], hub=g0["hub"])

    def pose(th):
        lbj = (P_l[0] + L_l * math.cos(th), P_l[1] + L_l * math.sin(th))
        # UBJ = circle(P_u, L_u) ∩ circle(lbj, d), pick the solution near design
        dx, dy = P_u[0] - lbj[0], P_u[1] - lbj[1]
        D = math.hypot(dx, dy)
        if D > L_u + d or D < abs(L_u - d):
            return None
        a = (d * d - L_u * L_u + D * D) / (2 * D)
        h = math.sqrt(max(d * d - a * a, 0))
        mx, my = lbj[0] + a * dx / D, lbj[1] + a * dy / D
        c1 = (mx - h * dy / D, my + h * dx / D)
        c2 = (mx + h * dy / D, my - h * dx / D)
        ref = g0["ubj"]
        ubj = c1 if math.dist(c1, ref) < math.dist(c2, ref) else c2
        # rigid transform of upright: design (lbj0->ubj0) -> (lbj->ubj)
        a0 = math.atan2(body["ubj"][1] - body["lbj"][1], body["ubj"][0] - body["lbj"][0])
        a1 = math.atan2(ubj[1] - lbj[1], ubj[0] - lbj[0])
        rot = a1 - a0

        def tf(p):
            q = _rot(p, body["lbj"], rot)
            return (q[0] + lbj[0] - body["lbj"][0], q[1] + lbj[1] - body["lbj"][1])
        return dict(lbj=lbj, ubj=ubj, contact=tf(body["contact"]), hub=tf(body["hub"]),
                    camber=math.degrees(rot))  # + rot (CCW, top moves inboard on +z side) = negative camber

    # frame bottom height above ground = cab_rail_bottom(frame coords) - contact_y
    target = rh
    rail_b = v["fg_rh_design"]

    def f(th):
        p = pose(th)
        return None if p is None else (rail_b - p["contact"][1]) - target

    lo, hi = th0 - math.radians(40), th0 + math.radians(40)
    # scan for a bracket
    ths = [lo + (hi - lo) * i / 400 for i in range(401)]
    vals = [f(t) for t in ths]
    best = None
    for i in range(400):
        if vals[i] is None or vals[i + 1] is None:
            continue
        if vals[i] == 0 or vals[i] * vals[i + 1] < 0:
            a, b = ths[i], ths[i + 1]
            for _ in range(60):
                m = (a + b) / 2
                if f(a) * f(m) <= 0:
                    b = m
                else:
                    a = m
            cand = (a + b) / 2
            if best is None or abs(cand - th0) < abs(best - th0):
                best = cand
    if best is None:
        return None
    p = pose(best)
    gy = p["contact"][1]
    shift = lambda q: (q[0], q[1] - gy)
    ubj, lbj = shift(p["ubj"]), shift(p["lbj"])
    upv, lpv = shift(P_u), shift(P_l)
    ic = _line_intersect(upv, ubj, lpv, lbj)
    contact = shift(p["contact"])
    k_now = math.atan2(ubj[0] - lbj[0], ubj[1] - lbj[1])  # lean of axis (neg = top inboard)
    # axis ground intersection
    t = -lbj[1] / (ubj[1] - lbj[1])
    axis_g = lbj[0] + t * (ubj[0] - lbj[0])
    return dict(rh=rh, ubj=ubj, lbj=lbj, uca_pivot=upv, lca_pivot=lpv, ic=ic,
                rc_y=_roll_center(contact, ic), contact=contact,
                camber=-p["camber"], kpi=-math.degrees(k_now),
                scrub=contact[0] - axis_g, half_track_change=contact[0] - g0["contact"][0],
                hub_y=shift(p["hub"])[1],
                uca_ang=math.degrees(math.atan2(ubj[1] - upv[1], ubj[0] - upv[0])),
                lca_ang=math.degrees(math.atan2(lbj[1] - lpv[1], lbj[0] - lpv[0])))
