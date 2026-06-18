# InvestGuide Frontend - Quick Start Guide

## Installation & Launch (5 minutes)

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

**What happens**:
- Downloads and installs all 35+ packages (including React, Next.js, TailwindCSS, Zustand, TanStack Query)
- Resolves peer dependencies automatically
- Creates `node_modules/` folder (~500MB)
- Generates `package-lock.json` for reproducible installs

**Expected output** (end of installation):
```
added 500+ packages, and audited 600+ packages in 3m45s
```

**Ignore these messages** (they are normal):
- Peer dependency warnings for React-related packages
- ESLint configuration notices

### Step 3: Start Development Server
```bash
npm run dev
```

**Expected output**:
```
  ▲ Next.js 14.2.5
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 2.3s
```

### Step 4: Open in Browser
Navigate to: **http://localhost:3000**

You should see the InvestGuide landing page with:
- Dark theme (default)
- Responsive navbar and sidebar
- Feature cards and call-to-action buttons
- Smooth animations

---

## Verification Checklist

After launching, verify these work:

✅ **Page loads without errors** (check browser console for any red errors)  
✅ **Dark mode active by default** (page has dark background)  
✅ **Navigation items clickable** (Dashboard, Markets, AI Assistant, etc.)  
✅ **Responsive design** (resize browser - layout adapts)  
✅ **No TypeScript errors** (terminal shows "✓ Ready")  
✅ **No missing import warnings** (terminal shows clean build)  

---

## Available Commands

```bash
# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Start production server (after build)
npm start

# Check TypeScript types
npm run type-check

# Lint code for issues
npm run lint

# Format code with Prettier
npm run format

# Check formatting without changes
npm run format:check
```

---

## Useful Endpoints

| Page | URL | Purpose |
|------|-----|---------|
| **Landing** | http://localhost:3000 | Homepage with features |
| **Dashboard** | http://localhost:3000/dashboard | Main dashboard overview |
| **Markets** | http://localhost:3000/markets | Market explorer |
| **Assets** | http://localhost:3000/assets/[ticker] | Asset detail page |
| **AI Assistant** | http://localhost:3000/ai-assistant | AI chat interface |
| **Education** | http://localhost:3000/education | Learning resources |
| **Settings** | http://localhost:3000/settings | User preferences |

---

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Landing page
│   ├── layout.tsx         # Root layout with providers
│   ├── dashboard/         # Dashboard pages
│   ├── markets/           # Markets pages
│   └── ...
├── components/            # Reusable React components
│   ├── layout/           # Layout components (Sidebar, Navbar)
│   ├── ui/               # Basic UI components
│   └── shared/           # Shared components
├── features/             # Feature-specific component groups
├── hooks/                # Custom React hooks (18)
├── providers/            # React providers (Theme, Query)
├── services/             # API client (Axios)
├── store/                # Global state (Zustand)
├── types/                # TypeScript type definitions
├── utils/                # Utility functions
└── styles/               # Global CSS and themes
```

---

## Technology Stack

**Core Framework**:
- **Next.js** 14.2.5 - React framework with App Router
- **React** 18.3.1 - UI library
- **TypeScript** 5.3.3 - Type safety

**Styling**:
- **TailwindCSS** 3.4.1 - Utility-first CSS
- **Framer Motion** 10.16.16 - Animations
- **Lucide React** 0.318.0 - Icon library

**State Management**:
- **Zustand** 4.4.7 - Global state (auth, theme, UI)
- **TanStack Query** 5.28.0 - Server state (API cache)

**Forms & Validation**:
- **React Hook Form** 7.50.0 - Form handling
- **Zod** 3.22.4 - Schema validation

**UI Components**:
- **Radix UI** - Accessible component primitives
- **shadcn/ui** - Pre-built component collection

**API**:
- **Axios** 1.7.7 - HTTP client with interceptors

---

## Key Features

✅ **Dark Mode First** - Default dark theme with CSS variables  
✅ **Responsive Design** - Works on mobile, tablet, desktop  
✅ **Type Safety** - Full TypeScript coverage with strict mode  
✅ **State Management** - Zustand for local, TanStack Query for server  
✅ **API Integration** - Axios with JWT interceptors and error handling  
✅ **Dark Mode Persistence** - Saves preference to localStorage  
✅ **Smooth Animations** - Framer Motion throughout UI  
✅ **Accessible Components** - Radix UI primitives ensure a11y  
✅ **Development Experience** - Hot reload, fast type checking  

---

## Environment Configuration

Create `.env.local` in the `frontend/` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_TIMEOUT=30000

# Optional: Feature flags
NEXT_PUBLIC_ENABLE_AI_FEATURES=true
NEXT_PUBLIC_ENABLE_BETA=false
```

---

## Development Workflow

### Making Changes

1. Edit any file in `app/`, `components/`, `hooks/`, etc.
2. Save the file
3. Browser automatically reloads (hot module replacement)
4. See changes instantly

### Creating New Pages

1. Create folder structure in `app/`: `app/new-page/page.tsx`
2. Add React component
3. It's automatically a route: `http://localhost:3000/new-page`

### Creating New Components

1. Add component to `components/` folder
2. Import and use in pages
3. Example: `components/MyComponent.tsx`

### Adding State

Use Zustand for:
- Global state (auth, user, theme)
- localStorage persistence
- Example in `store/authStore.ts`

### Fetching Data

Use TanStack Query for:
- API data fetching
- Automatic caching (5 min stale time)
- Background refetch
- Optimistic updates
- Example: `useQuery({ queryKey: ['assets'], queryFn: getAssets })`

---

## Troubleshooting

### "Cannot find module 'tailwindcss-animate'"
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### "Port 3000 already in use"
```bash
# Solution: Use different port
npm run dev -- -p 3001
```

### "TypeScript errors after changes"
```bash
# Solution: Rebuild project
npm run type-check
```

### "Styles not loading"
```bash
# Solution: Clear Next.js cache
rm -rf .next
npm run dev
```

### "Hot reload not working"
```bash
# Solution: Restart dev server
# Press Ctrl+C in terminal, then:
npm run dev
```

---

## Build & Deployment

### Production Build
```bash
npm run build
npm start
```

### Deployment Checklist
- ✅ All environment variables set in `.env.production`
- ✅ `npm run type-check` passes
- ✅ `npm run lint` passes
- ✅ `npm run build` completes successfully
- ✅ Test all pages in production build

---

## Next Steps

1. ✅ Installation complete
2. ✅ Dev server running
3. ⏳ **Connect to backend API** (set `NEXT_PUBLIC_API_URL`)
4. ⏳ **Implement login page** (see `store/authStore.ts`)
5. ⏳ **Add API integration** (see `services/api.ts`)
6. ⏳ **Build feature pages** (use components and hooks)
7. ⏳ **Deploy to production**

---

## Need Help?

- **Documentation**: See `docs/architecture/` folder
- **Component Examples**: Check `components/` and `features/` folders
- **Type Definitions**: See `types/index.ts`
- **API Examples**: See `services/api.ts`
- **Hooks Examples**: See `hooks/index.ts`

---

**Status**: ✅ Frontend Ready for Development

**Last Updated**: May 28, 2026  
**Version**: 1.0.0  
**Compatibility**: Node 18+, npm 9+
