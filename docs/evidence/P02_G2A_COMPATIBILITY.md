# P02-G2a Compatibility Aliases

**Parent:** #8  
**Canonical base:** `1f325340dd7f4e1e8b5e61c480c595447165481c`

## Scope

G2a introduces Gomrey-owned external configuration and MCP protocol names while preserving imported Presenton names as explicit compatibility aliases.

## Precedence invariant

```text
canonical variable is present -> use its value, including an explicit empty value
canonical variable is absent  -> consult the legacy Presenton alias
both are absent                -> use the existing documented default
```

The machine-readable registry is `config/compatibility-aliases.json`.

## Stage 1

This commit covers FastAPI/MCP boundaries: public URL, community enablement, Electron runtime mode, FastEmbed cache, MCP request marker, and export-task Electron detection.

Outbound MCP traffic uses `X-Gomrey-MCP-Request`. Inbound handling accepts `X-Presenton-MCP-Request` only when the canonical header is absent.

## Deliberate non-renames

`PRESENTON_COMMUNITY_API_URL`, Presenton OAuth identities, `@presenton/export-core`, and desktop signing/store/installer identities remain donor or deferred contracts.

## Qualification

No CI or review PASS is claimed in this file before those tools run. G2a requires tests, Graft, Alibaba Open Code Review delegation evidence, TypeSafe Jev, and exact-head GitHub Actions before merge.
