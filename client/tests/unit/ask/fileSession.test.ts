import { afterEach, expect, test } from "bun:test";

import "../auth/environment";

import { createAskSession } from "@services/ask/askSession";
import { createFileAskSession } from "@services/ask/fileSession";
import { coordination } from "@services/auth/auth";
import http from "@services/http/axios";

import { fileKey } from "@utils/file/file";

import useAuthStore from "@stores/auth";

import { harness, file, child } from "../folder/fixtures";

const originalFetch = globalThis.fetch;
const originalState = useAuthStore.getState();
const originalCoordination = {
  ...coordination,
};
const originalAdapter = http.defaults.adapter;
const cleanups: (() => void)[] = [];
const encoder = new TextEncoder();

type FetchImplementation = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

const mock = (implementation: FetchImplementation) => {
  globalThis.fetch = Object.assign(implementation, {
    preconnect: originalFetch.preconnect,
  });
};

afterEach(() => {
  cleanups.splice(0).forEach((close) => close());
  Object.assign(coordination, originalCoordination);
  useAuthStore.setState(originalState);
  http.defaults.adapter = originalAdapter;
  globalThis.fetch = originalFetch;
});

const event = (name: string, data: unknown) =>
  `event: ${name}\ndata: ${JSON.stringify(data)}\n\n`;
const partial = event("answer", {
  text: "Synthetic partial",
});
const complete =
  event("citations", {
    citations: [
      {
        index: 7,
        page: null,
        heading: null,
        section: null,
        excerpt: "Synthetic excerpt",
      },
    ],
  }) +
  event("done", {
    status: "completed",
  });

const response = (body: string | ReadableStream<Uint8Array>) =>
  new Response(body, {
    headers: {
      "Content-Type": "text/event-stream",
    },
  });

const setup = async () => {
  const h = await harness();
  const lifetime = createFileAskSession(file.id);
  lifetime.activate();
  cleanups.push(lifetime.retire, h.close);

  return {
    h,
    lifetime,
    ask: lifetime.session,
  };
};

test.each(["logout", "uncertain", "terminal", "account", "session", "route"])(
  "%s immediately retires a live abort-ignoring reader and clears private text/citations",
  async (boundary) => {
    const { h, lifetime, ask } = await setup();
    let controller!: ReadableStreamDefaultController<Uint8Array>;
    let canceled = 0;
    let signal: AbortSignal | null | undefined;
    mock(async (_url, init) => {
      signal = init?.signal;

      return response(
        new ReadableStream<Uint8Array>({
          start: (value) => {
            controller = value;
          },
          cancel: () => {
            canceled++;
          },
        }),
      );
    });

    const pending = ask.submit(" Question ");
    await Bun.sleep(1);
    controller.enqueue(encoder.encode(partial + complete));
    await Bun.sleep(1);
    expect(ask.getSnapshot().status).toBe("streaming");
    expect(ask.getSnapshot().answer).toBe("Synthetic partial");
    expect(ask.getSnapshot().citations).toEqual([]);

    if (boundary === "logout") {
      useAuthStore.getState().update({
        logout: "pending",
      });
    }

    if (boundary === "uncertain") {
      useAuthStore.getState().update({
        status: "error",
      });
    }

    if (boundary === "terminal") {
      useAuthStore.getState().update({
        status: "unauthenticated",
        accessToken: null,
      });
    }

    if (boundary === "account") {
      await h.adopt();
    }

    if (boundary === "session") {
      coordination.sessionVersion++;
      useAuthStore.getState().update({});
    }

    if (boundary === "route") {
      lifetime.retire();
    }

    expect(signal?.aborted).toBe(true);
    expect(ask.getSnapshot().status).toBe("idle");
    await pending;
    expect(canceled).toBe(1);
    expect(ask.getSnapshot().answer).toBe("");
    expect(ask.getSnapshot().citations).toEqual([]);
  },
);

test.each(["route", "account"])(
  "late %s response body is canceled without altering a replacement session or metadata",
  async (boundary) => {
    const { h, lifetime, ask } = await setup();
    let resolve!: (value: Response) => void;
    let calls = 0;
    mock(() => {
      calls++;

      return new Promise<Response>((done) => {
        resolve = done;
      });
    });
    const pending = ask.submit("Old question");
    await Bun.sleep(1);

    if (boundary === "account") {
      await h.adopt();
    }

    lifetime.retire();
    const next = createFileAskSession(boundary === "account" ? file.id : child);
    next.activate();
    cleanups.push(next.retire);
    h.cache.setQueryData(fileKey(file.id), {
      ...file,
      name: "Replacement metadata",
    });
    mock(async () => response(partial + complete));
    await next.session.submit("New question");
    const replacement = next.session.getSnapshot();
    let canceled = false;
    resolve(
      response(
        new ReadableStream<Uint8Array>({
          start: (controller) => {
            controller.enqueue(encoder.encode(partial + complete));
          },
          cancel: () => {
            canceled = true;
          },
        }),
      ),
    );
    await pending;

    expect(calls).toBe(1);
    expect(canceled).toBe(true);
    expect(ask.getSnapshot().status).toBe("idle");
    expect(next.session.getSnapshot()).toBe(replacement);
    expect(replacement.status).toBe("success");
    expect(h.cache.getQueryData(fileKey(file.id))).toEqual({
      ...file,
      name: "Replacement metadata",
    });
    expect(h.cache.getQueryState(fileKey(file.id))?.isInvalidated).toBe(false);
  },
);

test("publication guard blocks completion even without a boundary notification or abort", async () => {
  await setup();
  let current = true;
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const ask = createAskSession({
    current: () => current,
  });
  ask.setScope(file.id);
  mock(async () =>
    response(
      new ReadableStream<Uint8Array>({
        start: (value) => {
          controller = value;
        },
      }),
    ),
  );
  const pending = ask.submit("Question");
  await Bun.sleep(1);
  current = false;
  controller.enqueue(encoder.encode(partial + complete));
  controller.close();
  await pending;

  expect(ask.getSnapshot().status).toBe("idle");
  expect(ask.getSnapshot().answer).toBe("");
  expect(ask.getSnapshot().citations).toEqual([]);
});

test("StrictMode cleanup/reactivation restores only the current file scope and starts empty", async () => {
  const { lifetime, ask } = await setup();
  let calls = 0;
  mock(async () => {
    calls++;
    return response(partial + complete);
  });
  await ask.submit("First");
  lifetime.retire();
  lifetime.activate();

  expect(ask.getSnapshot().status).toBe("idle");
  await ask.submit("Second");
  expect(ask.getSnapshot().status).toBe("success");
  expect(calls).toBe(2);
});

test.each([
  [404, "FILE_NOT_FOUND"],
  [409, "FILE_NOT_READY"],
  [401, "AUTH_REQUIRED"],
  [422, "UNPROCESSABLE_ENTITY"],
  [503, "UNAVAILABLE"],
] as const)(
  "structured %s/%s failure exposes reconciliation code and no trusted answer",
  async (status, code) => {
    const { ask } = await setup();
    mock(async () =>
      Response.json(
        {
          error: "File unavailable.",
          code,
        },
        {
          status,
        },
      ),
    );

    await ask.submit("Question");

    expect(ask.getSnapshot().status).toBe("error");
    expect(ask.getSnapshot().httpFailure).toEqual({
      status,
      code,
    });
    expect(ask.getSnapshot().answer).toBe("");
    expect(ask.getSnapshot().citations).toEqual([]);
  },
);

test("invalid-access recovery failure retires the private result and never replays Ask POST", async () => {
  const { h, ask } = await setup();
  const paths: string[] = [];
  mock(async (url) => {
    const path = new URL(String(url)).pathname;
    paths.push(path);

    return Response.json(
      {
        error: "Access token is invalid.",
        code:
          path === "/auth/refresh"
            ? "INVALID_REFRESH_TOKEN"
            : "INVALID_ACCESS_TOKEN",
      },
      {
        status: 401,
      },
    );
  });
  await ask.submit("Question");

  expect(paths).toEqual([`/files/${file.id}/ask`, "/auth/refresh"]);
  expect(h.requests).toHaveLength(0);
  expect(ask.getSnapshot().status).toBe("idle");
  expect(ask.getSnapshot().citations).toEqual([]);
});
