export const themeTokens = {
  dark: {
    // Base colors
    background: {
      primary: 'rgb(15, 15, 15)',      // #0F0F0F - Quase preto
      secondary: 'rgb(24, 24, 27)',     // #18181B - Cinza muito escuro
      tertiary: 'rgb(39, 39, 42)',      // #27272A - Cinza escuro
      card: 'rgba(24, 24, 27, 0.8)',    // Card com transparência
    },
    
    // Text colors (WCAG AA compliant)
    text: {
      primary: 'rgb(244, 244, 245)',    // #F4F4F5 - Branco suave
      secondary: 'rgb(161, 161, 170)',  // #A1A1AA - Cinza claro
      muted: 'rgb(113, 113, 122)',      // #71717A - Cinza médio
    },
    
    // Brand colors
    accent: {
      primary: 'rgb(16, 185, 129)',     // #10B981 - Verde esmeralda
      secondary: 'rgb(20, 184, 166)',   // #14B8A6 - Teal
      glow: 'rgba(16, 185, 129, 0.4)',  // Glow verde
    },
    
    // UI elements
    border: 'rgba(63, 63, 70, 0.4)',    // Border sutil
    navbar: {
      bg: 'rgba(15, 15, 15, 0.7)',      // Navbar com blur
      blur: '20px',
    },
  },
  
  light: {
    // Base colors
    background: {
      primary: 'rgb(255, 255, 255)',    // #FFFFFF - Branco puro
      secondary: 'rgb(249, 250, 251)',  // #F9FAFB - Cinza muito claro
      tertiary: 'rgb(243, 244, 246)',   // #F3F4F6 - Cinza claro
      card: 'rgba(255, 255, 255, 0.9)', // Card branco
    },
    
    // Text colors (WCAG AA compliant)
    text: {
      primary: 'rgb(17, 24, 39)',       // #111827 - Quase preto (ratio 14.5:1)
      secondary: 'rgb(75, 85, 99)',     // #4B5563 - Cinza escuro (ratio 7.5:1)
      muted: 'rgb(107, 114, 128)',      // #6B7280 - Cinza médio (ratio 5.3:1)
    },
    
    // Brand colors
    accent: {
      primary: 'rgb(124, 58, 237)',     // #7C3AED - Roxo vibrante
      secondary: 'rgb(139, 92, 246)',   // #8B5CF6 - Roxo claro
      glow: 'rgba(124, 58, 237, 0.2)',  // Glow roxo suave
    },
    
    // UI elements  
    border: 'rgba(229, 231, 235, 0.6)', // Border muito sutil
    navbar: {
      bg: 'rgba(255, 255, 255, 0.8)',   // Navbar branca com blur
      blur: '12px',
    },
  }
}

// Tailwind class helpers
export const getThemeClasses = (isDark: boolean) => ({
  // Backgrounds
  bgPrimary: isDark ? 'bg-zinc-950' : 'bg-white',
  bgSecondary: isDark ? 'bg-zinc-900' : 'bg-gray-50',
  bgTertiary: isDark ? 'bg-zinc-800' : 'bg-gray-100',
  bgCard: isDark ? 'bg-zinc-900/80' : 'bg-white/90',
  
  // Text
  textPrimary: isDark ? 'text-zinc-50' : 'text-gray-900',
  textSecondary: isDark ? 'text-zinc-400' : 'text-gray-600',
  textMuted: isDark ? 'text-zinc-500' : 'text-gray-500',
  
  // Accents
  accentPrimary: isDark ? 'text-emerald-400' : 'text-violet-600',
  accentBg: isDark ? 'bg-emerald-500/10' : 'bg-violet-500/10',
  accentBorder: isDark ? 'border-emerald-500/30' : 'border-violet-500/30',
  accentGlow: isDark ? 'shadow-emerald-500/20' : 'shadow-violet-500/20',
  
  // Borders
  border: isDark ? 'border-zinc-800' : 'border-gray-200',
  borderSubtle: isDark ? 'border-zinc-800/50' : 'border-gray-200/50',
})