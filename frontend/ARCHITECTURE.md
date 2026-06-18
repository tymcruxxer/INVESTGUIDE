# Frontend Architecture Documentation

## Overview

InvestGuide Frontend is a modern, scalable Next.js 15+ application built with premium fintech UI design principles. The architecture follows a modular, feature-based approach with clear separation of concerns.

## Folder Structure Explanation

### `/app`
- **Purpose**: Next.js App Router pages and routes
- **Structure**: Follows Next.js 13+ conventions with route groups
- **Key Routes**:
  - `/dashboard` - Main analytics dashboard
  - `/markets` - Market exploration and filtering
  - `/assets/[ticker]` - Asset detail pages
  - `/ai-assistant` - Conversational AI interface
  - `/education` - Educational content hub
  - `/settings` - User preferences and profile

### `/components`
- **Purpose**: Reusable React components
- **Subfolders**:
  - `/layout` - Layout components (Sidebar, Navbar, AppShell)
  - `/ui` - Base UI components (to be populated with shadcn/ui)
  - `/common` - Shared components across features
  
### `/features`
- **Purpose**: Feature-specific business logic and components
- **Structure**: One folder per feature with internal components and logic
- **Features** (to be created):
  - `/dashboard` - Dashboard-specific components
  - `/markets` - Market exploration features
  - `/stocks` - Stock-specific functionality
  - `/vfex` - VFEX-specific functionality
  - `/reits` - REIT-specific functionality
  - `/ai-assistant` - AI chat components
  - `/sentiment` - Sentiment analysis features
  - `/macroeconomics` - Macro dashboard features

### `/hooks`
- **Purpose**: Custom React hooks for common patterns
- **Examples**:
  - `useLocalStorage` - Persist state to localStorage
  - `useWindowSize` - Track window dimensions
  - `useIsMobile` - Mobile detection
  - `useDebounce` - Debounced values
  - `useAsync` - Async operations with loading state

### `/services`
- **Purpose**: API client and backend communication
- **Key Files**:
  - `api.ts` - Axios client with interceptors and service methods
  - Future: `auth.ts`, `assets.ts`, `market.ts`, etc.

### `/store`
- **Purpose**: Zustand state management stores
- **Current Stores**:
  - `useAuthStore` - Authentication state and actions
  - `useThemeStore` - Theme management (dark/light mode)
  - `useUIStore` - UI state (sidebar, mobile menu)

### `/types`
- **Purpose**: TypeScript type definitions
- **Organized By**:
  - API response types
  - Asset and market types
  - Sentiment and analytics types
  - User and authentication types
  - UI component prop types

### `/utils`
- **Purpose**: Helper functions and utilities
- **Categories**:
  - `cn()` - Tailwind class merging
  - `format*()` - Data formatting functions
  - `debounce()` / `throttle()` - Function utilities
  - Color helpers - Sentiment and risk colors

### `/styles`
- **Purpose**: Global CSS and Tailwind configuration
- **Files**:
  - `globals.css` - Global styles, theme variables, component classes

### `/providers`
- **Purpose**: React context providers
- **Providers**:
  - `ThemeProvider` - Dark/light mode management
  - `ReactQueryProvider` - TanStack Query configuration
  - `index.tsx` - Combined provider component

## Architecture Decisions

### State Management
- **Zustand**: Lightweight state management for auth, theme, and UI
- **TanStack Query**: Server state management and caching
- **Local Storage**: Persistent client-side state via custom hook

### Styling
- **TailwindCSS**: Utility-first CSS with dark mode support
- **CSS Variables**: Theme colors as CSS variables for flexibility
- **Component Classes**: Reusable Tailwind patterns as @layer components

### Routing
- **App Router**: Next.js 13+ App Router with nested routes
- **Route Groups**: Organized by feature (dashboard, markets, assets)
- **Dynamic Routes**: `[ticker]` for asset detail pages

### Component Organization
- **Layout Components**: AppShell, Sidebar, Navbar (container-level)
- **Feature Components**: Domain-specific components in `/features`
- **UI Components**: Reusable UI elements (to be populated from shadcn/ui)
- **Common Components**: Shared across multiple features

### API Communication
- **Axios Client**: Centralized HTTP client with interceptors
- **Service Methods**: Organized by domain (assets, news, macro, etc.)
- **Error Handling**: Centralized error handling with type safety
- **Auth Tokens**: Automatic token injection and refresh

### Performance
- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js Image component
- **Turbopack**: Enabled in development for faster builds
- **Query Caching**: TanStack Query with 5-minute stale time

### Dark Mode
- **System Default**: Dark mode is the default
- **Toggle**: User can switch to light mode
- **Persistence**: Theme preference saved to localStorage
- **CSS Variables**: Dynamic theme switching without page reload

## File Naming Conventions

- **Components**: PascalCase (e.g., `Dashboard.tsx`, `AssetCard.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useLocalStorage.ts`)
- **Types**: PascalCase (e.g., `Asset.ts`, `ApiResponse.ts`)
- **Utils**: camelCase (e.g., `formatCurrency.ts`, `cn.ts`)
- **Folders**: kebab-case (e.g., `/ai-assistant`, `/asset-detail`)

## Development Workflow

### Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Adding Features
1. Create feature folder in `/features`
2. Create specific components in feature folder
3. Export components from feature index
4. Create hooks if needed in `/hooks`
5. Add types to `/types` if needed
6. Update routes in `/app`

### Adding Components
1. Create in `/components` if reusable across features
2. Create in feature folder if feature-specific
3. Use shadcn/ui as base for UI components
4. Apply Tailwind classes for styling

### API Integration
1. Define types in `/types`
2. Add service methods in `/services/api.ts`
3. Use `useQuery` or `useMutation` from TanStack Query
4. Handle loading and error states

## Best Practices

1. **Type Safety**: Always use TypeScript types for props and state
2. **Component Reusability**: Extract shared logic into custom hooks
3. **Error Boundaries**: Wrap major sections with ErrorBoundary
4. **Loading States**: Show Skeleton components during data fetching
5. **Mobile Responsive**: Use Tailwind breakpoints (mobile-first)
6. **Accessibility**: Use semantic HTML and ARIA attributes
7. **Performance**: Lazy load heavy components when appropriate
8. **Error Handling**: Comprehensive try-catch and API error handling

## Technologies

- **Next.js 15+** - React framework with SSR and optimization
- **TypeScript** - Type-safe JavaScript development
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality Radix-based components
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state and caching
- **Framer Motion** - Smooth animations
- **Recharts** - React charting library
- **Lucide Icons** - Beautiful icon library
- **Axios** - HTTP client
- **Zod** - Schema validation (future)

## Next Steps

1. Install dependencies: `npm install`
2. Add shadcn/ui components as needed
3. Implement specific feature pages
4. Connect to backend API
5. Add comprehensive error handling
6. Implement authentication flows
7. Add unit and E2E tests
