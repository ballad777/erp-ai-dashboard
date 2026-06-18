import Link from "next/link";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageHeader } from "@/components/PagePrimitives";
import { Button } from "@/components/ui/button";

describe("PageHeader", () => {
  it("keeps mixed actions unless the caller explicitly suppresses them", () => {
    render(
      <PageHeader
        title="資料摘要"
        description="檢視目前資料。"
        actions={
          <>
            <Button asChild>
              <Link href="/app/data">加入資料</Link>
            </Button>
            <button type="button">匯出摘要</button>
          </>
        }
      />
    );

    expect(screen.getByRole("link", { name: "加入資料" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "匯出摘要" })
    ).toBeInTheDocument();
  });

  it("hides actions only when the caller explicitly requests suppression", () => {
    render(
      <PageHeader
        title="資料摘要"
        description="檢視目前資料。"
        suppressActions
        actions={<button type="button">匯出摘要</button>}
      />
    );

    expect(
      screen.queryByRole("button", { name: "匯出摘要" })
    ).not.toBeInTheDocument();
  });
});
