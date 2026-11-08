/**
 * The shared CSS font-family stack.
 *
 * Every surface that names a font — the editor's DOM text layer, the inline
 * Tiptap editor, the measurement path and the HTML export renderer — routes
 * through this one function, so that measurement and rendering can never
 * disagree about which face a glyph will come from.
 *
 * The Arabic families in the fallback chain are SIL OFL 1.1 and are already
 * installed in the shipped container image (`fonts-noto-core`,
 * `fonts-noto-ui-core`). No new font binary is vendored, so this opens no
 * asset-rights question. A deployment that must not rely on Noto can point a
 * template's font at an uploaded licensed face; the fallback chain then only
 * ever matters for glyphs that face does not cover.
 */

/**
 * Arabic-capable families named after the design font.
 *
 * CSS falls back per glyph, so an Arabic character inside a Latin-design run
 * lands on the Arabic face automatically. That is why the renderer never
 * splits a run to apply a per-script font: splitting would break the
 * Unicode Bidirectional Algorithm's ability to reorder across the split.
 */
export const ARABIC_FALLBACK_FAMILIES = [
  "Noto Naskh Arabic",
  "Noto Sans Arabic",
  "Noto Sans Arabic UI",
] as const;

/**
 * Families that are portable to a reader's machine and cover Arabic.
 *
 * Arial and Tahoma exist on Windows and macOS. They are named *first* for
 * right-to-left content so that the font name recorded in an exported
 * artifact covers the script actually used. They are not installed in the
 * container image, so on the render side the Noto entries behind them carry
 * the glyphs.
 */
export const PORTABLE_ARABIC_FAMILIES = ["Arial", "Tahoma"] as const;

function escapeFamily(family: string): string {
  return family
    .trim()
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'")
    .replace(/[\r\n\f]/g, " ");
}

export function cssFontFamilyStack(
  family: string,
  options: { rtl?: boolean } = {},
): string {
  const design = `'${escapeFamily(family) || "Arial"}'`;
  const arabic = ARABIC_FALLBACK_FAMILIES.map(
    (name) => `'${name}'`,
  ).join(", ");

  if (options.rtl) {
    const portable = PORTABLE_ARABIC_FAMILIES.map(
      (name) => `'${name}'`,
    ).join(", ");
    return `${portable}, ${arabic}, ${design}, Helvetica, sans-serif`;
  }

  return `${design}, ${arabic}, Helvetica, sans-serif`;
}
