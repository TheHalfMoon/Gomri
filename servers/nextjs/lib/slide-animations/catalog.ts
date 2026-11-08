/**
 * Gomrey slide animation catalog.
 *
 * Adapted from the NextSlide OpenCode slide skill.
 *   repository : https://github.com/0xRafie/nextslide
 *   revision   : 90a46f933b3056d27460400c915ef268a9ec3f56
 *   source file: animation-library.md
 *   license    : MIT — Copyright (c) 2026 Danish Rafie Ekaputra
 *
 * Full attribution and adaptation record: docs/donors/nextslide-skill/NOTICE.md
 * Donor license text: docs/donors/nextslide-skill/LICENSE
 *
 * ADAPTATION NOTES (why this is not a verbatim copy)
 * -------------------------------------------------
 * 1. Namespace. The donor emits `animate-*` classes and `ns-*` keyframes. The
 *    donor's own base rule is `[class*="animate-"] { opacity: 0; ... }`.
 *    Tailwind CSS v4 ships `animate-spin`, `animate-pulse`, `animate-bounce`
 *    and `animate-ping` utilities. A wildcard attribute selector would match
 *    those and blank every spinner and loading indicator in the product to
 *    `opacity: 0`. Gomrey therefore owns an explicit `gs-anim-*` namespace and
 *    never uses wildcard class matching.
 * 2. No wildcard selectors. Every rule below targets explicitly enumerated
 *    Gomrey classes, so the animation contract cannot affect unrelated UI.
 * 3. Surface-agnostic activation. The donor gates playback on a `.slide.active`
 *    DOM contract that does not exist in Gomrey. Gomrey instead supports two
 *    explicit modes (see `stylesheet.ts`): `auto` for self-contained exports
 *    and `gated` for presenter-style surfaces that mark the visible slide with
 *    `[data-gs-slide-active="true"]`.
 * 4. Honest engine classification. The donor's `animate-counter-up` is not a
 *    CSS animation at all — it is a marker class driven by a JavaScript
 *    controller in the donor's HTML template. Gomrey records that truthfully as
 *    `engine: "controller"` instead of shipping a class that silently does
 *    nothing.
 * 5. Reduced motion is scoped. The donor's reduced-motion block uses a
 *    universal `*` selector with `!important`, which would freeze unrelated
 *    product chrome. Gomrey scopes it to the enumerated Gomrey animation
 *    classes only.
 */

/** Stable, surface-independent identifier for a slide animation. */
export type SlideAnimationId =
  | "fade-up"
  | "fade-down"
  | "fade-left"
  | "fade-right"
  | "fade-in"
  | "scale-up"
  | "scale-down"
  | "scale-x"
  | "scale-y"
  | "blur-in"
  | "flip-x"
  | "flip-y"
  | "zoom-in"
  | "pop"
  | "rotate-in"
  | "slide-in-left"
  | "slide-in-right"
  | "typewriter"
  | "counter-up"
  | "draw-line"
  | "pulse"
  | "glow"
  | "float"
  | "shimmer";

/**
 * `css`      — fully expressed by the generated stylesheet.
 * `controller` — requires a runtime controller (counter) or an author-supplied
 *                CSS variable (SVG path length). The stylesheet emits the
 *                supporting declarations; the driving behaviour is not part of
 *                this module and is never claimed to be.
 */
export type SlideAnimationEngine = "css" | "controller";

export type SlideAnimationCategory = "entrance" | "emphasis";

export type SlideAnimationEasing =
  | "default"
  | "bounce"
  | "smooth"
  | "spring"
  | "ease-in-out"
  | "linear"
  | "steps";

export interface SlideAnimationDefinition {
  /** Stable machine identifier. Persisted in artifact data; never renamed. */
  readonly id: SlideAnimationId;
  /** Gomrey-owned CSS class applied to the animated element. */
  readonly className: string;
  /** Gomrey-owned keyframe name, or `null` for controller-backed animations. */
  readonly keyframeName: string | null;
  readonly category: SlideAnimationCategory;
  readonly engine: SlideAnimationEngine;
  /** Human-readable intent, used by the authoring UI. */
  readonly description: string;
  /**
   * CSS declarations that make up the keyframe body. `from`/`to` steps are
   * preserved from the donor so visual behaviour is unchanged.
   */
  readonly keyframes: string;
  /** Default duration in milliseconds. */
  readonly durationMs: number;
  /** Default easing preset id. */
  readonly easing: SlideAnimationEasing;
  /** `1` for one-shot animations, `Infinity` for looping emphasis animations. */
  readonly iterationCount: number;
  /**
   * `true` when the element must stay hidden until the animation starts.
   * Such elements are restored to full opacity under reduced motion.
   */
  readonly hidesUntilStart: boolean;
  /**
   * Extra static declarations the animation depends on, such as
   * `transform-origin`. Applied to the animated element.
   */
  readonly elementDeclarations?: Readonly<Record<string, string>>;
  /**
   * Data attribute a runtime controller reads to drive this animation.
   * Only present for `engine: "controller"` animations.
   */
  readonly controllerAttribute?: string;
  /**
   * CSS custom property a renderer must supply for the effect to be exact.
   * Only present for animations that depend on measured geometry.
   */
  readonly requiredCustomProperty?: string;
}

/** Namespace prefix for every Gomrey-owned animation class. */
export const SLIDE_ANIMATION_CLASS_PREFIX = "gs-anim";

/** Namespace prefix for every Gomrey-owned keyframe name. */
export const SLIDE_ANIMATION_KEYFRAME_PREFIX = "gs-keyframe";

/** Namespace prefix for every Gomrey-owned animation CSS custom property. */
export const SLIDE_ANIMATION_VARIABLE_PREFIX = "gs";

/**
 * Easing curves, adapted from the donor's easing presets.
 *
 * `ease-in-out`, `linear` and `steps` are retained because the donor uses them
 * directly for the emphasis, shimmer and typewriter animations; collapsing
 * them into the four named curves would change the donor's visual behaviour.
 */
export const SLIDE_ANIMATION_EASINGS: Readonly<
  Record<SlideAnimationEasing, string>
> = {
  default: "cubic-bezier(0.16, 1, 0.3, 1)",
  bounce: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
  spring: "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
  "ease-in-out": "ease-in-out",
  linear: "linear",
  steps: "steps(40, end)",
};

/** Stagger delays in milliseconds, adapted from the donor's stagger presets. */
export const SLIDE_ANIMATION_STAGGER_DELAYS = [
  100, 200, 300, 400, 500, 600, 800, 1000,
] as const;

/** Duration modifiers in milliseconds, adapted from the donor's duration presets. */
export const SLIDE_ANIMATION_DURATIONS = {
  fast: 300,
  normal: 500,
  slow: 800,
} as const;

export type SlideAnimationDurationKey = keyof typeof SLIDE_ANIMATION_DURATIONS;

function entrance(
  id: SlideAnimationId,
  description: string,
  keyframes: string,
  options: {
    durationMs?: number;
    easing?: SlideAnimationEasing;
    elementDeclarations?: Record<string, string>;
    controllerAttribute?: string;
    requiredCustomProperty?: string;
    engine?: SlideAnimationEngine;
    hidesUntilStart?: boolean;
  } = {},
): SlideAnimationDefinition {
  const engine = options.engine ?? "css";
  // A controller-backed animation has no CSS keyframes. Emitting a keyframe
  // name for it would advertise a keyframe block that is never emitted, so the
  // contract stays honest by exposing `null`.
  const isControllerBacked = engine === "controller";
  return {
    id,
    className: `${SLIDE_ANIMATION_CLASS_PREFIX}-${id}`,
    keyframeName: isControllerBacked
      ? null
      : `${SLIDE_ANIMATION_KEYFRAME_PREFIX}-${id}`,
    category: "entrance",
    engine,
    description,
    keyframes: isControllerBacked ? "" : keyframes,
    durationMs: options.durationMs ?? SLIDE_ANIMATION_DURATIONS.normal,
    easing: options.easing ?? "default",
    iterationCount: 1,
    // A controller-backed animation has no CSS keyframe to reveal the element,
    // so it must never be hidden by the static rule. Leaving it hidden would
    // make the element permanently invisible.
    hidesUntilStart: isControllerBacked
      ? false
      : (options.hidesUntilStart ?? true),
    elementDeclarations: options.elementDeclarations,
    controllerAttribute: options.controllerAttribute,
    requiredCustomProperty: options.requiredCustomProperty,
  };
}

function emphasis(
  id: SlideAnimationId,
  description: string,
  keyframes: string,
  options: {
    durationMs?: number;
    easing?: SlideAnimationEasing;
    elementDeclarations?: Record<string, string>;
  } = {},
): SlideAnimationDefinition {
  return {
    id,
    className: `${SLIDE_ANIMATION_CLASS_PREFIX}-${id}`,
    keyframeName: `${SLIDE_ANIMATION_KEYFRAME_PREFIX}-${id}`,
    category: "emphasis",
    engine: "css",
    description,
    keyframes,
    durationMs: options.durationMs ?? 2000,
    easing: options.easing ?? "smooth",
    iterationCount: Infinity,
    hidesUntilStart: false,
    elementDeclarations: options.elementDeclarations,
  };
}

/**
 * The canonical Gomrey slide animation catalog.
 *
 * Twenty entrance animations and four emphasis animations, preserving the
 * donor's visual behaviour while re-namespacing the public contract.
 */
export const SLIDE_ANIMATIONS: readonly SlideAnimationDefinition[] = [
  entrance("fade-up", "Default content entrance with vertical lift.", "from { opacity: 0; transform: translateY(30px); }\n  to { opacity: 1; transform: translateY(0); }"),
  entrance("fade-down", "Content enters from above.", "from { opacity: 0; transform: translateY(-30px); }\n  to { opacity: 1; transform: translateY(0); }"),
  entrance("fade-left", "Content enters from the right side.", "from { opacity: 0; transform: translateX(30px); }\n  to { opacity: 1; transform: translateX(0); }"),
  entrance("fade-right", "Content enters from the left side.", "from { opacity: 0; transform: translateX(-30px); }\n  to { opacity: 1; transform: translateX(0); }"),
  entrance("fade-in", "Opacity only, no movement.", "from { opacity: 0; }\n  to { opacity: 1; }"),
  entrance("scale-up", "Subtle zoom in for images and cards.", "from { opacity: 0; transform: scale(0.85); }\n  to { opacity: 1; transform: scale(1); }"),
  entrance("scale-down", "Zoom out entrance.", "from { opacity: 0; transform: scale(1.15); }\n  to { opacity: 1; transform: scale(1); }"),
  entrance(
    "scale-x",
    "Horizontal bar fill for progress bars and horizontal charts.",
    "from { transform: scaleX(0); }\n  to { transform: scaleX(1); }",
    { hidesUntilStart: false, elementDeclarations: { "transform-origin": "left center" } },
  ),
  entrance(
    "scale-y",
    "Vertical bar fill for vertical bar charts.",
    "from { transform: scaleY(0); }\n  to { transform: scaleY(1); }",
    { hidesUntilStart: false, elementDeclarations: { "transform-origin": "bottom center" } },
  ),
  entrance("blur-in", "Focus-in effect using blur.", "from { opacity: 0; filter: blur(10px); }\n  to { opacity: 1; filter: blur(0); }"),
  entrance("flip-x", "Card flip on the horizontal axis.", "from { opacity: 0; transform: perspective(800px) rotateX(90deg); }\n  to { opacity: 1; transform: perspective(800px) rotateX(0); }"),
  entrance("flip-y", "Card flip on the vertical axis.", "from { opacity: 0; transform: perspective(800px) rotateY(90deg); }\n  to { opacity: 1; transform: perspective(800px) rotateY(0); }"),
  entrance("zoom-in", "Scale from zero with a slight bounce.", "from { opacity: 0; transform: scale(0); }\n  60% { opacity: 1; transform: scale(1.08); }\n  to { opacity: 1; transform: scale(1); }", {
    easing: "bounce",
  }),
  entrance("pop", "Playful bounce entrance.", "0% { opacity: 0; transform: scale(0); }\n  50% { opacity: 1; transform: scale(1.12); }\n  70% { transform: scale(0.95); }\n  100% { opacity: 1; transform: scale(1); }", {
    easing: "spring",
  }),
  entrance("rotate-in", "Subtle rotation entrance.", "from { opacity: 0; transform: rotate(-10deg) scale(0.9); }\n  to { opacity: 1; transform: rotate(0) scale(1); }"),
  entrance("slide-in-left", "Full-panel entrance from the left edge.", "from { opacity: 0; transform: translateX(-100%); }\n  to { opacity: 1; transform: translateX(0); }"),
  entrance("slide-in-right", "Full-panel entrance from the right edge.", "from { opacity: 0; transform: translateX(100%); }\n  to { opacity: 1; transform: translateX(0); }"),
  entrance("typewriter", "Character-by-character reveal via clip path.", "from { clip-path: inset(0 100% 0 0); }\n  to { clip-path: inset(0 0 0 0); }", {
    durationMs: 2000,
    easing: "steps",
    hidesUntilStart: false,
    elementDeclarations: { "display": "inline-block" },
  }),
  entrance("counter-up", "Numeric count-up driven by a runtime controller.", "", {
    engine: "controller",
    durationMs: 1500,
    controllerAttribute: "data-gs-count-target",
  }),
  entrance("draw-line", "SVG stroke reveal for line drawings.", "from { stroke-dashoffset: var(--gs-path-length, 1000); }\n  to { stroke-dashoffset: 0; }", {
    durationMs: 1500,
    easing: "smooth",
    hidesUntilStart: false,
    requiredCustomProperty: "--gs-path-length",
    elementDeclarations: { "stroke-dasharray": "var(--gs-path-length, 1000)" },
  }),
  emphasis("pulse", "Gentle breathing scale for highlighted cards.", "0%, 100% { transform: scale(1); }\n  50% { transform: scale(1.05); }", {
    easing: "ease-in-out",
  }),
  emphasis("glow", "Soft box-shadow glow for featured elements.", "0%, 100% { box-shadow: 0 0 8px rgba(59, 130, 246, 0.2); }\n  50% { box-shadow: 0 0 24px rgba(59, 130, 246, 0.5); }", {
    easing: "ease-in-out",
  }),
  emphasis("float", "Gentle vertical bob for decorative icons.", "0%, 100% { transform: translateY(0); }\n  50% { transform: translateY(-8px); }", {
    durationMs: 3000,
    easing: "ease-in-out",
  }),
  emphasis("shimmer", "Background gradient sweep for skeleton states.", "0% { background-position: -200% 0; }\n  100% { background-position: 200% 0; }", {
    easing: "linear",
    elementDeclarations: {
      background:
        "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%)",
      "background-size": "200% 100%",
    },
  }),
];

/** Lookup map from animation id to its definition. */
export const SLIDE_ANIMATION_BY_ID: Readonly<
  Record<SlideAnimationId, SlideAnimationDefinition>
> = Object.freeze(
  Object.fromEntries(
    SLIDE_ANIMATIONS.map((animation) => [animation.id, animation]),
  ) as Record<SlideAnimationId, SlideAnimationDefinition>,
);

/** All Gomrey animation class names, in catalog order. */
export const SLIDE_ANIMATION_CLASS_NAMES: readonly string[] =
  SLIDE_ANIMATIONS.map((animation) => animation.className);

/**
 * Resolve an animation definition by id.
 *
 * Returns `undefined` for unknown ids so callers can reject untrusted input
 * instead of silently rendering an inert class.
 */
export function findSlideAnimation(
  id: string | null | undefined,
): SlideAnimationDefinition | undefined {
  if (typeof id !== "string") {
    return undefined;
  }
  return Object.prototype.hasOwnProperty.call(SLIDE_ANIMATION_BY_ID, id)
    ? SLIDE_ANIMATION_BY_ID[id as SlideAnimationId]
    : undefined;
}

/**
 * Build the Gomrey class attribute for an animation.
 *
 * Returns an empty string for unknown ids. Callers must treat an empty result
 * as "no animation" and must not fall back to a donor class name.
 */
export function slideAnimationClassName(id: string | null | undefined): string {
  return findSlideAnimation(id)?.className ?? "";
}
