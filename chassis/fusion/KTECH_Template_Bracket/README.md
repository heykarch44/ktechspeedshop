# KTECH_Template_Bracket

Fusion 360 Python script that builds a parametric **3/16 in laser / waterjet plate** traced from a paper template: a boot / bottle-opener outline, a rounded left tab with one **1/2 in** hole, and two **5/8 in** holes in the wide end. Running the script exports a flat DXF of the face to `dxf_out/` next to the script.

This is a **standalone flat pattern**. Sketch origin is the far left of the rounded tab at X = 0, the straight bottom edge on Y = 0, wide end to the +X. Thickness extrudes in +Z. It is not placed in chassis coordinates.

## How to run in Fusion

1. Copy this whole folder to the Fusion scripts directory, or add it in place:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_Template_Bracket`
2. Fusion → **Utilities** → **Scripts and Add-Ins**
3. Next to **My Scripts**, click **+** and select the `KTECH_Template_Bracket` folder
4. Preferences → Design → Default design type → **Hybrid**
5. **File → New Design**, then **Run** `KTECH_Template_Bracket`
6. Fit view if needed; save as `KTECH_TEMPLATE_BRACKET`

Edit numbers in **Modify → Change Parameters** (or in `KTECH_Template_Bracket_parameters.csv` before run). Hole diameters and `plate_t` are fully parametric in the document. Outline spline / tab-angle changes pick up on a **New Design** and re-run.

## What it builds

| Component | Contents |
|---|---|
| `01_TEMPLATE_BRACKET` | `TEMPLATE_BRACKET` body: sketched profile, extruded `plate_t`, three through holes |

Plate DXF → `dxf_out/TEMPLATE_BRACKET.dxf` next to the script. Cut from the DXF; do not scale the preview PNG.

## Source of the numbers

The user photographed a paper template with a tape in frame and specified **3/16 in** plate, two **5/8 in** holes, and one **1/2 in** hole.

| Item | Default | Status |
|---|---|---|
| `plate_t` | 0.1875 in | Specified (3/16) |
| `hole_half_d` | 0.500 in | Specified (1/2) |
| `hole_58_d` | 0.625 in | Specified (5/8) |
| Overall length, heights, tab, hole locations, blend handles | see CSV | **PHOTO EST. ±1/8 in** — caliper the paper (or a first article) and update the named parameters before a production cut |

Kerf is **not** compensated; the shop should apply their kerf to finished sizes.

## Parameter list

Full table: **`KTECH_Template_Bracket_parameters.csv`**.

### Quick reference

| Param | Default | Notes |
|---|---|---|
| `plate_t` | 0.1875 in | 3/16 in plate |
| `overall_length` | 4.90 in | PHOTO EST. left tip to right end |
| `wide_end_height` | 2.40 in | PHOTO EST. right end height |
| `corner_r` | 0.06 in | PHOTO EST. right-end corner radius |
| `tab_r` / `tab_cx` / `tab_cy` | 0.875 / 0.875 / 2.00 in | PHOTO EST. left ear circle |
| `tab_arc_start_deg` / `tab_arc_end_deg` | 240 / 80 | PHOTO EST. ear sweep, deg from +X; travel is clockwise |
| `bottom_blend_x` / `bottom_handle` | 1.50 / 0.80 in | PHOTO EST. bottom Bezier into the ear |
| `top_straight_x` / `top_handle` | 4.00 / 1.00 in | PHOTO EST. top S-curve onto the wide end |
| `hole_half_d` / `hole_half_x` / `hole_half_y` | 0.500 / 0.90 / 2.15 in | 1/2 in hole; location PHOTO EST. |
| `hole_58_d` / `hole_58_y` / `hole_58_left_x` / `hole_58_spacing` | 0.625 / 1.05 / 2.80 / 1.0625 in | two 5/8 in holes; location PHOTO EST. |
| `hole_58_right_x` | `hole_58_left_x + hole_58_spacing` | Computed |
| `tab_top_y` | `tab_cy + tab_r` | Computed (2.875 in at defaults) |

## Open items

- Caliper the paper template (or a coupon cut) and replace every **PHOTO EST.** value
- Confirm material (steel vs aluminum) and shop kerf with the cutter
- Re-export the DXF after the numbers are frozen

## Related

- Rear clip plate export pattern: `../KTECH_C10_RearClip/`
- Utility module plates: `../KTECH_C10_UtilityModule/`
