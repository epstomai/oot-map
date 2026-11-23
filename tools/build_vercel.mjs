import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.dirname(__dirname);

const DATA_DIR = path.join(ROOT, "data");
const MAPS_SRC_DIR = path.join(DATA_DIR, "map_assets", "maps");
const FRONTEND_DIR = path.join(ROOT, "frontend");
const DIST_DIR = path.join(ROOT, "dist");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

fs.rmSync(DIST_DIR, { recursive: true, force: true });
ensureDir(path.join(DIST_DIR, "static"));
ensureDir(path.join(DIST_DIR, "data"));
ensureDir(path.join(DIST_DIR, "maps"));

fs.copyFileSync(path.join(FRONTEND_DIR, "index.html"), path.join(DIST_DIR, "index.html"));
fs.copyFileSync(path.join(FRONTEND_DIR, "styles.css"), path.join(DIST_DIR, "static", "styles.css"));
fs.copyFileSync(path.join(FRONTEND_DIR, "app.js"), path.join(DIST_DIR, "static", "app.js"));

const placesBlob = readJson(path.join(DATA_DIR, "places.json"));
const categories = readJson(path.join(DATA_DIR, "categories.json"));
const requirements = readJson(path.join(DATA_DIR, "requirements.json"));
const collectibles = readJson(path.join(DATA_DIR, "collectibles.json"));
const i18n = readJson(path.join(DATA_DIR, "ui_i18n.json"));
const gdBlob = readJson(path.join(DATA_DIR, "gamedata_hashes.json"));

const catalogPayload = {
  map: placesBlob.map,
  places: placesBlob.places,
  categories,
  requirements,
  collectibles,
  i18n,
  hashes: gdBlob.hashes,
};

fs.writeFileSync(
  path.join(DIST_DIR, "data", "catalog.json"),
  JSON.stringify(catalogPayload),
  "utf8"
);

const referencedMaps = new Set();
if (placesBlob.map?.image) {
  referencedMaps.add(path.basename(placesBlob.map.image));
}
for (const place of placesBlob.places || []) {
  for (const m of place.maps || []) {
    if (m.image) referencedMaps.add(path.basename(m.image));
  }
  for (const ex of place.exits || []) {
    if (ex.icon) referencedMaps.add(path.basename(ex.icon));
  }
}

let copiedCount = 0;
let copiedBytes = 0;
for (const name of referencedMaps) {
  const src = path.join(MAPS_SRC_DIR, name);
  if (!fs.existsSync(src)) {
    throw new Error(`Missing referenced map asset: ${src}`);
  }
  const dst = path.join(DIST_DIR, "maps", name);
  fs.copyFileSync(src, dst);
  copiedCount += 1;
  copiedBytes += fs.statSync(dst).size;
}

console.log(
  `Built Vercel static bundle at ${DIST_DIR}: ${copiedCount} maps (${(copiedBytes / 1024 / 1024).toFixed(2)} MB)`
);
