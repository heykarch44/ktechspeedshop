# Ktech C10 frame geometry

Working spec for a 67–87 C10 2WD restomod chassis: 2×6 A500 spine, plate clips, weld-on body hats, Wilwood 2.5" ProSpindle.

Taped body mounts: **2026-09-01** on a squarebody. Prices are not in this file.

Prototype: **73–87 C10 short, 117.5" wheelbase.** Stay 2WD until the box is right.

---

## Architecture

Not one universal 67–87 weldment. One rail architecture, generation-specific body hats, wheelbase on the rear clip.

```
[ front clip — plate ]==== 2x6 tube spine ==== [ rear clip + step ]
      IFS, horns, K-member              4-link, bags, bumper
      C-socket 14"                      C-socket 14"
```

- **Buy:** A500 2×6 × 0.188 (or 0.250), two sticks.
- **Laser:** front clip and rear clip from 3/16 plate, tab-and-slot.
- **Weld-on hats:** core / cab (later engine, trans). 67–72 vs 73–87 are different hats on the same spine.
- **Slip-fit is a jig.** Clips are a 12–16" open **C** that drop over the tube. A500 will not telescope through a sharp square hole (corner radii + weld seam). Clocking key on the tube top. Through-bolts, then weld the strap and perimeter. Ships as a **fully welded** chassis.

Raised bed: bed mounts are free. Body problem is **core + cab only**.

Split 2–4" behind the rear cab mount, in the straight rail. Not at the engine, kick-up, cab mount, or 4-link pickup.

Keep **one rail spacing**. Track width is housing length plus backspacing, not pinching the 2×6s.

---

## Taped body mounts (shop tape, 2026-09-01)

All center-to-center. Three widths, two spans. **Not** one cab width.

| Station | Fusion name | Width C-C | Along the rail | Vs 2×6 |
|---|---|---|---|---|
| Core support | `CORE` | **33.5"** | datum | Rails sit here (16.75" off CL) |
| Mid / cab front | `CAB_F` | **42.5"** | **55"** behind core | Hat ~4.5" outboard of tube |
| Back of cab | `CAB_R` | **23.5"** | **43"** behind mid | Hat ~5.0" inboard of tube |

Core to cab-rear = **98"**.

**2×6 follows the core.** Do not dogleg the tube to hit the mid or cab-rear holes. Those are weld-on hats.

**Still open:** core vs front axle (`core_x`). Placeholder is **−33"**. Tape core-bolt to front-axle centerline when the Wilwood is on the truck. That number slides the whole cab station set in Fusion.

---

## Locked product

| Item | Lock |
|---|---|
| Knuckle | **Wilwood ProSpindle 831-14202**, 2.5" drop, 1971–1987 pair |
| Same knuckle 67–72? | Yes. New A-arms use **73–87 ball joints**. Do not order 831-14201 |
| Hub | Modular / unit hub, 5×4.75 and 5×5 |
| Rear | 4-link, **22–24" lowers** (20" is the floor) |
| Tire / bags | 32" OD lay-out, ~11" bag stroke |
| Rail | 2×6 × 3/16 A500, 6" tall, 2" across the car |

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
| Tube | 2 × 6 × 0.188" A500 |
| Orientation | 6" tall, 2" across the car |
| Rail CL from vehicle CL | 16.75" |
| Clip overlap | 14" |
| Clip plate | 0.188" |
| C-socket clearance | 0.030" per side |

Clip is a 3-sided C plus closing strap, U-notch for tube radius. Tabs proud 0.06–0.10". Laser slot ~+0.010 over plate — freeze with a coupon.

---

## Fusion coordinates and side layout

Origin = **front axle × ground × frame centerline**.

- **+X** = rear
- **+Y** = up
- **+Z** = passenger (right)

| Parameter | Value | Status |
|---|---|---|
| `front_overhang` | 34" | Estimate — horns / core |
| `wb` | 117.5" | Locked for first proto |
| `rear_overhang` | 42" | Estimate — raised bed |
| `core_x` | −33" | **Placeholder — tape next** |
| `cab_f_x` | `core_x + 55` | Computed from tape |
| `cab_r_x` | `cab_f_x + 43` | Computed from tape |
| `rail_bottom` | 8" | Ride height — bags change this |
| `spine_length` | 193.5" | 34 + 117.5 + 42 |

If the Fusion canvas looks empty after Run: Fit view. Rails sit 16.75" off center, not on the origin.

---

## Wheelbases (rear clip, not cab hats)

| Body | Years | WB |
|---|---|---|
| Short 6.5' | 67–72 | 115.0" |
| Long 8' | 67–72 | 127.0" |
| Short 6.5' (prototype) | 73–87 | **117.5"** |
| Long 8' | 73–87 | 131.5" |

---

## What is shared vs what splits

| Share 67–87 | Split by generation |
|---|---|
| 2×6 spine, clip sockets, fixture pins | Cab / core hole pattern |
| IFS and 4-link architecture | Core support / horns vs OEM clip |
| Wilwood knuckle + 73–87 BJs | Engine-to-firewall hats |
| One rail spacing (core 33.5") | Wheelbase on the rear clip |

Do not share cab holes across 67–72 and 73–87.

---

## Front clip (the hard part)

Order: knuckle → travel envelope → lower inner → upper inner → rack last.

1. Ground, 32" tire, spindle at ride and at lay-out (frame near ground = full jounce).
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
| 01_SPINE_2x6 | Two mirrored tubes on core width |
| 02_CLIP_FRONT | Empty — next CAD |
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
2. Tape **core to front axle**. Set `core_x`. Re-run.
3. Model 831-14202 on SK_SIDE from `wilwood-831-14202.png`.
4. Front clip C-socket + LCA inners. Do not dogleg the 2×6.
5. Rear 4-link at 22–24", step around 32" tire + 11" bags.

This is a fabrication architecture, not a stamped chassis. FEA the splice, IFS pickups, and 4-link before kits leave the shop.
