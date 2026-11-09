import type { ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  AppRouterContext,
  type AppRouterInstance,
} from "next/dist/shared/lib/app-router-context.shared-runtime";
import { PathnameContext } from "next/dist/shared/lib/hooks-client-context.shared-runtime";

const router: AppRouterInstance = {
  bfcacheId: "auth-test",
  back: () => {},
  forward: () => {},
  refresh: () => {},
  push: () => {},
  replace: () => {},
  prefetch: async () => {},
};

/** Static rendering only; effects, DOM events and reactive navigation require Stage 02. */
export const renderAuth = (children: ReactNode, pathname: string) => {
  const cache = new QueryClient();

  const html = renderToStaticMarkup(
    <AppRouterContext.Provider value={router}>
      <PathnameContext.Provider value={pathname}>
        <QueryClientProvider client={cache}>{children}</QueryClientProvider>
      </PathnameContext.Provider>
    </AppRouterContext.Provider>,
  );

  cache.clear();

  return html;
};
