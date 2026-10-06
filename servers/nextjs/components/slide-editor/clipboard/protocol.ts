export const GOMREY_TEMPLATE_V2_CLIPBOARD_FORMAT = "gomrey/template-v2" as const;
export const LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_FORMAT =
  "presenton/template-v2" as const;

export const GOMREY_TEMPLATE_V2_CLIPBOARD_MIME =
  "application/x-gomrey-template-v2";
export const LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_MIME =
  "application/x-presenton-template-v2";

export const GOMREY_TEMPLATE_V2_CLIPBOARD_PREFIX = "GOMREY_TEMPLATE_V2:";
export const LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_PREFIX =
  "PRESENTON_TEMPLATE_V2:";

export const GOMREY_TEMPLATE_V2_CLIPBOARD_STORAGE_KEY =
  "gomrey:template-v2-clipboard";
export const LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_STORAGE_KEY =
  "presenton:template-v2-clipboard";

type ClipboardDataLike = {
  readonly types: readonly string[];
  getData(type: string): string;
};

export function isSupportedTemplateV2ClipboardFormat(
  value: unknown,
): value is
  | typeof GOMREY_TEMPLATE_V2_CLIPBOARD_FORMAT
  | typeof LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_FORMAT {
  return (
    value === GOMREY_TEMPLATE_V2_CLIPBOARD_FORMAT ||
    value === LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_FORMAT
  );
}

export function serializedTemplateV2PayloadFromText(text: string): string {
  if (text.startsWith(GOMREY_TEMPLATE_V2_CLIPBOARD_PREFIX)) {
    return text.slice(GOMREY_TEMPLATE_V2_CLIPBOARD_PREFIX.length);
  }
  if (text.startsWith(LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_PREFIX)) {
    return text.slice(LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_PREFIX.length);
  }
  return "";
}

export function serializedTemplateV2PayloadFromClipboardData(
  clipboardData: ClipboardDataLike | null | undefined,
): string {
  if (!clipboardData) return "";
  if (clipboardData.types.includes(GOMREY_TEMPLATE_V2_CLIPBOARD_MIME)) {
    return clipboardData.getData(GOMREY_TEMPLATE_V2_CLIPBOARD_MIME);
  }
  if (
    clipboardData.types.includes(LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_MIME)
  ) {
    return clipboardData.getData(LEGACY_PRESENTON_TEMPLATE_V2_CLIPBOARD_MIME);
  }
  return "";
}
