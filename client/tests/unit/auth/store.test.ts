import { expect, test } from "bun:test";
import { createElement } from "react";
import { renderToString } from "react-dom/server";

import "./environment";

import { createAuthStore } from "@stores/auth";

import { onAuthBoundary } from "@services/auth/auth";

import { fixture, response, user } from "./fixtures";

test("the Zustand hook and non-React API share one typed store with safe SSR state", () => {
  const store = createAuthStore();

  function Probe() {
    return createElement(
      "span",
      null,
      store((state) => state.status),
    );
  }

  expect(renderToString(createElement(Probe))).toContain("restoring");

  const users: unknown[] = [];
  let previous = store.getState().user;

  const unsubscribe = store.subscribe((state) => {
    if (previous !== state.user) {
      previous = state.user;

      users.push(state.user);
    }
  });

  store.getState().update({
    status: "authenticated",
    user,
    accessToken: response.access_token,
  });
  store.getState().update({
    persistence: "available",
  });

  expect(users).toEqual([user]);
  expect(store.getState().accessToken).toBe(response.access_token);
  expect(store.getInitialState().status).toBe("restoring");

  unsubscribe();
});

test("cache cleanup runs once per account boundary and not for token/persistence updates", async () => {
  const h = fixture();
  let cleanups = 0;

  const unsubscribe = onAuthBoundary(() => {
    cleanups++;
  }, h.session.context);

  await h.session.adopt(response);

  const lease = await h.session.acquire();

  expect<string | null>(lease.token).toBe(
    h.session.context.store.getState().accessToken,
  );

  await h.session.refresh(lease);

  expect(cleanups).toBe(1);

  await h.session.adopt({
    ...response,
    user: {
      ...user,
      id: "95bca73f-3610-443c-9f74-8c2c2f91a54c",
    },
  });
  await h.session.logout();

  expect(cleanups).toBe(3);

  unsubscribe();
});
