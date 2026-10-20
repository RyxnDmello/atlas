"use client";

import {
  environmentManager,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import type { ReactNode } from "react";

let browser: QueryClient | undefined;

function getClient() {
  if (environmentManager.isServer()) return new QueryClient();
  return (browser ??= new QueryClient());
}

export function QueryProvider({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={getClient()}>{children}</QueryClientProvider>
  );
}
