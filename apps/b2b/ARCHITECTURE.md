# Frontend Architecture Guide

## 🏗️ Clean Architecture + Design System

This frontend follows Clean Architecture principles with Ports & Adapters pattern, combined with a robust Design System built on shadcn/ui.

## 📁 Directory Structure

```
apps/web/
├── app/                      # Next.js App Router
│   ├── (marketing)/         # Public pages route group
│   └── (app)/              # Authenticated pages route group
│
├── core/                    # Business logic (Clean Architecture)
│   ├── entities/           # Domain entities
│   ├── ports/             # Interface definitions (contracts)
│   ├── usecases/          # Business rules orchestration
│   └── adapters/          # External service implementations
│
├── components/             # UI Components
│   ├── ui/               # Design System wrappers (public API)
│   ├── blocks/           # Composed components (Navbar, Footer, etc)
│   └── internal/         # Internal implementations
│       └── shadcn/       # Raw shadcn components (don't use directly)
│
├── lib/                    # Utilities and helpers
│   └── design-system/     # Design tokens and theme
│
└── tests/                  # Test files
```

## 🎯 Architecture Rules

### 1. Dependency Flow
```
UI Components → Use Cases → Ports ← Adapters
```

### 2. Import Restrictions

#### ❌ FORBIDDEN
- UI → Adapters (components should never import adapters)
- Use Cases → Adapters (use dependency injection)
- Use Cases → UI (business logic independent of UI)
- Ports → Anything (except entities)

#### ✅ ALLOWED
- UI → Use Cases → Ports
- Adapters → Ports (implements interfaces)
- Everyone → Entities

### 3. Component Guidelines

#### Always use wrappers
```tsx
// ❌ BAD - Direct import from shadcn
import { Button } from "@/components/internal/shadcn/button"

// ✅ GOOD - Use Design System wrapper
import { Button } from "@/components/ui/Button"
```

#### Compose complex components in blocks
```tsx
// components/blocks/Navbar.tsx
import { Button } from "@/components/ui/Button"
import { useLoginUseCase } from "@/core/usecases/auth/login"

export function Navbar() {
  const login = useLoginUseCase()
  // Component logic using use cases
}
```

## 🎨 Design System

### Design Tokens
All design decisions are centralized in `/lib/design-system/tokens.ts`:
- Colors (brand, semantic, neutral)
- Typography (fonts, sizes, weights)
- Spacing scale
- Border radius
- Shadows
- Transitions
- Z-index layers

### CSS Variables
Dark theme is the default. CSS variables are defined in `globals.css`:
```css
--primary: 158 64% 52%;     /* Brand green */
--background: 222 47% 8%;   /* Dark background */
--foreground: 0 0% 91%;     /* Light text */
--radius: 1rem;             /* Default border radius */
```

### Component Variants
Components support multiple variants for flexibility:
```tsx
<Button variant="brand" size="lg" rounded="xl">
  Click me
</Button>

<Card variant="glass" padding="lg" interactive>
  Content
</Card>
```

## 🔄 Migration Strategy

### Phase 1: Foundation ✅
- [x] Install shadcn/ui
- [x] Create Design System tokens
- [x] Setup component wrappers
- [x] Configure architecture folders
- [x] Add ESLint rules

### Phase 2: Core Components (Next)
- [ ] Migrate Navbar to shadcn
- [ ] Migrate Auth Modal
- [ ] Update forms with react-hook-form + zod

### Phase 3: Marketing Pages
- [ ] Hero with new components
- [ ] Features grid
- [ ] Pricing cards
- [ ] FAQ accordion

### Phase 4: App Shell
- [ ] Sidebar navigation
- [ ] Data tables
- [ ] Upload components

### Phase 5: Cleanup
- [ ] Remove old components
- [ ] Update all imports
- [ ] Document patterns

## 🧪 Testing Strategy

### Unit Tests
- Test wrappers render correctly
- Test use cases business logic
- Test adapters integration

### E2E Tests
- Test user flows
- Test authentication
- Test form submissions

### Visual Tests
- Storybook for component documentation
- Visual regression with Chromatic (optional)

## 📝 Code Examples

### Creating a Use Case
```typescript
// core/usecases/product/create-product.usecase.ts
export class CreateProductUseCase {
  constructor(private productPort: IProductPort) {}
  
  async execute(input: CreateProductInput): Promise<Product> {
    // Business logic here
    return this.productPort.create(input)
  }
}
```

### Using in a Component
```tsx
// components/blocks/ProductForm.tsx
import { useCreateProduct } from "@/core/usecases/product/create-product"
import { Button } from "@/components/ui/Button"

export function ProductForm() {
  const createProduct = useCreateProduct()
  
  const handleSubmit = async (data) => {
    await createProduct.execute(data)
  }
  
  return <form>...</form>
}
```

### Creating an Adapter
```typescript
// core/adapters/api/product.adapter.ts
import { IProductPort } from "@/core/ports/product.port"

export class ProductAPIAdapter implements IProductPort {
  async create(data: CreateProductInput): Promise<Product> {
    const response = await fetch("/api/products", {
      method: "POST",
      body: JSON.stringify(data)
    })
    return response.json()
  }
}
```

## 🚀 Best Practices

1. **Always use TypeScript** - No `any` types
2. **Prefer composition** - Small, focused components
3. **Use Design Tokens** - No hardcoded values
4. **Test business logic** - Use cases should be 100% tested
5. **Document complex logic** - Add JSDoc comments
6. **Keep components pure** - Side effects in use cases
7. **Use semantic HTML** - Accessibility first
8. **Optimize imports** - Use barrel exports wisely

## 📚 Resources

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Ports & Adapters](https://alistair.cockburn.us/hexagonal-architecture/)
- [Design System Best Practices](https://www.designsystems.com)

## 🆘 Help

For questions or issues:
1. Check this documentation
2. Look for examples in the codebase
3. Ask in the team channel
4. Create an issue with the `architecture` label