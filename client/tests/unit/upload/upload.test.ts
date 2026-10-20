import { describe, expect, test } from "bun:test";

import { parseEnvironment } from "@config/environment";
import { uploadFormSchema, uploadResponseSchema } from "@schemas/upload/upload";

const response = {
  id: "25bca73f-3610-443c-9f74-8c2c2f91a54c",
  name: "policy.md",
  type: ".md",
  total: 1,
  chunks: [
    {
      text: "Policy",
      index: 0,
      count: 1,
      page: null,
      heading: null,
      section: null,
    },
  ],
};

describe("upload boundaries", () => {
  test("preserves the server ID and nullable chunk metadata", () => {
    expect(uploadResponseSchema.parse(response)).toEqual(response);
  });
  test("rejects malformed success payloads", () => {
    for (const value of [
      null,
      {},
      { ...response, id: "invented" },
      { ...response, total: -1 },
      { ...response, chunks: [{ text: "Policy", index: "0", count: 1 }] },
    ]) {
      expect(uploadResponseSchema.safeParse(value).success).toBe(false);
    }
  });
  test("requires an actual file", () => {
    expect(uploadFormSchema.safeParse({}).success).toBe(false);
    expect(uploadFormSchema.safeParse({ file: "policy.md" }).success).toBe(
      false,
    );
    expect(
      uploadFormSchema.safeParse({ file: new File(["policy"], "policy.md") })
        .success,
    ).toBe(true);
  });
  test("evaluates safely when File is unavailable during prerender", () => {
    const original = Object.getOwnPropertyDescriptor(globalThis, "File");
    try {
      Object.defineProperty(globalThis, "File", {
        value: undefined,
        configurable: true,
      });
      expect(uploadFormSchema.safeParse({ file: {} }).success).toBe(false);
    } finally {
      if (original) Object.defineProperty(globalThis, "File", original);
    }
  });
  test("normalizes valid API configuration and rejects unsafe or missing values", () => {
    expect(parseEnvironment("https://api.example/v1/").apiBaseUrl).toBe(
      "https://api.example/v1",
    );
    expect(parseEnvironment(" https://api.example/ ").apiBaseUrl).toBe(
      "https://api.example",
    );
    for (const value of [
      undefined,
      "",
      "/api",
      "http:api.example",
      "https:///api.example",
      "ftp://api.example",
      "https://user:pass@api.example",
      "https://api.example?secret=x",
      "https://api.example#x",
    ]) {
      expect(() => parseEnvironment(value)).toThrow(
        "NEXT_PUBLIC_ATLAS_API_BASE_URL",
      );
    }
  });
});
