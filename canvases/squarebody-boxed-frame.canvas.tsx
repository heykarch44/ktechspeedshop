import {
  Callout,
  Card,
  CardBody,
  CardHeader,
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
  useHostTheme,
} from "cursor/canvas";

export default function SquarebodyBoxedFrame() {
  return (
    <Stack gap={28} style={{ padding: 24, maxWidth: 1080 }}>
      <Stack gap={8}>
        <Row gap={8} align="center">
          <Pill tone="info">Ktech chassis</Pill>
          <Pill>2×6 tube spine</Pill>
          <Pill>Fusion 360</Pill>
        </Row>
        <H1>2×6 spine, plate clips, weld-on mounts</H1>
        <Text tone="secondary">
          Front and rear clips locate on a purchased 2×6 tube. Year/model is
          weld-on hats. Slip-fit is how you fixture it. The truck still leaves
          the shop as one fully welded chassis — that is the RevB quality bar.
        </Text>
      </Stack>

      <Grid columns={3} gap={12}>
        <Stat value="2×6 × .188" label="A500 spine, two sticks" />
        <Stat value="12–16 in" label="Clip overlap on the tube" tone="info" />
        <Stat value="Body, not frame" label="What you scan" />
      </Grid>

      <Callout tone="warning" title="Do not copy an OEM rail in CAD">
        Scan or tram the cab, bed, and core support. An old C-channel is rusty,
        twisted, and shaped for leaf springs — not for bags, a step, and 24×15s.
        Hard points come from the body. The new rail is a clean 2×6 with
        designed clips.
      </Callout>

      <H2>How the kit is actually built</H2>
      <SpineSchematic />

      <Grid columns={3} gap={12}>
        <Card>
          <CardHeader trailing={<Pill>Buy</Pill>}>2×6 spine</CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              Two lengths of A500 2×6 × 3/16 (or .250 if you want it dumb-stout).
              Cut to long-bed max plus trim. This is the only part that is not
              laser plate. Clocking key on the top face of each tube.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Pill tone="info">Laser</Pill>}>
            Front / rear clips
          </CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              Tab-slot plate assemblies. Each has a 12–16 in socket that sits
              on the tube — open C plus a closing strap, not a closed square
              that has to telescope over A500 corner radii. Front = horns, IFS,
              core support. Rear = step/kick, 4-link, bumper.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Pill tone="warning">Hats</Pill>}>
            Weld-on mounts
          </CardHeader>
          <CardBody>
            <Text size="small" tone="secondary">
              Cab, bed, engine, trans, bumper as separate laser kits. 67–72 and
              73–87 are different hats on the same spine. Width of the rails
              stays one number; year only changes hole pattern and height.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="danger" title="A500 will not slip through a square hole">
        Rectangular tube has large exterior corner radii, a weld seam, and
        mill tolerance. A laser-cut 2.00 × 6.00 box will hang. Make the clip a
        three-sided C that drops over the tube, keyed to a strip on top, then
        weld the bottom strap and the perimeter. Slip is for location. Final
        structure is weld.
      </Callout>

      <H2>What RevB is actually selling</H2>
      <Text>
        They are not selling a clever splice. They sell a finished vehicle
        platform, generation-specific (67–72 and 73–87 are separate SKUs),
        fixture-welded front to back. Steal the product completeness, not the
        rail shape.
      </Text>
      <Table
        headers={["RevB does this", "What that means for Ktech"]}
        rows={[
          [
            "Separate chassis per generation",
            "Same 2×6 + clips; different mount hats. Do not share cab holes.",
          ],
          [
            "Lays out on 24×15 / 32 in rear tire, ~11 in lift",
            "Lock a tire and bag stroke in Fusion before you cut plate.",
          ],
          [
            "Change a rear wheel without pulling the bed",
            "Step, bag, and shock packaging is the hard CAD, not the rail.",
          ],
          [
            "Wiring access plates, tie-downs, tank, 9 in to spec",
            "Design the chassis as a shop product, not two sticks and hope.",
          ],
          [
            "Fully welded, not a customer slip-together",
            "Use slip to fixture in your jig. Weld it solid before it ships.",
          ],
        ]}
      />

      <H2>Width and “narrowing for big wheels”</H2>
      <Text>
        Keep one rail spacing for every year. Cab and bed mounts sit on that
        width. Track width is a different number — it is housing length plus
        backspacing, not how close the 2×6s are. For 24×15s you usually step
        the rear clip and keep the rails wide enough that a triangulated 4-link
        still has leverage. If you pinch the rails too far in, the truck looks
        like a go-kart and the link geometry gets short.
      </Text>
      <Table
        headers={["Dimension", "Freeze from", "Do not freeze from"]}
        rows={[
          [
            "Rail spacing",
            "Cab floor / bed mounts / exhaust / inner fender",
            "A rusty OEM frame that already kicked in",
          ],
          [
            "Track / 9 in width",
            "Wheel, backspace, tire, fender lip",
            "Whatever the donor housing was",
          ],
          [
            "Rear step",
            "Bag at lay-out + 32 in tire + bed floor",
            "OEM kick-up for leaf springs",
          ],
        ]}
      />

      <H2>Fusion 360 — file structure</H2>
      <Text>
        One Design. Skeleton first, parts second. Configurations for year and
        wheelbase. I cannot drop a .f3d into your Autodesk account from here —
        start this file, then we can fill sketches from your hard-point sheet.
      </Text>
      <Table
        headers={["Browser component", "What lives in it"]}
        rows={[
          [
            "00_SKELETON",
            "Origin at front axle × frame CL × ground. Layout sketches: top, side, front. All parameters.",
          ],
          [
            "01_SPINE_2x6",
            "Two mirrored A500 tubes. Length driven by wheelbase. Clocking key.",
          ],
          [
            "02_CLIP_FRONT",
            "Sheet-metal / plate tab-slot. Socket on the tube. IFS pickups, horns.",
          ],
          [
            "03_CLIP_REAR",
            "Step profile, 4-link pickups, bag cups, bumper. Socket on the tube.",
          ],
          [
            "04_MOUNTS_67_72",
            "Cab, bed, core support, engine, trans. Suppressed in 73–87 config.",
          ],
          [
            "04_MOUNTS_73_87",
            "Same idea, different holes. Default config for the first prototype.",
          ],
          [
            "05_IFS / 06_REAR",
            "Arms, rack, bags, housing as separate assemblies joined to the clips.",
          ],
          [
            "07_FIXTURE",
            "Weld table with the same pin holes as the clips. Laser this first.",
          ],
        ]}
      />

      <H3>Parameters to create before you draw anything</H3>
      <Table
        headers={["Name", "Start value", "Drives"]}
        columnAlign={["left", "right", "left"]}
        striped
        rows={[
          ["rail_h", "2.00 in", "Tube height"],
          ["rail_w", "6.00 in", "Tube width (tall way = 6 in)"],
          ["wall", "0.188 in", "Tube wall"],
          ["clip_t", "0.188 in", "Plate thickness"],
          ["clip_clear", "0.030 in", "Per side on the C-socket"],
          ["overlap", "14.00 in", "Clip on tube"],
          ["rail_spacing", "measure", "Inside-to-inside at the cab"],
          ["wb", "117.50 in", "73–87 short default"],
          ["track_f / track_r", "from wheel", "Spindle / housing, not rails"],
          ["tire_od", "32.00 in", "Lay-out lock"],
          ["bag_stroke", "11.00 in", "RevB-class travel target"],
          ["step_drop", "from bag + tire", "Rear clip profile"],
        ]}
      />

      <H2>Scan workflow in Fusion</H2>
      <Text>
        Scan a straight cab and bed on jack stands, plus the core support if
        you have one. Optional: scan a frame only to steal mount-hole
        coordinates, then throw the mesh away. Polycam, Revopoint, or an Einscan
        is enough if you scale with a tape on three known distances.
      </Text>
      <Table
        headers={["Step", "Fusion command", "Purpose"]}
        rows={[
          [
            "1. Insert STL",
            "Insert → Insert Mesh",
            "Keep it as mesh. Do not Mesh to BRep the whole cab.",
          ],
          [
            "2. Align",
            "Modify → Align, 3 points",
            "Frame CL, front axle, cab back. This is your origin.",
          ],
          [
            "3. Cut sections",
            "Create → Mesh → Mesh Section Sketch",
            "A plane through each cab mount, core support, bed mount, axle.",
          ],
          [
            "4. Fit curves",
            "Fit Curves to Mesh Section",
            "Turn noisy sections into lines and points you actually dimension.",
          ],
          [
            "5. Project to skeleton",
            "Project / Include to 00_SKELETON sketches",
            "Hard points become parameters. Hide the mesh after this.",
          ],
          [
            "6. Build solids",
            "Tube extrusion + sheet metal / extrude plate",
            "Clips and hats are parametric. Mesh is only a ghost.",
          ],
        ]}
      />
      <Callout title="Faster than a scan if the cab is already in the shop">
        Tram it. Pick a datum (front of cab, cab CL, underside of floor). Write
        X Y Z for every mount hole on a sheet. Type those into the skeleton
        sketch. For a ladder frame this often beats a warped photogrammetry
        mesh.
      </Callout>

      <H2>Plate clips in Fusion (no native tab-slot)</H2>
      <Text>
        Fusion has no SolidWorks-style Tab and Slot. Model one clip as
        components, then cut. Sheet metal is optional — for 3/16 with no
        brakes, stay in Solid: extrude flats, Combine → Cut the slots from the
        mating tabs, then Create → Drawing or save-as DXF from each face.
      </Text>
      <Grid columns={2} gap={16}>
        <Stack gap={6}>
          <Text weight="semibold">Per clip</Text>
          <Text size="small">
            Inner web, outer web, top cap, bulkheads. Tabs proud 0.06–0.10 in.
            Slot = clip_t + kerf table (laser ~0.010). Socket is a 3-sided C
            sized rail_h + 2×clip_clear by rail_w + 2×clip_clear, with a
            U-notch for the A500 corner radius so it drops on, not fights it.
          </Text>
        </Stack>
        <Stack gap={6}>
          <Text weight="semibold">Configs</Text>
          <Text size="small">
            Fusion Configurations: column for gen (67–72 / 73–87) suppresses
            the other mount hat. Column for wb (115 / 117.5 / 127 / 131.5)
            changes tube length and where the rear clip sits. One model, four
            pickup SKUs.
          </Text>
        </Stack>
      </Grid>

      <Divider />

      <H2>Build order in CAD this week</H2>
      <Table
        headers={["Order", "Do this"]}
        rows={[
          [
            "1",
            "New Fusion Design named KTECH_C10_CHASSIS. Create the parameter list above.",
          ],
          [
            "2",
            "Empty skeleton: three layout sketches and two 2×6 tubes mirrored. No clips yet.",
          ],
          [
            "3",
            "Put a 73–87 cab and bed on stands. Scan or tram mount holes into a spreadsheet.",
          ],
          [
            "4",
            "Drop those points on the skeleton. Then model the rear clip step around a 32 in tire and bag stroke.",
          ],
          [
            "5",
            "Front clip + IFS pickups. Mount hats last — they are the easy plates.",
          ],
        ]}
      />
      <Text size="small" tone="tertiary">
        Prototype the 73–87 short first. Same spine and clips cover 67–72 once
        the second hat exists. K-series is a different front clip, later.
      </Text>
    </Stack>
  );
}

function SpineSchematic() {
  const theme = useHostTheme();
  const ink = theme.text.primary;
  const mute = theme.text.tertiary;
  const tube = theme.accent.primary;
  const clip = theme.stroke.primary;

  return (
    <svg
      viewBox="0 0 920 200"
      width="100%"
      role="img"
      aria-label="Side view of 2x6 tube spine with front and rear plate clips slipping over it"
    >
      <rect width="920" height="200" fill={theme.bg.editor} />
      <rect x="60" y="78" width="800" height="28" fill={tube} />
      <rect x="60" y="70" width="240" height="44" fill="none" stroke={clip} strokeWidth="3" />
      <rect x="620" y="70" width="240" height="44" fill="none" stroke={clip} strokeWidth="3" />
      <path
        d="M620 70 L620 50 L860 50 L860 114 L620 114 Z"
        fill="none"
        stroke={clip}
        strokeWidth="3"
      />
      <text x="180" y="40" textAnchor="middle" fill={ink} fontSize="13" fontFamily="sans-serif">
        Front clip (plate)
      </text>
      <text x="460" y="40" textAnchor="middle" fill={ink} fontSize="13" fontFamily="sans-serif">
        2×6 tube spine
      </text>
      <text x="740" y="40" textAnchor="middle" fill={ink} fontSize="13" fontFamily="sans-serif">
        Rear clip + step
      </text>
      <text x="460" y="170" textAnchor="middle" fill={mute} fontSize="12" fontFamily="sans-serif">
        Clips drop onto the tube, key, then weld. Mount hats weld to the tube and clips.
      </text>
    </svg>
  );
}
