// Render every SVG in graphics/svg/ to a PNG in public/assets/img/.
// Run:  node graphics/render.js
// Needs sharp from the managed node workspace (NODE_PATH set by the caller).
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const HERE = __dirname;
const SVG_DIR = path.join(HERE, "svg");
const OUT_DIR = path.join(HERE, "..", "public", "assets", "img");

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const files = fs.readdirSync(SVG_DIR).filter((f) => f.endsWith(".svg"));
  for (const f of files) {
    const out = path.join(OUT_DIR, f.replace(/\.svg$/, ".png"));
    const info = await sharp(fs.readFileSync(path.join(SVG_DIR, f)))
      .png({ compressionLevel: 9 })
      .toFile(out);
    console.log(
      `${f}  ->  ${path.relative(path.join(HERE, ".."), out)}  ${info.width}x${info.height}  ${(info.size / 1024).toFixed(0)}KB`
    );
  }
})();
