import { afterEach, expect, test } from "bun:test";

const previous = process.env.VITE_ATLAS_API_BASE_URL;

process.env.VITE_ATLAS_API_BASE_URL = "http://localhost:8080";

const { default: fetch } = await import("@services/http/fetch");
const { coordination } = await import("@services/auth/auth");
const { response: authenticated, seedCredentials } =
  await import("../auth/fixtures");

await seedCredentials(authenticated, coordination);

if (previous === undefined) {
  delete process.env.VITE_ATLAS_API_BASE_URL;
} else {
  process.env.VITE_ATLAS_API_BASE_URL = previous;
}

const original = globalThis.fetch;

type FetchHandler = (
  input: string | URL | Request,
  options?: RequestInit,
) => Promise<Response>;

const mock = (handler: FetchHandler): void => {
  globalThis.fetch = Object.assign(handler, {
    preconnect: original.preconnect,
  });
};

afterEach(() => {
  globalThis.fetch = original;
});

test("get resolves relative paths, preserves options and returns HTTP errors untouched", async () => {
  const response = new Response("unavailable", {
    status: 503,
  });

  const owner = new AbortController();

  mock(async (url, options) => {
    expect(url).toBe("http://localhost:8080/system/health?verbose=true");
    expect(options?.method).toBe("GET");
    expect(options?.credentials).toBe("omit");
    expect(options?.signal).toBe(owner.signal);
    expect(options?.cache).toBe("no-store");

    return response;
  });

  expect(
    await fetch.get("system/health?verbose=true", {
      signal: owner.signal,
      cache: "no-store",
    }),
  ).toBe(response);
  expect(response.bodyUsed).toBe(false);
});

test("post serializes JSON, merges each native header input and leaves a stream unread", async () => {
  const owner = new AbortController();

  const headers: HeadersInit[] = [
    {
      "X-Request": "test",
    },
    [["X-Request", "test"]],
    new Headers({
      "X-Request": "test",
    }),
  ];

  for (const input of headers) {
    const response = new Response("event: done\ndata: {}\n\n");

    mock(async (url, options) => {
      expect(url).toBe("http://localhost:8080/files/exact-id/ask");
      expect(options?.method).toBe("POST");
      expect(options?.body).toBe('{"question":"Question"}');
      expect(options?.signal).toBe(owner.signal);
      expect(options?.credentials).toBe("omit");
      expect(new Headers(options?.headers).get("Content-Type")).toBe(
        "application/json",
      );
      expect(new Headers(options?.headers).get("X-Request")).toBe("test");

      return response;
    });

    const result = await fetch.post(
      "/files/exact-id/ask",
      {
        question: "Question",
      },
      {
        headers: input,
        signal: owner.signal,
      },
    );

    expect(result).toBe(response);
    expect(result.bodyUsed).toBe(false);
    expect(result.body?.locked).toBe(false);
  }
});

test("post honors caller content type and credentials", async () => {
  mock(async (_url, options) => {
    expect(new Headers(options?.headers).get("Content-Type")).toBe(
      "application/vnd.atlas+json",
    );
    expect(options?.credentials).toBe("include");

    return new Response(null);
  });

  await fetch.post(
    "/custom",
    {},
    {
      headers: {
        "content-type": "application/vnd.atlas+json",
      },
      credentials: "include",
    },
  );
});

test("base preserves raw multipart bodies without JSON headers or serialization", async () => {
  const body = new FormData();

  body.append("file", new File(["synthetic"], "fixture.md"));

  mock(async (url, options) => {
    expect(url).toBe("http://localhost:8080/files");
    expect(options?.method).toBe("POST");
    expect(options?.body).toBe(body);
    expect(new Headers(options?.headers).has("Content-Type")).toBe(false);

    return new Response(null);
  });

  await fetch.base("/files", {
    method: "POST",
    body,
  });
});

test("base forwards network failures and aborts to the owner", async () => {
  const owner = new AbortController();

  owner.abort();

  mock(async (_url, options) => {
    expect(options?.signal).toBe(owner.signal);

    throw new DOMException("Aborted", "AbortError");
  });

  await expect(
    fetch.get("/cancelled", {
      signal: owner.signal,
    }),
  ).rejects.toThrow(/aborted/i);
});
