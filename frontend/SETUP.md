# Frontend Setup & Installation Guide

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or yarn
- Git

## Installation Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install all required packages including:
- Next.js 15+
- React 19
- TypeScript
- TailwindCSS
- shadcn/ui dependencies
- Zustand
- TanStack Query
- Framer Motion
- Lucide Icons
- Axios

### 2. Environment Configuration

Copy the example env file and configure:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your backend API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Setup shadcn/ui Components

The project is configured with shadcn/ui. To add components as needed:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
```

(All Radix dependencies are already installed)

### 4. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting

## Project Structure Quick Reference

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard page
│   ├── markets/           # Markets page
│   ├── assets/[ticker]/   # Asset detail page
│   ├── ai-assistant/      # AI chat page
│   ├── education/         # Education hub
│   └── settings/          # User settings
├── components/            # Reusable components
│   ├── layout/           # Layout components
│   └── ui/               # shadcn/ui components
├── features/             # Feature-specific code
├── hooks/                # Custom React hooks
├── services/             # API client and services
├── store/                # Zustand stores
├── types/                # TypeScript definitions
├── utils/                # Utility functions
├── styles/               # Global CSS
└── providers/            # React providers
```

## Development Workflow

### Adding a New Page

1. Create folder in `/app` following route structure
2. Create `page.tsx` with your component
3. Import layout if needed (`AppShell` for authenticated pages)

Example:
```tsx
// app/new-feature/page.tsx
import { AppShell } from "@/components/layout";

export default function NewFeaturePage() {
  return (
    <AppShell>
      {/* Page content */}
    </AppShell>
  );
}
```

### Using Dark Mode

The app defaults to dark mode. Users can toggle with theme button in navbar.

Theme is persisted to localStorage and applied to `<html>` element:

```tsx
import { useThemeStore } from "@/store";

function MyComponent() {
  const { theme, toggleTheme } = useThemeStore();
  
  return (
    <button onClick={toggleTheme}>
      Toggle Theme
    </button>
  );
}
```

### Fetching Data

Use TanStack Query with the API service layer:

```tsx
import { useQuery } from "@tanstack/react-query";
import { assetService } from "@/services/api";

function AssetList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["assets"],
    queryFn: () => assetService.getAssets({ limit: 10 }),
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorFallback />;

  return <div>{/* Render data */}</div>;
}
```

### State Management

Use Zustand for client state:

```tsx
import { useAuthStore } from "@/store";

function MyComponent() {
  const { user, logout } = useAuthStore();
  
  return <button onClick={logout}>Logout</button>;
}
```

### Styling with Tailwind

Use utility classes and custom component classes:

```tsx
export function MyComponent() {
  return (
    <div className="p-6 bg-card border border-border rounded-lg">
      <h1 className="text-2xl font-bold">Title</h1>
      <p className="text-muted-foreground">Description</p>
    </div>
  );
}
```

Custom classes available:
- `.glass` - Glassmorphic background
- `.card-hover` - Card hover effect
- `.smooth-transition` - Smooth transitions
- `.text-gradient` - Gradient text effect

### Error Handling

Wrap major sections with `ErrorBoundary`:

```tsx
import { ErrorBoundary } from "@/components/error-boundary";

export default function Page() {
  return (
    <ErrorBoundary>
      <YourContent />
    </ErrorBoundary>
  );
}
```

## Building for Production

```bash
npm run build
npm start
```

The build output will be in the `.next` directory.

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy!

```bash
vercel --prod
```

### Docker

Create `Dockerfile` in frontend root:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t investguide-frontend .
docker run -p 3000:3000 investguide-frontend
```

## Troubleshooting

### Port 3000 Already in Use

```bash
npm run dev -- -p 3001
```

### Type Errors

Run type checking:
```bash
npm run type-check
```

### Cache Issues

Clear Next.js cache:
```bash
rm -rf .next
npm run build
```

### Dependency Issues

Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Tips

1. Use dynamic imports for heavy components
2. Leverage TanStack Query's caching
3. Optimize images with Next.js Image component
4. Use code splitting with route-based splitting
5. Monitor with Next.js Analytics

## Getting Help

- Check ARCHITECTURE.md for detailed structure
- Review existing components for patterns
- Check TypeScript types in `/types/index.ts`
- Review API service layer in `/services/api.ts`

## Next Phase

Once frontend foundation is complete:
1. Connect to backend API endpoints
2. Implement authentication flows
3. Add shadcn/ui components for common patterns
4. Build feature-specific components
5. Add comprehensive error handling
6. Implement loading and empty states
7. Add unit and integration tests
