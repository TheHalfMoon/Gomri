import fs from "fs";
import path from "path";

export const GOMREY_APP_DIRECTORY_NAME = "Gomrey";
export const LEGACY_PRESENTON_APP_DIRECTORY_NAME = "Presenton Open Source";
export const GOMREY_TEMP_DIRECTORY_NAME = "gomrey";
export const LEGACY_PRESENTON_TEMP_DIRECTORY_NAME = "presenton";

const STRONG_FILE_MARKERS = ["fastapi.db"] as const;
const STRONG_DIRECTORY_MARKERS = [
  "app_data",
  "images",
  "exports",
  "uploads",
  "templates",
  "fonts",
  "pptx-to-html",
  "pptx-to-json",
  "mem0",
] as const;
const CONFIG_MARKERS = ["userConfig.json"] as const;

export type PersistedStateLevel = "none" | "config" | "strong";

export type PersistedStateInspection = {
  level: PersistedStateLevel;
  markers: string[];
};

export type UserDataResolutionSource =
  | "override"
  | "canonical"
  | "legacy"
  | "fresh";

export type UserDataResolution = {
  directory: string;
  source: UserDataResolutionSource;
  canonicalState: PersistedStateInspection;
  legacyState: PersistedStateInspection;
};

function isMissingPathError(error: unknown): boolean {
  return (
    error instanceof Error &&
    "code" in error &&
    (error as NodeJS.ErrnoException).code === "ENOENT"
  );
}

function existingNonEmptyFile(filePath: string): boolean {
  try {
    const stat = fs.statSync(filePath);
    return stat.isFile() && stat.size > 0;
  } catch (error) {
    if (isMissingPathError(error)) return false;
    throw error;
  }
}

function existingNonEmptyDirectory(directoryPath: string): boolean {
  try {
    const stat = fs.statSync(directoryPath);
    if (!stat.isDirectory()) return false;
    return fs.readdirSync(directoryPath).length > 0;
  } catch (error) {
    if (isMissingPathError(error)) return false;
    throw error;
  }
}

export function inspectPersistedAppState(
  directory: string,
): PersistedStateInspection {
  const strongMarkers = [
    ...STRONG_FILE_MARKERS.filter((name) =>
      existingNonEmptyFile(path.join(directory, name)),
    ),
    ...STRONG_DIRECTORY_MARKERS.filter((name) =>
      existingNonEmptyDirectory(path.join(directory, name)),
    ),
  ];

  if (strongMarkers.length > 0) {
    return { level: "strong", markers: strongMarkers };
  }

  const configMarkers = CONFIG_MARKERS.filter((name) =>
    existingNonEmptyFile(path.join(directory, name)),
  );
  if (configMarkers.length > 0) {
    return { level: "config", markers: configMarkers };
  }

  return { level: "none", markers: [] };
}

function conflictError(
  canonicalDir: string,
  legacyDir: string,
  canonicalState: PersistedStateInspection,
  legacyState: PersistedStateInspection,
): Error {
  const markerSummary = (state: PersistedStateInspection) =>
    state.markers.length > 0 ? state.markers.join(", ") : state.level;

  return new Error(
    [
      "Gomrey found persisted application state in both canonical and legacy user-data directories.",
      `Canonical: ${canonicalDir} (${markerSummary(canonicalState)})`,
      `Legacy: ${legacyDir} (${markerSummary(legacyState)})`,
      "Set GOMREY_USER_DATA_DIRECTORY to the directory Gomrey should use. Gomrey will not merge or delete either directory automatically.",
    ].join(" "),
  );
}

export function resolveUserDataDirectory(options: {
  canonicalDir: string;
  legacyDir: string;
  overrideDir?: string;
}): UserDataResolution {
  const canonicalDir = path.resolve(options.canonicalDir);
  const legacyDir = path.resolve(options.legacyDir);
  const canonicalState = inspectPersistedAppState(canonicalDir);
  const legacyState = inspectPersistedAppState(legacyDir);

  if (options.overrideDir) {
    return {
      directory: path.resolve(options.overrideDir),
      source: "override",
      canonicalState,
      legacyState,
    };
  }

  const canonicalStrong = canonicalState.level === "strong";
  const legacyStrong = legacyState.level === "strong";

  if (canonicalStrong && legacyStrong) {
    throw conflictError(canonicalDir, legacyDir, canonicalState, legacyState);
  }
  if (canonicalStrong) {
    return {
      directory: canonicalDir,
      source: "canonical",
      canonicalState,
      legacyState,
    };
  }
  if (legacyStrong) {
    return {
      directory: legacyDir,
      source: "legacy",
      canonicalState,
      legacyState,
    };
  }

  const canonicalConfig = canonicalState.level === "config";
  const legacyConfig = legacyState.level === "config";
  if (canonicalConfig && legacyConfig) {
    throw conflictError(canonicalDir, legacyDir, canonicalState, legacyState);
  }
  if (canonicalConfig) {
    return {
      directory: canonicalDir,
      source: "canonical",
      canonicalState,
      legacyState,
    };
  }
  if (legacyConfig) {
    return {
      directory: legacyDir,
      source: "legacy",
      canonicalState,
      legacyState,
    };
  }

  return {
    directory: canonicalDir,
    source: "fresh",
    canonicalState,
    legacyState,
  };
}
