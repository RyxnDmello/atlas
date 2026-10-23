import { z } from "zod";

export const environmentSchema = z.object({
  apiBaseUrl: z
    .string()
    .trim()
    .pipe(z.url())
    .refine((value) => {
      try {
        const url = new URL(value);
        return (
          /^https?:\/\/[^/]/i.test(value) &&
          ["http:", "https:"].includes(url.protocol) &&
          !url.username &&
          !url.password &&
          !url.search &&
          !url.hash &&
          !value.includes("?") &&
          !value.includes("#")
        );
      } catch {
        return false;
      }
    }, "API base URL must be HTTP(S) without credentials, query, or fragment")
    .transform((value) => value.replace(/\/+$/, "")),
});

export function parseEnvironment(value: unknown) {
  const result = environmentSchema.safeParse({
    apiBaseUrl: value,
  });
  if (!result.success)
    throw new Error(
      "Set NEXT_PUBLIC_ATLAS_API_BASE_URL to an absolute HTTP(S) API URL without credentials, query, or fragment.",
    );
  return result.data;
}
