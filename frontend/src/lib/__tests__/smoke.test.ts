import { describe, expect, it, vi } from "vitest";

describe("frontend test harness", () => {
  it("runs TypeScript tests in jsdom", () => {
    expect(document.documentElement).toBeDefined();
  });

  it("dispatches change events to matchMedia listeners", () => {
    const mediaQuery = window.matchMedia("(min-width: 768px)");
    const listener = vi.fn();
    const event = new Event("change");

    mediaQuery.addEventListener("change", listener);
    mediaQuery.dispatchEvent(event);
    mediaQuery.removeEventListener("change", listener);
    mediaQuery.dispatchEvent(event);

    expect(listener).toHaveBeenCalledOnce();
    expect(listener).toHaveBeenCalledWith(event);
  });

  it("supports legacy matchMedia listeners", () => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const listener = vi.fn();
    const event = new Event("change");

    mediaQuery.addListener(listener);
    mediaQuery.dispatchEvent(event);
    mediaQuery.removeListener(listener);
    mediaQuery.dispatchEvent(event);

    expect(listener).toHaveBeenCalledOnce();
    expect(listener).toHaveBeenCalledWith(event);
  });
});
