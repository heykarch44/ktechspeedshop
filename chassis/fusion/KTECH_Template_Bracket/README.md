# KTECH_Template_Bracket

Fusion 360 Python script that builds a parametric **3/16 in laser / waterjet plate**: a **kicked-out gooseneck tab** with one **1/2 in** hole, and two **21/32 in** clearance holes (for **5/8** bolts) in the wide end, at **1.000 in** centers measured from the mating bracket. Running the script exports a flat DXF of the face to `dxf_out/` next to the script.

This is a **standalone flat pattern**. Sketch origin is the far left of the rounded tab at X = 0, the straight bottom edge on Y = 0, wide end to the +X. Thickness extrudes in +Z. It is not placed in chassis coordinates.

Body-frame parameters (`*_body`) match the 1:1 print the user sketched on (old X = 0 was the original tab left). `origin_shift_x = tab_r - tab_cx_body` re-zeros the flat pattern so the left ear tip is X = 0; the 21/32 pair and the wide end shift together, so their relative geometry does not change.

## How to run in Fusion

1. Copy this whole folder to the Fusion scripts directory, or add it in place:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_Template_Bracket`
2. Fusion → **Utilities** → **Scripts and Add-Ins**
3. Next to **My Scripts**, click **+** and select the `KTECH_Template_Bracket` folder
4. Preferences → Design → Default design type → **Hybrid**
5. **File → New Design**, then **Run** `KTECH_Template_Bracket`
6. Fit view if needed; save as `KTECH_TEMPLATE_BRACKET`

Edit numbers in **Modify → Change Parameters** (or in `KTECH_Template_Bracket_parameters.csv` before run). To kick the tab further, change `hole_half_x_body`, `hole_half_y`, and/or `tab_r`, then **New Design** and re-run (outline splines pick up on re-run). Hole diameters, C-C, and `plate_t` are fully parametric in the document.

## What it builds

| Component | Contents |
|---|---|
| `01_TEMPLATE_BRACKET` | `TEMPLATE_BRACKET` body: sketched profile, extruded `plate_t`, three through holes |

Plate DXF → `dxf_out/TEMPLATE_BRACKET.dxf` next to the script. Cut from the DXF, or print the 1:1 letter PDF at 100% / Actual size; do not scale the preview PNG.

## Source of the numbers

The user photographed a paper template, then printed a 1:1 PDF and sketched “kick out more” in pencil. The 1/2 in hole moves from body (0.90, 2.15) to about **(0.10, 3.60)**, with the same **0.875 in** ear centered on the hole. The two large holes were sized from a caliper check of the **mating** bracket: 0.66 in dia, 0.322 in edge-to-edge, 1.666 in outside-to-outside → **1.000 in** centers, cut as **21/32 in** (0.65625) clearance for 5/8 bolts. The pair and the 2.40 in wide end stay fixed relative to each other. The lower-left outline is one full convex cubic from the ear (near 182°) down and gently right, staying near X 0–0.3 through Y~2, then tangent into the straight bottom at X 1.85 (flat-pattern frame).

| Item | Default | Status |
|---|---|---|
| `plate_t` | 0.1875 in | Specified (3/16) |
| `hole_half_d` | 0.500 in | Specified (1/2) |
| `hole_half_x_body` / `hole_half_y` | 0.10 / 3.60 in | **SKETCH EST.** from pencil on the 1:1 print |
| `tab_r` / `tab_cx_body` / `tab_cy` | 0.875 / `hole_half_x_body` / `hole_half_y` | **SKETCH EST.** ear around the 1/2 in hole |
| `hole_58_d` | 0.65625 in | **MEASURED** mate ~0.66 in; 21/32 clearance for 5/8 bolt |
| `hole_58_spacing` | 1.000 in | **MEASURED** from mating-bracket C-C |
| `hole_58_mid_x_body` / `hole_58_y` | 3.33125 / 1.05 in | mid X held from the original photo-trace pair (body frame); Y PHOTO EST. |
| Lower convex / upper concave blends, wide-end height / corners | see CSV | **SKETCH/PHOTO EST.** |

Kerf is **not** compensated; the shop should apply their kerf to finished sizes.

## Parameter list

Full table: **`KTECH_Template_Bracket_parameters.csv`**.

### Quick reference

| Param | Default | Notes |
|---|---|---|
| `hole_half_x_body` / `hole_half_y` | 0.10 / 3.60 in | SKETCH EST. 1/2 in hole in the body / print frame |
| `tab_r` | 0.875 in | SKETCH EST. ear radius (centered on the hole) |
| `origin_shift_x` | `tab_r - tab_cx_body` | Computed (0.775 in at defaults) |
| `hole_half_x` / `tab_cx` | body + shift | Computed flat-pattern (0.875 / 0.875 in) |
| `overall_length` | `wide_end_right_body + origin_shift_x` | Computed (5.675 in) |
| `hole_58_d` | 0.65625 in | MEASURED mate ~0.66; 21/32 clearance for 5/8 bolt |
| `hole_58_spacing` | 1.000 in | MEASURED C-C from mating bracket |
| `hole_58_mid_x_body` / `hole_58_y` | 3.33125 / 1.05 in | body mid held from original pair; Y PHOTO EST. |
| `hole_58_mid_x` / left / right | mid_body + shift ± spacing/2 | Computed (4.10625 / 3.60625 / 4.60625 in) |
| `bottom_blend_x` | 1.85 in | SKETCH EST. flat-pattern X; lower convex sweep meets Y=0 here |
| `bottom_handle` / `bottom_handle_ear` | 0.80 / 2.40 in | SKETCH EST. lower-sweep Bezier handles (floor / ear) |
| `top_straight_x_body` | 2.85 in | SKETCH EST. upper concave curve meets the wide-end top (body frame) |
| `tab_arc_start_deg` / `tab_arc_end_deg` | 182 / 90 | SKETCH EST. ear sweep, deg from +X; travel is clockwise; lower sweep meets the ear near the left tip |
| `tab_top_y` | `tab_cy + tab_r` | Computed (4.475 in at defaults) |

## Open items

- Caliper the paper template outline (and the sketched 1/2 in hole / ear) and replace every remaining **SKETCH/PHOTO EST.** value; bolt-hole diameter and C-C are already measured from the mate
- Confirm material (steel vs aluminum) and shop kerf with the cutter
- Re-export the DXF after the numbers are frozen

## Related

- Rear clip plate export pattern: `../KTECH_C10_RearClip/`
- Utility module plates: `../KTECH_C10_UtilityModule/`
