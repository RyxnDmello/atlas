import { envSchema } from "@schemas/env";

export const env = envSchema.parse({
  API_BASE_URL: import.meta.env.VITE_ATLAS_API_BASE_URL,
});
