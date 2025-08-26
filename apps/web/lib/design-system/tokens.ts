/**
 * Design System Tokens
 * Centralizes all design decisions for the ValidaHub application
 */

export const tokens = {
  // ============================================
  // COLORS
  // ============================================
  colors: {
    // Brand - Based on emerald green (#22C55E)
    brand: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981', // Primary
      600: '#059669',
      700: '#047857',
      800: '#065f46',
      900: '#064e3b',
      950: '#022c22',
      DEFAULT: '#10b981',
      foreground: '#ffffff',
    },

    // Neutral - Dark-first (zinc/graphite)
    neutral: {
      50: '#fafafa',
      100: '#f4f4f5',
      200: '#e4e4e7',
      300: '#d4d4d8',
      400: '#a1a1aa',
      500: '#71717a',
      600: '#52525b',
      700: '#3f3f46',
      800: '#27272a',
      900: '#18181b',
      950: '#09090b',
      DEFAULT: '#18181b',
      foreground: '#fafafa',
    },

    // Semantic colors
    info: {
      DEFAULT: '#3b82f6', // Blue
      foreground: '#ffffff',
      50: '#eff6ff',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
    },

    danger: {
      DEFAULT: '#ef4444', // Red
      foreground: '#ffffff',
      50: '#fef2f2',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
    },

    warning: {
      DEFAULT: '#f59e0b', // Amber
      foreground: '#000000',
      50: '#fffbeb',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
    },

    success: {
      DEFAULT: '#22c55e', // Green
      foreground: '#ffffff',
      50: '#f0fdf4',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
    },

    // Background & Foreground
    background: {
      DEFAULT: '#0b0f1a', // Dark background
      secondary: '#111827',
      tertiary: '#1f2937',
      muted: '#374151',
    },

    foreground: {
      DEFAULT: '#e5e7eb', // Light text
      muted: '#9ca3af',
      subtle: '#6b7280',
    },
  },

  // ============================================
  // TYPOGRAPHY
  // ============================================
  typography: {
    // Font families
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      mono: ['JetBrains Mono', 'Consolas', 'monospace'],
    },

    // Font sizes
    fontSize: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      base: '1rem', // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem', // 20px
      '2xl': '1.5rem', // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem', // 48px
      '6xl': '3.75rem', // 60px
      '7xl': '4.5rem', // 72px
    },

    // Font weights
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },

    // Line heights
    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '1.75',
    },

    // Letter spacing
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },

  // ============================================
  // SPACING
  // ============================================
  spacing: {
    0: '0',
    1: '0.25rem', // 4px
    2: '0.5rem', // 8px
    3: '0.75rem', // 12px
    4: '1rem', // 16px
    5: '1.25rem', // 20px
    6: '1.5rem', // 24px
    7: '1.75rem', // 28px
    8: '2rem', // 32px
    9: '2.25rem', // 36px
    10: '2.5rem', // 40px
    12: '3rem', // 48px
    14: '3.5rem', // 56px
    16: '4rem', // 64px
    20: '5rem', // 80px
    24: '6rem', // 96px
    28: '7rem', // 112px
    32: '8rem', // 128px
  },

  // ============================================
  // BORDER RADIUS
  // ============================================
  borderRadius: {
    none: '0',
    sm: '0.25rem', // 4px
    DEFAULT: '0.5rem', // 8px
    md: '0.75rem', // 12px
    lg: '1rem', // 16px - Our default
    xl: '1.25rem', // 20px
    '2xl': '1.5rem', // 24px
    '3xl': '2rem', // 32px
    full: '9999px',
  },

  // ============================================
  // SHADOWS
  // ============================================
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    
    // Brand shadows
    'brand-sm': '0 2px 8px -2px rgb(16 185 129 / 0.2)',
    'brand-md': '0 4px 16px -4px rgb(16 185 129 / 0.3)',
    'brand-lg': '0 8px 24px -6px rgb(16 185 129 / 0.4)',
  },

  // ============================================
  // TRANSITIONS
  // ============================================
  transitions: {
    duration: {
      75: '75ms',
      100: '100ms',
      150: '150ms',
      200: '200ms',
      300: '300ms',
      500: '500ms',
      700: '700ms',
      1000: '1000ms',
      DEFAULT: '200ms',
    },
    
    easing: {
      linear: 'linear',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },

  // ============================================
  // Z-INDEX
  // ============================================
  zIndex: {
    0: '0',
    10: '10',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    dropdown: '1000',
    sticky: '1020',
    fixed: '1030',
    modalBackdrop: '1040',
    modal: '1050',
    popover: '1060',
    tooltip: '1070',
    toast: '1080',
    max: '9999',
  },

  // ============================================
  // BREAKPOINTS
  // ============================================
  breakpoints: {
    xs: '475px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
}

// Export individual token groups for convenience
export const { colors, typography, spacing, borderRadius, shadows, transitions, zIndex, breakpoints } = tokens

// CSS Variables for runtime theming
export const cssVariables = {
  light: {
    // Base colors
    '--background': '0 0% 100%',
    '--foreground': '240 10% 3.9%',
    
    // Card
    '--card': '0 0% 100%',
    '--card-foreground': '240 10% 3.9%',
    
    // Popover
    '--popover': '0 0% 100%',
    '--popover-foreground': '240 10% 3.9%',
    
    // Primary (Brand)
    '--primary': '158 64% 52%',
    '--primary-foreground': '0 0% 100%',
    
    // Secondary
    '--secondary': '240 4.8% 95.9%',
    '--secondary-foreground': '240 5.9% 10%',
    
    // Muted
    '--muted': '240 4.8% 95.9%',
    '--muted-foreground': '240 3.8% 46.1%',
    
    // Accent
    '--accent': '240 4.8% 95.9%',
    '--accent-foreground': '240 5.9% 10%',
    
    // Destructive
    '--destructive': '0 84.2% 60.2%',
    '--destructive-foreground': '0 0% 100%',
    
    // Border
    '--border': '240 5.9% 90%',
    '--input': '240 5.9% 90%',
    '--ring': '158 64% 52%',
    
    // Border radius
    '--radius': '1rem',
  },
  
  dark: {
    // Base colors
    '--background': '222 47% 8%', // #0b0f1a
    '--foreground': '0 0% 91%', // #e5e7eb
    
    // Card
    '--card': '220 26% 10%', // Slightly lighter than bg
    '--card-foreground': '0 0% 91%',
    
    // Popover
    '--popover': '220 26% 10%',
    '--popover-foreground': '0 0% 91%',
    
    // Primary (Brand)
    '--primary': '158 64% 52%', // #10b981
    '--primary-foreground': '0 0% 100%',
    
    // Secondary
    '--secondary': '217 19% 17%', // #1f2937
    '--secondary-foreground': '0 0% 91%',
    
    // Muted
    '--muted': '215 19% 23%', // #374151
    '--muted-foreground': '0 0% 64%', // #9ca3af
    
    // Accent
    '--accent': '158 64% 52%',
    '--accent-foreground': '0 0% 100%',
    
    // Destructive
    '--destructive': '0 72% 51%', // #ef4444
    '--destructive-foreground': '0 0% 100%',
    
    // Border
    '--border': '217 19% 27%', // #374151
    '--input': '217 19% 27%',
    '--ring': '158 64% 52%',
    
    // Border radius
    '--radius': '1rem',
  },
}

// Type exports
export type ColorToken = keyof typeof tokens.colors
export type SpacingToken = keyof typeof tokens.spacing
export type BorderRadiusToken = keyof typeof tokens.borderRadius
export type ShadowToken = keyof typeof tokens.shadows
export type FontSizeToken = keyof typeof tokens.typography.fontSize
export type FontWeightToken = keyof typeof tokens.typography.fontWeight