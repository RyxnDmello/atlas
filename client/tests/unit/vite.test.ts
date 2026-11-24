import { expect, test } from "bun:test";

import { viteEnvSchema } from "@schemas/vite";

const api = {
  API_BASE_URL: "http://localhost:8080",
};

test("development and preview ports default independently to the existing origin", () => {
  const defaults = viteEnvSchema.parse(api);

  expect(defaults.ATLAS_SERVER_PORT).toBe(3000);
  expect(defaults.ATLAS_PREVIEW_PORT).toBe(3000);

  const development = viteEnvSchema.parse({
    ...api,
    ATLAS_SERVER_PORT: "3100",
  });

  expect(development.ATLAS_SERVER_PORT).toBe(3100);
  expect(development.ATLAS_PREVIEW_PORT).toBe(3000);

  const preview = viteEnvSchema.parse({
    ...api,
    ATLAS_PREVIEW_PORT: "4100",
  });

  expect(preview.ATLAS_SERVER_PORT).toBe(3000);
  expect(preview.ATLAS_PREVIEW_PORT).toBe(4100);
});

test("ports accept independent overrides and both valid boundaries", () => {
  const ports = viteEnvSchema.parse({
    ...api,
    ATLAS_SERVER_PORT: "1",
    ATLAS_PREVIEW_PORT: "65535",
  });

  expect(ports.ATLAS_SERVER_PORT).toBe(1);
  expect(ports.ATLAS_PREVIEW_PORT).toBe(65535);
});

for (const name of ["ATLAS_SERVER_PORT", "ATLAS_PREVIEW_PORT"] as const) {
  test(`${name} rejects invalid values without disclosing the input`, () => {
    for (const value of [
      "",
      " ",
      "0",
      "65536",
      "-1",
      "3000.5",
      "3e3",
      "0xBB8",
      "3000junk",
      "https://private.example",
    ]) {
      const result = viteEnvSchema.safeParse({
        ...api,
        [name]: value,
      });

      expect(result.success).toBe(false);

      if (!result.success) {
        expect(result.error.issues[0].message).toBe(
          `Set ${name} to a decimal integer from 1 to 65535.`,
        );
      }
    }
  });
}
