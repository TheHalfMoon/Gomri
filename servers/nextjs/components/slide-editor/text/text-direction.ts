/**
 * Script and text-direction classification — the TypeScript mirror of
 * `servers/fastapi/gomrey/text_direction.py`.
 *
 * The two implementations share one set of ranges and one resolution rule, so
 * that a decision made here agrees with the Python side and with the browser
 * that will render the text. The qualification suite asserts the agreement.
 *
 * Two distinct concepts:
 *
 * - `scriptProfile(text)` — *which* scripts and numeral systems are present.
 *   The `direction` field is **presence-based**: `rtl` when Arabic is present
 *   and Latin is not, `mixed` when both are present, `ltr` otherwise. This
 *   matches the Python `script_profile`.
 * - `resolveBaseDirection(text)` — *which* base direction the text's
 *   paragraphs have, by the **first-strong-character** rule that CSS
 *   `dir="auto"` implements.
 */

/** Characters with a strong right-to-left bidi type. */
const RTL_STRONG_PATTERN =
  /[֐-ࣿיִ-﷿ﹰ-ﻼ]/u;

/** Characters with a strong left-to-right bidi type. */
const LTR_STRONG_PATTERN =
  /[A-Za-zÀ-ʯͰ-֏Ѐ-ԯ԰-ᙿḀ-῿Ⰰ-퟿]/u;

/** Arabic script, including the Arabic Presentation Forms blocks. */
const ARABIC_PATTERN = /[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]/u;

/** Latin letters. */
const LATIN_PATTERN = /[A-Za-z]/u;

/** Arabic-Indic digits. */
const ARABIC_INDIC_DIGITS_PATTERN = /[٠-٩]/u;

/** Western digits. */
const WESTERN_DIGITS_PATTERN = /[0-9]/u;

/**
 * The ranges, as data, so the qualification suite can check the Python and
 * TypeScript declarations against one another.
 */
export const SCRIPT_RANGES = {
  arabic: "[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]",
  latin: "[A-Za-z]",
  arabic_indic_digits: "[٠-٩]",
  western_digits: "[0-9]",
} as const;

export interface TextScriptProfile {
  readonly arabic: boolean;
  readonly latin: boolean;
  readonly arabic_indic_digits: boolean;
  readonly western_digits: boolean;
  readonly direction: "rtl" | "mixed" | "ltr";
}

/** Observe script and numeral systems present in the text. */
export function scriptProfile(text: string): TextScriptProfile {
  const arabic = ARABIC_PATTERN.test(text);
  const latin = LATIN_PATTERN.test(text);
  return {
    arabic,
    latin,
    arabic_indic_digits: ARABIC_INDIC_DIGITS_PATTERN.test(text),
    western_digits: WESTERN_DIGITS_PATTERN.test(text),
    direction: arabic && !latin ? "rtl" : arabic && latin ? "mixed" : "ltr",
  };
}

/**
 * Resolve the base direction of `text` from its first strong character.
 *
 * Returns `"rtl"` or `"ltr"`. This is the rule CSS `dir="auto"` implements,
 * so it agrees with the browser that will render the text. Digits and
 * punctuation do not decide, and text with no strong character is `ltr`.
 */
export function resolveBaseDirection(text: string): "rtl" | "ltr" {
  for (const character of text) {
    if (RTL_STRONG_PATTERN.test(character)) return "rtl";
    if (LTR_STRONG_PATTERN.test(character)) return "ltr";
  }
  return "ltr";
}

/**
 * Whether the text contains any right-to-left character.
 *
 * Konva lays rich-text runs out as individual left-to-right canvas segments,
 * so scripts that require bidi reordering are routed through the browser text
 * engine instead, to keep their visual order identical in the DOM editor.
 */
export function containsRtlText(text: string): boolean {
  return RTL_STRONG_PATTERN.test(text);
}
