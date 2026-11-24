import { createRootRoute, Outlet } from "@tanstack/react-router";

import NotFound from "@components/Common/NotFound";

function RootLayout() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-6">
      <h1 className="text-2xl font-semibold">Atlas</h1>

      <Outlet />
    </main>
  );
}

export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFound,
});
