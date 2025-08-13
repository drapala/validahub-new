import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(240 10% 7%)",
        foreground: "hsl(0 0% 98%)",
        border: "#27272a", // zinc-800
        card: {
          DEFAULT: "hsl(240 10% 9%)",
          foreground: "hsl(0 0% 98%)"
        },
        muted: {
          DEFAULT: "hsl(240 5% 15%)",
          foreground: "hsl(240 5% 64%)"
        },
        primary: {
          DEFAULT: "hsl(142 71% 45%)", // emerald-500
          foreground: "hsl(146 70% 10%)"
        },
        ring: "hsl(142 71% 45%)"
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem"
      },
      boxShadow: {
        subtle: "0 6px 30px -12px rgba(0,0,0,0.35)"
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;