# Ktech C10 boxed frame — design pack

Last updated 2026-10-04. This is the working spec for a 67–87 C10 2WD restomod chassis: 2×6 spine, plate clips, weld-on body hats, Wilwood 2.5" ProSpindle.

Fusion script lives in `KTECH_C10_Chassis_Setup/`. On the Fusion PC, copy that whole folder into:

`%APPDATA%\Autodesk\Autodesk Fusion 360\API\Scripts\KTECH_C10_Chassis_Setup`

Then Fusion → Design → **Hybrid** (or let the script switch it) → New Design → Utilities → Scripts → run **KTECH_C10_Chassis_Setup**, not the leftover script named `C10`.

New Fusion defaults to **Part Design** (one component). A chassis is **Hybrid**. Preferences → Design → Default design type → Hybrid.

---

## What we are building

Not one universal 67–87 weldment. One rail architecture, generation-specific body hats, wheelbase on the rear clip.

- **Buy:** A500 2×6 × 0.188 (or 0.250) tube, two sticks.
- **Laser:** front clip and rear clip from 3/16 plate, tab-and-slot.
- **Weld-on hats:** core / cab (and later engine, trans). 67–72 vs 73–87 are different hats on the same spine.
- **Slip-fit is a jig.** Clips are a 12–16 in open **C** that drop over the tube (A500 will not telescope through a sharp square hole). Clocking key on the tube top. Through-bolts, then weld the strap and perimeter. Ships as a fully welded chassis (RevB bar).

Raised bed: bed mounts are free. Body problem is core + cab only.

Prototype: **73–87 C10 short (117.5")**. Same clips cover 67–72 once the second hat exists. Stay 2WD until the box is right.

---

## Locked product choices

| Item | Lock |
|---|---|
| Knuckle | **Wilwood ProSpindle 831-14202**, 2.5" drop, 1971–1987 pair |
| Same knuckle 67–72? | Yes. New A-arms use **73–87 ball joints**. Do not order 831-14201 |
| Hub | Modular / unit hub on the Wilwood, 5×4.75 and 5×5 |
| Brakes | Wilwood kit for this spindle, 12–14" when the wheel is picked |
| Rear | Triangulated or parallel 4-link, **22–24" lowers** (20" floor) |
| Tire / bags | 32" OD lay-out target, ~11" bag stroke |
| Rail | 2×6 × 3/16 A500, 6" tall, 2" across the car |

CPP X10 was considered (same modern hub idea) then dropped because Wilwood published the print. Drawing: `KTECH_C10_Chassis_Setup/wilwood-831-14202.png`.

Wilwood drawing numbers in the Fusion parameters:

- BJ spread 9.06"
- Kingpin vs hub face 82°
- Hub face to BJ axis 3.68"
- Tie rod 4.09" out, 2.35" below spindle CL

---

## Taped body mounts (2026-09-01)

Center-to-center. Three stations, two spans. **Not** one cab width.

| Station | Width C-C | Along rail from previous |
|---|---|---|
| Core | 33.5" | — |
| Mid (cab front) | 42.5" | 55" behind core |
| Back of cab | 23.5" | 43" behind mid |

Core to cab-rear = **98"**.

**2×6 follows the core** (16.75" off vehicle CL each side). Mid pads are ~4.5" outboard (hats). Cab-rear pads are ~5" inboard (hats). Do not dogleg the tube to hit those holes.

Still open: **core vs front axle** (`core_x`). Set when the Wilwood and IFS land. Placeholder is −33".

Wheelbases to hit later (rear clip / splice, not cab hats):

| Body | Years | WB |
|---|---|---|
| Short 6.5' | 67–72 | 115.0" |
| Long 8' | 67–72 | 127.0" |
| Short 6.5' | 73–87 | 117.5" |
| Long 8' | 73–87 | 131.5" |

---

## Architecture

```
[ front clip — plate ]==== 2x6 tube spine ==== [ rear clip + step ]
      IFS, horns, K-member              4-link, bags, bumper
      C-socket 14"                      C-socket 14"
```

Split 2–4" behind rear cab mount, in the straight rail. Not at the engine, kick-up, cab mount, or 4-link pickup.

**Share 67–87:** tube, bulkhead library, IFS/4-link, clip sockets, fixture pins.

**Split by generation:** cab/core hole pattern, core support / horns vs OEM clip, engine-to-firewall. Do not share cab holes.

Track vs rails: keep one rail spacing. Big wheels are housing width and backspacing, not pinching the 2×6s. Narrowing the front triangle shortens the lowers and wrecks bump steer.

---

## Front clip (the hard part)

Order: knuckle → travel envelope → lower inner → upper inner → rack last.

1. Ground, 32" tire, spindle at ride and at lay-out (frame near ground = full jounce).
2. Drop in 831-14202. That locks BJ height vs hub.
3. Lower arm ~level at ride, as long as the fender allows (~14–16").
4. Upper inner from BJ spread, not from the rail.
5. Engine: pan vs K-member ~1". Pan vs **ground** at lay-out is the real limit.
6. Cab still sits on the taped mounts. 2×6 under the cab stays at `mount_y`. Front clip may hang **below** the tube (drop member). Do not kink the 2×6 for the arms.

Bags: 11" of travel will not hide a high/low rack. Tie rod same length as the lower arm and parallel in top and side view.

---

## Rear

22–24" lower bars, uppers within ~1". Level or slightly downhill to the front at ride. Mild anti-squat. Front 4-link pickups just behind the cab.

---

## Plate / tab-slot

Four flats + bulkheads every 12–16" and at every mount. Webs are the full side profile (horns, step). Tabs proud 0.06–0.10", welded both sides. Laser slot ~+0.010 over thickness — freeze with a coupon.

A500 corner radii: clip is a 3-sided C + closing strap, ~0.030" per side clearance, U-notch for the radius.

---

## Fusion file map

| Component | Role |
|---|---|
| 00_ORIGIN | 6" cube so a good run is obvious |
| 00_SKELETON | SK_SIDE, SK_TOP |
| 01_SPINE_2x6 | Two mirrored tubes |
| 02_CLIP_FRONT | Empty — next CAD |
| 03_CLIP_REAR | Empty — next CAD |
| 04_MOUNTS_73_87 | CORE / CAB_F / CAB_R construction points |
| 04_MOUNTS_67_72 | Empty hat |
| 05_IFS | Wilwood + arms + rack |
| 06_REAR | 4-link |
| 07_FIXTURE | Weld table |

Coordinates: origin = front axle × ground × frame CL. **+X rear, +Y up, +Z passenger.**

If the canvas looks empty after Run: Fit view. Rails are 16.75" off center, not on the origin.

Do not run the Fusion-generated hello script named `C10` — it only pops “Untitled”.

---

## Next on the Fusion PC

1. Pull this repo / copy `chassis/fusion/KTECH_C10_Chassis_Setup` into Fusion My Scripts.
2. Preferences → Hybrid. New Design. Run **KTECH_C10_Chassis_Setup**.
3. Confirm six mount points match the tape.
4. Tape **core to front axle**, set `core_x`.
5. Model 831-14202 on SK_SIDE from the Wilwood png.
6. Front clip C-socket + LCA inners. Rear 4-link at 22–24".

This is a fabrication architecture, not a stamped chassis. FEA the splice, IFS pickups, and 4-link before kits leave the shop.
