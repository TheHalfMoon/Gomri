const fs = require("fs");
const path = require("path");

const electronRoot = path.join(__dirname, "..");
const pkg = JSON.parse(
  fs.readFileSync(path.join(electronRoot, "package.json"), "utf8"),
);

const version = pkg.version;

const update = {
  version,
  message: process.env.UPDATE_MESSAGE || "",
  downloads: {
    linux: `https://github.com/TheHalfMoon/Gomrey/releases/download/electron-v${version}/Gomrey-${version}.deb`,
    mac: `https://github.com/TheHalfMoon/Gomrey/releases/download/electron-v${version}/Gomrey-${version}.dmg`,
    windows: `https://github.com/TheHalfMoon/Gomrey/releases/download/electron-v${version}/Gomrey-${version}.exe`,
  },
};

fs.writeFileSync(
  path.join(electronRoot, "version.json"),
  `${JSON.stringify(update, null, 2)}\n`,
);

console.log("version.json generated");
