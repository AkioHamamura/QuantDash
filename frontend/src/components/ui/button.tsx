import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_3px_0_rgba(0,0,0,0.1),0_1px_2px_0_rgba(0,0,0,0.06)] hover:scale-105 hover:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.2),0_4px_8px_0_rgba(0,0,0,0.15),0_2px_4px_0_rgba(0,0,0,0.1)] transform transition-all",
        destructive:
          "bg-destructive text-destructive-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_3px_0_rgba(0,0,0,0.1)] hover:bg-destructive/90 hover:scale-105 transform transition-all",
        outline:
          "border-2 border-primary bg-background/80 backdrop-blur-sm text-primary shadow-[0_1px_3px_0_rgba(0,0,0,0.1)] hover:bg-primary hover:text-primary-foreground hover:scale-105 transform transition-all",
        secondary:
          "bg-secondary text-secondary-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_3px_0_rgba(0,0,0,0.1)] hover:bg-secondary/80 hover:scale-105 transform transition-all",
        ghost: "hover:bg-primary/10 hover:text-primary hover:scale-105 transform transition-all",
        link: "text-primary underline-offset-4 hover:underline",
        gradient: "bg-primary text-primary-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.2),0_4px_8px_0_rgba(0,0,0,0.15),0_2px_4px_0_rgba(0,0,0,0.1)] hover:scale-105 hover:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.3),0_6px_12px_0_rgba(0,0,0,0.2)] transform transition-all duration-300",
        success: "bg-primary text-primary-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_3px_0_rgba(0,0,0,0.1)] hover:scale-105 hover:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.2),0_4px_8px_0_rgba(0,0,0,0.15)] transform transition-all",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
