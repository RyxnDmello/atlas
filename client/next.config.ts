import type { NextConfig } from "next";

import { envSchema } from "./src/schemas/env";

envSchema.parse({
  API_BASE_URL: process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL,
});

const config: NextConfig = {
  agentRules: false,
  output: "export",
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default config;
