import { expect, test } from "bun:test";

import "./environment";

import { createAuthStore } from "@stores/auth";
import { initializeAuth, createCoordination } from "@services/auth/auth";

import { fixture, response, user } from "./fixtures";

interface Observation {
  url: string;
  options?: RequestInit;
}

test.each([true, false])(
  "internal raw restoration uses fixed trusted paths and scoped credentials, recovered=%s",
  async (recovered) => {
    const h = fixture(
      {},
      {
        load: async () => {
          return recovered ? "old.fixture" : undefined;
        },
      },
    );
    const context = createCoordination(createAuthStore(), h.storage);
    const previous = globalThis.fetch;
    const observations: Observation[] = [];

    globalThis.fetch = Object.assign(
      async (input: string | URL | Request, options?: RequestInit) => {
        const url = String(input);

        observations.push({
          url,
          options,
        });

        return new Response(
          JSON.stringify(url.endsWith("/auth") ? user : response),
        );
      },
      {
        preconnect: previous.preconnect,
      },
    );

    try {
      await initializeAuth(context);

      expect(observations.map((c) => new URL(c.url).pathname)).toEqual(
        recovered ? ["/auth"] : ["/auth/refresh", "/auth"],
      );
      expect(observations.map((c) => c.options?.credentials)).toEqual(
        recovered ? ["omit"] : ["include", "omit"],
      );
      expect(
        observations.every(
          (c) => new URL(c.url).origin === "http://localhost:8080",
        ),
      ).toBe(true);
      expect(
        new Headers(observations.at(-1)?.options?.headers).get("Authorization"),
      ).toBe(`Bearer ${recovered ? "old.fixture" : response.access_token}`);
      expect(context.store.getState().user).toEqual(user);
      expect(observations.every((c) => c.options?.redirect === "error")).toBe(
        true,
      );

      if (!recovered) {
        expect(
          new Headers(observations[0].options?.headers).has("Authorization"),
        ).toBe(false);
        expect(observations[0].options?.body).toBeUndefined();
      }
    } finally {
      globalThis.fetch = previous;
    }
  },
);
