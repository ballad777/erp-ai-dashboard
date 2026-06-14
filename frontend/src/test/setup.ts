import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());

Object.defineProperty(window, "matchMedia", {
  configurable: true,
  writable: true,
  value: (query: string): MediaQueryList => {
    const listeners = new Set<EventListenerOrEventListenerObject>();
    const mediaQueryList = {
      matches: false,
      media: query,
      onchange: null,
      addListener: (
        listener:
          | ((this: MediaQueryList, event: MediaQueryListEvent) => void)
          | null,
      ) => {
        if (listener) listeners.add(listener as EventListener);
      },
      removeListener: (
        listener:
          | ((this: MediaQueryList, event: MediaQueryListEvent) => void)
          | null,
      ) => {
        if (listener) listeners.delete(listener as EventListener);
      },
      addEventListener: (
        type: string,
        listener: EventListenerOrEventListenerObject | null,
      ) => {
        if (type === "change" && listener) listeners.add(listener);
      },
      removeEventListener: (
        type: string,
        listener: EventListenerOrEventListenerObject | null,
      ) => {
        if (type === "change" && listener) listeners.delete(listener);
      },
      dispatchEvent: (event: Event) => {
        if (event.type === "change") {
          listeners.forEach((listener) => {
            if (typeof listener === "function") {
              listener.call(mediaQueryList, event);
            } else {
              listener.handleEvent(event);
            }
          });
        }

        return !event.defaultPrevented;
      },
    } as MediaQueryList;

    return mediaQueryList;
  },
});
