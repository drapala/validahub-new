# Marketing Landing Page Documentation

## Overview
This document describes the structure, components, and guidelines for the ValidaHub marketing landing page and related pages.

## Page Structure

### Route Groups
```
app/
├── (marketing)/          # Public marketing pages
│   ├── layout.tsx       # Marketing layout with Navbar
│   ├── page.tsx         # Landing page
│   ├── pricing/         # Pricing page
│   ├── faq/            # FAQ page  
│   ├── privacy/        # Privacy policy
│   └── terms/          # Terms of service
└── (app)/              # Protected application routes
    ├── layout.tsx      # App layout
    ├── upload/         # File upload (protected)
    ├── jobs/          # Job history (protected)
    └── ...
```

## Landing Page Components

### Component Hierarchy
```
LandingPage
├── Navbar (persistent)
├── Hero
├── SocialProof
├── HowItWorks
├── Features
├── Pricing
├── FAQ
├── CTA
└── Footer
```

### 1. Hero Section
**Purpose**: Primary value proposition and conversion point

**Content**:
- Headline: Product value in one sentence
- Subheadline: Supporting details
- Primary CTA: "Começar agora" → Opens signup modal
- Secondary CTA: "Ver planos" → Scrolls to pricing

**Design**:
- Full viewport height
- Dark gradient background
- Green accent for CTAs
- Trust indicators below CTAs

### 2. Social Proof
**Purpose**: Build credibility with logos

**Content**:
- "Empresas que confiam" headline
- 6 placeholder company logos
- Grayscale with hover effect

### 3. How It Works
**Purpose**: Explain the process simply

**Structure**:
- 3 steps with icons
- Step numbers (01, 02, 03)
- Connected with visual line on desktop
- Each step: Icon + Title + Description

### 4. Features Grid
**Purpose**: Showcase capabilities

**Layout**:
- 6 main features in 3x2 grid
- Each with unique icon and color
- Hover effects for engagement
- Additional mini-features below

**Features**:
1. Regras por categoria (marketplace-specific)
2. Correções automáticas
3. Validações avançadas (enum, regex, etc.)
4. Engine YAML versionada
5. Job History com links
6. Webhooks & Connectors

### 5. Pricing Section
**Purpose**: Clear pricing options

**Tiers**:
1. **Starter** (Free)
   - 100 validations/month
   - Basic features
   - CTA: "Criar conta grátis"

2. **Pro** (R$ 199/month)
   - Unlimited validations
   - All features
   - Highlighted as "Mais popular"
   - CTA: "Assinar Pro"

3. **Enterprise** (Custom)
   - SSO, SLA, dedicated
   - CTA: "Falar com vendas"

**Features**:
- Monthly/Annual toggle (10% discount)
- Feature comparison with checks/crosses
- Clear CTAs per tier

### 6. FAQ Section
**Purpose**: Address common concerns

**Topics**:
- Validation process
- Data security
- Integration options
- Processing time
- Auto-corrections
- Plan differences

**Interaction**:
- Accordion pattern
- Smooth expand/collapse
- One open at a time (optional)

### 7. Final CTA
**Purpose**: Last conversion opportunity

**Content**:
- Compelling headline
- Brief value reminder
- Prominent action buttons
- Trust indicators

### 8. Footer
**Purpose**: Navigation and legal

**Sections**:
- Product links
- Company info
- Legal links
- Resources
- Social media icons

## Design System

### Colors
```scss
// Primary
$green-500: #10b981  // Primary actions
$green-400: #34d399  // Accents

// Neutral
$gray-900: #111827   // Backgrounds
$gray-800: #1f2937   // Cards
$gray-700: #374151   // Borders
$gray-400: #9ca3af   // Body text
$white: #ffffff      // Headlines
```

### Typography
```scss
// Headlines
h1: 4xl-7xl, bold, white
h2: 3xl-4xl, bold, white
h3: xl-2xl, semibold, white

// Body
p: base-lg, regular, gray-400

// CTAs
button: base-lg, semibold
```

### Spacing
```scss
// Sections
py-20 (80px) between sections
container max-w-6xl

// Components
p-8 for cards
gap-8 for grids
mb-16 for section headers
```

## Responsive Design

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Mobile Adaptations
- Stack columns vertically
- Hamburger menu for navigation
- Full-width CTAs
- Reduced font sizes
- Touch-friendly tap targets (min 44px)

## Authentication Integration

### Modal Trigger Points
1. Hero "Começar agora" button
2. Navbar "Cadastrar" button
3. Pricing tier CTAs (when not authenticated)
4. Final CTA section

### Auth Modal Features
- Google OAuth (primary)
- Email/password (secondary)
- Tab switching for method
- Mode toggle (signin/signup)
- Terms acceptance checkbox

## Performance Optimization

### Image Optimization
- Use Next.js Image component
- Lazy load below-fold images
- WebP format with fallbacks
- Responsive srcsets

### Code Splitting
- Dynamic imports for heavy components
- Separate bundles for marketing vs app
- Prefetch critical routes

### SEO
- Semantic HTML structure
- Meta tags per page
- Open Graph tags
- Structured data for pricing

## Accessibility

### Requirements
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators
- ARIA labels where needed

### Implementation
- Semantic HTML elements
- Proper heading hierarchy
- Alt text for images
- Focus trap in modals
- Skip navigation links

## Internationalization (Future)

### Prepared Structure
- Extract all strings to constants
- Date/number formatting helpers
- RTL layout support ready
- Language switcher space reserved

## Analytics Integration

### Events to Track
- CTA clicks (hero, pricing, final)
- Auth modal opens
- Signup/signin attempts
- Pricing toggle (monthly/annual)
- FAQ interactions
- Navigation clicks

### Implementation
```typescript
// Example event
gtag('event', 'click', {
  event_category: 'CTA',
  event_label: 'hero_start_now',
  value: 1
})
```

## Testing Guidelines

### E2E Tests
- Landing page sections visible
- Navigation works
- Auth modal flow
- Pricing interactions
- Responsive behavior

### Visual Regression
- Component screenshots
- Responsive layouts
- Dark mode consistency
- Hover states

## Content Management

### Update Frequency
- Pricing: Review monthly
- Features: Update with releases
- FAQ: Based on support tickets
- Social proof: Quarterly updates

### Copy Guidelines
- Clear value propositions
- Benefit-focused (not feature-focused)
- Consistent terminology
- Action-oriented CTAs
- Trust-building language

## Deployment Checklist

- [ ] All images optimized
- [ ] Meta tags updated
- [ ] Analytics configured
- [ ] Performance budget met (<3s FCP)
- [ ] Accessibility audit passed
- [ ] Mobile responsiveness verified
- [ ] Forms tested
- [ ] Legal pages linked
- [ ] SSL certificate active
- [ ] CDN configured