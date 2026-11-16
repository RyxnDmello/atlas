import { afterEach, expect, test } from "bun:test";
import { renderToString } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createRouter,
  createMemoryHistory,
  RouterProvider,
} from "@tanstack/react-router";

import "./auth/environment";

import useAuthStore from "@stores/auth";

import { routeTree } from "../../src/routeTree.gen";

const initial = useAuthStore.getInitialState();
const original = {
  ...initial,
};
const user = {
  id: "00000000-0000-4000-8000-000000000005",
  name: "Canonical <script>profile</script>",
  email: "canonical@example.test",
};
const folderPath = "/drive/00000000-0000-4000-8000-000000000005";
const filePath = "/drive/file/00000000-0000-4000-8000-000000000005";
const paths = [
  "/",
  "/login",
  "/register",
  "/verify",
  "/drive",
  folderPath,
  filePath,
];
const protectedPath = (path: string) =>
  path === "/drive" || path === folderPath || path === filePath;

const createTestRouter = (path: string) => {
  return createRouter({
    routeTree,
    history: createMemoryHistory({
      initialEntries: [path],
    }),
    isServer: true,
  });
};

/** Loads the actual generated routes, without browser effects or HTTP. */
const renderRoute = async (path: string) => {
  const router = createTestRouter(path);
  const cache = new QueryClient();

  await router.load();

  try {
    return renderToString(
      <QueryClientProvider client={cache}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    );
  } finally {
    cache.clear();
  }
};

afterEach(() => {
  Object.assign(initial, original);
});

for (const path of paths) {
  test.each([
    "restoring",
    "authenticated",
    "unauthenticated",
    "error",
  ] as const)(
    `${path}: generated route composition protects %s visibility`,
    async (status) => {
      Object.assign(initial, {
        status,
        user: status === "authenticated" ? user : null,
      });

      const html = await renderRoute(path);

      if (status === "restoring") {
        expect(html).toContain("Checking session");
        expect(html).not.toContain("<form");
      } else if (status === "error") {
        expect(html).toContain("Retry session check");
        expect(html).not.toContain("<form");
      } else if (status === "authenticated" && path === filePath) {
        expect(html).toContain("Loading file");
        expect(html).not.toContain("Question");
      } else if (status === "authenticated" && protectedPath(path)) {
        expect(html).toContain("canonical@example.test");
        expect(html).toContain(
          "Canonical &lt;script&gt;profile&lt;/script&gt;",
        );
        expect(html).toContain("Logout");
        expect(html).not.toContain("<form");
      } else if (
        status === "unauthenticated" &&
        path !== "/" &&
        !protectedPath(path)
      ) {
        expect(html).toContain("<form");
      } else {
        expect(html).toContain("Redirecting");
        expect(html).not.toContain("<form");
      }

      if (status !== "authenticated" || !protectedPath(path)) {
        expect(html).not.toContain("canonical@example.test");
      }

      expect(html).not.toContain("<script>profile</script>");
    },
  );
}

test.each([
  "/dashboard",
  "/unknown",
  "/drive/invalid",
  "/drive/file",
  "/drive/file/invalid",
])(
  "%s has a neutral not-found result without protected content",
  async (path) => {
    Object.assign(initial, {
      status: "authenticated",
      user,
    });

    const html = await renderRoute(path);

    expect(html).toContain("Page not found.");
    expect(html).not.toContain("canonical@example.test");
    expect(html).not.toContain("Logout");
    expect(html).not.toContain("<form");
  },
);

test("the generated route tree registers the seven approved routes including file detail", () => {
  const router = createTestRouter("/");

  expect(Object.keys(router.routesByPath).sort()).toEqual([
    "/",
    "/drive",
    "/drive/$id",
    "/drive/file/$id",
    "/login",
    "/register",
    "/verify",
  ]);
});
