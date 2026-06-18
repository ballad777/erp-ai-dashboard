"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from "react";

type FeedbackContextValue = {
  soundEnabled: boolean;
  setSoundEnabled: (enabled: boolean) => void;
  playSuccess: () => void;
  playError: () => void;
};

const FeedbackContext = createContext<FeedbackContextValue | null>(null);
const storageKey = "finai-feedback-v1";

export function FeedbackProvider({ children }: { children: ReactNode }) {
  const [soundEnabled, setSoundEnabledState] = useState(false);

  useEffect(() => {
    try {
      setSoundEnabledState(window.localStorage.getItem(storageKey) === "on");
    } catch {
      setSoundEnabledState(false);
    }
  }, []);

  const setSoundEnabled = useCallback((enabled: boolean) => {
    setSoundEnabledState(enabled);
    try {
      window.localStorage.setItem(storageKey, enabled ? "on" : "off");
    } catch {
      // Preference persistence is optional; visual feedback remains available.
    }
  }, []);

  const playSuccess = useCallback(() => {
    if (soundEnabled) playTone("success");
  }, [soundEnabled]);

  const playError = useCallback(() => {
    if (soundEnabled) playTone("error");
  }, [soundEnabled]);

  const value = useMemo(
    () => ({ soundEnabled, setSoundEnabled, playSuccess, playError }),
    [playError, playSuccess, setSoundEnabled, soundEnabled]
  );

  return (
    <FeedbackContext.Provider value={value}>
      {children}
    </FeedbackContext.Provider>
  );
}

export function useFeedback() {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error("useFeedback 必須在 FeedbackProvider 內使用。");
  }
  return context;
}

function playTone(tone: "success" | "error") {
  if (document.visibilityState !== "visible") return;
  const AudioContextClass =
    window.AudioContext ??
    (
      window as typeof window & {
        webkitAudioContext?: typeof AudioContext;
      }
    ).webkitAudioContext;
  if (!AudioContextClass) return;

  const context = new AudioContextClass();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const now = context.currentTime;

  oscillator.type = "sine";
  oscillator.frequency.setValueAtTime(tone === "success" ? 520 : 230, now);
  oscillator.frequency.exponentialRampToValueAtTime(
    tone === "success" ? 690 : 180,
    now + 0.12
  );
  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(0.035, now + 0.015);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.19);
  oscillator.addEventListener("ended", () => {
    void context.close();
  });
}

