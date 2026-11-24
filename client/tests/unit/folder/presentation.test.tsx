import { afterEach, expect, test } from "bun:test";
import { renderToString } from "react-dom/server";
import { QueryClientProvider } from "@tanstack/react-query";
import {
  createRouter,
  createMemoryHistory,
  RouterProvider,
} from "@tanstack/react-router";

import "../auth/environment";

import http from "@services/http/axios";
import { coordination } from "@services/auth/auth";

import type { FolderListing } from "@schemas/folder/folder";

import { folderKey, FolderFailure } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

import { routeTree } from "@/routeTree.gen";

import { harness, folder, file, listing, id, child, other } from "./fixtures";

const initial = useAuthStore.getInitialState();
const originalInitial = {
  ...initial,
};
const originalState = useAuthStore.getState();
const originalCoordination = {
  ...coordination,
};
const originalAdapter = http.defaults.adapter;
const cleanups: (() => void)[] = [];

afterEach(() => {
  cleanups.splice(0).forEach((cleanup) => cleanup());
  Object.assign(initial, originalInitial);
  Object.assign(coordination, originalCoordination);
  useAuthStore.setState(originalState);
  http.defaults.adapter = originalAdapter;
});

/** Actual generated routes + SSR only; no DOM events, effects or live HTTP. */
const render = async (
  path: string,
  data?: FolderListing,
  failure?: FolderFailure,
) => {
  const h = await harness();

  cleanups.push(h.close);
  Object.assign(initial, useAuthStore.getState());

  const key = folderKey(path === "/drive" ? null : path.split("/")[2]);

  if (data) {
    h.cache.setQueryData(key, data);
  }

  if (failure) {
    h.cache
      .getQueryCache()
      .build(h.cache, {
        queryKey: key,
      })
      .setState({
        status: "error",
        error: failure,
      });
  }

  const router = createRouter({
    routeTree,
    history: createMemoryHistory({
      initialEntries: [path],
    }),
    isServer: true,
  });

  await router.load();

  return {
    html: renderToString(
      <QueryClientProvider client={h.cache}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    ),
    requests: h.requests,
  };
};

test("root renders folders before managed files, UUID links, duplicates and retained account controls", async () => {
  const { html, requests } = await render("/drive", {
    folder: null,
    folders: [
      {
        ...folder,
        name: "Duplicate",
      },
      {
        ...folder,
        id: child,
        name: "Duplicate",
      },
    ],
    files: [
      {
        ...file,
        name: "Read-only file",
      },
      {
        ...file,
        id: "00000000-0000-4000-8000-000000000014",
        name: "Other file",
        status: "deleting",
      },
    ],
  });

  expect(html).toContain("My Drive");
  expect(html).toContain(`href="/drive/${id}"`);
  expect(html).toContain(`href="/drive/${child}"`);
  expect(html.lastIndexOf("Duplicate")).toBeLessThan(
    html.indexOf("Read-only file"),
  );
  expect(html.indexOf("Read-only file")).toBeLessThan(
    html.indexOf("Other file"),
  );
  expect(html).toContain("New Folder");
  expect(html).not.toContain("Edit Folder");
  expect(html).toContain(`href="/drive/file/${file.id}"`);
  expect(html).toContain("Upload File");
  expect(html).toContain("Edit File");
  expect(html).toContain("Delete File");
  expect(html).toContain("Retry delete");
  expect(html).not.toContain("Ask");
  expect(html).toContain("Logout");
  expect(html).toContain("fixture@example.test");
  expect(requests).toHaveLength(0);
});

test.each([null, other])(
  "selected deep link uses canonical title/description and parent %s without loading root",
  async (parent) => {
    const { html, requests } = await render(`/drive/${id}`, {
      ...listing,
      folder: {
        ...folder,
        parent_id: parent,
      },
      files: [file],
    });

    expect(html).toContain("Selected folder");
    expect(html).toContain("Canonical description");
    expect(html).toContain("Edit Folder");
    expect(html).toContain("New Folder");
    expect(html).toMatch(
      new RegExp(`href="${parent ? `/drive/${parent}` : "/drive"}"[^>]*>Up`),
    );
    expect(html).not.toContain("This folder is empty.");
    expect(requests).toHaveLength(0);
  },
);

test.each(["ready", "processing", "deleting"] as const)(
  "nested file status %s exposes only its permitted inline controls",
  async (status) => {
    const { html, requests } = await render(`/drive/${id}`, {
      ...listing,
      folder,
      files: [
        {
          ...file,
          status,
        },
      ],
    });

    expect(html).toContain(status);
    expect(html.includes("Edit File")).toBe(status === "ready");
    expect(html.includes("Delete File")).toBe(status === "ready");
    expect(html.includes("Retry delete")).toBe(status === "deleting");
    expect(html).toContain(`href="/drive/file/${file.id}"`);
    expect(html).not.toContain("Ask");
    expect(requests).toHaveLength(0);
  },
);

test("genuine empty and loading are separate and do not mount open mutation forms", async () => {
  const empty = await render("/drive", listing);
  const loading = await render("/drive");

  expect(empty.html).toContain("This folder is empty.");
  expect(empty.html).not.toContain("Loading folder");
  expect(empty.html).not.toContain("<form");
  expect(loading.html).toContain("Loading folder");
  expect(loading.html).not.toContain("This folder is empty.");
});

test("foreign/missing 404 hides cached names and diagnostics; transport/invalid response offers recovery", async () => {
  const missing = await render(
    `/drive/${id}`,
    {
      ...listing,
      folder,
    },
    new FolderFailure(404, "FOLDER_NOT_FOUND"),
  );
  const transport = await render(
    "/drive",
    undefined,
    new FolderFailure(0, "SECRET_DIAGNOSTIC"),
  );
  const invalid = await render(
    "/drive",
    undefined,
    new FolderFailure(200, "INVALID_RESPONSE"),
  );

  expect(missing.html).toContain("Folder not found.");
  expect(missing.html).not.toContain("Selected folder");
  expect(transport.html).toContain("Retry");
  expect(transport.html).not.toContain("SECRET_DIAGNOSTIC");
  expect(invalid.html).toContain("Retry");
});
