import { describe, expect, it } from "vitest";

import { themes } from "@/lib/themes";

type Rgb = {
  red: number;
  green: number;
  blue: number;
};

const textTokens = [
  ["textPrimary", "primary text"],
  ["textSecondary", "secondary text"]
] as const;

const surfaceTokens = [
  ["surface", "surface"],
  ["surfaceElevated", "elevated surface"]
] as const;

const accentTokens = [
  ["accentPrimary", "primary accent"],
  ["accentSecondary", "secondary accent"]
] as const;

describe("theme contrast", () => {
  it("keeps primary and secondary text at AA contrast on every surface", () => {
    for (const theme of themes) {
      for (const [textToken, textLabel] of textTokens) {
        for (const [surfaceToken, surfaceLabel] of surfaceTokens) {
          expect(
            contrastRatio(
              theme.tokens[textToken],
              theme.tokens[surfaceToken]
            ),
            `${theme.id} ${textLabel} on ${surfaceLabel}`
          ).toBeGreaterThanOrEqual(4.5);
        }
      }
    }
  });

  it("keeps control accents legible enough for non-text indicators", () => {
    for (const theme of themes) {
      for (const [accentToken, accentLabel] of accentTokens) {
        for (const [surfaceToken, surfaceLabel] of surfaceTokens) {
          expect(
            contrastRatio(
              theme.tokens[accentToken],
              theme.tokens[surfaceToken]
            ),
            `${theme.id} ${accentLabel} on ${surfaceLabel}`
          ).toBeGreaterThanOrEqual(3);
        }
      }
    }
  });
});

function contrastRatio(foreground: string, background: string) {
  const foregroundLuminance = relativeLuminance(hexToRgb(foreground));
  const backgroundLuminance = relativeLuminance(hexToRgb(background));
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);

  return (lighter + 0.05) / (darker + 0.05);
}

function relativeLuminance({ red, green, blue }: Rgb) {
  const [linearRed, linearGreen, linearBlue] = [red, green, blue].map(
    toLinearChannel
  );

  return linearRed * 0.2126 + linearGreen * 0.7152 + linearBlue * 0.0722;
}

function toLinearChannel(channel: number) {
  const normalized = channel / 255;

  return normalized <= 0.03928
    ? normalized / 12.92
    : ((normalized + 0.055) / 1.055) ** 2.4;
}

function hexToRgb(hex: string): Rgb {
  const normalized = hex.replace("#", "");
  const value = Number.parseInt(normalized, 16);

  return {
    red: (value >> 16) & 255,
    green: (value >> 8) & 255,
    blue: value & 255
  };
}
