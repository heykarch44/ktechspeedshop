# Ktech C10 utility module for Autodesk Fusion 360
#
# Install
#   1. Fusion → Utilities → Add-Ins → Scripts and Add-Ins
#   2. Next to My Scripts, click the green +
#   3. Select this folder (KTECH_C10_UtilityModule)
#   4. Run it. It opens / uses a Design document. Save as KTECH_C10_UTILITY_MODULE.
#
# Design intent
#   Bench-built bolt-in tray. Air & fuel utility module uses 2x4 tube
#   rails (mod_w=2 across car, mod_h=4 tall) that slide INSIDE the
#   rear-clip rectangular receivers (rcv_w x rcv_h) by mod_insert_depth
#   (default 6 in) and cross-bolt. Module bottom at rail_bottom 3.5 /
#   top 7.5 at ride. mod_front_x = rcv_rear_x - mod_insert_depth; receiver
#   length on the clip is shortened to key bay + end cap + tip clear +
#   insert (match rear-clip expressions). Tray is keyed laser-cut plate.
#   Parametric envelopes / mounts for fuel tank (welded alum box + Boyd
#   21057 sump + Radium 20-0278 6x10 24-bolt weld flange / FCST-X + Usher
#   UD3F fill + Ace Race Parts ORB feed/return/drain/vent + SAE 5-bolt
#   sender), air tank, twin compressors, valve manifold, twin batteries.
#   Forward bulkhead service plate with AN fuel feed/return, air,
#   battery-cable, and control pass-throughs.
#   module_variant = air_fuel | fuel_only.
#
# Fuel fittings (sourced) — see README for full URLs
#   Radium 20-0278 6x10 24-bolt weld flange + 18-0015 FKM gasket; FCST-X
#     https://www.radiumauto.com/products/fuel-cell-mounting-accessories
#     https://www.radiumauto.com/products/fcst-x-fuel-cell-surge-tank
#   Nuke Performance 6x10-24bolts.DXF (bolt / opening geometry)
#     https://www.nukeperformance.com/dokument/6x10-24bolts.DXF
#   Dakota Digital SEN-06-1 / Tanks Inc SAE 5-hole sender
#     https://www.dakotadigital.com/index.cfm/page/ptype=product/product_id=112/mode=prod/prd112.htm
#     https://www.tanksinc.com/index.cfm/page/ptype=results/category_id=159/mode=cat/cat159.htm
#   Ace Race Parts 6061 ORB weld bungs (-6 / -8) via K2 Fabrication
#     https://www.k2-fabrication.com/products/6an-female-weld-bung-6061-aluminum
#     https://www.k2-fabrication.com/products/8an-female-weld-bung-6061-aluminum
#   Usher UD3F flush aero weld-on filler
#     https://www.fillernecksupply.com/usher-precision-manufacturing-aero-aluminum-flush-mount-fuel-filler-neck-flange-and-cap-weld-on-ud3f-us-3-f/
#   Boyd Welding 21057 2.5 in OD weld-in sump
#     https://fueltankparts.com/products/2-5-od-aluminum-weld-in-sump
# PLACEHOLDER still: tank shell size, sender screw angles (SAE uneven),
#   bung pilot holes, filler cutout, rollover valve fit.
#
# Coordinates (Fusion Y-up) — same as KTECH_C10_RearClip / Chassis_Setup
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

PLATE_BODY_NAMES = (
    "TRAY_FLOOR",
    "TRAY_KEY_RH",
    "TRAY_KEY_LH",
    "BULKHEAD_SERVICE",
    "FUEL_PUMP_FLANGE",
    "MOUNT_FUEL_RH",
    "MOUNT_FUEL_LH",
    "MOUNT_AIR",
    "MOUNT_COMP_RH",
    "MOUNT_COMP_LH",
    "MOUNT_MANIFOLD",
    "MOUNT_BATT_RH",
    "MOUNT_BATT_LH",
)

STRING_PARAMS = {
    "module_variant": "air_fuel",
}

PARAM_ORDER = [
    # Shared names (match rear clip / chassis setup where they apply)
    ("tube_w", "2 in", "in", "Shared spine width reference (cab 2x5)"),
    ("tube_h", "5 in", "in", "Shared spine height reference (cab 2x5; was 6)"),
    ("wall", "0.188 in", "in", "Shared spine wall reference"),
    (
        "rail_bottom",
        "3.5 in",
        "in",
        "Shared — cab/rear bottom at design ride (was stale 8)",
    ),
    (
        "wb_stock",
        "116.5 in",
        "in",
        "TAPED 2026-11-27. Stock WB / stock rear-axle station. Match rear clip",
    ),
    ("wb_73_87_short", "wb_stock", "in", "73-87 shortbed stock WB"),
    ("wb", "wb_stock", "in", "Active STOCK wheelbase — match rear clip"),
    (
        "axle_setback",
        "0.5 in",
        "in",
        "DEFAULT 0.5 (range 0.5–1.0). Tray uses stock frame end",
    ),
    ("core_width", "33.5 in", "in", "TAPED. Core support C-C"),
    (
        "rail_cl",
        "16.0 in",
        "in",
        "Literal. Match rear clip / front 34 in OD (was core_width/2)",
    ),
    ("clip_t", "0.188 in", "in", "Laser plate thickness"),
    ("clip_clear", "0.030 in", "in", "Shared slip-clear name"),
    (
        "kickup_aft",
        "7 in",
        "in",
        "Match rear clip — kick end aft of STOCK rear axle (~123.5)",
    ),
    (
        "rear_overhang",
        "36 in",
        "in",
        "TAPED 2026-11-27. From STOCK rear axle to frame end 152.5",
    ),
    # Air & fuel utility module: 2x4 rails + matching rectangular receivers
    (
        "mod_w",
        "2.000 in",
        "in",
        "Air & fuel utility module rail width — 2x4 rectangle (2 in across car)",
    ),
    (
        "mod_h",
        "4.000 in",
        "in",
        "Air & fuel utility module rail height — 2x4 rectangle (4 in tall)",
    ),
    ("mod_wall", "0.188 in", "in", "PLACEHOLDER. Module rail wall"),
    (
        "mod_slip_clear",
        "0.030 in",
        "in",
        "PLACEHOLDER. Per-side clear vs receiver ID",
    ),
    ("rcv_wall", "0.188 in", "in", "PLACEHOLDER. Match rear clip receiver wall"),
    (
        "rcv_w",
        "mod_w + 2 * mod_slip_clear + 2 * rcv_wall",
        "in",
        "Match rear clip — receiver outer width for 2x4 module",
    ),
    (
        "rcv_h",
        "mod_h + 2 * mod_slip_clear + 2 * rcv_wall",
        "in",
        "Match rear clip — receiver outer height for 2x4 module",
    ),
    (
        "rcv_front_x",
        "wb_stock + kickup_aft",
        "in",
        "Match rear clip — kick end / receiver forward face (~123.5)",
    ),
    (
        "rcv_key_w",
        "1.500 in",
        "in",
        "PLACEHOLDER. Match rear clip — forward lap of key tab onto rail "
        "side plate ahead of rcv_front_x (also key-bay length)",
    ),
    (
        "mod_insert_depth",
        "6.000 in",
        "in",
        "PLACEHOLDER. Match rear clip — module rail insert depth into receiver",
    ),
    (
        "rcv_length",
        "rcv_key_w + clip_t + 0.125 in + mod_insert_depth",
        "in",
        "Match rear clip — key bay + end cap + tip clear + insert depth",
    ),
    (
        "rcv_rear_x",
        "rcv_front_x + rcv_length",
        "in",
        "Match rear clip — receiver aft mouth X",
    ),
    (
        "rcv_cl_y",
        "rail_bottom + mod_h / 2",
        "in",
        "Module/receiver CL — bottom at rail_bottom 3.5 / top 7.5",
    ),
    (
        "rail_end_x",
        "rcv_front_x + rcv_key_w",
        "in",
        "Match rear clip — aft end of plate-box rails / end cap",
    ),
    (
        "clip_rear_x",
        "rcv_rear_x",
        "in",
        "Match rear clip — aft end of clip (= receiver mouths)",
    ),
    ("rcv_bolt_d", "0.500 in", "in", "PLACEHOLDER. Match rear clip cross-bolt dia"),
    ("rcv_bolt_count", "2", "", "PLACEHOLDER. Match rear clip bolt count"),
    ("rcv_bolt_pitch", "3.000 in", "in", "PLACEHOLDER. Match rear clip bolt pitch"),
    (
        "rcv_bolt_first_x",
        "(rcv_rear_x - mod_insert_depth) + "
        "(mod_insert_depth - rcv_bolt_pitch) / 2",
        "in",
        "PLACEHOLDER. Match rear clip — first bolt centered in insert",
    ),
    # Module rail lengths
    (
        "mod_insert_len",
        "mod_insert_depth",
        "in",
        "Insert length into receiver (= mod_insert_depth)",
    ),
    (
        "mod_tray_len",
        "(wb_stock + rear_overhang) - rcv_rear_x",
        "in",
        "Exposed tray to frame end 152.5 (~21.187 at defaults). Was ~20.2 at 153.5",
    ),
    ("mod_rail_len", "mod_insert_len + mod_tray_len", "in", "Total module rail length"),
    (
        "mod_front_x",
        "rcv_rear_x - mod_insert_depth",
        "in",
        "Module rail forward tip = mouth − insert depth (aft of end cap)",
    ),
    ("mod_rear_x", "mod_front_x + mod_rail_len", "in", "Module rail aft tip X"),
    # Tray
    ("tray_t", "clip_t", "in", "PLACEHOLDER. Tray plate thickness"),
    (
        "tray_width",
        "2 * rail_cl - mod_w",
        "in",
        "PLACEHOLDER. Tray width between rail inboard faces",
    ),
    ("tray_length", "mod_tray_len", "in", "PLACEHOLDER. Tray length along X"),
    (
        "tray_x0",
        "rcv_rear_x",
        "in",
        "PLACEHOLDER. Tray forward edge at receiver mouth (rcv_rear_x)",
    ),
    (
        "tray_y",
        "rcv_cl_y - mod_h / 2",
        "in",
        "PLACEHOLDER. Tray top face (on rail top = rail_bottom + mod_h)",
    ),
    ("tray_drop", "0.000 in", "in", "PLACEHOLDER. Extra drop below rail top"),
    ("tab_width", "0.750 in", "in", "PLACEHOLDER. Tray key tab width"),
    ("tab_length", "clip_t", "in", "Tab length = mating thickness"),
    ("slot_clear", "0.010 in", "in", "PLACEHOLDER. Slot oversize vs tab"),
    # Fuel tank envelope (shell PLACEHOLDER; fittings sourced)
    ("fuel_l", "28.000 in", "in", "PLACEHOLDER. Fuel tank length along X"),
    ("fuel_w", "18.000 in", "in", "PLACEHOLDER. Fuel tank width along Z"),
    ("fuel_h", "10.000 in", "in", "PLACEHOLDER. Fuel tank height"),
    ("fuel_wall", "0.125 in", "in", "PLACEHOLDER. Alum tank wall"),
    ("fuel_x", "tray_x0 + 4.000 in", "in", "PLACEHOLDER. Fuel tank forward face X"),
    ("fuel_y", "tray_y + tray_t", "in", "PLACEHOLDER. Fuel tank bottom Y"),
    (
        "fuel_sump_od",
        "2.500 in",
        "in",
        "SOURCED (Boyd Welding 21057). Weld-in sump OD",
    ),
    (
        "fuel_sump_h",
        "0.875 in",
        "in",
        "SOURCED (Boyd 21057). Installed height below tank floor (+/-)",
    ),
    (
        "fuel_sump_hole_d",
        "2.250 in",
        "in",
        "SOURCED (Boyd 21057). Tank hole required. Fitting 1/4 NPT",
    ),
    (
        "fuel_pf_outer_l",
        "11.575 in",
        "in",
        "SOURCED (Nuke Performance 6x10-24bolts.DXF). Weld flange outer obround length along X. Verify vs Radium 20-0278 in hand",
    ),
    (
        "fuel_pf_outer_w",
        "7.598 in",
        "in",
        "SOURCED (Nuke DXF). Weld flange outer obround width along Z. Verify vs 20-0278",
    ),
    (
        "fuel_pf_open_l",
        "10.157 in",
        "in",
        "SOURCED (Nuke DXF). 6x10 opening length along X (ends drawn as splines; modeled as obround)",
    ),
    (
        "fuel_pf_open_w",
        "6.181 in",
        "in",
        "SOURCED (Nuke DXF). 6x10 opening width along Z",
    ),
    (
        "fuel_pf_bolt_r",
        "3.445 in",
        "in",
        "SOURCED (Nuke DXF). Bolt-line end radius (87.5 mm)",
    ),
    (
        "fuel_pf_bolt_ctr",
        "3.976 in",
        "in",
        "SOURCED (Nuke DXF). Distance between bolt-line end-arc centers along X (101 mm)",
    ),
    (
        "fuel_pf_bolt_d",
        "0.315 in",
        "in",
        "SOURCED (Nuke DXF). Bolt hole dia in DXF (8 mm). Radium 20-0278 is tapped 1/4-28 instead",
    ),
    (
        "fuel_pf_bolt_n",
        "24",
        "",
        "SOURCED (Radium). Industry-standard 6x10 24-bolt pattern",
    ),
    (
        "fuel_pf_t",
        "0.240 in",
        "in",
        "SOURCED (Radium 20-0278). Weld flange thickness, fly-cut",
    ),
    (
        "fuel_pf_gasket_t",
        "0.0625 in",
        "in",
        "SOURCED (Radium 18-0015). FKM gasket thickness",
    ),
    (
        "fuel_fcst_min_depth",
        "7.700 in",
        "in",
        "SOURCED (Radium FCST-X). Min depth outer top face to internal floor",
    ),
    (
        "fuel_fcst_max_depth",
        "12.700 in",
        "in",
        "SOURCED (Radium FCST-X). Deeper tanks need Radium extension",
    ),
    (
        "fuel_sender_flange_od",
        "2.800 in",
        "in",
        "SOURCED (Dakota Digital SEN-06-1). Sender flange overall size",
    ),
    (
        "fuel_sender_bc",
        "2.125 in",
        "in",
        "SOURCED (Dakota Digital / Tanks Inc SAE 5-hole). Bolt circle",
    ),
    (
        "fuel_sender_hole_d",
        "1.700 in",
        "in",
        "SOURCED (Dakota Digital). Tank hole size",
    ),
    (
        "fuel_sender_screw_d",
        "0.190 in",
        "in",
        "SOURCED (Dakota Digital). 10-32 screws; hole = tap/nut-ring per build",
    ),
    ("fuel_sender_bolt_n", "5", "", "SOURCED. SAE 5-hole"),
    (
        "fuel_fill_flange_od",
        "3.750 in",
        "in",
        "SOURCED (Usher UD3F). Flat weld flange OD",
    ),
    (
        "fuel_fill_flange_t",
        "0.090 in",
        "in",
        "SOURCED (UD3F). Flange thickness",
    ),
    (
        "fuel_fill_cap_od",
        "2.250 in",
        "in",
        "SOURCED (UD3F). Cap OD",
    ),
    (
        "fuel_fill_h",
        "0.600 in",
        "in",
        "SOURCED (UD3F). Overall height",
    ),
    (
        "fuel_fill_hole_d",
        "2.000 in",
        "in",
        "PLACEHOLDER. Tank cutout for filler neck; not published",
    ),
    (
        "fuel_vent_od",
        "0.875 in",
        "in",
        "SOURCED (Ace Race Parts -6AN ORB). Vent/rollover bung body; rollover valve is -6AN (e.g. Racetronix ROV-6) PLACEHOLDER fit",
    ),
    (
        "fuel_feed_an",
        "1.055 in",
        "in",
        "SOURCED (Ace Race Parts -8AN ORB weld bung, 3/4-16). Body dia",
    ),
    (
        "fuel_return_an",
        "1.055 in",
        "in",
        "SOURCED (Ace Race Parts -8AN ORB weld bung, 3/4-16). Body dia",
    ),
    (
        "fuel_an8_shoulder_d",
        "1.213 in",
        "in",
        "SOURCED (Ace Race Parts -8AN). Shoulder dia",
    ),
    (
        "fuel_an8_h",
        "0.563 in",
        "in",
        "SOURCED (Ace Race Parts -8AN). Bung height",
    ),
    (
        "fuel_an6_body_d",
        "0.875 in",
        "in",
        "SOURCED (Ace Race Parts -6AN ORB, 9/16-18). Body dia",
    ),
    (
        "fuel_an6_shoulder_d",
        "0.984 in",
        "in",
        "SOURCED (Ace Race Parts -6AN). Shoulder dia",
    ),
    (
        "fuel_an6_h",
        "0.500 in",
        "in",
        "SOURCED (Ace Race Parts -6AN). Bung height",
    ),
    (
        "fuel_an8_hole_d",
        "0.875 in",
        "in",
        "PLACEHOLDER. Tank hole for -8 bung pilot; confirm with bung in hand",
    ),
    (
        "fuel_an6_hole_d",
        "0.750 in",
        "in",
        "PLACEHOLDER. Tank hole for -6 bung pilot; confirm with bung in hand",
    ),
    # Air system (air_fuel only)
    ("air_tank_l", "20.000 in", "in", "PLACEHOLDER. Air tank length along X"),
    ("air_tank_od", "6.000 in", "in", "PLACEHOLDER. Air tank OD"),
    ("air_tank_x", "tray_x0 + 4.000 in", "in", "PLACEHOLDER. Air tank forward X"),
    (
        "air_tank_y",
        "tray_y + tray_t + air_tank_od / 2 + 1.000 in",
        "in",
        "PLACEHOLDER. Air tank CL height",
    ),
    ("air_tank_z", "rail_cl * 0.35", "in", "PLACEHOLDER. Air tank CL lateral"),
    ("comp_l", "10.000 in", "in", "PLACEHOLDER. Compressor envelope length"),
    ("comp_w", "6.000 in", "in", "PLACEHOLDER. Compressor envelope width"),
    ("comp_h", "8.000 in", "in", "PLACEHOLDER. Compressor envelope height"),
    ("comp_gap", "2.000 in", "in", "PLACEHOLDER. Gap between twin compressors"),
    ("comp_x", "tray_x0 + 18.000 in", "in", "PLACEHOLDER. Compressor forward X"),
    ("comp_y", "tray_y + tray_t", "in", "PLACEHOLDER. Compressor bottom Y"),
    ("manifold_l", "8.000 in", "in", "PLACEHOLDER. Valve manifold length"),
    ("manifold_w", "4.000 in", "in", "PLACEHOLDER. Valve manifold width"),
    ("manifold_h", "3.000 in", "in", "PLACEHOLDER. Valve manifold height"),
    ("manifold_x", "tray_x0 + 28.000 in", "in", "PLACEHOLDER. Manifold forward X"),
    ("manifold_y", "tray_y + tray_t", "in", "PLACEHOLDER. Manifold bottom Y"),
    # Batteries
    ("batt_l", "13.000 in", "in", "PLACEHOLDER. Battery envelope length"),
    ("batt_w", "7.000 in", "in", "PLACEHOLDER. Battery envelope width"),
    ("batt_h", "8.000 in", "in", "PLACEHOLDER. Battery envelope height"),
    ("batt_gap", "1.500 in", "in", "PLACEHOLDER. Gap between twin batteries"),
    ("batt_x", "tray_x0 + 22.000 in", "in", "PLACEHOLDER. Battery forward X"),
    ("batt_y", "tray_y + tray_t", "in", "PLACEHOLDER. Battery bottom Y"),
    # Bulkhead service plate
    ("bh_t", "clip_t", "in", "PLACEHOLDER. Bulkhead plate thickness"),
    ("bh_w", "tray_width", "in", "PLACEHOLDER. Bulkhead width along Z"),
    ("bh_h", "12.000 in", "in", "PLACEHOLDER. Bulkhead height along Y"),
    ("bh_x", "tray_x0", "in", "PLACEHOLDER. Bulkhead aft face X"),
    ("bh_y", "tray_y", "in", "PLACEHOLDER. Bulkhead bottom Y"),
    ("bh_an_feed_d", "0.750 in", "in", "PLACEHOLDER. AN fuel feed pass-through"),
    ("bh_an_return_d", "0.625 in", "in", "PLACEHOLDER. AN fuel return pass-through"),
    ("bh_air_d", "0.500 in", "in", "PLACEHOLDER. Air line pass-through"),
    ("bh_batt_cable_d", "1.000 in", "in", "PLACEHOLDER. Battery cable pass-through"),
    ("bh_ctrl_d", "1.250 in", "in", "PLACEHOLDER. Control connector pass-through"),
    ("bh_pitch_z", "2.500 in", "in", "PLACEHOLDER. Pass-through lateral pitch"),
    ("bh_row_y", "bh_y + bh_h * 0.55", "in", "PLACEHOLDER. Pass-through row height"),
]

DO = adsk.fusion.DimensionOrientations
IN_TO_CM = 2.54

# Nuke Performance 6x10-24bolts.DXF bolt layout (hard-coded; not user params)
_FUEL_PF_BOLT_ARC_DEG = 20.51
_FUEL_PF_BOLT_SIDE_X = 1.233  # in; 31.32 mm pitch along X on straight sides


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
            root.name = "KTECH_C10_UTILITY_MODULE"
        except Exception:
            pass

        already = False
        for i in range(root.occurrences.count):
            if "01_RAILS" in root.occurrences.item(i).name:
                already = True
                break
        if already:
            ui.messageBox(
                "This document already has the utility module in it.\n\n"
                "File → New Design, then Run the script again."
            )
            return

        mark = add_component(root, "00_ORIGIN")
        mark_origin(mark)

        skel = add_component(root, "00_SKELETON")
        rails = add_component(root, "01_RAILS")
        tray = add_component(root, "02_TRAY")
        fuel = add_component(root, "03_FUEL_TANK")
        air = add_component(root, "04_AIR")
        batts = add_component(root, "05_BATTERY")
        bulk = add_component(root, "06_BULKHEAD")
        add_component(root, "07_FIXTURE")

        draw_layout_sketches(skel)
        build_module_rails(rails)
        build_tray(tray)
        build_fuel_tank(fuel)
        variant = string_param("module_variant", "air_fuel")
        if variant == "air_fuel":
            build_air_system(air)
        else:
            # Leave 04_AIR empty for fuel_only — sketch note only.
            sk = air.sketches.add(air.xYConstructionPlane)
            sk.name = "SK_AIR_OMITTED_FUEL_ONLY"
        build_batteries(batts)
        build_bulkhead(bulk)

        dxf_dir = os.path.join(SCRIPT_DIR, "dxf_out")
        n_dxf = export_plate_dxfs(design, dxf_dir)
        fit_note = _fit_check_note(design)
        fuel_note = _fuel_fcst_depth_note(design)
        notes = fit_note
        if fuel_note:
            notes = "{}\n{}".format(fit_note, fuel_note)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        ui.messageBox(
            "Utility module built in this document.\n\n"
            "Variant: {} (module_variant user/CSV string).\n"
            "Rails: 2x4 (mod_w x mod_h) with mod_wall; rectangular "
            "receivers rcv_w x rcv_h; tube-in-tube + cross-bolt. "
            "Bottom at rail_bottom 3.5 / top 7.5.\n"
            "{}\n"
            "Exported {} plate DXFs to:\n{}\n\n"
            "Fit view if the canvas looks empty.\n"
            "Save as KTECH_C10_UTILITY_MODULE.".format(
                variant,
                notes,
                n_dxf,
                dxf_dir,
            )
        )
    except Exception:
        if ui:
            ui.messageBox(
                "KTECH_C10_UtilityModule failed:\n{}".format(traceback.format_exc())
            )


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def apply_csv_overrides():
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "utility_module_parameters.csv")
    if not os.path.isfile(params_path):
        return
    with open(params_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = (row.get("name") or "").strip()
            expr = (row.get("expression") or "").strip()
            unit = (row.get("unit") or "").strip()
            comment = (row.get("comment") or "").strip()
            if name in STRING_PARAMS:
                STRING_PARAMS[name] = expr if expr else STRING_PARAMS[name]
                continue
            if name not in by_name:
                continue
            unit = unit or "in"
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
    for key, val in STRING_PARAMS.items():
        try:
            design.attributes.add("KTECH_C10_UtilityModule", key, str(val))
        except Exception:
            pass


def param_cm(design, name):
    return design.userParameters.itemByName(name).value


def string_param(name, default=""):
    return STRING_PARAMS.get(name, default)


def _int_param(design, name, default=1):
    try:
        return max(int(round(design.userParameters.itemByName(name).value)), 1)
    except Exception:
        return default


def _fit_check_note(design):
    """Receiver ID vs module OD + 2*slip — soft check printed at run."""
    try:
        wall = param_cm(design, "rcv_wall")
        clear = param_cm(design, "mod_slip_clear")
        try:
            rcv_w = param_cm(design, "rcv_w")
            rcv_h = param_cm(design, "rcv_h")
            mod_w = param_cm(design, "mod_w")
            mod_h = param_cm(design, "mod_h")
        except Exception:
            rcv_w = rcv_h = param_cm(design, "rcv_od")
            mod_w = mod_h = param_cm(design, "mod_od")
        gap_w = (rcv_w - 2.0 * wall - mod_w - 2.0 * clear) / IN_TO_CM
        gap_h = (rcv_h - 2.0 * wall - mod_h - 2.0 * clear) / IN_TO_CM
        ok_w = "OK" if gap_w >= -0.001 else "TIGHT/INTERFERENCE"
        ok_h = "OK" if gap_h >= -0.001 else "TIGHT/INTERFERENCE"
        lines = [
            "Tube-in-tube fit W (rcv ID − mod − 2*clear): {:.3f} in — {}.".format(
                gap_w, ok_w
            ),
            "Tube-in-tube fit H (rcv ID − mod − 2*clear): {:.3f} in — {}.".format(
                gap_h, ok_h
            ),
        ]
        # Packaging stations vs rear clip.
        rcv_front = param_cm(design, "rcv_front_x") / IN_TO_CM
        rail_end = param_cm(design, "rail_end_x") / IN_TO_CM
        clip_t = param_cm(design, "clip_t") / IN_TO_CM
        cap_aft = rail_end + clip_t
        rcv_rear = param_cm(design, "rcv_rear_x") / IN_TO_CM
        mod_front = param_cm(design, "mod_front_x") / IN_TO_CM
        mod_rear = param_cm(design, "mod_rear_x") / IN_TO_CM
        tray_x0 = param_cm(design, "tray_x0") / IN_TO_CM
        insert = param_cm(design, "mod_insert_depth") / IN_TO_CM
        bolt0 = param_cm(design, "rcv_bolt_first_x") / IN_TO_CM
        bolt_d = param_cm(design, "rcv_bolt_d") / IN_TO_CM
        pitch = param_cm(design, "rcv_bolt_pitch") / IN_TO_CM
        n = _int_param(design, "rcv_bolt_count", 2)
        try:
            wb_frame = param_cm(design, "wb_stock")
        except Exception:
            wb_frame = param_cm(design, "wb")
        body_end = (wb_frame + param_cm(design, "rear_overhang")) / IN_TO_CM
        expect_front = rcv_rear - insert
        bolt1 = bolt0
        bolt2 = bolt0 + pitch if n > 1 else bolt0
        lines.append(
            "Stations (in): rcv_front={:.3f} rail_end={:.3f} cap_aft={:.3f} "
            "mod_front={:.3f} (expect {:.3f}) insert={:.3f} "
            "bolt1={:.3f} bolt2={:.3f} rcv_rear={:.3f} tray_x0={:.3f} "
            "mod_rear={:.3f} (wb_stock+rear_overhang={:.3f}).".format(
                rcv_front,
                rail_end,
                cap_aft,
                mod_front,
                expect_front,
                insert,
                bolt1,
                bolt2,
                rcv_rear,
                tray_x0,
                mod_rear,
                body_end,
            )
        )
        if abs(mod_front - expect_front) > 0.01:
            lines.append(
                "WARN: mod_front_x is not rcv_rear_x − mod_insert_depth "
                "({:.3f} vs {:.3f}).".format(mod_front, expect_front)
            )
        if mod_front < cap_aft + 0.001:
            lines.append(
                "WARN: module tip at/forward of end-cap aft face "
                "(mod_front={:.3f}, cap_aft={:.3f}).".format(mod_front, cap_aft)
            )
        if mod_front < rcv_front - 0.01:
            lines.append("WARN: mod_front_x forward of rcv_front_x.")
        if tray_x0 + 0.01 < rcv_rear:
            lines.append("WARN: tray/bulkhead forward of receiver mouth (rcv_rear_x).")
        for i in range(n):
            bx = bolt0 + i * pitch
            if bx < mod_front - 0.01 or bx > rcv_rear + 0.01:
                lines.append(
                    "WARN: bolt {} at X={:.3f} outside insert "
                    "[{:.3f}, {:.3f}].".format(i + 1, bx, mod_front, rcv_rear)
                )
            edge0 = bx - bolt_d / 2.0
            edge1 = bx + bolt_d / 2.0
            if edge0 < mod_front - 0.01 or edge1 > rcv_rear + 0.01:
                lines.append(
                    "WARN: bolt {} hole edges [{:.3f},{:.3f}] do not clear "
                    "insert ends.".format(i + 1, edge0, edge1)
                )
            if edge0 < cap_aft - 0.01:
                lines.append(
                    "WARN: bolt {} hole edge overlaps end cap "
                    "(edge={:.3f}, cap_aft={:.3f}).".format(i + 1, edge0, cap_aft)
                )
        if abs(mod_rear - body_end) > 6.0:
            lines.append(
                "NOTE: mod_rear_x is >6 in from wb_stock+rear_overhang — "
                "adjust mod_tray_len PLACEHOLDER if packaging to body end."
            )
        return "\n".join(lines)
    except Exception:
        return "Tube-in-tube fit check unavailable."


def _fuel_fcst_depth_note(design):
    """Warn if tank height is outside Radium FCST-X depth range."""
    try:
        h = param_cm(design, "fuel_h") / IN_TO_CM
        mn = param_cm(design, "fuel_fcst_min_depth") / IN_TO_CM
        mx = param_cm(design, "fuel_fcst_max_depth") / IN_TO_CM
        if h < mn or h > mx:
            return (
                "Fuel tank height {:.3f} in is outside FCST-X depth "
                "{:.3f}-{:.3f} in.".format(h, mn, mx)
            )
        return ""
    except Exception:
        return ""


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
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    s = 3.0 * IN_TO_CM
    p0 = adsk.core.Point3D.create(-s, -s, 0)
    p1 = adsk.core.Point3D.create(s, -s, 0)
    p2 = adsk.core.Point3D.create(s, s, 0)
    p3 = adsk.core.Point3D.create(-s, s, 0)
    lines.addByTwoPoints(p0, p1)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p0)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(s))
    ext = extrudes.add(ext_in)
    ext.name = "EX_ORIGIN_CUBE"
    ext.bodies.item(0).name = "ORIGIN_MARKER"
    try:
        ext.bodies.item(0).opacity = 0.25
    except Exception:
        pass


def draw_layout_sketches(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_SIDE"
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    x0 = param_cm(design, "mod_front_x")
    x1 = param_cm(design, "mod_rear_x")
    y = param_cm(design, "rcv_cl_y")
    lines.addByTwoPoints(
        sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y, 0)),
        sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y, 0)),
    )
    sk.isComputeDeferred = False

    sk2 = comp.sketches.add(comp.xZConstructionPlane)
    sk2.name = "SK_TOP"
    sk2.isComputeDeferred = True
    lines2 = sk2.sketchCurves.sketchLines
    cl = param_cm(design, "rail_cl")
    y0 = param_cm(design, "tray_y")
    lines2.addByTwoPoints(
        sk2.modelToSketchSpace(adsk.core.Point3D.create(x0, y0, cl)),
        sk2.modelToSketchSpace(adsk.core.Point3D.create(x1, y0, cl)),
    )
    lines2.addByTwoPoints(
        sk2.modelToSketchSpace(adsk.core.Point3D.create(x0, y0, -cl)),
        sk2.modelToSketchSpace(adsk.core.Point3D.create(x1, y0, -cl)),
    )
    sk2.isComputeDeferred = False


# ---------------------------------------------------------------------------
# Module rails (tube-in-tube into rear-clip receivers)
# ---------------------------------------------------------------------------

def build_module_rails(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    for passenger in (True, False):
        _build_one_module_rail(comp, design, passenger=passenger)
        _cut_module_bolt_holes(comp, design, passenger=passenger)


def _mod_wh_cm(design):
    """Module rail outer width (Z) and height (Y) in cm."""
    try:
        return param_cm(design, "mod_w"), param_cm(design, "mod_h")
    except Exception:
        od = param_cm(design, "mod_od")
        return od, od


def _build_one_module_rail(comp, design, passenger=True):
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    x0 = param_cm(design, "mod_front_x")
    length = param_cm(design, "mod_rail_len")
    mw, mh = _mod_wh_cm(design)
    wall = param_cm(design, "mod_wall")
    cy = param_cm(design, "rcv_cl_y")
    cz = param_cm(design, "rail_cl") * sign

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x0))
    pl = planes.add(pin)
    pl.name = "PL_MOD_RAIL_{}".format(side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_MOD_RAIL_{}".format(side)
    sk.isComputeDeferred = True
    half_h = mh / 2.0
    half_w = mw / 2.0
    oc = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy, cz))
    or_ = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x0, cy + half_h, cz + half_w)
    )
    ir_ = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x0, cy + half_h - wall, cz + half_w - wall)
    )
    sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, or_)
    if half_h - wall > 0.05 and half_w - wall > 0.05:
        sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, ir_)
    sk.isComputeDeferred = False

    ring = _find_ring_profile(sk)
    if not ring:
        if sk.profiles.count < 1:
            return None
        ring = _largest_profile(sk)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(length))
    ext = extrudes.add(ext_in)
    ext.name = "EX_MOD_RAIL_{}".format(side)
    body = ext.bodies.item(0)
    body.name = "MOD_RAIL_{}".format(side)
    return body


def _cut_module_bolt_holes(comp, design, passenger=True):
    """Matching cross-bolt holes through module rails (align with receiver bolts)."""
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    mw, _mh = _mod_wh_cm(design)
    cy = param_cm(design, "rcv_cl_y")
    cz = param_cm(design, "rail_cl") * sign
    d = param_cm(design, "rcv_bolt_d")
    pitch = param_cm(design, "rcv_bolt_pitch")
    x_first = param_cm(design, "rcv_bolt_first_x")
    n = _int_param(design, "rcv_bolt_count", 2)
    z_face = cz + sign * (mw / 2.0)

    for i in range(n):
        xc = x_first + i * pitch
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
        pl = planes.add(pin)
        pl.name = "PL_MOD_BOLT_{}_{}".format(side, i + 1)

        sk = comp.sketches.add(pl)
        sk.name = "SK_MOD_BOLT_{}_{}".format(side, i + 1)
        ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, cy, z_face))
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, d / 2.0)
        if sk.profiles.count < 1:
            continue
        prof = sk.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
        reverse = sign > 0
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(mw + 0.1))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_MOD_BOLT_{}_{}".format(side, i + 1)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Keyed laser tray
# ---------------------------------------------------------------------------

def build_tray(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    x0 = param_cm(design, "tray_x0")
    length = param_cm(design, "tray_length")
    width = param_cm(design, "tray_width")
    y = param_cm(design, "tray_y") - param_cm(design, "tray_drop")
    t = param_cm(design, "tray_t")
    z0 = -width / 2.0
    z1 = width / 2.0
    x1 = x0 + length

    body = _extrude_xz_plate(comp, "TRAY_FLOOR", x0, x1, y, z0, z1, t, up=True)
    if body:
        _cut_tray_key_slots(comp, design, body)
    _build_tray_keys(comp, design)


def _cut_tray_key_slots(comp, design, _body):
    """Slot cuts near LH/RH edges for rail key tabs."""
    x0 = param_cm(design, "tray_x0")
    length = param_cm(design, "tray_length")
    y = param_cm(design, "tray_y") - param_cm(design, "tray_drop")
    t = param_cm(design, "tray_t")
    tw = param_cm(design, "tab_width")
    sc = param_cm(design, "slot_clear")
    cl = param_cm(design, "rail_cl")
    mw, _mh = _mod_wh_cm(design)
    # Three tabs along each long edge.
    n_tabs = 3
    pitch = length / (n_tabs + 1)
    for side_sign, label in ((1.0, "RH"), (-1.0, "LH")):
        z_edge = side_sign * (cl - mw / 2.0)
        for i in range(n_tabs):
            xc = x0 + (i + 1) * pitch
            planes = comp.constructionPlanes
            pin = planes.createInput()
            pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
            pl = planes.add(pin)
            pl.name = "PL_TRAY_SLOT_{}_{}".format(label, i + 1)
            sk = comp.sketches.add(pl)
            sk.name = "SK_TRAY_SLOT_{}_{}".format(label, i + 1)
            sk.isComputeDeferred = True
            hx = tw / 2.0 + sc
            hz = t / 2.0 + sc
            # Slot along edge, thin in Z.
            p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, y, z_edge - hz))
            p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, y, z_edge + hz))
            p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, y, z_edge + hz))
            p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, y, z_edge - hz))
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
            ext_in = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(t + 0.05))
            try:
                ext = extrudes.add(ext_in)
                ext.name = "EX_TRAY_SLOT_{}_{}".format(label, i + 1)
            except Exception:
                pass


def _build_tray_keys(comp, design):
    """Key tabs that seat into tray slots / weld to module rails (DXF)."""
    x0 = param_cm(design, "tray_x0")
    length = param_cm(design, "tray_length")
    y = param_cm(design, "tray_y") - param_cm(design, "tray_drop")
    t = param_cm(design, "tray_t")
    tw = param_cm(design, "tab_width")
    tl = param_cm(design, "tab_length")
    cl = param_cm(design, "rail_cl")
    mw, _mh = _mod_wh_cm(design)
    n_tabs = 3
    pitch = length / (n_tabs + 1)
    # One representative key plate per side (union of tab strip) for DXF.
    for side_sign, side in ((1.0, "RH"), (-1.0, "LH")):
        z0 = side_sign * (cl - mw / 2.0) - tl / 2.0
        z1 = side_sign * (cl - mw / 2.0) + tl / 2.0
        # Single strip covering all tab stations for a clean DXF body.
        name = "TRAY_KEY_{}".format(side)
        _extrude_xz_plate(
            comp,
            name,
            x0 + pitch - tw / 2.0,
            x0 + n_tabs * pitch + tw / 2.0,
            y,
            min(z0, z1),
            max(z0, z1),
            t,
            up=True,
        )


# ---------------------------------------------------------------------------
# Fuel tank envelope
# ---------------------------------------------------------------------------

def build_fuel_tank(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    x0 = param_cm(design, "fuel_x")
    l = param_cm(design, "fuel_l")
    w = param_cm(design, "fuel_w")
    h = param_cm(design, "fuel_h")
    y0 = param_cm(design, "fuel_y")
    z0 = -w / 2.0
    z1 = w / 2.0

    # Main tank box.
    _extrude_xz_plate(comp, "FUEL_TANK_BOX", x0, x0 + l, y0, z0, z1, h, up=True)

    # Boyd 21057 weld-in sump under 6x10 flange center.
    top_y = y0 + h
    cx = x0 + l * 0.35
    _add_vertical_cylinder(
        comp,
        "FUEL_SUMP",
        cx,
        y0,
        0.0,
        param_cm(design, "fuel_sump_od") / 2.0,
        param_cm(design, "fuel_sump_h"),
        up=False,
    )

    # Radium 20-0278 / Nuke 6x10 24-bolt weld flange (obround envelope).
    _add_obround_xz(
        comp,
        "FUEL_PUMP_FLANGE",
        cx,
        top_y,
        0.0,
        param_cm(design, "fuel_pf_outer_l"),
        param_cm(design, "fuel_pf_outer_w"),
        param_cm(design, "fuel_pf_t"),
        up=True,
    )
    _add_6x10_flange_sketch(comp, design, cx, top_y)

    # Usher UD3F filler — shift aft if flange would overlap 6x10 at defaults.
    fill_frac = 0.70
    fill_x = x0 + l * fill_frac
    pf_aft = cx + param_cm(design, "fuel_pf_outer_l") / 2.0
    fill_fwd = fill_x - param_cm(design, "fuel_fill_flange_od") / 2.0
    if fill_fwd < pf_aft:
        fill_frac = 0.80
        fill_x = x0 + l * fill_frac
    fill_z = w * 0.25
    flange_t = param_cm(design, "fuel_fill_flange_t")
    cap_h = param_cm(design, "fuel_fill_h") - flange_t
    _add_vertical_cylinder(
        comp,
        "FUEL_FILL_FLANGE",
        fill_x,
        top_y,
        fill_z,
        param_cm(design, "fuel_fill_flange_od") / 2.0,
        flange_t,
        up=True,
    )
    if cap_h > 0.0:
        _add_vertical_cylinder(
            comp,
            "FUEL_FILL_CAP",
            fill_x,
            top_y + flange_t,
            fill_z,
            param_cm(design, "fuel_fill_cap_od") / 2.0,
            cap_h,
            up=True,
        )

    _add_vertical_cylinder(
        comp,
        "FUEL_VENT",
        x0 + l * 0.85,
        top_y,
        -w * 0.25,
        param_cm(design, "fuel_vent_od") / 2.0,
        param_cm(design, "fuel_an6_h"),
        up=True,
    )

    sender_x = x0 + l * 0.55
    sender_z = -w * 0.30
    _add_vertical_cylinder(
        comp,
        "FUEL_SENDER",
        sender_x,
        top_y,
        sender_z,
        param_cm(design, "fuel_sender_flange_od") / 2.0,
        param_cm(design, "tray_t"),
        up=True,
    )
    _add_sender_cut_sketch(comp, design, sender_x, top_y, sender_z)

    # Feed / return -8AN ORB bungs on forward face (YZ).
    an8_h = param_cm(design, "fuel_an8_h")
    _add_bung_on_yz(
        comp,
        "FUEL_FEED_BUNG",
        x0,
        y0 + h * 0.35,
        w * 0.20,
        param_cm(design, "fuel_feed_an") / 2.0,
        an8_h,
    )
    _add_bung_on_yz(
        comp,
        "FUEL_RETURN_BUNG",
        x0,
        y0 + h * 0.55,
        -w * 0.20,
        param_cm(design, "fuel_return_an") / 2.0,
        an8_h,
    )
    # -6AN drain bung on aft face, low on centerline, protruding aft (+X).
    _add_bung_on_yz(
        comp,
        "FUEL_DRAIN_BUNG",
        x0 + l,
        y0 + param_cm(design, "fuel_an6_body_d"),
        0.0,
        param_cm(design, "fuel_an6_body_d") / 2.0,
        param_cm(design, "fuel_an6_h"),
        aft=True,
    )

    # Simple mount plates under tank (DXF).
    mw = 3.0 * IN_TO_CM
    ml = 4.0 * IN_TO_CM
    my = y0
    for sign, side in ((1.0, "RH"), (-1.0, "LH")):
        zc = sign * (w / 2.0 - mw / 2.0)
        _extrude_xz_plate(
            comp,
            "MOUNT_FUEL_{}".format(side),
            x0 + l * 0.2,
            x0 + l * 0.2 + ml,
            my,
            zc - mw / 2.0,
            zc + mw / 2.0,
            param_cm(design, "tray_t"),
            up=False,
        )


def _add_6x10_flange_sketch(comp, design, cx, top_y):
    """Sketch-only 6x10 opening + 24-bolt pattern (laser/DXF cutout ref).

    Always draws the DXF 24-hole layout (even if fuel_pf_bolt_n != 24).
    """
    _ = _int_param(design, "fuel_pf_bolt_n", 24)  # kept user-editable; layout fixed
    open_l = param_cm(design, "fuel_pf_open_l")
    open_w = param_cm(design, "fuel_pf_open_w")
    bolt_r = param_cm(design, "fuel_pf_bolt_r")
    bolt_ctr = param_cm(design, "fuel_pf_bolt_ctr")
    bolt_d = param_cm(design, "fuel_pf_bolt_d")
    side_x = _FUEL_PF_BOLT_SIDE_X * IN_TO_CM

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(top_y))
    pl = planes.add(pin)
    pl.name = "PL_FUEL_PUMP_6X10"
    sk = comp.sketches.add(pl)
    sk.name = "SK_FUEL_PUMP_6X10"
    sk.isComputeDeferred = True

    _sketch_obround_xz(sk, cx, top_y, 0.0, open_l, open_w)

    # End-arc hole angles from outward X (Nuke DXF): 0, +/-20.51, ... +/-82.04
    arc_mults = (0, 1, -1, 2, -2, 3, -3, 4, -4)
    for side in (1.0, -1.0):
        acx = cx + side * (bolt_ctr / 2.0)
        for m in arc_mults:
            ang = math.radians(_FUEL_PF_BOLT_ARC_DEG * m)
            # Outward X: +side; angle measured from that direction in XZ
            zx = acx + side * bolt_r * math.cos(ang)
            zz = 0.0 + bolt_r * math.sin(ang)
            ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(zx, top_y, zz))
            sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, bolt_d / 2.0)

    # Straight-side holes at z = +/- bolt_r, x = -1.233, 0, +1.233 relative to center
    for z_sign in (1.0, -1.0):
        for dx in (-side_x, 0.0, side_x):
            ctr = sk.modelToSketchSpace(
                adsk.core.Point3D.create(cx + dx, top_y, z_sign * bolt_r)
            )
            sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, bolt_d / 2.0)

    sk.isComputeDeferred = False


def _add_sender_cut_sketch(comp, design, cx, top_y, cz):
    """Sketch-only SAE 5-bolt sender tank cutout + screw holes."""
    hole_d = param_cm(design, "fuel_sender_hole_d")
    screw_d = param_cm(design, "fuel_sender_screw_d")
    bc = param_cm(design, "fuel_sender_bc") / 2.0
    n = _int_param(design, "fuel_sender_bolt_n", 5)

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(top_y))
    pl = planes.add(pin)
    pl.name = "PL_FUEL_SENDER_CUT"
    sk = comp.sketches.add(pl)
    sk.name = "SK_FUEL_SENDER_CUT"
    sk.isComputeDeferred = True
    ctr0 = sk.modelToSketchSpace(adsk.core.Point3D.create(cx, top_y, cz))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr0, hole_d / 2.0)
    # PLACEHOLDER angles: SAE 5-hole pattern is NOT evenly spaced (two holes wider apart); verify against sender gasket
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        zx = cx + bc * math.cos(ang)
        zz = cz + bc * math.sin(ang)
        ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(zx, top_y, zz))
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, screw_d / 2.0)
    sk.isComputeDeferred = False


def _sketch_obround_xz(sk, cx, y, cz, length, width):
    """Closed obround (stadium) in an XZ sketch: length along X, width along Z."""
    half_w = width / 2.0
    span = length - width
    if span <= 1.0e-6:
        ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(cx, y, cz))
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, max(half_w, 1.0e-4))
        return
    lc = cx - span / 2.0
    rc = cx + span / 2.0
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    p_tl = sk.modelToSketchSpace(adsk.core.Point3D.create(lc, y, cz + half_w))
    p_tr = sk.modelToSketchSpace(adsk.core.Point3D.create(rc, y, cz + half_w))
    p_bl = sk.modelToSketchSpace(adsk.core.Point3D.create(lc, y, cz - half_w))
    p_br = sk.modelToSketchSpace(adsk.core.Point3D.create(rc, y, cz - half_w))
    lines.addByTwoPoints(p_tl, p_tr)
    lines.addByTwoPoints(p_bl, p_br)
    mid_r = sk.modelToSketchSpace(adsk.core.Point3D.create(rc + half_w, y, cz))
    mid_l = sk.modelToSketchSpace(adsk.core.Point3D.create(lc - half_w, y, cz))
    arcs.addByThreePoints(p_tr, mid_r, p_br)
    arcs.addByThreePoints(p_bl, mid_l, p_tl)


def _add_obround_xz(comp, name, cx, y0, cz, length, width, height, up=True):
    """Extrude an obround envelope on an XZ plane."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y0))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    _sketch_obround_xz(sk, cx, y0, cz, length, width)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return None
    prof = _largest_profile(sk)
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByReal(height))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    ext.bodies.item(0).name = name
    return ext.bodies.item(0)


# ---------------------------------------------------------------------------
# Air system (air_fuel variant)
# ---------------------------------------------------------------------------

def build_air_system(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    # Air tank — cylinder along X.
    x0 = param_cm(design, "air_tank_x")
    l = param_cm(design, "air_tank_l")
    r = param_cm(design, "air_tank_od") / 2.0
    cy = param_cm(design, "air_tank_y")
    cz = param_cm(design, "air_tank_z")
    _extrude_circle_x(comp, "AIR_TANK", x0, cy, cz, r, l)

    _extrude_xz_plate(
        comp,
        "MOUNT_AIR",
        x0 + l * 0.3,
        x0 + l * 0.3 + 4.0 * IN_TO_CM,
        param_cm(design, "tray_y") + param_cm(design, "tray_t"),
        cz - 2.0 * IN_TO_CM,
        cz + 2.0 * IN_TO_CM,
        param_cm(design, "tray_t"),
        up=True,
    )

    # Twin compressors.
    clen = param_cm(design, "comp_l")
    cw = param_cm(design, "comp_w")
    ch = param_cm(design, "comp_h")
    gap = param_cm(design, "comp_gap")
    cx0 = param_cm(design, "comp_x")
    cy0 = param_cm(design, "comp_y")
    span = cw + gap / 2.0
    for sign, side in ((1.0, "RH"), (-1.0, "LH")):
        zc = sign * span
        _extrude_xz_plate(
            comp,
            "COMPRESSOR_{}".format(side),
            cx0,
            cx0 + clen,
            cy0,
            zc - cw / 2.0,
            zc + cw / 2.0,
            ch,
            up=True,
        )
        _extrude_xz_plate(
            comp,
            "MOUNT_COMP_{}".format(side),
            cx0,
            cx0 + clen,
            cy0,
            zc - cw / 2.0,
            zc + cw / 2.0,
            param_cm(design, "tray_t"),
            up=False,
        )

    # Valve manifold.
    ml = param_cm(design, "manifold_l")
    mw = param_cm(design, "manifold_w")
    mh = param_cm(design, "manifold_h")
    mx = param_cm(design, "manifold_x")
    my = param_cm(design, "manifold_y")
    _extrude_xz_plate(
        comp, "VALVE_MANIFOLD", mx, mx + ml, my, -mw / 2.0, mw / 2.0, mh, up=True
    )
    _extrude_xz_plate(
        comp,
        "MOUNT_MANIFOLD",
        mx,
        mx + ml,
        my,
        -mw / 2.0,
        mw / 2.0,
        param_cm(design, "tray_t"),
        up=False,
    )


# ---------------------------------------------------------------------------
# Batteries
# ---------------------------------------------------------------------------

def build_batteries(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    bl = param_cm(design, "batt_l")
    bw = param_cm(design, "batt_w")
    bh = param_cm(design, "batt_h")
    gap = param_cm(design, "batt_gap")
    bx = param_cm(design, "batt_x")
    by = param_cm(design, "batt_y")
    span = bw + gap / 2.0
    for sign, side in ((1.0, "RH"), (-1.0, "LH")):
        zc = sign * span
        _extrude_xz_plate(
            comp,
            "BATTERY_{}".format(side),
            bx,
            bx + bl,
            by,
            zc - bw / 2.0,
            zc + bw / 2.0,
            bh,
            up=True,
        )
        _extrude_xz_plate(
            comp,
            "MOUNT_BATT_{}".format(side),
            bx,
            bx + bl,
            by,
            zc - bw / 2.0,
            zc + bw / 2.0,
            param_cm(design, "tray_t"),
            up=False,
        )


# ---------------------------------------------------------------------------
# Bulkhead service plate
# ---------------------------------------------------------------------------

def build_bulkhead(comp):
    design = adsk.fusion.Design.cast(comp.parentDesign)
    x = param_cm(design, "bh_x")
    t = param_cm(design, "bh_t")
    w = param_cm(design, "bh_w")
    h = param_cm(design, "bh_h")
    y0 = param_cm(design, "bh_y")
    # Plate on YZ at bh_x, extruded aft (+X) by bh_t.
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x - t))
    pl = planes.add(pin)
    pl.name = "PL_BULKHEAD"

    sk = comp.sketches.add(pl)
    sk.name = "SK_BULKHEAD"
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    z0 = -w / 2.0
    z1 = w / 2.0
    xf = x - t
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xf, y0, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xf, y0 + h, z0))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xf, y0 + h, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xf, y0, z1))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)

    # Pass-through holes in the same sketch (cut with plate).
    row_y = param_cm(design, "bh_row_y")
    pitch = param_cm(design, "bh_pitch_z")
    holes = [
        ("FEED", param_cm(design, "bh_an_feed_d"), -2.0 * pitch),
        ("RETURN", param_cm(design, "bh_an_return_d"), -1.0 * pitch),
        ("AIR", param_cm(design, "bh_air_d"), 0.0),
        ("BATT", param_cm(design, "bh_batt_cable_d"), 1.0 * pitch),
        ("CTRL", param_cm(design, "bh_ctrl_d"), 2.0 * pitch),
    ]
    # fuel_only still gets air hole as spare / future; variant does not remove holes.
    for _label, dia, z_off in holes:
        ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xf, row_y, z_off))
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, dia / 2.0)
    sk.isComputeDeferred = False

    # Outer profile = largest; holes are inner loops of the plate profile.
    if sk.profiles.count < 1:
        return
    # Prefer a profile with holes (multiple loops).
    prof = None
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        if p.profileLoops.count >= 2:
            prof = p
            break
    if not prof:
        prof = _largest_profile(sk)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(t))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return
    ext.name = "EX_BULKHEAD_SERVICE"
    ext.bodies.item(0).name = "BULKHEAD_SERVICE"


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

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


def _find_ring_profile(sk):
    for i in range(sk.profiles.count):
        prof = sk.profiles.item(i)
        if prof.profileLoops.count == 2:
            return prof
    return None


# NOTE: up=False is a symmetric extrude (isSymmetric flag); kept as-is for existing bodies
def _extrude_xz_plate(comp, name, x0, x1, y, z0, z1, thickness, up):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
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
    ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByReal(thickness))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


def _add_vertical_cylinder(comp, name, cx, y0, cz, radius, height, up=True):
    """Vertical cylinder envelope. up=True: +Y (PositiveExtent); up=False: -Y (NegativeExtent)."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y0))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(cx, y0, cz))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, radius)
    if sk.profiles.count < 1:
        return None
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    direction = (
        adsk.fusion.ExtentDirections.PositiveExtentDirection
        if up
        else adsk.fusion.ExtentDirections.NegativeExtentDirection
    )
    ext_in.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(height)),
        direction,
    )
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    ext.bodies.item(0).name = name
    return ext.bodies.item(0)


def _add_bung_on_yz(comp, name, x_face, cy, cz, radius, length, aft=False):
    """ORB bung on a YZ tank face. aft=True: +X (PositiveExtent); aft=False: -X forward (NegativeExtent)."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, radius)
    if sk.profiles.count < 1:
        return None
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    # aft=True: +X; aft=False (default): forward -X via NegativeExtentDirection
    direction = (
        adsk.fusion.ExtentDirections.PositiveExtentDirection
        if aft
        else adsk.fusion.ExtentDirections.NegativeExtentDirection
    )
    ext_in.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(length)),
        direction,
    )
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    ext.bodies.item(0).name = name
    return ext.bodies.item(0)


def _extrude_circle_x(comp, name, x0, cy, cz, radius, length):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x0))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy, cz))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, radius)
    if sk.profiles.count < 1:
        return None
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(
        sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(length))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    ext.bodies.item(0).name = name
    return ext.bodies.item(0)


# ---------------------------------------------------------------------------
# DXF export (same pattern as rear clip)
# ---------------------------------------------------------------------------

def export_plate_dxfs(design, out_dir):
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
