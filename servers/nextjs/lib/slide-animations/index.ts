/**
 * Gomrey slide animation contract.
 *
 * A surface-agnostic catalog of slide animations plus deterministic stylesheet
 * generation. Adapted from the NextSlide OpenCode slide skill (MIT).
 * See docs/donors/nextslide-skill/NOTICE.md.
 */

export {
  findSlideAnimation,
  slideAnimationClassName,
  SLIDE_ANIMATIONS,
  SLIDE_ANIMATION_BY_ID,
  SLIDE_ANIMATION_CLASS_NAMES,
  SLIDE_ANIMATION_CLASS_PREFIX,
  SLIDE_ANIMATION_DURATIONS,
  SLIDE_ANIMATION_EASINGS,
  SLIDE_ANIMATION_KEYFRAME_PREFIX,
  SLIDE_ANIMATION_STAGGER_DELAYS,
  SLIDE_ANIMATION_VARIABLE_PREFIX,
  type SlideAnimationCategory,
  type SlideAnimationDefinition,
  type SlideAnimationDurationKey,
  type SlideAnimationEasing,
  type SlideAnimationEngine,
  type SlideAnimationId,
} from "./catalog";

export {
  buildSlideAnimationStylesheet,
  slideAnimationClassAttribute,
  SLIDE_ANIMATION_ACTIVE_ATTRIBUTE,
  SLIDE_ANIMATION_DELAY_CLASS_PREFIX,
  SLIDE_ANIMATION_DURATION_CLASS_PREFIX,
  SLIDE_ANIMATION_SELECTORS,
  type SlideAnimationStylesheetMode,
  type SlideAnimationStylesheetOptions,
} from "./stylesheet";
