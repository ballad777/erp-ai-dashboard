import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import RootLayout from "@/app/layout";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app/data"
}));

describe("RootLayout", () => {
  it("keeps the product theme bootstrap script out of head-managed markup", () => {
    const html = renderToString(
      <RootLayout>
        <main>content</main>
      </RootLayout>
    );
    const headContent = html.match(/<head[^>]*>([\s\S]*?)<\/head>/)?.[1] ?? "";
    const bodyContent = html.match(/<body[^>]*>([\s\S]*?)<\/body>/)?.[1] ?? "";

    expect(headContent).not.toContain("finai-product-theme-init");
    expect(bodyContent).toContain("finai-product-theme-init");
  });
});
