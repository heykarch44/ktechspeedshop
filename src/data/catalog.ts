export type BuildStatus = "complete" | "in-build" | "sold";

export type Build = {
  slug: string;
  title: string;
  year: number;
  model: string;
  nickname: string;
  status: BuildStatus;
  cover: string;
  gallery: string[];
  summary: string;
  story: string;
  specs: string[];
  featured: boolean;
  projectSlug?: string;
};

export type SaleListing = {
  slug: string;
  title: string;
  year: number;
  model: string;
  price: string;
  status: "available" | "pending" | "coming";
  cover: string;
  summary: string;
  details: string;
  highlights: string[];
};

export type Part = {
  slug: string;
  title: string;
  price: string;
  fits: string;
  cover: string;
  summary: string;
  details: string;
};

export type Merch = {
  slug: string;
  title: string;
  price: string;
  cover: string;
  summary: string;
  sizes?: string;
};

export const builds: Build[] = [
  {
    slug: "black-68-shortbed",
    title: "1968 C10 Shortbed",
    year: 1968,
    model: "C10",
    nickname: "Night Shift",
    status: "complete",
    cover: "/images/builds/hero-c10.png",
    gallery: [
      "/images/builds/hero-c10.png",
      "/images/builds/engine-bay-ls.png",
    ],
    summary:
      "Bagged shortbed, LS power, tucked bodywork. Built to drive, not sit under a cover.",
    story:
      "This 1968 shortbed started as a tired driver and left as a laid-out C10 with modern power and a clean engine bay. Air ride to put it on the ground, an LS3 that actually gets used, and bodywork that still looks like a truck.",
    specs: [
      "LS3 / 4L65E",
      "Air ride, front and rear",
      "Wilwood discs",
      "Tucked bumpers, smoothed firewall",
      "Custom bed wood and rails",
    ],
    featured: true,
    projectSlug: "68-c10-shortbed",
  },
  {
    slug: "69-patina-cruiser",
    title: "1969 C10 Patina",
    year: 1969,
    model: "C10",
    nickname: "Barn Find",
    status: "complete",
    cover: "/images/builds/69-patina.png",
    gallery: ["/images/builds/69-patina.png"],
    summary:
      "Kept the original skin. Fixed everything underneath. The right kind of patina build.",
    story:
      "Most patina trucks are a pose. This one keeps the original paint because it earned it, then gets a chassis, brakes, and drivetrain that belong on the highway. Air bags to lay it out at a show. Coilover-friendly geometry so it still rides when you air up and go home.",
    specs: [
      "Original faded paint, sealed",
      "Air suspension",
      "Disc brakes",
      "Updated steering and cooling",
      "Steelies and white-letter rubber",
    ],
    featured: true,
  },
  {
    slug: "72-cheyenne-super",
    title: "1972 C10 Cheyenne",
    year: 1972,
    model: "C10 Cheyenne Super",
    nickname: "Hugger",
    status: "complete",
    cover: "/images/builds/72-orange.png",
    gallery: ["/images/builds/72-orange.png"],
    summary:
      "Color, chrome, and a chassis that can keep up. A 67–72 done the right way.",
    story:
      "The last year of the 67–72 body is a favorite for a reason. This Cheyenne Super got a full paint and chassis job, oak bed, and a stance that still clears a driveway. Built as a weekend driver that can take a 400-mile Saturday without drama.",
    specs: [
      "Hugger Orange, show paint",
      "Lowered suspension, disc brakes",
      "White oak bed",
      "Rally wheels",
      "Restored chrome and trim",
    ],
    featured: false,
  },
  {
    slug: "78-squarebody",
    title: "1978 C10 Squarebody",
    year: 1978,
    model: "C10",
    nickname: "Square",
    status: "complete",
    cover: "/images/builds/78-square.png",
    gallery: ["/images/builds/78-square.png"],
    summary:
      "73–87 squarebody, bagged, blacked out, built to sit and cruise.",
    story:
      "Squarebodies are having a moment, and most of them look the same. This one is a two-tone shortbed with modern lighting, a laid-out stance, and an interior you can actually sit in for more than a parade lap.",
    specs: [
      "Air ride, body drop friendly",
      "Two-tone paint",
      "Billet wheels",
      "LED lighting",
      "Custom interior",
    ],
    featured: true,
  },
  {
    slug: "85-lifted-square",
    title: "1985 C10 Silverado",
    year: 1985,
    model: "C10 Silverado",
    nickname: "Carolina",
    status: "complete",
    cover: "/images/builds/squarebody-blue.jpg",
    gallery: ["/images/builds/squarebody-blue.jpg"],
    summary:
      "Not every C10 needs to lay frame. Color-matched lift, blacked-out trim, built to go anywhere.",
    story:
      "A squarebody does not have to be bagged to be a custom. This Silverado got a proper lift, color-matched suspension, and a matte finish that does not hide dirt. Shop truck energy. Highway manners.",
    specs: [
      "Lifted suspension, color-matched",
      "Matte Carolina blue",
      "Blacked-out trim and bumpers",
      "Off-road wheel and tire package",
    ],
    featured: false,
    projectSlug: "85-c10-silverado",
  },
  {
    slug: "68-c10-in-build",
    title: "1968 C10",
    year: 1968,
    model: "C10",
    nickname: "In the jig",
    status: "in-build",
    cover: "/images/builds/71-project.png",
    gallery: ["/images/builds/71-project.png", "/images/shop/garage.jpg"],
    summary:
      "Currently in the shop. Chassis, LS, and metalwork underway. Ask if you want in on a similar build.",
    story:
      "This 68 is on stands for chassis work and an LS swap. Follow the shop log for in-progress shots — these are the photos most sites never show.",
    specs: [
      "Frame and suspension in progress",
      "LS swap staged",
      "Cab metalwork",
      "Available as a commissioned finish or similar build slot",
    ],
    featured: false,
    projectSlug: "68-c10-in-build",
  },
];

export const listings: SaleListing[] = [
  {
    slug: "68-c10-project",
    title: "1968 C10 project",
    year: 1968,
    model: "C10",
    price: "Inquire",
    status: "available",
    cover: "/images/builds/71-project.png",
    summary:
      "Rolling 68 C10 with the hard metal started. Better than a Craigslist shell. Worse than a finished truck — on purpose.",
    details:
      "This is a shop project, not a polished turn-key. 1968 C10, frame work underway, LS staged, cab is honest. If you want a 68 without paying for someone else's taste in paint, this is the lane. Serious inquiries only — tell us how you want it finished.",
    highlights: [
      "1968 C10",
      "Chassis work started",
      "LS swap staged",
      "Can be finished in-house",
    ],
  },
  {
    slug: "78-squarebody-driver",
    title: "1978 C10 squarebody",
    year: 1978,
    model: "C10",
    price: "Coming to market",
    status: "coming",
    cover: "/images/builds/78-square.png",
    summary:
      "Bagged squarebody finishing in the shop. Get on the list before it hits the site with a number.",
    details:
      "Shortbed squarebody, air ride, two-tone. We will publish price and a full gallery when it is ready to leave. DM the shop if you want first look.",
    highlights: [
      "73–87 squarebody shortbed",
      "Air ride",
      "Turn-key driver when released",
      "First look via Instagram",
    ],
  },
];

export const parts: Part[] = [
  {
    slug: "67-72-tailgate-latch",
    title: "67–72 C10 tailgate latch kit",
    price: "$425",
    fits: "1967–1972 C10 / C20",
    cover: "/images/parts/latch.png",
    summary:
      "Billet latch kit so the tailgate shuts like a door, not a farm implement.",
    details:
      "CNC machined hardware for 67–72 GM trucks. Replaces tired factory latches with a kit you can actually adjust. Finish options on request. Email or Instagram to order — we ship.",
  },
  {
    slug: "bed-floor-hinges",
    title: "Billet bed floor hinges",
    price: "$1,000+",
    fits: "C10 beds, custom floors",
    cover: "/images/parts/metal.jpg",
    summary:
      "Hinges for a raised or one-piece bed floor. Made here, not drop-shipped from a catalog.",
    details:
      "If you are running a smooth bed floor or a hinged setup over tanks and bags, these are the hinges. Machined in billet, sold as a pair. Tell us the bed year and floor style when you order.",
  },
  {
    slug: "ls-swap-crossmember",
    title: "C10 LS swap crossmember",
    price: "Inquire",
    fits: "60–72 and 73–87 C10",
    cover: "/images/builds/engine-bay-ls.png",
    summary:
      "Crossmember and mount package for an LS that sits where it should.",
    details:
      "We do not sell a mystery Amazon crossmember. This is the mount package we use on shop LS swaps. Call out your year, trans, and oil pan and we will confirm fitment before you buy.",
  },
  {
    slug: "cab-mount-kit",
    title: "C10 cab mount kit",
    price: "$220",
    fits: "1967–1972 C10",
    cover: "/images/parts/billet.jpg",
    summary:
      "New cab mounts so the cab does not rock like a porch swing.",
    details:
      "Poly or rubber, your call. A cheap part that changes how the whole truck feels. Pair it with a body bushing kit if the rest of the truck is equally tired.",
  },
];

export const merch: Merch[] = [
  {
    slug: "ktech-snapback",
    title: "K-TECH snapback",
    price: "$32",
    cover: "/images/merch/hat.png",
    summary: "Black hat, rust K-TECH mark. The one that lives in the shop truck.",
    sizes: "One size",
  },
  {
    slug: "speedshop-tee",
    title: "K-TECH tee",
    price: "$28",
    cover: "/images/merch/tee.png",
    summary: "Heavyweight black tee. K-TECH SPEEDSHOP on the chest.",
    sizes: "S–XXL",
  },
  {
    slug: "shop-hoodie",
    title: "K-TECH hoodie",
    price: "$58",
    cover: "/images/merch/hoodie.png",
    summary: "K-TECH SPEEDSHOP on the chest. The hoodie you wear in the bay when the heater is lying.",
    sizes: "S–XXL",
  },
  {
    slug: "k-tech-tee",
    title: "K_tech tee",
    price: "$28",
    cover: "/images/merch/ktech-tee.png",
    summary: "Bone mark, rust underscore. The tech side of the shop.",
    sizes: "S–XXL",
  },
  {
    slug: "k-tech-sweatshirt",
    title: "K_tech sweatshirt",
    price: "$48",
    cover: "/images/merch/ktech-sweatshirt.png",
    summary: "Crewneck. K_tech on the chest. For the bay that also ships code.",
    sizes: "S–XXL",
  },
];

export function getBuild(slug: string) {
  return builds.find((item) => item.slug === slug);
}

export function getListing(slug: string) {
  return listings.find((item) => item.slug === slug);
}

export function getPart(slug: string) {
  return parts.find((item) => item.slug === slug);
}

export function getMerch(slug: string) {
  return merch.find((item) => item.slug === slug);
}

export const featuredBuilds = builds.filter((item) => item.featured);
