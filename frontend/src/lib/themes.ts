export const themeIds = [
  "mist",
  "atlas",
  "iris",
  "clay",
  "sage",
  "frost",
  "graphite",
  "amber",
  "deep-sea",
  "midnight",
] as const;

export type ThemeId = (typeof themeIds)[number];

export type ThemeTokens = {
  readonly background: string;
  readonly surface: string;
  readonly surfaceElevated: string;
  readonly textPrimary: string;
  readonly textSecondary: string;
  readonly border: string;
  readonly accentPrimary: string;
  readonly accentSecondary: string;
  readonly success: string;
  readonly warning: string;
  readonly danger: string;
};

export type ProductTheme = {
  readonly id: ThemeId;
  readonly labelZh: string;
  readonly labelEn: string;
  readonly descriptionZh: string;
  readonly descriptionEn: string;
  readonly appearance: "light" | "dark";
  readonly tokens: ThemeTokens;
  readonly chart: readonly [string, string, string, string, string, string];
};

export const defaultThemeId: ThemeId = "mist";

const rawThemes = [
  {
    id: "mist",
    labelZh: "晨霧藍綠",
    labelEn: "Morning Mist",
    descriptionZh: "目前品牌預設，清楚而安靜",
    descriptionEn: "The calm, clear brand default",
    appearance: "light",
    tokens: {
      background: "#eef3f5",
      surface: "#ffffff",
      surfaceElevated: "#f7f9fa",
      textPrimary: "#122033",
      textSecondary: "#5f6f82",
      border: "#d7e1e8",
      accentPrimary: "#39777e",
      accentSecondary: "#315f8e",
      success: "#2c806c",
      warning: "#94651f",
      danger: "#ad5158",
    },
    chart: ["#39777e", "#315f8e", "#8b6f47", "#7b668f", "#3f806a", "#b05d62"],
  },
  {
    id: "atlas",
    labelZh: "Atlas 藍",
    labelEn: "Atlas Blue",
    descriptionZh: "理性、專業，適合密集分析",
    descriptionEn: "Focused and professional for dense analysis",
    appearance: "light",
    tokens: {
      background: "#edf2f6",
      surface: "#ffffff",
      surfaceElevated: "#f4f7fa",
      textPrimary: "#142238",
      textSecondary: "#5e6e83",
      border: "#d5e0e8",
      accentPrimary: "#315f8e",
      accentSecondary: "#467f84",
      success: "#347a68",
      warning: "#916323",
      danger: "#aa4f5b",
    },
    chart: ["#315f8e", "#467f84", "#8c7045", "#755f87", "#4d7f64", "#ad5961"],
  },
  {
    id: "iris",
    labelZh: "Iris 灰紫",
    labelEn: "Iris",
    descriptionZh: "柔和、有辨識度但不霓虹",
    descriptionEn: "Distinctive muted violet without neon",
    appearance: "light",
    tokens: {
      background: "#f1f0f4",
      surface: "#ffffff",
      surfaceElevated: "#f6f4f8",
      textPrimary: "#201d2e",
      textSecondary: "#6b6578",
      border: "#ded9e5",
      accentPrimary: "#6b638b",
      accentSecondary: "#4f7281",
      success: "#427866",
      warning: "#93622f",
      danger: "#a84f5d",
    },
    chart: ["#6b638b", "#4f7281", "#967244", "#437868", "#b05d68", "#697d4f"],
  },
  {
    id: "clay",
    labelZh: "Clay 暖灰",
    labelEn: "Clay",
    descriptionZh: "低刺激，適合閱讀長報告",
    descriptionEn: "Low-stimulation reading for long reports",
    appearance: "light",
    tokens: {
      background: "#f3f0ee",
      surface: "#fffdfc",
      surfaceElevated: "#f7f3f1",
      textPrimary: "#29211f",
      textSecondary: "#70645f",
      border: "#e2d9d5",
      accentPrimary: "#7b5f52",
      accentSecondary: "#526f76",
      success: "#4c7865",
      warning: "#8d5f29",
      danger: "#a5524d",
    },
    chart: ["#7b5f52", "#526f76", "#8a733e", "#6d6682", "#4c7865", "#aa5b56"],
  },
  {
    id: "sage",
    labelZh: "Sage 灰綠",
    labelEn: "Sage",
    descriptionZh: "自然沉穩，狀態辨識清楚",
    descriptionEn: "Natural, calm, and status-friendly",
    appearance: "light",
    tokens: {
      background: "#eef2ef",
      surface: "#ffffff",
      surfaceElevated: "#f4f7f5",
      textPrimary: "#17251f",
      textSecondary: "#627269",
      border: "#d7e1da",
      accentPrimary: "#4f6f61",
      accentSecondary: "#4f6682",
      success: "#34705a",
      warning: "#896627",
      danger: "#a34e52",
    },
    chart: ["#4f6f61", "#4f6682", "#967242", "#746184", "#3c7a70", "#a9585e"],
  },
  {
    id: "frost",
    labelZh: "Frost 高亮",
    labelEn: "Frost",
    descriptionZh: "最明亮，適合投影與簡報",
    descriptionEn: "High clarity for projection and presentations",
    appearance: "light",
    tokens: {
      background: "#f7f9fb",
      surface: "#ffffff",
      surfaceElevated: "#f4f7fa",
      textPrimary: "#172235",
      textSecondary: "#5f7085",
      border: "#d9e3eb",
      accentPrimary: "#526b88",
      accentSecondary: "#2f6178",
      success: "#2f7969",
      warning: "#8c6127",
      danger: "#a44d57",
    },
    chart: ["#526b88", "#2f6178", "#88703f", "#70668a", "#3e7763", "#a8525c"],
  },
  {
    id: "graphite",
    labelZh: "Graphite 灰階",
    labelEn: "Graphite",
    descriptionZh: "近單色，專注資料與結構",
    descriptionEn: "Near-monochrome focus on data structure",
    appearance: "light",
    tokens: {
      background: "#eff1f2",
      surface: "#ffffff",
      surfaceElevated: "#f5f6f7",
      textPrimary: "#20242a",
      textSecondary: "#676e77",
      border: "#dadee2",
      accentPrimary: "#666c75",
      accentSecondary: "#3e6571",
      success: "#3e7461",
      warning: "#85602f",
      danger: "#985157",
    },
    chart: ["#515862", "#3e6571", "#857044", "#6d637d", "#47735f", "#9a555b"],
  },
  {
    id: "amber",
    labelZh: "Amber 紙金",
    labelEn: "Amber Paper",
    descriptionZh: "溫和重點色，不使用亮橘",
    descriptionEn: "Warm emphasis without bright orange",
    appearance: "light",
    tokens: {
      background: "#f5f2ec",
      surface: "#fffefa",
      surfaceElevated: "#f8f5ef",
      textPrimary: "#28231b",
      textSecondary: "#70695f",
      border: "#e2ddd2",
      accentPrimary: "#806638",
      accentSecondary: "#526d78",
      success: "#4c7762",
      warning: "#855d1f",
      danger: "#a4534e",
    },
    chart: ["#806638", "#526d78", "#756383", "#477762", "#a35752", "#5e6685"],
  },
  {
    id: "deep-sea",
    labelZh: "Deep Sea 深色",
    labelEn: "Deep Sea",
    descriptionZh: "低眩光深色工作區",
    descriptionEn: "Low-glare dark workspace",
    appearance: "dark",
    tokens: {
      background: "#11171b",
      surface: "#182025",
      surfaceElevated: "#20292e",
      textPrimary: "#ecf2f3",
      textSecondary: "#aab7bd",
      border: "#334047",
      accentPrimary: "#5b9b96",
      accentSecondary: "#8298b7",
      success: "#72b59a",
      warning: "#d0a263",
      danger: "#de8182",
    },
    chart: ["#70b0ab", "#8fa4c3", "#d3aa68", "#a797c3", "#78b995", "#dc8589"],
  },
  {
    id: "midnight",
    labelZh: "Midnight 藍黑",
    labelEn: "Midnight",
    descriptionZh: "夜間分析，維持高可讀性",
    descriptionEn: "High-readability night analysis",
    appearance: "dark",
    tokens: {
      background: "#131720",
      surface: "#1b202b",
      surfaceElevated: "#232a36",
      textPrimary: "#eff2f7",
      textSecondary: "#aeb7c6",
      border: "#364050",
      accentPrimary: "#7085aa",
      accentSecondary: "#65a09a",
      success: "#74b398",
      warning: "#cca166",
      danger: "#da7d87",
    },
    chart: ["#8297bd", "#72aaa4", "#d0aa70", "#a99ac7", "#7db69d", "#de858e"],
  },
] satisfies readonly ProductTheme[];

function freezeTheme(theme: ProductTheme): ProductTheme {
  Object.freeze(theme.tokens);
  Object.freeze(theme.chart);

  return Object.freeze(theme);
}

export const themes: readonly ProductTheme[] = Object.freeze(
  rawThemes.map(freezeTheme),
);

function findDefaultTheme(): ProductTheme {
  const theme = themes.find(({ id }) => id === defaultThemeId);

  if (!theme) {
    throw new Error(
      `Default product theme "${defaultThemeId}" is not registered.`,
    );
  }

  return theme;
}

const defaultTheme = findDefaultTheme();

export function getTheme(id: string | null | undefined): ProductTheme {
  return themes.find((theme) => theme.id === id) ?? defaultTheme;
}
