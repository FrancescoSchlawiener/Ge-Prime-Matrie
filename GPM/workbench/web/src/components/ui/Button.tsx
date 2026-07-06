import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "md" | "sm";
  children: ReactNode;
}

export function Button({ variant = "primary", size = "md", className = "", children, type = "button", ...rest }: ButtonProps) {
  const classes = [
    "gpm-btn",
    variant === "ghost" ? "gpm-btn--ghost" : "",
    variant === "secondary" ? "gpm-btn--secondary" : "",
    size === "sm" ? "gpm-btn--sm" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <button type={type} className={classes} {...rest}>
      {children}
    </button>
  );
}
