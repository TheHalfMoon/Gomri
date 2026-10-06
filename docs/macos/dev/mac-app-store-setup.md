# Gomrey Mac App Store Setup

Gomrey Mac App Store (MAS) builds are **fail-closed**. The repository does not
contain or fall back to Presenton App IDs, Team IDs, provisioning profiles, or
Store signing identities.

MAS builds must run on macOS with Apple signing tools available.

## Required Apple-owned inputs

Before building, create these resources in the Apple Developer account that will
own Gomrey:

1. A macOS App ID for Gomrey.
2. An Apple Development certificate for `mas-dev`.
3. An Apple Distribution certificate for App Store distribution.
4. A development provisioning profile for the Gomrey App ID.
5. A Mac App Store distribution provisioning profile for the same App ID.

Real provisioning profiles are local secrets and are ignored by Git.

## Canonical environment variables

| Variable | Required for | Meaning |
| --- | --- | --- |
| `GOMREY_MAC_TARGET` | scripts | `mas-dev`, `mas`, or `dmg` |
| `GOMREY_MAS_APP_ID` | MAS | Exact App ID registered for Gomrey |
| `GOMREY_TEAM_ID` | MAS | Apple Developer Team ID that owns the App ID |
| `GOMREY_MAS_DEV_PROVISIONING_PROFILE` | `mas-dev` | Absolute path to the development profile |
| `GOMREY_MAS_PROVISIONING_PROFILE` | `mas` | Absolute path to the distribution profile |
| `GOMREY_MAS_DEV_IDENTITY` | `mas-dev` | Apple Development signing identity; `CSC_NAME` is also accepted when explicitly set |
| `GOMREY_MAS_DISTRIBUTION_IDENTITY` | `mas` | Apple Distribution identity/qualifier |
| `GOMREY_MAS_IDENTITY` | `mas` | Alias for the distribution identity |
| `GOMREY_APP_STORE_VERSION` | `mas` | App Store version in `x.y.z` form |
| `GOMREY_APP_STORE_BUILD` | `mas` | Optional App Store build number |

No `PRESENTON_*` signing variable is accepted.

## Provisioning profiles

You may either set the absolute profile paths above or use these local filenames:

- `electron/build/GomreyMASDev.provisionprofile`
- `electron/build/GomreyMAS.provisionprofile`

Verify a profile on macOS:

```bash
security cms -D -i electron/build/GomreyMASDev.provisionprofile
security cms -D -i electron/build/GomreyMAS.provisionprofile
```

The build validates that the selected profile is decodable before packaging.

## Example: MAS development

```bash
export GOMREY_MAS_APP_ID="your.registered.gomrey.appid"
export GOMREY_TEAM_ID="YOUR_TEAM_ID"
export GOMREY_MAS_DEV_PROVISIONING_PROFILE="/absolute/path/GomreyMASDev.provisionprofile"
export GOMREY_MAS_DEV_IDENTITY="Apple Development: Your Name (YOUR_TEAM_ID)"

cd electron
npm run build:all:mas-dev
```

## Example: App Store distribution

```bash
export GOMREY_MAS_APP_ID="your.registered.gomrey.appid"
export GOMREY_TEAM_ID="YOUR_TEAM_ID"
export GOMREY_MAS_PROVISIONING_PROFILE="/absolute/path/GomreyMAS.provisionprofile"
export GOMREY_MAS_DISTRIBUTION_IDENTITY="Apple Distribution: Your Org (YOUR_TEAM_ID)"
export GOMREY_APP_STORE_VERSION="1.0.0"
export GOMREY_APP_STORE_BUILD="42"

cd electron
npm run build:all:mas
```

## Entitlements

`electron/build/entitlements.mas.plist` contains Gomrey's sandbox/runtime
capabilities only. P02-G3c removed the imported donor application-group
entitlement and donor Team/App identifiers.

The inherited helper entitlements remain in
`electron/build/entitlements.mas.inherit.plist`.

## Artwork

P02-G3c removed imported donor package artwork. Gomrey currently relies on
neutral Electron/electron-builder defaults until a Gomrey-owned binary icon set
is explicitly admitted. Do not rename or reuse donor artwork as Gomrey artwork.

## Microsoft Store

AppX packaging is disabled. Re-enable it only after a Gomrey-owned Microsoft
Store identity and signing certificate are available. The configured publisher
must exactly match the certificate Subject.

## Troubleshooting

**Missing `GOMREY_MAS_APP_ID` or `GOMREY_TEAM_ID`**

Create/verify the Gomrey App ID in Apple Developer, then set the canonical
variables. Do not substitute donor values.

**Missing provisioning profile**

Set the appropriate absolute-path environment variable or place the profile at
one of the canonical local filenames above.

**Profile cannot be decoded**

Re-download the profile from Apple Developer. Do not commit the real profile.

**MAS build on a non-macOS host**

MAS packaging requires macOS signing tools and intentionally fails closed.

## See also

- [Direct macOS distribution](./direct-distribution.md)
- [Signed DMG build steps](./signed-dmg-build-steps.md)
