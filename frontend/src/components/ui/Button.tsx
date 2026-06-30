import { forwardRef, type ButtonHTMLAttributes } from "react";

import { buttonClassName, type ButtonVariant } from "./buttonStyles";

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant }
>(function Button({ className = "", variant = "primary", ...props }, ref) {
  return (
    <button
      className={buttonClassName(variant, className)}
      ref={ref}
      {...props}
    />
  );
});
