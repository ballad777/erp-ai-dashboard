import { AppShell } from "@/components/AppShell";
import { UploadPanel } from "@/components/UploadPanel";

export default function UploadPage() {
  return (
    <AppShell active="upload">
      <UploadPanel />
    </AppShell>
  );
}
