import { z } from "zod";

import { envSchema } from "./env.ts";

const portSchema = (name: string) => {
  const message = `Set ${name} to a decimal integer from 1 to 65535.`;

  return z
    .string({
      error: message,
    })
    .regex(/^\d+$/, message)
    .transform(Number)
    .pipe(z.number().int(message).min(1, message).max(65535, message))
    .default(3000);
};

export const viteEnvSchema = envSchema.extend({
  ATLAS_SERVER_PORT: portSchema("ATLAS_SERVER_PORT"),
  ATLAS_PREVIEW_PORT: portSchema("ATLAS_PREVIEW_PORT"),
});
