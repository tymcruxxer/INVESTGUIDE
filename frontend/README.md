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
â”œâ”€â”€ app/                    # Next.js App Router pages
â”‚   â”œâ”€â”€ layout.tsx         # Root layout with providers
â”‚   â”œâ”€â”€ page.tsx           # Landing page
â”‚   â”œâ”€â”€ dashboard/         # Dashboard page
â”‚   â”œâ”€â”€ markets/           # Markets explorer
â”‚   â”œâ”€â”€ assets/[ticker]/   # Asset detail page
â”‚   â”œâ”€â”€ ai-assistant/      # AI chat interface
â”‚   â”œâ”€â”€ education/         # Education hub
â”‚   â””â”€â”€ settings/          # User settings
â”œâ”€â”€ components/            # Reusable components
â”‚   â”œâ”€â”€ layout/           # AppShell, Sidebar, Navbar
â”‚   â”œâ”€â”€ error-boundary.tsx # Error handling
â”‚   â””â”€â”€ skeleton.tsx       # Loading skeletons
â”œâ”€â”€ features/             # Feature-specific modules
â”œâ”€â”€ hooks/                # Custom React hooks
â”œâ”€â”€ services/             # API client layer
â”œâ”€â”€ store/                # Zustand state stores
â”œâ”€â”€ types/                # TypeScript definitions
â”œâ”€â”€ utils/                # Helper functions
â”œâ”€â”€ styles/               # Global CSS and theme
â””â”€â”€ providers/            # React providers
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

### âœ¨ Architecture
- **Modular Design**: Clean separation of concerns
- **Type Safe**: Strict TypeScript throughout
- **Scalable**: Feature-based folder structure
- **Maintainable**: Clear naming conventions and patterns

### ðŸŽ¨ Dark Mode First
- Premium fintech UI design
- Smooth theme transitions
- System preference detection
- Persistent theme selection

### ðŸ“± Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1600px
- Touch-friendly navigation
- Adaptive layouts

### âš¡ Performance
- Code splitting with App Router
- Turbopack in development
- Image optimization
- Query caching strategies

### ðŸ›¡ï¸ Robustness
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

The frontend now communicates with the backend via a centralized API service layer for assets, news, and investor profile data:

```tsx
import { assetService } from "@/services/api";
import { useQuery } from "@tanstack/react-query";

const { data, isLoading } = useQuery({
  queryKey: ["assets"],
  queryFn: () => assetService.getAssets({ limit: 10 }),
});
```

The asset detail page now also consumes the `/assets/{ticker}/assessment` endpoint through `assetService.getAssetAssessment(ticker)`, and renders a reusable `AssetAssessmentPanel` component on the asset detail page.

### API Services
- `assetService` - Asset list and detail operations
- `newsService` - News feed and asset-linked news operations
- `investorProfileService` - Investor profile retrieval and update
- `macroService` - Macroeconomic data
- `watchlistService` - Watchlist operations
- `aiService` - AI assistant operations

### Backend-connected pages
- Dashboard uses backend assets, news, and investor profile state where available.
- Asset explorer uses backend assets with search, exchange, type, and sector filters.
- Asset detail uses backend asset details plus linked news.
- Comparison uses the backend asset catalog as its selectable source.

### Fallback strategy
If the backend is unavailable, the UI displays an explicit message and falls back to demo content for preview only.

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

1. âœ… Frontend foundation setup
2. â³ Connect to backend API
3. â³ Implement authentication flows
4. â³ Add shadcn/ui components
5. â³ Build feature-specific pages
6. â³ Implement error handling
7. â³ Add unit tests
8. â³ Optimize performance

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

Â© 2024 InvestGuide. All rights reserved.

---

**InvestGuide** - AI-powered investment intelligence for Zimbabwe ðŸ‡¿ðŸ‡¼

## Sprint 022 Auth and Onboarding Flow

Sprint 022 adds the first user-facing authentication and personalization flow.

Implemented frontend routes:

* `/auth/login` - email/password login with loading and error states
* `/auth/signup` - email/password signup with confirm-password validation
* `/onboarding` - seven-step investor personalization flow for experience level, investment goals, preferred asset types, risk appetite, investment horizon, planned investment range, and language preference

Auth state lives in `store/index.ts` and persists the current access token in localStorage for development. On app load, `AuthSessionProvider` hydrates the session and calls `/api/v1/auth/me` when a token exists.

API support lives in `services/api.ts`:

* `authService.login`
* `authService.signup`
* `authService.me`
* `investorProfileService.getProfile`
* `investorProfileService.createProfile`
* `investorProfileService.updateProfile`

Route protection is client-side for now. Existing private pages use `AppShell`, which redirects unauthenticated users to `/auth/login` and authenticated users without a completed investor profile to `/onboarding`.

Set the backend URL with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Known limitation: full end-to-end signup/login/profile persistence still requires the backend PostgreSQL blocker to be resolved. The frontend compiles against the backend contract, but live persistence depends on a reachable migrated database.

## Sprint 023 Frontend Integration Validation

Sprint 023 validated the frontend against the locally running backend URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Route smoke results from the Next.js dev server on port `3000`:

* `/auth/signup`: 200
* `/auth/login`: 200
* `/onboarding`: 200
* `/dashboard`: 200

Validation commands:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

Known limitation: browser-level signup/login/onboarding persistence could not be completed because the backend database remains unavailable with the configured local PostgreSQL credentials. The frontend routes and build are healthy; persistence depends on resolving the Docker/PostgreSQL blocker.

## Sprint 024 Frontend Runtime Validation

Sprint 024 revalidated frontend route availability with the backend URL set to:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Route smoke results from the Next.js dev server on port `3000`:

* `/auth/signup`: 200
* `/auth/login`: 200
* `/onboarding`: 200
* `/dashboard`: 200

Validation commands:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

Persisted browser validation remains pending because backend signup/login/profile writes are blocked by the local Docker/PostgreSQL environment.

## Sprint 028 Backend-Connected Asset & News Data

Sprint 028 connects the frontend showcase pages to the existing backend data APIs while keeping explicit demo fallback for unavailable local backend/database states.

Connected APIs:

* `GET /api/v1/assets`
* `GET /api/v1/assets/{ticker}`
* `GET /api/v1/news`
* `GET /api/v1/news/{id}` through the service layer
* `GET /api/v1/investor-profile`

Updated pages:

* Dashboard uses backend investor profile, assets, and news when available.
* Asset Explorer at `/assets` and Markets at `/markets` use backend assets with search, exchange, asset type, and sector filters.
* Asset detail pages use backend asset detail plus related news through the news API.
* Compare uses the backend asset catalog for selecting two assets.

Fallback strategy:

* Demo content is used only when backend data is unavailable or empty.
* The UI displays: `Backend unavailable. Showing demo data for preview only.`
* Demo content should not be treated as live market data.

## Sprint 031 Company Intelligence Frontend

Sprint 031 adds the first Company Intelligence page while preserving the existing frontend design system.

Frontend page:

* `/company/[ticker]` - company overview page with profile, quick facts, related investments, latest news, deterministic assessment summary, educational context, and quick actions.

API service additions:

* `companyService.getCompanies()` uses `GET /api/v1/companies`.
* `companyService.getCompanyByTicker(ticker)` uses `GET /api/v1/companies/{ticker}`.
* `companyService.getCompanyAssessment(ticker)` uses `GET /api/v1/companies/{ticker}/assessment`.

Search routing:

* The top navigation search now recognizes Company, Asset, and News result types.
* Searches such as `delta`, `reit`, and `treasury` offer relevant routes.

Company page sections:

* Overview.
* Company profile.
* Related investments.
* Latest news.
* Quick facts.
* Assessment.
* Quick actions: View Assets, Compare, Latest News, Assessment, Financial Statements Coming Soon, and Watchlist Coming Soon.

Fallback remains explicit. If backend company data is unavailable, demo company data is used for preview only. No AI, predictions, recommendations, portfolio features, watchlists, live prices, financial statements, dividends, scrapers, or auth changes were added.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.

## Sprint 032 Company Intelligence Enrichment Frontend

Sprint 032 extends `/company/[ticker]` with a Company Intelligence section backed by the new company profile endpoint.

Frontend additions:

* `companyService.getCompanyProfile(ticker)` calls `GET /api/v1/companies/{ticker}/profile`.
* Company profile types were added to `types/index.ts`.
* Company profile mappers normalize backend profile and verification payloads.
* Development demo profile data is clearly labeled as fixture data.

The Company Intelligence section displays:

* Business Summary
* Primary Business
* Products & Services
* Industry
* Headquarters
* Founded
* Website
* Research Status badge
* Last Verified
* Source name and source URL

Research status badge values:

* Development
* Verified
* Needs Review
* Unavailable

Source transparency is always shown where data exists. If the backend is unavailable, fixture-backed profile data may be displayed for preview only. No AI, predictions, recommendations, portfolio, watchlists, live APIs, live scraping, financial statements, dividends, competitors, ESG, ratings, or auth changes were added.

## Sprint 033 Backend-First Company Profile Loading

Sprint 033 updates `/company/[ticker]` to prefer persisted backend company profile data whenever it exists.

Company profile loading order:

1. Use `GET /api/v1/companies/{ticker}/profile`.
2. If the returned profile has a persisted backend id, render it as `Persisted Backend`.
3. If no persisted profile is available, use clearly labeled development preview fixture data when available.
4. If backend/profile data is unavailable and no preview exists, show a clean unavailable message.

The Company Intelligence section now displays:

* Research Status
* Source
* Last Verified
* Data Origin

Data Origin values:

* `Persisted Backend` - profile row exists in the backend database.
* `Development Preview` - fixture-backed preview data is being shown and should not be treated as live research.
* `Unavailable` - neither backend nor preview profile data is available.

The page also handles missing profiles, backend unavailability, and database unavailability with user-facing messages rather than stack traces. No AI, recommendations, portfolio, watchlist, live API, live scraping, financial statement, dividend, ESG, rating, or authentication changes were added.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed and generated 14 routes including `/company/[ticker]`.

## Sprint 033.1 Local Runtime Validation

Sprint 033.1 validated the frontend against the fixed local backend runtime.

Use this local API URL when running the frontend against the Docker PostgreSQL-backed backend on port `8001`:

```powershell
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8001/api/v1'
npm.cmd run dev
```

Validated frontend routes returned HTTP 200 from the Next.js dev server:

* `/auth/signup`
* `/auth/login`
* `/onboarding`
* `/dashboard`
* `/assets`
* `/company/delta`
* `/compare`

Frontend validation also passed:

* `npm.cmd run lint`
* `npm.cmd run type-check`
* `npm.cmd run build`
---

## Authentication Runtime Stabilization

Local frontend authentication now defaults to `http://127.0.0.1:8001/api/v1` when `NEXT_PUBLIC_API_URL` is not provided. Signup calls `POST /auth/signup`, login calls `POST /auth/login`, and transport failures display a clear backend-unreachable message pointing operators to `http://127.0.0.1:8001`.

For manual testing on Windows PowerShell:

```powershell
$env:NEXT_PUBLIC_API_URL="http://127.0.0.1:8001/api/v1"
npm.cmd run dev
```

The public landing page routes Get Started actions to `/auth/signup` and Login actions to `/auth/login`.
## Sprint 036 Real Backend Data Integration

Sprint 036 tightened the manual demo path so frontend pages prefer persisted backend data and clearly label preview fallback content.

Local API URL for manual testing:

```powershell
$env:NEXT_PUBLIC_API_URL="http://127.0.0.1:8001/api/v1"
npm.cmd run dev
```

Backend-first behavior:

* Dashboard uses backend investor profile, assets, and news where available.
* Asset Explorer and Markets use `GET /api/v1/assets` before falling back to preview assets.
* Asset detail uses `GET /api/v1/assets/{ticker}`, `GET /api/v1/assets/{ticker}/assessment`, and backend news data.
* Company pages use `GET /api/v1/companies/{ticker}`, `GET /api/v1/companies/{ticker}/profile`, and `GET /api/v1/companies/{ticker}/assessment`.
* Compare uses the backend asset catalog before falling back to preview assets.

Fallback strategy:

* Fallback content is shown only when the backend request fails or the backend is unavailable.
* Fallback copy now says: `Backend unavailable. Showing development preview data.`
* Company profile source transparency continues to show `Persisted Backend`, `Development Preview`, or `Unavailable`.

Ticker routing:

* The persisted Delta ticker is `DLTA`.
* Frontend route helpers map `/company/delta` and `/assets/delta` to backend ticker `DLTA` for manual demos.
* Search results route Delta asset/company results through the canonical ticker helper.

Sprint 036 route smoke from the Next.js dev server on `http://localhost:3000` returned HTTP 200 for:

* `/auth/signup`
* `/auth/login`
* `/onboarding`
* `/dashboard`
* `/assets`
* `/assets/delta`
* `/company/delta`
* `/compare`
* `/markets`

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed.