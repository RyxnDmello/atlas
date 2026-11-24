import { expect, test } from "bun:test";

import { envSchema } from "@schemas/env";

test("normalizes valid API configuration and rejects unsafe or missing values", () => {
  expect(
    envSchema.parse({
      API_BASE_URL: "https://api.example/v1/",
    }).API_BASE_URL,
  ).toBe("https://api.example/v1");

  expect(
    envSchema.parse({
      API_BASE_URL: " https://api.example/ ",
    }).API_BASE_URL,
  ).toBe("https://api.example");

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
    expect(() =>
      envSchema.parse({
        API_BASE_URL: value,
      }),
    ).toThrow("VITE_ATLAS_API_BASE_URL");
  }
});
