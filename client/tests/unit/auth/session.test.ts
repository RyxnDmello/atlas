import { expect, test } from "bun:test";

import "./environment";

import { AuthFailure } from "@services/http/validate";
import { startAuth, finishLogin, finishLogout } from "@services/auth/auth";

import { deferred, fixture, fixtureAccess, response, user } from "./fixtures";

test.each([401, 500])(
  "completed initialization remains shared after refresh status %i",
  async (status) => {
    let refreshes = 0;

    const context = fixture({
      refresh: async () => {
        refreshes++;

        throw new AuthFailure(
          status,
          status === 401 ? "INVALID_REFRESH_TOKEN" : "SERVER_ERROR",
        );
      },
    });

    const startup = context.session.initialize();

    await startup;

    expect(context.session.initialize()).toBe(startup);
    await context.session.initialize();
    expect(refreshes).toBe(1);

    if (status === 500) {
      const retry = context.session.retry();

      expect(retry).not.toBe(startup);
      await retry;
      expect(context.session.initialize()).toBe(retry);
      expect(refreshes).toBe(2);
    }
  },
);

test.each(["login", "logout"] as const)(
  "explicit %s suppresses automatic initialization while pending and after completion",
  async (action) => {
    let reads = 0;
    const context = fixture(
      {},
      {
        load: async () => {
          reads++;

          return undefined;
        },
      },
    );
    const operation = startAuth(action, context.session.context);
    const initialization = context.session.initialize();

    await initialization;
    expect(reads).toBe(0);
    expect(context.calls).toEqual([]);

    await operation.ready;
    operation.release();
    await operation.clearing;

    if (action === "login") {
      await finishLogin(operation, response, context.session.context);
    } else {
      await finishLogout(operation, true, context.session.context);
    }

    expect(context.session.initialize()).toBe(initialization);
    expect(reads).toBe(0);
  },
);

test("old refresh completion cannot clear or join a newer account refresh", async () => {
  const oldResponse = deferred<typeof response>();
  const newResponse = deferred<typeof response>();
  let refreshes = 0;

  const context = fixture({
    refresh: () => {
      refreshes++;

      return refreshes === 1 ? oldResponse.promise : newResponse.promise;
    },
  });

  await context.session.adopt(response);

  const oldRefresh = context.session.refresh(await context.session.acquire());

  await Promise.resolve();
  expect(refreshes).toBe(1);

  const replacement = {
    access_token: "new.account.fixture",
    user: {
      ...user,
      id: "93fa7f76-f873-4850-92a0-b14dd13d8dde",
    },
  };

  await context.session.adopt(replacement);

  const lease = await context.session.acquire();
  const newRefresh = context.session.refresh(lease);
  const flight = context.session.context.refresh;

  oldResponse.resolve(response);
  await oldRefresh;

  expect(refreshes).toBe(2);
  expect(context.session.context.refresh).toBe(flight);
  expect(context.session.getSnapshot().user?.id).toBe(replacement.user.id);

  const duplicate = context.session.refresh(lease);

  newResponse.resolve(replacement);
  await Promise.all([newRefresh, duplicate]);

  expect(refreshes).toBe(2);
  expect(context.session.context.refresh).toBeUndefined();
  expect(context.saved()).toBe(replacement.access_token);
});

test("a delayed failure for an identical token string cannot trigger another rotation", async () => {
  const context = fixture();

  await context.session.adopt(response);

  const original = await context.session.acquire();

  await context.session.refresh(original);

  const replacement = await context.session.acquire();

  expect(replacement.token).toBe(original.token);
  expect(replacement.tokenVersion).toBeGreaterThan(original.tokenVersion);

  await context.session.refresh(original);

  expect(context.calls).toEqual(["refresh"]);
});

test("initializers share recovery and valid decrypted token is server-validated without refresh", async () => {
  const read = deferred<string | undefined>();
  let reads = 0;

  const context = fixture(
    {},
    {
      load: () => {
        reads++;

        return read.promise;
      },
    },
  );

  const first = context.session.initialize();

  expect(context.session.initialize()).toBe(first);

  const access = context.session.acquire();

  expect(context.session.getSnapshot().status).toBe("restoring");

  read.resolve("saved.fixture");

  await first;

  expect((await access).token).toBe("saved.fixture");
  expect(reads).toBe(1);
  expect(context.calls).toEqual(["current"]);
  expect(context.session.getSnapshot().user).toEqual(user);
});

test("rejected saved access refreshes once then validates the new access before saving", async () => {
  const tokens: string[] = [];

  const context = fixture(
    {
      current: async (token) => {
        tokens.push(token);

        if (token === "old") {
          throw new AuthFailure(401, "INVALID_ACCESS_TOKEN");
        }

        return user;
      },
    },
    {
      load: async () => {
        return "old";
      },
    },
  );

  await context.session.initialize();

  expect(tokens).toEqual(["old", response.access_token]);
  expect(context.calls).toEqual(["refresh"]);
  expect(context.saved()).toBe(response.access_token);
});

test("missing token restores through refresh then GET auth", async () => {
  const context = fixture();

  await context.session.initialize();

  expect(context.calls).toEqual(["refresh", "current"]);
  expect(context.session.getSnapshot().status).toBe("authenticated");
});

test.each([
  [401, "INVALID_REFRESH_TOKEN", "unauthenticated"],
  [401, "OTHER", "error"],
  [500, "SERVER_ERROR", "error"],
  [0, "TRANSPORT_ERROR", "error"],
  [200, "INVALID_RESPONSE", "error"],
] as const)(
  "refresh failure %i %s produces %s",
  async (status, code, expected) => {
    const context = fixture({
      refresh: async () => {
        throw new AuthFailure(Number(status), String(code));
      },
    });

    await context.session.initialize();

    expect(context.session.getSnapshot().status).toBe(expected);

    await expect(context.session.acquire()).rejects.toThrow("unavailable");
  },
);

test("unexpected rejection of fresh startup token is an inconsistent error", async () => {
  const context = fixture({
    current: async () => {
      throw new AuthFailure(401, "INVALID_ACCESS_TOKEN");
    },
  });

  await context.session.initialize();

  expect(context.session.getSnapshot().error).toBe("inconsistent_session");
  expect(context.saved()).toBeUndefined();
});

test.each([true, false])(
  "current-user transport uncertainty stays retryable after refresh=%s",
  async (fresh) => {
    const context = fixture(
      {
        current: async () => {
          throw new AuthFailure(500, "SERVER_ERROR");
        },
      },
      {
        load: async () => {
          return fresh ? undefined : "recovered";
        },
      },
    );

    await context.session.initialize();

    expect(context.session.getSnapshot().status).toBe("error");
    expect(context.session.getSnapshot().error).toBe("session_uncertain");
    expect(context.calls).toEqual(fresh ? ["refresh"] : []);
  },
);

test("refresh error code from a non-refresh current-user operation is not terminal", async () => {
  const context = fixture(
    {
      current: async () => {
        throw new AuthFailure(401, "INVALID_REFRESH_TOKEN");
      },
    },
    {
      load: async () => {
        return "recovered";
      },
    },
  );

  await context.session.initialize();

  expect(context.session.getSnapshot().status).toBe("error");
  expect(context.calls).toEqual([]);
});

test.each(["login", "verify"] as const)(
  "%s establishes directly without GET auth",
  async (method) => {
    const context = fixture();

    if (method === "login") {
      await context.session.login({
        email: user.email,
        password: "synthetic-password",
      });
    } else {
      await context.session.verify({
        email: user.email,
        otp: "001234",
      });
    }

    expect(context.calls).toEqual([method]);
    expect(context.session.getSnapshot().status).toBe("authenticated");
    expect(context.session.context.store.getState().accessToken).toBe(
      response.access_token,
    );
  },
);

test("concurrent refresh shares one flight; stale failures reuse the newer token version", async () => {
  const pending = deferred<typeof response>();
  let refreshes = 0;

  const context = fixture({
    refresh: () => {
      refreshes++;

      return pending.promise;
    },
  });

  await context.session.adopt(response);

  const lease = await context.session.acquire();

  const requests = [
    context.session.refresh(lease),
    context.session.refresh(lease),
    context.session.refresh(lease),
  ];

  await Promise.resolve();

  expect(refreshes).toBe(1);

  pending.resolve({
    ...response,
    access_token: "replacement",
  });

  await Promise.all(requests);

  await context.session.refresh(lease);

  expect(refreshes).toBe(1);
  expect((await context.session.acquire()).token).toBe("replacement");
  expect(context.calls).toEqual([]);
});

test("late decrypt after logout cannot restore or repersist", async () => {
  const read = deferred<string | undefined>();

  const context = fixture(
    {},
    {
      load: () => read.promise,
    },
  );

  const initializing = context.session.initialize();

  await context.session.logout();

  read.resolve("old");

  await initializing;

  expect(context.calls).toEqual(["logout"]);
  expect(context.saved()).toBeUndefined();
  expect(context.session.getSnapshot().status).toBe("unauthenticated");
});

test("logout blocks immediately and waits for dispatched refresh before clearing cookie", async () => {
  const pending = deferred<typeof response>();
  const events: string[] = [];

  const context = fixture({
    refresh: () => {
      events.push("refresh");

      return pending.promise;
    },

    logout: async () => {
      events.push("logout");
    },
  });

  await context.session.adopt(response);

  const refreshing = context.session.refresh(await context.session.acquire());

  await Promise.resolve();

  const logout = context.session.logout();

  expect(context.session.getSnapshot().status).toBe("unauthenticated");

  await expect(context.session.acquire()).rejects.toThrow();

  expect(events).toEqual(["refresh"]);

  pending.resolve(response);

  expect(await logout).toBe("confirmed");

  await refreshing;

  expect(events).toEqual(["refresh", "logout"]);
  expect(context.saved()).toBeUndefined();
});

test("old terminal refresh cannot erase a newly adopted account", async () => {
  const pending = deferred<typeof response>();

  const context = fixture({
    refresh: () => pending.promise,
  });

  await context.session.adopt(response);

  const refreshing = context.session.refresh(await context.session.acquire());

  await Promise.resolve();

  await context.session.adopt({
    ...response,
    access_token: "new.account",
    user: {
      ...user,
      id: "95bca73f-3610-443c-9f74-8c2c2f91a54c",
    },
  });

  pending.reject(new AuthFailure(401, "INVALID_REFRESH_TOKEN"));

  await refreshing;

  expect((await context.session.acquire()).token).toBe("new.account");
});

test("failed logout persists signout intent, reload suppresses restore, explicit retry recovers", async () => {
  const context = fixture({
    logout: async () => {
      throw new Error("offline");
    },
  });

  let cleanups = 0;

  context.session.registerCleanup(() => {
    cleanups++;
  });

  await context.session.adopt(response);

  expect(await context.session.logout()).toBe("unconfirmed");
  expect(cleanups).toBe(2);

  const reloaded = fixtureAccess(context.api, context.storage);

  await reloaded.initialize();

  expect(reloaded.getSnapshot().logout).toBe("unconfirmed");
  expect(context.calls).toEqual([]);

  await reloaded.retry();

  expect(reloaded.getSnapshot().status).toBe("authenticated");
});

test("late current-user and delayed persistence cannot supersede account replacement", async () => {
  const validation = deferred<typeof user>();
  const writing = deferred<void>();
  let stored: string | undefined;

  const context = fixture(
    {
      current: () => validation.promise,
    },
    {
      load: async () => {
        return "old";
      },

      save: async (token, current) => {
        if (token === response.access_token) {
          await writing.promise;
        }

        if (current()) {
          stored = token;
        }

        return current();
      },
    },
  );

  const initializing = context.session.initialize();

  await Promise.resolve();

  const first = context.session.adopt(response);

  await context.session.adopt({
    ...response,
    access_token: "newest",
  });

  validation.resolve(user);

  writing.resolve();

  await Promise.all([initializing, first]);

  expect((await context.session.acquire()).token).toBe("newest");
  expect(stored).toBe("newest");
});

test("failed persistence retains valid memory authentication and exposes degradation", async () => {
  const context = fixture(
    {},
    {
      save: async () => {
        return false;
      },
    },
  );

  await context.session.adopt(response);

  expect(context.session.getSnapshot().persistence).toBe("unavailable");
  expect((await context.session.acquire()).token).toBe(response.access_token);
});

test("cookie-changing login waits for earlier refresh, and stale logout cannot clear newer login", async () => {
  const pending = deferred<typeof response>();
  const loggedOut = deferred<void>();
  const events: string[] = [];

  const context = fixture({
    refresh: () => {
      events.push("refresh");

      return pending.promise;
    },

    login: async () => {
      events.push("login");

      return {
        ...response,
        access_token: "new.login",
      };
    },

    logout: () => {
      events.push("logout");

      return loggedOut.promise;
    },
  });

  await context.session.adopt(response);

  const refreshing = context.session.refresh(await context.session.acquire());

  await Promise.resolve();

  const login = context.session.login({
    email: user.email,
    password: "synthetic-password",
  });

  expect(events).toEqual(["refresh"]);

  pending.resolve(response);

  await Promise.all([refreshing, login]);

  expect(events).toEqual(["refresh", "login"]);

  const logout = context.session.logout();

  await Promise.resolve();

  const second = context.session.login({
    email: user.email,
    password: "synthetic-password",
  });

  loggedOut.resolve();

  await Promise.all([logout, second]);

  expect((await context.session.acquire()).token).toBe("new.login");
  expect(context.session.getSnapshot().logout).toBe("none");
});

test("terminal in-session invalid refresh clears token, ciphertext and account cache", async () => {
  const context = fixture({
    refresh: async () => {
      throw new AuthFailure(401, "INVALID_REFRESH_TOKEN");
    },
  });

  await context.session.adopt(response);

  let cleared = false;

  context.session.registerCleanup(() => {
    cleared = true;
  });

  await context.session.refresh(await context.session.acquire());

  expect(cleared).toBe(true);
  expect(context.saved()).toBeUndefined();
  expect(context.session.getSnapshot().status).toBe("unauthenticated");
});

test("late rejected startup candidate cannot remove a replacement account ciphertext", async () => {
  const candidate = deferred<typeof user>();
  let validations = 0;
  let clears = 0;

  const h = fixture(
    {
      current: () => {
        validations++;

        return candidate.promise;
      },
    },
    {
      load: async () => {
        return "old.candidate.fixture";
      },
      clear: async () => {
        clears++;
      },
    },
  );

  const startup = h.session.initialize();

  await Bun.sleep(0);
  await h.session.adopt(response);

  const previous = clears;

  candidate.reject(new AuthFailure(401, "INVALID_ACCESS_TOKEN"));

  await startup;

  expect(validations).toBe(1);
  expect(clears).toBe(previous);
  expect(h.saved()).toBe(response.access_token);
  expect(h.session.getSnapshot().accessToken).toBe(response.access_token);
  expect(h.calls).toEqual([]);
});
