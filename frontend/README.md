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
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ app/                    # Next.js App Router pages
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ layout.tsx         # Root layout with providers
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ page.tsx           # Landing page
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ dashboard/         # Dashboard page
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ markets/           # Markets explorer
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ assets/[ticker]/   # Asset detail page
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ ai-assistant/      # AI chat interface
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ education/         # Education hub
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ settings/          # User settings
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ components/            # Reusable components
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ layout/           # AppShell, Sidebar, Navbar
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ error-boundary.tsx # Error handling
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ skeleton.tsx       # Loading skeletons
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ features/             # Feature-specific modules
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ hooks/                # Custom React hooks
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ services/             # API client layer
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ store/                # Zustand state stores
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ types/                # TypeScript definitions
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ utils/                # Helper functions
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ styles/               # Global CSS and theme
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ providers/            # React providers
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

### ÃƒÂ¢Ã…â€œÃ‚Â¨ Architecture
- **Modular Design**: Clean separation of concerns
- **Type Safe**: Strict TypeScript throughout
- **Scalable**: Feature-based folder structure
- **Maintainable**: Clear naming conventions and patterns

### ÃƒÂ°Ã…Â¸Ã…Â½Ã‚Â¨ Dark Mode First
- Premium fintech UI design
- Smooth theme transitions
- System preference detection
- Persistent theme selection

### ÃƒÂ°Ã…Â¸Ã¢â‚¬Å“Ã‚Â± Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1600px
- Touch-friendly navigation
- Adaptive layouts

### ÃƒÂ¢Ã…Â¡Ã‚Â¡ Performance
- Code splitting with App Router
- Turbopack in development
- Image optimization
- Query caching strategies

### ÃƒÂ°Ã…Â¸Ã¢â‚¬ÂºÃ‚Â¡ÃƒÂ¯Ã‚Â¸Ã‚Â Robustness
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

1. ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ Frontend foundation setup
2. ÃƒÂ¢Ã‚ÂÃ‚Â³ Connect to backend API
3. ÃƒÂ¢Ã‚ÂÃ‚Â³ Implement authentication flows
4. ÃƒÂ¢Ã‚ÂÃ‚Â³ Add shadcn/ui components
5. ÃƒÂ¢Ã‚ÂÃ‚Â³ Build feature-specific pages
6. ÃƒÂ¢Ã‚ÂÃ‚Â³ Implement error handling
7. ÃƒÂ¢Ã‚ÂÃ‚Â³ Add unit tests
8. ÃƒÂ¢Ã‚ÂÃ‚Â³ Optimize performance

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

Ãƒâ€šÃ‚Â© 2024 InvestGuide. All rights reserved.

---

**InvestGuide** - AI-powered investment intelligence for Zimbabwe ÃƒÂ°Ã…Â¸Ã¢â‚¬Â¡Ã‚Â¿ÃƒÂ°Ã…Â¸Ã¢â‚¬Â¡Ã‚Â¼

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
* Asset detail uses `GET /api/v1/assets/{ticker}`, `GET /api/v1/assets/{ticker}/assessment`, `GET /api/v1/assets/{ticker}/research`, and backend news data.
* Company pages use `GET /api/v1/companies/{ticker}`, `GET /api/v1/companies/{ticker}/profile`, `GET /api/v1/companies/{ticker}/assessment`, and `GET /api/v1/companies/{ticker}/research`.
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
## Sprint 037 Product Polish and UX Audit

Sprint 037 focused on product polish, clarity, and QA without adding new modules or changing backend business logic.

UX improvements:

* Settings now shows a real account/profile review surface instead of fake skeleton fields and dead controls.
* Education now shows useful learning-path previews and honest curriculum-empty states instead of permanent loading skeletons.
* Dashboard news now shows an honest `No persisted news yet` empty state when the backend is reachable but has no articles.
* Sidebar navigation now includes clearer helper labels, active `aria-current` states, and closes predictably on mobile navigation.
* Global search now shows a helpful no-results state with a next action instead of silently disappearing.

Manual QA route checks returned HTTP 200 for:

* `/`
* `/auth/signup`
* `/auth/login`
* `/onboarding`
* `/dashboard`
* `/assets`
* `/assets/delta`
* `/company/delta`
* `/compare`
* `/markets`
* `/education`
* `/settings`

Validation:

* `python -m pytest -q`: passed, 228 tests.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
## Sprint 038 AI Research Frontend

Sprint 038 adds the first structured AI Research display surfaces without adding chat, LLM calls, predictions, recommendations, portfolios, watchlists, live prices, or new product modules.

Frontend additions:

* `assetService.getAssetResearch(ticker)` calls `GET /api/v1/assets/{ticker}/research`.
* `companyService.getCompanyResearch(ticker)` calls `GET /api/v1/companies/{ticker}/research`.
* `ResearchAssessment` TypeScript response types were added in `types/index.ts`.
* A reusable `ResearchPanel` renders opportunity, risk, evidence, education, Explain Like I am 18, suggested questions, and transparency metadata.
* `/assets/[ticker]` now displays an AI Research section after the existing deterministic assessment.
* `/company/[ticker]` now displays a Company AI Research section using backend company research data.

The panel is intentionally not a chatbot. It presents deterministic, structured, evidence-based research from backend data and states that it is educational analysis, not financial advice or prediction.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed and generated 14 routes.
* `python -m pytest -q`: passed from the repository root with 235 tests and 1 non-blocking pytest cache permission warning.
## Sprint 039 Research Experience Polish

Sprint 039 improves the user-facing AI Research experience without changing business logic or adding new AI capabilities.

Research UI improvements:

* Upgraded the reusable `ResearchPanel` into a more institutional research surface with stronger hierarchy and clearer sections.
* Added a top-line `What the evidence suggests` summary.
* Improved Opportunity display with score, current outlook, key drivers, and supporting evidence.
* Improved Risk display with semantic risk tone, risk contributors, watch items, and uncertainty reducers.
* Made Evidence Strength more prominent with data completeness, available data, missing data, and freshness details.
* Made Education visually distinct with `Learn before you invest` positioning.
* Reformatted Explain Like I am 18 as a friendly callout with Zimbabwe-context copy.
* Changed Suggested Questions into clickable chips that route to existing pages or anchors.
* Added dedicated `ResearchPanelSkeleton` and `ResearchUnavailable` states instead of generic loading/error cards.
* Improved hover and focus states for research cards and chips.

Runtime route smoke on `http://localhost:3000`:

* `/`: 200 after dev-server warmup.
* `/auth/signup`: 200.
* `/auth/login`: 200.
* `/onboarding`: 200.
* `/dashboard`: 200.
* `/assets`: 200.
* `/assets/delta`: 200.
* `/company/delta`: 200.
* `/compare`: 200.
* `/markets`: 200.
* `/education`: 200.
* `/settings`: 200.

Validation:

* `python -m pytest -q`: passed, 235 tests, 1 non-blocking pytest cache permission warning.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Full visual browser QA with screenshots across desktop, tablet, and mobile remains recommended; this session validated route/runtime health and server logs from the local environment.
## Sprint 040 Research Navigation

Sprint 040 adds relationship-aware research navigation to the frontend while preserving the existing design system and routes.

Frontend additions:

* `/compare` now consumes `GET /api/v1/compare` when backend assets are available and displays deterministic business, opportunity, risk, evidence, and Learn Next comparison sections.
* `/company/[ticker]` now consumes `GET /api/v1/companies/{ticker}/related` and displays Related Research, related companies, Learn Next topic chips, and relationship methodology.
* New TypeScript contracts were added for `ComparePayload`, `CompanyRelatedResearch`, `KnowledgeGraphPayload`, related companies, and Learn Next topics.
* Existing fallback behavior remains in place when the backend is unavailable.

UX rule:

* A research page should not end in a dead end. Company pages now guide users toward adjacent companies and educational concepts with visible relationship reasons.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed, 241 tests, 1 non-blocking pytest cache permission warning.

Known limitations:

* Relationship cards are deterministic and educational only.
* No AI chat, predictions, watchlists, portfolio optimization, alerts, or live scraping were added.

## Sprint 041 Premium Product Experience Polish

Sprint 041 refined the existing UI without adding product features or changing backend contracts.

UX and accessibility improvements:

* Global search now supports ArrowDown, ArrowUp, Enter, and Escape keyboard behavior.
* Search results use combobox/listbox semantics, active result highlighting, and `aria-selected` state.
* Search has a clear action while active and a stronger no-results state.
* Sidebar navigation now has a clearer active-page indicator and smoother mobile overlay transition.
* AppShell and public pages use a shared `page-shell` fade-in treatment.
* Shared `skeleton-card` and `interactive-card` utilities were added for more intentional loading and hover states.
* Buttons now have subtle press feedback, and reduced-motion users are respected through a global media query.

Runtime route smoke on `http://localhost:3000` returned HTTP 200 for:

* `/`
* `/auth/signup`
* `/auth/login`
* `/dashboard`
* `/assets`
* `/assets/delta`
* `/company/delta`
* `/compare`
* `/markets`
* `/education`
* `/settings`

Validation:

* `python -m pytest -q`: passed, 241 tests.
* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.

Known limitations:

* Full DevTools console inspection and screenshot-based browser QA across desktop, tablet, and mobile still requires an interactive browser pass.
* Edge headless DOM inspection has been unreliable in this shell in prior validation attempts, so server logs and HTTP smoke checks were used here.

## Sprint 042 News Intelligence Frontend

Sprint 042 adds a premium News Intelligence panel to the existing dashboard latest-news section.

Frontend additions:

* `newsService.getNewsResearch(id)` calls `GET /api/v1/news/{id}/research`.
* `NewsResearch` TypeScript contracts define event category, importance, evidence, related companies, learning topics, knowledge graph, and transparency fields.
* `features/news/news-intelligence-panel.tsx` renders a reusable panel with:
  * What happened?
  * Why it matters
  * Evidence
  * Related companies
  * Learn Next
  * Related concepts
  * Explain Like I am 18
  * Event category and importance badges

Dashboard behavior:

* When backend news exists, the dashboard fetches research for the latest article and displays the News Intelligence panel.
* When the backend is unavailable and development preview news is used, the research call is disabled.
* The panel presents deterministic education and relationship context only. It does not show predictions, buy/sell recommendations, personalized advice, alerts, or sentiment model output.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed from the repository root with 247 tests and 1 non-blocking pytest cache permission warning.

## Sprint 043 Company Deep Dive Frontend

Sprint 043 adds a Company Deep Dive surface to `/company/[ticker]` using the deterministic backend Business Intelligence endpoint.

Frontend additions:

* `companyService.getCompanyBusiness(ticker)` calls `GET /api/v1/companies/{ticker}/business`.
* `industryService.getIndustry(industry)` calls `GET /api/v1/industries/{industry}` for future industry explorer surfaces.
* `BusinessIntelligence`, `IndustryIntelligence`, `CompetitorMap`, and related TypeScript contracts were added.
* `features/company/business-deep-dive.tsx` renders a reusable deep-dive panel with:
  * Business overview
  * Business model
  * Revenue drivers
  * Industry intelligence
  * Competitive position
  * Operational risks
  * Competitors
  * Learn Next
  * Transparency

Company page behavior:

* `/company/[ticker]` now fetches Business Intelligence alongside profile, assessment, research, related companies, and news.
* If the backend business endpoint is unavailable, the page shows a clear unavailable state and preserves the existing company profile, assessment, related research, and news sections.
* All outputs are deterministic, educational, and non-advisory.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `python -m pytest -q`: passed from the repository root with 253 tests and 1 non-blocking pytest cache permission warning.

## Sprint 044 Financial Dashboard

Sprint 044 adds a Company Financial Dashboard to `/company/[ticker]`.

Frontend integration:

* `companyService.getCompanyFinancials(ticker)` calls `GET /api/v1/companies/{ticker}/financials`.
* `companyService.getCompanyFinancialHealth(ticker)` calls `GET /api/v1/companies/{ticker}/financial-health`.
* `frontend/types/index.ts` includes Financial Intelligence, ratio, trend, financial health, statement row, and endpoint payload contracts.
* `frontend/features/company/financial-dashboard.tsx` provides reusable financial components:
  * `FinancialHealthCard`
  * `FinancialRatioTable`
  * `RevenuePanel`
  * `ProfitabilityPanel`
  * `CashFlowPanel`
  * `BalanceSheetPanel`
  * `TrendChart`
  * `FinancialEducationPanel`

The dashboard displays financial health, revenue, profitability, cash flow, balance sheet intelligence, ratios, trend analysis, educational notes, ELI18 explanation, data sources, available periods, and missing data.

Transparency rules:

* Development financial fixtures are labelled through backend transparency metadata.
* Missing financial data is shown explicitly.
* The dashboard remains educational and does not show predictions, buy/sell recommendations, portfolio advice, alerts, or AI-generated advice.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* Backend validation: `python -m pytest -q` passed with 260 tests.

## Sprint 045 Financial Dashboard Runtime Notes

Sprint 045 validates the Company Financial Dashboard against PostgreSQL-backed financial rows and improves empty/error behavior.

Runtime behavior:

* `/company/delta` route-smoke returned HTTP 200 from the Next.js dev server.
* The frontend was started with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8010/api/v1` because local port `8001` was occupied by a stale listener during validation.
* The dashboard consumes `GET /api/v1/companies/{ticker}/financials` and respects backend transparency metadata.

Financial states:

* When financial statements exist, the complete dashboard renders.
* When no persisted statement rows exist, the page shows: `Financial statements are not available for this company yet.`
* When the backend is unavailable, the financial section shows: `Financial Intelligence is temporarily unavailable.`
* The UI does not inject Delta or other preview financial rows for unrelated companies.
* Development financial data is exposed through the backend `development_data` transparency flag and labelled in the dashboard.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* Backend validation: `python -m pytest -q` passed with 268 tests.

## Sprint 046 Dividend Intelligence UI

The company page now includes a Dividend Intelligence section on `/company/[ticker]`.

States:

* Verified backend dividend records: render persisted dividend history and source transparency.
* Development dividend records: render the dashboard with a clear `Development Preview` label.
* No dividend records: show an honest empty state explaining that missing platform data is not proof that no dividend was paid.
* Backend unavailable: show `Dividend Intelligence is temporarily unavailable` without injecting fallback dividend data into another company.

The UI displays dividend status, historical dividend rows, yield availability, payout ratio, cash payout ratio, growth, sustainability, things to watch, educational notes, ELI18 copy, source transparency, and suggested learning topics.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 14 routes generated.
* `/company/delta`: returned HTTP 200 against backend `http://127.0.0.1:8011/api/v1`.

## Sprint 047 Data Ingestion Contract Note

Sprint 047 adds a backend-only verified data pipeline framework. The frontend contract is unchanged: company, asset, news, financial, dividend, and intelligence screens continue to read from existing backend APIs.

The frontend should not branch on whether data came from JSON, CSV, ZSE, VFEX, annual reports, APIs, or manual curation. Source provenance and development-preview transparency should continue to come from backend payload metadata and existing UI transparency sections.

## Sprint 048 Frontend Data Contract Note

Sprint 048 completes additional backend ingestion coverage without changing frontend contracts. The frontend continues to read company, asset, news, financial, dividend, and intelligence data from existing backend APIs.

Frontend behavior remains source-agnostic:

* The UI does not branch on JSON, CSV, future ZSE/VFEX connectors, annual reports, APIs, or manual curation.
* Source transparency and development-preview labels continue to come from backend payload metadata.
* Market snapshot reference prices are consumed indirectly through existing intelligence endpoints, not through a new frontend-specific data path.

Route smoke validation:

* `/company/delta`: HTTP 200 from Next.js dev server.
* `/assets/delta`: HTTP 200 from Next.js dev server.
* `/compare`: HTTP 200 from Next.js dev server.
* `/dashboard`: HTTP 200 from Next.js dev server.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed after rerunning separately from `next build`; the first concurrent run hit a transient `.next/types` regeneration race.
* `npm.cmd run build`: passed, 14 routes generated.

## Sprint 049 Internal Data Operations UI

Sprint 049 adds internal operator pages that are not linked from public investor navigation:

* `/internal/data-operations`
* `/internal/data-operations/runs/[id]`

These pages consume development-guarded backend endpoints under `/api/v1/internal/...` and show pipeline health, recent runs, source health, entity quality, rejection filtering, run metadata, issue-code distribution, retry guidance, and safe issue details.

The frontend does not add public ingestion controls and does not expose write/import actions. The dashboard is intentionally practical and operations-focused rather than investor-facing.

Route smoke validation:

* `/internal/data-operations`: HTTP 200 on Next.js dev server port `3021`.
* `/internal/data-operations/runs/23`: HTTP 200 on Next.js dev server port `3021`.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 15 routes generated.

## Sprint 050 Macro Intelligence UI

Sprint 050 adds frontend Macro Intelligence surfaces powered by backend APIs, not hardcoded macro values.

Frontend additions:

* Dynamic macro pages at `/macro/[type]` for inflation, interest rates, exchange rates, GDP, and commodity prices.
* Company page Macro Factors panel on `/company/[ticker]` using `GET /api/v1/macro/company/{ticker}`.
* Frontend API client methods in `macroService` for overview, indicator, research, and company impact endpoints.
* TypeScript contracts for macro records, evidence, research payloads, related companies, and company macro impact.

The UI displays current value, provenance, Development Preview labels, evidence, affected sectors, affected companies, knowledge graph relationships, Learn Next topics, and the educational/not-advice boundary.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 15 routes generated including `/macro/[type]`.
* Route smoke on port `3022`: `/macro/inflation`, `/macro/gdp`, and `/company/delta` returned HTTP 200.

## Sprint 051 Sector and Industry Research UI

Sprint 051 adds frontend surfaces for deterministic Sector and Industry Intelligence while preserving existing business logic and backend contracts.

Frontend additions:

* Dynamic sector research pages at `/sector/[slug]`.
* Dynamic industry research pages at `/industry/[slug]`.
* Company page Sector Intelligence panel powered by `GET /api/v1/sectors/{slug}/research`.
* Macro pages now link affected sectors to their sector research pages.
* Frontend API client methods in `sectorService` and `industryService` for list, detail, and research endpoints.
* TypeScript contracts for sectors, industries, research payloads, related companies, knowledge graph nodes, Learn Next topics, and provenance metadata.

UI behavior:

* Sector and industry pages show overview, companies, macro relationships, risks, opportunities, knowledge graph relationships, Learn Next topics, and transparency notes.
* Development Preview data remains clearly labelled through backend provenance fields.
* The frontend remains source-agnostic and consumes backend APIs rather than hardcoded sector or industry facts.

Route smoke validation:

* `/company/delta`: HTTP 200 on Next.js dev server port `3023`.
* `/sector/consumer-staples`: HTTP 200 on Next.js dev server port `3023`.
* `/industry/beverages`: HTTP 200 on Next.js dev server port `3023`.
* `/macro/inflation`: HTTP 200 on Next.js dev server port `3023`.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 18 routes generated including `/sector/[slug]` and `/industry/[slug]`.

## Sprint 052 Financial Statement Intelligence UI

Sprint 052 adds a backend-connected Financial Statement Intelligence panel to the company page.

Frontend additions:

* `FinancialStatementIntelligencePanel` for `/company/[ticker]`.
* Frontend API client methods for:
  * `GET /companies/{ticker}/financial-statements`
  * `GET /companies/{ticker}/financial-intelligence`
* TypeScript contracts for statement intelligence sections, provenance, confidence, coverage, missing fields, and transparency.

UI behavior:

* Company pages now show revenue, profitability, liquidity, leverage, cash flow, and earnings quality sections when backend data is available.
* Each section displays explanation, evidence strength, source/provenance, ELI18 copy, and Learn Next topics.
* Missing or development data is presented transparently without fake scores or predictions.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 19 routes generated including `/company/[ticker]`.

## Sprint 052 Administration Shell

Sprint 052 adds a dedicated frontend administration shell without changing the investor experience.

Frontend additions:

* `/admin` redirects to `/admin/dashboard`.
* `/admin/dashboard` shows the administration operating-system foundation, permission snapshot, and future module placeholders.
* `/admin/settings` shows Owner protections, sensitive-action readiness, and the permission catalog.
* `AdminShell` provides separate navigation, loading state, unauthorized state, Admin Mode indicator, environment badge, current user/role display, and switch back to User View.
* The normal user sidebar shows `Admin Dashboard` only after the backend confirms the user has admin access.

Validation:

* `npm.cmd run lint`: passed.
* `npm.cmd run type-check`: passed.
* `npm.cmd run build`: passed, 22 routes generated including `/admin`, `/admin/dashboard`, and `/admin/settings`.

## Sprint 053: Admin User Management UI

The frontend administration shell now includes user and role management surfaces:

* `/admin/users` - searchable, filterable user directory.
* `/admin/users/[id]` - safe user detail, effective permissions, audit summary, role assignment/removal, and account suspend/restore actions.
* `/admin/roles` - read-only role catalog.
* `/admin/roles/[id]` - inherited permission inspection for one role.

The UI consumes backend admin APIs and does not expose password hashes, editable permissions, Owner transfer, MFA, billing, feature flags, or data-source controls. Permission editing remains intentionally deferred.

## Sprint 054: Data Source Registry Admin UI

The admin frontend now includes source-management pages:

* `/admin/sources` - searchable/filterable source registry, pagination, and source creation form.
* `/admin/sources/[id]` - source overview, connector configuration, masked credentials, provenance, operational settings, version history, and audited status/soft-delete controls.

The UI does not run ingestion, live scraping, scheduled jobs, feature flags, or AI provider management. Credential values are never displayed after creation.

## Pre-Sprint 055: Source Capabilities UI

The admin source registry now displays declared source capabilities on `/admin/sources` and `/admin/sources/[id]`. These labels are informational only; they do not trigger ingestion, scraping, scheduling, or live connector execution.

## Sprint 055: Ingestion Operations Centre UI

The admin frontend now includes ingestion operations pages:

* `/admin/ingestion/jobs` - job registry, summary widgets, filters, pagination, and job creation.
* `/admin/ingestion/jobs/[id]` - job overview, configuration, freshness, metrics, failures, execution history, and manual request buttons.
* `/admin/ingestion/executions` - immutable execution history with status, trigger, operator, metrics, and failures.

The UI is operator-facing only. Buttons record requests through backend APIs and do not start live ingestion, workers, queues, scrapers, or schedulers.

## Sprint 056: Connector Registry Admin UI

The admin frontend now includes connector-management pages:

* `/admin/connectors` - searchable/filterable connector registry, pagination, and connector creation form.
* `/admin/connectors/[id]` - connector overview, capabilities, configuration schema, authentication contract, validation history, compatible sources, version history, recent activity, and lifecycle controls.

The UI is operator-facing only. It defines future connector contracts and can request metadata validation, but it does not execute live API calls, scraping, RSS fetching, parsing, workers, queues, schedulers, or AI processing.
