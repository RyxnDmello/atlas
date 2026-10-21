"use client";

import type { ReactNode } from "react";

import {
  QueryClient,
  environmentManager,
  QueryClientProvider,
} from "@tanstack/react-query";

let browser: QueryClient | undefined;

function getClient() {
  if (environmentManager.isServer()) return new QueryClient();

  return (browser ??= new QueryClient());
}

export interface QueryProviderProps {
  children: ReactNode;
}

export default function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={getClient()}>{children}</QueryClientProvider>
  );
}
