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
#   for 67-72. REV-B layout: outboard lower 4-link bars; rear_link_type selects
#   triangulated (inboard uppers) or parallel_watts (parallel uppers + Watts
#   lateral). Inboard bag/shock on axle tubes; keyed over-axle XM with bag OR
#   coilover (suspension_mode). Rails / kickup / OA XM / receivers stay identical
#   across link variants so the same UtilityModule plugs into either.
#   Aft of kickup the rails step back down and END at rail_end_x (short key
#   bay past rcv_front_x). An end-cap plate welds onto the box aft face at
#   rail_end_x (extrudes aft by clip_t) with a square cutout for the
#   receiver OD. Square RECEIVER tubes pass through the cap; RCV_KEY tabs
#   seat on the receiver OD faces and lap the rail side-plate outer faces
#   forward of the key-bay window (rcv_od > box_od_w — weld/shim gap, no
#   interior tube-in-box). Receivers continue aft to rcv_rear_x
#   (= clip_rear_x); open mouths are the aft-most clip feature. Cross-bolts
#   lock the slide-in utility module (see KTECH_C10_UtilityModule).
#   rear_overhang remains a body/module envelope reference and no longer
#   drives rail length.
#
# Coordinates (Fusion Y-up) — same as KTECH_C10_Chassis_Setup
#   Origin = front axle × ground × frame centerline
#   +X = rear   +Y = up   +Z = passenger (right)
#   Layout params lower_link_y / bag_y / shock_y are LATERAL (|Z| from frame CL).

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
    "RAIL_RH_TOP_TAIL",
    "RAIL_RH_BOT_FWD",
    "RAIL_RH_BOT_AFT",
    "RAIL_RH_BOT_TAIL",
    "RAIL_RH_END_CAP",
    "RAIL_RH_OUTBOARD",
    "RAIL_RH_INBOARD",
    "RAIL_LH_TOP_FWD",
    "RAIL_LH_TOP_AFT",
    "RAIL_LH_TOP_TAIL",
    "RAIL_LH_BOT_FWD",
    "RAIL_LH_BOT_AFT",
    "RAIL_LH_BOT_TAIL",
    "RAIL_LH_END_CAP",
    "RAIL_LH_OUTBOARD",
    "RAIL_LH_INBOARD",
    "XMEMBER_UPPER",
    "XMEMBER_OA_TOP",
    "XMEMBER_OA_WEB_FWD",
    "XMEMBER_OA_WEB_AFT",
    "XMEMBER_OA_BOT",
    "BRACKET_LOWER_RH",
    "BRACKET_LOWER_LH",
    "BRACKET_UPPER_RH",
    "BRACKET_UPPER_LH",
    "AXLE_TAB_LOWER_RH",
    "AXLE_TAB_LOWER_LH",
    "AXLE_TAB_UPPER_RH",
    "AXLE_TAB_UPPER_LH",
    "SHOCK_TAB_UPPER_RH_A",
    "SHOCK_TAB_UPPER_RH_B",
    "SHOCK_TAB_UPPER_LH_A",
    "SHOCK_TAB_UPPER_LH_B",
    "SHOCK_TAB_LOWER_RH_A",
    "SHOCK_TAB_LOWER_RH_B",
    "SHOCK_TAB_LOWER_LH_A",
    "SHOCK_TAB_LOWER_LH_B",
    "MOUNT_BAG_UPPER_RH",
    "MOUNT_BAG_UPPER_LH",
    "MOUNT_BAG_LOWER_RH",
    "MOUNT_BAG_LOWER_LH",
    "XMEMBER_RCV",
    "RCV_KEY_RH_IN",
    "RCV_KEY_RH_OUT",
    "RCV_KEY_LH_IN",
    "RCV_KEY_LH_OUT",
    "BRACKET_WATTS_RH",
    "BRACKET_WATTS_LH",
    "WATTS_CRANK",
    "WATTS_PIVOT_MOUNT",
)

# String / enum params (Fusion user params are numeric; these live in CSV + attributes).
STRING_PARAMS = {
    "rear_link_type": "triangulated",
    "lateral_locator": "none",
    "rod_end_shank_thread": "3/4-16",
}

PARAM_ORDER = [
    # Shared spine / tape names (match KTECH_C10_Chassis_Setup)
    ("tube_w", "2 in", "in", "A500 width across the car"),
    ("tube_h", "6 in", "in", "A500 height"),
    ("wall", "0.188 in", "in", "A500 wall"),
    ("rail_bottom", "8 in", "in", "Bottom of tube off ground"),
    ("wb_73_87_short", "117.5 in", "in", "73-87 shortbed WB — first prototype"),
    ("wb_67_72_short", "115.0 in", "in", "67-72 shortbed WB — switch wb to this"),
    ("wb", "wb_73_87_short", "in", "Active wheelbase"),
    (
        "rear_overhang",
        "42 in",
        "in",
        "PLACEHOLDER. Body/module envelope aft of axle — NOT rail length",
    ),
    ("core_width", "33.5 in", "in", "TAPED. Core support C-C"),
    ("rail_cl", "core_width / 2", "in", "2x6 CL from vehicle CL"),
    ("core_x", "-33 in", "in", "PLACEHOLDER. Core vs front axle"),
    ("core_to_mid", "55 in", "in", "TAPED. Core to mid along rail"),
    ("mid_to_rear", "43 in", "in", "TAPED. Mid to cab-rear along rail"),
    ("cab_f_x", "core_x + core_to_mid", "in", "Computed"),
    ("cab_r_x", "cab_f_x + mid_to_rear", "in", "Computed"),
    # Rear clip / slip-fit (clip_rear_x defined after rcv_* / rail_end_x)
    ("splice_aft", "3 in", "in", "PLACEHOLDER. Split aft of cab_r"),
    ("slip_overlap", "8 in", "in", "Slip-fit overlap of plate box on tube"),
    ("clip_t", "0.188 in", "in", "Laser plate thickness"),
    ("clip_clear", "0.030 in", "in", "Per-side slip clearance"),
    ("center_tube_end_x", "cab_r_x + splice_aft", "in", "Aft end of purchased 2x6"),
    ("clip_front_x", "center_tube_end_x - slip_overlap", "in", "Forward end of plate box"),
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
    # 4-link — REV-B lowers outboard; uppers inboard (triangulated) or parallel
    ("lower_link_len", "23 in", "in", "PLACEHOLDER. Target lower C-C (actual from pickups)"),
    ("upper_link_len", "22 in", "in", "PLACEHOLDER. Target upper C-C (actual from pickups)"),
    ("lower_pickup_x", "cab_r_x + 2 in", "in", "PLACEHOLDER. Frame lower pickup X"),
    ("upper_pickup_x", "cab_r_x + 6 in", "in", "PLACEHOLDER. Frame upper pickup X"),
    ("lower_pickup_y", "rail_bottom + 1 in", "in", "PLACEHOLDER. Lower pickup height (Fusion Y)"),
    ("upper_pickup_y", "rail_bottom + tube_h - 1 in", "in", "PLACEHOLDER. Upper pickup height (Fusion Y)"),
    # lower_link_y / bag_y / shock_y = lateral |Z| from frame CL (not Fusion Y-up)
    (
        "lower_link_y",
        "rail_cl + tube_w / 2 + clip_clear + clip_t + 0.75 in",
        "in",
        "PLACEHOLDER. Lower bar lateral from CL — outboard of rail outboard face",
    ),
    ("axle_link_spread_z", "lower_link_y", "in", "Legacy alias → lower_link_y (outboard lowers)"),
    ("frame_link_spread_z", "lower_link_y", "in", "Frame lower pickups at lower_link_y (outboard)"),
    (
        "frame_upper_spread_z",
        "rail_cl * 0.5",
        "in",
        "PLACEHOLDER. Frame upper half-spread — triangulated inboard (ignored when parallel_watts)",
    ),
    ("link_bar_od", "1.25 in", "in", "Four-link bar tube OD"),
    ("link_bar_wall", "0.120 in", "in", "PLACEHOLDER. Four-link bar tube wall"),
    ("rod_end_shank_od", "0.750 in", "in", "PLACEHOLDER. Shank major dia (3/4-16)"),
    ("rod_end_housing_od", "1.750 in", "in", "PLACEHOLDER. Bushing housing OD"),
    ("rod_end_housing_width", "0.875 in", "in", "PLACEHOLDER. Bushing housing width"),
    ("rod_end_bore", "0.625 in", "in", "PLACEHOLDER. Rod-end bolt bore"),
    ("rod_end_eye_to_shoulder", "2.125 in", "in", "PLACEHOLDER. Eye center to shoulder"),
    (
        "rod_end_thread_engagement_min",
        "1.000 in",
        "in",
        "PLACEHOLDER. Min thread engagement into bung",
    ),
    (
        "rod_end_adjustable_length",
        "1.500 in",
        "in",
        "PLACEHOLDER. Spin-to-adjust range each end",
    ),
    ("bung_length", "1.500 in", "in", "PLACEHOLDER. Threaded tube insert length"),
    ("bung_od", "link_bar_od - 2 * link_bar_wall", "in", "Bung OD ≈ tube ID"),
    ("jam_nut_od", "1.125 in", "in", "PLACEHOLDER. Jam nut OD"),
    ("jam_nut_width", "0.375 in", "in", "PLACEHOLDER. Jam nut width"),
    ("axle_bracket_w", "4.000 in", "in", "PLACEHOLDER. Axle link tab width along X"),
    ("axle_bracket_h", "3.000 in", "in", "PLACEHOLDER. Axle link tab height along Y"),
    ("axle_bracket_t", "clip_t", "in", "Axle link tab plate thickness"),
    ("upper_xmember_w", "2.000 in", "in", "PLACEHOLDER. Frame upper 4-link xmember width along X"),
    ("upper_xmember_h", "4.000 in", "in", "PLACEHOLDER. Frame upper 4-link xmember height"),
    ("bracket_plate_w", "4.000 in", "in", "PLACEHOLDER. Link bracket width"),
    ("bracket_plate_h", "3.500 in", "in", "PLACEHOLDER. Link bracket height"),
    ("bracket_hole_d", "0.625 in", "in", "PLACEHOLDER. Link bolt hole dia"),
    # Suspension mode: 1 = airbag, 0 = coilover (evaluated at run)
    ("suspension_mode", "1", "", "1=airbag on over-axle XM, 0=coilover/shock tabs"),
    # Over-axle crossmember (kickup rails, above axle CL)
    ("ox_plate_t", "0.188 in", "in", "PLACEHOLDER. Over-axle XM laser plate thickness"),
    ("ox_width_x", "6.000 in", "in", "PLACEHOLDER. Over-axle XM fore-aft width"),
    ("ox_web_h", "3.000 in", "in", "PLACEHOLDER. Over-axle XM front/rear web height"),
    ("ox_include_bottom", "1", "", "1=include bottom plate, 0=open channel"),
    # Shared bag / coilover mount positions (REV-B: inboard of rails)
    (
        "bag_diameter",
        "8.000 in",
        "in",
        "PLACEHOLDER. Airbag OD for clearance checks (not solid-modeled)",
    ),
    (
        "bag_y",
        "(rail_cl - box_od_w / 2 + frame_upper_spread_z) / 2",
        "in",
        "PLACEHOLDER. Bag center lateral — between rail inboard face and upper link",
    ),
    (
        "shock_y",
        "bag_y",
        "in",
        "PLACEHOLDER. Shock/coilover lateral — same inboard bay as bag by default",
    ),
    ("mount_z_off", "bag_y", "in", "Legacy alias → bag_y (shared mount lateral)"),
    ("mount_x_off", "0.000 in", "in", "PLACEHOLDER. Mount fore/aft offset from axle CL"),
    (
        "shock_eye_y",
        "rail_bottom + tube_h + kickup_rise - 1 in",
        "in",
        "PLACEHOLDER. Upper shock/coilover eye height (Fusion Y)",
    ),
    ("shock_bore", "0.500 in", "in", "PLACEHOLDER. Shock/coilover bolt bore"),
    ("shock_tab_w", "2.500 in", "in", "PLACEHOLDER. Shock tab width along X"),
    ("shock_tab_h", "3.500 in", "in", "PLACEHOLDER. Shock tab height along Y"),
    ("shock_tab_gap", "1.000 in", "in", "PLACEHOLDER. Double-shear clear between tabs"),
    ("bag_mount_w", "6.000 in", "in", "PLACEHOLDER. Bag mount plate width along X"),
    ("bag_mount_l", "6.000 in", "in", "PLACEHOLDER. Bag mount plate length along Z"),
    ("bag_stud_d", "0.375 in", "in", "PLACEHOLDER. Single 3/8 bag stud hole dia"),
    ("bag_stud_offset", "1.500 in", "in", "PLACEHOLDER. Stud offset from plate center along X"),
    ("bag_air_hole_d", "0.750 in", "in", "PLACEHOLDER. Center air-fitting hole dia"),
    (
        "axle_travel_up",
        "3.000 in",
        "in",
        "PLACEHOLDER. Axle bump travel up for clearance checks",
    ),
    (
        "axle_travel_down",
        "5.000 in",
        "in",
        "PLACEHOLDER. Axle droop travel down for bar-to-rail clearance",
    ),
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
    ("axle_lower_pickup_x", "wb", "in", "PLACEHOLDER. Axle lower pickup X"),
    ("axle_lower_pickup_y", "axle_cl_y - 1 in", "in", "PLACEHOLDER. Axle lower pickup height"),
    (
        "axle_lower_spread_z",
        "lower_link_y",
        "in",
        "PLACEHOLDER. Axle lower lateral — outboard of rails near housing tubes",
    ),
    ("axle_upper_pickup_x", "wb", "in", "PLACEHOLDER. Axle upper pickup X"),
    ("axle_upper_pickup_y", "axle_cl_y + 2 in", "in", "PLACEHOLDER. Axle upper pickup height"),
    (
        "axle_upper_spread_z",
        "cs_width / 2 + 1.5 in",
        "in",
        "PLACEHOLDER. Axle upper half-spread — triangulated (ignored when parallel_watts)",
    ),
    ("mount_y", "rail_bottom + tube_h", "in", "Top of straight tube / slip section"),
    # Watts link (used when rear_link_type = parallel_watts) — all PLACEHOLDER
    (
        "watts_pivot_x",
        "wb + cs_depth / 2",
        "in",
        "PLACEHOLDER. Watts pivot X — aft face of housing center section",
    ),
    (
        "watts_pivot_y",
        "axle_cl_y",
        "in",
        "PLACEHOLDER. Watts center pivot height at ride (Fusion Y)",
    ),
    (
        "watts_crank_len",
        "6.000 in",
        "in",
        "PLACEHOLDER. Bell crank tip-to-pivot (half-arm length)",
    ),
    (
        "watts_crank_arm_w",
        "1.500 in",
        "in",
        "PLACEHOLDER. Bell crank arm width",
    ),
    (
        "watts_crank_t",
        "clip_t",
        "in",
        "PLACEHOLDER. Bell crank plate thickness along X",
    ),
    (
        "watts_link_len",
        "12.000 in",
        "in",
        "PLACEHOLDER. Target Watts lateral link C-C (actual from pickups)",
    ),
    (
        "watts_link_od",
        "0.750 in",
        "in",
        "PLACEHOLDER. Watts lateral link tube OD",
    ),
    (
        "watts_link_wall",
        "0.120 in",
        "in",
        "PLACEHOLDER. Watts lateral link tube wall",
    ),
    (
        "watts_bolt_d",
        "0.500 in",
        "in",
        "PLACEHOLDER. Watts link / frame bracket bolt diameter",
    ),
    (
        "watts_pivot_bolt_d",
        "0.625 in",
        "in",
        "PLACEHOLDER. Watts center pivot bolt diameter",
    ),
    (
        "watts_bracket_w",
        "3.000 in",
        "in",
        "PLACEHOLDER. Frame Watts bracket width along X",
    ),
    (
        "watts_bracket_h",
        "3.000 in",
        "in",
        "PLACEHOLDER. Frame Watts bracket height along Y",
    ),
    (
        "watts_frame_x",
        "watts_pivot_x",
        "in",
        "PLACEHOLDER. Frame Watts bracket station X (horizontal links)",
    ),
    (
        "watts_frame_y",
        "watts_pivot_y",
        "in",
        "PLACEHOLDER. Frame Watts pickup height (Fusion Y)",
    ),
    (
        "watts_pivot_mount_w",
        "4.000 in",
        "in",
        "PLACEHOLDER. Axle Watts pivot mount plate width along Z",
    ),
    (
        "watts_pivot_mount_h",
        "4.000 in",
        "in",
        "PLACEHOLDER. Axle Watts pivot mount plate height along Y",
    ),
    # Aft receivers (slide-in utility module — tube-in-tube)
    (
        "rcv_od",
        "2.500 in",
        "in",
        "PLACEHOLDER. Receiver square tube outer size (OD)",
    ),
    (
        "rcv_wall",
        "0.188 in",
        "in",
        "PLACEHOLDER. Receiver square tube wall",
    ),
    (
        "rcv_length",
        "14.000 in",
        "in",
        "PLACEHOLDER. Receiver tube length along X (aft of kickup step-down)",
    ),
    (
        "rcv_front_x",
        "wb + kickup_aft",
        "in",
        "PLACEHOLDER. Receiver forward face X (start of step-down aft bay)",
    ),
    (
        "rcv_rear_x",
        "rcv_front_x + rcv_length",
        "in",
        "Receiver aft face X (open mouth — aft-most clip feature)",
    ),
    (
        "rcv_cl_y",
        "rail_bottom + tube_h / 2",
        "in",
        "PLACEHOLDER. Receiver CL height (Fusion Y) after kickup step-down",
    ),
    (
        "rcv_key_w",
        "1.500 in",
        "in",
        "PLACEHOLDER. Forward lap of key tab onto rail side plate ahead of "
        "rcv_front_x (also sets key-bay length via rail_end_x)",
    ),
    (
        "rcv_key_h",
        "rcv_od",
        "in",
        "PLACEHOLDER. Receiver key tab height (matches tube OD)",
    ),
    (
        "rcv_weld_clear",
        "0.030 in",
        "in",
        "PLACEHOLDER. Extra cutout clear around rcv_od at rail end cap",
    ),
    (
        "rail_end_x",
        "rcv_front_x + rcv_key_w",
        "in",
        "Aft end of plate-box rails (key bay); receivers continue aft",
    ),
    (
        "clip_rear_x",
        "rcv_rear_x",
        "in",
        "Aft end of rear clip (= receiver mouths)",
    ),
    (
        "rcv_bolt_d",
        "0.500 in",
        "in",
        "PLACEHOLDER. Cross-bolt hole diameter through receiver (locks slide-in module)",
    ),
    (
        "rcv_bolt_count",
        "2",
        "",
        "PLACEHOLDER. Number of cross-bolts per receiver",
    ),
    (
        "rcv_bolt_pitch",
        "3.000 in",
        "in",
        "PLACEHOLDER. Cross-bolt spacing along X",
    ),
    (
        "rcv_bolt_first_x",
        "rail_end_x + clip_t + 0.750 in",
        "in",
        "PLACEHOLDER. First cross-bolt X — aft of end-cap aft face "
        "(rail_end_x + clip_t)",
    ),
    (
        "rcv_xm_w",
        "2.000 in",
        "in",
        "PLACEHOLDER. Rear receiver XM fore-aft envelope (layout ref; thickness is rcv_xm_t)",
    ),
    (
        "rcv_xm_h",
        "rcv_od",
        "in",
        "PLACEHOLDER. Rear receiver crossmember plate height",
    ),
    (
        "rcv_xm_t",
        "clip_t",
        "in",
        "PLACEHOLDER. Rear receiver crossmember plate thickness along X",
    ),
    (
        "rcv_xm_x",
        "rail_end_x + (rcv_rear_x - rail_end_x) / 2",
        "in",
        "PLACEHOLDER. Rear receiver crossmember center X (mid of free tube)",
    ),
    # Utility-module fuel tank envelope mirrors (clearance only — after rcv_*)
    (
        "um_fuel_l",
        "28.000 in",
        "in",
        "PLACEHOLDER. Match UtilityModule fuel_l — Watts clearance",
    ),
    (
        "um_fuel_w",
        "18.000 in",
        "in",
        "PLACEHOLDER. Match UtilityModule fuel_w — Watts clearance",
    ),
    (
        "um_fuel_h",
        "10.000 in",
        "in",
        "PLACEHOLDER. Match UtilityModule fuel_h — Watts clearance",
    ),
    (
        "um_fuel_x",
        "rcv_rear_x + 4.000 in",
        "in",
        "PLACEHOLDER. Match UtilityModule fuel_x — Watts clearance",
    ),
    (
        "um_fuel_y",
        "rcv_cl_y - 1.000 in + clip_t",
        "in",
        "PLACEHOLDER. Match UtilityModule fuel_y approx (tray top + tray_t)",
    ),
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
        receivers = add_component(root, "08_RECEIVERS")
        add_component(root, "07_FIXTURE")

        draw_layout_sketches(skel)
        build_center_tube_ref(center)
        build_rail_side(rail_rh, passenger=True)
        build_rail_side(rail_lh, passenger=False)
        link_type = rear_link_type_value()
        build_upper_crossmember(xmembers)
        build_four_link_brackets(links)
        build_axle_ref(axle)
        build_axle_link_brackets(axle)
        cut_rows = build_four_link_bars(links)
        maybe_build_lateral_locator(links)
        build_over_axle_crossmember(xmembers)
        build_suspension_mounts(mounts, axle)
        build_receivers(receivers, rail_rh, rail_lh, xmembers)

        cut_path = os.path.join(SCRIPT_DIR, "four_link_bar_cut_list.csv")
        write_bar_cut_list(cut_path, cut_rows)

        dxf_dir = os.path.join(SCRIPT_DIR, "dxf_out")
        n_dxf = export_plate_dxfs(design, dxf_dir)
        gap_in, gap_note = bump_clearance_report(design)
        clear_txt = layout_clearance_report(design)
        pack_txt = receiver_packaging_report(design)
        ifx_txt = try_receiver_interference_check(design)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        mode = suspension_mode_value(design)
        mode_txt = "airbag" if mode >= 0.5 else "coilover"
        if link_type == "parallel_watts":
            link_txt = (
                "parallel_watts — uppers parallel to lowers in plan; Watts lateral "
                "on axle CS aft face"
            )
            lat_txt = "watts (implied by parallel_watts)"
        else:
            link_txt = "triangulated — uppers inboard toward third member"
            lat = string_param("lateral_locator", "none").strip().lower()
            if lat == "panhard":
                lat_txt = "panhard (TODO — not modeled)"
            elif lat == "watts":
                lat_txt = "watts (use rear_link_type=parallel_watts)"
            else:
                lat_txt = "none (triangulated uppers provide lateral)"
        ui.messageBox(
            "Rear clip built in this document.\n\n"
            "Prototype WB = wb_73_87_short (117.5). For 67-72 set wb = wb_67_72_short.\n"
            "rear_link_type: {}\n"
            "REV-B: lowers outboard (lower_link_y); bag/shock inboard "
            "(bag_y / shock_y). Rails/kickup/OA XM/receivers identical for both "
            "link variants.\n"
            "Suspension mount mode: {} (suspension_mode user param).\n"
            "Four-link bars: {} (1.25 tube + RH/LH rod ends; cut list written).\n"
            "Over-axle XM bump clearance (underside vs housing/CS): {:.3f} in — {}.\n"
            "{}\n"
            "{}\n"
            "{}\n"
            "Aft receivers: rails end at rail_end_x; end cap welded aft; "
            "open mouths at rcv_rear_x (= clip_rear_x); RCV_KEY on receiver "
            "OD lapping rail side plates; cross-bolts aft of end cap for "
            "slide-in utility module.\n"
            "Lateral locator: {}.\n"
            "Exported {} plate DXFs to:\n{}\n"
            "Bar cut list:\n{}\n\n"
            "Fit view if the canvas looks empty. Rails sit at rail_cl off CL.\n"
            "Save as KTECH_C10_REAR_CLIP.".format(
                link_txt,
                mode_txt,
                len(cut_rows),
                gap_in,
                gap_note,
                clear_txt,
                pack_txt,
                ifx_txt,
                lat_txt,
                n_dxf,
                dxf_dir,
                cut_path,
            )
        )
    except Exception:
        if ui:
            ui.messageBox("KTECH_C10_RearClip failed:\n{}".format(traceback.format_exc()))


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

def apply_csv_overrides():
    """Load rear_clip_parameters.csv into PARAM_ORDER expressions + STRING_PARAMS."""
    by_name = {row[0]: row for row in PARAM_ORDER}
    params_path = os.path.join(SCRIPT_DIR, "rear_clip_parameters.csv")
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
    # Persist string enums on the design (Fusion user params are numeric).
    for key, val in STRING_PARAMS.items():
        try:
            design.attributes.add("KTECH_C10_RearClip", key, str(val))
        except Exception:
            pass


def param_cm(design, name):
    return design.userParameters.itemByName(name).value


def suspension_mode_value(design):
    try:
        return design.userParameters.itemByName("suspension_mode").value
    except Exception:
        return 1.0


def string_param(name, default=""):
    return STRING_PARAMS.get(name, default)


def rear_link_type_value():
    """triangulated (default) | parallel_watts."""
    raw = string_param("rear_link_type", "triangulated").strip().lower()
    if raw in ("parallel_watts", "parallel", "watts", "parallel-watts"):
        return "parallel_watts"
    return "triangulated"


def is_parallel_watts():
    return rear_link_type_value() == "parallel_watts"


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
    # Plate-box rails end at rail_end_x (receivers continue to clip_rear_x).
    xr = param_cm(design, "rail_end_x")
    wb = param_cm(design, "wb")
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
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

    # REV-B: rise over axle, plateau, then step back down aft of kickup
    # into a short key bay ending at rail_end_x (receivers aft of that).
    if top:
        return [
            (xf, y_top),
            (x_k0, y_top),
            (x_k1, y_top_hi),
            (x_k2, y_top_hi),
            (x_k3, y_top),
            (xr, y_top),
        ]
    return [
        (xf, y_bot),
        (x_k0, y_bot),
        (x_k1, y_bot_hi),
        (x_k2, y_bot_hi),
        (x_k3, y_bot),
        (xr, y_bot),
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

    # Key slots in outboard plate for lower-link brackets (REV-B outboard lowers).
    # Parallel-watts also keys upper brackets into the same outboard plate.
    _add_bracket_key_slots(comp, design, side, sign)

    # Key slots in inboard plate so rails fixture the over-axle crossmember.
    _add_over_axle_key_slots(comp, design, side, sign)

    # Watts frame brackets key into inboard plates (parallel_watts only).
    if is_parallel_watts():
        _add_watts_key_slots(comp, design, side, sign)

    # Clearance tunnel through plate box in the key bay so rcv_od can pass
    # without intersecting rail plates (keys lap outside — see receivers).
    _cut_receiver_rail_clearance(comp, design, side, sign)


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
    """Flat top/bottom plates: forward, raised kickup plateau, and aft step-down."""
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
    th = param_cm(design, "tube_h")
    t = param_cm(design, "clip_t")
    rise = param_cm(design, "kickup_rise")
    xf = param_cm(design, "clip_front_x")
    xr = param_cm(design, "rail_end_x")
    wb = param_cm(design, "wb")
    ahead = param_cm(design, "kickup_ahead")
    aft = param_cm(design, "kickup_aft")
    ramp = param_cm(design, "kickup_ramp")

    x_k0 = wb - ahead
    x_k1 = x_k0 + ramp
    x_k2 = wb + aft - ramp
    x_k3 = wb + aft
    # Forward ends at kickup start; raised plateau between ramps; aft after step-down
    # ends at rail_end_x (not clip_rear_x — receivers own the overhang).
    x_fwd_end = x_k0
    x_plat_start = x_k1
    x_plat_end = x_k2
    x_aft_start = x_k3

    y_bot_outer = rb - clear - t
    y_top_outer = rb + th + clear
    y_bot_hi = y_bot_outer + rise
    y_top_hi = y_top_outer + rise

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
    # Raised kickup plateau (between rise and step-down ramps).
    if x_plat_start < x_plat_end - 0.1 * IN_TO_CM:
        _extrude_rect_plate(
            comp,
            "TOP_AFT",
            side,
            x0=x_plat_start,
            x1=x_plat_end,
            y=y_top_hi,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=True,
        )
        _extrude_rect_plate(
            comp,
            "BOT_AFT",
            side,
            x0=x_plat_start,
            x1=x_plat_end,
            y=y_bot_hi + t,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=False,
        )
    # Step-down key bay (rails end at rail_end_x; OD keys + aft-welded end cap).
    if x_aft_start < xr - 0.1 * IN_TO_CM:
        _extrude_rect_plate(
            comp,
            "TOP_TAIL",
            side,
            x0=x_aft_start,
            x1=xr,
            y=y_top_outer,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=True,
        )
        _extrude_rect_plate(
            comp,
            "BOT_TAIL",
            side,
            x0=x_aft_start,
            x1=xr,
            y=y_bot_outer + t,
            z0=z0,
            z1=z1,
            thickness_expr="clip_t",
            up=False,
        )

    # Rail-end cap plate with square cutout for receiver OD (+ weld clear).
    _build_rail_end_cap(comp, design, side, sign, z_in_outer, z_out_outer)


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
    """Key slots in the outboard plate for link brackets.

    Always keys lowers (REV-B outboard). Keys uppers only for parallel_watts
    (triangulated uppers sit inboard — no outboard rail keys).
    """
    bw = param_cm(design, "bracket_plate_w")
    bh = param_cm(design, "bracket_plate_h")
    sc = param_cm(design, "slot_clear")
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    z_out_inner = cl + sign * (tw / 2.0 + clear)

    pockets = [
        ("KEY_LOWER", param_cm(design, "lower_pickup_x"), param_cm(design, "lower_pickup_y")),
    ]
    if is_parallel_watts():
        pockets.append(
            (
                "KEY_UPPER",
                param_cm(design, "upper_pickup_x"),
                param_cm(design, "upper_pickup_y"),
            )
        )

    for label, xc, yc in pockets:
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(
            comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_out_inner)
        )
        pl = planes.add(pin)
        pl.name = "PL_{}_{}".format(side, label)

        sk = comp.sketches.add(pl)
        sk.name = "SK_{}_{}".format(side, label)
        sk.isComputeDeferred = True
        hx = bw / 2.0 + sc
        hy = bh / 2.0 + sc
        p00 = sk.modelToSketchSpace(
            adsk.core.Point3D.create(xc - hx, yc - hy, z_out_inner)
        )
        p01 = sk.modelToSketchSpace(
            adsk.core.Point3D.create(xc - hx, yc + hy, z_out_inner)
        )
        p11 = sk.modelToSketchSpace(
            adsk.core.Point3D.create(xc + hx, yc + hy, z_out_inner)
        )
        p10 = sk.modelToSketchSpace(
            adsk.core.Point3D.create(xc + hx, yc - hy, z_out_inner)
        )
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
        reverse = sign > 0
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}_{}".format(side, label)
        except Exception:
            pass


def _add_watts_key_slots(comp, design, side, sign):
    """Key pockets in the inboard plate for Watts frame brackets."""
    xc = param_cm(design, "watts_frame_x")
    yc = param_cm(design, "watts_frame_y")
    bw = param_cm(design, "watts_bracket_w")
    bh = param_cm(design, "watts_bracket_h")
    sc = param_cm(design, "slot_clear")
    z_in = _rail_inboard_inner_z(design, sign)
    label = "KEY_WATTS"

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_in))
    pl = planes.add(pin)
    pl.name = "PL_{}_{}".format(side, label)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}_{}".format(side, label)
    sk.isComputeDeferred = True
    hx = bw / 2.0 + sc
    hy = bh / 2.0 + sc
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc - hy, z_in))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc + hy, z_in))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc + hy, z_in))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc - hy, z_in))
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
    reverse = sign > 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    try:
        ext = extrudes.add(ext_in)
        ext.name = "EX_{}_{}".format(side, label)
    except Exception:
        pass


def _add_over_axle_key_slots(comp, design, side, sign):
    """Rectangular key pockets in the inboard plate for over-axle XM ends."""
    wb = param_cm(design, "wb")
    ox_w = param_cm(design, "ox_width_x")
    ox_t = param_cm(design, "ox_plate_t")
    ox_h = param_cm(design, "ox_web_h")
    sc = param_cm(design, "slot_clear")
    y_top = _over_axle_top_y(design)
    z_in = _rail_inboard_inner_z(design, sign)
    include_bot = _ox_include_bottom(design)

    # Pockets cut from inboard inner face into plate thickness (clip_t).
    # Web pockets centered on the web plate thickness (extruded inboard from outer face).
    pockets = [
        ("OA_TOP", wb, y_top + ox_t / 2.0, ox_w, ox_t),
        ("OA_WEB_FWD", wb - ox_w / 2.0 + ox_t / 2.0, y_top - ox_h / 2.0, ox_t, ox_h),
        ("OA_WEB_AFT", wb + ox_w / 2.0 - ox_t / 2.0, y_top - ox_h / 2.0, ox_t, ox_h),
    ]
    if include_bot:
        pockets.append(("OA_BOT", wb, y_top - ox_h - ox_t / 2.0, ox_w, ox_t))

    for label, xc, yc, span_x, span_y in pockets:
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_in))
        pl = planes.add(pin)
        pl.name = "PL_{}_{}".format(side, label)

        sk = comp.sketches.add(pl)
        sk.name = "SK_{}_{}".format(side, label)
        sk.isComputeDeferred = True
        hx = span_x / 2.0 + sc
        hy = span_y / 2.0 + sc
        p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc - hy, z_in))
        p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc + hy, z_in))
        p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc + hy, z_in))
        p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc - hy, z_in))
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
        # Inboard plate extruded toward CL from z_in; cut into the plate (RH −Z, LH +Z).
        reverse = sign > 0
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}_{}".format(side, label)
        except Exception:
            pass


def _rail_inboard_inner_z(design, sign):
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    return cl - sign * (tw / 2.0 + clear)


def _rail_outboard_inner_z(design, sign):
    cl = param_cm(design, "rail_cl") * sign
    tw = param_cm(design, "tube_w")
    clear = param_cm(design, "clip_clear")
    return cl + sign * (tw / 2.0 + clear)


def _rcv_weld_clear_cm(design):
    try:
        return param_cm(design, "rcv_weld_clear")
    except Exception:
        return 0.030 * IN_TO_CM


def _cut_receiver_rail_clearance(comp, design, side, sign):
    """Cut rcv_od (+ weld clear) side-plate windows in the key bay.

    rcv_od exceeds slip_id_w / box_od_w, so without this cut the receiver
    would intersect the side plates over [rcv_front_x, rail_end_x]. Top and
    bottom plates are cut only when the receiver Y span actually reaches
    that plate's inner face (defaults: receiver sits inside the 6 in box).
    RCV_KEY tabs seat on the receiver OD and lap the side-plate outer
    faces forward of the window.
    """
    x0 = param_cm(design, "rcv_front_x")
    x1 = param_cm(design, "rail_end_x")
    if x1 <= x0 + 0.05 * IN_TO_CM:
        return
    cy = param_cm(design, "rcv_cl_y")
    od = param_cm(design, "rcv_od")
    clear = _rcv_weld_clear_cm(design)
    half = od / 2.0 + clear
    cz = param_cm(design, "rail_cl") * sign
    z_in = _rail_inboard_inner_z(design, sign)
    z_out = _rail_outboard_inner_z(design, sign)
    t = param_cm(design, "clip_t")
    # Side-plate cuts (sketch on XY at each inner face).
    for role, z_face, reverse_cut in (
        ("RCV_CLR_IN", z_in, sign > 0),
        ("RCV_CLR_OUT", z_out, sign < 0),
    ):
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
        pl = planes.add(pin)
        pl.name = "PL_{}_{}".format(side, role)
        sk = comp.sketches.add(pl)
        sk.name = "SK_{}_{}".format(side, role)
        sk.isComputeDeferred = True
        p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy - half, z_face))
        p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy + half, z_face))
        p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, cy + half, z_face))
        p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, cy - half, z_face))
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
        ext_in.setDistanceExtent(reverse_cut, adsk.core.ValueInput.createByString("clip_t"))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}_{}".format(side, role)
        except Exception:
            pass

    # Top / bottom plate cuts only if receiver Y span reaches that inner face.
    rb = param_cm(design, "rail_bottom")
    clip_clear = param_cm(design, "clip_clear")
    th = param_cm(design, "tube_h")
    y_top_inner = rb + th + clip_clear
    y_bot_inner = rb - clip_clear
    rcv_y0 = cy - half
    rcv_y1 = cy + half
    z0 = min(cz - half, cz + half)
    z1 = max(cz - half, cz + half)
    # Expand Z cut to full box width so top/bottom fully clear the tunnel.
    z_box0 = min(z_in - sign * t, z_out + sign * t)
    z_box1 = max(z_in - sign * t, z_out + sign * t)
    z0 = min(z0, z_box0)
    z1 = max(z1, z_box1)

    cuts = []
    if rcv_y1 >= y_top_inner - 1e-6:
        cuts.append(("RCV_CLR_TOP", y_top_inner, True))
    if rcv_y0 <= y_bot_inner + 1e-6:
        # Sketch on bottom-plate inner face; cut −Y into the plate thickness.
        cuts.append(("RCV_CLR_BOT", y_bot_inner, False))

    for role, y_face, up in cuts:
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y_face))
        pl = planes.add(pin)
        pl.name = "PL_{}_{}".format(side, role)
        sk = comp.sketches.add(pl)
        sk.name = "SK_{}_{}".format(side, role)
        sk.isComputeDeferred = True
        p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y_face, z0))
        p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, y_face, z1))
        p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y_face, z1))
        p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x1, y_face, z0))
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
        # XZ normal +Y; top plate cut upward into plate, bottom downward.
        ext_in.setDistanceExtent(not up, adsk.core.ValueInput.createByString("clip_t"))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}_{}".format(side, role)
        except Exception:
            pass


def _build_rail_end_cap(comp, design, side, sign, z_in_outer, z_out_outer):
    """YZ end plate welded onto the box aft face at rail_end_x.

    Extrudes aft (+X) by clip_t so the cap occupies
    [rail_end_x, rail_end_x + clip_t] with no overlap into the side / tail
    plates. Outer rect = box outer (grown to surround the receiver cutout);
    cutout = rcv_od + 2*rcv_weld_clear.
    """
    x_face = param_cm(design, "rail_end_x")
    t = param_cm(design, "clip_t")
    rb = param_cm(design, "rail_bottom")
    clear = param_cm(design, "clip_clear")
    th = param_cm(design, "tube_h")
    cy = param_cm(design, "rcv_cl_y")
    cz = param_cm(design, "rail_cl") * sign
    od = param_cm(design, "rcv_od")
    weld = _rcv_weld_clear_cm(design)
    half_cut = od / 2.0 + weld

    y0 = rb - clear - t
    y1 = rb + th + clear + t
    z0 = min(z_in_outer, z_out_outer)
    z1 = max(z_in_outer, z_out_outer)
    # Grow the cap to fully surround the receiver cutout if OD > box OD.
    z0 = min(z0, cz - half_cut - t)
    z1 = max(z1, cz + half_cut + t)
    y0 = min(y0, cy - half_cut - t)
    y1 = max(y1, cy + half_cut + t)

    name = "RAIL_{}_END_CAP".format(side)
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    # Outer rectangle (YZ sketch: x→Z, y→Y).
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y0, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y1, z0))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y1, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y0, z1))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    # Inner square cutout centered on receiver.
    oc = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz))
    or_ = sk.modelToSketchSpace(
        adsk.core.Point3D.create(x_face, cy + half_cut, cz + half_cut)
    )
    sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, or_)
    sk.isComputeDeferred = False

    ring = _find_ring_profile(sk)
    if not ring:
        if sk.profiles.count < 1:
            return None
        ring = _largest_profile(sk)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # YZ normal +X; extrude aft so the cap welds onto the box end face.
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByString("clip_t"))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


def _over_axle_top_y(design):
    """Inner top of kickup rail (underside of raised top plate / XM top seat)."""
    rb = param_cm(design, "rail_bottom")
    th = param_cm(design, "tube_h")
    clear = param_cm(design, "clip_clear")
    rise = param_cm(design, "kickup_rise")
    return rb + th + clear + rise


def _ox_include_bottom(design):
    try:
        return design.userParameters.itemByName("ox_include_bottom").value >= 0.5
    except Exception:
        return True


def _over_axle_underside_y(design):
    """Lowest face of over-axle crossmember (bottom plate underside or web bottom)."""
    y_top = _over_axle_top_y(design)
    ox_h = param_cm(design, "ox_web_h")
    ox_t = param_cm(design, "ox_plate_t")
    if _ox_include_bottom(design):
        return y_top - ox_h - ox_t
    return y_top - ox_h


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

    # Frame upper 4-link crossmember spans between inboard faces of LH/RH rails.
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
    label = "UPPER" if upper else "LOWER"
    parallel = is_parallel_watts()

    if upper and not parallel:
        # Triangulated: upper brackets sit inboard at frame_upper_spread_z.
        z_pick = param_cm(design, "frame_upper_spread_z") * sign
        z_face = z_pick + sign * (clip_t / 2.0)
    else:
        # Lowers always, and parallel uppers: key into outboard rail plate.
        z_face = cl + sign * (tw / 2.0 + clear + clip_t)

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
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
    # Outboard-keyed: extrude toward CL into rail key. Triangulated upper: same sense.
    reverse = sign > 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByString("clip_t"))
    ext = extrudes.add(ext_in)
    ext.name = "EX_BRACKET_{}_{}".format(label, side)
    ext.bodies.item(0).name = "BRACKET_{}_{}".format(label, side)


def _draw_link_ref(comp, design, side, sign):
    """Construction lines for lower + upper bars (reference)."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_LINK_REF_{}".format(side)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines

    frame_l, axle_l = _link_pickup_pair(design, sign, upper=False)
    frame_u, axle_u = _link_pickup_pair(design, sign, upper=True)

    lower = lines.addByTwoPoints(
        sk.modelToSketchSpace(frame_l),
        sk.modelToSketchSpace(axle_l),
    )
    upper = lines.addByTwoPoints(
        sk.modelToSketchSpace(frame_u),
        sk.modelToSketchSpace(axle_u),
    )
    lower.isConstruction = True
    upper.isConstruction = True
    sk.isComputeDeferred = False


def _link_pickup_pair(design, sign, upper, axle_y_delta=0.0):
    """Return (frame_point, axle_point) as Point3D for one link side.

    axle_y_delta shifts the axle pickup height (cm) for bump/droop checks.
    parallel_watts: upper laterals match lowers so bars are parallel in plan.
    """
    if upper:
        fx = param_cm(design, "upper_pickup_x")
        fy = param_cm(design, "upper_pickup_y")
        ax = param_cm(design, "axle_upper_pickup_x")
        ay = param_cm(design, "axle_upper_pickup_y") + axle_y_delta
        if is_parallel_watts():
            # Parallel in plan view: same |Z| as lowers (outboard of rails).
            fz = param_cm(design, "frame_link_spread_z") * sign
            az = param_cm(design, "axle_lower_spread_z") * sign
        else:
            fz = param_cm(design, "frame_upper_spread_z") * sign
            az = param_cm(design, "axle_upper_spread_z") * sign
    else:
        fx = param_cm(design, "lower_pickup_x")
        fy = param_cm(design, "lower_pickup_y")
        fz = param_cm(design, "frame_link_spread_z") * sign
        ax = param_cm(design, "axle_lower_pickup_x")
        ay = param_cm(design, "axle_lower_pickup_y") + axle_y_delta
        az = param_cm(design, "axle_lower_spread_z") * sign
    return (
        adsk.core.Point3D.create(fx, fy, fz),
        adsk.core.Point3D.create(ax, ay, az),
    )


def _point_distance(p0, p1):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    dz = p1.z - p0.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _point_lerp(p0, p1, t):
    return adsk.core.Point3D.create(
        p0.x + (p1.x - p0.x) * t,
        p0.y + (p1.y - p0.y) * t,
        p0.z + (p1.z - p0.z) * t,
    )


def _axis_orthonormal(dx, dy, dz):
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-8:
        return (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    ax, ay, az = dx / length, dy / length, dz / length
    if abs(ax) < 0.9:
        hx, hy, hz = 1.0, 0.0, 0.0
    else:
        hx, hy, hz = 0.0, 1.0, 0.0
    ux = hy * az - hz * ay
    uy = hz * ax - hx * az
    uz = hx * ay - hy * ax
    ul = math.sqrt(ux * ux + uy * uy + uz * uz)
    ux, uy, uz = ux / ul, uy / ul, uz / ul
    vx = ay * uz - az * uy
    vy = az * ux - ax * uz
    vz = ax * uy - ay * ux
    return (ax, ay, az), (ux, uy, uz), (vx, vy, vz)


def _plane_perp_at_point(comp, origin, axis_vec, name):
    """Construction plane through origin, normal along axis_vec."""
    dx, dy, dz = axis_vec
    _n, u, v = _axis_orthonormal(dx, dy, dz)
    p0 = origin
    p1 = adsk.core.Point3D.create(origin.x + u[0], origin.y + u[1], origin.z + u[2])
    p2 = adsk.core.Point3D.create(origin.x + v[0], origin.y + v[1], origin.z + v[2])
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByThreePoints(p0, p1, p2)
    pl = planes.add(pin)
    pl.name = name
    return pl


def _extrude_circle_along(comp, origin, axis_end, radius, dist, name, hollow_id=None):
    """Extrude a circle (optional hollow) from origin toward axis_end by dist."""
    if dist <= 1e-6:
        return None
    dx = axis_end.x - origin.x
    dy = axis_end.y - origin.y
    dz = axis_end.z - origin.z
    pl = _plane_perp_at_point(comp, origin, (dx, dy, dz), "PL_{}".format(name))
    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    ctr = sk.modelToSketchSpace(origin)
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, radius)
    if hollow_id is not None and hollow_id > 0 and hollow_id < radius:
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, hollow_id)
    sk.isComputeDeferred = False

    prof = None
    if hollow_id is not None:
        prof = _find_ring_profile(sk)
    if prof is None and sk.profiles.count:
        prof = _largest_profile(sk)
    if prof is None:
        return None

    # Match extrude sense to desired axis (three-point plane winding can flip).
    reverse = False
    try:
        n = pl.geometry.normal
        reverse = (n.x * dx + n.y * dy + n.z * dz) < 0.0
    except Exception:
        reverse = False

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(dist))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        ext_in = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        ext_in.setDistanceExtent(not reverse, adsk.core.ValueInput.createByReal(dist))
        ext = extrudes.add(ext_in)
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


def _extrude_bolt_axis_housing(comp, center, width, od, bore, name):
    """Simplified bushed rod-end housing: cylinder along world Z with bore."""
    z0 = center.z - width / 2.0
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z0))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    ctr = sk.modelToSketchSpace(
        adsk.core.Point3D.create(center.x, center.y, z0)
    )
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, od / 2.0)
    if bore > 0:
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, bore / 2.0)
    sk.isComputeDeferred = False

    prof = _find_ring_profile(sk)
    if prof is None and sk.profiles.count:
        prof = _largest_profile(sk)
    if prof is None:
        return None

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(width))
    ext = extrudes.add(ext_in)
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


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
# Axle-side keyed link tabs (plate bodies → DXF)
# ---------------------------------------------------------------------------

def build_axle_link_brackets(comp):
    """Lower + upper link tabs on the Currie axle mockup (keyed plates)."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        _build_axle_link_tab(comp, design, side, sign, upper=False)
        _build_axle_link_tab(comp, design, side, sign, upper=True)


def _build_axle_link_tab(comp, design, side, sign, upper):
    _frame, axle_pt = _link_pickup_pair(design, sign, upper=upper)
    bw = param_cm(design, "axle_bracket_w")
    bh = param_cm(design, "axle_bracket_h")
    bt = param_cm(design, "axle_bracket_t")
    hole = param_cm(design, "bracket_hole_d")
    key_w = param_cm(design, "tab_width")
    key_l = bt

    xc, yc, zc = axle_pt.x, axle_pt.y, axle_pt.z
    label = "UPPER" if upper else "LOWER"
    # Plate on XY at outboard face of tab; extrude toward vehicle CL.
    z_face = zc + sign * (bt / 2.0)

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
    pl = planes.add(pin)
    pl.name = "PL_AXLE_TAB_{}_{}".format(label, side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_AXLE_TAB_{}_{}".format(label, side)
    sk.isComputeDeferred = True
    hx = bw / 2.0
    hy = bh / 2.0
    # Single outer loop: plate + forward key tongue (fixture / weld key).
    # Walk CCW: key tip → up key → plate front-top → around plate → key bottom.
    kx0 = xc - hx - key_l
    pts = [
        (kx0, yc - key_w / 2.0),
        (kx0, yc + key_w / 2.0),
        (xc - hx, yc + key_w / 2.0),
        (xc - hx, yc + hy),
        (xc + hx, yc + hy),
        (xc + hx, yc - hy),
        (xc - hx, yc - hy),
        (xc - hx, yc - key_w / 2.0),
    ]
    lines = sk.sketchCurves.sketchLines
    sp = [
        sk.modelToSketchSpace(adsk.core.Point3D.create(px, py, z_face))
        for px, py in pts
    ]
    for i in range(len(sp)):
        lines.addByTwoPoints(sp[i], sp[(i + 1) % len(sp)])

    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, yc, z_face))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, hole / 2.0)
    sk.isComputeDeferred = False

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
    reverse = sign > 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(bt))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return
    ext.name = "EX_AXLE_TAB_{}_{}".format(label, side)
    ext.bodies.item(0).name = "AXLE_TAB_{}_{}".format(label, side)


# ---------------------------------------------------------------------------
# Triangulated four-link bars (tube + RH/LH rod ends + bungs + jam nuts)
# ---------------------------------------------------------------------------

def build_four_link_bars(comp):
    """Build 4 bars between frame and axle pickups; return cut-list rows."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    rows = []
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        for upper, role in ((False, "LOWER"), (True, "UPPER")):
            row = _build_one_link_bar(comp, design, side, sign, upper, role)
            if row:
                rows.append(row)
    return rows


def _build_one_link_bar(comp, design, side, sign, upper, role):
    """One bar: frame RH rod end ↔ tube ↔ axle LH rod end (spin-to-adjust)."""
    frame_pt, axle_pt = _link_pickup_pair(design, sign, upper=upper)
    cc = _point_distance(frame_pt, axle_pt)
    if cc < 1e-4:
        return None

    eye = param_cm(design, "rod_end_eye_to_shoulder")
    bung_l = param_cm(design, "bung_length")
    tube_od = param_cm(design, "link_bar_od")
    tube_wall = param_cm(design, "link_bar_wall")
    bung_od = param_cm(design, "bung_od")
    shank_od = param_cm(design, "rod_end_shank_od")
    housing_od = param_cm(design, "rod_end_housing_od")
    housing_w = param_cm(design, "rod_end_housing_width")
    bore = param_cm(design, "rod_end_bore")
    jam_od = param_cm(design, "jam_nut_od")
    jam_w = param_cm(design, "jam_nut_width")
    adjust = param_cm(design, "rod_end_adjustable_length")
    engage = param_cm(design, "rod_end_thread_engagement_min")
    thread_callout = string_param("rod_end_shank_thread", "3/4-16")

    # cut = C-C − eye-to-shoulder (both ends) − bung lengths (both ends)
    tube_cut = cc - 2.0 * eye - 2.0 * bung_l
    if tube_cut < 0:
        tube_cut = 0.0

    bar_name = "BAR_{}_{}".format(role, side)

    # Stations along bar from frame (t=0) to axle (t=1), by arc length.
    # Frame eye @ 0
    # Frame shoulder @ eye
    # Frame bung starts after shoulder+adjust region ≈ eye + adjust
    #   (adjustable thread between shoulder and bung face)
    # Tube from (eye + bung_l) ... but bung occupies bung_l into the gap after shoulder.
    # Layout used here (symmetric):
    #   [eye]--shank/adjust--[bung][TUBE][bung]--shank/adjust--[eye]
    #   shoulder at eye distance; bung abuts tube; exposed adjust = (cc - tube - 2*bung - 2*eye)/2
    # which equals 0 if cut formula is exact with no extra adjust gap.
    # Keep adjustable_length as a documented param; geometry places bung face at
    # distance eye from each eye center (bung starts at eye, extends bung_l toward mid).
    t_bung0_a = eye / cc
    t_bung0_b = (eye + bung_l) / cc
    t_tube_a = t_bung0_b
    t_tube_b = 1.0 - (eye + bung_l) / cc
    t_bung1_a = t_tube_b
    t_bung1_b = 1.0 - eye / cc

    # Rod-end housings at pickups (bolt axis ≈ world Z, matches bracket plates).
    _extrude_bolt_axis_housing(
        comp, frame_pt, housing_w, housing_od, bore,
        "{}_RE_RH".format(bar_name),
    )
    _extrude_bolt_axis_housing(
        comp, axle_pt, housing_w, housing_od, bore,
        "{}_RE_LH".format(bar_name),
    )

    # Shanks from eye toward tube (simplified cylinders along bar).
    shank_len = max(eye * 0.85, engage)
    _extrude_circle_along(
        comp, frame_pt, axle_pt, shank_od / 2.0, shank_len,
        "{}_SHANK_RH".format(bar_name),
    )
    _extrude_circle_along(
        comp, axle_pt, frame_pt, shank_od / 2.0, shank_len,
        "{}_SHANK_LH".format(bar_name),
    )

    # Jam nuts on shanks just outboard of each bung face.
    jam_t0 = max(t_bung0_a - jam_w / cc, 0.01)
    jam_frame = _point_lerp(frame_pt, axle_pt, jam_t0)
    _extrude_circle_along(
        comp, jam_frame, axle_pt, jam_od / 2.0, jam_w,
        "{}_JAM_RH".format(bar_name),
    )
    # Axle jam sits between bung face and eye; extrude toward axle eye.
    jam_axle = _point_lerp(frame_pt, axle_pt, t_bung1_b)
    _extrude_circle_along(
        comp, jam_axle, axle_pt, jam_od / 2.0, jam_w,
        "{}_JAM_LH".format(bar_name),
    )

    # Bungs (threaded inserts) at each tube end.
    bung0 = _point_lerp(frame_pt, axle_pt, t_bung0_a)
    _extrude_circle_along(
        comp, bung0, axle_pt, bung_od / 2.0, bung_l,
        "{}_BUNG_RH".format(bar_name),
    )
    bung1 = _point_lerp(frame_pt, axle_pt, t_bung1_a)
    _extrude_circle_along(
        comp, bung1, axle_pt, bung_od / 2.0, bung_l,
        "{}_BUNG_LH".format(bar_name),
    )

    # Tube between bung inner faces.
    if tube_cut > 1e-4 and t_tube_b > t_tube_a:
        tube_start = _point_lerp(frame_pt, axle_pt, t_tube_a)
        tube_id = max(tube_od / 2.0 - tube_wall, 0.01)
        _extrude_circle_along(
            comp, tube_start, axle_pt, tube_od / 2.0, tube_cut,
            "{}_TUBE".format(bar_name),
            hollow_id=tube_id,
        )

    return {
        "name": bar_name,
        "side": side,
        "role": role,
        "cc_length_in": cc / IN_TO_CM,
        "tube_cut_length_in": tube_cut / IN_TO_CM,
        "rod_end_frame": "RH {}".format(thread_callout),
        "rod_end_axle": "LH {}".format(thread_callout),
        "eye_to_shoulder_in": eye / IN_TO_CM,
        "bung_length_in": bung_l / IN_TO_CM,
        "adjustable_length_in": adjust / IN_TO_CM,
        "thread_engagement_min_in": engage / IN_TO_CM,
        "bar_od_in": tube_od / IN_TO_CM,
        "bar_wall_in": tube_wall / IN_TO_CM,
        "notes": (
            (
                "PLACEHOLDER pickups; parallel upper (plan-parallel to lower)"
                if is_parallel_watts()
                else "PLACEHOLDER pickups; triangulated upper inboard"
            )
            if upper
            else "PLACEHOLDER pickups; REV-B lower outboard of rails"
        ),
    }


def write_bar_cut_list(path, rows):
    """Write four-link tube cut list CSV (inches)."""
    fields = [
        "name",
        "side",
        "role",
        "cc_length_in",
        "tube_cut_length_in",
        "rod_end_frame",
        "rod_end_axle",
        "eye_to_shoulder_in",
        "bung_length_in",
        "adjustable_length_in",
        "thread_engagement_min_in",
        "bar_od_in",
        "bar_wall_in",
        "notes",
    ]
    try:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                out = {}
                for key in fields:
                    val = row.get(key, "")
                    if isinstance(val, float):
                        out[key] = "{:.4f}".format(val)
                    else:
                        out[key] = val
                writer.writerow(out)
    except Exception:
        pass


def maybe_build_lateral_locator(comp):
    """Build Watts when parallel_watts; panhard stays TODO; else no-op.

    lateral_locator string is legacy: watts is implied by rear_link_type=
    parallel_watts. panhard remains a stub TODO.
    """
    if is_parallel_watts():
        build_watts_link(comp)
        return

    loc = string_param("lateral_locator", "none").strip().lower()
    if loc in ("", "none", "0"):
        return
    if loc == "watts":
        # Prefer rear_link_type=parallel_watts so uppers are parallel too.
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = "SK_LATERAL_TODO_WATTS_USE_parallel_watts"
        sk.isComputeDeferred = True
        lines = sk.sketchCurves.sketchLines
        ln = lines.addByTwoPoints(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(1.0, 0, 0),
        )
        ln.isConstruction = True
        sk.isComputeDeferred = False
        return
    # panhard (or unknown): stub TODO — not modeled.
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_LATERAL_TODO_{}".format(loc.upper())
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    ln = lines.addByTwoPoints(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(1.0, 0, 0),
    )
    ln.isConstruction = True
    sk.isComputeDeferred = False


def _watts_pivot_point(design, axle_y_delta=0.0):
    """Center pivot on the aft face of the housing center section."""
    px = param_cm(design, "watts_pivot_x")
    py = param_cm(design, "watts_pivot_y") + axle_y_delta
    pz = param_cm(design, "pinion_offset")
    return adsk.core.Point3D.create(px, py, pz)


def _watts_frame_pickup(design, sign):
    """Frame-side Watts bracket pickup (inboard of rail)."""
    fx = param_cm(design, "watts_frame_x")
    fy = param_cm(design, "watts_frame_y")
    # Pickup at inboard outer face (bracket keys into inboard plate from inside).
    fz = _rail_inboard_outer_z(design) * sign
    return adsk.core.Point3D.create(fx, fy, fz)


def _watts_crank_tip(design, sign, axle_y_delta=0.0):
    """Bell-crank tip — flat horizontal 180° crank (ride + bump/droop sweep).

    Pivot rides with the axle (axle_y_delta). Tips stay at pivot Y, ±crank in Z
    (PLACEHOLDER; link angle absorbs vertical travel for the clearance AABB).
    """
    pivot = _watts_pivot_point(design, axle_y_delta)
    crank = param_cm(design, "watts_crank_len")
    return adsk.core.Point3D.create(pivot.x, pivot.y, pivot.z + sign * crank)


def build_watts_link(comp):
    """Axle-mounted Watts: pivot mount + bell crank + 2 lateral links + frame brackets."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    _build_watts_pivot_mount(comp, design)
    _build_watts_crank(comp, design)
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        _build_watts_frame_bracket(comp, design, side, sign)
        _build_watts_lateral_link(comp, design, side, sign)


def _build_watts_pivot_mount(comp, design):
    """Keyed plate on the aft face of the CS for the center pivot (DXF)."""
    pivot = _watts_pivot_point(design)
    mw = param_cm(design, "watts_pivot_mount_w")
    mh = param_cm(design, "watts_pivot_mount_h")
    mt = param_cm(design, "watts_crank_t")
    hole = param_cm(design, "watts_pivot_bolt_d")
    # Plate on YZ at aft CS face; extrude aft (+X) by mt.
    x_face = pivot.x
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_WATTS_PIVOT_MOUNT"

    sk = comp.sketches.add(pl)
    sk.name = "SK_WATTS_PIVOT_MOUNT"
    sk.isComputeDeferred = True
    cy, cz = pivot.y, pivot.z
    hw, hh = mw / 2.0, mh / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - hh, cz - hw))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + hh, cz - hw))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + hh, cz + hw))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - hh, cz + hw))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, hole / 2.0)
    sk.isComputeDeferred = False

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
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mt))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return
    ext.name = "EX_WATTS_PIVOT_MOUNT"
    ext.bodies.item(0).name = "WATTS_PIVOT_MOUNT"


def _build_watts_crank(comp, design):
    """Horizontal 180° bell crank plate (YZ) aft of the pivot mount (DXF)."""
    pivot = _watts_pivot_point(design)
    crank = param_cm(design, "watts_crank_len")
    arm_w = param_cm(design, "watts_crank_arm_w")
    mt = param_cm(design, "watts_crank_t")
    pivot_hole = param_cm(design, "watts_pivot_bolt_d")
    tip_hole = param_cm(design, "watts_bolt_d")
    # Crank plane just aft of pivot mount.
    x_face = pivot.x + mt
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_WATTS_CRANK"

    sk = comp.sketches.add(pl)
    sk.name = "SK_WATTS_CRANK"
    sk.isComputeDeferred = True
    cy, cz = pivot.y, pivot.z
    # Capsule / bar outline along Z through pivot.
    half_z = crank + arm_w / 2.0
    hy = arm_w / 2.0
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - hy, cz - half_z))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + hy, cz - half_z))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + hy, cz + half_z))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - hy, cz + half_z))
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    # Center pivot + tip holes.
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz)),
        pivot_hole / 2.0,
    )
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz + crank)),
        tip_hole / 2.0,
    )
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy, cz - crank)),
        tip_hole / 2.0,
    )
    sk.isComputeDeferred = False

    # Prefer the profile with the most loops (outer + 3 holes).
    prof = None
    best = -1
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        n = p.profileLoops.count
        if n > best:
            best = n
            prof = p
    if prof is None:
        return
    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mt))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return
    ext.name = "EX_WATTS_CRANK"
    ext.bodies.item(0).name = "WATTS_CRANK"


def _build_watts_frame_bracket(comp, design, side, sign):
    """Keyed plate on inboard rail face for Watts lateral link (DXF)."""
    pt = _watts_frame_pickup(design, sign)
    bw = param_cm(design, "watts_bracket_w")
    bh = param_cm(design, "watts_bracket_h")
    hole = param_cm(design, "watts_bolt_d")
    clip_t = param_cm(design, "clip_t")
    # Bracket sits on inboard outer face; extrude toward CL into the key? 
    # Keys are cut from inboard INNER face into plate. Bracket keys from bay
    # (inboard of rail) into the plate — face at inboard outer, extrude outboard.
    z_face = pt.z  # inboard outer
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
    pl = planes.add(pin)
    pl.name = "PL_BRACKET_WATTS_{}".format(side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_BRACKET_WATTS_{}".format(side)
    sk.isComputeDeferred = True
    xc, yc = pt.x, pt.y
    hx, hy = bw / 2.0, bh / 2.0
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
    # Extrude into the inboard plate (outboard direction into key pocket).
    # RH inboard outer normal is −Z (toward CL); pocket is +Z into plate → reverse for RH.
    reverse = sign < 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(clip_t))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return
    ext.name = "EX_BRACKET_WATTS_{}".format(side)
    ext.bodies.item(0).name = "BRACKET_WATTS_{}".format(side)


def _build_watts_lateral_link(comp, design, side, sign):
    """Simple tube between crank tip and frame Watts pickup."""
    tip = _watts_crank_tip(design, sign)
    frame = _watts_frame_pickup(design, sign)
    od = param_cm(design, "watts_link_od")
    wall = param_cm(design, "watts_link_wall")
    cc = _point_distance(tip, frame)
    if cc < 1e-4:
        return
    tube_id = max(od / 2.0 - wall, 0.01)
    _extrude_circle_along(
        comp,
        tip,
        frame,
        od / 2.0,
        cc,
        "WATTS_LINK_{}".format(side),
        hollow_id=tube_id,
    )
    # Construction ref.
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "SK_WATTS_LINK_REF_{}".format(side)
    sk.isComputeDeferred = True
    ln = sk.sketchCurves.sketchLines.addByTwoPoints(
        sk.modelToSketchSpace(tip),
        sk.modelToSketchSpace(frame),
    )
    ln.isConstruction = True
    sk.isComputeDeferred = False


# ---------------------------------------------------------------------------
# Over-axle crossmember (keyed into inboard kickup rails)
# ---------------------------------------------------------------------------

def build_over_axle_crossmember(comp):
    """Top + front/rear webs + optional bottom; end keys into inboard rail slots."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    wb = param_cm(design, "wb")
    ox_w = param_cm(design, "ox_width_x")
    ox_t = param_cm(design, "ox_plate_t")
    ox_h = param_cm(design, "ox_web_h")
    key_l = param_cm(design, "clip_t")
    y_top = _over_axle_top_y(design)
    z_rh = _rail_inboard_inner_z(design, 1.0)
    z_lh = _rail_inboard_inner_z(design, -1.0)
    # Span between inboard faces; tabs protrude key_l into each rail pocket.
    z0 = min(z_lh, z_rh) - key_l
    z1 = max(z_lh, z_rh) + key_l
    x0 = wb - ox_w / 2.0
    x1 = wb + ox_w / 2.0

    _ox_horizontal_plate(
        comp, "XMEMBER_OA_TOP", x0, x1, y_top, z0, z1, ox_t, up=True
    )
    _ox_web_plate(comp, "XMEMBER_OA_WEB_FWD", x0, y_top, y_top - ox_h, z0, z1, ox_t)
    _ox_web_plate(comp, "XMEMBER_OA_WEB_AFT", x1, y_top, y_top - ox_h, z0, z1, ox_t)
    if _ox_include_bottom(design):
        _ox_horizontal_plate(
            comp,
            "XMEMBER_OA_BOT",
            x0,
            x1,
            y_top - ox_h,
            z0,
            z1,
            ox_t,
            up=False,
        )


def _ox_horizontal_plate(comp, name, x0, x1, y, z0, z1, thickness, up):
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


def _ox_web_plate(comp, name, x_face, y_top, y_bot, z0, z1, thickness):
    """Vertical web on YZ at x_face; extrude toward axle CL (inboard along X)."""
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    lines = sk.sketchCurves.sketchLines
    # YZ sketch: x→Z, y→Y
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y_bot, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y_top, z0))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y_top, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, y_bot, z1))
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
    # YZ plane normal is +X. FWD web at x0 wants +X (into box); AFT at x1 wants −X.
    wb = param_cm(adsk.fusion.Design.cast(comp.parentDesign), "wb")
    reverse = x_face > wb
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(thickness))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


# ---------------------------------------------------------------------------
# Aft receivers (square tube through end cap + OD key lap + rear XM)
# ---------------------------------------------------------------------------

def build_receivers(comp, rail_rh, rail_lh, xmembers):
    """Hollow square receivers LH/RH, OD-face key tabs, rear XM, bolt holes."""
    design = adsk.fusion.Design.cast(comp.parentDesign)
    for passenger in (True, False):
        _build_one_receiver(comp, design, passenger=passenger)
        _build_receiver_keys(comp, design, passenger=passenger)
        _cut_receiver_bolt_holes(comp, design, passenger=passenger)
    build_receiver_crossmember(xmembers, design)
    # rail_rh / rail_lh already have clearance tunnels + end caps.
    _ = (rail_rh, rail_lh)


def _build_one_receiver(comp, design, passenger=True):
    """Extrude hollow square tube along +X at rail_cl / rcv_cl_y.

    Tube runs rcv_front_x → rcv_rear_x, passing through the rail-end cap
    cutout. Key-bay plate material is cleared so OD does not intersect rails.
    """
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    x0 = param_cm(design, "rcv_front_x")
    x1 = param_cm(design, "rcv_rear_x")
    length = x1 - x0
    if length <= 0.05 * IN_TO_CM:
        length = param_cm(design, "rcv_length")
    od = param_cm(design, "rcv_od")
    wall = param_cm(design, "rcv_wall")
    cy = param_cm(design, "rcv_cl_y")
    cz = param_cm(design, "rail_cl") * sign

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x0))
    pl = planes.add(pin)
    pl.name = "PL_RCV_{}".format(side)

    sk = comp.sketches.add(pl)
    sk.name = "SK_RCV_{}".format(side)
    sk.isComputeDeferred = True
    half = od / 2.0
    inner = half - wall
    oc = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy, cz))
    or_ = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy + half, cz + half))
    ir_ = sk.modelToSketchSpace(adsk.core.Point3D.create(x0, cy + inner, cz + inner))
    sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, or_)
    if inner > 0.05:
        sk.sketchCurves.sketchLines.addCenterPointRectangle(oc, ir_)
    sk.isComputeDeferred = False

    ring = _find_ring_profile(sk)
    if not ring:
        # Fall back to solid outer if ring not found.
        if sk.profiles.count < 1:
            return None
        ring = _largest_profile(sk)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(ring, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(length))
    ext = extrudes.add(ext_in)
    ext.name = "EX_RCV_{}".format(side)
    body = ext.bodies.item(0)
    body.name = "RECEIVER_{}".format(side)
    return body


def _build_receiver_keys(comp, design, passenger=True):
    """Key tabs on receiver OD faces, lapping rail side plates (DXF).

    Inner face of each tab sits on the receiver OD (|z − rail_cl·sign| =
    rcv_od/2) and extrudes outward by clip_t. X span is
    [rcv_front_x − rcv_key_w, rail_end_x]: lap the receiver in the key bay
    and the rail side-plate outer face forward of the window. Gap to the
    plate outer face is rcv_od/2 − box_od_w/2 (weld/shim; no intersection).
    OUT tabs land outboard of the receiver; IN tabs inboard.
    """
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    rcv_front = param_cm(design, "rcv_front_x")
    key_w = param_cm(design, "rcv_key_w")
    x0 = rcv_front - key_w
    x1 = param_cm(design, "rail_end_x")
    key_h = param_cm(design, "rcv_key_h")
    cy = param_cm(design, "rcv_cl_y")
    od = param_cm(design, "rcv_od")
    t = param_cm(design, "clip_t")
    cz = param_cm(design, "rail_cl") * sign
    xc = 0.5 * (x0 + x1)
    hx = max(abs(x1 - x0) / 2.0, 0.05 * IN_TO_CM)
    hy = key_h / 2.0
    # Receiver OD faces (inner face of each tab).
    z_in_od = cz - sign * (od / 2.0)
    z_out_od = cz + sign * (od / 2.0)

    for role, z_face, toward_outboard in (
        ("IN", z_in_od, False),
        ("OUT", z_out_od, True),
    ):
        name = "RCV_KEY_{}_{}".format(side, role)
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
        pl = planes.add(pin)
        pl.name = "PL_{}".format(name)

        sk = comp.sketches.add(pl)
        sk.name = "SK_{}".format(name)
        sk.isComputeDeferred = True
        p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, cy - hy, z_face))
        p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, cy + hy, z_face))
        p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, cy + hy, z_face))
        p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, cy - hy, z_face))
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
        ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # Extrude away from the receiver CL: OUT further outboard, IN further
        # inboard. XY normal is +Z; reverse selects −Z.
        if sign > 0:
            reverse = not toward_outboard
        else:
            reverse = toward_outboard
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(t))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_{}".format(name)
            ext.bodies.item(0).name = name
        except Exception:
            pass


def _rcv_bolt_count(design):
    try:
        return max(int(round(design.userParameters.itemByName("rcv_bolt_count").value)), 1)
    except Exception:
        return 2


def _cut_receiver_bolt_holes(comp, design, passenger=True):
    """Cross-bolt holes through receiver side walls (along Z) for module lock."""
    sign = 1.0 if passenger else -1.0
    side = "RH" if passenger else "LH"
    od = param_cm(design, "rcv_od")
    cy = param_cm(design, "rcv_cl_y")
    cz = param_cm(design, "rail_cl") * sign
    d = param_cm(design, "rcv_bolt_d")
    pitch = param_cm(design, "rcv_bolt_pitch")
    x_first = param_cm(design, "rcv_bolt_first_x")
    n = _rcv_bolt_count(design)
    # Sketch on XY at outboard outer face of tube; cut through full OD along −sign Z.
    z_face = cz + sign * (od / 2.0)

    for i in range(n):
        xc = x_first + i * pitch
        planes = comp.constructionPlanes
        pin = planes.createInput()
        pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
        pl = planes.add(pin)
        pl.name = "PL_RCV_BOLT_{}_{}".format(side, i + 1)

        sk = comp.sketches.add(pl)
        sk.name = "SK_RCV_BOLT_{}_{}".format(side, i + 1)
        ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, cy, z_face))
        sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, d / 2.0)
        if sk.profiles.count < 1:
            continue
        prof = sk.profiles.item(0)
        extrudes = comp.features.extrudeFeatures
        ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
        # Cut through both walls (+ a little) toward frame CL.
        reverse = sign > 0
        ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(od + 0.1))
        try:
            ext = extrudes.add(ext_in)
            ext.name = "EX_RCV_BOLT_{}_{}".format(side, i + 1)
        except Exception:
            pass


def build_receiver_crossmember(comp, design):
    """Plate crossmember tying LH/RH receivers; ends seat on inboard tube faces."""
    xc = param_cm(design, "rcv_xm_x")
    # Plate thickness along X = rcv_xm_t (rcv_xm_w is layout envelope only).
    try:
        t = param_cm(design, "rcv_xm_t")
    except Exception:
        t = param_cm(design, "rcv_xm_w")
    h = param_cm(design, "rcv_xm_h")
    if t < 0.01:
        t = param_cm(design, "rcv_xm_w")
    cy = param_cm(design, "rcv_cl_y")
    od = param_cm(design, "rcv_od")
    cl = param_cm(design, "rail_cl")
    # Span between inboard faces of the two receivers.
    z0 = -(cl - od / 2.0)
    z1 = cl - od / 2.0
    x_face = xc - t / 2.0

    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(x_face))
    pl = planes.add(pin)
    pl.name = "PL_XMEMBER_RCV"

    sk = comp.sketches.add(pl)
    sk.name = "SK_XMEMBER_RCV"
    sk.isComputeDeferred = True
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - h / 2.0, z0))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + h / 2.0, z0))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy + h / 2.0, z1))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(x_face, cy - h / 2.0, z1))
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
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(t))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_XMEMBER_RCV"
    body = ext.bodies.item(0)
    body.name = "XMEMBER_RCV"
    return body


# ---------------------------------------------------------------------------
# Bag / coilover mounts on over-axle XM (shared positions via suspension_mode)
# ---------------------------------------------------------------------------

def build_suspension_mounts(mounts_comp, axle_comp):
    """Upper mounts on over-axle XM; matching lower mounts on axle housing."""
    design = adsk.fusion.Design.cast(mounts_comp.parentDesign)
    mode = suspension_mode_value(design)
    for passenger in (True, False):
        sign = 1.0 if passenger else -1.0
        side = "RH" if passenger else "LH"
        if mode >= 0.5:
            _build_bag_mount_pair(mounts_comp, axle_comp, design, side, sign)
        else:
            _build_shock_tab_pair(mounts_comp, axle_comp, design, side, sign)


def _mount_xyz(design, sign):
    """Bag/shock mount X and lateral Z. REV-B: inboard via bag_y / shock_y."""
    wb = param_cm(design, "wb")
    x = wb + param_cm(design, "mount_x_off")
    mode = suspension_mode_value(design)
    if mode >= 0.5:
        z = param_cm(design, "bag_y") * sign
    else:
        z = param_cm(design, "shock_y") * sign
    return x, z


def _build_shock_tab_pair(mounts_comp, axle_comp, design, side, sign):
    """Keyed double-shear tab pairs: upper from XM, lower on axle housing."""
    x, z = _mount_xyz(design, sign)
    eye_y = param_cm(design, "shock_eye_y")
    tw = param_cm(design, "shock_tab_w")
    th = param_cm(design, "shock_tab_h")
    gap = param_cm(design, "shock_tab_gap")
    bore = param_cm(design, "shock_bore")
    pt = param_cm(design, "ox_plate_t")
    sc = param_cm(design, "slot_clear")
    key_l = pt
    # Key into bottom plate when present; otherwise into top plate underside.
    if _ox_include_bottom(design):
        y_seat = _over_axle_underside_y(design)
    else:
        y_seat = _over_axle_top_y(design)

    # Upper pair hangs from XM; key tongue into bottom/top plate.
    y1 = y_seat + key_l
    for idx, z_face in enumerate((z - gap / 2.0, z + gap / 2.0)):
        label = "A" if idx == 0 else "B"
        # Mating slot in XM plate for the key tongue.
        _cut_ox_shock_key_slot(
            mounts_comp, design, side, label, x, z_face, tw, pt, sc, y_seat
        )
        _build_shock_tab_plate(
            mounts_comp,
            "SHOCK_TAB_UPPER_{}_{}".format(side, label),
            xc=x,
            yc=eye_y,
            z_face=z_face,
            sign=sign,
            tab_w=tw,
            tab_h=th,
            key_l=key_l,
            y_key_top=y1,
            bore=bore,
            thickness=pt,
        )

    # Lower pair on axle housing — mirror layout, eye near axle tube top.
    ay = param_cm(design, "axle_cl_y")
    tube_od = param_cm(design, "axle_tube_od")
    low_eye = ay + tube_od / 2.0 + th * 0.35
    for idx, z_face in enumerate((z - gap / 2.0, z + gap / 2.0)):
        label = "A" if idx == 0 else "B"
        _build_shock_tab_plate(
            axle_comp,
            "SHOCK_TAB_LOWER_{}_{}".format(side, label),
            xc=x,
            yc=low_eye,
            z_face=z_face,
            sign=sign,
            tab_w=tw,
            tab_h=th,
            key_l=key_l,
            y_key_top=low_eye + th / 2.0,
            bore=bore,
            thickness=pt,
            key_down=True,
        )


def _cut_ox_shock_key_slot(comp, design, side, label, xc, z_face, tab_w, plate_t, slot_clear, y_under):
    """Cut a key slot through the over-axle underside plate for an upper shock tab."""
    # Slot lives on the XM component (03_CROSSMEMBERS); find it via root.
    root = adsk.fusion.Design.cast(comp.parentDesign).rootComponent
    xm_comp = None
    for i in range(root.occurrences.count):
        occ = root.occurrences.item(i)
        if "03_CROSSMEMBERS" in occ.component.name or "03_CROSSMEMBERS" in occ.name:
            xm_comp = occ.component
            break
    if xm_comp is None:
        xm_comp = comp

    planes = xm_comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(xm_comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y_under))
    pl = planes.add(pin)
    name = "OA_SHOCK_SLOT_{}_{}".format(side, label)
    pl.name = "PL_{}".format(name)

    sk = xm_comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    key_half = min(tab_w * 0.25, param_cm(design, "tab_width") / 2.0) + slot_clear
    # Slot along Z ≈ plate thickness of the shock tab + clear; along X = key width.
    z0 = z_face - plate_t / 2.0 - slot_clear
    z1 = z_face + plate_t / 2.0 + slot_clear
    lines = sk.sketchCurves.sketchLines
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - key_half, y_under, min(z0, z1)))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - key_half, y_under, max(z0, z1)))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + key_half, y_under, max(z0, z1)))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + key_half, y_under, min(z0, z1)))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    sk.isComputeDeferred = False
    if sk.profiles.count < 1:
        return
    prof = _largest_profile(sk)
    extrudes = xm_comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    # Cut upward into the underside plate.
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(plate_t + 2 * slot_clear))
    try:
        ext = extrudes.add(ext_in)
        ext.name = "EX_{}".format(name)
    except Exception:
        pass


def _build_shock_tab_plate(
    comp, name, xc, yc, z_face, sign, tab_w, tab_h, key_l, y_key_top, bore, thickness,
    key_down=False,
):
    """Single shock tab in XY (thin along Z) with key tongue and bolt bore."""
    _ = sign  # reserved for future asymmetric keying
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_face))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    hx = tab_w / 2.0
    hy = tab_h / 2.0
    y_lo = yc - hy
    y_hi = yc + hy
    key_half = min(hx * 0.4, tab_w * 0.25)

    if key_down:
        # Plate + key tongue below into axle housing.
        pts = [
            (xc - hx, y_lo),
            (xc - hx, y_hi),
            (xc + hx, y_hi),
            (xc + hx, y_lo),
            (xc + key_half, y_lo),
            (xc + key_half, y_lo - key_l),
            (xc - key_half, y_lo - key_l),
            (xc - key_half, y_lo),
        ]
    else:
        # Plate + key tongue up into over-axle XM slot.
        y_top = max(y_hi, y_key_top)
        pts = [
            (xc - key_half, y_top),
            (xc - hx, y_hi if y_hi < y_top else y_top),
            (xc - hx, y_lo),
            (xc + hx, y_lo),
            (xc + hx, y_hi if y_hi < y_top else y_top),
            (xc + key_half, y_top),
        ]
        if y_hi < y_top:
            pts = [
                (xc - key_half, y_top),
                (xc - key_half, y_hi),
                (xc - hx, y_hi),
                (xc - hx, y_lo),
                (xc + hx, y_lo),
                (xc + hx, y_hi),
                (xc + key_half, y_hi),
                (xc + key_half, y_top),
            ]

    lines = sk.sketchCurves.sketchLines
    sp = [
        sk.modelToSketchSpace(adsk.core.Point3D.create(px, py, z_face))
        for px, py in pts
    ]
    for i in range(len(sp)):
        lines.addByTwoPoints(sp[i], sp[(i + 1) % len(sp)])

    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, yc, z_face))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, bore / 2.0)
    sk.isComputeDeferred = False

    prof = None
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        if p.profileLoops.count == 2:
            prof = p
            break
    if prof is None and sk.profiles.count:
        prof = _largest_profile(sk)
    if prof is None:
        return None

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Extrude toward vehicle CL from the tab face.
    reverse = z_face > 0
    ext_in.setDistanceExtent(reverse, adsk.core.ValueInput.createByReal(thickness))
    try:
        ext = extrudes.add(ext_in)
    except Exception:
        return None
    ext.name = "EX_{}".format(name)
    body = ext.bodies.item(0)
    body.name = name
    return body


def _build_bag_mount_pair(mounts_comp, axle_comp, design, side, sign):
    """Upper bag plate on XM underside; lower bag plate on axle (~1:1 under it)."""
    x, z = _mount_xyz(design, sign)
    mw = param_cm(design, "bag_mount_w")
    ml = param_cm(design, "bag_mount_l")
    stud_d = param_cm(design, "bag_stud_d")
    stud_off = param_cm(design, "bag_stud_offset")
    air_d = param_cm(design, "bag_air_hole_d")
    pt = param_cm(design, "ox_plate_t")
    xm_under = _over_axle_underside_y(design)

    _build_bag_plate(
        mounts_comp,
        "MOUNT_BAG_UPPER_{}".format(side),
        xc=x,
        yc=xm_under,
        zc=z,
        mw=mw,
        ml=ml,
        thickness=pt,
        up=False,
        stud_d=stud_d,
        stud_off=stud_off,
        air_d=air_d,
    )

    # Lower plate sits on axle tube / CS top, directly under upper (~1:1).
    ay = param_cm(design, "axle_cl_y")
    tube_od = param_cm(design, "axle_tube_od")
    csh = param_cm(design, "cs_height")
    house_top = ay + max(tube_od / 2.0, csh / 2.0)
    _build_bag_plate(
        axle_comp,
        "MOUNT_BAG_LOWER_{}".format(side),
        xc=x,
        yc=house_top,
        zc=z,
        mw=mw,
        ml=ml,
        thickness=pt,
        up=True,
        stud_d=stud_d,
        stud_off=stud_off,
        air_d=air_d,
    )


def _build_bag_plate(
    comp, name, xc, yc, zc, mw, ml, thickness, up, stud_d, stud_off, air_d
):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(yc))
    pl = planes.add(pin)
    pl.name = "PL_{}".format(name)

    sk = comp.sketches.add(pl)
    sk.name = "SK_{}".format(name)
    sk.isComputeDeferred = True
    hx = mw / 2.0
    hz = ml / 2.0
    lines = sk.sketchCurves.sketchLines
    p00 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc, zc - hz))
    p01 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc - hx, yc, zc + hz))
    p11 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc, zc + hz))
    p10 = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + hx, yc, zc - hz))
    lines.addByTwoPoints(p00, p01)
    lines.addByTwoPoints(p01, p11)
    lines.addByTwoPoints(p11, p10)
    lines.addByTwoPoints(p10, p00)
    # Center air-fitting hole + single 3/8 stud (PLACEHOLDER pattern).
    ctr = sk.modelToSketchSpace(adsk.core.Point3D.create(xc, yc, zc))
    sk.sketchCurves.sketchCircles.addByCenterRadius(ctr, air_d / 2.0)
    stud = sk.modelToSketchSpace(adsk.core.Point3D.create(xc + stud_off, yc, zc))
    sk.sketchCurves.sketchCircles.addByCenterRadius(stud, stud_d / 2.0)
    sk.isComputeDeferred = False

    prof = None
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        if p.profileLoops.count >= 2:
            # Prefer the outer ring with holes (most loops).
            if prof is None or p.profileLoops.count > prof.profileLoops.count:
                prof = p
    if prof is None and sk.profiles.count:
        prof = _largest_profile(sk)
    if prof is None:
        return None

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


def receiver_packaging_report(design):
    """Pure-math packaging checks for rail end / receiver / slide-in path."""
    lines = ["Receiver packaging checks (math):"]
    try:
        rcv_od = param_cm(design, "rcv_od")
        slip_id_w = param_cm(design, "slip_id_w")
        slip_id_h = param_cm(design, "slip_id_h")
        box_od_w = param_cm(design, "box_od_w")
        box_od_h = param_cm(design, "box_od_h")
        clip_t = param_cm(design, "clip_t")
        rail_end = param_cm(design, "rail_end_x")
        rcv_front = param_cm(design, "rcv_front_x")
        rcv_rear = param_cm(design, "rcv_rear_x")
        clip_rear = param_cm(design, "clip_rear_x")
        bolt0 = param_cm(design, "rcv_bolt_first_x")
        bolt_d = param_cm(design, "rcv_bolt_d")
        pitch = param_cm(design, "rcv_bolt_pitch")
        n = _rcv_bolt_count(design)
        xm_x = param_cm(design, "rcv_xm_x")
        try:
            xm_t = param_cm(design, "rcv_xm_t")
        except Exception:
            xm_t = param_cm(design, "rcv_xm_w")
        key_w = param_cm(design, "rcv_key_w")
        overhang = param_cm(design, "rear_overhang")
        wb = param_cm(design, "wb")
        cap_aft = rail_end + clip_t

        # Width math: OD vs box — key tabs on OD with weld gap to plate.
        od_in = rcv_od / IN_TO_CM
        id_w_in = slip_id_w / IN_TO_CM
        id_h_in = slip_id_h / IN_TO_CM
        box_w_in = box_od_w / IN_TO_CM
        box_h_in = box_od_h / IN_TO_CM
        key_gap = (rcv_od / 2.0 - box_od_w / 2.0) / IN_TO_CM
        if rcv_od > slip_id_w + 1e-6 or rcv_od > slip_id_h + 1e-6:
            lines.append(
                "  rcv_od={:.3f} > slip_id {:.3f}x{:.3f} (box OD {:.3f}x{:.3f}) — "
                "side-plate window + RCV_KEY on OD (gap to plate outer "
                "{:.3f} in).".format(
                    od_in,
                    id_w_in,
                    id_h_in,
                    box_w_in,
                    box_h_in,
                    key_gap,
                )
            )
        else:
            lines.append(
                "  rcv_od={:.3f} fits slip_id {:.3f}x{:.3f} — interior key possible.".format(
                    od_in, id_w_in, id_h_in
                )
            )
        if key_gap < -1e-4:
            lines.append(
                "  WARN: key/plate Z gap={:.3f} in negative — tab intersects "
                "rail side-plate outer face.".format(key_gap)
            )
        else:
            lines.append(
                "  Key/plate Z gap={:.3f} in (rcv_od/2 − box_od_w/2; weld/shim).".format(
                    key_gap
                )
            )

        # X stations
        key_x0 = rcv_front - key_w
        lines.append(
            "  X stations (in): key_tab=[{:.3f},{:.3f}]  rcv_front={:.3f}  "
            "rail_end={:.3f}  cap_aft={:.3f}  "
            "rcv_rear=clip_rear={:.3f}  wb+rear_overhang={:.3f}".format(
                key_x0 / IN_TO_CM,
                rail_end / IN_TO_CM,
                rcv_front / IN_TO_CM,
                rail_end / IN_TO_CM,
                cap_aft / IN_TO_CM,
                rcv_rear / IN_TO_CM,
                (wb + overhang) / IN_TO_CM,
            )
        )
        if abs(clip_rear - rcv_rear) > 0.01 * IN_TO_CM:
            lines.append("  WARN: clip_rear_x != rcv_rear_x")
        if rail_end < rcv_front - 0.01 * IN_TO_CM:
            lines.append("  WARN: rail_end_x forward of rcv_front_x")
        if rail_end > rcv_rear + 0.01 * IN_TO_CM:
            lines.append(
                "  WARN: rail_end_x aft of rcv_rear_x — rails block receiver mouth"
            )
        else:
            lines.append(
                "  Slide path clear: end cap aft of rail_end_x; no rail plate "
                "aft of cap; receiver bore open rcv_rear → rcv_front."
            )

        # Bolts must clear the end-cap aft face and lie on the free tube.
        bolt_ok = True
        bolt_edge0 = bolt0 - bolt_d / 2.0
        if bolt_edge0 < cap_aft - 0.01 * IN_TO_CM:
            bolt_ok = False
            lines.append(
                "  WARN: first bolt hole edge X={:.3f} overlaps end cap "
                "[rail_end={:.3f}, cap_aft={:.3f}].".format(
                    bolt_edge0 / IN_TO_CM,
                    rail_end / IN_TO_CM,
                    cap_aft / IN_TO_CM,
                )
            )
        for i in range(n):
            bx = bolt0 + i * pitch
            if bx < cap_aft - 0.01 * IN_TO_CM or bx > rcv_rear + 0.01 * IN_TO_CM:
                bolt_ok = False
                lines.append(
                    "  WARN: bolt {} at X={:.3f} in outside free receiver "
                    "[cap_aft, rcv_rear].".format(i + 1, bx / IN_TO_CM)
                )
        if bolt_ok:
            lines.append(
                "  Cross-bolts OK: first={:.3f} in, count={}, pitch={:.3f} in "
                "(first hole edge ≥ cap_aft={:.3f}).".format(
                    bolt0 / IN_TO_CM,
                    n,
                    pitch / IN_TO_CM,
                    cap_aft / IN_TO_CM,
                )
            )

        # XM must sit on free tube clear of the end cap and bolt holes.
        xm0 = xm_x - xm_t / 2.0
        xm1 = xm_x + xm_t / 2.0
        xm_ok = True
        if xm_x < cap_aft - 0.01 * IN_TO_CM or xm_x > rcv_rear + 0.01 * IN_TO_CM:
            xm_ok = False
            lines.append(
                "  WARN: rcv_xm_x={:.3f} in not on free receiver tube "
                "[cap_aft, rcv_rear].".format(xm_x / IN_TO_CM)
            )
        if xm0 < cap_aft - 0.01 * IN_TO_CM and xm1 > rail_end - 0.01 * IN_TO_CM:
            xm_ok = False
            lines.append(
                "  WARN: XMEMBER_RCV X=[{:.3f},{:.3f}] overlaps end cap.".format(
                    xm0 / IN_TO_CM, xm1 / IN_TO_CM
                )
            )
        for i in range(n):
            bx = bolt0 + i * pitch
            b0 = bx - bolt_d / 2.0
            b1 = bx + bolt_d / 2.0
            if xm0 < b1 - 1e-6 and xm1 > b0 + 1e-6:
                xm_ok = False
                lines.append(
                    "  WARN: XMEMBER_RCV X=[{:.3f},{:.3f}] overlaps bolt {} "
                    "hole [{:.3f},{:.3f}].".format(
                        xm0 / IN_TO_CM,
                        xm1 / IN_TO_CM,
                        i + 1,
                        b0 / IN_TO_CM,
                        b1 / IN_TO_CM,
                    )
                )
        if xm_ok:
            lines.append(
                "  Receiver XM at X={:.3f} in (clear of end cap + bolt holes).".format(
                    xm_x / IN_TO_CM
                )
            )

        # Watts brackets are on rails near axle — flag if they landed aft of rail_end.
        try:
            wfx = param_cm(design, "watts_frame_x")
            if is_parallel_watts() and wfx > rail_end + 0.01 * IN_TO_CM:
                lines.append(
                    "  WARN: watts_frame_x={:.3f} aft of rail_end — "
                    "move bracket to receiver/XM.".format(wfx / IN_TO_CM)
                )
            elif is_parallel_watts():
                lines.append(
                    "  Watts frame bracket X={:.3f} in is on rail box "
                    "(forward of rail_end).".format(wfx / IN_TO_CM)
                )
        except Exception:
            pass
    except Exception as exc:
        lines.append("  Packaging check failed: {}".format(exc))
    return "\n".join(lines)


def try_receiver_interference_check(design):
    """Best-effort Fusion interference on rails / end caps / keys / receivers / XM."""
    names = (
        "RAIL_RH_OUTBOARD",
        "RAIL_RH_INBOARD",
        "RAIL_RH_TOP_TAIL",
        "RAIL_RH_BOT_TAIL",
        "RAIL_RH_END_CAP",
        "RAIL_LH_OUTBOARD",
        "RAIL_LH_INBOARD",
        "RAIL_LH_TOP_TAIL",
        "RAIL_LH_BOT_TAIL",
        "RAIL_LH_END_CAP",
        "RECEIVER_RH",
        "RECEIVER_LH",
        "XMEMBER_RCV",
        "RCV_KEY_RH_IN",
        "RCV_KEY_RH_OUT",
        "RCV_KEY_LH_IN",
        "RCV_KEY_LH_OUT",
    )
    try:
        bodies_by_name = {}
        _collect_bodies(design.rootComponent, bodies_by_name)
        coll = adsk.core.ObjectCollection.create()
        found = []
        for name in names:
            entry = bodies_by_name.get(name)
            if entry:
                coll.add(entry[0])
                found.append(name)
        if coll.count < 2:
            return "Fusion interference: skipped (found {} of {} bodies).".format(
                coll.count, len(names)
            )
        if not hasattr(design, "createInterferenceInput"):
            return (
                "Fusion interference: API unavailable — rely on math packaging check "
                "({} bodies considered).".format(coll.count)
            )
        iin = design.createInterferenceInput(coll)
        results = design.analyzeInterference(iin)
        n = results.count if results else 0
        note = "OK" if n == 0 else "REVIEW"
        msg = (
            "Fusion interference (rails/end caps/receivers/keys/XM): "
            "{} set(s) — {} ({} bodies).".format(n, note, coll.count)
        )
        if n > 0 and results:
            pairs = []
            for i in range(min(n, 5)):
                r = results.item(i)
                try:
                    a = r.entityOne.name
                except Exception:
                    a = "?"
                try:
                    b = r.entityTwo.name
                except Exception:
                    b = "?"
                pairs.append("{}×{}".format(a, b))
            msg += " Offenders: {}.".format("; ".join(pairs))
        return msg
    except Exception as exc:
        return "Fusion interference: skipped ({})".format(exc)


def bump_clearance_report(design):
    """Min gap (in) between over-axle XM underside and housing/CS at bump.

    Returns (gap_inches, note). Positive = clearance; negative = interference.
    """
    xm_under = _over_axle_underside_y(design)
    ay = param_cm(design, "axle_cl_y")
    travel = param_cm(design, "axle_travel_up")
    csh = param_cm(design, "cs_height")
    tube_od = param_cm(design, "axle_tube_od")
    # Highest housing feature under the XM (CS box or axle tube).
    house_top_ride = ay + max(csh / 2.0, tube_od / 2.0)
    house_top_bump = house_top_ride + travel
    gap_cm = xm_under - house_top_bump
    gap_in = gap_cm / IN_TO_CM
    if gap_in >= 0.25:
        note = "OK (≥0.25 in)"
    elif gap_in >= 0.0:
        note = "TIGHT (<0.25 in)"
    else:
        note = "INTERFERENCE (negative gap)"
    return gap_in, note


def _rail_outboard_outer_z(design):
    """|Z| of rail outboard outer face from frame CL (cm)."""
    return (
        param_cm(design, "rail_cl")
        + param_cm(design, "tube_w") / 2.0
        + param_cm(design, "clip_clear")
        + param_cm(design, "clip_t")
    )


def _rail_inboard_outer_z(design):
    """|Z| of rail inboard outer face from frame CL (cm)."""
    return (
        param_cm(design, "rail_cl")
        - param_cm(design, "tube_w") / 2.0
        - param_cm(design, "clip_clear")
        - param_cm(design, "clip_t")
    )


def _rail_bottom_y_at_x(design, x):
    """Outer-ish rail bottom height (cm) at station X from kickup polyline."""
    pts = _kickup_world_points(design, top=False)
    if not pts:
        return param_cm(design, "rail_bottom")
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if x0 <= x <= x1 or x1 <= x <= x0:
            if abs(x1 - x0) < 1e-9:
                return y0
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pts[-1][1]


def _upper_link_z_at_x(design, x):
    """Interpolate upper-link |Z| (cm) at station X along the RH bar path."""
    frame_pt, axle_pt = _link_pickup_pair(design, 1.0, upper=True)
    dx = axle_pt.x - frame_pt.x
    if abs(dx) < 1e-9:
        return abs(frame_pt.z)
    t = (x - frame_pt.x) / dx
    t = max(0.0, min(1.0, t))
    return abs(frame_pt.z + t * (axle_pt.z - frame_pt.z))


def _clearance_note(gap_in, ok=0.25):
    if gap_in >= ok:
        return "OK"
    if gap_in >= 0.0:
        return "TIGHT"
    return "INTERFERENCE"


def _min_bar_to_rail_gap(design, axle_y_delta):
    """Min gap (in) lower-bar OD to rail: lateral outboard face + vertical bottom.

    Samples the RH lower bar at the given axle height shift (bump/droop).
    """
    frame_pt, axle_pt = _link_pickup_pair(
        design, 1.0, upper=False, axle_y_delta=axle_y_delta
    )
    bar_r = param_cm(design, "link_bar_od") / 2.0
    z_out = _rail_outboard_outer_z(design)
    samples = 12
    min_lat = None
    min_vert = None
    for i in range(samples + 1):
        t = float(i) / float(samples)
        p = _point_lerp(frame_pt, axle_pt, t)
        # Lateral: bar is outboard of rail — gap = |z_bar| - rail_out - bar_r
        lat = abs(p.z) - z_out - bar_r
        # Vertical: bar above rail bottom outline — gap = y_bar - rail_bot - bar_r
        rail_bot = _rail_bottom_y_at_x(design, p.x)
        vert = p.y - rail_bot - bar_r
        min_lat = lat if min_lat is None else min(min_lat, lat)
        min_vert = vert if min_vert is None else min(min_vert, vert)
    # Report the tighter of lateral vs vertical approach.
    min_cm = min(min_lat, min_vert)
    return min_cm / IN_TO_CM, min_lat / IN_TO_CM, min_vert / IN_TO_CM


def layout_clearance_report(design):
    """REV-B runtime clearance summary (inches) for the run dialog."""
    bag_y = param_cm(design, "bag_y")
    bag_r = param_cm(design, "bag_diameter") / 2.0
    bar_r = param_cm(design, "link_bar_od") / 2.0
    rail_in = _rail_inboard_outer_z(design)
    mount_x = param_cm(design, "wb") + param_cm(design, "mount_x_off")
    upper_z = _upper_link_z_at_x(design, mount_x)

    # Bag sits inboard of rail inboard face, outboard of upper-link path.
    gap_bag_rail = (rail_in - (bag_y + bag_r)) / IN_TO_CM
    parallel = is_parallel_watts()
    if parallel:
        # Uppers are outboard with lowers — bag-to-upper-link N/A (not in bay).
        gap_bag_upper = None
    else:
        gap_bag_upper = ((bag_y - bag_r) - (upper_z + bar_r)) / IN_TO_CM

    bump = param_cm(design, "axle_travel_up")
    droop = param_cm(design, "axle_travel_down")
    gap_bump, _, _ = _min_bar_to_rail_gap(design, bump)
    gap_droop, _, _ = _min_bar_to_rail_gap(design, -droop)
    gap_ride, _, _ = _min_bar_to_rail_gap(design, 0.0)

    lines = [
        "REV-B clearance checks (min gap, in):",
        "  bag-to-rail (inboard face):     {:.3f} — {}".format(
            gap_bag_rail, _clearance_note(gap_bag_rail)
        ),
    ]
    if gap_bag_upper is None:
        lines.append("  bag-to-upper-link:               N/A (parallel_watts uppers outboard)")
    else:
        lines.append(
            "  bag-to-upper-link (at mount X): {:.3f} — {}".format(
                gap_bag_upper, _clearance_note(gap_bag_upper)
            )
        )
    lines.extend(
        [
            "  lower-bar-to-rail @ ride:       {:.3f} — {}".format(
                gap_ride, _clearance_note(gap_ride)
            ),
            "  lower-bar-to-rail @ full bump:  {:.3f} — {}".format(
                gap_bump, _clearance_note(gap_bump)
            ),
            "  lower-bar-to-rail @ full droop: {:.3f} — {}".format(
                gap_droop, _clearance_note(gap_droop)
            ),
            "  (bag_diameter={:.3f} in PLACEHOLDER; bag_y={:.3f}; shock_y={:.3f}; "
            "lower_link_y={:.3f})".format(
                param_cm(design, "bag_diameter") / IN_TO_CM,
                bag_y / IN_TO_CM,
                param_cm(design, "shock_y") / IN_TO_CM,
                param_cm(design, "lower_link_y") / IN_TO_CM,
            ),
        ]
    )
    if parallel:
        lines.append(watts_clearance_report(design))
    return "\n".join(lines)


def _aabb_gap(a_min, a_max, b_min, b_max):
    """Positive gap between 1D intervals; negative = overlap depth."""
    if a_max < b_min:
        return b_min - a_max
    if b_max < a_min:
        return a_min - b_max
    return -min(a_max, b_max) + max(a_min, b_min)


def _watts_sweep_points(design):
    """Sample Watts crank tips + link midpoints at ride / bump / droop (cm)."""
    bump = param_cm(design, "axle_travel_up")
    droop = param_cm(design, "axle_travel_down")
    pts = []
    for delta in (0.0, bump, -droop):
        pivot = _watts_pivot_point(design, delta)
        pts.append(pivot)
        for sign in (1.0, -1.0):
            tip = _watts_crank_tip(design, sign, delta)
            frame = _watts_frame_pickup(design, sign)
            pts.append(tip)
            pts.append(frame)
            pts.append(_point_lerp(tip, frame, 0.5))
            # Link OD envelope: nudge tip/frame mid ± half OD in Y
            link_r = param_cm(design, "watts_link_od") / 2.0
            mid = _point_lerp(tip, frame, 0.5)
            pts.append(adsk.core.Point3D.create(mid.x, mid.y + link_r, mid.z))
            pts.append(adsk.core.Point3D.create(mid.x, mid.y - link_r, mid.z))
        # Crank arm width envelope at tip Z
        arm = param_cm(design, "watts_crank_arm_w") / 2.0
        crank = param_cm(design, "watts_crank_len")
        pts.append(adsk.core.Point3D.create(pivot.x, pivot.y + arm, pivot.z + crank))
        pts.append(adsk.core.Point3D.create(pivot.x, pivot.y - arm, pivot.z + crank))
        pts.append(adsk.core.Point3D.create(pivot.x, pivot.y + arm, pivot.z - crank))
        pts.append(adsk.core.Point3D.create(pivot.x, pivot.y - arm, pivot.z - crank))
    return pts


def watts_clearance_report(design):
    """Watts crank/links vs utility-module fuel tank + rear XM at bump/droop."""
    pts = _watts_sweep_points(design)
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    w_xmin, w_xmax = min(xs), max(xs)
    w_ymin, w_ymax = min(ys), max(ys)
    w_zmin, w_zmax = min(zs), max(zs)

    # Utility-module fuel tank AABB (mirrored PLACEHOLDER envelope).
    fx0 = param_cm(design, "um_fuel_x")
    fy0 = param_cm(design, "um_fuel_y")
    fl = param_cm(design, "um_fuel_l")
    fw = param_cm(design, "um_fuel_w")
    fh = param_cm(design, "um_fuel_h")
    t_xmin, t_xmax = fx0, fx0 + fl
    t_ymin, t_ymax = fy0, fy0 + fh
    t_zmin, t_zmax = -fw / 2.0, fw / 2.0

    gap_x = _aabb_gap(w_xmin, w_xmax, t_xmin, t_xmax)
    gap_y = _aabb_gap(w_ymin, w_ymax, t_ymin, t_ymax)
    gap_z = _aabb_gap(w_zmin, w_zmax, t_zmin, t_zmax)
    # Separating-axis: if any axis has positive gap, AABBs are separate;
    # report the minimum positive sep, or most negative overlap if intersecting.
    if gap_x > 0 or gap_y > 0 or gap_z > 0:
        tank_gap = min(g for g in (gap_x, gap_y, gap_z) if g > 0)
    else:
        tank_gap = min(gap_x, gap_y, gap_z)  # overlapping — most negative axis
    tank_gap_in = tank_gap / IN_TO_CM

    # Rear receiver crossmember AABB.
    xm_x = param_cm(design, "rcv_xm_x")
    try:
        xm_t = param_cm(design, "rcv_xm_t")
    except Exception:
        xm_t = param_cm(design, "rcv_xm_w")
    xm_h = param_cm(design, "rcv_xm_h")
    xm_cy = param_cm(design, "rcv_cl_y")
    z_rh = _rail_inboard_inner_z(design, 1.0)
    z_lh = _rail_inboard_inner_z(design, -1.0)
    r_xmin, r_xmax = xm_x - xm_t / 2.0, xm_x + xm_t / 2.0
    r_ymin, r_ymax = xm_cy - xm_h / 2.0, xm_cy + xm_h / 2.0
    r_zmin, r_zmax = min(z_lh, z_rh), max(z_lh, z_rh)

    rgx = _aabb_gap(w_xmin, w_xmax, r_xmin, r_xmax)
    rgy = _aabb_gap(w_ymin, w_ymax, r_ymin, r_ymax)
    rgz = _aabb_gap(w_zmin, w_zmax, r_zmin, r_zmax)
    if rgx > 0 or rgy > 0 or rgz > 0:
        rcv_gap = min(g for g in (rgx, rgy, rgz) if g > 0)
    else:
        rcv_gap = min(rgx, rgy, rgz)
    rcv_gap_in = rcv_gap / IN_TO_CM

    return (
        "Watts clearance (AABB sweep ride/bump/droop, in):\n"
        "  watts vs utility fuel tank:    {:.3f} — {} "
        "(um_fuel_* PLACEHOLDER mirrors UtilityModule)\n"
        "  watts vs rear XM (XMEMBER_RCV): {:.3f} — {}\n"
        "  (watts_pivot_y={:.3f}; watts_crank_len={:.3f}; "
        "axle_travel_up/down={:.3f}/{:.3f})".format(
            tank_gap_in,
            _clearance_note(tank_gap_in),
            rcv_gap_in,
            _clearance_note(rcv_gap_in),
            param_cm(design, "watts_pivot_y") / IN_TO_CM,
            param_cm(design, "watts_crank_len") / IN_TO_CM,
            param_cm(design, "axle_travel_up") / IN_TO_CM,
            param_cm(design, "axle_travel_down") / IN_TO_CM,
        )
    )


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
