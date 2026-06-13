import Link from "next/link";
import { Upload } from "lucide-react";
import { AmbientCanvas, RouteStage } from "@/components/MotionPrimitives";
import { Button } from "@/components/ui/button";

type AppShellProps = {
  active: "home" | "upload";
  children: React.ReactNode;
};

const navItems = [
  { href: "/", label: "首頁", key: "home" },
  { href: "/upload", label: "上傳資料", key: "upload" }
] as const;

export function AppShell({ active, children }: AppShellProps) {
  return (
    <div className="app-frame min-h-screen bg-canvas">
      <AmbientCanvas />
      <header className="app-header sticky top-0 z-40 border-b border-border/70 bg-background/82">
        <div className="app-header-inner mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/" className="brand-link flex min-w-0 items-center gap-3">
            <div className="brand-mark">
              智
            </div>
            <div className="min-w-0">
              <div className="app-brand-title truncate font-semibold tracking-normal text-ink">
                智能金融資料分析
              </div>
            </div>
          </Link>
          <nav className="app-nav hidden items-center gap-1 rounded-[var(--radius-control)] border border-border/75 bg-background/80 p-1 md:flex">
            {navItems.map((item) => {
              const isActive = active === item.key;
              return (
                <Link
                  key={item.key}
                  href={item.href}
                  className={`rounded-[calc(var(--radius-control)-2px)] px-5 py-2.5 text-sm font-semibold transition-[color,background-color,box-shadow,transform] duration-[var(--motion-fast)] ease-[var(--ease-out)] ${
                    isActive
                      ? "bg-accent text-accent-foreground shadow-[inset_0_-1px_0_rgb(var(--color-primary)/0.48)]"
                      : "text-muted-foreground hover:bg-secondary/72 hover:text-foreground"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="flex items-center gap-3">
            <Button asChild variant="outline" size="sm" className="sm:hidden">
              <Link href="/upload">
                <Upload aria-hidden="true" />
                上傳
              </Link>
            </Button>
          </div>
        </div>
      </header>
      <main className="app-main mx-auto max-w-[1600px] px-4 py-7 sm:px-6 lg:px-8">
        <RouteStage>{children}</RouteStage>
      </main>
    </div>
  );
}
