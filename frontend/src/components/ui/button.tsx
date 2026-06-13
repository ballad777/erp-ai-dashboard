import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-control)] text-sm font-semibold tracking-normal outline-none transition-[color,background-color,border-color,box-shadow,transform,opacity] duration-[var(--motion-fast)] ease-[var(--ease-out)] focus-visible:ring-[3px] focus-visible:ring-ring/25 disabled:pointer-events-none disabled:opacity-50 motion-reduce:transition-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default:
          "border border-primary/90 bg-primary text-primary-foreground shadow-[var(--shadow-action)] hover:bg-primary/92 hover:shadow-[var(--shadow-action-hover)] active:translate-y-px",
        premium:
          "border border-primary/80 bg-[linear-gradient(135deg,rgb(var(--color-primary)),rgb(var(--color-primary-deep)))] text-primary-foreground shadow-[var(--shadow-action)] hover:shadow-[var(--shadow-action-hover)] active:translate-y-px",
        destructive:
          "border border-destructive/20 bg-destructive text-white shadow-sm hover:bg-destructive/90 active:translate-y-px",
        outline:
          "border border-border bg-background/90 text-foreground shadow-[var(--shadow-control)] hover:border-primary/28 hover:bg-accent hover:text-accent-foreground active:translate-y-px",
        secondary:
          "border border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/75 active:translate-y-px",
        ghost:
          "border border-transparent text-muted-foreground hover:bg-accent hover:text-accent-foreground active:translate-y-px",
        link: "text-primary underline-offset-4 hover:underline"
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 gap-1.5 px-3",
        lg: "h-12 rounded-[calc(var(--radius-control)+2px)] px-5 text-[15px]",
        icon: "size-10",
        "icon-sm": "size-9"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
