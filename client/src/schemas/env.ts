import { z } from "zod";

const message =
  "Set VITE_ATLAS_API_BASE_URL to an absolute HTTP(S) API URL without credentials, query, or fragment.";

export const envSchema = z.object({
  API_BASE_URL: z
    .string({
      error: message,
    })
    .trim()
    .pipe(
      z.url({
        error: message,
      }),
    )
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
    }, message)
    .transform((value) => value.replace(/\/+$/, "")),
});
