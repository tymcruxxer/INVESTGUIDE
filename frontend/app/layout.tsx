/**
 * Root Layout
 * Main application layout with providers and structure
 */

import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/providers";
import { ErrorBoundary } from "@/components/error-boundary";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "InvestGuide - AI-Powered Investment Intelligence",
  description:
    "Zimbabwe's leading AI-powered investment intelligence platform for ZSE, VFEX, and REITs",
  keywords: [
    "investment",
    "zimbabwe",
    "stocks",
    "zse",
    "vfex",
    "reits",
    "financial",
    "analytics",
    "ai",
  ],
  robots: "index, follow",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://investguide.co.zw",
    title: "InvestGuide - AI-Powered Investment Intelligence",
    description:
      "Zimbabwe's leading AI-powered investment intelligence platform",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#050816" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className={inter.variable}>
        <ErrorBoundary>
          <Providers>{children}</Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}
