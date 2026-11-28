# KTECH_C10_FrontClip

Fusion 360 Python script that builds a parametric **front clip** for the Ktech C10 chassis: four-piece laser plate box rails with a narrowed **28 × 4 in** nose, single **23° / 7 in** plan-view kick, flat **5 in / 34 in OD** rail through steering and A-arms, angular **6.57 in** drop into the cab section, and a keyed slip over the purchased **2×5** center tube.

## How to run

1. Prefer: open the chassis doc from `KTECH_C10_Chassis_Setup` (has empty `02_CLIP_FRONT`), **or** File → New Design
2. Fusion → **Utilities** → **Scripts and Add-Ins** → **+** → select this folder
3. Preferences → Design → Default design type → **Hybrid**
4. **Run** `KTECH_C10_FrontClip`
5. Fit view (rails sit at `rail_cl = 16.0` / nose at `rail_cl_nose = 13.0`)
6. Save as `KTECH_C10_FRONT_CLIP` (or keep on the chassis doc)

Edit numbers in **Modify → Change Parameters** or in `parameters.csv` before run. After big layout changes, New Design + re-run.

Coordinates match Chassis_Setup: origin = **STOCK** front hub × ground × frame CL; **+X rear, +Y up, +Z passenger**. Design front hub at `front_axle_x` (= `−front_axle_forward`, default **−1.0**) — pickups translate; rails/drop/nose/core stay.

## Key defaults (rail heights)

| Item | Value |
|---|---|
| `rail_cl` | **16.0** → 34 in OD through arms/engine (uncoupled from `core_width`) |
| `rail_cl_nose` | **13.0** → 28 in OD nose |
| `front_rail_bottom` / `front_rail_h` | **10.07** / **5** (flat, no arch; was 6) → top **15.07** — **unchanged at A-arms** |
| `nose_rail_h` / `nose_bottom` / `nose_top` | **4** / **6.07** / **10.07** (vs stock core bottom 9.00 = **−2.93**) |
| Nose elev | Top drop **5 in** ≈ **35.5°**; bottom drop **4 in** ≈ **29.7°** over 7 in kick (was 1 in top / level bottom) |
| Kick | **23°**, **7 in**, **3 in** inset/side; constant `box_od_w` ≈ 2.44 |
| Drop | **6.57** top **and** bottom over **12 in**, `x = 8` → `20`, finished **9.5 in** before `cab_f_x = 29.5` |
| Cab / slip | `cab_rail_bottom = 3.5`, `cab_rail_h = 5` (2×5) — matches rear slip |
| LCA pivot | **(13.50, 8.07)** Y/Z LOCKED — 2.00 hang; X at `front_axle_x` |
| UCA pivot | **(15.50, 17.88)** Y/Z LOCKED — ~**2.81** tower; X at `front_axle_x` |
| Core pads | **2.75** outboard of 28 in nose; `core_width = 33.5` C-C |
| `wb_stock` / `cab_f_x` / `core_x` | **116.5** / **29.5** / **−25** literal (2026-11-27 tapes) |
| Tire FLAG | Chassis/RearClip lay-out **27.5** (275/35/20); FrontGeometry still locked **29** on 22×9 — do not alter that package |

Ride notes (comments / FrontGeometry): design cab 3.5 / front 10.07–15.07; laid out frame −3.5; aired cab 7.

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
- Rear clip (2×5 slip): `../KTECH_C10_RearClip/`
- Notes: `../C10-FRAME-GEOMETRY.md`, `../DESIGN.md`
