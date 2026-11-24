import type { ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createRouter,
  createRootRoute,
  createMemoryHistory,
  RouterContextProvider,
} from "@tanstack/react-router";

/** Static rendering only; effects, DOM events and reactive navigation require Stage 02. */
export const renderAuth = (children: ReactNode, pathname: string) => {
  const cache = new QueryClient();
  const router = createRouter({
    routeTree: createRootRoute(),
    history: createMemoryHistory({
      initialEntries: [pathname],
    }),
    isServer: true,
  });

  const html = renderToStaticMarkup(
    <RouterContextProvider router={router}>
      <QueryClientProvider client={cache}>{children}</QueryClientProvider>
    </RouterContextProvider>,
  );

  cache.clear();

  return html;
};
