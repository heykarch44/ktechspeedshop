import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Code,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  TodoListCard,
  useHostTheme,
} from "cursor/canvas";

export default function C10FrameGeometry() {
  return (
    <Stack gap={28} style={{ padding: 24, maxWidth: 1120 }}>
      <Stack gap={8}>
        <Row gap={8} align="center">
          <Pill tone="info">Ktech chassis</Pill>
          <Pill>73–87 short prototype</Pill>
          <Pill>No prices</Pill>
        </Row>
        <H1>C10 frame geometry</H1>
        <Text tone="secondary">
          Taped 2026-09-01 on a squarebody. Wilwood 831-14202 locked. Fusion
          parameters match this sheet. Prices stay on the C10 build sheet.
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Stat value="33.5 in" label="Core C-C (taped)" />
        <Stat value="42.5 in" label="Mid / cab-front C-C" tone="info" />
        <Stat value="23.5 in" label="Back of cab C-C" />
        <Stat value="98 in" label="Core to cab-rear" tone="warning" />
      </Grid>

      <Callout tone="warning" title="Still open: core vs front axle">
        core_x is a −33 in placeholder. Tape core-bolt to front-axle centerline
        when the Wilwood is on the truck. That number slides the whole cab
        station set in Fusion.
      </Callout>

      <H2>Taped body mounts</H2>
      <Text>
        Center-to-center on the frame. Three widths, two spans. Not one cab
        width. 2×6 rails follow the core. Mid and cab-rear are weld-on hats.
      </Text>
      <PlanView />
      <Table
        headers={["Station", "Fusion", "Width C-C", "Along rail", "Vs 2×6"]}
        columnAlign={["left", "left", "right", "right", "left"]}
        striped
        rowTone={["success", "success", "success"]}
        rows={[
          [
            "Core support",
            <Code>CORE</Code>,
            "33.5 in",
            "datum",
            "Rails sit here (16.75 in off CL)",
          ],
          [
            "Mid / cab front",
            <Code>CAB_F</Code>,
            "42.5 in",
            "55 in behind core",
            "Hat ~4.5 in outboard of tube",
          ],
          [
            "Back of cab",
            <Code>CAB_R</Code>,
            "23.5 in",
            "43 in behind mid",
            "Hat ~5.0 in inboard of tube",
          ],
        ]}
      />
      <Text size="small" tone="tertiary">
        Source: shop tape, 2026-09-01. Bed mounts omitted — raised bed is free.
      </Text>

      <H2>Locked product geometry</H2>
      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader trailing={<Pill tone="success">Locked</Pill>}>
            Wilwood 831-14202
          </CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                2.5 in drop ProSpindle, 1971–1987 C10. Same knuckle on 67–72
                with 73–87 ball joints in the new A-arms. Do not order 831-14201.
                Modular hub, 5×4.75 and 5×5.
              </Text>
              <Table
                headers={["Dim", "Value"]}
                columnAlign={["left", "right"]}
                framed={false}
                rows={[
                  ["Spindle drop", "2.50 in"],
                  ["BJ spread", "9.06 in"],
                  ["Kingpin vs hub face", "82°"],
                  ["Hub face to BJ axis", "3.68 in"],
                  ["Tie rod reach", "4.09 in"],
                  ["Tie rod drop", "2.35 in"],
                ]}
              />
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Pill>A500</Pill>}>Spine and clips</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Buy two 2×6 sticks. Laser the clips. Year is hats, not a
                different tube. Slip-fit is a jig; the truck ships fully welded.
              </Text>
              <Table
                headers={["Dim", "Value"]}
                columnAlign={["left", "right"]}
                framed={false}
                rows={[
                  ["Tube", "2 × 6 × 0.188 in A500"],
                  ["Tube orientation", "6 in tall, 2 in across"],
                  ["Rail CL from vehicle CL", "16.75 in"],
                  ["Clip overlap", "14 in"],
                  ["Clip plate", "0.188 in"],
                  ["C-socket clearance", "0.030 in / side"],
                ]}
              />
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H2>Side layout (Fusion origin)</H2>
      <Text>
        Origin = front axle × ground × frame centerline. +X rear, +Y up, +Z
        passenger. Prototype wheelbase 117.5 in (73–87 short).
      </Text>
      <SideView />
      <Table
        headers={["Parameter", "Value", "Status"]}
        columnAlign={["left", "right", "left"]}
        striped
        rowTone={["neutral", "info", "neutral", "warning", "success", "success", "neutral", "neutral"]}
        rows={[
          [<Code>front_overhang</Code>, "34 in", "Estimate — horns / core"],
          [<Code>wb</Code>, "117.5 in", "Locked for first proto"],
          [<Code>rear_overhang</Code>, "42 in", "Estimate — raised bed"],
          [<Code>core_x</Code>, "−33 in", "Placeholder — tape next"],
          [<Code>cab_f_x</Code>, "core_x + 55", "Computed from tape"],
          [<Code>cab_r_x</Code>, "cab_f_x + 43", "Computed from tape"],
          [<Code>rail_bottom</Code>, "8 in", "Ride height — bags change this"],
          [<Code>spine_length</Code>, "193.5 in", "34 + 117.5 + 42"],
        ]}
      />

      <H2>Wheelbases (rear clip, not cab hats)</H2>
      <Table
        headers={["Body", "Years", "WB"]}
        columnAlign={["left", "left", "right"]}
        rowTone={[undefined, undefined, "info", undefined]}
        rows={[
          ["Short 6.5 ft", "67–72", "115.0 in"],
          ["Long 8 ft", "67–72", "127.0 in"],
          ["Short 6.5 ft (prototype)", "73–87", "117.5 in"],
          ["Long 8 ft", "73–87", "131.5 in"],
        ]}
      />

      <H2>IFS and rear</H2>
      <Grid columns={2} gap={16}>
        <Stack gap={8}>
          <H3>Front — order of design</H3>
          <Table
            headers={["Step", "Rule"]}
            rows={[
              ["1. Knuckle", "831-14202 at ride and at lay-out"],
              ["2. Travel", "32 in tire, ~11 in bag stroke"],
              ["3. Lower inner", "Arm ~level at ride, 14–16 in if fender allows"],
              ["4. Upper inner", "From BJ spread, not from the rail"],
              ["5. Rack last", "Tie rod same length as lower, parallel"],
              ["6. Engine", "Pan vs K-member ~1 in; pan vs ground at lay-out"],
            ]}
          />
          <Text size="small" tone="secondary">
            Cab stays on the taped mounts. 2×6 under the cab stays at mount_y.
            Front clip may hang below the tube. Do not kink the spine for the
            arms. Do not pinch rails for big wheels.
          </Text>
        </Stack>
        <Stack gap={8}>
          <H3>Rear 4-link</H3>
          <Table
            headers={["Item", "Lock"]}
            columnAlign={["left", "left"]}
            rows={[
              ["Lower bars", "22–24 in (20 in is the floor)"],
              ["Uppers", "Within ~1 in of the lowers"],
              ["At ride", "Level or slightly downhill to the front"],
              ["Anti-squat", "Mild"],
              ["Front pickups", "Just behind the cab"],
              ["Track width", "Housing + backspace, not rail pinch"],
            ]}
          />
        </Stack>
      </Grid>

      <H2>What is shared vs what splits</H2>
      <Table
        headers={["Share 67–87", "Split by generation"]}
        rows={[
          ["2×6 spine, clip sockets, fixture pins", "Cab / core hole pattern"],
          ["IFS and 4-link architecture", "Core support / horns vs OEM clip"],
          ["Wilwood knuckle + 73–87 BJs", "Engine-to-firewall hats"],
          ["One rail spacing (core 33.5)", "Wheelbase on the rear clip"],
        ]}
      />
      <Callout title="A500 will not telescope through a square hole">
        Clip is a 3-sided C plus closing strap, U-notch for tube radius, 0.030
        in per side. Clocking key on the tube top. Tabs proud 0.06–0.10 in.
        Laser slot ~+0.010 over plate — freeze with a coupon.
      </Callout>

      <H2>Fusion file</H2>
      <Text>
        Script: chassis/fusion/KTECH_C10_Chassis_Setup. Hybrid design, not Part.
        Run that script, not the leftover C10 hello-world. After Run, Fit view
        — rails sit 16.75 in off centerline.
      </Text>
      <Table
        headers={["Component", "What is in it now"]}
        rows={[
          ["00_ORIGIN", "6 in cube so a good run is obvious"],
          ["00_SKELETON", "SK_SIDE, SK_TOP"],
          ["01_SPINE_2x6", "Two mirrored 2×6 tubes on core width"],
          ["02_CLIP_FRONT", "Empty — next CAD"],
          ["03_CLIP_REAR", "Empty — next CAD"],
          ["04_MOUNTS_73_87", "CORE / CAB_F / CAB_R construction points"],
          ["04_MOUNTS_67_72", "Empty hat"],
          ["05_IFS", "Empty — Wilwood + arms + rack"],
          ["06_REAR", "Empty — 4-link"],
          ["07_FIXTURE", "Empty — weld table"],
        ]}
      />

      <Divider />

      <H2>Next on the Fusion PC</H2>
      <TodoListCard
        defaultExpanded
        todos={[
          {
            id: "run",
            content: "Hybrid + New Design + Run KTECH_C10_Chassis_Setup. Confirm six mount points.",
            status: "pending",
          },
          {
            id: "corex",
            content: "Tape core to front axle. Set core_x. Re-run.",
            status: "pending",
          },
          {
            id: "spindle",
            content: "Model 831-14202 on SK_SIDE from wilwood-831-14202.png.",
            status: "pending",
          },
          {
            id: "front",
            content: "Front clip C-socket + LCA inners. Do not dogleg the 2×6.",
            status: "pending",
          },
          {
            id: "rear",
            content: "Rear 4-link at 22–24 in, step around 32 in tire + 11 in bags.",
            status: "pending",
          },
        ]}
      />
    </Stack>
  );
}

function PlanView() {
  const theme = useHostTheme();
  const ink = theme.text.primary;
  const mute = theme.text.tertiary;
  const rail = theme.accent.primary;
  const line = theme.stroke.primary;
  const fill = theme.fill.tertiary;

  const scale = 8;
  const y = (halfIn: number) => 118 - halfIn * scale;
  const coreY = y(33.5 / 2);
  const midY = y(42.5 / 2);
  const rearY = y(23.5 / 2);
  const railY = y(16.75);
  const x0 = 70;
  const xCore = x0;
  const xMid = x0 + 55 * 1.6;
  const xRear = xMid + 43 * 1.6;

  return (
    <svg
      viewBox="0 0 400 236"
      width="100%"
      role="img"
      aria-label="Plan view of taped core, mid, and cab-rear widths on 2x6 rails"
    >
      <rect width="400" height="236" fill={theme.bg.editor} />
      <line x1="40" y1="118" x2="380" y2="118" stroke={mute} strokeDasharray="4 4" />
      <text x="48" y="112" fill={mute} fontSize="10" fontFamily="sans-serif">
        CL
      </text>

      <rect x={xCore} y={railY} width={xRear - xCore + 24} height={2.0 * scale} fill={rail} />
      <rect
        x={xCore}
        y={236 - railY - 2.0 * scale}
        width={xRear - xCore + 24}
        height={2.0 * scale}
        fill={rail}
      />

      <line x1={xCore} y1={coreY} x2={xCore} y2={236 - coreY} stroke={line} strokeWidth="2" />
      <line x1={xMid} y1={midY} x2={xMid} y2={236 - midY} stroke={line} strokeWidth="2" />
      <line x1={xRear} y1={rearY} x2={xRear} y2={236 - rearY} stroke={line} strokeWidth="2" />

      <circle cx={xCore} cy={coreY} r="4" fill={ink} />
      <circle cx={xCore} cy={236 - coreY} r="4" fill={ink} />
      <circle cx={xMid} cy={midY} r="4" fill={ink} />
      <circle cx={xMid} cy={236 - midY} r="4" fill={ink} />
      <circle cx={xRear} cy={rearY} r="4" fill={ink} />
      <circle cx={xRear} cy={236 - rearY} r="4" fill={ink} />

      <rect x={xCore - 28} y="8" width="56" height="18" fill={fill} />
      <text x={xCore} y="21" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        33.5
      </text>
      <rect x={xMid - 28} y="8" width="56" height="18" fill={fill} />
      <text x={xMid} y="21" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        42.5
      </text>
      <rect x={xRear - 28} y="8" width="56" height="18" fill={fill} />
      <text x={xRear} y="21" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        23.5
      </text>

      <text x={(xCore + xMid) / 2} y="228" textAnchor="middle" fill={mute} fontSize="11" fontFamily="sans-serif">
        55 in
      </text>
      <text x={(xMid + xRear) / 2} y="228" textAnchor="middle" fill={mute} fontSize="11" fontFamily="sans-serif">
        43 in
      </text>
    </svg>
  );
}

function SideView() {
  const theme = useHostTheme();
  const ink = theme.text.primary;
  const mute = theme.text.tertiary;
  const tube = theme.accent.primary;
  const clip = theme.stroke.primary;

  return (
    <svg
      viewBox="0 0 920 168"
      width="100%"
      role="img"
      aria-label="Side view: front clip, 2x6 spine, cab stations, rear clip"
    >
      <rect width="920" height="168" fill={theme.bg.editor} />
      <line x1="40" y1="130" x2="880" y2="130" stroke={mute} strokeDasharray="4 4" />
      <text x="48" y="148" fill={mute} fontSize="11" fontFamily="sans-serif">
        ground
      </text>

      <circle cx="140" cy="130" r="18" fill="none" stroke={clip} strokeWidth="2" />
      <circle cx="140" cy="130" r="3" fill={ink} />
      <text x="140" y="162" textAnchor="middle" fill={mute} fontSize="11" fontFamily="sans-serif">
        front axle / origin
      </text>

      <circle cx="610" cy="130" r="18" fill="none" stroke={clip} strokeWidth="2" />
      <text x="610" y="162" textAnchor="middle" fill={mute} fontSize="11" fontFamily="sans-serif">
        rear axle · 117.5 WB
      </text>

      <rect x="70" y="78" width="760" height="22" fill={tube} />
      <rect x="70" y="70" width="200" height="38" fill="none" stroke={clip} strokeWidth="2" />
      <path
        d="M620 70 L620 52 L830 52 L830 108 L620 108 Z"
        fill="none"
        stroke={clip}
        strokeWidth="2"
      />

      <line x1="108" y1="68" x2="108" y2="100" stroke={ink} strokeWidth="2" />
      <text x="108" y="62" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        CORE
      </text>
      <line x1="328" y1="68" x2="328" y2="100" stroke={ink} strokeWidth="2" />
      <text x="328" y="62" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        CAB_F +55
      </text>
      <line x1="500" y1="68" x2="500" y2="100" stroke={ink} strokeWidth="2" />
      <text x="500" y="62" textAnchor="middle" fill={ink} fontSize="11" fontFamily="sans-serif">
        CAB_R +43
      </text>
    </svg>
  );
}
