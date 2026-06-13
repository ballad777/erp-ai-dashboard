import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--color-background) / <alpha-value>)",
        foreground: "rgb(var(--color-foreground) / <alpha-value>)",
        card: "rgb(var(--color-card) / <alpha-value>)",
        "card-foreground": "rgb(var(--color-card-foreground) / <alpha-value>)",
        popover: "rgb(var(--color-popover) / <alpha-value>)",
        "popover-foreground": "rgb(var(--color-popover-foreground) / <alpha-value>)",
        primary: "rgb(var(--color-primary) / <alpha-value>)",
        "primary-foreground": "rgb(var(--color-primary-foreground) / <alpha-value>)",
        secondary: "rgb(var(--color-secondary) / <alpha-value>)",
        "secondary-foreground": "rgb(var(--color-secondary-foreground) / <alpha-value>)",
        muted: "rgb(var(--color-muted) / <alpha-value>)",
        "muted-foreground": "rgb(var(--color-muted-foreground) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
        "accent-foreground": "rgb(var(--color-accent-foreground) / <alpha-value>)",
        destructive: "rgb(var(--color-destructive) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        input: "rgb(var(--color-input) / <alpha-value>)",
        ring: "rgb(var(--color-ring) / <alpha-value>)",
        ink: "rgb(var(--color-foreground) / <alpha-value>)",
        line: "rgb(var(--color-border) / <alpha-value>)",
        panel: "rgb(var(--color-card) / <alpha-value>)",
        canvas: "rgb(var(--color-background) / <alpha-value>)",
        brand: "rgb(var(--color-primary) / <alpha-value>)",
        navy: "rgb(var(--color-primary-deep) / <alpha-value>)",
        amber: "rgb(var(--color-amber) / <alpha-value>)"
      },
      boxShadow: {
        soft: "var(--shadow-mid)"
      }
    }
  },
  plugins: []
};

export default config;
