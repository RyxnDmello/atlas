import { afterEach, expect, test } from "bun:test";
import { existsSync, readdirSync } from "node:fs";
import { renderToString } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createRouter,
  createMemoryHistory,
  Outlet,
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

test("the drive parent owns only an Outlet and three independent child pages", () => {
  const router = createTestRouter("/drive");
  const parent = router.routesById["/drive"];

  expect(parent.options.component).toBe(Outlet);
  expect(parent.options.loader).toBeUndefined();
  expect(parent.options.beforeLoad).toBeUndefined();
  expect(
    Object.values(parent.children ?? {})
      .map((route) => route.id)
      .sort(),
  ).toEqual(["/drive/", "/drive/$id", "/drive/file/$id"]);

  const target = router.buildLocation({
    to: "/drive",
  });

  expect(target.pathname).toBe("/drive");
});

test.each([
  ["/drive", "/drive/"],
  ["/drive/", "/drive/"],
  [folderPath, "/drive/$id"],
  [`${folderPath}/`, "/drive/$id"],
  [filePath, "/drive/file/$id"],
  [`${filePath}/`, "/drive/file/$id"],
] as const)("%s matches exactly its nested page %s", (path, leaf) => {
  const router = createTestRouter(path);
  const matches = router.matchRoutes(path);

  expect(matches.map((match) => match.routeId)).toEqual([
    "__root__",
    "/drive",
    leaf,
  ]);
});

test("the route directory contains no old flat or unintended route definitions", () => {
  const directory = new URL("../../src/routes/", import.meta.url);
  const files = readdirSync(directory, {
    encoding: "utf8",
    recursive: true,
  })
    .map((path) => path.replaceAll("\\", "/"))
    .filter((path) => path.endsWith(".tsx"))
    .sort();

  expect(files).toEqual([
    "__root.tsx",
    "drive/$id.tsx",
    "drive/file/$id.tsx",
    "drive/index.tsx",
    "drive/route.tsx",
    "index.tsx",
    "login.tsx",
    "register.tsx",
    "verify.tsx",
  ]);
  expect(existsSync(new URL("drive.tsx", directory))).toBe(false);
});
