import opentype from "opentype.js";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

mkdirSync("print", { recursive: true });
mkdirSync("public/print", { recursive: true });

const RUST = "#D3541A";
const CREAM = "#F1E7D4";

function loadFont(file) {
  const buf = readFileSync(file);
  return opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
}

const bold = loadFont("print/Oswald-Bold.ttf");
const medium = loadFont("print/Oswald-Medium.ttf");

function commandsToD(commands) {
  return commands
    .map((c) => {
      if (c.type === "Z") return "Z";
      if (c.type === "M" || c.type === "L") return `${c.type}${round(c.x)} ${round(c.y)}`;
      if (c.type === "Q") return `Q${round(c.x1)} ${round(c.y1)} ${round(c.x)} ${round(c.y)}`;
      if (c.type === "C")
        return `C${round(c.x1)} ${round(c.y1)} ${round(c.x2)} ${round(c.y2)} ${round(c.x)} ${round(c.y)}`;
      return "";
    })
    .join("");
}

function round(n) {
  return Math.round(n * 100) / 100;
}

function boxOf(commands) {
  let x1 = Infinity;
  let y1 = Infinity;
  let x2 = -Infinity;
  let y2 = -Infinity;
  for (const c of commands) {
    for (const key of ["x", "y", "x1", "y1", "x2", "y2"]) {
      if (typeof c[key] !== "number" || Number.isNaN(c[key])) continue;
      if (key.startsWith("x")) {
        x1 = Math.min(x1, c[key]);
        x2 = Math.max(x2, c[key]);
      } else {
        y1 = Math.min(y1, c[key]);
        y2 = Math.max(y2, c[key]);
      }
    }
  }
  return { x1, y1, x2, y2 };
}

function pathFrom(font, text, x, y, size) {
  const scale = (1 / font.unitsPerEm) * size;
  let cursor = x;
  const commands = [];
  for (const ch of text) {
    const glyph = font.charToGlyph(ch);
    const gp = glyph.getPath(cursor, y, size);
    commands.push(...gp.commands);
    cursor += (glyph.advanceWidth || 0) * scale;
  }
  return { d: commandsToD(commands), box: boxOf(commands) };
}

function svg(width, height, body) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
  <title>K-TECH Speedshop merch art</title>
  ${body}
</svg>
`;
}

function save(name, contents) {
  writeFileSync(`print/${name}`, contents);
  writeFileSync(`public/print/${name}`, contents);
  console.log("wrote", name);
}

function c10Filled() {
  return `<g id="c10" fill="${RUST}" fill-rule="evenodd">
    <path d="M42 168 L78 152 L118 118 L198 108 L238 78 L318 62 L402 62 L428 88 L448 108 L712 108 L728 88 L748 88 L762 118 L778 168 L778 198 L748 208 L728 188 L638 188 L618 208 L548 208 L528 188 L248 188 L228 208 L158 208 L138 188 L78 188 L58 208 L42 198 Z M188 198 A62 62 0 1 0 188 197.9 Z M588 198 A62 62 0 1 0 588 197.9 Z"/>
    <circle cx="188" cy="198" r="36"/>
    <circle cx="588" cy="198" r="36"/>
    <path d="M248 78 L318 68 L398 68 L418 88 L248 88 Z" opacity="0.28"/>
  </g>`;
}

function c10Line() {
  return `<g id="c10-line" fill="none" stroke="${RUST}" stroke-width="10" stroke-linejoin="round" stroke-linecap="round">
    <path d="M48 170 L82 154 L122 120 L200 110 L240 80 L320 64 L400 64 L426 90 L448 110 L710 110 L726 90 L746 90 L760 120 L776 170 L776 198"/>
    <path d="M138 190 L248 190"/>
    <path d="M528 190 L638 190"/>
    <path d="M248 80 L248 190"/>
    <path d="M426 90 L426 190"/>
    <path d="M128 120 L236 120"/>
    <circle cx="188" cy="198" r="48"/>
    <circle cx="588" cy="198" r="48"/>
    <circle cx="188" cy="198" r="16"/>
    <circle cx="588" cy="198" r="16"/>
  </g>`;
}

function trackedWord(font, text, size, targetWidth) {
  const glyphs = [...text].map((ch) => pathFrom(font, ch, 0, 0, size));
  const total = glyphs.reduce((a, g) => a + (g.box.x2 - g.box.x1), 0);
  const gap = (targetWidth - total) / (glyphs.length - 1);
  let x = 0;
  return glyphs
    .map((g) => {
      const dx = x - g.box.x1;
      x += g.box.x2 - g.box.x1 + gap;
      return `<path fill="${RUST}" d="${g.d}" transform="translate(${round(dx)} 0)"/>`;
    })
    .join("\n      ");
}

const ktech = pathFrom(bold, "K-TECH", 0, 0, 180);
const speedHat = pathFrom(medium, "SPEEDSHOP", 0, 0, 48);
const ktechW = ktech.box.x2 - ktech.box.x1;
const hatSpeedW = speedHat.box.x2 - speedHat.box.x1;

const hatPadX = 90;
const hatPadY = 100;
const hatKtechX = hatPadX - ktech.box.x1;
const hatKtechY = hatPadY - ktech.box.y1;
const hatSpeedX = hatKtechX + ktech.box.x1 + ktechW - hatSpeedW;
const hatSpeedY = hatKtechY + 82;
const hatW = Math.ceil(hatPadX + ktechW + 90);
const hatH = Math.ceil(hatPadY + (ktech.box.y2 - ktech.box.y1) + 120);

save(
  "ktech-hat.svg",
  svg(
    hatW,
    hatH,
    `<g transform="skewX(-11)">
      <path fill="${RUST}" d="${ktech.d}" transform="translate(${round(hatKtechX)} ${round(hatKtechY)})"/>
      <path fill="${RUST}" d="${speedHat.d}" transform="translate(${round(hatSpeedX)} ${round(hatSpeedY)})"/>
    </g>`
  )
);

const hoodKtechX = hatPadX - ktech.box.x1;
const hoodKtechY = hatPadY - ktech.box.y1;
const hoodSpeedY = hoodKtechY + 74;
const hoodW = Math.ceil(hatPadX + ktechW + 90);
const hoodH = Math.ceil(hatPadY + (ktech.box.y2 - ktech.box.y1) + 110);
const hoodTracked = trackedWord(medium, "SPEEDSHOP", 42, ktechW);

save(
  "ktech-hoodie-chest.svg",
  svg(
    hoodW,
    hoodH,
    `<g transform="skewX(-11)">
      <path fill="${RUST}" d="${ktech.d}" transform="translate(${round(hoodKtechX)} ${round(hoodKtechY)})"/>
      <g transform="translate(${round(hoodKtechX + ktech.box.x1)} ${round(hoodSpeedY)})">
        ${hoodTracked}
      </g>
    </g>`
  )
);

save("ktech-c10-filled.svg", svg(820, 280, c10Filled()));
save("ktech-c10-line.svg", svg(820, 280, c10Line()));

const teeK = pathFrom(bold, "K-TECH", 0, 0, 160);
const teeS = pathFrom(medium, "SPEEDSHOP", 0, 0, 44);
const teeKW = teeK.box.x2 - teeK.box.x1;
const teeSW = teeS.box.x2 - teeS.box.x1;
const teeW = 900;
const teeH = 620;
const teeKx = (teeW - teeKW) / 2 - teeK.box.x1;
const teeKy = 130 - teeK.box.y1;
const teeSx = (teeW - teeSW) / 2 - teeS.box.x1;
const teeSy = teeKy + 70;

save(
  "ktech-tee.svg",
  svg(
    teeW,
    teeH,
    `<path fill="${RUST}" d="${teeK.d}" transform="translate(${round(teeKx)} ${round(teeKy)})"/>
  <path fill="${RUST}" d="${teeS.d}" transform="translate(${round(teeSx)} ${round(teeSy)})"/>
  <g transform="translate(40 250)">${c10Filled()}</g>`
  )
);

const kPart = pathFrom(bold, "K", 0, 0, 96);
const techPart = pathFrom(bold, "tech", 0, 0, 96);
const techSpeed = pathFrom(medium, "SPEEDSHOP", 0, 0, 36);
const barW = 52;
const gap = 10;
const kW = kPart.box.x2 - kPart.box.x1;
const tW = techPart.box.x2 - techPart.box.x1;
const techLineW = kW + gap + barW + gap + tW;
const speedW = techSpeed.box.x2 - techSpeed.box.x1;
const techPad = 60;
const techCanvasW = Math.ceil(techPad * 2 + Math.max(techLineW, speedW));
const kX = techPad - kPart.box.x1;
const kY = 150 - kPart.box.y1;
const barX = techPad + kW + gap;
const barY = kY + kPart.box.y2 - 18;
const techX = barX + barW + gap - techPart.box.x1;
const speedX = techPad - techSpeed.box.x1;
const speedY = kY + 62;
const techCanvasH = Math.ceil(speedY + (techSpeed.box.y2 - techSpeed.box.y1) + 50);

save(
  "ktech-tech.svg",
  svg(
    techCanvasW,
    techCanvasH,
    `<path fill="${CREAM}" d="${kPart.d}" transform="translate(${round(kX)} ${round(kY)})"/>
  <rect x="${round(barX)}" y="${round(barY)}" width="${barW}" height="16" rx="1" fill="${RUST}"/>
  <path fill="${CREAM}" d="${techPart.d}" transform="translate(${round(techX)} ${round(kY)})"/>
  <path fill="${RUST}" d="${techSpeed.d}" transform="translate(${round(speedX)} ${round(speedY)})"/>`
  )
);

save(
  "ktech-wordmark.svg",
  svg(
    hoodW,
    hoodH,
    `<path fill="${RUST}" d="${ktech.d}" transform="translate(${round(hoodKtechX)} ${round(hoodKtechY)})"/>
  <g transform="translate(${round(hoodKtechX + ktech.box.x1)} ${round(hoodSpeedY)})">
    ${hoodTracked}
  </g>`
  )
);

const notes = `K-TECH Speedshop merch vectors
Rust: #D3541A
Cream (tech mark): #F1E7D4
Transparent background. Type is outlined — no font install needed.

ktech-hat.svg            Hat front. Italic K-TECH, SPEEDSHOP under and to the right.
ktech-hoodie-chest.svg   Hoodie chest. Italic K-TECH, SPEEDSHOP tracked to width.
ktech-c10-line.svg       Hoodie sleeve, line-art C10.
ktech-tee.svg            Tee: K-TECH, SPEEDSHOP, slammed C10.
ktech-c10-filled.svg     C10 only.
ktech-tech.svg           Tech tee / sweatshirt lockup.
ktech-wordmark.svg       Upright two-line wordmark.

Print DTF or screen. Not embroidery. Scale freely. Keep rust on black.
`;

writeFileSync("print/PRINT-NOTES.txt", notes);
writeFileSync("public/print/PRINT-NOTES.txt", notes);
console.log("done");
