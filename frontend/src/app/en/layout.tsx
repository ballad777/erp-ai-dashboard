import type { Metadata } from "next";
import { LocaleProvider } from "@/components/LocaleProvider";

export const metadata: Metadata = {
  title: {
    default: "Intelligent Financial Data Analysis",
    template: "%s | Intelligent Financial Data Analysis"
  },
  description:
    "Understand CSV, Excel, and JSON data, compare suitable models, inspect financial signals, and generate reproducible code and reports."
};

export default function EnglishLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <LocaleProvider locale="en">{children}</LocaleProvider>;
}
