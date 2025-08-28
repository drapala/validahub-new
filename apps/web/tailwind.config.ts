import type { Config } from "tailwindcss";

// Import tokens safely
const tokens = require('./lib/design-system/tokens').tokens || {};

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "./core/**/*.{ts,tsx}",
    "../../packages/**/*.{ts,tsx}",
    "./node_modules/@radix-ui/**/*.{js,ts,tsx}",
  ],
  safelist: [
    // Dynamic color classes
    { pattern: /(bg|text|border)-(zinc|gray|neutral|green|emerald|purple|red|blue|yellow)-(50|100|200|300|400|500|600|700|800|900|950)/ },
    // Dynamic opacity/transform classes
    { pattern: /(opacity|translate|scale|rotate)-(0|5|10|20|25|30|40|50|60|70|75|80|90|95|100)/ },
    // Dark mode variants
    { pattern: /dark:(bg|text|border)-(zinc|gray|neutral|green|emerald|purple)-(50|100|200|300|400|500|600|700|800|900|950)/ },
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Brand colors
        brand: tokens.colors.brand,
        
        // Neutral colors
        neutral: tokens.colors.neutral,
        
        // Semantic colors
        info: tokens.colors.info,
        danger: tokens.colors.danger,
        warning: tokens.colors.warning,
        success: tokens.colors.success,
        
        // Base colors (CSS variables for theming)
        background: {
          DEFAULT: "hsl(var(--background))",
          secondary: tokens.colors.background.secondary,
          tertiary: tokens.colors.background.tertiary,
          muted: tokens.colors.background.muted,
        },
        foreground: {
          DEFAULT: "hsl(var(--foreground))",
          muted: tokens.colors.foreground.muted,
          subtle: tokens.colors.foreground.subtle,
        },
        
        // Component colors
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        
        // Utility colors
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        
        // Legacy colors (for backward compatibility)
        gray: tokens.colors.neutral,
        green: tokens.colors.brand,
        blue: tokens.colors.info,
        red: tokens.colors.danger,
        yellow: tokens.colors.warning,
      },
      
      fontFamily: tokens.typography.fontFamily,
      fontSize: tokens.typography.fontSize,
      fontWeight: tokens.typography.fontWeight,
      lineHeight: tokens.typography.lineHeight,
      letterSpacing: tokens.typography.letterSpacing,
      
      spacing: tokens.spacing,
      
      borderRadius: {
        ...tokens.borderRadius,
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      
      boxShadow: {
        ...tokens.shadows,
      },
      
      transitionDuration: tokens.transitions.duration,
      transitionTimingFunction: tokens.transitions.easing,
      
      zIndex: tokens.zIndex,
      
      screens: tokens.breakpoints,
      
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "fade-out": {
          from: { opacity: "1" },
          to: { opacity: "0" },
        },
        "slide-in": {
          from: { transform: "translateY(100%)" },
          to: { transform: "translateY(0)" },
        },
        "slide-out": {
          from: { transform: "translateY(0)" },
          to: { transform: "translateY(100%)" },
        },
        "zoom-in": {
          from: { transform: "scale(0.95)", opacity: "0" },
          to: { transform: "scale(1)", opacity: "1" },
        },
        "zoom-out": {
          from: { transform: "scale(1)", opacity: "1" },
          to: { transform: "scale(0.95)", opacity: "0" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "fade-out": "fade-out 0.2s ease-out",
        "slide-in": "slide-in 0.3s ease-out",
        "slide-out": "slide-out 0.3s ease-out",
        "zoom-in": "zoom-in 0.2s ease-out",
        "zoom-out": "zoom-out 0.2s ease-out",
        shimmer: "shimmer 2s linear infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;