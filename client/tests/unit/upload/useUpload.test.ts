import { afterEach, expect, test } from "bun:test";
import type { AxiosAdapter } from "axios";

const previous = process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL;
process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL = "http://localhost:8080";
const { http } = await import("@services/http/client");
const { uploadFile } = await import("@hooks/upload/useUpload");
if (previous === undefined) delete process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL;
else process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL = previous;

const original = http.defaults.adapter;
afterEach(() => {
  http.defaults.adapter = original;
});

test("sends one file with browser-owned multipart encoding and validates the returned ID", async () => {
  const file = new File(["policy"], "policy.md");
  const id = "25bca73f-3610-443c-9f74-8c2c2f91a54c";
  const adapter: AxiosAdapter = async (config) => {
    expect(config.url).toBe("/documents/upload");
    expect(config.data).toBeInstanceOf(FormData);
    expect(config.data.get("file").name).toBe("policy.md");
    expect(config.headers.getContentType()).not.toContain("boundary=");
    return {
      config,
      status: 200,
      statusText: "OK",
      headers: {},
      data: { id, name: file.name, type: ".md", total: 0, chunks: [] },
    };
  };
  http.defaults.adapter = adapter;
  expect((await uploadFile(file)).id).toBe(id);
});

test("rejects malformed 200 responses instead of adopting a false scope", async () => {
  http.defaults.adapter = async (config) => ({
    config,
    status: 200,
    statusText: "OK",
    headers: {},
    data: { id: "false" },
  });
  await expect(uploadFile(new File(["policy"], "policy.md"))).rejects.toThrow(
    "invalid upload response",
  );
});
