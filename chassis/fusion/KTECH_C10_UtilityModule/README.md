# KTECH_C10_UtilityModule

Fusion 360 Python script that builds a parametric **bench-built bolt-in utility tray** for the Ktech C10 rear clip: two square-tube rails that **slide inside** the rear-clip receivers (tube-in-tube) and **cross-bolt**, a keyed laser-cut tray, fuel-tank envelope (welded aluminum box + Boyd 21057 sump + Radium 20-0278 6x10 24-bolt flange / FCST-X + Usher UD3F fill + Ace Race Parts ORB bungs + SAE 5-bolt sender), optional air system (tank, twin compressors, valve manifold), twin batteries, and a forward **bulkhead service plate** with AN / air / battery-cable / control pass-throughs.

Mates to `../KTECH_C10_RearClip/` receivers (`rcv_*` params must match).

## How to run in Fusion

1. Copy this whole folder to the Fusion scripts directory, or add it in place:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_C10_UtilityModule`
2. Fusion → **Utilities** → **Scripts and Add-Ins**
3. Next to **My Scripts**, click **+** and select the `KTECH_C10_UtilityModule` folder
4. Preferences → Design → Default design type → **Hybrid**
5. **File → New Design**, then **Run** `KTECH_C10_UtilityModule`
6. Fit view if needed; save as `KTECH_C10_UTILITY_MODULE`

Edit numbers in **Modify → Change Parameters** (or in `utility_module_parameters.csv` before run). After big layout changes, use a **New Design** and run again.

Coordinates match the chassis / rear clip: origin = front axle × ground × frame CL; **+X rear, +Y up, +Z passenger**.

## What it builds

| Component | Contents |
|---|---|
| `00_ORIGIN` | 6" marker cube |
| `00_SKELETON` | SK_SIDE, SK_TOP layout refs |
| `01_RAILS` | LH/RH hollow square tubes (`mod_od` × `mod_wall`) + matching cross-bolt holes |
| `02_TRAY` | Keyed laser floor plate + rail key strips (`TRAY_FLOOR`, `TRAY_KEY_*`) |
| `03_FUEL_TANK` | Box + Boyd sump + 6x10 flange / fill / vent / sender / feed+return+drain bung envelopes + mount plates |
| `04_AIR` | Air tank, twin compressors, valve manifold + mounts (**air_fuel** only; omitted note when `fuel_only`) |
| `05_BATTERY` | Twin battery envelopes + mount plates |
| `06_BULKHEAD` | Forward service plate with AN feed/return, air, battery-cable, control holes |
| `07_FIXTURE` | Placeholder |

Plate DXFs → `dxf_out/` next to the script. Run dialog also prints a **tube-in-tube fit check** (receiver ID vs module OD + 2×`mod_slip_clear`) and warns if `fuel_h` is outside FCST-X depth.

## Fuel fittings (sourced)

| Fitting | Part / source | Notes |
|---|---|---|
| 6x10 24-bolt weld flange | Radium **20-0278** (accepts FCST-X or blank 6x10 plate) | Obround outer + Nuke DXF bolt/opening geometry; thickness fly-cut |
| FKM gasket | Radium **18-0015** | `fuel_pf_gasket_t` |
| Surge tank depth | Radium **FCST-X** | 7.7–12.7 in outer top to internal floor; deeper needs extension |
| 6x10 bolt / opening DXF | Nuke Performance **6x10-24bolts.DXF** | Geometry source; verify flange vs 20-0278 in hand |
| Fuel level sender | Dakota Digital **SEN-06-1** / Tanks Inc SAE 5-hole | 5-bolt flange; screw *angles* still PLACEHOLDER (SAE uneven) |
| -8AN ORB weld bungs | Ace Race Parts (feed + return) via K2 | Body / shoulder / height; pilot hole PLACEHOLDER |
| -6AN ORB weld bungs | Ace Race Parts (drain + vent) via K2 | Vent/rollover valve fit PLACEHOLDER |
| Flush aero filler | Usher **UD3F** (fillernecksupply.com) | Flange + cap stack; tank cutout PLACEHOLDER |
| Weld-in sump | Boyd Welding **21057** 2.5 in OD | Under 6x10 center; 1/4 NPT fitting |

### Source URLs

- https://www.radiumauto.com/products/fuel-cell-mounting-accessories (20-0278 flange, 18-0015 gasket)
- https://www.radiumauto.com/products/fcst-x-fuel-cell-surge-tank (FCST-X depth 7.7–12.7 in, 6x10 24-bolt)
- https://www.nukeperformance.com/dokument/6x10-24bolts.DXF (6x10 24-bolt geometry)
- https://www.dakotadigital.com/index.cfm/page/ptype=product/product_id=112/mode=prod/prd112.htm (SAE 5-bolt sender)
- https://www.tanksinc.com/index.cfm/page/ptype=results/category_id=159/mode=cat/cat159.htm (SAE 5-hole uneven spacing)
- https://www.k2-fabrication.com/products/6an-female-weld-bung-6061-aluminum and https://www.k2-fabrication.com/products/8an-female-weld-bung-6061-aluminum (Ace Race Parts ORB bungs)
- https://www.fillernecksupply.com/usher-precision-manufacturing-aero-aluminum-flush-mount-fuel-filler-neck-flange-and-cap-weld-on-ud3f-us-3-f/ (UD3F filler)
- https://fueltankparts.com/products/2-5-od-aluminum-weld-in-sump (Boyd 21057 sump)

### Still PLACEHOLDER

- Tank shell size (`fuel_l` / `fuel_w` / `fuel_h` / `fuel_wall` / `fuel_x` / `fuel_y`)
- Sender screw angles (SAE 5-hole is **not** evenly spaced)
- Bung pilot holes (`fuel_an8_hole_d`, `fuel_an6_hole_d`)
- Filler tank cutout (`fuel_fill_hole_d`)
- Rollover valve fit on vent bung

## Tube-in-tube mate

Mirrors `KTECH_C10_RearClip` receiver packaging. Shared `mod_insert_depth` (default **6 in**) sets slip depth; the clip shortens the receiver to `rcv_key_w + clip_t + 0.125 in + mod_insert_depth` (≈**7.813 in**) so there is no long empty stub ahead of the tip. Module tip stays **0.125 in** aft of the end-cap aft face.

| Station | Expression | Default (in) @ wb=117.5 |
|---|---|---|
| `rcv_front_x` | `wb + kickup_aft` | **125.5** |
| `rail_end_x` | `rcv_front_x + rcv_key_w` | **127.0** |
| end-cap aft | `rail_end_x + clip_t` | **127.188** |
| `mod_front_x` | `rcv_rear_x - mod_insert_depth` | **127.313** |
| bolt 1 / bolt 2 | centered in insert, pitch 3.000 | **128.813** / **131.813** |
| `rcv_rear_x` / `clip_rear_x` | `rcv_front_x + rcv_length` | **133.313** |
| `tray_x0` / `bh_x` | `rcv_rear_x` | **133.313** (at receiver mouths) |
| `wb + rear_overhang` | body envelope ref | **159.5** (`mod_rear_x` ≈ this when `mod_tray_len` is dialed in) |

- Rear clip receivers: `rcv_od` / `rcv_wall` (default **2.5 × 0.188 PLACEHOLDER**) — must match rear clip exactly
- Module rails: `mod_od` / `mod_wall` (default **2.0 × 0.188 PLACEHOLDER**) slide in from `rcv_rear_x` forward by `mod_insert_depth`
- Per-side slip: `mod_slip_clear` (default **0.030 PLACEHOLDER**)
- Insert: `mod_insert_len = mod_insert_depth`; `mod_front_x = rcv_rear_x - mod_insert_depth`
- Cross-bolts (shared exprs): `rcv_bolt_first_x = (rcv_rear_x - mod_insert_depth) + (mod_insert_depth - rcv_bolt_pitch) / 2` — both holes inside the insert with ~1.5 in end distance
- End-cap cutout on the clip is sized for `rcv_od`; module OD fits through the receiver bore and the cap opening

## Variant

`module_variant` (CSV / design attribute string):

| Value | Behavior |
|---|---|
| `air_fuel` (default) | Fuel + air tank + twin compressors + manifold + batteries |
| `fuel_only` | Fuel + batteries; `04_AIR` left empty with a note sketch |

## Parameter list

Full table: **`utility_module_parameters.csv`**. Shared names reused from rear clip / chassis setup where they apply (`wb`, `rail_cl`, `rail_bottom`, `rcv_*`, `clip_t`, …).

Sourced fitting comments start with **SOURCED (…)**. Layout / unverified items stay **PLACEHOLDER**.

### Quick reference

| Param | Default | Notes |
|---|---|---|
| `module_variant` | air_fuel | air_fuel\|fuel_only |
| `rcv_*` / `rail_end_x` / `clip_rear_x` / `mod_insert_depth` | match rear clip | Mirror expressions/defaults exactly |
| `rear_overhang` | 42 in | Match rear clip body/module envelope |
| `mod_od` / `mod_wall` | 2.0 / 0.188 in | PLACEHOLDER module rail |
| `mod_slip_clear` | 0.030 in | PLACEHOLDER per side vs rcv ID |
| `mod_insert_depth` / `mod_insert_len` | 6.000 in / `= depth` | Slip depth into receiver |
| `mod_front_x` | `rcv_rear_x - mod_insert_depth` | Tip aft of end cap (≈127.313) |
| `tray_x0` | `rcv_rear_x` | Tray/bulkhead at receiver mouths (≈133.313) |
| `mod_tray_len` | 36 in | PLACEHOLDER exposed tray length |
| `fuel_l` / `fuel_w` / `fuel_h` | 28 / 18 / 10 in | PLACEHOLDER tank shell |
| `fuel_pf_*` / `fuel_fcst_*` | sourced | Radium 20-0278 / Nuke DXF / FCST-X |
| `fuel_sender_*` | sourced | SAE 5-bolt (angles PLACEHOLDER) |
| `fuel_fill_*` | sourced | Usher UD3F (cutout PLACEHOLDER) |
| `fuel_feed_an` / `fuel_return_an` / `fuel_an*` | sourced | Ace Race Parts -8 / -6 ORB |
| `fuel_sump_*` | sourced | Boyd 21057 |
| `air_tank_*` / `comp_*` / `manifold_*` | various | PLACEHOLDER — air_fuel only |
| `batt_*` | various | PLACEHOLDER twin batteries |
| `bh_*` | various | PLACEHOLDER bulkhead + pass-throughs |

## Open items

- Freeze `mod_od` / `rcv_od` / `mod_slip_clear` against purchased tube and a slip coupon
- Confirm bolt pattern with rear-clip receivers before drilling
- Verify Nuke DXF flange outer vs Radium 20-0278 in hand; confirm SAE sender screw angles vs gasket
- Confirm bung pilot holes and filler cutout with parts in hand
- Tape tray length vs bed / bumper envelope; settle `fuel_only` vs `air_fuel` packaging
- FEA tray keys, bulkhead, and rail insert before kits leave the shop

## Related

- Rear clip receivers: `../KTECH_C10_RearClip/`
- Chassis spine / mounts: `../KTECH_C10_Chassis_Setup/`
- Architecture notes: `../DESIGN.md`, `../C10-FRAME-GEOMETRY.md`
