import { afterEach, expect, test } from "bun:test";
const previous = process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL;
process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL = "http://localhost:8080";
const { createAskSession } = await import("@services/ask/askSession");
if (previous === undefined) delete process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL;
else process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL = previous;
const original = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = original;
});
const id = "25bca73f-3610-443c-9f74-8c2c2f91a54c";
const encoder = new TextEncoder();
const event = (name: string, data: unknown) =>
  `event: ${name}\ndata: ${JSON.stringify(data)}\n\n`;
const citation = {
  index: 0,
  page: null,
  heading: "Policy",
  section: null,
  excerpt: "Synthetic evidence",
};
const answer =
  event("answer", {
    text: "Hello ",
  }) +
  event("answer", {
    text: "world",
  });
const citations = event("citations", {
  citations: [citation],
});
const done = event("done", {
  status: "completed",
});
const error = event("error", {
  error: "Generation failed.",
  code: "GENERATION_FAILED",
});
function response(text: string) {
  return new Response(text, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
    },
  });
}
function session() {
  const value = createAskSession();
  value.setScope(id);
  return value;
}
function mock(
  impl: (
    input: string | URL | Request,
    init?: RequestInit,
  ) => Promise<Response>,
) {
  globalThis.fetch = Object.assign(impl, {
    preconnect: original.preconnect,
  });
}

test("no file or blank question makes no request", async () => {
  let count = 0;
  mock(async () => {
    count++;
    return response("");
  });
  const ask = createAskSession();
  await ask.submit("Question");
  ask.setScope(id);
  await ask.submit(" \t ");
  expect(count).toBe(0);
  expect(ask.getSnapshot().status).toBe("idle");
});
test("native POST uses exact ID, trimmed body, omitted credentials and signal; retains citations", async () => {
  mock(async (url, init) => {
    expect(url).toBe(`http://localhost:8080/files/${id}/ask`);
    expect(init?.method).toBe("POST");
    expect(new Headers(init?.headers).get("Content-Type")).toBe(
      "application/json",
    );
    expect(init?.body).toBe('{"question":"Question"}');
    expect(init?.credentials).toBe("omit");
    expect(init?.signal).toBeInstanceOf(AbortSignal);
    return response(answer + citations + done);
  });
  const ask = session();
  const snapshots: string[] = [];
  ask.subscribe(() => snapshots.push(ask.getSnapshot().answer));
  await ask.submit(" Question ");
  expect(snapshots).toContain("Hello ");
  expect(ask.getSnapshot()).toEqual({
    status: "success",
    answer: "Hello world",
    citations: [citation],
  });
});
test("canonical fallback with empty citations succeeds", async () => {
  const fallback =
    "I don't have enough information in this file to answer that.";
  mock(async () =>
    response(
      event("answer", {
        text: fallback,
      }) +
        event("citations", {
          citations: [],
        }) +
        done,
    ),
  );
  const ask = session();
  await ask.submit("Question");
  expect(ask.getSnapshot()).toEqual({
    status: "success",
    answer: fallback,
    citations: [],
  });
});
const invalid: [string, string][] = [
  ["early done", done],
  ["duplicate citations", answer + citations + citations + done],
  ["duplicate done", answer + citations + done + done],
  ["answer after citations", citations + answer + done],
  ["answer after done", citations + done + answer],
  ["error", answer + error],
  ["error after staged citations", answer + citations + error],
  ["done after error", answer + error + done],
  ["duplicate error", error + error],
  ["EOF", answer],
  ["missing done", answer + citations],
  ["empty stream", ""],
  ["unknown event", event("mystery", {})],
  ["invalid JSON", "event: answer\ndata: {\n\n"],
  [
    "invalid answer",
    event("answer", {
      text: 1,
    }),
  ],
  [
    "invalid citations",
    answer +
      event("citations", {
        citations: [
          {
            index: -1,
          },
        ],
      }) +
      done,
  ],
  [
    "missing nullable fields",
    event("citations", {
      citations: [
        {
          index: 0,
          excerpt: "",
        },
      ],
    }) + done,
  ],
  [
    "invalid done",
    citations +
      event("done", {
        status: "ok",
      }),
  ],
  [
    "invalid error",
    event("error", {
      error: "x",
    }),
  ],
  ["incomplete record", answer + "event: citations\ndata: {}"],
  [
    "internal marker",
    event("answer", {
      text: "Unsafe [[cite:1]]",
    }) +
      citations +
      done,
  ],
];
for (const [name, text] of invalid)
  test(`rejects ${name} and clears provisional output`, async () => {
    mock(async () => response(text));
    const ask = session();
    await ask.submit("Question");
    expect(ask.getSnapshot().status).toBe("error");
    expect(ask.getSnapshot().answer).toBe("");
    expect(ask.getSnapshot().citations).toEqual([]);
  });
test("split internal markers never reach subscribers", async () => {
  for (let split = 1; split < "[[cite:123]]".length; split++) {
    const marker = "[[cite:123]]";
    mock(async () =>
      response(
        event("answer", {
          text: "Safe " + marker.slice(0, split),
        }) +
          event("answer", {
            text: marker.slice(split),
          }) +
          citations +
          done,
      ),
    );
    const ask = session();
    const observed: string[] = [];
    ask.subscribe(() => observed.push(ask.getSnapshot().answer));
    await ask.submit("Question");
    expect(observed.every((text) => !text.includes("[[cite:"))).toBe(true);
    expect(ask.getSnapshot().status).toBe("error");
  }
});
for (const [name, make] of [
  [
    "network",
    () => {
      throw new Error("private provider details");
    },
  ],
  [
    "HTML error",
    () =>
      new Response("<html>private</html>", {
        status: 500,
      }),
  ],
  ["wrong content type", () => new Response("private")],
  [
    "missing body",
    () =>
      new Response(null, {
        headers: {
          "Content-Type": "text/event-stream",
        },
      }),
  ],
] satisfies [string, () => Response][])
  test(`safe generic failure for ${name}`, async () => {
    mock(async () => make());
    const ask = session();
    await ask.submit("Question");
    expect(ask.getSnapshot().status).toBe("error");
    expect(ask.getSnapshot().error).not.toContain("private");
  });
test("validated structured HTTP error is displayed", async () => {
  mock(async () =>
    Response.json(
      {
        error: "File unavailable.",
        code: "FILE_NOT_FOUND",
      },
      {
        status: 404,
      },
    ),
  );
  const ask = session();
  await ask.submit("Question");
  expect(ask.getSnapshot().error).toBe("File unavailable.");
});
test("duplicates are guarded synchronously; reset aborts without false error or stale updates", async () => {
  let calls = 0;
  let signal: AbortSignal | null | undefined;
  let resolve!: (value: Response) => void;
  mock(async (_url, init) => {
    calls++;
    signal = init?.signal;
    return new Promise<Response>((done) => {
      resolve = done;
    });
  });
  const ask = session();
  const pending = ask.submit("Question");
  await ask.submit("Duplicate");
  expect(calls).toBe(1);
  ask.reset();
  expect(signal?.aborted).toBe(true);
  expect(ask.getSnapshot().status).toBe("idle");
  resolve(response(answer + citations + done));
  await pending;
  expect(ask.getSnapshot().status).toBe("idle");
});
test("scope replacement aborts, resets and protects newer result from stale callbacks", async () => {
  let signal: AbortSignal | null | undefined;
  let resolve!: (value: Response) => void;
  mock(async (_url, init) => {
    signal = init?.signal;
    return new Promise<Response>((done) => {
      resolve = done;
    });
  });
  const ask = session();
  const pending = ask.submit("Old");
  ask.setScope("replacement");
  expect(signal?.aborted).toBe(true);
  mock(async (url) => {
    expect(url).toBe("http://localhost:8080/files/replacement/ask");
    return response(answer + citations + done);
  });
  await ask.submit("New");
  resolve(response(error));
  await pending;
  expect(ask.getSnapshot().status).toBe("success");
});
test("new request clears successful answer before reading; partial failures clear text", async () => {
  const ask = session();
  mock(async () => response(answer + citations + done));
  await ask.submit("One");
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  mock(
    async () =>
      new Response(
        new ReadableStream<Uint8Array>({
          start(value) {
            controller = value;
          },
        }),
        {
          headers: {
            "Content-Type": "text/event-stream",
          },
        },
      ),
  );
  const pending = ask.submit("Two");
  expect(ask.getSnapshot().answer).toBe("");
  expect(ask.getSnapshot().citations).toEqual([]);
  await Promise.resolve();
  controller.enqueue(encoder.encode(answer + citations));
  await Bun.sleep(1);
  expect(ask.getSnapshot().answer).toBe("Hello world");
  expect(ask.getSnapshot().citations).toEqual([]);
  controller.enqueue(encoder.encode(error));
  controller.close();
  await pending;
  expect(ask.getSnapshot().answer).toBe("");
  expect(ask.getSnapshot().status).toBe("error");
  expect(ask.getSnapshot().citations).toEqual([]);
});

test("done remains provisional until clean EOF and trailing events invalidate it", async () => {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  mock(
    async () =>
      new Response(
        new ReadableStream<Uint8Array>({
          start(value) {
            controller = value;
          },
        }),
        {
          headers: {
            "Content-Type": "text/event-stream",
          },
        },
      ),
  );
  const ask = session();
  const pending = ask.submit("Question");
  await Promise.resolve();
  controller.enqueue(encoder.encode(answer + citations + done));
  await Bun.sleep(1);
  expect(ask.getSnapshot().status).toBe("streaming");
  expect(ask.getSnapshot().citations).toEqual([]);
  controller.enqueue(
    encoder.encode(
      event("answer", {
        text: "forbidden",
      }),
    ),
  );
  controller.close();
  await pending;
  expect(ask.getSnapshot().status).toBe("error");
  expect(ask.getSnapshot().answer).toBe("");
});

test("teardown reset aborts a live reader, clears partial text and permits a new request", async () => {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  let signal: AbortSignal | null | undefined;
  mock(async (_url, init) => {
    signal = init?.signal;
    return new Response(
      new ReadableStream<Uint8Array>({
        start(value) {
          controller = value;
          signal?.addEventListener("abort", () =>
            value.error(new DOMException("Aborted", "AbortError")),
          );
        },
      }),
      {
        headers: {
          "Content-Type": "text/event-stream",
        },
      },
    );
  });
  const ask = session();
  const pending = ask.submit("Question");
  await Promise.resolve();
  controller.enqueue(encoder.encode(answer + citations));
  await Bun.sleep(1);
  expect(ask.getSnapshot().answer).toBe("Hello world");
  expect(ask.getSnapshot().citations).toEqual([]);
  ask.reset();
  await pending;
  expect(signal?.aborted).toBe(true);
  expect(ask.getSnapshot()).toEqual({
    status: "idle",
    answer: "",
    citations: [],
  });
  mock(async () => response(citations + done));
  await ask.submit("Again");
  expect(ask.getSnapshot().status).toBe("success");
});

test("preserves backend citation nullable and integer semantics, including empty excerpts", async () => {
  const value = {
    index: 7,
    page: -2,
    heading: null,
    section: "",
    excerpt: "",
  };
  mock(async () =>
    response(
      event("citations", {
        citations: [value],
      }) + done,
    ),
  );
  const ask = session();
  await ask.submit("Question");
  expect(ask.getSnapshot()).toEqual({
    status: "success",
    answer: "",
    citations: [value],
  });
});

test("scope change and reset clear a completed cited result", async () => {
  mock(async () => response(answer + citations + done));
  const ask = session();

  await ask.submit("First");
  expect(ask.getSnapshot().citations).toEqual([citation]);

  ask.setScope("replacement");
  expect(ask.getSnapshot()).toEqual({
    status: "idle",
    answer: "",
    citations: [],
  });

  await ask.submit("Second");
  expect(ask.getSnapshot().citations).toEqual([citation]);

  ask.reset();
  expect(ask.getSnapshot()).toEqual({
    status: "idle",
    answer: "",
    citations: [],
  });
});
