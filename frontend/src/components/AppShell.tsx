import Link from "next/link";
import { CommandCenter, CommandTriggerButton } from "@/components/CommandCenter";
import { SystemStatus } from "@/components/SystemStatus";

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
    <div className="min-h-screen bg-canvas">
      <header className="sticky top-0 z-40 border-b border-blue-100/80 bg-white/76 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex min-w-0 items-center gap-3">
            <div className="brand-mark">
              智
            </div>
            <div className="min-w-0">
              <div className="truncate text-lg font-semibold tracking-normal text-ink sm:text-xl">
                智能金融資料分析
              </div>
            </div>
          </Link>
          <nav className="hidden items-center gap-2 rounded-2xl border border-blue-100 bg-white/66 p-1 shadow-[0_14px_34px_rgba(15,23,42,0.05)] backdrop-blur-xl md:flex">
            {navItems.map((item) => {
              const isActive = active === item.key;
              return (
                <Link
                  key={item.key}
                  href={item.href}
                  className={`rounded-xl px-5 py-2.5 text-base font-semibold transition ${
                    isActive
                      ? "bg-cyan-50 text-brand shadow-[inset_0_-2px_0_rgba(20,184,166,0.85)]"
                      : "text-slate-600 hover:bg-slate-50 hover:text-ink"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="flex items-center gap-3">
            <div className="hidden lg:block">
              <SystemStatus />
            </div>
            <CommandTriggerButton />
            <Link
              href="/upload"
              className="inline-flex h-11 items-center rounded-xl border border-sky-200 bg-white/78 px-4 text-sm font-semibold text-brand shadow-[0_12px_28px_rgba(15,23,42,0.05)] sm:hidden"
            >
              上傳
            </Link>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1600px] px-4 py-7 sm:px-6 lg:px-8">{children}</main>
      <CommandCenter />
    </div>
  );
}
