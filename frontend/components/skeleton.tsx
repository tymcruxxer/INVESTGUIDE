/**
 * Loading Skeleton
 * Reusable skeleton loader for UI elements
 */

import { cn } from "@/utils";

interface SkeletonProps {
  className?: string;
  count?: number;
}

export function Skeleton({ className, count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-12 bg-muted rounded-lg animate-pulse",
            className
          )}
        />
      ))}
    </>
  );
}

export function CardSkeleton() {
  return (
    <div className="p-4 bg-card rounded-lg border border-border">
      <Skeleton className="h-6 w-3/4 mb-4" />
      <Skeleton className="h-4 w-full mb-2" count={3} />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="w-full h-[300px] bg-card rounded-lg border border-border animate-pulse" />
  );
}
