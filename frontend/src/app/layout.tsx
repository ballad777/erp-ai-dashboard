import type { Metadata } from "next";
import { WorkspaceProvider } from "@/components/WorkspaceProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "智能金融資料分析",
  description: "智慧金融與資料分析平台"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant" data-scroll-behavior="smooth">
      <body>
        <WorkspaceProvider>{children}</WorkspaceProvider>
      </body>
    </html>
  );
}
