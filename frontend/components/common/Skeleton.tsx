"use client";

import React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-2xl bg-white/5 border border-white/5", className)}
      {...props}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-xl">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-16" />
      </div>
      <Skeleton className="h-10 w-48 mt-2" />
      <div className="grid grid-cols-4 gap-2 pt-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    </div>
  );
}
