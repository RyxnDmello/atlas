import { afterEach, expect, test } from "bun:test";

import "../auth/environment";

import useCreateFolder from "@hooks/folder/useCreateFolder";
import useEditFolder from "@hooks/folder/useEditFolder";
import useFolder from "@hooks/folder/useFolder";

import http from "@services/http/axios";
import { folderSession, checkFolderSession } from "@services/folder/session";
import {
  coordination,
  startAuth,
  finishLogout,
  failCredentials,
} from "@services/auth/auth";

import {
  fileSchema,
  folderSchema,
  listingSchema,
  folderFormSchema,
  folderCreateSchema,
  folderPatchSchema,
} from "@schemas/folder/folder";

import {
  folderKey,
  folderChanges,
  folderResponse,
  folderFeedback,
  FolderFailure,
} from "@utils/folder/folder";

import useAuthStore, { initialAuth } from "@stores/auth";

import { deferred, response } from "../auth/fixtures";
import {
  harness,
  renderHook,
  observeFolder,
  folder,
  file,
  listing,
  id,
  child,
  other,
} from "./fixtures";

const originalCoordination = {
  ...coordination,
};
const originalStore = useAuthStore.getState();
const originalAdapter = http.defaults.adapter;
const originalGet = http.get;
const cleanups: (() => void)[] = [];

afterEach(() => {
  cleanups.splice(0).forEach((cleanup) => cleanup());
  Object.assign(coordination, originalCoordination);
  useAuthStore.setState(originalStore);
  http.defaults.adapter = originalAdapter;
  http.get = originalGet;
});

const setup = async (status = 200, data: unknown = listing) => {
  const h = await harness({
    status,
    data,
  });

  cleanups.push(h.close);

  return h;
};

test("DTOs accept exactly public metadata, nullable fields and all three statuses", () => {
  expect(folderSchema.parse(folder)).toEqual(folder);

  for (const status of ["processing", "ready", "deleting"] as const) {
    expect(
      fileSchema.parse({
        ...file,
        status,
      }).status,
    ).toBe(status);
  }

  expect(listingSchema.parse(listing)).toEqual(listing);

  for (const change of [
    {
      status: "failed",
    },
    {
      id: "bad",
    },
    {
      size_bytes: "25",
    },
    {
      created_at: "yesterday",
    },
    {
      owner_id: other,
    },
  ]) {
    expect(
      fileSchema.safeParse({
        ...file,
        ...change,
      }).success,
    ).toBe(false);
  }

  expect(
    folderSchema.safeParse({
      ...folder,
      description: undefined,
    }).success,
  ).toBe(false);
  expect(
    listingSchema.safeParse({
      folders: [],
      files: [],
    }).success,
  ).toBe(false);
  expect(() =>
    folderResponse(
      {
        status: 200,
        data: {},
      },
      200,
      listingSchema,
    ),
  ).toThrow(FolderFailure);
});

test("form/create/PATCH validation normalizes metadata without invented uniqueness or length constraints", () => {
  expect(
    folderFormSchema.safeParse({
      name: " ",
      description: "",
    }).success,
  ).toBe(false);
  expect(
    folderFormSchema.safeParse({
      name: "a".repeat(1000),
      description: "b".repeat(1000),
    }).success,
  ).toBe(true);
  expect(
    folderCreateSchema.parse({
      name: " Duplicate ",
      description: " ",
      parent_id: null,
    }),
  ).toEqual({
    name: "Duplicate",
    description: null,
    parent_id: null,
  });
  expect(
    folderPatchSchema.parse({
      description: null,
    }),
  ).toEqual({
    description: null,
  });
  expect(
    folderPatchSchema.parse({
      name: " Changed ",
    }),
  ).toEqual({
    name: "Changed",
  });

  for (const input of [
    {},
    {
      name: null,
    },
    {
      parent_id: child,
    },
    {
      owner_id: other,
    },
  ]) {
    expect(folderPatchSchema.safeParse(input).success).toBe(false);
  }

  expect(
    folderChanges(folder, {
      name: folder.name,
      description: folder.description,
    }),
  ).toEqual({});
  expect(
    folderChanges(folder, {
      name: " Changed ",
      description: " ",
    }),
  ).toEqual({
    name: "Changed",
    description: null,
  });
});

test.each([null, id])(
  "GET %s uses exact path, protected shared Axios, signal and simple keys",
  async (selected) => {
    const data = {
      ...listing,
      folder: selected === null ? null : folder,
    };
    const h = await setup(200, data);
    const { query, observer } = observeFolder(h.cache, selected);

    expect(query.queryKey).toEqual(["drive", "folder", selected ?? "root"]);
    expect(observer.options.staleTime).toBe(60_000);
    expect(query.options.retry).toBe(false);
    expect(h.requests).toHaveLength(0);
    expect((await observer.refetch()).data).toEqual(data);
    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].url).toBe(
      selected === null ? "/folders" : `/folders/${id}`,
    );
    expect(h.requests[0].params).toBeUndefined();
    expect(h.requests[0].isProtected).toBe(true);
    expect(h.requests[0].signal).toBeInstanceOf(AbortSignal);
    expect(h.requests[0].headers.get("Authorization")).toBe(
      `Bearer ${response.access_token}`,
    );
  },
);

test.each(["restoring", "unauthenticated", "error"] as const)(
  "%s gates query execution and manual refresh",
  async (status) => {
    const h = await setup();

    useAuthStore.getState().update({
      status,
    });

    const { hook, query, observer } = observeFolder(h.cache, null);

    expect("enabled" in query.options && query.options.enabled).toBe(false);
    await expect(hook.refreshFolder()).rejects.toThrow();
    expect((await observer.refetch()).isError).toBe(true);
    expect(h.requests).toHaveLength(0);
  },
);

test("missing canonical user, pending logout and malformed IDs never dispatch", async () => {
  const h = await setup();
  const snapshot = useAuthStore.getState();

  for (const update of [
    {
      user: null,
    },
    {
      logout: "pending" as const,
    },
  ]) {
    useAuthStore.setState({
      ...snapshot,
      ...update,
    });

    const { observer } = observeFolder(h.cache, null);

    expect((await observer.refetch()).isError).toBe(true);
  }

  useAuthStore.setState(snapshot);

  const { hook, query, observer } = observeFolder(h.cache, "file");

  expect("enabled" in query.options && query.options.enabled).toBe(false);
  expect(hook.isFolderInvalid).toBe(true);
  expect((await observer.refetch()).isError).toBe(true);
  expect(h.requests).toHaveLength(0);
});

test.each([null, id])(
  "GET %s rejects wrong selected location and malformed success without caching",
  async (selected) => {
    const h = await setup(200, {
      ...listing,
      folder: selected === null ? folder : null,
    });
    const { observer } = observeFolder(h.cache, selected);

    expect((await observer.refetch()).error).toBeInstanceOf(FolderFailure);
    expect(h.cache.getQueryData(folderKey(selected))).toBeUndefined();
    expect(h.requests).toHaveLength(1);
  },
);

test("missing and foreign 404s have the same safe message; invalid responses and 5xx remain explicit", async () => {
  const h = await setup(404, {
    code: "FOLDER_NOT_FOUND",
    error: "private diagnostic",
  });
  const { observer } = observeFolder(h.cache, id);
  const result = await observer.refetch();

  expect(folderFeedback(result.error)).toBe("Folder not found.");
  expect(
    folderFeedback(new FolderFailure(500, "PRIVATE_DATABASE_ERROR")),
  ).not.toContain("PRIVATE");
  expect(folderFeedback(new FolderFailure(422, "VALIDATION_ERROR"))).toContain(
    "name and description",
  );
  expect(h.requests).toHaveLength(1);
});

test.each([null, id])(
  "create injects exact parent %s, normalizes fields and invalidates drive only",
  async (parent) => {
    const returned = {
      ...folder,
      parent_id: parent,
    };
    const h = await setup(201, returned);

    h.cache.setQueryData(folderKey(null), listing);
    h.cache.setQueryData(folderKey(child), {
      ...listing,
      folder,
    });
    h.cache.setQueryData(["auth"], "retain");

    const hook = renderHook(() => useCreateFolder(), h.cache);

    expect(
      await hook.createFolder({
        name: " Duplicate ",
        description: " ",
        parent_id: parent,
      }),
    ).toEqual(returned);
    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].url).toBe("/folders");
    expect(h.requests[0].method).toBe("post");
    expect(JSON.parse(h.requests[0].data)).toEqual({
      name: "Duplicate",
      description: null,
      parent_id: parent,
    });
    expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);
    expect(h.cache.getQueryState(folderKey(child))?.isInvalidated).toBe(true);
    expect(h.cache.getQueryState(["auth"])?.isInvalidated).toBe(false);
  },
);

test("metadata PATCH sends changed fields only, supports null and rejects relocation/empty/null name", async () => {
  const h = await setup(200, {
    ...folder,
    description: null,
  });
  const hook = renderHook(() => useEditFolder(folder), h.cache);

  await hook.editFolder({
    description: null,
  });

  expect(h.requests[0].url).toBe(`/folders/${id}`);
  expect(h.requests[0].method).toBe("patch");
  expect(JSON.parse(h.requests[0].data)).toEqual({
    description: null,
  });

  await expect(hook.editFolder({})).rejects.toThrow();
  await expect(
    hook.editFolder(JSON.parse('{"parent_id":null}')),
  ).rejects.toThrow();
  await expect(hook.editFolder(JSON.parse('{"name":null}'))).rejects.toThrow();
  expect(h.requests).toHaveLength(1);
});

test("cancel/unsubmitted hooks and invalid creation send no HTTP", async () => {
  const h = await setup();
  const creation = renderHook(() => useCreateFolder(), h.cache);

  renderHook(() => useEditFolder(folder), h.cache);

  expect(h.requests).toHaveLength(0);
  await expect(
    creation.createFolder({
      name: " ",
      parent_id: null,
    }),
  ).rejects.toThrow();
  expect(h.requests).toHaveLength(0);
});

test.each(["create", "edit"] as const)(
  "%s guards rapid duplicate submissions and keeps pending until confirmation",
  async (operation) => {
    const h = await setup();
    const waiting = deferred<void>();

    http.defaults.adapter = async (config) => {
      h.requests.push(config);

      await waiting.promise;

      return {
        config,
        status: operation === "create" ? 201 : 200,
        statusText: "fixture",
        headers: {},
        data: folder,
      };
    };

    const creation = renderHook(() => useCreateFolder(), h.cache);
    const editing = renderHook(() => useEditFolder(folder), h.cache);
    const submit = () =>
      operation === "create"
        ? creation.createFolder({
            name: "Name",
            parent_id: null,
          })
        : editing.editFolder({
            name: "Name",
          });

    const first = submit();
    const duplicate = submit();

    await expect(duplicate).rejects.toMatchObject({
      code: "REQUEST_PENDING",
    });
    expect(h.requests).toHaveLength(1);
    expect(
      h.cache
        .getMutationCache()
        .getAll()
        .some((mutation) => mutation.state.status === "pending"),
    ).toBe(true);

    waiting.resolve();

    await first;

    expect(h.requests).toHaveLength(1);
  },
);

test.each([0, 500, 201])(
  "ambiguous mutation %s never retries or publishes invented success",
  async (status) => {
    const h = await setup(status, {
      invalid: "private",
    });
    const hook = renderHook(() => useCreateFolder(), h.cache);

    if (status === 0) {
      http.defaults.adapter = async (config) => {
        h.requests.push(config);

        throw new Error("transport");
      };
    }

    const error = await hook
      .createFolder({
        name: "Name",
        parent_id: null,
      })
      .catch((failure: unknown) => failure);

    expect(error).toBeInstanceOf(FolderFailure);
    expect(error instanceof FolderFailure && error.uncertain).toBe(true);
    expect(h.requests).toHaveLength(1);
    expect(h.cache.getQueryData(folderKey(null))).toBeUndefined();
  },
);

test("active root refetches after create while inactive nested cache waits until revisit", async () => {
  const h = await setup();
  const { observer, query } = observeFolder(h.cache, null);

  observer.setOptions({
    ...query.options,
    queryKey: query.queryKey,
    enabled: true,
  });

  const unsubscribe = observer.subscribe(() => undefined);

  cleanups.push(unsubscribe);
  await observer.refetch();
  h.cache.setQueryData(folderKey(child), {
    ...listing,
    folder: {
      ...folder,
      id: child,
    },
  });
  h.cache.setQueryData(["auth"], "unchanged");

  const before = h.requests.length;
  const original = http.defaults.adapter;

  http.defaults.adapter = async (config) => {
    if (config.method === "post") {
      h.requests.push(config);

      return {
        config,
        status: 201,
        statusText: "fixture",
        headers: {},
        data: folder,
      };
    }

    if (typeof original !== "function") {
      throw new Error("Expected test adapter.");
    }

    return original(config);
  };

  await renderHook(() => useCreateFolder(), h.cache).createFolder({
    name: "Name",
    parent_id: null,
  });

  expect(h.requests.slice(before).map((request) => request.url)).toEqual([
    "/folders",
    "/folders",
  ]);
  expect(h.cache.getQueryState(folderKey(child))?.isInvalidated).toBe(true);
  expect(h.cache.getQueryState(["auth"])?.isInvalidated).toBe(false);
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(false);

  const calls = h.requests.length;

  observer.setOptions({
    ...query.options,
    queryKey: query.queryKey,
    enabled: true,
  });

  expect(h.requests).toHaveLength(calls);
});

test("logout begins cache retirement immediately, including unconfirmed server logout", async () => {
  const h = await setup();

  h.cache.setQueryData(folderKey(null), listing);

  const operation = startAuth("logout");

  expect(h.cache.getQueryData(folderKey(null))).toBeUndefined();
  expect(useAuthStore.getState().logout).toBe("pending");

  operation.release();

  await finishLogout(operation, false);

  expect(useAuthStore.getState().logout).toBe("unconfirmed");
  expect(renderHook(() => useFolder(null), h.cache).folderData).toBeUndefined();
  expect(h.requests).toHaveLength(0);
});

test("uncertain auth failure without a version change still retires private cache", async () => {
  const h = await setup();
  const version = coordination.sessionVersion;

  h.cache.setQueryData(folderKey(null), listing);

  await failCredentials(new Error(), version);

  expect(coordination.sessionVersion).toBe(version);
  expect(useAuthStore.getState().status).toBe("error");
  expect(h.cache.getQueryData(folderKey(null))).toBeUndefined();
});

test("same-user token/persistence updates preserve cache, direct user replacement clears it", async () => {
  const h = await setup();

  h.cache.setQueryData(folderKey(null), listing);
  useAuthStore.getState().update({
    accessToken: "new.synthetic.token",
    persistence: "available",
  });

  expect(h.cache.getQueryData(folderKey(null))).toEqual(listing);

  useAuthStore.getState().update({
    user: {
      ...response.user,
      id: other,
    },
  });

  expect(h.cache.getQueryData(folderKey(null))).toBeUndefined();
});

test("provider boundary aborts owner A GET and owner B reuses the exact key safely", async () => {
  const h = await setup();
  const waiting = deferred<void>();
  const started = deferred<void>();
  let signal: AbortSignal | undefined;

  http.defaults.adapter = async (config) => {
    signal = config.signal as AbortSignal;
    started.resolve();

    await waiting.promise;

    return {
      config,
      status: 200,
      statusText: "fixture",
      headers: {},
      data: {
        ...listing,
        folders: [folder],
      },
    };
  };

  const first = observeFolder(h.cache, null).observer.refetch();

  await started.promise;
  await h.adopt();

  expect(signal?.aborted).toBe(true);

  h.reply.data = {
    ...listing,
    folders: [
      {
        ...folder,
        name: "Owner B",
      },
    ],
  };
  http.defaults.adapter = async (config) => ({
    config,
    status: 200,
    statusText: "fixture",
    headers: {},
    data: h.reply.data,
  });

  const second = observeFolder(h.cache, null);

  await second.observer.refetch();
  waiting.resolve();
  await first;

  expect(h.cache.getQueryData(folderKey(null))).toEqual(h.reply.data);
  expect(h.cache.getQueryCache().getAll()).toHaveLength(1);
});

test("explicit lease guard rejects a late response even when the HTTP seam ignores cancellation", async () => {
  const h = await setup();
  const waiting = deferred<void>();

  h.close();

  http.get = (async () => {
    await waiting.promise;

    return {
      status: 200,
      data: listing,
    };
  }) as typeof http.get;

  const { observer } = observeFolder(h.cache, null);
  const pending = observer.refetch();
  const snapshot = folderSession();

  useAuthStore.getState().update({
    ...initialAuth,
  });

  expect(() => checkFolderSession(snapshot)).toThrow();
  waiting.resolve();
  await pending;

  expect(h.cache.getQueryData(folderKey(null))).toBeUndefined();
});

test.each(["create", "edit"] as const)(
  "late %s cannot invalidate a replacement account's same-key cache",
  async (operation) => {
    const h = await setup();
    const waiting = deferred<void>();
    const started = deferred<void>();

    http.defaults.adapter = async (config) => {
      h.requests.push(config);
      started.resolve();

      await waiting.promise;

      return {
        config,
        status: operation === "create" ? 201 : 200,
        statusText: "fixture",
        headers: {},
        data: folder,
      };
    };

    const creation = renderHook(() => useCreateFolder(), h.cache);
    const editing = renderHook(() => useEditFolder(folder), h.cache);
    const pending = (
      operation === "create"
        ? creation.createFolder({
            name: "Name",
            parent_id: null,
          })
        : editing.editFolder({
            name: "Name",
          })
    ).catch(() => undefined);

    await started.promise;
    await h.adopt();

    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].signal?.aborted).toBe(true);

    const value = {
      ...listing,
      folders: [
        {
          ...folder,
          name: "Owner B",
        },
      ],
    };

    h.cache.setQueryData(folderKey(null), value);
    waiting.resolve();
    await pending;

    expect(h.cache.getQueryData(folderKey(null))).toEqual(value);
    expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(false);
  },
);

test("confirmed edit refetches selected title and leaves parent stale until its next visit", async () => {
  const h = await setup();
  let canonical = folder;

  http.defaults.adapter = async (config) => {
    h.requests.push(config);

    if (config.method === "patch") {
      canonical = {
        ...folder,
        name: "Renamed folder",
      };

      return {
        config,
        status: 200,
        statusText: "fixture",
        headers: {},
        data: canonical,
      };
    }

    return {
      config,
      status: 200,
      statusText: "fixture",
      headers: {},
      data:
        config.url === "/folders"
          ? {
              ...listing,
              folders: [canonical],
            }
          : {
              ...listing,
              folder: canonical,
            },
    };
  };

  h.cache.setQueryData(folderKey(null), {
    ...listing,
    folders: [folder],
  });

  const selected = observeFolder(h.cache, id);

  selected.observer.setOptions({
    ...selected.query.options,
    queryKey: selected.query.queryKey,
    enabled: true,
  });

  cleanups.push(selected.observer.subscribe(() => undefined));
  await selected.observer.refetch();

  await renderHook(() => useEditFolder(folder), h.cache).editFolder({
    name: "Renamed folder",
  });

  expect(
    renderHook(() => useFolder(id), h.cache).folderData?.folder?.name,
  ).toBe("Renamed folder");
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);
  expect(
    h.requests.filter((request) => request.url === "/folders"),
  ).toHaveLength(0);

  await observeFolder(h.cache, null).observer.refetch();

  expect(
    renderHook(() => useFolder(null), h.cache).folderData?.folders[0].name,
  ).toBe("Renamed folder");
});

test("fresh location revisits reuse cache, stale revisits fetch without additional retry layers", async () => {
  const h = await setup();

  h.cache.setQueryData(folderKey(null), listing);

  const fresh = observeFolder(h.cache, null);

  fresh.observer.setOptions({
    ...fresh.query.options,
    queryKey: fresh.query.queryKey,
    enabled: true,
  });

  const unsubscribe = fresh.observer.subscribe(() => undefined);

  expect(h.requests).toHaveLength(0);
  unsubscribe();

  h.cache.setQueryData(folderKey(null), listing, {
    updatedAt: Date.now() - 60_001,
  });

  const stale = observeFolder(h.cache, null);

  stale.observer.setOptions({
    ...stale.query.options,
    queryKey: stale.query.queryKey,
    enabled: true,
  });

  cleanups.push(stale.observer.subscribe(() => undefined));
  await stale.observer.refetch();

  expect(h.requests).toHaveLength(1);
});

test("uncertain save marks drive stale without replay or automatic reconciliation; explicit GET can reconcile", async () => {
  const h = await setup(500, {
    code: "POSTGRES_OPERATION_FAILED",
    error: "private diagnostic",
  });

  h.cache.setQueryData(folderKey(null), listing);
  h.cache.setQueryData(["auth"], "retain");

  const error = await renderHook(() => useCreateFolder(), h.cache)
    .createFolder({
      name: "Maybe created",
      parent_id: null,
    })
    .catch((failure: unknown) => failure);

  expect(error instanceof FolderFailure && error.uncertain).toBe(true);
  expect(h.requests).toHaveLength(1);
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);
  expect(h.cache.getQueryState(["auth"])?.isInvalidated).toBe(false);

  h.reply.status = 200;
  h.reply.data = {
    ...listing,
    folders: [folder],
  };

  const reconciled = await observeFolder(h.cache, null).hook.refreshFolder();

  expect(reconciled?.folders).toEqual([folder]);
  expect(h.requests.map((request) => request.method)).toEqual(["post", "get"]);
});
