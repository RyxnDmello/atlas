import { useEffect, type ReactNode } from "react";
import {
  QueryClient,
  environmentManager,
  QueryClientProvider,
} from "@tanstack/react-query";

import { initializeAuth, onAuthBoundary } from "@services/auth/auth";

let browser: QueryClient | undefined;

export const bindAuthCache = (cache: QueryClient) => {
  return onAuthBoundary(() => {
    void cache.cancelQueries();
    cache.clear();
  });
};

const getClient = () => {
  if (environmentManager.isServer()) {
    return new QueryClient();
  }

  if (!browser) {
    browser = new QueryClient();

    const cache = browser;

    bindAuthCache(cache);
  }

  return browser;
};

export interface QueryProviderProps {
  children: ReactNode;
}

export default function QueryProvider({ children }: QueryProviderProps) {
  useEffect(() => {
    void initializeAuth();
  }, []);

  return (
    <QueryClientProvider client={getClient()}>{children}</QueryClientProvider>
  );
}
