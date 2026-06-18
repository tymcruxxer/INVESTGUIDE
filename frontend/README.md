# InvestGuide Frontend

AI-powered Zimbabwean investment intelligence platform frontend built with Next.js 15, TypeScript, TailwindCSS, and modern fintech UI design.

## Quick Start

### Install Dependencies
```bash
npm install
```

### Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local` and set your backend API URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Landing page
│   ├── dashboard/         # Dashboard page
│   ├── markets/           # Markets explorer
│   ├── assets/[ticker]/   # Asset detail page
│   ├── ai-assistant/      # AI chat interface
│   ├── education/         # Education hub
│   └── settings/          # User settings
├── components/            # Reusable components
│   ├── layout/           # AppShell, Sidebar, Navbar
│   ├── error-boundary.tsx # Error handling
│   └── skeleton.tsx       # Loading skeletons
├── features/             # Feature-specific modules
├── hooks/                # Custom React hooks
├── services/             # API client layer
├── store/                # Zustand state stores
├── types/                # TypeScript definitions
├── utils/                # Helper functions
├── styles/               # Global CSS and theme
└── providers/            # React providers
```

## Technology Stack

- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript 5+
- **Styling**: TailwindCSS 3+ with dark mode
- **UI Components**: shadcn/ui (Radix-based)
- **State Management**: Zustand (auth, theme, UI)
- **Server State**: TanStack Query v5
- **Forms**: React Hook Form
- **Validation**: Zod
- **Animation**: Framer Motion
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Charts**: Recharts
- **Build Tool**: Turbopack (Next.js 15)

## Key Features

### ✨ Architecture
- **Modular Design**: Clean separation of concerns
- **Type Safe**: Strict TypeScript throughout
- **Scalable**: Feature-based folder structure
- **Maintainable**: Clear naming conventions and patterns

### 🎨 Dark Mode First
- Premium fintech UI design
- Smooth theme transitions
- System preference detection
- Persistent theme selection

### 📱 Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1600px
- Touch-friendly navigation
- Adaptive layouts

### ⚡ Performance
- Code splitting with App Router
- Turbopack in development
- Image optimization
- Query caching strategies

### 🛡️ Robustness
- Error boundaries
- Loading states with skeletons
- Comprehensive error handling
- Type-safe API communication

## Available Scripts

```bash
# Development
npm run dev              # Start dev server with Turbopack

# Production
npm run build            # Build for production
npm start               # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run type-check      # TypeScript validation
npm run format          # Format with Prettier
npm run format:check    # Check formatting
```

## Design System

### Colors (Dark Mode)
- **Primary**: Electric blue (#3B82F6)
- **Background**: Deep black (#050816)
- **Card**: Charcoal (#111827)
- **Border**: Slate (#1F2937)
- **Positive**: Emerald green (#10B981)
- **Negative**: Soft red (#EF4444)

### Components
- Reusable layout components (Sidebar, Navbar, AppShell)
- Loading skeletons for better UX
- Error boundary for error handling
- Smooth animations with Framer Motion

### Utilities
- `cn()` - Safe Tailwind class merging
- `format*()` - Data formatting helpers
- `getSentiment*()` - Sentiment color/label helpers
- `getRiskLevel*()` - Risk level styling

## State Management

### Zustand Stores
- **useAuthStore** - Authentication and user state
- **useThemeStore** - Dark/light mode management
- **useUIStore** - Sidebar and mobile menu state

### TanStack Query
- Server state caching
- Automatic refetching
- Background sync
- Optimistic updates

## API Integration

The frontend communicates with the backend via a centralized API service layer:

```tsx
import { assetService } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

const { data, isLoading } = useQuery({
  queryKey: ["assets"],
  queryFn: () => assetService.getAssets({ limit: 10 }),
});
```

### API Services
- `assetService` - Asset operations
- `newsService` - News feed operations
- `macroService` - Macroeconomic data
- `watchlistService` - Watchlist operations
- `aiService` - AI assistant operations

## Component Patterns

### Page Component
```tsx
"use client";

import { AppShell } from "@/components/layout";
import { motion } from "framer-motion";

export default function Page() {
  return (
    <AppShell>
      <motion.div>
        {/* Page content */}
      </motion.div>
    </AppShell>
  );
}
```

### Data Fetching
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ["key"],
  queryFn: () => apiService.getData(),
});
```

### State Management
```tsx
const { user, logout } = useAuthStore();
const { theme, toggleTheme } = useThemeStore();
```

## Deployment

### Vercel (Recommended)
```bash
vercel --prod
```

### Docker
```bash
docker build -t investguide-frontend .
docker run -p 3000:3000 investguide-frontend
```

### Environment Variables for Production
```env
NEXT_PUBLIC_API_URL=https://api.investguide.co.zw/api/v1
NEXT_PUBLIC_APP_URL=https://investguide.co.zw
```

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed architecture and folder structure
- **[SETUP.md](./SETUP.md)** - Installation and development guide

## Next Steps

1. ✅ Frontend foundation setup
2. ⏳ Connect to backend API
3. ⏳ Implement authentication flows
4. ⏳ Add shadcn/ui components
5. ⏳ Build feature-specific pages
6. ⏳ Implement error handling
7. ⏳ Add unit tests
8. ⏳ Optimize performance

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

Follow the coding patterns established in existing components:
- Use TypeScript strictly
- Follow the folder structure
- Keep components modular
- Document complex logic
- Use Tailwind utilities
- Implement responsive design

## License

© 2024 InvestGuide. All rights reserved.

---

**InvestGuide** - AI-powered investment intelligence for Zimbabwe 🇿🇼
