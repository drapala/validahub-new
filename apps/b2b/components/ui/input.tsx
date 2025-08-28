/**
 * Input Component Wrapper
 * Extends shadcn/ui input with our Design System tokens
 */

import * as React from "react"
import { cn } from "@/lib/utils"
import { Input as ShadcnInput } from "@/components/internal/shadcn/input"
import { cva, type VariantProps } from "class-variance-authority"

const inputVariants = cva(
  "flex w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
  {
    variants: {
      variant: {
        default: "",
        ghost: "border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0",
        filled: "bg-muted border-muted",
        error: "border-destructive focus-visible:ring-destructive",
        success: "border-success-500 focus-visible:ring-success-500",
      },
      size: {
        sm: "h-9 px-2 py-1 text-xs",
        md: "h-10 px-3 py-2 text-sm",
        lg: "h-11 px-4 py-2",
        xl: "h-12 px-4 py-3 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">,
    VariantProps<typeof inputVariants> {
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
  error?: boolean
  success?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    type, 
    variant,
    size,
    icon,
    iconPosition = "left",
    error,
    success,
    ...props 
  }, ref) => {
    const inputVariant = error ? "error" : success ? "success" : variant
    
    if (icon) {
      return (
        <div className="relative">
          {icon && iconPosition === "left" && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {icon}
            </div>
          )}
          <ShadcnInput
            type={type}
            className={cn(
              inputVariants({ variant: inputVariant, size, className }),
              iconPosition === "left" && "pl-10",
              iconPosition === "right" && "pr-10"
            )}
            ref={ref}
            {...props}
          />
          {icon && iconPosition === "right" && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {icon}
            </div>
          )}
        </div>
      )
    }
    
    return (
      <ShadcnInput
        type={type}
        className={cn(inputVariants({ variant: inputVariant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input, inputVariants }