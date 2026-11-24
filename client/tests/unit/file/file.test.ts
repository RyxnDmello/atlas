import { afterEach, expect, test } from "bun:test";
import { AxiosError } from "axios";
import { QueryObserver } from "@tanstack/react-query";

import "../auth/environment";

import useUploadFile from "@hooks/file/useUploadFile";
import useEditFile from "@hooks/file/useEditFile";
import useDeleteFile from "@hooks/file/useDeleteFile";
import useReadFile from "@hooks/file/useReadFile";
import useFileRecovery from "@hooks/file/useFileRecovery";

import http from "@services/http/axios";
import { fileLifetime } from "@services/file/lifetime";
import { coordination, startAuth } from "@services/auth/auth";

import {
  extensions,
  sourceSchema,
  fileFormSchema,
  filePatchSchema,
  type FileUpload,
} from "@schemas/file/file";

import {
  fileBody,
  fileChanges,
  fileError,
  fileFeedback,
  FileFailure,
} from "@utils/file/file";
import { folderKey } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

import { deferred } from "../auth/fixtures";
import {
  harness,
  renderHook,
  file,
  folder,
  id,
  child,
  listing,
  observeFolder,
} from "../folder/fixtures";

const originalCoordination = {
  ...coordination,
};
const originalStore = useAuthStore.getState();
const originalAdapter = http.defaults.adapter;
const originalMethods = {
  post: http.post,
  patch: http.patch,
  delete: http.delete,
};
const cleanups: (() => void)[] = [];

afterEach(() => {
  cleanups.splice(0).forEach((cleanup) => cleanup());
  Object.assign(coordination, originalCoordination);
  useAuthStore.setState(originalStore);
  http.defaults.adapter = originalAdapter;
  Object.assign(http, originalMethods);
});

const setup = async (status = 201, data: unknown = file) => {
  const h = await harness({
    status,
    data,
  });

  cleanups.push(h.close);

  return h;
};

const upload = (): FileUpload => ({
  file: new File(["# real bytes\n"], "source.MD", {
    type: "text/markdown",
  }),
  name: " Display name ",
  description: " ",
});

test("file metadata matches backend Unicode alphabet, code-point lengths and null/omitted rules", () => {
  expect(
    fileFormSchema.parse({
      name: "  Report [1] & 测试  ",
      description: "  note  ",
    }),
  ).toEqual({
    name: "Report [1] & 测试",
    description: "note",
  });

  for (const name of [
    "",
    " ",
    "slash/name",
    "bad:name",
    "a".repeat(101),
    "combining e\u0301",
    "emoji😀",
  ]) {
    expect(
      fileFormSchema.safeParse({
        name,
        description: "",
      }).success,
    ).toBe(false);
  }

  expect(
    fileFormSchema.safeParse({
      name: "𐐀".repeat(100),
      description: "😀".repeat(250),
    }).success,
  ).toBe(true);
  expect(
    fileFormSchema.safeParse({
      name: "Valid",
      description: "😀".repeat(251),
    }).success,
  ).toBe(false);
  expect(
    filePatchSchema.parse({
      description: " ",
    }),
  ).toEqual({
    description: null,
  });
  expect(filePatchSchema.safeParse({}).success).toBe(false);
  expect(
    filePatchSchema.safeParse({
      name: null,
    }).success,
  ).toBe(false);
  expect(
    filePatchSchema.safeParse({
      folder_id: id,
    }).success,
  ).toBe(false);
  expect(
    fileChanges(file, {
      name: file.name,
      description: " ",
    }),
  ).toEqual({});
  expect(
    fileChanges(
      {
        ...file,
        description: "old",
      },
      {
        name: " Rename ",
        description: " ",
      },
    ),
  ).toEqual({
    name: "Rename",
    description: null,
  });
});

test("source validation accepts the actual supported suffixes, rejects empty/unsupported input and has no invented size cap", () => {
  for (const extension of extensions) {
    expect(
      sourceSchema.safeParse(
        new File(["data"], `source${extension.toUpperCase()}`),
      ).success,
    ).toBe(true);
  }

  for (const source of [
    null,
    "source.pdf",
    new File([], "empty.pdf"),
    new File(["x"], "source.exe"),
    new File(["x"], ".pdf"),
    new File(["x"], "noextension"),
  ]) {
    expect(sourceSchema.safeParse(source).success).toBe(false);
  }
});

test.each([null, id])(
  "multipart destination %s contains only actual bytes and canonical fields",
  async (parent) => {
    const input = upload();
    const body = fileBody(input, parent);

    expect(Array.from(body.keys())).toEqual(
      parent ? ["file", "name", "folder_id"] : ["file", "name"],
    );
    expect(body.get("name")).toBe("Display name");
    expect(body.getAll("folder_id")).toEqual(parent ? [parent] : []);

    const source = body.get("file");

    expect(source).toBeInstanceOf(File);

    if (!(source instanceof File)) {
      throw new Error("Missing source fixture.");
    }

    expect(source.name).toBe("source.MD");
    expect(await source.text()).toBe("# real bytes\n");
    expect(
      fileBody(
        {
          ...input,
          description: " note ",
        },
        parent,
      ).get("description"),
    ).toBe("note");
    expect(() => fileBody(input, "invalid")).toThrow();
  },
);

test.each([null, id])(
  "confirmed upload at %s sends one protected POST without a manually selected boundary",
  async (parent) => {
    const h = await setup(201, {
      ...file,
      folder_id: parent,
    });
    const action = renderHook(() => useUploadFile(parent), h.cache);

    h.cache.setQueryData(folderKey(parent), {
      ...listing,
    });
    h.cache.setQueryData(folderKey(child), {
      ...listing,
    });
    h.cache.setQueryData(["auth", "untouched"], "keep");

    expect(await action.uploadFile(upload())).toEqual({
      ...file,
      folder_id: parent,
    });
    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].method).toBe("post");
    expect(h.requests[0].url).toBe("/files");
    expect(h.requests[0].isProtected).toBe(true);
    expect(h.requests[0].data).toBeInstanceOf(FormData);
    expect(h.requests[0].headers.get("Content-Type")).not.toContain(
      "multipart/form-data",
    );
    expect(h.cache.getQueryState(folderKey(parent))?.isInvalidated).toBe(true);
    expect(h.cache.getQueryState(folderKey(child))?.isInvalidated).toBe(true);
    expect(h.cache.getQueryState(["auth", "untouched"])?.isInvalidated).toBe(
      false,
    );
    expect(h.cache.getMutationCache().getAll()[0].options.retry).toBe(false);
  },
);

test("confirmed upload actively refetches the mounted listing and inactive locations refetch on revisit", async () => {
  const h = await setup();
  const input = upload();
  const active = observeFolder(h.cache, null);
  const inactive = observeFolder(h.cache, id);

  h.cache.setQueryData(folderKey(null), listing);
  h.cache.setQueryData(folderKey(id), {
    ...listing,
    folder,
  });

  active.observer.setOptions({
    ...active.query.options,
    queryKey: active.query.queryKey,
    enabled: true,
  });

  const stop = active.observer.subscribe(() => undefined);

  cleanups.push(stop);

  const methods: string[] = [];

  http.defaults.adapter = async (config) => {
    methods.push(`${config.method} ${config.url}`);

    return {
      config,
      status: config.method === "post" ? 201 : 200,
      statusText: "fixture",
      headers: {},
      data:
        config.method === "post"
          ? {
              ...file,
              folder_id: null,
            }
          : config.url === "/folders"
            ? {
                ...listing,
                files: [
                  {
                    ...file,
                    folder_id: null,
                  },
                ],
              }
            : {
                ...listing,
                folder,
              },
    };
  };

  await renderHook(() => useUploadFile(null), h.cache).uploadFile(input);

  expect(methods).toEqual(["post /files", "get /folders"]);
  expect(h.cache.getQueryData(folderKey(null))).toEqual({
    ...listing,
    files: [
      {
        ...file,
        folder_id: null,
      },
    ],
  });
  expect(h.cache.getQueryState(folderKey(id))?.isInvalidated).toBe(true);
  expect(inactive.observer.options.staleTime).toBe(60_000);

  await inactive.hook.refreshFolder();

  expect(methods).toEqual([
    "post /files",
    "get /folders",
    `get /folders/${id}`,
  ]);
});

test.each([
  [200, file],
  [
    201,
    {
      ...file,
      status: "processing",
    },
  ],
  [
    201,
    {
      ...file,
      status: "deleting",
    },
  ],
  [
    201,
    {
      ...file,
      folder_id: child,
    },
  ],
  [
    201,
    {
      ...file,
      id: "invalid",
    },
  ],
  [
    201,
    {
      ...file,
      status: "failed",
    },
  ],
  [201, {}],
  [
    500,
    {
      error: "private diagnostic",
      code: "INTERNAL_SERVER_ERROR",
    },
  ],
])(
  "unconfirmed upload status %s never inserts a row, retries or refetches automatically",
  async (status, data) => {
    const h = await setup(Number(status), data);

    h.cache.setQueryData(folderKey(id), listing);

    const observed = observeFolder(h.cache, id);

    observed.observer.setOptions({
      ...observed.query.options,
      queryKey: observed.query.queryKey,
      enabled: true,
    });

    const stop = observed.observer.subscribe(() => undefined);

    cleanups.push(stop);

    const action = renderHook(() => useUploadFile(id), h.cache);

    await expect(action.uploadFile(upload())).rejects.toBeInstanceOf(
      FileFailure,
    );
    expect(h.requests).toHaveLength(1);
    expect(h.cache.getQueryData(folderKey(id))).toEqual(listing);
    expect(h.cache.getQueryState(folderKey(id))?.isInvalidated).toBe(true);
  },
);

test("pending upload guards same-tick duplicates; lost acknowledgement stays uncertain with no automatic reconciliation", async () => {
  const h = await setup();
  const started = deferred<void>();
  const release = deferred<void>();
  let count = 0;

  http.defaults.adapter = async () => {
    count++;
    started.resolve();
    await release.promise;

    throw new Error("acknowledgement lost after hypothetical commit");
  };

  const action = renderHook(() => useUploadFile(id), h.cache);
  const first = action.uploadFile(upload()).catch(fileError);

  await started.promise;

  await expect(action.uploadFile(upload())).rejects.toMatchObject({
    code: "REQUEST_PENDING",
  });
  expect(count).toBe(1);

  release.resolve();

  const error = await first;

  expect(error).toBeInstanceOf(FileFailure);
  expect(fileFeedback(error)).toContain("outcome is unknown");
  expect(count).toBe(1);
});

test("ready metadata PATCH sends only changed fields and validates identity/source facts", async () => {
  const h = await setup(200, {
    ...file,
    name: "Renamed",
    description: null,
  });
  const action = renderHook(
    () =>
      useEditFile({
        ...file,
        description: "old",
      }),
    h.cache,
  );

  expect(
    await action.editFile({
      name: " Renamed ",
      description: null,
    }),
  ).toEqual({
    ...file,
    name: "Renamed",
    description: null,
  });
  expect(h.requests).toHaveLength(1);
  expect(h.requests[0].method).toBe("patch");
  expect(h.requests[0].url).toBe(`/files/${file.id}`);
  expect(JSON.parse(h.requests[0].data)).toEqual({
    name: "Renamed",
    description: null,
  });
});

test.each(["patch", "delete"] as const)(
  "pending %s rejects duplicates and a lost acknowledgement never replays",
  async (kind) => {
    const h = await setup();
    const started = deferred<void>();
    const release = deferred<void>();
    let count = 0;

    http.defaults.adapter = async () => {
      count++;
      started.resolve();
      await release.promise;

      throw new Error("acknowledgement lost");
    };

    const action = renderHook(
      () => ({
        edit: useEditFile(file),
        removal: useDeleteFile(file),
      }),
      h.cache,
    );

    const submit = () =>
      kind === "patch"
        ? action.edit.editFile({
            description: null,
          })
        : action.removal.deleteFile();

    const first = submit().catch(fileError);

    await started.promise;

    await expect(submit()).rejects.toMatchObject({
      code: "REQUEST_PENDING",
    });
    expect(count).toBe(1);

    release.resolve();

    expect(await first).toMatchObject({
      uncertain: true,
    });
    expect(count).toBe(1);
  },
);

test.each(["patch", "delete"] as const)(
  "confirmed %s refetches active drive queries and preserves unrelated cache",
  async (kind) => {
    const h = await setup();

    h.cache.setQueryData(folderKey(id), {
      ...listing,
      folder,
      files: [file],
    });
    h.cache.setQueryData(folderKey(null), listing);
    h.cache.setQueryData(["auth", "keep"], "untouched");

    const active = observeFolder(h.cache, id);

    active.observer.setOptions({
      ...active.query.options,
      queryKey: active.query.queryKey,
      enabled: true,
    });
    cleanups.push(active.observer.subscribe(() => undefined));

    const methods: string[] = [];

    http.defaults.adapter = async (config) => {
      methods.push(`${config.method} ${config.url}`);

      return {
        config,
        status: config.method === "delete" ? 204 : 200,
        statusText: "fixture",
        headers: {},
        data:
          config.method === "get"
            ? {
                ...listing,
                folder,
                files:
                  kind === "delete"
                    ? []
                    : [
                        {
                          ...file,
                          name: "New",
                        },
                      ],
              }
            : {
                ...file,
                name: "New",
              },
      };
    };

    if (kind === "patch") {
      await renderHook(() => useEditFile(file), h.cache).editFile({
        name: "New",
      });
    } else {
      await renderHook(() => useDeleteFile(file), h.cache).deleteFile();
    }

    expect(methods).toEqual([
      `${kind} /files/${file.id}`,
      `get /folders/${id}`,
    ]);
    expect(h.cache.getQueryData(folderKey(id))).toEqual({
      ...listing,
      folder,
      files:
        kind === "delete"
          ? []
          : [
              {
                ...file,
                name: "New",
              },
            ],
    });
    expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);
    expect(h.cache.getQueryState(["auth", "keep"])?.isInvalidated).toBe(false);
  },
);

test("a canonical deleting file requires each retry explicitly, even after repeated failures", async () => {
  const h = await setup(503, {});
  const action = renderHook(
    () =>
      useDeleteFile({
        ...file,
        status: "deleting",
      }),
    h.cache,
  );

  expect(h.requests).toHaveLength(0);
  await expect(action.deleteFile()).rejects.toMatchObject({
    uncertain: true,
  });
  expect(h.requests).toHaveLength(1);
  await expect(action.deleteFile()).rejects.toMatchObject({
    uncertain: true,
  });
  expect(h.requests).toHaveLength(2);
  expect(h.requests.every((request) => request.method === "delete")).toBe(true);
});

test.each(["processing", "deleting"] as const)(
  "metadata editing rejects canonical %s without HTTP",
  async (status) => {
    const h = await setup();

    await expect(
      renderHook(
        () =>
          useEditFile({
            ...file,
            status,
          }),
        h.cache,
      ).editFile({
        name: "New",
      }),
    ).rejects.toMatchObject({
      code: "FILE_NOT_READY",
    });
    expect(h.requests).toHaveLength(0);
  },
);

test.each([
  {},
  {
    name: null,
  },
  {
    status: "ready",
  },
  {
    folder_id: null,
  },
])("invalid or unchanged PATCH %j sends nothing", async (patch) => {
  const h = await setup();
  const action = renderHook(() => useEditFile(file), h.cache);

  // External input is deliberately invalid; exercise the runtime validator.

  await expect(action.editFile(patch as never)).rejects.toThrow();
  expect(h.requests).toHaveLength(0);
});

test.each([
  {
    id: child,
  },
  {
    folder_id: null,
  },
  {
    original_name: "replacement.pdf",
  },
  {
    extension: ".pdf",
  },
  {
    size_bytes: 999,
  },
  {
    status: "deleting",
  },
  {
    created_at: "2020-01-01T00:00:00Z",
  },
])("PATCH rejects mismatched canonical response %j", async (change) => {
  const h = await setup(200, {
    ...file,
    ...change,
  });

  await expect(
    renderHook(() => useEditFile(file), h.cache).editFile({
      name: "New",
    }),
  ).rejects.toMatchObject({
    uncertain: true,
  });
  expect(h.requests).toHaveLength(1);
});

test.each([400, 404, 409, 422, 500])(
  "PATCH HTTP %s never replays",
  async (status) => {
    const h = await setup(status, {
      error: "safe",
      code: status === 409 ? "FILE_NOT_READY" : "UNPROCESSABLE_ENTITY",
    });

    await expect(
      renderHook(() => useEditFile(file), h.cache).editFile({
        description: null,
      }),
    ).rejects.toMatchObject({
      status,
    });
    expect(h.requests).toHaveLength(1);
  },
);

test.each(["ready", "deleting"] as const)(
  "explicit deletion of %s accepts only one bodyless 204",
  async (status) => {
    const h = await setup(204, "");

    h.cache.setQueryData(folderKey(id), listing);

    await renderHook(
      () =>
        useDeleteFile({
          ...file,
          status,
        }),
      h.cache,
    ).deleteFile();

    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].method).toBe("delete");
    expect(h.requests[0].url).toBe(`/files/${file.id}`);
    expect(h.requests[0].data).toBeUndefined();
    expect(h.cache.getQueryState(folderKey(id))?.isInvalidated).toBe(true);
  },
);

test("processing cannot be deleted and creating a delete hook dispatches no request", async () => {
  const h = await setup(204, "");

  renderHook(() => useDeleteFile(file), h.cache);

  expect(h.requests).toHaveLength(0);
  await expect(
    renderHook(
      () =>
        useDeleteFile({
          ...file,
          status: "processing",
        }),
      h.cache,
    ).deleteFile(),
  ).rejects.toMatchObject({
    code: "FILE_NOT_READY",
  });
  expect(h.requests).toHaveLength(0);
});

test.each([200, 202, 404, 409, 500])(
  "DELETE %s never claims success or automatically retries",
  async (status) => {
    const h = await setup(status, "");

    await expect(
      renderHook(() => useDeleteFile(file), h.cache).deleteFile(),
    ).rejects.toMatchObject({
      status,
    });
    expect(h.requests).toHaveLength(1);
  },
);

test.each(["ready", "processing", "deleting", "absent", "unavailable"])(
  "explicit reconciliation reads canonical %s without replaying a write",
  async (status) => {
    const h = await setup(
      status === "absent" ? 404 : status === "unavailable" ? 503 : 200,
      {
        ...file,
        status,
      },
    );
    let refreshed = 0;

    const refresh = async () => {
      refreshed++;

      return listing;
    };

    const recovery = renderHook(
      () =>
        useFileRecovery({
          file,
          refresh,
        }),
      h.cache,
    );

    expect(h.requests).toHaveLength(0);

    const result = await recovery.refreshFile();

    expect(h.requests).toHaveLength(1);
    expect(h.requests[0].method).toBe("get");
    expect(h.requests[0].url).toBe(`/files/${file.id}`);
    expect(result).toEqual(
      status === "absent"
        ? null
        : status === "unavailable"
          ? undefined
          : {
              ...file,
              status,
            },
    );
    expect(refreshed).toBe(status === "unavailable" ? 0 : 1);
  },
);

test("read reconciliation validates identity, handles actual Axios 404 and rejects invalid UUID before dispatch", async () => {
  const h = await setup(200, {
    ...file,
    id: child,
  });
  const action = renderHook(() => useReadFile(), h.cache);

  await expect(action.readFile(file.id)).rejects.toMatchObject({
    code: "INVALID_RESPONSE",
  });
  await expect(action.readFile("invalid")).rejects.toThrow();
  expect(h.requests).toHaveLength(1);

  http.defaults.adapter = async (config) => {
    throw new AxiosError("not found", "ERR_BAD_REQUEST", config, undefined, {
      config,
      status: 404,
      statusText: "fixture",
      headers: {},
      data: {
        error: "File not found",
        code: "FILE_NOT_FOUND",
      },
    });
  };

  expect(await action.readFile(file.id)).toBeNull();
});

test.each(["upload", "patch", "delete"] as const)(
  "late owner-A %s cannot publish or invalidate/refetch owner B's same-key cache",
  async (kind) => {
    const h = await setup();
    const started = deferred<void>();
    const release = deferred<void>();
    let signal: AbortSignal | undefined;
    let requests = 0;

    http.defaults.adapter = async (config) => {
      requests++;
      signal = config.signal as AbortSignal;
      started.resolve();
      await release.promise;

      return {
        config,
        status: kind === "upload" ? 201 : kind === "patch" ? 200 : 204,
        statusText: "fixture",
        headers: {},
        data: file,
      };
    };

    const action = renderHook(
      () => ({
        upload: useUploadFile(id),
        patch: useEditFile(file),
        removal: useDeleteFile(file),
      }),
      h.cache,
    );
    const operation = (
      kind === "upload"
        ? action.upload.uploadFile(upload())
        : kind === "patch"
          ? action.patch.editFile({
              name: "New",
            })
          : action.removal.deleteFile()
    ).then(
      () => "published",
      () => "retired",
    );

    await started.promise;
    await h.adopt();

    expect(signal?.aborted).toBe(true);

    const sentinel = {
      ...listing,
      files: [
        {
          ...file,
          name: "Owner B",
        },
      ],
    };

    h.cache.setQueryData(folderKey(null), sentinel);

    const observer = new QueryObserver(h.cache, {
      queryKey: folderKey(null),
      queryFn: async () => {
        throw new Error("Owner A must not trigger B refetch");
      },
      staleTime: 60_000,
    });
    const stop = observer.subscribe(() => undefined);

    cleanups.push(stop);
    release.resolve();

    expect(await operation).toBe("retired");
    expect(h.cache.getQueryData(folderKey(null))).toEqual(sentinel);
    expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(false);
    expect(requests).toBe(1);
  },
);

test.each(["upload", "patch", "delete"] as const)(
  "explicit %s lease guard blocks a late response even if transport ignores cancellation",
  async (kind) => {
    const h = await setup();
    const started = deferred<void>();
    const release = deferred<void>();
    let count = 0;

    const reply = async () => {
      count++;
      started.resolve();
      await release.promise;

      return {
        status: kind === "upload" ? 201 : kind === "patch" ? 200 : 204,
        data: file,
      };
    };

    http.post = reply as typeof http.post;
    http.patch = reply as typeof http.patch;
    http.delete = reply as typeof http.delete;

    const action = renderHook(
      () => ({
        upload: useUploadFile(id),
        edit: useEditFile(file),
        removal: useDeleteFile(file),
      }),
      h.cache,
    );
    const operation = (
      kind === "upload"
        ? action.upload.uploadFile(upload())
        : kind === "patch"
          ? action.edit.editFile({
              description: null,
            })
          : action.removal.deleteFile()
    ).then(
      () => "published",
      () => "retired",
    );

    await started.promise;
    await h.adopt();
    h.cache.setQueryData(folderKey(id), {
      ...listing,
      folder,
    });
    release.resolve();

    expect(await operation).toBe("retired");
    expect(count).toBe(1);
    expect(h.cache.getQueryState(folderKey(id))?.isInvalidated).toBe(false);
  },
);

test("retiring a route lifetime aborts pending transport, marks old data stale once, and blocks completion after remount", async () => {
  const h = await setup();

  h.cache.setQueryData(folderKey(null), listing);

  const lifetime = fileLifetime(h.cache);
  const request = lifetime.begin();

  lifetime.retire();

  expect(request.controller.signal.aborted).toBe(true);
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(true);

  h.cache.setQueryData(folderKey(null), {
    ...listing,
    files: [file],
  });
  lifetime.activate();

  expect(() => lifetime.check(request)).toThrow();
  await expect(lifetime.invalidate(request, true)).rejects.toThrow();
  expect(h.cache.getQueryState(folderKey(null))?.isInvalidated).toBe(false);

  lifetime.end(request);
});

test("logout-start retires writes, and unauthenticated calls never dispatch", async () => {
  const h = await setup();
  const lifetime = fileLifetime(h.cache);
  const request = lifetime.begin();
  const logout = startAuth("logout");

  await logout.clearing;

  expect(request.controller.signal.aborted).toBe(true);
  expect(() => lifetime.check(request)).toThrow();
  await expect(
    renderHook(() => useUploadFile(null), h.cache).uploadFile(upload()),
  ).rejects.toThrow();
  expect(h.requests).toHaveLength(0);

  lifetime.end(request);
});
