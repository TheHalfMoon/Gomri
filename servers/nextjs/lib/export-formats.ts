/**
 * Formats the bundled export runtime can render.
 *
 * `png` renders one PNG per slide and packages them into a ZIP archive whose
 * entries keep the renderer's `slide_001.png` naming. The Gomrey image archive
 * contract — deterministic entry names, slide ordering, the JPEG and WebP
 * re-encode, and the export budget — is owned by the FastAPI service, and it
 * keeps this runtime's entry names so both surfaces describe the same slides
 * the same way.
 */
export const BUNDLED_EXPORT_FORMATS = ["pdf", "pptx", "png"] as const;

export type BundledPresentationExportFormat =
  (typeof BUNDLED_EXPORT_FORMATS)[number];

export function isBundledExportFormat(
  value: unknown,
): value is BundledPresentationExportFormat {
  return (
    typeof value === "string" &&
    (BUNDLED_EXPORT_FORMATS as readonly string[]).includes(value)
  );
}
