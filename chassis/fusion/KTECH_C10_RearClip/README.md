# KTECH_C10_RearClip

Fusion 360 Python script that builds a parametric **73–87 C10 shortbed** rear clip (first prototype, **REV-B** layout): purchased **2×5** center-tube reference, four-piece laser plate box rails with slip-fit and tab-and-slot keys (**5 in** straight / slip, **4 in** over the arch), **two rear-suspension variants** via `rear_link_type` (`triangulated` default, or `parallel_watts`), Currie 9-inch axle mockup, keyed **over-axle crossmember** with **inboard** bag **or** coilover mounts, kickup that **steps back down** aft into **rectangular** receiver tubes for the **2×4** utility module (keyed/welded into rail plates, tied by a rear crossmember, cross-bolted), plate DXF export, and a four-link bar cut list CSV.

Rails, kickup, over-axle XM, receivers, and the utility-module interface stay **identical** for both link variants so the same `KTECH_C10_UtilityModule` plugs into either.

Owner design intent for this script **overrides** the older open-C socket notes in `../DESIGN.md`: the rear clip is a **closed four-piece box** that slip-fits over the A500 tube for length adjustment, then welds.

## How to run in Fusion

1. Copy this whole folder to the Fusion scripts directory, or add it in place:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_C10_RearClip`
2. Fusion → **Utilities** → **Scripts and Add-Ins**
3. Next to **My Scripts**, click **+** and select the `KTECH_C10_RearClip` folder
4. Preferences → Design → Default design type → **Hybrid** (chassis is Hybrid, not Part)
5. **File → New Design**, then **Run** `KTECH_C10_RearClip`
6. Fit view if the canvas looks empty (rails sit at `rail_cl = 16.0` / 34 in OD; `rail_bottom = 3.5` ride)
7. Save as `KTECH_C10_REAR_CLIP`

Edit numbers in **Modify → Change Parameters** (or in `rear_clip_parameters.csv` before run). Geometry is generated at run time from those values — after big layout changes, use a **New Design** and run again (same rule as `KTECH_C10_Chassis_Setup`).

Coordinates match the chassis setup script: origin = **STOCK** front hub × ground × frame CL; **+X rear, +Y up, +Z passenger**. `front_axle_forward` / `axle_setback` move suspension pickups and axle centerlines only — not frame stations, kick-up, or hoop.

## What it builds

| Component | Contents |
|---|---|
| `00_ORIGIN` | 6" marker cube |
| `00_SKELETON` | SK_SIDE, SK_TOP, SK_KICKUP_REF |
| `01_CENTER_TUBE` | Semi-transparent **reference** A500 2×5 through the slip region only — not plate |
| `02_RAIL_RH` / `02_RAIL_LH` | Top / bottom / inboard / outboard plates, tabs, slots, bracket + over-axle key pockets, tail plates, end caps with receiver cutouts |
| `03_CROSSMEMBERS` | Frame upper 4-link crossmember + **over-axle** keyed plate XM (top, webs, optional bottom) |
| `04_FOUR_LINK` | Frame-side upper & lower bracket plates, 4 link bars (tube + RH/LH rod ends + bungs/jam nuts), link refs; Watts pivot/crank/links/brackets when `parallel_watts` |
| `05_AXLE_REF` | Parametric Currie 9" mockup (CS box + tubes + WMS markers) + keyed axle link tabs + lower bag/shock mounts |
| `06_BAG_SHOCK` | Airbag **or** coilover upper mounts on the over-axle XM (`suspension_mode`) at `bag_y` / `shock_y` |
| `07_FIXTURE` | Placeholder; DXF sketches land here when possible |
| `08_RECEIVERS` | LH/RH rectangular receiver tubes (`rcv_w` × `rcv_h` for 2×4 module) + OD-face key tabs; cross-bolt holes; rear XM lives on `03_CROSSMEMBERS` as `XMEMBER_RCV` |

Plate DXFs are written to `dxf_out/` next to the script (top-face profile sketch per named plate body), including Watts plates when `parallel_watts`. Bar tube cut lengths are written to `four_link_bar_cut_list.csv` (C–C from pickups minus rod-end eye-to-shoulder and bung lengths). On run, the dialog reports **over-axle XM bump clearance**, **REV-B layout clearances** (bag-to-rail, bag-to-upper-link when triangulated, lower-bar-to-rail at ride / bump / droop), and when `parallel_watts` a **Watts vs utility fuel-tank / rear XM** AABB clearance sweep at ride / full bump / full droop.

## Generation switch (73–87 vs 67–72)

Prototype defaults to **73–87 short** (2026-11-27 tapes):

- `wb_stock` = **116.5** in (stock hub-to-hub / stock rear-axle station; was 117.5)
- `wb` = `wb_stock` (frame + hoop driver)
- `axle_setback` = **0.5** default (range **0.5–1.0**) → `rear_axle_x` = 117.0
- `front_axle_forward` = **1.0** → design WB = **118.0** (resulting; not a frame driver)
- `wb_67_72_short` = 115.0 in

For 67–72 short, set the `wb` expression to `wb_67_72_short` and re-run. Cab hats stay generation-specific; stock WB / hoop live on the rear clip.

## Slip-fit box rail

- Inside: `slip_id_w` / `slip_id_h` = tube OD + `2 * clip_clear` (default clear **0.030 in/side**)
- Overlap: `slip_overlap` default **8 in**
- Plate: `clip_t` default **0.188 in**
- Four flats per side: top, bottom, inboard, outboard; side webs carry the kickup profile
- Tab-and-slot: `tab_width`, `tab_length` (= `clip_t`), `slot_clear`, `tab_pitch`
- Lower-bracket key pockets in the **outboard** plates (REV-B outboard lowers); rails fixture those brackets
- Over-axle XM key pockets in the **inboard** plates so rails fixture the kickup crossmember
- Kickup rises from `kick_start_x` (=74.5) into a stock hoop (**14** bottom / **8** top, centered on `wb_stock`); steps down at `wb_stock + kickup_aft` (~123.5); plate-box rails **end** at `rail_end_x`
- Tail top/bottom plates (`*_TOP_TAIL` / `*_BOT_TAIL`) + `*_END_CAP` at normal rail height in the short key bay

## Aft receivers (slide-in utility module)

Receiver length is sized to the insert, not a long empty stub. With `wb_stock=116.5`, `kickup_aft=7`, `rcv_key_w=1.5`, `clip_t=0.188`, `mod_insert_depth=6`, and **0.125 in** tip clear between end-cap aft face and module tip:

`rcv_length = rcv_key_w + clip_t + 0.125 in + mod_insert_depth` → **7.813 in** (a bare 7.5 in would put the 6 in insert into the end cap).

| Station | Expression | Default (in) |
|---|---|---|
| `rcv_front_x` | `wb_stock + kickup_aft` | **123.5** |
| `rail_end_x` | `rcv_front_x + rcv_key_w` | **125.0** |
| end-cap aft | `rail_end_x + clip_t` | **125.188** |
| `mod_front` (equiv.) | `rcv_rear_x - mod_insert_depth` | **125.313** |
| bolt 1 | `rcv_bolt_first_x` | **126.813** |
| bolt 2 | `+ rcv_bolt_pitch` | **129.813** |
| `rcv_rear_x` / `clip_rear_x` | `rcv_front_x + rcv_length` | **131.313** |
| `wb_stock + rear_overhang` | frame end / body envelope | **152.5** |

- Rectangular tube per side: `rcv_w` / `rcv_h` / `rcv_wall` sized from `mod_w=2` / `mod_h=4` + slip clear (≈ **2.436 × 4.436**), CL at `rcv_cl_y = rail_bottom + mod_h/2` (module bottom 3.5 / top 7.5)
- Plate-box rails stop at `rail_end_x`; open receiver mouths at `rcv_rear_x` are the **aft-most** clip feature (`clip_rear_x = rcv_rear_x`)
- **End cap** (`RAIL_*_END_CAP`) welds onto the box aft face at `rail_end_x` and extrudes **aft** by `clip_t`; rectangular cutout = `(rcv_w × rcv_h) + 2*rcv_weld_clear`; receiver passes through the cap
- **Insert depth** `mod_insert_depth` (default **6 in**, shared with UtilityModule) drives `rcv_length` and bolt stations; tip stays **0.125 in** aft of the end-cap aft face
- Key-bay **side** plates get a clearance window when needed. `RCV_KEY_*` tabs seat on the **receiver OD** faces and lap the rail side-plate outer faces (`rcv_key_w` = forward lap ahead of `rcv_front_x`)
- Rear plate crossmember `XMEMBER_RCV` at `rcv_xm_x` (mid of free tube aft of `rail_end_x`; clear of end cap + bolts)
- Cross-bolts sit **inside the inserted span** with equal ~1.5 in end distance: `rcv_bolt_first_x = (rcv_rear_x - mod_insert_depth) + (mod_insert_depth - rcv_bolt_pitch) / 2` (pitch **3.000** default)
- `rear_overhang` remains a body/module envelope reference for `KTECH_C10_UtilityModule` and no longer drives rail length
- Runtime: math packaging report (insert span / bolt / tip-clear checks) + best-effort Fusion interference on rails/end caps/keys/receivers/XM
- Plate DXFs: `XMEMBER_RCV`, `RCV_KEY_*`, `*_TAIL`, `*_END_CAP`

## Suspension (REV-B layout)

Selected by string param **`rear_link_type`** = `triangulated` (default) \| `parallel_watts`.

### Shared (both variants)

- **Lowers outboard of the rails:** lateral pickups at `lower_link_y` (default = rail outboard face + 0.75 in). Frame lowers key into outboard rail plates; axle lowers sit on the housing tubes outboard of the rail lines (`axle_lower_spread_z` = `lower_link_y`)
- Bars: `link_bar_od` 1.25 in round tube (`link_bar_wall` default 0.120 PLACEHOLDER)
- Each bar: RH bushed rod end at frame, LH at axle (spin-to-adjust), jam nut + threaded bung; shank thread callout `rod_end_shank_thread` (default `3/4-16` PLACEHOLDER)
- Tube cut = pickup C–C − 2×`rod_end_eye_to_shoulder` − 2×`bung_length` → `four_link_bar_cut_list.csv`
- Axle / frame pickup coordinates are PLACEHOLDER starting values in the CSV
- Frame upper crossmember + axle-side keyed tabs always built

### `triangulated` (default)

- **Uppers inboard:** converge toward the housing center / third member (`frame_upper_spread_z`, `axle_upper_spread_z` ≈ CS half-width + clearance). Frame upper brackets sit at the inboard pickup (not outboard-rail keyed)
- Lateral: triangulation; `lateral_locator` = `none` \| `panhard` (panhard remains **TODO** stub)

### `parallel_watts`

- **Uppers parallel to lowers in plan view:** frame + axle upper laterals match lower spreads (`lower_link_y` / `axle_lower_spread_z`). Frame **and** axle upper brackets are **keyed** like the lowers (outboard rail keys + axle tabs)
- Same 1.25 tube + RH/LH rod-end construction and cut list as triangulated
- **Watts link** (implied — replaces the old `lateral_locator=watts` stub):
  - Axle-mounted center bell-crank pivot on the **aft face** of the housing center section (`watts_pivot_x` / `watts_pivot_y`)
  - Horizontal lateral links to keyed frame brackets on each rail inboard face (`BRACKET_WATTS_*`)
  - Plates: `WATTS_PIVOT_MOUNT`, `WATTS_CRANK`, `BRACKET_WATTS_RH/LH` → DXF
  - All Watts dims (`watts_crank_len`, `watts_link_*`, bolt sizes, bracket sizes, …) are **PLACEHOLDER**
- Runtime clearance: Watts crank/links AABB sweep vs utility-module fuel-tank envelope (`um_fuel_*` mirrors) and rear receiver XM at ride / full bump / full droop

> **Naming note:** `lower_link_y`, `bag_y`, and `shock_y` are **lateral** offsets from frame CL (Fusion **|Z|**). Vertical heights still use Fusion **Y** (`*_pickup_y`, `shock_eye_y`, `axle_cl_y`, …).

### Over-axle crossmember

- Spans LH↔RH kickup rails, centered on **STOCK** rear axle (`wb_stock`); design axle may sit `axle_setback` aft under the same hoop
- Laser plate stack: **top**, **front web**, **rear web**, optional **bottom** (`ox_include_bottom`); thickness `ox_plate_t` (default **0.188 PLACEHOLDER**)
- End keys tab into inboard rail pockets (rails fixture the XM)
- All OA plates export to DXF (`XMEMBER_OA_*`)

### Bag / coilover mounts (inboard bay)

- Airbags and shocks sit **inboard of the rails** on the axle tubes, in the space between the rail inboard face and the upper-link path
- `suspension_mode` = **1** → airbag plates at `bag_y`; **0** → coilover double-shear shock tabs at `shock_y` (defaults to `bag_y`)
- `bag_y` default = midpoint of rail inboard face and `frame_upper_spread_z`; `mount_z_off` is a legacy alias → `bag_y`
- Shared fore/aft: `mount_x_off` (from axle CL)
- `bag_diameter` (default **8 in PLACEHOLDER**) drives clearance checks only — bag is not solid-modeled
- **Coilover / shock:** per-side keyed double-shear tab pairs hanging from the XM (`shock_eye_y`, `shock_bore` default **0.5 PLACEHOLDER**); matching lower tabs on the axle housing
- **Bag:** per-side upper plate on XM underside with single **3/8** stud + center air-fitting hole (`bag_stud_d`, `bag_stud_offset`, `bag_air_hole_d` PLACEHOLDER); matching lower plate on the housing directly under (~1:1)
- Clearance checks printed at run time:
  - XM underside ↔ housing/CS top at bump (`axle_travel_up`)
  - min gap **bag-to-rail** (inboard face) and **bag-to-upper-link** (uses `bag_diameter`)
  - min gap **lower-bar-to-rail** at ride, full bump (`axle_travel_up`), and full droop (`axle_travel_down`)

## Parameter list

Full table with expressions and notes: **`rear_clip_parameters.csv`**.

Shared names reused from `KTECH_C10_Chassis_Setup` where they apply (`tube_w`, `tube_h`, `wall`, `rail_bottom`, `wb`, `rail_cl`, `core_*`, `cab_*`, `clip_t`, `clip_clear`, `tire_od`, `bag_stroke`, …).

Anything invented for layout and not yet taped or vendor-confirmed is marked **PLACEHOLDER** (or **PLACEHOLDER UNVERIFIED** for Currie CS dims) in the CSV `comment` column.

### Quick reference — layout & slip

| Param | Default | Notes |
|---|---|---|
| `wb_stock` / `wb` | 116.5 / `wb_stock` | Stock WB + hoop center (was 117.5) |
| `axle_setback` / `rear_axle_x` | 0.5 / expr | Range 0.5–1.0; design rear hub (default 117.0) |
| `design_wb` | expr | RESULTING 118.0 — not a frame driver |
| `slip_overlap` | 8 in | Box over tube |
| `clip_clear` | 0.030 in | Per side |
| `clip_t` | 0.188 in | Plate thickness |
| `splice_aft` | 3 in | PLACEHOLDER — FLAG: cab_r+3=75.5 is 1 in into kick 74.5 |
| `tube_h` / `arch_rail_h` | 5 / 4 in | Straight 2×5; 4 in tall over arch (1 in cut on ramps) |
| `rail_bottom` / `rail_cl` | 3.5 / 16.0 in | Absolute ride height (cab match); 34 in OD |
| `kick_start_x` / `cab_back` | expr / 45 | Rise starts at 74.5; FLAG 45 vs mount 43 |
| `kickup_rise` / `kickup_top_rise` | 17 / expr | Bottom rise 17; top rise 16. Ride: bottom **20.5** / top **24.5**; laid out **17** / **21** |
| `kickup_ahead` / `aft` / `ramp` | 7 / 7 / 3 | Stock hoop 109.5–123.5 bottom / 112.5–120.5 top |
| `tire_od` | 27.5 in | 275/35/20 (was 32) |
| `lower_link_y` | rail outboard + 0.75 in | PLACEHOLDER lateral (Fusion \|Z\|) — outboard lowers |
| `frame_link_spread_z` / `axle_lower_spread_z` | `lower_link_y` | Outboard lower pickups |
| `rear_link_type` | triangulated | triangulated\|parallel_watts (string) |
| `frame_upper_spread_z` / `axle_upper_spread_z` | inboard exprs | Triangulated uppers toward CS (ignored when parallel_watts) |
| `watts_*` / `um_fuel_*` | various | PLACEHOLDER — Watts + UtilityModule fuel mirror for clearance |
| `suspension_mode` | 1 | 1=bag, 0=coilover (on over-axle XM) |
| `ox_plate_t` / `ox_width_x` / `ox_web_h` | 0.188 / 6 / 3 in | PLACEHOLDER over-axle XM |
| `ox_include_bottom` | 1 | 1=closed box, 0=open channel |
| `bag_y` / `shock_y` | mid inboard bay / `bag_y` | PLACEHOLDER lateral — inboard of rails |
| `bag_diameter` | 8 in | PLACEHOLDER — clearance check only |
| `mount_z_off` / `mount_x_off` | `bag_y` / 0 in | Legacy alias + fore/aft |
| `shock_bore` / `shock_eye_y` | 0.5 in / expr | PLACEHOLDER coilover eye |
| `bag_stud_d` / `bag_air_hole_d` | 0.375 / 0.750 in | PLACEHOLDER bag pattern |
| `axle_travel_up` / `axle_travel_down` | 3 / 5 in | PLACEHOLDER bump / droop for clearance |
| `link_bar_od` / `link_bar_wall` | 1.25 / 0.120 in | Bar tube; wall PLACEHOLDER |
| `rod_end_*` / `bung_*` | various | PLACEHOLDER rod-end / bung stack |
| `axle_*_pickup_*` / `axle_*_spread_z` | various | PLACEHOLDER axle pickups |
| `lateral_locator` | none | none\|panhard — watts via parallel_watts; panhard TODO |
| `mod_w` / `mod_h` | 2 / 4 in | 2×4 utility-module rails (match UtilityModule) |
| `rcv_w` / `rcv_h` / `rcv_wall` | derived / 0.188 | Rectangular pocket = mod + 2×clear + 2×wall |
| `mod_insert_depth` | 6.000 in | Shared with UtilityModule — slip depth into receiver |
| `rcv_length` | `rcv_key_w + clip_t + 0.125 + mod_insert_depth` | ≈7.813 in — key bay + cap + tip clear + insert |
| `rcv_front_x` | `wb_stock + kickup_aft` | Receiver forward face (~123.5) |
| `rcv_key_w` | 1.5 in | Forward lap of key tab onto rail side plate (also key-bay length) |
| `rail_end_x` | `rcv_front_x + rcv_key_w` | Plate-box aft end (key bay); end cap welds aft |
| `rcv_rear_x` / `clip_rear_x` | `rcv_front_x + rcv_length` | Receiver mouths = clip aft end (≈131.313) |
| `rcv_weld_clear` | 0.030 in | PLACEHOLDER end-cap cutout oversize |
| `rcv_bolt_d` / `rcv_bolt_count` | 0.5 in / 2 | PLACEHOLDER cross-bolts (inside insert) |
| `rcv_bolt_first_x` | centered in insert (see above) | Equal ~1.5 in end distance; pitch 3.000 |
| `rcv_xm_w` / `rcv_xm_t` | 2 / `clip_t` in | PLACEHOLDER rear receiver XM |
| `rear_overhang` | 36 in | TAPED from **STOCK** rear axle → frame end **152.5** — **not** rail length |
| `cab_to_axle` / `cab_f_x` / `core_x` / `cab_r_x` | 87 / 29.5 / −25 / 72.5 | FRONT cab→**stock** axle; core literal |
| `axle_wms_a` | **58.0 in** | PLACEHOLDER — LOCKED this pass |
| `cs_width` / `cs_height` / `cs_depth` / `tube_insert` | — | PLACEHOLDER UNVERIFIED — Currie |

## FLAG — arch / axle / tire clearance (2026-11-27)

`kickup_rise = 17` with `arch_rail_h = 4` → arch underside **20.5** / top **24.5** at ride (`rail_bottom = 3.5`); laid out underside **17** / top **21**.

Stock tape: arch underside **23** off the floor and **8** above the axle imply an axle at **15**, which does **not** match the **13.75** tire radius on a **27.5** OD (275/35/20). The same **1.25** gap shows up as: 20.5 underside is **6.75** above a 13.75 axle CL (and **5.25** above a 3 in tube top at 15.25) — **not** 8. Do not close one tape to match the other.

In side view the rail will cross the 27.5 tire OD because the rails sit **inboard** of the tires; the relevant clearance is to the **axle / tube**, not the tire OD.

Default `axle_setback = 0.5` puts the design rear axle **0.5 aft of hoop center** — still under the 8/14 hoop; hoop stays on the stock station.

Rear bag: ~**9** nearly fully aired at the taped stance; probably ~**10** fully stretched. Record only — no invented bag-to-crossmember packaging.

FLAG: FrontGeometry still locks a **29 in** 22×9 front package; both ends are specified here as 275/35/20 / 27.5 — confirm whether front matches.

## Open items

- Slip is **matched 2×5** (`tube_h = 5` / `slip_id_h` follows) with FrontClip / Chassis_Setup.
- **Currie 9-inch CAD** requested **2026-11-15** — replace `cs_width`, `cs_height`, `cs_depth`, `tube_insert` placeholders
- **Wilwood CAD** requested **2026-11-15** — front/related; rear brake package still TBD against WMS / housing ends
- Freeze `slot_clear` with a laser coupon
- Tape / fixture: confirm `splice_aft` vs kick_start (75.5 vs 74.5), kickup vs 27.5 tire + bag stroke, and 4-link pickup coordinates (frame + axle)
- Confirm REV-B laterals: `lower_link_y` (outboard lowers), `bag_y` / `shock_y` (inboard bay), and `bag_diameter` against purchased bags
- Confirm rod-end / bung stack (`rod_end_eye_to_shoulder`, `bung_length`, thread callout) against purchased ends before cutting tubes
- Confirm over-axle XM plate gauge (`ox_plate_t`), bag stud/air pattern, and shock bore against purchased hardware
- Confirm bump/droop travel (`axle_travel_up` / `axle_travel_down`) and printed clearance gaps against tire/bag stroke and third-member envelope
- Optional panhard (`lateral_locator=panhard`) — TODO stub; Watts ships with `parallel_watts`
- Confirm Watts PLACEHOLDERs (`watts_pivot_*`, crank length, link OD/bolts) and `um_fuel_*` vs live UtilityModule tank package
- Confirm rectangular `rcv_w`/`rcv_h` vs 2×4 module + slip (`KTECH_C10_UtilityModule`), bolt pattern, OD-key / end-cap weld clear, and key sizes before cutting
- Confirm `rail_end_x` key-bay length vs weld practice; freeze `rcv_weld_clear` with a coupon
- FEA splice, over-axle XM, receiver XM, end caps, frame upper xmember, 4-link brackets, and Watts mount before kits leave the shop
- Remaining PLACEHOLDERs: Currie CS dims, Watts stack, bag/shock hardware, rod-end/bung stack, `um_fuel_*` mirrors, kickup/splice tape values (see CSV `comment` column)

## Related

- Chassis spine / mounts: `../KTECH_C10_Chassis_Setup/`
- Slide-in utility tray (tube-in-tube into receivers): `../KTECH_C10_UtilityModule/`
- Architecture notes: `../DESIGN.md`, `../C10-FRAME-GEOMETRY.md` (slip-fit **box** here supersedes C-socket wording for the rear clip)
