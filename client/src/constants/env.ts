import { envSchema } from "@schemas/env";

export const env = envSchema.parse({
  API_BASE_URL: process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL,
});
