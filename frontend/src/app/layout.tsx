import type { Metadata } from "next";
import { FeedbackProvider } from "@/components/FeedbackProvider";
import { LocaleProvider } from "@/components/LocaleProvider";
import { ThemeProvider } from "@/components/ThemeProvider";
import { WorkspaceProvider } from "@/components/WorkspaceProvider";
import {
  defaultThemeId,
  getThemeRuntimeVariables,
  themes,
} from "@/lib/themes";
import "./globals.css";
import "./product-themes.css";
import "./product-interface.css";
import "./product-motion.css";

const productThemeStorageKey = "finai-product-theme-v1";
const productThemeScriptId = "finai-product-theme-init";

const productThemeInitializationData = Object.fromEntries(
  themes.map((theme) => [
    theme.id,
    {
      appearance: theme.appearance,
      variables: getThemeRuntimeVariables(theme)
    }
  ])
);

const productThemeInitializationScript = `(()=>{const themes=${JSON.stringify(
  productThemeInitializationData
)};let id=${JSON.stringify(defaultThemeId)};try{const stored=window.localStorage.getItem(${JSON.stringify(
  productThemeStorageKey
)});if(stored&&Object.prototype.hasOwnProperty.call(themes,stored))id=stored}catch{}const theme=themes[id];const root=document.documentElement;root.dataset.productTheme=id;root.dataset.productAppearance=theme.appearance;for(const [name,value] of Object.entries(theme.variables))root.style.setProperty(name,value)})();`;

export const metadata: Metadata = {
  title: {
    default: "智能金融資料分析",
    template: "%s｜智能金融資料分析"
  },
  description:
    "上傳 CSV、Excel 或 JSON，理解資料結構、比較合適模型、查看金融指標，並產出程式碼與報告。",
  applicationName: "智能金融資料分析"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-Hant"
      className="light"
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <body>
        <script
          id={productThemeScriptId}
          suppressHydrationWarning
          dangerouslySetInnerHTML={{
            __html: productThemeInitializationScript
          }}
        />
        <LocaleProvider locale="zh-Hant">
          <FeedbackProvider>
            <ThemeProvider>
              <WorkspaceProvider>{children}</WorkspaceProvider>
            </ThemeProvider>
          </FeedbackProvider>
        </LocaleProvider>
      </body>
    </html>
  );
}
