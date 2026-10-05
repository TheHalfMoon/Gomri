import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relativePath) => readFile(path.join(repoRoot, relativePath), "utf8");

test("compatibility alias matrix has unique canonical names", async () => {
  const matrix = JSON.parse(await read("config/compatibility-aliases.json"));
  const canonicals = matrix.environment_aliases.map(({ canonical }) => canonical);
  assert.equal(new Set(canonicals).size, canonicals.length);
  assert.equal(matrix.environment_aliases.length, 12);
  assert.equal(matrix.protocol_aliases[0].canonical, "X-Gomrey-MCP-Request");
  assert.equal(matrix.protocol_aliases[0].legacy, "X-Presenton-MCP-Request");
});

test("runtime boundaries expose Gomrey canonical names and legacy fallbacks", async () => {
  const [compose, electronMain, getEnv, mcpUrls, nextConfig] = await Promise.all([
    read("docker-compose.yml"),
    read("electron/app/main.ts"),
    read("servers/fastapi/utils/get_env.py"),
    read("servers/fastapi/utils/mcp_public_urls.py"),
    read("servers/nextjs/next.config.mjs"),
  ]);
  assert.match(compose, /GOMREY_DOCKER_PLATFORM/);
  assert.match(compose, /PRESENTON_DOCKER_PLATFORM/);
  assert.match(electronMain, /GOMREY_APP_ROOT/);
  assert.match(electronMain, /PRESENTON_APP_ROOT/);
  assert.match(getEnv, /GOMREY_PUBLIC_URL/);
  assert.match(getEnv, /PRESENTON_PUBLIC_URL/);
  assert.match(mcpUrls, /X-Gomrey-MCP-Request/);
  assert.match(mcpUrls, /X-Presenton-MCP-Request/);
  assert.match(nextConfig, /GOMREY_ELECTRON_BUILD/);
  assert.match(nextConfig, /PRESENTON_ELECTRON_BUILD/);
  assert.match(getEnv, /DEFAULT_PRESENTON_OAUTH_ISSUER/);
});
