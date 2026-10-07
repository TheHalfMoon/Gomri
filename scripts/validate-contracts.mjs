import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// Supported keyword subset (documented contract; anything else fails loudly):
// type, enum, const, required, properties, additionalProperties,
// items, minLength, maxLength, minimum, maximum, pattern,
// format (date-time, uri, uuid), anyOf, oneOf, allOf, $ref (local #/$defs/... only).
const SUPPORTED_KEYWORDS = new Set([
  "$defs",
  "$id",
  "$ref",
  "additionalProperties",
  "allOf",
  "anyOf",
  "const",
  "description",
  "enum",
  "format",
  "items",
  "maxLength",
  "maximum",
  "minLength",
  "minimum",
  "oneOf",
  "pattern",
  "properties",
  "required",
  "title",
  "type",
  "version",
]);

const FORMATS = {
  "date-time": /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/,
  uri: /^[a-zA-Z][a-zA-Z0-9+.-]*:[^\s]+$/,
  uuid: /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/,
};

function typeName(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (Number.isInteger(value)) return "integer";
  return typeof value;
}

function checkType(value, expected) {
  const actual = typeName(value);
  if (expected === "number") return actual === "number" || actual === "integer" ? null : actual;
  if (expected === "integer") return actual === "integer" ? null : actual;
  return actual === expected ? null : actual;
}

export function validateValue(value, schema, root, location = "$") {
  const errors = [];
  if (!schema || typeof schema !== "object") return ["schema is not an object"];
  for (const key of Object.keys(schema)) {
    if (!SUPPORTED_KEYWORDS.has(key)) {
      return [`${location}: unsupported keyword ${key}`];
    }
  }
  if (schema.$ref !== undefined) {
    if (typeof schema.$ref !== "string" || !schema.$ref.startsWith("#/$defs/")) {
      return [`${location}: only local #/$defs/... refs are supported`];
    }
    const name = schema.$ref.slice("#/$defs/".length);
    const target = root?.$defs?.[name];
    if (!target) return [`${location}: unknown $defs entry ${name}`];
    return validateValue(value, target, root, location);
  }
  if (schema.const !== undefined && JSON.stringify(value) !== JSON.stringify(schema.const)) {
    errors.push(`${location}: must equal constant ${JSON.stringify(schema.const)}`);
  }
  if (schema.enum !== undefined && !schema.enum.some((option) => JSON.stringify(option) === JSON.stringify(value))) {
    errors.push(`${location}: must be one of ${JSON.stringify(schema.enum)}`);
  }
  if (schema.type !== undefined) {
    const expected = Array.isArray(schema.type) ? schema.type : [schema.type];
    const matches = expected.some((option) => checkType(value, option) === null);
    if (!matches) {
      errors.push(`${location}: expected type ${expected.join("|")}, got ${typeName(value)}`);
      return errors;
    }
  }
  if (typeof value === "string") {
    if (schema.minLength !== undefined && value.length < schema.minLength) {
      errors.push(`${location}: shorter than minLength ${schema.minLength}`);
    }
    if (schema.maxLength !== undefined && value.length > schema.maxLength) {
      errors.push(`${location}: longer than maxLength ${schema.maxLength}`);
    }
    if (schema.pattern !== undefined && !new RegExp(schema.pattern).test(value)) {
      errors.push(`${location}: does not match pattern ${schema.pattern}`);
    }
    if (schema.format !== undefined) {
      const pattern = FORMATS[schema.format];
      if (!pattern) errors.push(`${location}: unsupported format ${schema.format}`);
      else if (!pattern.test(value)) errors.push(`${location}: invalid ${schema.format}`);
    }
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum) {
      errors.push(`${location}: below minimum ${schema.minimum}`);
    }
    if (schema.maximum !== undefined && value > schema.maximum) {
      errors.push(`${location}: above maximum ${schema.maximum}`);
    }
  }
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    for (const name of schema.required ?? []) {
      if (!(name in value)) errors.push(`${location}: missing required property ${name}`);
    }
    for (const [name, sub] of Object.entries(schema.properties ?? {})) {
      if (name in value) errors.push(...validateValue(value[name], sub, root, `${location}.${name}`));
    }
    if (schema.additionalProperties === false) {
      const known = new Set(Object.keys(schema.properties ?? {}));
      for (const name of Object.keys(value)) {
        if (!known.has(name)) errors.push(`${location}: additional property ${name} is not allowed`);
      }
    } else if (typeof schema.additionalProperties === "object") {
      for (const [name, field] of Object.entries(value)) {
        if (!(name in (schema.properties ?? {}))) {
          errors.push(...validateValue(field, schema.additionalProperties, root, `${location}.${name}`));
        }
      }
    }
  }
  if (Array.isArray(value) && schema.items !== undefined) {
    value.forEach((item, index) => {
      errors.push(...validateValue(item, schema.items, root, `${location}[${index}]`));
    });
  }
  if (schema.anyOf !== undefined) {
    const ok = schema.anyOf.some((option) => validateValue(value, option, root, location).length === 0);
    if (!ok) errors.push(`${location}: matches no anyOf option`);
  }
  if (schema.oneOf !== undefined) {
    const count = schema.oneOf.filter((option) => validateValue(value, option, root, location).length === 0).length;
    if (count !== 1) errors.push(`${location}: must match exactly one oneOf option (matched ${count})`);
  }
  if (schema.allOf !== undefined) {
    for (const option of schema.allOf) errors.push(...validateValue(value, option, root, location));
  }
  return errors;
}

export async function loadSchemas(root = repoRoot) {
  const dir = path.join(root, "contracts", "v1");
  const manifest = JSON.parse(await readFile(path.join(dir, "manifest.json"), "utf8"));
  const schemas = {};
  for (const entry of manifest.schemas) {
    schemas[entry.name] = JSON.parse(await readFile(path.join(root, entry.file), "utf8"));
  }
  return { manifest, schemas };
}

export async function checkContracts(root = repoRoot) {
  const errors = [];
  const { manifest, schemas } = await loadSchemas(root);
  const files = (await readdir(path.join(root, "contracts", "v1")))
    .filter((file) => file.endsWith(".schema.json"))
    .sort();
  const listed = new Set(manifest.schemas.map((entry) => path.basename(entry.file)));
  for (const file of files) {
    if (!listed.has(file)) errors.push(`contracts: ${file} exists but is not listed in manifest.json`);
  }
  for (const entry of manifest.schemas) {
    const schema = schemas[entry.name];
    if (!schema) {
      errors.push(`contracts: manifest entry ${entry.name} has no loadable schema`);
      continue;
    }
    if (schema.version !== 1) errors.push(`contracts: ${entry.name} version must be 1`);
    if (schema.type !== "object") errors.push(`contracts: ${entry.name} top-level type must be object`);
    const probe = validateValue({}, schema, schema);
    if (!probe.some((message) => message.includes("missing required property"))) {
      errors.push(`contracts: ${entry.name} must declare required properties`);
    }
  }
  return errors;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const errors = await checkContracts();
  if (errors.length > 0) {
    for (const error of errors.slice(0, 30)) console.error(error);
    console.error(`contracts: FAIL (${errors.length} issue(s))`);
    process.exit(1);
  }
  const { manifest } = await loadSchemas();
  console.log(`contracts: OK (${manifest.schemas.length} schemas listed and loadable)`);
}
