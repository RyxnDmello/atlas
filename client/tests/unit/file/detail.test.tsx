import { afterEach, expect, test } from "bun:test";
import { renderToString } from "react-dom/server";
import type { AxiosResponse } from "axios";
import { QueryClientProvider, QueryObserver } from "@tanstack/react-query";
import {
  createRouter,
  createMemoryHistory,
  RouterProvider,
} from "@tanstack/react-router";

import "../auth/environment";

import useFile from "@hooks/file/useFile";
import useEditFile from "@hooks/file/useEditFile";

import http from "@services/http/axios";
import { coordination } from "@services/auth/auth";

import { fileKey, FileFailure } from "@utils/file/file";
import { folderKey } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

import { routeTree } from "@/routeTree.gen";

import {
  harness,
  renderHook,
  file,
  id,
  child,
  listing,
} from "../folder/fixtures";

const originalState = useAuthStore.getState();
const originalInitial = {
  ...useAuthStore.getInitialState(),
};
const originalCoordination = {
  ...coordination,
};
const originalAdapter = http.defaults.adapter;
const originalGet = http.get;
const cleanups: (() => void)[] = [];

afterEach(() => {
  cleanups.splice(0).forEach((close) => close());
  Object.assign(useAuthStore.getInitialState(), originalInitial);
  Object.assign(coordination, originalCoordination);
  useAuthStore.setState(originalState);
  http.defaults.adapter = originalAdapter;
  http.get = originalGet;
});

const setup = async (status = 200, data: unknown = file) => {
  const h = await harness({
    status,
    data,
  });
  cleanups.push(h.close);

  return h;
};

const observe = (
  cache: Awaited<ReturnType<typeof harness>>["cache"],
  selected = file.id,
) => {
  const hook = renderHook(() => useFile(selected), cache);
  const query = cache.getQueryCache().find({
    queryKey: fileKey(selected),
  });

  if (!query) {
    throw new Error("Missing file query.");
  }

  const observer = new QueryObserver(cache, {
    ...query.options,
    queryKey: query.queryKey,
    enabled: false,
  });

  return {
    hook,
    query,
    observer,
  };
};

test.each(["processing", "ready", "deleting"])(
  "direct %s metadata uses exact key, shared protected GET, matching ten-field DTO and 60-second cache",
  async (status) => {
    const data = {
      ...file,
      status,
    };
    const h = await setup(200, data);
    const { query, observer } = observe(h.cache);

    expect(query.queryKey).toEqual(["drive", "file", file.id]);
    expect(observer.options.staleTime).toBe(60_000);
    expect(query.options.retry).toBe(false);
    expect(h.requests).toHaveLength(0);
    expect((await observer.refetch()).data).toEqual(data);
    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].url).toBe(`/files/${file.id}`);
    expect(h.requests[0].isProtected).toBe(true);
    expect(h.requests[0].signal).toBeInstanceOf(AbortSignal);
    expect(h.requests[0].headers.get("Authorization")).toStartWith("Bearer ");
    expect(h.cache.getQueryCache().getAll()).toHaveLength(1);
    expect(renderHook(() => useFile(file.id), h.cache).fileData).toEqual(data);

    await h.cache.fetchQuery({
      ...query.options,
      queryKey: query.queryKey,
      staleTime: 60_000,
    });

    expect(h.requests).toHaveLength(1);
  },
);

test.each([
  {
    ...file,
    id,
  },
  {
    ...file,
    owner_id: id,
  },
  {
    ...file,
    status: "failed",
  },
  {
    ...file,
    folder_id: "invalid",
  },
  {
    ...file,
    created_at: "yesterday",
  },
  {
    name: "Incomplete",
  },
])("malformed or mismatched metadata is never cached", async (data) => {
  const h = await setup(200, data);
  const result = await observe(h.cache).observer.refetch();

  expect(result.error).toBeInstanceOf(FileFailure);
  expect(h.cache.getQueryData(fileKey(file.id))).toBeUndefined();
});

test.each(["restoring", "error", "unauthenticated"] as const)(
  "%s prevents cached metadata exposure and even manual GET dispatch",
  async (status) => {
    const h = await setup();
    h.cache.setQueryData(fileKey(file.id), file);
    useAuthStore.getState().update({
      status,
    });

    const { hook, observer } = observe(h.cache);

    expect(hook.fileData).toBeUndefined();
    await expect(hook.refreshFile()).rejects.toThrow();
    expect((await observer.refetch()).isError).toBe(true);
    expect(h.requests).toHaveLength(0);
  },
);

test("malformed ID, missing user and pending logout cannot dispatch file reads", async () => {
  const h = await setup();
  const { hook, observer } = observe(h.cache, "bad-id");

  expect(hook.isFileInvalid).toBe(true);
  expect((await observer.refetch()).isError).toBe(true);

  for (const update of [
    {
      user: null,
    },
    {
      logout: "pending" as const,
    },
  ]) {
    useAuthStore.getState().update(update);

    expect(
      renderHook(() => useFile(file.id), h.cache).fileData,
    ).toBeUndefined();
    expect((await observe(h.cache).observer.refetch()).isError).toBe(true);
  }

  expect(h.requests).toHaveLength(0);
});

test("metadata Retry explicitly refetches; Ask not-ready reconciles with GET and never a write", async () => {
  const h = await setup(503, {
    error: "private",
    code: "INTERNAL_ERROR",
  });
  const first = observe(h.cache);

  expect((await first.observer.refetch()).isError).toBe(true);
  h.reply.status = 200;
  h.reply.data = file;

  expect(await first.hook.refreshFile()).toEqual(file);
  h.reply.data = {
    ...file,
    status: "deleting",
  };
  await first.hook.reconcileFile(409, "FILE_NOT_READY");

  expect(h.cache.getQueryData(fileKey(file.id))).toEqual(h.reply.data);
  expect(h.requests).toHaveLength(3);
  expect(h.requests.every((request) => request.method === "get")).toBe(true);
});

test("confirmed existing PATCH refetches active file detail and stales inactive drive queries only", async () => {
  const h = await setup();
  const { observer } = observe(h.cache);
  observer.setOptions({
    ...observer.options,
    enabled: true,
  });
  const unsubscribe = observer.subscribe(() => undefined);
  cleanups.push(unsubscribe);
  await observer.refetch();
  h.cache.setQueryData(folderKey(null), listing);
  h.cache.setQueryData(fileKey(child), {
    ...file,
    id: child,
  });
  h.cache.setQueryData(["auth", "unrelated"], "preserved");
  h.reply.data = {
    ...file,
    name: "Changed",
  };

  await renderHook(() => useEditFile(file), h.cache).editFile({
    name: "Changed",
    description: "",
  });

  expect(h.cache.getQueryData(fileKey(file.id))).toEqual(h.reply.data);
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);
  expect(h.cache.getQueryState(fileKey(child))?.isInvalidated).toBe(true);
  expect(h.cache.getQueryState(["auth", "unrelated"])?.isInvalidated).toBe(
    false,
  );
  expect(h.requests.map((request) => request.method)).toEqual([
    "get",
    "patch",
    "get",
  ]);
});

test("an abort-ignoring old-owner GET cannot publish into owner B's SAME file key", async () => {
  const h = await setup();
  let resolve!: (value: AxiosResponse<unknown>) => void;

  http.get = (() =>
    new Promise<AxiosResponse<unknown>>((done) => {
      resolve = done;
    })) as typeof http.get;
  const pending = observe(h.cache).observer.refetch();
  await h.adopt();
  http.get = originalGet;
  h.reply.data = {
    ...file,
    name: "Owner B",
  };
  await observe(h.cache).observer.refetch();
  resolve({
    data: file,
    status: 200,
    statusText: "fixture",
    headers: {},
    config: {
      headers: h.requests[0].headers,
    },
  });
  await pending;

  expect(h.cache.getQueryData(fileKey(file.id))).toEqual(h.reply.data);
  expect(h.cache.getQueryCache().getAll()).toHaveLength(1);
});

test("lease guard rejects late metadata even without QueryProvider cancellation", async () => {
  const h = await setup();
  h.close();
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  http.get = (async () => {
    await waiting;

    return {
      status: 200,
      data: file,
    };
  }) as typeof http.get;
  const pending = observe(h.cache).observer.refetch();
  useAuthStore.getState().update({
    status: "error",
  });
  release();
  await pending;

  expect(h.cache.getQueryData(fileKey(file.id))).toBeUndefined();
});

/** Generated router + SSR only: no DOM effects or live browser/network. */
const render = async (path: string, data?: unknown, failure?: FileFailure) => {
  const h = await setup();
  Object.assign(useAuthStore.getInitialState(), useAuthStore.getState());
  const selected = path.split("/").at(-1)?.toLowerCase() ?? file.id;

  if (data) {
    h.cache.setQueryData(fileKey(selected), data);
  }

  if (failure) {
    h.cache
      .getQueryCache()
      .build(h.cache, {
        queryKey: fileKey(selected),
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
    router,
  };
};

test.each([null, id])(
  "generated direct file route renders canonical parent %s, escaped metadata and only ready Ask",
  async (parent) => {
    const selected = "25bca73f-3610-443c-9f74-8c2c2f91a54c";
    const { html, requests, router } = await render(
      `/drive/file/${selected.toUpperCase()}`,
      {
        ...file,
        id: selected,
        name: "<script>private</script>",
        folder_id: parent,
      },
    );

    expect(router.state.matches.map((match) => match.routeId)).toEqual([
      "__root__",
      "/drive",
      "/drive/file/$id",
    ]);
    expect(html).toContain(`href="${parent ? `/drive/${parent}` : "/drive"}"`);
    expect(html).toContain("&lt;script&gt;");
    expect(html).not.toContain("<script>private");
    expect(html).toContain("source.md");
    expect(html).toContain("Question");
    expect(html).toContain("Ask this file");
    expect(html).not.toContain("Sources");
    expect(html).not.toContain("Edit File");
    expect(html).not.toContain("Delete File");
    expect(html).not.toContain("Logout");
    expect(html).not.toContain("Loading folder");
    expect(requests).toHaveLength(0);
  },
);

test.each(["processing", "deleting"])(
  "%s metadata is visible with refresh and no Ask form",
  async (status) => {
    const { html } = await render(`/drive/file/${file.id}`, {
      ...file,
      status,
    });

    expect(html.replaceAll("<!-- -->", "")).toContain(
      `Ask is unavailable while this file is ${status}`,
    );
    expect(html).toContain("Refresh file");
    expect(html).not.toContain("Question");
  },
);

test("loading, invalid path, safe 404 and recoverable errors withhold private names", async () => {
  expect((await render(`/drive/file/${file.id}`)).html).toContain(
    "Loading file",
  );
  const invalid = await render("/drive/file/not-a-uuid", file);
  expect(invalid.requests).toHaveLength(0);
  expect(invalid.html).not.toContain(file.name);

  for (const code of ["FILE_NOT_FOUND", "FOREIGN_PRIVATE_DIAGNOSTIC"]) {
    const { html } = await render(
      `/drive/file/${file.id}`,
      file,
      new FileFailure(404, code),
    );

    expect(html).toContain("File not found.");
    expect(html).not.toContain(file.name);
    expect(html).not.toContain(code);
  }

  const { html } = await render(
    `/drive/file/${file.id}`,
    file,
    new FileFailure(503, "PRIVATE_TRACE"),
  );
  expect(html).toContain("Unable to load this file");
  expect(html).not.toContain("PRIVATE_TRACE");
  expect(html).not.toContain(file.name);
});
