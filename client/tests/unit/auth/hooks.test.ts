import { afterEach, expect, test } from "bun:test";
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import axios, { type AxiosRequestConfig } from "axios";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "./environment";

import useRegister from "@hooks/auth/useRegister";
import useResend from "@hooks/auth/useResend";
import useLogin from "@hooks/auth/useLogin";
import useVerify from "@hooks/auth/useVerify";
import useLogout from "@hooks/auth/useLogout";
import useAuth from "@hooks/auth/useAuth";

import http from "@services/http/axios";
import {
  coordination,
  onAuthBoundary,
  acquireAccess,
  refreshCredentials,
  startAuth,
  finishLogout,
} from "@services/auth/auth";
import { AuthFailure } from "@services/http/validate";

import { fixture, response, user, deferred, seedCredentials } from "./fixtures";

/** Executes real hook contracts using existing React SSR, without a DOM test library. */
const renderHook = <T>(hook: () => T, cache = new QueryClient()) => {
  let result: T | undefined;

  function Probe() {
    result = hook();

    return null;
  }

  renderToString(
    createElement(
      QueryClientProvider,
      {
        client: cache,
      },
      createElement(Probe),
    ),
  );

  if (result === undefined) {
    throw new Error("Hook did not render.");
  }

  return result;
};

interface Reply {
  status: number;
  data: unknown;
}

type MutationResult =
  | ReturnType<typeof useRegister>
  | ReturnType<typeof useResend>
  | ReturnType<typeof useVerify>
  | ReturnType<typeof useLogin>
  | ReturnType<typeof useLogout>;

type VerificationMutationResult =
  | ReturnType<typeof useRegister>
  | ReturnType<typeof useResend>
  | ReturnType<typeof useVerify>;

const originalContext = {
  ...coordination,
};
const originalAdapter = http.defaults.adapter;

afterEach(() => {
  Object.assign(coordination, originalContext);

  http.defaults.adapter = originalAdapter;
});

const harness = (reply?: Reply) => {
  const context = fixture();
  const configurations: AxiosRequestConfig[] = [];

  const raw = axios.create({
    baseURL: "http://localhost:8080",
    adapter: async (config) => {
      configurations.push(config);

      const path = config.url;

      return {
        config,
        status:
          reply?.status ??
          (path === "/auth/register"
            ? 201
            : path === "/auth/logout"
              ? 204
              : 200),
        statusText: "fixture",
        headers: {},
        data: reply
          ? reply.data
          : path === "/auth/logout"
            ? ""
            : path === "/auth"
              ? user
              : path === "/auth/register" || path === "/auth/resend"
                ? {
                    status: "verification_required",
                  }
                : response,
      };
    },
  });

  Object.assign(coordination, context.session.context);

  http.defaults.adapter = raw.defaults.adapter;

  return {
    ...context,
    session: {
      ...context.session,
      adopt: (value: typeof response) => seedCredentials(value, coordination),
    },
    client: http,
    configurations,
    context: coordination,
  };
};

test("real endpoint hooks dispatch only when invoked and own all six public contracts", async () => {
  const h = harness();
  const cache = new QueryClient();
  const register = renderHook(() => useRegister(), cache);
  const resend = renderHook(() => useResend(), cache);
  const login = renderHook(() => useLogin(), cache);
  const verify = renderHook(() => useVerify(), cache);
  const current = renderHook(() => useAuth(), cache);
  const logout = renderHook(() => useLogout(), cache);

  expect(h.configurations).toHaveLength(0);

  await register.register({
    name: " Synthetic User ",
    email: "FIXTURE@example.test",
    password: "synthetic-password",
  });
  await resend.resend({
    email: user.email,
  });

  expect(h.context.store.getState().status).toBe("restoring");
  expect(h.saved()).toBeUndefined();

  expect(
    await login.login({
      email: user.email,
      password: "synthetic-password",
    }),
  ).toEqual(user);
  expect(h.context.store.getState().accessToken).toBe(response.access_token);
  expect(h.saved()).toBe(response.access_token);

  await verify.verify({
    email: user.email,
    otp: "001234",
  });

  expect(h.configurations.some((c) => c.url === "/auth")).toBe(false);
  expect((await current.getAuth()).data).toEqual(user);

  cache.setQueryData(["private"], "previous account");

  const unsubscribe = onAuthBoundary(() => cache.clear(), h.context);

  expect(await logout.logout()).toBe("confirmed");
  expect(cache.getQueryData(["private"])).toBeUndefined();
  expect(h.context.store.getState().accessToken).toBeNull();
  expect(h.context.store.getState().user).toBeNull();
  expect(h.saved()).toBeUndefined();
  expect(h.configurations.map((c) => c.url)).toEqual([
    "/auth/register",
    "/auth/resend",
    "/auth/login",
    "/auth/verify",
    "/auth",
    "/auth/logout",
  ]);
  expect(h.configurations.map((c) => c.withCredentials)).toEqual([
    false,
    false,
    true,
    true,
    false,
    true,
  ]);
  expect(h.configurations.map((c) => c.method)).toEqual([
    "post",
    "post",
    "post",
    "post",
    "get",
    "post",
  ]);
  expect(JSON.parse(String(h.configurations[0].data)).name).toBe(
    "Synthetic User",
  );
  expect(JSON.parse(String(h.configurations[3].data)).otp).toBe("001234");
  expect(h.configurations[4].headers?.Authorization).toBe(
    `Bearer ${response.access_token}`,
  );
  expect(h.configurations[0].headers?.Authorization).toBeUndefined();
  expect(
    JSON.stringify(
      cache
        .getMutationCache()
        .getAll()
        .map((m) => m.state.data),
    ),
  ).not.toContain(response.access_token);

  unsubscribe();
  cache.clear();
});

test.each([
  [
    403,
    {
      error: "Private verification detail",
      code: "VERIFICATION_REQUIRED",
    },
    "VERIFICATION_REQUIRED",
  ],
  [
    401,
    {
      error: "Invalid",
      code: "INVALID_CREDENTIALS",
    },
    "INVALID_CREDENTIALS",
  ],
  [401, "unstructured", "INVALID_RESPONSE"],
  [
    200,
    {
      access_token: "secret",
    },
    "INVALID_RESPONSE",
  ],
  [
    200,
    {
      ...response,
      refresh_token: "forbidden",
    },
    "INVALID_RESPONSE",
  ],
])(
  "login hook sanitizes status %i and malformed or structured errors",
  async (status, data, code) => {
    const h = harness({
      status: Number(status),
      data,
    });
    const mutation = renderHook(() => useLogin());

    try {
      await mutation.login({
        email: user.email,
        password: "synthetic-password",
      });

      throw new Error("Expected rejection.");
    } catch (error) {
      expect(error).toBeInstanceOf(AuthFailure);
      expect(error instanceof AuthFailure && error.code).toBe(code);
      expect(JSON.stringify(error)).not.toContain("secret");
      expect(JSON.stringify(error)).not.toContain("config");
    }

    expect(h.context.store.getState().accessToken).toBeNull();
    expect(h.context.store.getState().status).toBe("error");
    expect(h.context.store.getState().error).toBe("credential_action");
  },
);

test("hook input validation rejects numeric OTP and short password before HTTP", async () => {
  const h = harness();
  const login = renderHook(() => useLogin());
  const verify = renderHook(() => useVerify());

  await expect(
    login.login({
      email: user.email,
      password: "short",
    }),
  ).rejects.toThrow();

  await expect(
    verify.verify({
      email: user.email,
      // Exercise the runtime boundary deliberately, rather than bypassing its schema.
      otp: 123456 as unknown as string,
    }),
  ).rejects.toThrow();

  expect(h.configurations).toHaveLength(0);
});

test("login normalizes submitted email but commits only the canonical response without GET auth", async () => {
  const h = harness();
  const mutation = renderHook(() => useLogin());
  const result = await mutation.login({
    email: "SUBMITTED@example.test",
    password: "synthetic-password",
  });

  expect(result).toEqual(user);
  expect(h.context.store.getState().user).toEqual(user);
  expect(h.context.store.getState().status).toBe("authenticated");
  expect(h.configurations.map((config) => config.url)).toEqual(["/auth/login"]);
  expect(JSON.parse(String(h.configurations[0].data)).email).toBe(
    "submitted@example.test",
  );
  expect(h.configurations[0].withCredentials).toBe(true);
  expect(h.configurations[0].isProtected).toBe(false);
  expect(h.configurations[0].headers?.Authorization).toBeUndefined();
  expect(JSON.stringify(result)).not.toContain(response.access_token);
});

test("logout hook blocks synchronously and exposes an unconfirmed transport failure", async () => {
  const h = harness();
  const pending = deferred<never>();

  await h.session.adopt(response);

  h.client.defaults.adapter = () => pending.promise;

  const logout = renderHook(() => useLogout());
  const result = logout.logout();

  await Bun.sleep(0);

  expect(h.context.store.getState().status).toBe("unauthenticated");
  expect(h.context.store.getState().accessToken).toBeNull();

  pending.reject(new Error("sensitive transport internals"));

  expect(await result).toBe("unconfirmed");
  expect(h.storage.signedOut()).toBe(true);
});

test("explicit current-user hook validates the canonical DTO and never dispatches on render", async () => {
  const h = harness({
    status: 200,
    data: response,
  });

  await h.session.adopt(response);

  const query = renderHook(() => useAuth());

  expect(h.configurations).toHaveLength(0);
  expect((await query.getAuth()).error).toMatchObject({
    code: "INVALID_RESPONSE",
  });
  expect(h.configurations).toHaveLength(1);
});

test("login hook sanitizes transport exceptions without retrying or retaining config", async () => {
  const h = harness();
  let calls = 0;

  h.client.defaults.adapter = async () => {
    calls++;

    throw new Error("sensitive transport internals");
  };

  const login = renderHook(() => useLogin());

  await expect(
    login.login({
      email: user.email,
      password: "synthetic-password",
    }),
  ).rejects.toMatchObject({
    status: 0,
    code: "TRANSPORT_ERROR",
  });

  expect(calls).toBe(1);
  expect(h.saved()).toBeUndefined();
});

test("same-hook duplicate login is blocked before React renders pending state", async () => {
  const h = harness();
  const pending = deferred<void>();
  const adapter = h.client.defaults.adapter;
  let calls = 0;

  h.client.defaults.adapter = async (config) => {
    calls++;

    await pending.promise;

    return axios.getAdapter(adapter)(config);
  };

  const login = renderHook(() => useLogin());
  const credentials = {
    email: user.email,
    password: "synthetic-password",
  };

  const first = login.login(credentials);

  await expect(login.login(credentials)).rejects.toMatchObject({
    code: "REQUEST_PENDING",
  });

  expect(calls).toBe(1);

  pending.resolve();

  expect(await first).toEqual(user);
  expect(h.context.store.getState().accessToken).toBe(response.access_token);
});

test.each([200, 204])(
  "logout hook does not confirm malformed status/body %i",
  async (status) => {
    const h = harness({
      status,
      data: {
        unexpected: true,
      },
    });

    await h.session.adopt(response);

    const logout = renderHook(() => useLogout());

    expect(await logout.logout()).toBe("unconfirmed");
    expect(h.storage.signedOut()).toBe(true);
  },
);

test("direct login hook waits for an active refresh before sending its cookie request", async () => {
  const h = harness();
  const renewal = deferred<typeof response>();

  await h.session.adopt(response);

  const lease = await acquireAccess();
  const refreshing = refreshCredentials(
    lease,
    coordination,
    () => renewal.promise,
  );
  const login = renderHook(() => useLogin());
  const result = login.login({
    email: user.email,
    password: "synthetic-password",
  });

  await Bun.sleep(0);

  expect(h.configurations).toHaveLength(0);

  renewal.resolve({
    ...response,
    access_token: "obsolete.refresh.fixture",
  });

  await refreshing;

  expect(await result).toEqual(user);
  expect(h.configurations.map((c) => c.url)).toEqual(["/auth/login"]);
  expect(h.context.store.getState().accessToken).toBe(response.access_token);
});

test("logout supersedes a pending direct login and still dispatches after its failure", async () => {
  const h = harness();
  const pending = deferred<void>();
  const adapter = h.client.defaults.adapter;

  h.client.defaults.adapter = async (config) => {
    if (config.url === "/auth/login") {
      await pending.promise;
    }

    return axios.getAdapter(adapter)(config);
  };

  const login = renderHook(() => useLogin());
  const logout = renderHook(() => useLogout());
  const signingIn = login
    .login({
      email: user.email,
      password: "synthetic-password",
    })
    .then(
      () => "accepted",
      () => "superseded",
    );

  await Bun.sleep(0);

  const signingOut = logout.logout();

  await Bun.sleep(0);

  expect(h.context.store.getState().status).toBe("unauthenticated");

  pending.resolve();

  expect(await signingIn).toBe("superseded");
  expect(await signingOut).toBe("confirmed");
  expect(h.context.store.getState().accessToken).toBeNull();
  expect(h.saved()).toBeUndefined();
  expect(h.configurations.map((c) => c.url)).toEqual([
    "/auth/login",
    "/auth/logout",
  ]);
});

test("logout hook rejects duplicates until local key cleanup finishes", async () => {
  const h = harness();
  const cleanup = deferred<boolean>();

  await h.session.adopt(response);

  h.storage.destroy = () => cleanup.promise;

  const logout = renderHook(() => useLogout());
  const first = logout.logout();

  await Bun.sleep(0);

  expect(h.configurations).toHaveLength(1);

  await expect(logout.logout()).rejects.toMatchObject({
    code: "REQUEST_PENDING",
  });

  cleanup.resolve(true);

  expect(await first).toBe("confirmed");
  expect(h.configurations).toHaveLength(1);
});

test("account replacement after queue readiness prevents obsolete hook dispatch", async () => {
  const h = harness();
  const gate = deferred<void>();

  coordination.cookieQueue = gate.promise;

  const login = renderHook(() => useLogin());
  const result = login
    .login({
      email: user.email,
      password: "synthetic-password",
    })
    .then(
      () => "accepted",
      () => "superseded",
    );

  await Bun.sleep(0);

  const replacement = gate.promise.then(() => startAuth("logout"));

  gate.resolve();

  const operation = await replacement;

  expect(await result).toBe("superseded");
  expect(h.configurations).toHaveLength(0);

  await operation.ready;

  operation.release();

  expect(await finishLogout(operation, false)).toBe("unconfirmed");
  expect(h.context.store.getState().accessToken).toBeNull();
});

test("all six hooks expose only their intentionally named public fields", () => {
  harness();

  const hooks = [useRegister, useResend, useVerify, useLogin, useLogout];
  const names = ["Register", "Resend", "Verify", "Login", "Logout"];

  hooks.forEach((hook, index) => {
    const result = renderHook<MutationResult>(hook);
    const name = names[index];
    const action = name.toLowerCase();

    expect(Object.keys(result).sort()).toEqual(
      [action, `is${name}Loading`, `is${name}Success`, `${action}Error`].sort(),
    );
    expect(
      Object.values(result).filter((value) => value === false),
    ).toHaveLength(2);
  });

  const current = renderHook(() => useAuth());

  expect(Object.keys(current).sort()).toEqual([
    "authError",
    "authUser",
    "getAuth",
    "isAuthLoading",
  ]);
  expect(current.isAuthLoading).toBe(false);
});

test.each([
  [
    "register",
    useRegister,
    {
      name: "Fixture",
      email: user.email,
      password: "synthetic-password",
    },
  ],
  [
    "resend",
    useResend,
    {
      email: user.email,
    },
  ],
  [
    "verify",
    useVerify,
    {
      email: user.email,
      otp: "001234",
    },
  ],
] as const)(
  "%s rejects duplicate requests while its mutation is pending",
  async (name, hook, input) => {
    const h = harness();
    const gate = deferred<void>();
    const adapter = h.client.defaults.adapter;
    const cache = new QueryClient();

    h.client.defaults.adapter = async (config) => {
      await gate.promise;

      return axios.getAdapter(adapter)(config);
    };

    const result = renderHook<VerificationMutationResult>(hook, cache);
    const dispatch = () => {
      if ("register" in result && "name" in input) {
        return result.register(input);
      }

      if ("resend" in result) {
        return result.resend(input);
      }

      if ("verify" in result && "otp" in input) {
        return result.verify(input);
      }

      throw new Error("Mismatched fixture.");
    };

    const first = dispatch();

    await Bun.sleep(0);

    expect(cache.getMutationCache().getAll()[0].state.status).toBe("pending");

    await expect(dispatch()).rejects.toMatchObject({
      code: "REQUEST_PENDING",
    });

    gate.resolve();

    await first;

    expect(h.configurations).toHaveLength(1);

    if (name !== "verify") {
      expect(h.context.store.getState().user).toBeNull();
      expect(h.saved()).toBeUndefined();
    }

    cache.clear();
  },
);

test.each([
  [409, "ACCOUNT_ALREADY_EXISTS"],
  [422, "UNPROCESSABLE_ENTITY"],
  [400, "INVALID_VERIFICATION"],
  [400, "VERIFICATION_EXPIRED"],
  [409, "VERIFICATION_NOT_REQUIRED"],
  [404, "ACCOUNT_NOT_FOUND"],
] as const)(
  "registration/verification/resend preserve safe %i %s errors",
  async (status, code) => {
    const h = harness({
      status,
      data: {
        code,
        error: "private server detail",
      },
    });
    const register = renderHook(() => useRegister());
    const verify = renderHook(() => useVerify());
    const resend = renderHook(() => useResend());

    const calls = [
      () =>
        register.register({
          name: "Fixture",
          email: user.email,
          password: "synthetic-password",
        }),
      () =>
        verify.verify({
          email: user.email,
          otp: "001234",
        }),
      () =>
        resend.resend({
          email: user.email,
        }),
    ];

    for (const call of calls) {
      try {
        await call();

        throw new Error("Expected rejection.");
      } catch (error) {
        expect(error).toMatchObject({
          status,
          code,
        });
        expect(JSON.stringify(error)).not.toContain("private server detail");
      }
    }

    expect(h.context.store.getState().user).toBeNull();
  },
);

test("registration and resend reject invalid fields before dispatch", async () => {
  const h = harness();
  const registration = renderHook(() => useRegister());
  const resending = renderHook(() => useResend());

  await expect(
    registration.register({
      name: " ",
      email: "invalid",
      password: "short",
    }),
  ).rejects.toThrow();
  await expect(
    resending.resend({
      email: "invalid",
    }),
  ).rejects.toThrow();

  expect(h.configurations).toHaveLength(0);
});

test("register, verify and resend sanitize uncertain network failures without authenticating", async () => {
  const h = harness();

  h.client.defaults.adapter = async () => {
    throw new Error("private transport configuration");
  };

  const registration = renderHook(() => useRegister());
  const verification = renderHook(() => useVerify());
  const resending = renderHook(() => useResend());
  const calls = [
    () =>
      registration.register({
        name: "Fixture",
        email: user.email,
        password: "synthetic-password",
      }),
    () =>
      verification.verify({
        email: user.email,
        otp: "001234",
      }),
    () =>
      resending.resend({
        email: user.email,
      }),
  ];

  for (const call of calls) {
    await expect(call()).rejects.toMatchObject({
      status: 0,
      code: "TRANSPORT_ERROR",
    });
  }

  expect(h.context.store.getState().user).toBeNull();
  expect(h.context.store.getState().error).toBe("credential_action");
  expect(h.saved()).toBeUndefined();
});

test("verify commits the canonical response profile without a redundant current-user request", async () => {
  const h = harness();
  const verification = renderHook(() => useVerify());
  const result = await verification.verify({
    email: "submitted@example.test",
    otp: "001234",
  });

  expect(result).toEqual(user);
  expect(h.context.store.getState().status).toBe("authenticated");
  expect(h.context.store.getState().user).toEqual(user);
  expect(h.context.store.getState().user?.email).not.toBe(
    "submitted@example.test",
  );
  expect(h.configurations.map((config) => config.url)).toEqual([
    "/auth/verify",
  ]);
});
