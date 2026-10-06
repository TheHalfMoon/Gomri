# P02-G3a — Runtime State and Path Migration

**Parent:** #11  
**Canonical base:** `3927c8849a912696de33f38632bdebdfc5ce59b3`

## Goal

Move Gomrey's runtime path identity away from donor naming without making existing
Presenton-derived user data disappear and without copying, merging, renaming, or
deleting mutable state automatically.

## Safety model

G3a uses **reuse-first migration**.

- Fresh installs select the canonical `Gomrey` user-data directory.
- An existing legacy `Presenton Open Source` directory with authoritative app
  state is reused in place when canonical state is absent or only weaker.
- Canonical app state wins when it is authoritative and legacy state is only
  weaker configuration state.
- If both canonical and legacy directories contain equally authoritative state,
  startup fails closed with an actionable error. Gomrey does not guess which
  database is authoritative.
- `GOMREY_USER_DATA_DIRECTORY` is the explicit operator override for a
  conflict or a deliberately custom user-data root.

The machine-readable policy is `config/desktop-state-identity.json`.

## Authority markers

Strong state includes the local SQLite database (`fastapi.db`) and non-empty
Gomrey/Presenton app-owned data directories such as uploads, exports, templates,
images, fonts, conversion artifacts, memory state, or the development
`app_data` root.

A non-empty `userConfig.json` is configuration state but is weaker than a
database/app-owned content tree. Chromium caches and generic browser-profile
files do not establish application-state authority.

## Important non-goals

G3a does **not**:

- change the desktop app ID, bundle ID, Store identity, signing identity,
  executable name, installer name, or release artifact name;
- relabel or replace donor artwork;
- rename `@presenton/export-core`;
- physically move a user's existing database or assets;
- merge two state directories.

Those operations belong to later G3 grains after this resolver is qualified.

## Rollback

Because G3a selects a directory instead of moving it, rollback is non-destructive.
The legacy directory remains byte-for-byte in place. The explicit override can
select either directory if an operator needs to resolve a conflict.

The lower-level `presenton-app-data` fallback base is intentionally retained in G3a so installations that previously fell back there are not orphaned. Canonicalizing that fallback requires a separate two-root discovery/migration step.

## Qualification

Acceptance requires:

1. behavioral tests for fresh, canonical, legacy, conflict, and override paths;
2. Electron TypeScript compilation and source qualification;
3. cache-cleanup logic that knows both canonical and legacy ephemeral paths but
   never deletes user configuration, databases, exports, or other persistent
   content;
4. Graft exact-range analysis;
5. Alibaba Open Code Review delegation/host review evidence;
6. TypeSafe Jev exact-candidate review;
7. exact-head GitHub Actions success before a normal merge commit.
