# KTECH_C10_RearClip

Fusion 360 Python script that builds a parametric **73–87 C10 shortbed** rear clip (first prototype): purchased 2×6 center-tube reference, four-piece laser plate box rails with slip-fit and tab-and-slot keys, triangulated 4-link bracket plates, Currie 9-inch axle mockup, bag **or** coilover upper mounts, and flat DXF export per plate.

Owner design intent for this script **overrides** the older open-C socket notes in `../DESIGN.md`: the rear clip is a **closed four-piece box** that slip-fits over the A500 tube for length adjustment, then welds.

## How to run in Fusion

1. Copy this whole folder to the Fusion scripts directory, or add it in place:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_C10_RearClip`
2. Fusion → **Utilities** → **Scripts and Add-Ins**
3. Next to **My Scripts**, click **+** and select the `KTECH_C10_RearClip` folder
4. Preferences → Design → Default design type → **Hybrid** (chassis is Hybrid, not Part)
5. **File → New Design**, then **Run** `KTECH_C10_RearClip`
6. Fit view if the canvas looks empty (rails sit at `rail_cl` ≈ 16.75" off centerline)
7. Save as `KTECH_C10_REAR_CLIP`

Edit numbers in **Modify → Change Parameters** (or in `rear_clip_parameters.csv` before run). Geometry is generated at run time from those values — after big layout changes, use a **New Design** and run again (same rule as `KTECH_C10_Chassis_Setup`).

Coordinates match the chassis setup script: origin = front axle × ground × frame CL; **+X rear, +Y up, +Z passenger**.

## What it builds

| Component | Contents |
|---|---|
| `00_ORIGIN` | 6" marker cube |
| `00_SKELETON` | SK_SIDE, SK_TOP, SK_KICKUP_REF |
| `01_CENTER_TUBE` | Semi-transparent **reference** A500 2×6 through the slip region only — not plate |
| `02_RAIL_RH` / `02_RAIL_LH` | Top / bottom / inboard / outboard plates, tabs, slots, bracket key pockets |
| `03_CROSSMEMBERS` | Upper 4-link crossmember plate |
| `04_FOUR_LINK` | Frame-side upper & lower bracket plates + link construction refs |
| `05_AXLE_REF` | Parametric Currie 9" mockup (CS box + tubes + WMS markers) |
| `06_BAG_SHOCK` | Airbag **or** coilover upper mount plates (`suspension_mode`) |
| `07_FIXTURE` | Placeholder; DXF sketches land here when possible |

Plate DXFs are written to `dxf_out/` next to the script (top-face profile sketch per named plate body).

## Generation switch (73–87 vs 67–72)

Prototype defaults to **73–87 short**:

- `wb_73_87_short` = 117.5 in  
- `wb_67_72_short` = 115.0 in  
- `wb` = `wb_73_87_short`

For 67–72 short, set the `wb` expression to `wb_67_72_short` in User Parameters (or in the CSV) and re-run on a new design. Cab hats stay generation-specific elsewhere; wheelbase lives on the rear clip.

## Slip-fit box rail

- Inside: `slip_id_w` / `slip_id_h` = tube OD + `2 * clip_clear` (default clear **0.030 in/side**)
- Overlap: `slip_overlap` default **8 in**
- Plate: `clip_t` default **0.188 in**
- Four flats per side: top, bottom, inboard, outboard; side webs carry the kickup profile
- Tab-and-slot: `tab_width`, `tab_length` (= `clip_t`), `slot_clear`, `tab_pitch`
- Bracket key pockets in the outboard plates so rails act as the fixture for link brackets

## Suspension

- Triangulated 4-link: frame upper/lower bracket plates + upper crossmember
- `suspension_mode` = **1** → airbag upper mount plates; **0** → coilover upper mount plates
- Axle: Currie 9-inch mockup — WMS width `axle_wms_a` (default 63.625), brake space 2.500 Torino late big bearing, housing `B = A - 2*brake_space`, tubes 3.00 × 0.188, pinion offset 0.94 toward passenger

## Parameter list

Full table with expressions and notes: **`rear_clip_parameters.csv`**.

Shared names reused from `KTECH_C10_Chassis_Setup` where they apply (`tube_w`, `tube_h`, `wall`, `rail_bottom`, `wb`, `rail_cl`, `core_*`, `cab_*`, `clip_t`, `clip_clear`, `tire_od`, `bag_stroke`, …).

Anything invented for layout and not yet taped or vendor-confirmed is marked **PLACEHOLDER** (or **PLACEHOLDER UNVERIFIED** for Currie CS dims) in the CSV `comment` column.

### Quick reference — layout & slip

| Param | Default | Notes |
|---|---|---|
| `wb` | `wb_73_87_short` | Active wheelbase |
| `slip_overlap` | 8 in | Box over tube |
| `clip_clear` | 0.030 in | Per side |
| `clip_t` | 0.188 in | Plate thickness |
| `splice_aft` | 3 in | PLACEHOLDER — split aft of `cab_r` |
| `kickup_*` | various | PLACEHOLDER — rise/ramps over axle |
| `suspension_mode` | 1 | 1=bag, 0=coilover |
| `axle_wms_a` | 63.625 in | Set from wheel/tire combo |
| `cs_width` / `cs_height` / `cs_depth` / `tube_insert` | — | PLACEHOLDER UNVERIFIED — Currie |

## Open items

- **Currie 9-inch CAD** requested **2026-11-15** — replace `cs_width`, `cs_height`, `cs_depth`, `tube_insert` placeholders
- **Wilwood CAD** requested **2026-11-15** — front/related; rear brake package still TBD against WMS / housing ends
- Freeze `slot_clear` with a laser coupon
- Tape / fixture: confirm `splice_aft`, kickup envelope vs 32" tire + bag stroke, and 4-link pickup coordinates
- FEA splice, upper xmember, and 4-link brackets before kits leave the shop

## Related

- Chassis spine / mounts: `../KTECH_C10_Chassis_Setup/`
- Architecture notes: `../DESIGN.md`, `../C10-FRAME-GEOMETRY.md` (slip-fit **box** here supersedes C-socket wording for the rear clip)
