import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-full border px-2.5 py-1 text-xs font-semibold tracking-normal transition-[color,background-color,border-color,box-shadow] duration-[var(--motion-fast)] ease-[var(--ease-out)] focus-visible:ring-[3px] focus-visible:ring-ring/25 [&_svg]:pointer-events-none [&_svg]:size-3",
  {
    variants: {
      variant: {
        default: "border-primary/16 bg-primary/8 text-primary",
        secondary: "border-border bg-secondary text-secondary-foreground",
        outline: "border-border bg-background/72 text-muted-foreground",
        success: "border-emerald-600/16 bg-emerald-50 text-emerald-700",
        warning: "border-amber-600/18 bg-amber-50 text-amber-800",
        destructive: "border-destructive/16 bg-destructive/8 text-destructive"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return (
    <span
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Badge, badgeVariants };
