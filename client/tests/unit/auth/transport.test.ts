import { afterEach, expect, test, spyOn } from "bun:test";
import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import "./environment";

import http from "@services/http/axios";
import { authAccess, type AuthAccess } from "@services/auth/auth";
import fetchClient from "@services/http/fetch";
import { protectedUrl, resolveUrl, trustedUrl } from "@/services/http/policy";

import { deferred, fixture, response } from "./fixtures";

const original = globalThis.fetch;
const originalAdapter = http.defaults.adapter;
const originalHeaders = http.defaults.headers;
const spies: ReturnType<typeof spyOn>[] = [];

const bindAuthority = (authority: AuthAccess) => {
  spies.push(
    spyOn(authAccess, "acquire").mockImplementation(authority.acquire),
  );
  spies.push(
    spyOn(authAccess, "current").mockImplementation(authority.current),
  );
  spies.push(
    spyOn(authAccess, "refresh").mockImplementation(authority.refresh),
  );
};

/** Only tests replace an adapter; production exports one real Axios instance. */
const axiosFixture = (authority: AuthAccess, raw: AxiosInstance) => {
  bindAuthority(authority);

  http.defaults.adapter = raw.defaults.adapter;
  http.defaults.headers = raw.defaults.headers;
  http.defaults.withCredentials = false;

  return http;
};

const fetchFixture = (authority: AuthAccess) => {
  bindAuthority(authority);

  return fetchClient;
};

afterEach(() => {
  globalThis.fetch = original;
  http.defaults.adapter = originalAdapter;
  http.defaults.headers = originalHeaders;

  for (const spy of spies.reverse()) {
    spy.mockRestore();
  }

  spies.length = 0;
});

type Kind = "axios" | "fetch";

interface RequestObservation {
  url: string;
  method: string;
  token: string | null;
  signal?: AbortSignal | null;
  headers: Headers;
}

interface Reply {
  status: number;
  body: unknown;
}

type Handler = (request: RequestObservation) => Promise<Reply>;

const harness = (
  kind: Kind,
  context: ReturnType<typeof fixture>,
  handler: Handler,
) => {
  if (kind === "fetch") {
    globalThis.fetch = Object.assign(
      async (input: string | URL | Request, init?: RequestInit) => {
        const headers = new Headers(init?.headers);

        const reply = await handler({
          url: String(input),
          method: init?.method ?? "GET",
          token: headers.get("Authorization"),
          signal: init?.signal,
          headers,
        });

        return new Response(JSON.stringify(reply.body), {
          status: reply.status,
        });
      },
      {
        preconnect: original.preconnect,
      },
    );

    const client = fetchFixture(context.session);

    return (path = "/files", method = "GET", signal?: AbortSignal) =>
      client.base(path, {
        method,
        signal,
        headers: {
          "X-Fixture": "preserved",
        },
      });
  }

  const client = axiosFixture(
    context.session,
    axios.create({
      baseURL: "http://localhost:8080",
      adapter: async (config: InternalAxiosRequestConfig) => {
        const headers = new Headers(
          config.headers.toJSON() as Record<string, string>,
        );

        const reply = await handler({
          url: resolveUrl(config.url ?? "", config.baseURL),
          method: config.method?.toUpperCase() ?? "GET",
          token: headers.get("Authorization"),
          signal: config.signal as AbortSignal | undefined,
          headers,
        });

        const result = {
          status: reply.status,
          statusText: "fixture",
          data: reply.body,
          headers: {},
          config,
        };

        if (reply.status >= 400) {
          throw new AxiosError(
            "fixture",
            "ERR_BAD_REQUEST",
            config,
            undefined,
            result,
          );
        } else {
          return result;
        }
      },
    }),
  );

  return (path = "/files", method = "GET", signal?: AbortSignal) =>
    client.request({
      url: path,
      method,
      signal,
      timeout: 2000,
      headers: {
        "X-Fixture": "preserved",
      },
    });
};

const invalid: Reply = {
  status: 401,
  body: {
    error: "Invalid access",
    code: "INVALID_ACCESS_TOKEN",
  },
};

const success: Reply = {
  status: 200,
  body: {
    ok: true,
  },
};

test.each(["axios", "fetch"] as const)(
  "%s waits for one restoration and attaches bearer only to trusted targets",
  async (kind) => {
    const reading = deferred<string | undefined>();

    const context = fixture(
      {},
      {
        load: () => reading.promise,
      },
    );

    const observations: RequestObservation[] = [];

    const send = harness(kind, context, async (request) => {
      observations.push(request);

      return success;
    });

    const first = send();
    const second = send("/folders");

    await Bun.sleep(1);

    expect(observations.length).toBe(0);

    reading.resolve("recovered");

    await Promise.all([first, second]);

    expect(context.calls).toEqual(["current"]);
    expect(observations.map((item) => item.token)).toEqual([
      "Bearer recovered",
      "Bearer recovered",
    ]);

    await send("https://external.example.test/files");

    await send("/auth/refresh", "POST");

    await send("/system/health");

    expect(observations.slice(2).every((item) => item.token === null)).toBe(
      true,
    );
  },
);

test.each(["axios", "fetch"] as const)(
  "%s shares three expired GETs, replays once and preserves options",
  async (kind) => {
    const pending = deferred<typeof response>();
    let refreshes = 0;

    const context = fixture({
      refresh: () => {
        refreshes++;

        return pending.promise;
      },
    });

    await context.session.adopt(response);

    const observations: RequestObservation[] = [];

    const send = harness(kind, context, async (request) => {
      observations.push(request);

      expect(request.headers.get("X-Fixture")).toBe("preserved");

      return request.token === `Bearer ${response.access_token}`
        ? invalid
        : success;
    });

    const owner = new AbortController();
    const requests = [send("/files", "GET", owner.signal), send(), send()];

    await Bun.sleep(5);

    expect(refreshes).toBe(1);
    expect(observations).toHaveLength(3);

    pending.resolve({
      ...response,
      access_token: "renewed",
    });

    await Promise.all(requests);

    expect(observations).toHaveLength(6);
    expect(
      observations.slice(3).every((item) => item.token === "Bearer renewed"),
    ).toBe(true);
    expect(
      observations.filter((item) => item.signal === owner.signal),
    ).toHaveLength(2);
  },
);

test.each(["axios", "fetch"] as const)(
  "%s stale delayed 401 reuses newer token without second rotation",
  async (kind) => {
    const late = deferred<Reply>();

    const context = fixture({
      refresh: async () => {
        context.calls.push("refresh");

        return {
          ...response,
          access_token: "renewed",
        };
      },
    });

    await context.session.adopt(response);

    let calls = 0;

    const send = harness(kind, context, async (request) => {
      calls++;

      if (request.url.endsWith("/late") && request.token !== "Bearer renewed") {
        return late.promise;
      } else {
        return request.token === "Bearer renewed" ? success : invalid;
      }
    });

    const delayed = send("/late");

    await send();

    late.resolve(invalid);

    await delayed;

    expect(context.calls).toEqual(["refresh"]);
    expect(calls).toBe(4);
  },
);

test.each(["axios", "fetch"] as const)(
  "%s second invalid GET stops after one retry",
  async (kind) => {
    const context = fixture();

    await context.session.adopt(response);

    let calls = 0;

    const send = harness(kind, context, async () => {
      calls++;

      return invalid;
    });

    await Promise.allSettled([send()]);

    expect(calls).toBe(2);
    expect(context.calls).toEqual(["refresh"]);
  },
);

for (const kind of ["axios", "fetch"] as const) {
  test.each(["POST", "PATCH", "DELETE"])(
    `${kind} never replays %s after refresh`,
    async (method) => {
      const context = fixture();

      await context.session.adopt(response);

      let calls = 0;

      const send = harness(kind, context, async () => {
        calls++;

        return invalid;
      });

      await Promise.allSettled([send("/files/fixture/ask", method)]);

      expect(calls).toBe(1);
      expect(context.calls).toEqual(["refresh"]);
    },
  );

  test.each([
    [401, "INVALID_CREDENTIALS"],
    [401, "MALFORMED"],
    [403, "INVALID_ACCESS_TOKEN"],
    [500, "INVALID_ACCESS_TOKEN"],
  ])(
    `${kind} preserves status %i code %s without refresh`,
    async (status, code) => {
      const context = fixture();

      await context.session.adopt(response);

      const send = harness(kind, context, async () => ({
        status: Number(status),
        body:
          code === "MALFORMED"
            ? "invalid"
            : {
                error: "Failure",
                code,
              },
      }));

      await Promise.allSettled([send()]);

      expect(context.calls).toEqual([]);
    },
  );
}

test.each(["axios", "fetch"] as const)(
  "%s abort during restore detaches only its waiter",
  async (kind) => {
    const reading = deferred<string | undefined>();

    const context = fixture(
      {},
      {
        load: () => reading.promise,
      },
    );

    let requests = 0;

    const send = harness(kind, context, async () => {
      requests++;

      return success;
    });

    const owner = new AbortController();
    const waiting = send("/files", "GET", owner.signal);

    owner.abort();

    await expect(waiting).rejects.toThrow();

    expect(requests).toBe(0);

    reading.resolve("recovered");

    await send();

    expect(requests).toBe(1);
    expect(context.calls).toEqual(["current"]);
  },
);

test.each(["axios", "fetch"] as const)(
  "%s abort during refresh prevents replay while shared renewal completes",
  async (kind) => {
    const pending = deferred<typeof response>();

    const context = fixture({
      refresh: () => pending.promise,
    });

    await context.session.adopt(response);

    let requests = 0;

    const send = harness(kind, context, async () => {
      requests++;

      return invalid;
    });

    const owner = new AbortController();
    const request = send("/files", "GET", owner.signal);

    await Bun.sleep(5);

    owner.abort();

    await expect(request).rejects.toThrow();

    pending.resolve(response);

    await Bun.sleep(1);

    expect(requests).toBe(1);
    expect(context.session.getSnapshot().status).toBe("authenticated");
  },
);

test.each(["axios", "fetch"] as const)(
  "%s account change prevents replay of old account request",
  async (kind) => {
    const pending = deferred<Reply>();
    const context = fixture();

    await context.session.adopt(response);

    let requests = 0;

    const send = harness(kind, context, async () => {
      requests++;

      return pending.promise;
    });

    const request = send();

    await Bun.sleep(1);

    await context.session.adopt({
      ...response,
      access_token: "other.account",
    });

    pending.resolve(invalid);

    await Promise.allSettled([request]);

    expect(requests).toBe(1);
    expect(context.calls).toEqual([]);
  },
);

test("fetch inspects only cloned error body and leaves raw SSE response untouched", async () => {
  const context = fixture();

  await context.session.adopt(response);

  const client = fetchFixture(context.session);

  const error = new Response(JSON.stringify(invalid.body), {
    status: 401,
  });

  const stream = new Response("event: done\ndata: {}\n\n");
  let result = error;

  globalThis.fetch = Object.assign(async () => result, {
    preconnect: original.preconnect,
  });

  expect(await client.post("/files/fixture/ask", {})).toBe(error);
  expect(error.bodyUsed).toBe(false);
  expect(await error.json()).toEqual(invalid.body);

  result = stream;

  expect(await client.post("/files/fixture/ask", {})).toBe(stream);
  expect(stream.bodyUsed).toBe(false);
  expect(stream.body?.locked).toBe(false);
});

test("URL trust rejects external/userinfo/base-prefix lookalikes and bypasses controls", () => {
  expect(protectedUrl("https://external.test/files")).toBe(false);
  expect(protectedUrl("http://user@localhost:8080/files")).toBe(false);
  expect(protectedUrl("http://localhost:8080/auth")).toBe(false);
  expect(protectedUrl("http://localhost:8080/auth/refresh")).toBe(false);
  expect(protectedUrl("http://localhost:8080/files")).toBe(true);
  expect(
    protectedUrl(
      "http://localhost:8080/api/files",
      "http://localhost:8080/api",
    ),
  ).toBe(true);
  expect(
    protectedUrl(
      "http://localhost:8080/api-lookalike/files",
      "http://localhost:8080/api",
    ),
  ).toBe(false);
  expect(
    protectedUrl("http://localhost:8080/files", "http://localhost:8080/api"),
  ).toBe(false);
  expect(
    protectedUrl("http://localhost:8080/api/auth", "http://localhost:8080/api"),
  ).toBe(false);
  expect(resolveUrl("//external.test/files")).toBe(
    "http://external.test/files",
  );
});

test("Axios CancelToken cancels a restore waiter without dispatch or cancelling shared initialization", async () => {
  const reading = deferred<string | undefined>();

  const context = fixture(
    {},
    {
      load: () => reading.promise,
    },
  );

  let dispatched = false;

  const client = axiosFixture(
    context.session,
    axios.create({
      baseURL: "http://localhost:8080",
      adapter: async (config) => {
        dispatched = true;

        return {
          config,
          status: 200,
          statusText: "OK",
          headers: {},
          data: {},
        };
      },
    }),
  );

  const owner = axios.CancelToken.source();

  const waiting = client.get("/files", {
    cancelToken: owner.token,
  });

  await Promise.resolve();

  owner.cancel();

  try {
    await waiting;

    throw new Error("Expected cancellation");
  } catch (error) {
    expect(axios.isCancel(error)).toBe(true);
  }

  expect(dispatched).toBe(false);

  reading.resolve("recovered");

  await context.session.initialize();

  expect(context.session.getSnapshot().status).toBe("authenticated");
});

test.each(["axios", "fetch"] as const)(
  "%s isProtected false strips inherited Bearer, skips bootstrap/recovery and retains explicit cookies",
  async (kind) => {
    const context = fixture();
    let header: string | null = "unexpected";
    let cookies: unknown;

    if (kind === "axios") {
      const client = axiosFixture(
        context.session,
        axios.create({
          baseURL: "http://localhost:8080",
          headers: {
            Authorization: "Bearer inherited.fixture",
          },
          adapter: async (config) => {
            header = config.headers.get("Authorization")?.toString() ?? null;
            cookies = config.withCredentials;

            throw new AxiosError("fixture", undefined, config, undefined, {
              config,
              status: 401,
              statusText: "fixture",
              headers: {},
              data: {
                error: "fixture",
                code: "INVALID_ACCESS_TOKEN",
              },
            });
          },
        }),
      );

      await expect(
        client.get("/files", {
          isProtected: false,
          withCredentials: true,
        }),
      ).rejects.toThrow();

      expect(cookies).toBe(true);
    } else {
      globalThis.fetch = Object.assign(
        async (_input: string | URL | Request, init?: RequestInit) => {
          header = new Headers(init?.headers).get("Authorization");
          cookies = init?.credentials;

          return new Response(
            JSON.stringify({
              error: "fixture",
              code: "INVALID_ACCESS_TOKEN",
            }),
            {
              status: 401,
            },
          );
        },
        {
          preconnect: original.preconnect,
        },
      );

      const response = await fetchFixture(context.session).get("/files", {
        isProtected: false,
        credentials: "include",
        headers: {
          Authorization: "Bearer inherited.fixture",
        },
      });

      expect(response.status).toBe(401);
      expect(cookies).toBe("include");
    }

    expect(header).toBeNull();
    expect(context.calls).toEqual([]);
    expect(context.session.context.initialization).toBeUndefined();
  },
);

test.each(["axios", "fetch"] as const)(
  "%s isProtected true authenticates current-user reads and rejects off-origin before dispatch",
  async (kind) => {
    const context = fixture();

    await context.session.adopt(response);

    let dispatched = 0;
    let header: string | null = null;

    const raw = axios.create({
      baseURL: "http://localhost:8080",
      adapter: async (config) => {
        dispatched++;
        header = config.headers.get("Authorization")?.toString() ?? null;

        expect(config.withCredentials).toBe(false);

        return {
          config,
          status: 200,
          statusText: "fixture",
          headers: {},
          data: {},
        };
      },
    });

    globalThis.fetch = Object.assign(
      async (_input: string | URL | Request, init?: RequestInit) => {
        dispatched++;
        header = new Headers(init?.headers).get("Authorization");

        expect(init?.credentials).toBe("omit");

        return new Response("{}");
      },
      {
        preconnect: original.preconnect,
      },
    );

    const client =
      kind === "axios"
        ? axiosFixture(context.session, raw)
        : fetchFixture(context.session);

    await client.get("/auth", {
      isProtected: true,
    });

    expect<string | null>(header).toBe(`Bearer ${response.access_token}`);

    await expect(
      client.get("https://external.test/files", {
        isProtected: true,
      }),
    ).rejects.toThrow("not trusted");

    expect(dispatched).toBe(1);
    expect(context.calls).toEqual([]);
    expect(
      trustedUrl(
        "http://localhost:8080/api-lookalike/auth",
        "http://localhost:8080/api",
      ),
    ).toBe(false);
  },
);

test("Axios and fetch invalid-access requests share the same single refresh flight", async () => {
  let refreshes = 0;
  const pending = deferred<typeof response>();

  const context = fixture({
    refresh: () => {
      refreshes++;

      return pending.promise;
    },
  });

  await context.session.adopt(response);

  const handler: Handler = async (request) => ({
    status: request.token === "Bearer replacement" ? 200 : 401,
    body: {
      error: "fixture",
      code: "INVALID_ACCESS_TOKEN",
    },
  });

  const ordinary = harness("axios", context, handler);
  const streamed = harness("fetch", context, handler);
  const requests = [ordinary(), streamed(), ordinary(), streamed()];

  await Bun.sleep(5);

  expect(refreshes).toBe(1);

  pending.resolve({
    ...response,
    access_token: "replacement",
  });

  await Promise.all(requests);

  expect(refreshes).toBe(1);
  expect(context.session.context.store.getState().accessToken).toBe(
    "replacement",
  );
});
