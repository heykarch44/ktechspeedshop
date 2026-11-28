# Ktech C10 frame geometry

Working spec for a 67–87 C10 2WD restomod chassis: 2×6 A500 spine, plate clips, weld-on body hats, Wilwood 2.5" ProSpindle.

Taped body mounts: **2026-09-01** on a squarebody. Prices are not in this file.

Prototype: **73–87 C10 short.** Stock hub-to-hub **`wb_stock = 116.5"`** (taped 2026-11-27; CAD had 117.5). Design WB = `wb_stock + front_axle_forward + axle_setback` = **118.0"** at defaults (1.0 + 0.5) — resulting, not a frame driver. Stay 2WD until the box is right.

---

## Architecture

Not one universal 67–87 weldment. One rail architecture, generation-specific body hats, wheelbase on the rear clip.

```
[ front clip — plate ]==== 2x5 tube spine ==== [ rear clip + step ]
      IFS, horns, K-member              4-link, bags, bumper
      C-socket 14"                      C-socket 14"
```

- **Buy:** A500 2×5 × 0.188 (or 0.250) center/cab tube (FLAG: was 2×6), two sticks.
- **Laser:** front clip and rear clip from 3/16 plate, tab-and-slot.
- **Weld-on hats:** core / cab (later engine, trans). 67–72 vs 73–87 are different hats on the same spine.
- **Slip-fit is a jig.** Clips are a 12–16" open **C** that drop over the tube. A500 will not telescope through a sharp square hole (corner radii + weld seam). Clocking key on the tube top. Through-bolts, then weld the strap and perimeter. Ships as a **fully welded** chassis.

Raised bed: bed mounts are free. Body problem is **core + cab only**.

Split 2–4" behind the rear cab mount, in the straight rail. Not at the engine, kick-up, cab mount, or 4-link pickup.

Straight section through arms/engine is **34 in OD** (`rail_cl = 16.0`). Nose ahead of the rack narrows to **28 × 4 in**. Track width is housing length plus backspacing, not pinching the rails.

---

## Taped body mounts (shop tape, 2026-09-01)

All center-to-center. Three widths, two spans. **Not** one cab width.

| Station | Fusion name | Width C-C | Along the rail | Vs 2×6 |
|---|---|---|---|---|
| Core support | `CORE` | **33.5"** | datum | Core-mount C-C (28 in nose + 2.75 pads/side) — not rail spacing |
| Mid / cab front | `CAB_F` | **42.5"** | **55"** behind core | Hat outboard of tube |
| Back of cab | `CAB_R` | **23.5"** | **43"** behind mid | Hat inboard of tube |

Core to cab-rear = **98"**.

**Rails through arms/engine:** `rail_cl = 16.0` (34 in OD). Core width stays 33.5 as mount C-C. Do not dogleg the tube to hit mid/cab-rear holes — those are weld-on hats. Cab/center tube is now **2×5** at bottom **3.5** (FLAG: was 2×6).

**Cab stations (2026-11-27):** Origin = **STOCK** front hub. `cab_to_axle = 87` is **FRONT** cab mount to **STOCK** rear axle (confirmed). Drivers: `cab_f_x = wb_stock − 87 = 29.5` (also taped); `core_x = −25` **literal** (not from `core_to_mid`); `cab_r_x = 29.5 + 43 = 72.5`. Keep earlier `core_to_mid = 55` as a recorded tape — direct span is 54.5 (**FLAG 0.5 in**; do not close). `cab_back = 45` → kick start 74.5; keep separate from mount tape `mid_to_rear = 43` (**FLAG: 45 vs 43**).

---

## Locked product

| Item | Lock |
|---|---|
| Knuckle | **Wilwood ProSpindle 831-14202**, 2.5" drop, 1971–1987 pair |
| Same knuckle 67–72? | Yes. New A-arms use **73–87 ball joints**. Do not order 831-14201 |
| Hub | Modular / unit hub, 5×4.75 and 5×5 |
| Rear | 4-link, **22–24" lowers** (20" is the floor) |
| Tire / bags | 27.5" OD (275/35/20) lay-out; ~11" bag stroke. FLAG: FrontGeometry still 29" 22×9 |
| Rail | Cab/center **2×5** × 3/16 A500; front clip flat **5"** / 34" OD (was 6); nose 28×4 |

CPP X10 was considered and dropped because Wilwood published the print.

### Wilwood 831-14202 (from the drawing)

| Dim | Value |
|---|---|
| Spindle drop | 2.50" |
| BJ spread | 9.06" |
| Kingpin vs hub face | 82° |
| Hub face to BJ axis | 3.68" |
| Tie rod reach | 4.09" |
| Tie rod drop | 2.35" |

Drawing file in the Fusion script folder: `wilwood-831-14202.png`.

---

## Spine and clips

| Dim | Value |
|---|---|
| Tube (cab/center) | 2 × 5 × 0.188" A500 (FLAG: was 2×6) |
| Front clip at arms | Flat **5"** tall, 34" OD (`rail_cl = 16.0`), bottom 10.07 / top 15.07 at ride |
| Nose | 28 × 4 in, 23° / 7 in kick, top ramps **5 in** (~35.5°), bottom **4 in** (~29.7°); nose top **10.07** / bottom **6.07** (vs stock core bottom 9.00 = −2.93); drop 6.57 x=8→20 finishes 9.5 in before `cab_f_x=29.5` |
| Rear arch | `kickup_rise=19`, `arch_rail_h=4` → top rise **18**. Ride bottom **22.5** / top **26.5**; laid out **19** / **23**. Hoop on stock axle 109.5-123.5 / 112.5-120.5. Sized 19 above rail bottom (2 in to housing at pancake +1 for 5 in rail +1 for ~29 in tire). |
| Clip overlap | 14" (legacy) / FrontClip slip 8" over 2×5 |
| Clip plate | 0.188" |
| Slip clearance | 0.030" per side |
| Rear WMS A | 58.0 PLACEHOLDER (tire TBD) |

Clip is a 3-sided C plus closing strap, U-notch for tube radius. Tabs proud 0.06–0.10". Laser slot ~+0.010 over plate — freeze with a coupon.

---

## Fusion coordinates and side layout

Origin = **STOCK front hub × ground × frame centerline**.

- **+X** = rear
- **+Y** = up
- **+Z** = passenger (right)

`front_axle_forward` (default **1.0**) and `axle_setback` (default **0.5**, range **0.5–1.0**) move **only** suspension pickups / axle centerlines — not rails, drop, nose, core, cab mounts, kick-up/hoop, or frame end.

| Parameter | Value | Status |
|---|---|---|
| `front_overhang` | 34" | Estimate — horns / core |
| `wb_stock` | 116.5" | TAPED 2026-11-27 stock hub-to-hub / stock rear axle |
| `front_axle_forward` / `front_axle_x` | 1.0 / −1.0 | Design front hub; pickups only |
| `axle_setback` / `rear_axle_x` | 0.5 / 117.0 | Range 0.5–1.0; axle + axle-side links only |
| `design_wb` | 118.0" | RESULTING — not a frame-station driver |
| `rear_overhang` | 36" | TAPED from **STOCK** rear axle → frame end **152.5** (35.5 aft of default design rear) |
| `cab_to_axle` | 87" | CONFIRMED: **FRONT** cab mount → stock rear axle |
| `cab_f_x` | 29.5" | Driver (`wb_stock − 87`) |
| `core_x` | −25" | LITERAL tape (was −24.5 derived) |
| `cab_r_x` | 72.5" | `cab_f_x + mid_to_rear(43)` |
| `cab_back` / `kick_start_x` | 45 / 74.5 | FLAG vs mount 43; kick rises into hoop |
| `cab_rail_bottom` / `rail_bottom` | 3.5" | Cab/center bottom at design ride |
| `front_rail_bottom` | 10.07" | Front clip at arms (LOCKED) |
| `spine_length` | 186.5" | 34 + 116.5 + 36 (frame end 152.5) |

If the Fusion canvas looks empty after Run: Fit view. Rails sit at `rail_cl = 16.0` (34 in OD), not on the origin.

---

## Wheelbases (rear clip, not cab hats)

| Body | Years | Stock WB | Notes |
|---|---|---|---|
| Short 6.5' | 67–72 | 115.0" | |
| Long 8' | 67–72 | 127.0" | |
| Short 6.5' (prototype) | 73–87 | **116.5"** | Taped; design WB 118.0 at defaults |
| Long 8' | 73–87 | 131.5" | |

---

## What is shared vs what splits

| Share 67–87 | Split by generation |
|---|---|
| 2×6 spine, clip sockets, fixture pins | Cab / core hole pattern |
| IFS and 4-link architecture | Core support / horns vs OEM clip |
| Wilwood knuckle + 73–87 BJs | Engine-to-firewall hats |
| 34 in OD through arms/engine (`rail_cl` 16.0) | Wheelbase on the rear clip; 28 in nose ahead of rack |

Do not share cab holes across 67–72 and 73–87.

---

## Front clip (the hard part)

Order: knuckle → travel envelope → lower inner → upper inner → rack last.

1. Ground, 27.5" tire (FLAG vs FrontGeometry 29"), spindle at ride and at lay-out (frame near ground = full jounce).
2. Drop in 831-14202. That locks BJ height vs hub.
3. Lower arm ~level at ride, as long as the fender allows (~14–16").
4. Upper inner from BJ spread, not from the rail.
5. Rack last. Tie rod same length as the lower arm and parallel in top and side view.
6. Engine: pan vs K-member ~1". Pan vs **ground** at lay-out is the real limit.

Cab still sits on the taped mounts. 2×6 under the cab stays at `mount_y`. Front clip may hang **below** the tube (drop member). Do not kink the 2×6 for the arms.

11" of bag travel will not hide a high/low rack.

---

## Rear 4-link

- Lower bars **22–24"**
- Uppers within ~1" of the lowers
- Level or slightly downhill to the front at ride
- Mild anti-squat
- Front pickups just behind the cab
- Track width = housing + backspace, not rail pinch

---

## Fusion file map

Script folder: `chassis/fusion/KTECH_C10_Chassis_Setup`

On the Fusion PC, copy that folder to:

`%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_C10_Chassis_Setup`

Preferences → Design → Default design type → **Hybrid**. New Fusion defaults to Part (one component). A chassis is Hybrid.

Run **KTECH_C10_Chassis_Setup**. Do **not** run the leftover Fusion-generated script named `C10` — that only pops “Untitled”.

| Component | Role now |
|---|---|
| 00_ORIGIN | 6" cube so a good run is obvious |
| 00_SKELETON | SK_SIDE, SK_TOP |
| 01_SPINE_2x5 | Two mirrored cab/center tubes (`rail_cl` 16.0, bottom 3.5) |
| 02_CLIP_FRONT | Empty browser slot — run `KTECH_C10_FrontClip` |
| 03_CLIP_REAR | Empty — next CAD |
| 04_MOUNTS_73_87 | CORE / CAB_F / CAB_R construction points |
| 04_MOUNTS_67_72 | Empty hat |
| 05_IFS | Empty — Wilwood + arms + rack |
| 06_REAR | Empty — 4-link |
| 07_FIXTURE | Empty — weld table |

Numbers live in `parameters.csv` and `mount_points.csv`. The `.py` script builds a new document from those.

---

## Next on the Fusion PC

1. Hybrid + New Design + Run **KTECH_C10_Chassis_Setup**. Confirm six mount points.
2. Cab stations from 2026-11-27 tapes (`cab_f_x=29.5`, `core_x=-25`); 45 in is the back cab wall (kick starts at 74.5). Remaining FLAG: 54.5 vs 55 core-to-cab.
3. Model 831-14202 on SK_SIDE from `wilwood-831-14202.png`.
4. Front clip C-socket + LCA inners at `front_axle_x`. Do not dogleg the 2×5.
5. Rear 4-link at 22-24", arch rise 19 (underside 19 above the cab/rear rail bottom).

This is a fabrication architecture, not a stamped chassis. FEA the splice, IFS pickups, and 4-link before kits leave the shop.
