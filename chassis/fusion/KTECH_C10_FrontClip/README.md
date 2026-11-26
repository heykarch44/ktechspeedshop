# KTECH_C10_FrontClip

Fusion 360 Python script that builds a parametric **front clip** for the Ktech C10 chassis: four-piece laser plate box rails with a narrowed **28 × 4 in** nose, single **23° / 7 in** plan-view kick, flat **6 in / 34 in OD** rail through steering and A-arms, angular **6.57 in** drop into the cab section, and a keyed slip over the purchased **2×5** center tube.

**FLAG:** the purchased center spine was specified as **2×6** and is now **2×5** (`cab_rail_h = 5`). FrontClip aft slip (`slip_id_h`) is sized to the 2×5. RearClip still uses `tube_h = 6` in this pass — temporary mismatch until a follow-up.

## How to run

1. Prefer: open the chassis doc from `KTECH_C10_Chassis_Setup` (has empty `02_CLIP_FRONT`), **or** File → New Design
2. Fusion → **Utilities** → **Scripts and Add-Ins** → **+** → select this folder
3. Preferences → Design → Default design type → **Hybrid**
4. **Run** `KTECH_C10_FrontClip`
5. Fit view (rails sit at `rail_cl = 16.0` / nose at `rail_cl_nose = 13.0`)
6. Save as `KTECH_C10_FRONT_CLIP` (or keep on the chassis doc)

Edit numbers in **Modify → Change Parameters** or in `parameters.csv` before run. After big layout changes, New Design + re-run.

Coordinates match Chassis_Setup: origin = front axle × ground × frame CL; **+X rear, +Y up, +Z passenger**.

## Key defaults (2026-11-25 box sketches)

| Item | Value |
|---|---|
| `rail_cl` | **16.0** → 34 in OD through arms/engine (uncoupled from `core_width`) |
| `rail_cl_nose` | **13.0** → 28 in OD nose |
| `front_rail_bottom` / `front_rail_h` | **10.07** / **6** (flat, no arch) → top 16.07 |
| `nose_rail_h` | **4** (bottom level with front; top ramps 2 in over kick) |
| Kick | **23°**, **7 in**, **3 in** inset/side; constant `box_od_w` ≈ 2.44 |
| Drop | **6.57** over **12 in**, `x = 8` → `20`, finished before `cab_f_x = 22` |
| Cab / slip | `cab_rail_bottom = 3.5`, `cab_rail_h = 5` (2×5) |
| LCA pivot | **(13.50, 8.07)** — 2.00 hang below rail |
| UCA pivot | **(15.50, 17.88)** — ~1.81 tower above rail top |
| Core pads | **2.75** outboard of 28 in nose; `core_width = 33.5` C-C |
| `core_x` | **−33** PLACEHOLDER |

Ride notes (comments / FrontGeometry): design cab 3.5 / front 10.07–16.07; laid out frame −3.5; aired cab 7.

## What is solid vs sketched

| Built as solid | Layout / construction |
|---|---|
| Four-piece plate box RH/LH (nose, kick facet, raised straight, drop, cab slip) | `SK_SIDE`, `SK_TOP`, `SK_FRONT` |
| Ribs at kick bend lines | Pivot construction points `LCA_*` / `UCA_*` |
| Core-support pads | Pivot stub solids (hanging LCA + UCA tower) |
| Center-tube slip reference (2×5) | Tab-and-slot full pitch along every edge (stubs only on slip) |

Not in this pass: full laser tab schedule on every long edge, rack/crossmember solids, A-arm solids, DXF export.

## Related

- Chassis spine / mounts: `../KTECH_C10_Chassis_Setup/`
- Front-view geometry: `../KTECH_C10_FrontGeometry/`
- Rear clip (slip still 2×6 until follow-up): `../KTECH_C10_RearClip/`
- Notes: `../C10-FRAME-GEOMETRY.md`, `../DESIGN.md`
