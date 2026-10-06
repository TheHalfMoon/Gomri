"use client";

import { useLayoutEffect, useState, type CSSProperties } from "react";
import { cn } from "@/lib/utils";

interface GomreySplashLoaderProps {
  message?: string;
  className?: string;
}

export const GOMREY_SPLASH_MIN_DURATION_MS = 3000;

const SPLASH_ANIMATION_MS = 2600;
const GOMREY_WORDMARK = "GOMREY";

let splashSessionStartedAt: number | null = null;

function markSplashSessionStart(): number {
  if (splashSessionStartedAt === null) {
    splashSessionStartedAt = Date.now();
  }
  return splashSessionStartedAt;
}

function getSplashAnimationDelayMs(): number {
  const elapsed = Date.now() - markSplashSessionStart();
  return -Math.min(elapsed, SPLASH_ANIMATION_MS);
}

export function GomreySplashLoader({
  message = "Preparing your workspace",
  className,
}: GomreySplashLoaderProps) {
  const [animationDelayMs, setAnimationDelayMs] = useState(0);

  useLayoutEffect(() => {
    setAnimationDelayMs(getSplashAnimationDelayMs());
  }, []);

  const containerStyle: CSSProperties = {
    position: "fixed",
    inset: 0,
    zIndex: 2147483000,
    display: "flex",
    minHeight: "100vh",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    background: "#ffffff",
  };

  const surfaceStyle: CSSProperties = {
    position: "absolute",
    top: "50%",
    left: "50%",
    width: "142vmax",
    height: "142vmax",
    borderRadius: "50%",
    background: "#7a5af8",
    transform: "translate3d(-50%, -50%, 0) scale(0.001)",
    animation: `gomrey-splash-surface-grow ${SPLASH_ANIMATION_MS}ms linear ${animationDelayMs}ms both`,
    willChange: "transform",
    backfaceVisibility: "hidden",
  };

  const wordmarkStyle: CSSProperties = {
    position: "relative",
    zIndex: 1,
    width: "min(72vw, 620px)",
    height: "clamp(64px, 11vw, 118px)",
    transform: "translateZ(0)",
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
    fontSize: "clamp(42px, 8vw, 92px)",
    fontWeight: 700,
    letterSpacing: "0.12em",
    lineHeight: 1,
    textAlign: "center",
  };

  const wordmarkLayerStyle: CSSProperties = {
    position: "absolute",
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    whiteSpace: "nowrap",
  };

  return (
    <main
      aria-busy="true"
      aria-label={message}
      className={cn("gomrey-splash-loader", className)}
      role="status"
      style={containerStyle}
    >
      <div
        className="gomrey-splash-surface"
        aria-hidden="true"
        style={surfaceStyle}
      />
      <div
        className="gomrey-splash-wordmark"
        aria-hidden="true"
        style={wordmarkStyle}
      >
        <span
          className="gomrey-splash-wordmark-layer gomrey-splash-wordmark-base"
          style={{
            ...wordmarkLayerStyle,
            color: "#7a5af8",
          }}
        >
          {GOMREY_WORDMARK}
        </span>
        <span
          className="gomrey-splash-wordmark-layer gomrey-splash-wordmark-reveal"
          style={{
            ...wordmarkLayerStyle,
            color: "#ffffff",
            clipPath: "circle(0 at 50% 50%)",
            animation: `gomrey-splash-text-reveal ${SPLASH_ANIMATION_MS}ms linear ${animationDelayMs}ms both`,
            willChange: "clip-path",
          }}
        >
          {GOMREY_WORDMARK}
        </span>
      </div>
    </main>
  );
}
