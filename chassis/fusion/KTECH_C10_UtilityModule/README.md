# KTECH_C10_UtilityModule

Fusion 360 Python script that builds a parametric **bench-built bolt-in utility tray** for the Ktech C10 rear clip: two square-tube rails that **slide inside** the rear-clip receivers (tube-in-tube) and **cross-bolt**, a keyed laser-cut tray, fuel-tank envelope (welded aluminum box + sump + Radium-style in-tank pump flange + fill / vent / sender / feed / return), optional air system (tank, twin compressors, valve manifold), twin batteries, and a forward **bulkhead service plate** with AN / air / battery-cable / control pass-throughs.

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
| `03_FUEL_TANK` | Box + sump + pump flange / fill / vent / sender / feed+return bung envelopes + mount plates |
| `04_AIR` | Air tank, twin compressors, valve manifold + mounts (**air_fuel** only; omitted note when `fuel_only`) |
| `05_BATTERY` | Twin battery envelopes + mount plates |
| `06_BULKHEAD` | Forward service plate with AN feed/return, air, battery-cable, control holes |
| `07_FIXTURE` | Placeholder |

Plate DXFs → `dxf_out/` next to the script. Run dialog also prints a **tube-in-tube fit check** (receiver ID vs module OD + 2×`mod_slip_clear`).

## Tube-in-tube mate

- Rear clip receivers: `rcv_od` / `rcv_wall` (default **2.5 × 0.188 PLACEHOLDER**) — must match `KTECH_C10_RearClip`
- Module rails: `mod_od` / `mod_wall` (default **2.0 × 0.188 PLACEHOLDER**)
- Per-side slip: `mod_slip_clear` (default **0.030 PLACEHOLDER**)
- Insert length / stations: `mod_insert_len`, `mod_front_x`, bolt pattern mirrors `rcv_bolt_*`

## Variant

`module_variant` (CSV / design attribute string):

| Value | Behavior |
|---|---|
| `air_fuel` (default) | Fuel + air tank + twin compressors + manifold + batteries |
| `fuel_only` | Fuel + batteries; `04_AIR` left empty with a note sketch |

## Parameter list

Full table: **`utility_module_parameters.csv`**. Shared names reused from rear clip / chassis setup where they apply (`wb`, `rail_cl`, `rail_bottom`, `rcv_*`, `clip_t`, …).

Everything invented for layout and not yet taped or vendor-confirmed is marked **PLACEHOLDER** in the CSV `comment` column.

### Quick reference

| Param | Default | Notes |
|---|---|---|
| `module_variant` | air_fuel | air_fuel\|fuel_only |
| `mod_od` / `mod_wall` | 2.0 / 0.188 in | PLACEHOLDER module rail |
| `mod_slip_clear` | 0.030 in | PLACEHOLDER per side vs rcv ID |
| `mod_tray_len` | 36 in | PLACEHOLDER exposed tray length |
| `fuel_*` | various | PLACEHOLDER tank / sump / flange / bungs |
| `air_tank_*` / `comp_*` / `manifold_*` | various | PLACEHOLDER — air_fuel only |
| `batt_*` | various | PLACEHOLDER twin batteries |
| `bh_*` | various | PLACEHOLDER bulkhead + pass-throughs |

## Open items

- Freeze `mod_od` / `rcv_od` / `mod_slip_clear` against purchased tube and a slip coupon
- Confirm bolt pattern with rear-clip receivers before drilling
- Vendor-confirm Radium (or chosen) pump flange bolt circle and bung AN sizes
- Tape tray length vs bed / bumper envelope; settle `fuel_only` vs `air_fuel` packaging
- FEA tray keys, bulkhead, and rail insert before kits leave the shop

## Related

- Rear clip receivers: `../KTECH_C10_RearClip/`
- Chassis spine / mounts: `../KTECH_C10_Chassis_Setup/`
- Architecture notes: `../DESIGN.md`, `../C10-FRAME-GEOMETRY.md`
