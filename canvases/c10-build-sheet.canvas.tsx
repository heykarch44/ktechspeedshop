import {
  BarChart,
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Link,
  PieChart,
  Pill,
  Row,
  Select,
  Spacer,
  Stack,
  Stat,
  Swatch,
  Table,
  Text,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";

type Gen = "6772" | "7387";
type SectionId = "body" | "chassis" | "drivetrain" | "interior";

type Option = {
  id: string;
  label: string;
  sku: string;
  price: number;
  years?: Gen[];
  href?: string;
  includesRearBrakes?: boolean;
  includesShocks?: boolean;
};

type Line = {
  id: string;
  name: string;
  brand: string;
  locked?: boolean;
  options: Option[];
};

type Section = {
  id: SectionId;
  title: string;
  blurb: string;
  color: "blue" | "orange" | "green" | "purple";
  lines: Line[];
};

const SOURCE =
  "Street prices pulled Aug 23, 2026 from Summit, Wilwood, Currie, Ringbrothers, AutoMeter, United Pacific, Aces EFI, Vintage Air, US Mags, and dealer listings. Parts only — no paint, labor, or freight.";

const SECTIONS: Section[] = [
  {
    id: "body",
    title: "Body",
    blurb: "Lights are United Pacific. Mirrors, door pulls, and hood hinges are Ringbrothers. Sheet metal is Premier. Wider tubs are Hart Fab.",
    color: "blue",
    lines: [
      {
        id: "lights",
        name: "Lights",
        brand: "United Pacific",
        locked: true,
        options: [
          {
            id: "up-full-7387",
            label: "Ultralit 7\" LED pair + 56-LED sequential tails + flasher",
            sku: "31459 + CTL7387LED",
            price: 572,
            years: ["7387"],
            href: "https://upcarparts.com/products/56-led-sequential-tail-light-without-trim-for-1973-87-chevy-gmc-truck",
          },
          {
            id: "up-full-6772",
            label: "Ultralit 7\" LED pair + sequential LED tails",
            sku: "31459 + 67-72 sequential",
            price: 570,
            years: ["6772"],
            href: "https://upcarparts.com/",
          },
          {
            id: "up-tails-only-7387",
            label: "Sequential LED tails with trim + flasher, keep sealed beams",
            sku: "Speedway 73-87 kit",
            price: 221,
            years: ["7387"],
            href: "https://www.speedwaymotors.com/United-Pacific-LED-Sequential-Tail-Lights-1973-87-C-K-w-Flasher,485952.html",
          },
        ],
      },
      {
        id: "grille",
        name: "Grille",
        brand: "Brothers / LMC",
        options: [
          {
            id: "brothers-chrome-7387",
            label: "Brothers chrome grille, 73–80",
            sku: "Brothers grille",
            price: 289,
            years: ["7387"],
          },
          {
            id: "brothers-chrome-81",
            label: "Brothers chrome grille, 81–87",
            sku: "Brothers 81–87 grille",
            price: 319,
            years: ["7387"],
          },
          {
            id: "brothers-6772",
            label: "Brothers chrome grille, 67–72",
            sku: "Brothers 67–72 grille",
            price: 349,
            years: ["6772"],
          },
          {
            id: "billet-grille",
            label: "Billet Specialties insert, painted shell",
            sku: "Billet insert",
            price: 620,
          },
        ],
      },
      {
        id: "bumpers",
        name: "Bumpers",
        brand: "Brothers",
        options: [
          {
            id: "brothers-chrome",
            label: "Brothers chrome front + rear, stock contour",
            sku: "Brothers bumper pair",
            price: 468,
          },
          {
            id: "brothers-smooth",
            label: "Brothers smooth chrome, no holes",
            sku: "Smooth pair",
            price: 680,
          },
          {
            id: "roll-pan-rear",
            label: "Chrome front + roll pan rear",
            sku: "Front bumper + roll pan",
            price: 540,
          },
        ],
      },
      {
        id: "glass",
        name: "Glass",
        brand: "Auto City Classic",
        options: [
          {
            id: "acc-windshield",
            label: "Windshield, door glass, back glass — clear",
            sku: "ACC C10 glass set",
            price: 1120,
          },
          {
            id: "acc-tint",
            label: "Same set, factory green tint",
            sku: "ACC tinted set",
            price: 1280,
          },
          {
            id: "windshield-only",
            label: "Windshield only, reuse side/back",
            sku: "ACC windshield",
            price: 285,
          },
        ],
      },
      {
        id: "core",
        name: "Core support",
        brand: "Premier",
        options: [
          {
            id: "core-keep",
            label: "Keep original core support",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-core-7380",
            label: "Premier radiator support, 73–80",
            sku: "Premier core 73–80",
            price: 349,
            years: ["7387"],
          },
          {
            id: "premier-core-8187",
            label: "Premier radiator support, 81–87",
            sku: "Premier core 81–87",
            price: 379,
            years: ["7387"],
          },
          {
            id: "premier-core-6772",
            label: "Premier radiator support, 67–72",
            sku: "Premier core 67–72",
            price: 329,
            years: ["6772"],
          },
        ],
      },
      {
        id: "fenders",
        name: "Fenders",
        brand: "Premier",
        options: [
          {
            id: "fenders-keep",
            label: "Keep original fenders",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-fenders",
            label: "Premier front fenders, pair",
            sku: "Premier fender pair",
            price: 438,
          },
        ],
      },
      {
        id: "hood",
        name: "Hood",
        brand: "Premier",
        options: [
          {
            id: "hood-keep",
            label: "Keep original hood",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-hood",
            label: "Premier stock-contour hood",
            sku: "Premier hood",
            price: 449,
          },
          {
            id: "premier-cowl",
            label: "Premier 2-inch cowl hood",
            sku: "Premier 2in cowl",
            price: 400,
          },
        ],
      },
      {
        id: "hoodHinges",
        name: "Hood hinges",
        brand: "Ringbrothers",
        options: [
          {
            id: "rb-hinges-6772",
            label: "Ringbrothers billet air-frame, steel hood, 67–72",
            sku: "RB 67-72 steel",
            price: 800,
            years: ["6772"],
            href: "https://www.ringbrothers.com/1967-1972-chevy-truck-hood-hinge-kit-air-frame-steel-natural",
          },
          {
            id: "rb-hinges-7380",
            label: "Ringbrothers billet solid-frame, steel hood, 73–80",
            sku: "1173 NS",
            price: 800,
            years: ["7387"],
            href: "https://www.ringbrothers.com/1973-1980-chevy-truck-hood-hinge-kit-solid-frame-steel-natural",
          },
          {
            id: "eddie-hinges",
            label: "Eddie Motorsports slammed billet, 73–80",
            sku: "MS149-24",
            price: 755,
            years: ["7387"],
            href: "https://eddiemotorsports.com/products/hood-hinges-73-80-chevy-truck",
          },
          {
            id: "hinges-keep",
            label: "Keep original hinges",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "mirrors",
        name: "Mirrors",
        brand: "Ringbrothers",
        options: [
          {
            id: "rb-rect-black",
            label: "Ringbrothers rectangular billet, black, pair",
            sku: "9019 B",
            price: 680,
            href: "https://www.ringbrothers.com/mirrors",
          },
          {
            id: "rb-round-black",
            label: "Ringbrothers round billet, black, pair",
            sku: "9018 B",
            price: 680,
            href: "https://www.ringbrothers.com/mirrors",
          },
          {
            id: "rb-rect-nat",
            label: "Ringbrothers rectangular billet, natural, pair",
            sku: "9019 N",
            price: 650,
            href: "https://www.ringbrothers.com/mirrors",
          },
        ],
      },
      {
        id: "cab",
        name: "Cab",
        brand: "Premier",
        options: [
          {
            id: "cab-keep",
            label: "Keep original cab",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-cab-repair",
            label: "Premier cab corners + rockers",
            sku: "Premier cab repair",
            price: 249,
          },
          {
            id: "premier-cab-floors",
            label: "Premier floors + corners + rockers",
            sku: "Premier cab structure",
            price: 529,
          },
          {
            id: "premier-cab-shell",
            label: "Replacement cab shell, freight extra",
            sku: "Premier / used cab",
            price: 4200,
          },
        ],
      },
      {
        id: "bed",
        name: "Bed",
        brand: "Premier",
        options: [
          {
            id: "bed-keep",
            label: "Keep original bed",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-bed-floor",
            label: "Premier steel bed floor, short",
            sku: "Premier floor SWB",
            price: 640,
          },
          {
            id: "premier-bed-short",
            label: "Premier complete fleetside, short",
            sku: "Premier SWB bed",
            price: 2890,
          },
        ],
      },
      {
        id: "tailgate",
        name: "Tailgate",
        brand: "Premier",
        options: [
          {
            id: "tailgate-keep",
            label: "Keep original tailgate",
            sku: "—",
            price: 0,
          },
          {
            id: "premier-tailgate",
            label: "Premier fleetside tailgate",
            sku: "Premier tailgate",
            price: 329,
          },
        ],
      },
      {
        id: "tubs",
        name: "Wider tubs",
        brand: "Hart Fab",
        options: [
          {
            id: "tubs-stock",
            label: "Keep stock inners and bed tubs",
            sku: "—",
            price: 0,
          },
          {
            id: "hartfab-inners",
            label: "Hart Fab slammed inner fenders, pair",
            sku: "Hart Fab C10 inners",
            price: 995,
            href: "https://hart-fab.com/products/73-80-c10-inner-fenders-22-wheel",
          },
          {
            id: "hartfab-bed",
            label: "Hart Fab raised bed-floor tubs, pair",
            sku: "Hart Fab bed tubs",
            price: 695,
            href: "https://hart-fab.com/products/raised-bed-floor-tubs",
          },
          {
            id: "hartfab-both",
            label: "Hart Fab inners + raised bed tubs",
            sku: "Hart Fab inners + tubs",
            price: 1690,
          },
        ],
      },
      {
        id: "weatherstrip",
        name: "Weatherstrip",
        brand: "Metro / Steele",
        options: [
          {
            id: "weather-full",
            label: "Full cab weatherstrip — doors, glass, cab, tailgate",
            sku: "Metro C10 kit",
            price: 395,
          },
          {
            id: "weather-keep",
            label: "Reuse original seals",
            sku: "—",
            price: 0,
          },
        ],
      },
    ],
  },
  {
    id: "chassis",
    title: "Chassis",
    blurb: "Ktech 2×6 spine. Ride is QA1 coilovers or AccuAir dual-compressor. Spindles, calipers, booster, and EPB rears are Wilwood.",
    color: "orange",
    lines: [
      {
        id: "frame",
        name: "Chassis",
        brand: "Ktech",
        locked: true,
        options: [
          {
            id: "ktech-26",
            label: "2×6 A500 spine, plate clips, A-arms, 4-link, year hats",
            sku: "KTECH-C10-26",
            price: 12500,
          },
        ],
      },
      {
        id: "spindles",
        name: "Spindles",
        brand: "Wilwood",
        locked: true,
        options: [
          {
            id: "wilwood-831-14202",
            label: "ProSpindle 2.5\" drop, forged alum, hubs + arms, pair",
            sku: "831-14202",
            price: 853,
            href: "https://www.summitracing.com/parts/wil-831-14202",
          },
        ],
      },
      {
        id: "frontBrakes",
        name: "Front brakes",
        brand: "Wilwood",
        locked: true,
        options: [
          {
            id: "wilwood-12-sl4",
            label: "12.19\" Superlite 4R, slotted, black",
            sku: "140-15302",
            price: 1645,
          },
          {
            id: "wilwood-14-sl6",
            label: "14\" Superlite 6R, drilled + slotted, black",
            sku: "140-15304-D",
            price: 2330,
            href: "https://azproperformance.com/products/wilwood-14-front-superlite-6r-for-aluminum-pro-spindle-60-87-c10-140-15304-d",
          },
          {
            id: "wilwood-14-aero",
            label: "14\" Aero6, drilled + slotted, black",
            sku: "140-15305-D",
            price: 2596,
            href: "https://www.accesspeed.com/wilwood-140-15305-d-aero6-front-14-in-brake-kit-black-drilled-1963-1987-c-10-w-wilwood-pro-spindles.html",
          },
        ],
      },
      {
        id: "rearBrakes",
        name: "Rear brakes",
        brand: "Wilwood",
        locked: true,
        options: [
          {
            id: "wilwood-14-epb",
            label: "12.88\" FNSL4R + EPB — calipers, control unit, switch, harness, Big Ford 9\"",
            sku: "140-15844",
            price: 3411,
            href: "https://www.wilwood.com/BrakeKits/BrakeKitsProdRear?itemno=140-15844-DR",
          },
          {
            id: "wilwood-11-4p",
            label: "11\" 4-piston, cable parking brake, 9\" housing",
            sku: "Wilwood 11\" 9-inch kit",
            price: 1495,
          },
          {
            id: "wilwood-14-rear",
            label: "14\" Superlite rear, cable parking brake, 9\" housing",
            sku: "Wilwood 14\" rear",
            price: 1895,
          },
          {
            id: "rear-included",
            label: "Included with Currie crate — do not add",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "booster",
        name: "Booster / master",
        brand: "Wilwood",
        locked: true,
        options: [
          {
            id: "wilwood-tandem-boost",
            label: "9\" booster + Wilwood tandem master + combo valve",
            sku: "261-13269-BK + 9in booster",
            price: 880,
            href: "https://www.wilwood.com/MasterCylinders/MasterCylinderProdAcc?itemno=261-13269-BK",
          },
          {
            id: "wilwood-tandem-only",
            label: "Wilwood tandem master + combo valve, manual",
            sku: "261-13269-BK",
            price: 476,
            href: "https://www.wilwood.com/MasterCylinders/MasterCylinderProdAcc?itemno=261-13269-BK",
          },
        ],
      },
      {
        id: "brakeLines",
        name: "Brake lines",
        brand: "Ktech",
        locked: true,
        options: [
          {
            id: "brake-lines-custom",
            label: "Custom stainless brake lines, hard line + AN, shop-built",
            sku: "KTECH brake lines",
            price: 600,
          },
        ],
      },
      {
        id: "air",
        name: "Ride",
        brand: "QA1 / AccuAir",
        options: [
          {
            id: "qa1-da",
            label: "QA1 double-adjustable coilovers, set of 4",
            sku: "QA1 DA C10 set",
            price: 1995,
            includesShocks: true,
            href: "https://www.qa1.net/",
          },
          {
            id: "qa1-sa",
            label: "QA1 single-adjustable coilovers, set of 4",
            sku: "QA1 SA C10 set",
            price: 1495,
            includesShocks: true,
            href: "https://www.qa1.net/",
          },
          {
            id: "accuair-dual",
            label: "AccuAir Height+ VU4, dual compressor, Slam SS7",
            sku: "AccuAir Height+ dual",
            price: 3890,
            href: "https://airslamit.com/collections/1973-1987-chevy-c10-accuair-air-ride-suspension-kits",
          },
          {
            id: "accuair-pressure-dual",
            label: "AccuAir Pressure+ VU4, dual compressor, Slam SS7",
            sku: "AccuAir Pressure+ dual",
            price: 2775,
            href: "https://airslamit.com/products/chevrolet-accuair-e-level-pressure-vu4-manifold-air-management-x-series-for-1973-1987-c10-2wd",
          },
        ],
      },
      {
        id: "shocks",
        name: "Shocks",
        brand: "Viking / JRI",
        options: [
          {
            id: "viking",
            label: "Viking double-adjustable, set of 4",
            sku: "Viking Cruiser C10",
            price: 1080,
          },
          {
            id: "jri",
            label: "JRI single-adjustable, set of 4",
            sku: "JRI C10",
            price: 1840,
          },
          {
            id: "ridetech-hq",
            label: "RideTech HQ Series, set of 4",
            sku: "RideTech HQ",
            price: 996,
          },
        ],
      },
      {
        id: "steering",
        name: "Steering",
        brand: "Flaming River",
        options: [
          {
            id: "fr-power",
            label: "Flaming River hydraulic rack and pinion + pump",
            sku: "FR rack kit",
            price: 1850,
          },
          {
            id: "sweet",
            label: "Sweet Mfg hydraulic rack and pinion",
            sku: "Sweet rack",
            price: 2400,
          },
          {
            id: "epas-rack",
            label: "EPAS electric rack and pinion, 67–87 C10",
            sku: "EPAS 1105",
            price: 2625,
            href: "https://epasperformance.com/products/chevrolet-c10",
          },
          {
            id: "fr-microsteer",
            label: "Flaming River Microsteer electric assist",
            sku: "FR40200KT",
            price: 2300,
            href: "https://www.flamingriver.com/electronic-power-assisted-steering/fr40200kt-microsteer-electric-power-steering",
          },
        ],
      },
      {
        id: "battery",
        name: "Battery",
        brand: "Optima",
        options: [
          {
            id: "optima-single",
            label: "YellowTop D34/78, one battery",
            sku: "D34/78",
            price: 320,
            href: "https://www.optimabatteries.com/products/yellowtop-d34-78",
          },
          {
            id: "optima-dual",
            label: "YellowTop D34/78 pair — EPAS, power brakes, or air ride",
            sku: "D34/78 pair",
            price: 640,
            href: "https://www.optimabatteries.com/products/yellowtop-d34-78",
          },
        ],
      },
      {
        id: "steeringShaft",
        name: "Steering shaft",
        brand: "Flaming River",
        options: [
          {
            id: "fr-shaft",
            label: "Flaming River DD shaft + U-joints, column to rack",
            sku: "FR shaft kit",
            price: 285,
          },
        ],
      },
      {
        id: "psHoses",
        name: "PS hoses",
        brand: "Aeroquip",
        options: [
          {
            id: "ps-hoses",
            label: "Custom -6 AN power-steering hoses, hydraulic rack",
            sku: "Shop PS hoses",
            price: 185,
          },
          {
            id: "ps-na",
            label: "N/A — electric rack, no pump hoses",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "swayBars",
        name: "Sway bars",
        brand: "QA1 / Hotchkis",
        options: [
          {
            id: "qa1-bars",
            label: "QA1 front + rear sway bars",
            sku: "QA1 C10 bars",
            price: 520,
          },
          {
            id: "sway-na",
            label: "N/A — no sway bars",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "wheels",
        name: "Wheels",
        brand: "US Mags / Intro / Schott",
        options: [
          {
            id: "usmags-indy-15",
            label: "US Mags Indy 15×8 / 15×10 polished, 5×5",
            sku: "U101 staggered set",
            price: 1150,
          },
          {
            id: "usmags-22-rambler",
            label: "US Mags Rambler 22×9 / 22×11 gunmetal, 5×5",
            sku: "U111 staggered set",
            price: 2140,
            href: "https://www.summitracing.com/parts/usm-u11122117367",
          },
          {
            id: "intro-24",
            label: "Intro custom 24×12 / 24×15, 5×5",
            sku: "Intro 24 staggered",
            price: 5600,
          },
          {
            id: "schott-24",
            label: "Schott Magnum 24×12 / 24×15 billet, 5×5",
            sku: "Schott Magnum set",
            price: 7800,
          },
        ],
      },
      {
        id: "tires",
        name: "Tires",
        brand: "Nitto / Toyo",
        options: [
          {
            id: "bfg-15",
            label: "BFGoodrich Radial T/A, 15\" staggered",
            sku: "Radial T/A set",
            price: 720,
          },
          {
            id: "nitto-22",
            label: "Nitto NT555 G2 265/35-22 + 305/35-22",
            sku: "NT555 G2 set",
            price: 1280,
          },
          {
            id: "toyo-24",
            label: "Toyo Proxes ST 275/30-24 + 335/30-24",
            sku: "Proxes ST set",
            price: 2100,
          },
        ],
      },
    ],
  },
  {
    id: "drivetrain",
    title: "Drivetrain",
    blurb: "ECU is Aces EFI. Rear is Currie 9-inch. Trans cooler is always on. First-fill fluids are a shop kit.",
    color: "green",
    lines: [
      {
        id: "engine",
        name: "Engine",
        brand: "Chevrolet Performance",
        options: [
          {
            id: "lq4",
            label: "LQ4 6.0 dressed takeout, fresh seals",
            sku: "LQ4 takeout",
            price: 4500,
          },
          {
            id: "ls3-430",
            label: "LS3 6.2 430 hp crate, 19540155",
            sku: "19540155",
            price: 10800,
            href: "https://www.gmperformancemotor.com/parts/19540155.html",
          },
          {
            id: "lt1",
            label: "LT1 6.2 crate, Gen V",
            sku: "Chevrolet Performance LT1",
            price: 12900,
          },
          {
            id: "lt4",
            label: "LT4 6.2 supercharged crate",
            sku: "Chevrolet Performance LT4",
            price: 21800,
          },
        ],
      },
      {
        id: "ecu",
        name: "ECU",
        brand: "Aces EFI",
        locked: true,
        options: [
          {
            id: "aces-jackpot2",
            label: "Jackpot 2 LS EFI, standalone ECU + harness",
            sku: "Jackpot 2 LS",
            price: 990,
            href: "https://acesefi.com/collections/ls-efi-systems",
          },
          {
            id: "aces-tbi",
            label: "Jackpot 2 LS TBI, four 100 lb/hr, classic look",
            sku: "Jackpot 2 TBI",
            price: 1090,
            href: "https://acesefi.com/products/jackpot-ls-efi-tbi-system-1",
          },
          {
            id: "aces-master",
            label: "Jackpot 2 Master, in-tank pump + PTFE hose",
            sku: "Jackpot 2 Master",
            price: 2090,
            href: "https://acesefi.com/collections/jackpot-2-ls-kits",
          },
        ],
      },
      {
        id: "trans",
        name: "Transmission",
        brand: "GM / TREMEC",
        options: [
          {
            id: "4l80e",
            label: "4L80E reman, 2WD, converter",
            sku: "4L80E 2WD",
            price: 2800,
          },
          {
            id: "6l80e",
            label: "6L80E reman, 2WD slip yoke, converter",
            sku: "6L80E 2WD",
            price: 3020,
            href: "https://powertraincompany.com/product/6l80e-2wd-slip-yoke-remanufactured-automatic-transmission-assembly-cadillac-chevrolet-gmc-2014-2018/",
          },
          {
            id: "tkx",
            label: "TREMEC TKX 5-speed, mechanical",
            sku: "TKX",
            price: 3399,
          },
          {
            id: "10l80",
            label: "10L80 reman, 2WD",
            sku: "10L80 2WD",
            price: 6200,
          },
        ],
      },
      {
        id: "rearend",
        name: "Rear end",
        brand: "Currie",
        locked: true,
        options: [
          {
            id: "currie-housing",
            label: "Centurion housing + 31-spline axles, 5×5",
            sku: "Currie housing/axle",
            price: 1550,
            href: "https://www.currieenterprises.com/60-87-chevy-c10-9-inch-housing-and-axle-package",
          },
          {
            id: "currie-third",
            label: "Housing + Sportsman 3rd, 3.70 Truetrac, 31-spline",
            sku: "Currie housing + 3rd",
            price: 3350,
            href: "https://www.currieenterprises.com/63-87-c10-1500-rear-ends",
          },
          {
            id: "currie-crate",
            label: "Assembled crate, Truetrac, 3.70, 11\" Wilwood",
            sku: "Currie crate + Wilwood",
            price: 4700,
            includesRearBrakes: true,
            href: "https://www.redbirdspeed.com/product-page/fully-assembled-1970-1972-chevy-c10-9-rear-wilwood-currie-enterprises",
          },
        ],
      },
      {
        id: "headers",
        name: "Headers",
        brand: "Ultimate Headers",
        options: [
          {
            id: "ultimate-c10",
            label: "Ultimate Headers LS long-tube, 64–87 C10",
            sku: "Ultimate C10 LS",
            price: 1659,
            href: "https://ultimateheaders.com/shop/",
          },
          {
            id: "custom-ss-headers",
            label: "Custom 304 stainless long-tubes, shop-built",
            sku: "Custom SS headers",
            price: 1800,
          },
        ],
      },
      {
        id: "pipes",
        name: "Exhaust pipes",
        brand: "Custom stainless",
        options: [
          {
            id: "custom-ss-pipes",
            label: "Custom 3\" 304 stainless, header-back, X-pipe",
            sku: "Shop 3in stainless",
            price: 1200,
          },
          {
            id: "custom-ss-hpipe",
            label: "Custom 3\" 304 stainless, H-pipe",
            sku: "Shop 3in H-pipe",
            price: 980,
          },
        ],
      },
      {
        id: "mufflers",
        name: "Mufflers",
        brand: "MagnaFlow",
        options: [
          {
            id: "magnaflow-pair",
            label: "MagnaFlow 3\" 409 stainless, pair",
            sku: "11219 pair",
            price: 236,
            href: "https://www.summitracing.com/parts/MPE-11219",
          },
          {
            id: "magnaflow-oval",
            label: "MagnaFlow 3\" oval case, pair",
            sku: "12229 pair",
            price: 278,
            href: "https://www.summitracing.com/parts/mpe-12229",
          },
        ],
      },
      {
        id: "fuel",
        name: "Fuel",
        brand: "Tanks Inc",
        options: [
          {
            id: "tanks-inc",
            label: "Tanks Inc coated steel, in-tank pump provision",
            sku: "Tanks Inc C10",
            price: 649,
          },
          {
            id: "tanks-pump",
            label: "Tanks Inc + Aeromotive in-tank 340",
            sku: "Tanks + Aeromotive",
            price: 1040,
          },
          {
            id: "fuel-in-aces",
            label: "Pump/hose covered by Aces Master kit",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "cooling",
        name: "Cooling",
        brand: "Griffin",
        options: [
          {
            id: "griffin-ls",
            label: "Griffin aluminum LS radiator + dual fans",
            sku: "Griffin C10 LS",
            price: 789,
          },
          {
            id: "champion",
            label: "Champion aluminum 3-row + fans",
            sku: "Champion C10",
            price: 520,
          },
        ],
      },
      {
        id: "fluids",
        name: "Fluids",
        brand: "Ktech",
        locked: true,
        options: [
          {
            id: "fluids-fill",
            label: "First fill — oil, trans, coolant, brake, gear oil, PS",
            sku: "KTECH fluids",
            price: 425,
          },
        ],
      },
      {
        id: "driveshaft",
        name: "Driveshaft",
        brand: "Custom",
        options: [
          {
            id: "custom-1350",
            label: "Custom 1350, measured after chassis",
            sku: "1350 one-piece",
            price: 650,
          },
          {
            id: "custom-two-piece",
            label: "Custom 1350 two-piece, if the one-piece will not clear",
            sku: "1350 two-piece",
            price: 980,
          },
        ],
      },
      {
        id: "mounts",
        name: "Engine / trans mounts",
        brand: "Ktech / Dirty Dingo",
        options: [
          {
            id: "ls-mounts",
            label: "LS / LT mounts + trans crossmember, 2WD",
            sku: "LS mount kit",
            price: 425,
          },
        ],
      },
      {
        id: "serpentine",
        name: "Accessory drive",
        brand: "ICT / Holley",
        options: [
          {
            id: "ict-serpentine",
            label: "ICT Billet LS serpentine, alt + PS + A/C",
            sku: "ICT LS drive",
            price: 895,
          },
          {
            id: "holley-hi-ram",
            label: "Holley mid-mount accessory drive, LS",
            sku: "Holley LS drive",
            price: 1095,
          },
        ],
      },
      {
        id: "transCooler",
        name: "Trans cooler",
        brand: "Derale",
        locked: true,
        options: [
          {
            id: "derale-cooler",
            label: "Derale tube-and-fin cooler + AN lines — every trans",
            sku: "Derale cooler",
            price: 350,
          },
        ],
      },
      {
        id: "fuelLines",
        name: "Fuel lines",
        brand: "Ktech",
        options: [
          {
            id: "fuel-lines-an",
            label: "Custom PTFE AN fuel lines, tank to rail, feed + return",
            sku: "KTECH fuel lines",
            price: 450,
          },
        ],
      },
      {
        id: "shifter",
        name: "Shifter",
        brand: "Lokar",
        options: [
          {
            id: "lokar-auto",
            label: "Lokar floor shifter, 6L80 / 4L80, 16\"",
            sku: "Lokar auto",
            price: 425,
          },
          {
            id: "lokar-manual",
            label: "Lokar stick + boots, TKX",
            sku: "Lokar manual",
            price: 289,
          },
        ],
      },
    ],
  },
  {
    id: "interior",
    title: "Interior",
    blurb: "Cluster is Dakota Digital or AutoMeter analog. Door pulls are Ringbrothers. Harness is a $1,400 shop build.",
    color: "purple",
    lines: [
      {
        id: "dash",
        name: "Gauge cluster",
        brand: "Dakota Digital / AutoMeter",
        options: [
          {
            id: "dakota-vhx-7387",
            label: "Dakota Digital VHX analog/digital, direct-fit 73–87",
            sku: "VHX-73C-PU",
            price: 945,
            years: ["7387"],
            href: "https://www.dakotadigital.com/index.cfm/page/ptype=product/product_id=782/mode=prod/prd782.htm",
          },
          {
            id: "dakota-vhx-6772",
            label: "Dakota Digital VHX analog/digital, direct-fit 67–72",
            sku: "VHX-67C-PU",
            price: 995,
            years: ["6772"],
            href: "https://www.dakotadigital.com/",
          },
          {
            id: "autometer-7027",
            label: "AutoMeter Sport-Comp analog 6-gauge, direct-fit 73–83",
            sku: "7027-SC",
            price: 1689,
            years: ["7387"],
          },
          {
            id: "autometer-7045",
            label: "AutoMeter Sport-Comp analog 6-gauge, direct-fit 67–72",
            sku: "7045-SC",
            price: 1250,
            years: ["6772"],
          },
          {
            id: "autometer-invision",
            label: "AutoMeter InVision 12.3\" LCD, direct-fit 73–87",
            sku: "InVision C10",
            price: 1022,
            years: ["7387"],
            href: "https://www.autometer.com/invision-lcd-dash-kit-73-87-chevy-gmc-full-size-truck-direct-fit-digital-dash.html",
          },
        ],
      },
      {
        id: "seats",
        name: "Seats",
        brand: "TMI",
        options: [
          {
            id: "tmi-xr-buckets",
            label: "Sport XR Pro buckets + C10 tracks",
            sku: "TMI Sport XR",
            price: 1785,
            href: "https://www.canadaseatskins.us/1967-1972-chevrolet-truck-custom-interiors/tmi-pro-series-sport-xr-truck-bucket-seat-kit.html",
          },
          {
            id: "tmi-xr-console",
            label: "Sport XR buckets + waterfall console",
            sku: "TMI XR + console",
            price: 2775,
          },
          {
            id: "tmi-bench",
            label: "Sport Pro split bench + tracks",
            sku: "TMI bench",
            price: 2200,
          },
        ],
      },
      {
        id: "trim",
        name: "Trim",
        brand: "TMI",
        options: [
          {
            id: "tmi-doors-carpet",
            label: "Sport door panels + molded carpet",
            sku: "TMI doors + carpet",
            price: 1240,
          },
          {
            id: "tmi-full",
            label: "Doors, carpet, headliner, dash pad",
            sku: "TMI cab kit",
            price: 2180,
          },
          {
            id: "keep-trim",
            label: "Keep original trim",
            sku: "—",
            price: 0,
          },
        ],
      },
      {
        id: "doorPulls",
        name: "Door pulls",
        brand: "Ringbrothers",
        options: [
          {
            id: "rb-int-handles",
            label: "Ringbrothers pro-touring interior handles, pair",
            sku: "9202 B",
            price: 200,
            href: "https://www.ringbrothers.com/handles-cranks",
          },
          {
            id: "rb-lock-pulls",
            label: "Ringbrothers billet lock pulls, pair",
            sku: "RB lock pulls",
            price: 55,
            href: "https://www.ringbrothers.com/universal-door-lock-pulls10-24-thread-x-1-58-tall-black",
          },
          {
            id: "rb-ext-handles",
            label: "Ringbrothers billet exterior door handles, pair",
            sku: "2012 BB",
            price: 550,
            href: "https://www.ringbrothers.com/handles-cranks",
          },
        ],
      },
      {
        id: "ac",
        name: "A/C",
        brand: "Vintage Air",
        options: [
          {
            id: "ac-na",
            label: "N/A — no A/C",
            sku: "—",
            price: 0,
          },
          {
            id: "vintage-air",
            label: "Gen 5 SureFit complete, factory-air trucks",
            sku: "945619 / 945621",
            price: 2400,
            href: "https://vintageair.com/1973-80-chevrolet-pickup-with-factory-air-gen-5-surefit-complete-kit/",
          },
          {
            id: "vintage-air-non",
            label: "Gen 5 SureFit complete, non-factory air",
            sku: "Vintage Air SureFit",
            price: 2400,
          },
        ],
      },
      {
        id: "wiring",
        name: "Wiring",
        brand: "Ktech",
        locked: true,
        options: [
          {
            id: "wiring-custom",
            label: "Custom shop harness — chassis, engine, interior",
            sku: "KTECH harness",
            price: 1400,
          },
          {
            id: "aaw-classic",
            label: "American Autowire Classic Update complete harness",
            sku: "AAW Classic Update",
            price: 1025,
            href: "https://moderndaymuffler.com/products/fits-75-82-chevrolet-c10-american-auto-wire-classic-update-wiring-system-uwh7382",
          },
        ],
      },
      {
        id: "belts",
        name: "Seat belts",
        brand: "Juliano's",
        options: [
          {
            id: "julianos-3pt",
            label: "Juliano's 3-point retractable, pair",
            sku: "Juliano 3-point",
            price: 289,
          },
        ],
      },
      {
        id: "column",
        name: "Column",
        brand: "ididit",
        options: [
          {
            id: "ididit",
            label: "ididit tilt column, chrome, C10 floor shift",
            sku: "ididit C10 tilt",
            price: 569,
          },
          {
            id: "ididit-key",
            label: "ididit tilt + ignition, chrome",
            sku: "ididit keyed",
            price: 749,
          },
        ],
      },
      {
        id: "wheel",
        name: "Steering wheel",
        brand: "Billet Specialties",
        options: [
          {
            id: "billet-gt",
            label: "Billet Specialties GT, 14\" leather",
            sku: "Billet GT 14",
            price: 289,
          },
          {
            id: "grant",
            label: "Grant Classic, 15\"",
            sku: "Grant Classic",
            price: 149,
          },
        ],
      },
    ],
  },
];

const DEFAULT_GEN: Gen = "7387";

const DEFAULT_SELECTIONS: Record<string, string> = {
  lights: "up-full-7387",
  grille: "brothers-chrome-7387",
  bumpers: "brothers-smooth",
  glass: "acc-windshield",
  core: "core-keep",
  fenders: "fenders-keep",
  hood: "hood-keep",
  hoodHinges: "rb-hinges-7380",
  mirrors: "rb-rect-black",
  cab: "cab-keep",
  bed: "bed-keep",
  tailgate: "tailgate-keep",
  tubs: "hartfab-both",
  weatherstrip: "weather-full",
  frame: "ktech-26",
  spindles: "wilwood-831-14202",
  frontBrakes: "wilwood-14-sl6",
  rearBrakes: "wilwood-14-epb",
  booster: "wilwood-tandem-boost",
  brakeLines: "brake-lines-custom",
  air: "qa1-da",
  shocks: "viking",
  steering: "fr-power",
  battery: "optima-dual",
  steeringShaft: "fr-shaft",
  psHoses: "ps-hoses",
  swayBars: "qa1-bars",
  wheels: "usmags-22-rambler",
  tires: "nitto-22",
  engine: "ls3-430",
  ecu: "aces-jackpot2",
  trans: "6l80e",
  rearend: "currie-third",
  headers: "ultimate-c10",
  pipes: "custom-ss-pipes",
  mufflers: "magnaflow-pair",
  fuel: "tanks-inc",
  cooling: "griffin-ls",
  fluids: "fluids-fill",
  driveshaft: "custom-1350",
  mounts: "ls-mounts",
  serpentine: "ict-serpentine",
  transCooler: "derale-cooler",
  fuelLines: "fuel-lines-an",
  shifter: "lokar-auto",
  dash: "dakota-vhx-7387",
  seats: "tmi-xr-buckets",
  trim: "tmi-doors-carpet",
  doorPulls: "rb-int-handles",
  ac: "ac-na",
  wiring: "wiring-custom",
  belts: "julianos-3pt",
  column: "ididit",
  wheel: "billet-gt",
};

function money(n: number) {
  return n.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

function optionsFor(line: Line, gen: Gen) {
  const filtered = line.options.filter((o) => !o.years || o.years.includes(gen));
  return filtered.length > 0 ? filtered : line.options;
}

function pickOption(line: Line, selectedId: string | undefined, gen: Gen): Option {
  const opts = optionsFor(line, gen);
  return opts.find((o) => o.id === selectedId) ?? opts[0];
}

function allLines() {
  return SECTIONS.flatMap((s) => s.lines.map((line) => ({ section: s, line })));
}

export default function C10BuildSheet() {
  const theme = useHostTheme();
  const [gen, setGen] = useCanvasState<Gen>("gen", DEFAULT_GEN);
  const [sel, setSel] = useCanvasState<Record<string, string>>(
    "sel",
    DEFAULT_SELECTIONS,
  );

  const resolved = allLines().map(({ section, line }) => {
    const opt = pickOption(line, sel[line.id], gen);
    return { section, line, opt };
  });

  const rearIncludesBrakes = resolved.some(
    (r) => r.line.id === "rearend" && r.opt.includesRearBrakes,
  );

  const steeringId = resolved.find((r) => r.line.id === "steering")?.opt.id;
  const boosterId = resolved.find((r) => r.line.id === "booster")?.opt.id;
  const rideOpt = resolved.find((r) => r.line.id === "air")?.opt;
  const transId = resolved.find((r) => r.line.id === "trans")?.opt.id;
  const electricSteer = steeringId === "epas-rack" || steeringId === "fr-microsteer";
  const hydraulicSteer = steeringId === "fr-power" || steeringId === "sweet";
  const powerBrakes = boosterId === "wilwood-tandem-boost";
  const coilover = Boolean(rideOpt?.includesShocks);
  const airRide = rideOpt?.id === "accuair-dual" || rideOpt?.id === "accuair-pressure-dual";
  const needsDualBattery = Boolean(electricSteer || powerBrakes || airRide);
  const dualBattery = SECTIONS.flatMap((s) => s.lines)
    .find((l) => l.id === "battery")
    ?.options.find((o) => o.id === "optima-dual");
  const shockIncluded = SECTIONS.flatMap((s) => s.lines)
    .find((l) => l.id === "shocks")
    ?.options[0];
  const psNa = SECTIONS.flatMap((s) => s.lines)
    .find((l) => l.id === "psHoses")
    ?.options.find((o) => o.id === "ps-na");
  const psHyd = SECTIONS.flatMap((s) => s.lines)
    .find((l) => l.id === "psHoses")
    ?.options.find((o) => o.id === "ps-hoses");
  const shifterManual = SECTIONS.flatMap((s) => s.lines)
    .find((l) => l.id === "shifter")
    ?.options.find((o) => o.id === "lokar-manual");

  const priced = resolved.map((r) => {
    if (r.line.id === "rearBrakes" && rearIncludesBrakes && r.opt.id === "wilwood-11-4p") {
      return { ...r, opt: { ...r.opt, price: 0, label: "Included in Currie crate" } };
    }
    if (r.line.id === "battery" && needsDualBattery && dualBattery) {
      return { ...r, opt: dualBattery };
    }
    if (r.line.id === "shocks" && coilover) {
      return {
        ...r,
        opt: {
          ...(shockIncluded ?? r.opt),
          price: 0,
          label: "Included in QA1 coilovers",
          sku: "—",
        },
      };
    }
    if (r.line.id === "psHoses" && steeringId === "epas-rack" && psNa) {
      return { ...r, opt: psNa };
    }
    if (r.line.id === "psHoses" && hydraulicSteer && psHyd) {
      return { ...r, opt: psHyd };
    }
    if (r.line.id === "shifter" && transId === "tkx" && shifterManual) {
      return { ...r, opt: shifterManual };
    }
    return r;
  });

  const sectionTotals = SECTIONS.map((s) => ({
    id: s.id,
    title: s.title,
    color: s.color,
    total: priced
      .filter((r) => r.section.id === s.id)
      .reduce((sum, r) => sum + r.opt.price, 0),
  }));

  const grand = sectionTotals.reduce((sum, s) => sum + s.total, 0);
  const lockedCount = SECTIONS.flatMap((s) => s.lines).filter((l) => l.locked).length;
  const lineCount = SECTIONS.reduce((n, s) => n + s.lines.length, 0);
  const wb = gen === "7387" ? "117.5 in" : "115 in";

  function setLine(id: string, value: string) {
    setSel((prev) => ({ ...prev, [id]: value }));
  }

  return (
    <Stack gap={28} style={{ padding: 24, maxWidth: 1120 }}>
      <Stack gap={8}>
        <Row gap={8} align="center" wrap>
          <Pill active>Ktech C10</Pill>
          <Pill>Parts build sheet</Pill>
          <Pill>Aug 23, 2026 street</Pill>
        </Row>
        <H1>C10 build sheet</H1>
        <Text tone="secondary">
          House spec for a short-bed 67–87 C10 on the Ktech 2×6 chassis.
          Ride is QA1 coilovers or AccuAir dual-compressor. Locked brands
          are filled. Change a line and the total follows.
        </Text>
      </Stack>

      <Row gap={8} align="center" wrap>
        <Text size="small" tone="tertiary" as="span">
          Generation
        </Text>
        <Pill active={gen === "7387"} onClick={() => setGen("7387")}>
          73–87 squarebody
        </Pill>
        <Pill active={gen === "6772"} onClick={() => setGen("6772")}>
          67–72 action line
        </Pill>
        <Spacer />
        <Text size="small" tone="tertiary" as="span">
          Short bed only · {wb}
        </Text>
      </Row>

      <Grid columns={4} gap={12}>
        <Stat value={money(grand)} label="Parts total" tone="info" />
        <Stat value={String(lockedCount)} label="Locked brands" />
        <Stat value={String(lineCount)} label="Line items" />
        <Stat value={wb} label="Wheelbase" />
      </Grid>

      <Grid columns="1.1fr 1fr" gap={16} align="start">
        <Stack gap={8}>
          <H3>Spend by section</H3>
          <BarChart
            horizontal
            categories={sectionTotals.map((s) => s.title)}
            series={[
              {
                name: "Parts $",
                data: sectionTotals.map((s) => s.total),
              },
            ]}
            valuePrefix="$"
            height={180}
            showValues
          />
          <Text size="small" tone="tertiary">
            Source: selected options on this sheet · {SOURCE}
          </Text>
        </Stack>
        <Card>
          <CardHeader>Mix</CardHeader>
          <CardBody>
            <PieChart
              donut
              size={200}
              data={sectionTotals.map((s) => ({
                label: s.title,
                value: s.total,
              }))}
            />
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="info" title="Locked, not guessed">
        Wilwood sells EPB rear kits — house spec is FNSL4R 12.88" with
        electronic parking brake ($3,411). Trans cooler stays on every trans.
        Mirrors, hood hinges, and door pulls are Ringbrothers. Fluids are a
        $425 first-fill kit. Dual Optima YellowTops when EPAS, power brakes,
        or air ride is on. Short bed only.
      </Callout>

      {SECTIONS.map((section) => {
        const sub = sectionTotals.find((s) => s.id === section.id)?.total ?? 0;
        return (
          <Stack key={section.id} gap={12}>
            <Row gap={8} align="center">
              <Swatch color={section.color} />
              <H2>{section.title}</H2>
              <Spacer />
              <Text weight="semibold">{money(sub)}</Text>
            </Row>
            <Text size="small" tone="secondary">
              {section.blurb}
            </Text>
            <Stack gap={10}>
              {section.lines.map((line) => {
                const opts = optionsFor(line, gen);
                const opt = pickOption(line, sel[line.id], gen);
                const display =
                  line.id === "rearBrakes" &&
                  rearIncludesBrakes &&
                  opt.id === "wilwood-11-4p"
                    ? { ...opt, price: 0, label: "Included in Currie crate" }
                    : line.id === "battery" && needsDualBattery && dualBattery
                      ? dualBattery
                      : line.id === "shocks" && coilover
                        ? {
                            ...opt,
                            price: 0,
                            label: "Included in QA1 coilovers",
                            sku: "—",
                          }
                        : line.id === "psHoses" && steeringId === "epas-rack" && psNa
                          ? psNa
                          : opt;
                const lockSelect =
                  opts.length === 1 ||
                  (line.id === "rearBrakes" &&
                    rearIncludesBrakes &&
                    opt.id === "wilwood-11-4p") ||
                  (line.id === "battery" && needsDualBattery) ||
                  (line.id === "shocks" && coilover) ||
                  (line.id === "psHoses" && steeringId === "epas-rack");
                const skuNode = display.href ? (
                  <Link href={display.href}>{display.sku}</Link>
                ) : (
                  <Text size="small" tone="tertiary" as="span">
                    {display.sku}
                  </Text>
                );
                return (
                  <Stack
                    key={line.id}
                    gap={6}
                    style={{
                      paddingBottom: 10,
                      borderBottom: `1px solid ${theme.stroke.tertiary}`,
                    }}
                  >
                    <Row gap={8} align="center" wrap>
                      <Text
                        weight="semibold"
                        as="span"
                        style={{ minWidth: 120 }}
                      >
                        {line.name}
                      </Text>
                      {line.locked ? (
                        <Pill size="sm" active>
                          {line.brand} locked
                        </Pill>
                      ) : (
                        <Text size="small" tone="tertiary" as="span">
                          {line.brand}
                        </Text>
                      )}
                      <Spacer />
                      <Text weight="semibold" as="span">
                        {display.price === 0 ? "—" : money(display.price)}
                      </Text>
                    </Row>
                    {lockSelect ? (
                      <Text size="small">{display.label}</Text>
                    ) : (
                      <Select
                        value={opt.id}
                        onChange={(v) => setLine(line.id, v)}
                        options={opts.map((o) => ({
                          value: o.id,
                          label: `${o.label}  ·  ${money(o.price)}`,
                        }))}
                        style={{ maxWidth: 640 }}
                      />
                    )}
                    <Text size="small" tone="tertiary">
                      {skuNode}
                    </Text>
                  </Stack>
                );
              })}
            </Stack>
          </Stack>
        );
      })}

      <Divider />

      <Stack gap={10}>
        <Row gap={8} align="center">
          <H2>This spec</H2>
          <Spacer />
          <Button
            variant="secondary"
            onClick={() => {
              setGen(DEFAULT_GEN);
              setSel(DEFAULT_SELECTIONS);
            }}
          >
            Reset house spec
          </Button>
        </Row>
        <Text size="small" tone="secondary">
          {gen === "7387" ? "1973–1987" : "1967–1972"} C10 · short bed · {wb}{" "}
          wheelbase · 5×5 · 2WD
        </Text>
        <Table
          headers={["Section", "Item", "Product", "SKU", "Price"]}
          columnAlign={["left", "left", "left", "left", "right"]}
          striped
          stickyHeader
          rows={priced.map((r) => [
            r.section.title,
            r.line.name,
            r.opt.label,
            r.opt.sku,
            r.opt.price === 0 ? "—" : money(r.opt.price),
          ])}
        />
        <Row justify="end">
          <Text weight="bold">Parts total {money(grand)}</Text>
        </Row>
        <Text size="small" tone="tertiary">
          {SOURCE} Ktech chassis is a working shop number, not a published
          MSRP. Comparable complete airbag chassis: Choppin Block ~$9,995,
          Roadster Shop SPEC ~$15,495, RevB ~$18,495 (those kits bundle
          spindles / bags / 9-inch that this sheet lists separately).
        </Text>
      </Stack>
    </Stack>
  );
}
