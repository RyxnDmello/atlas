import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";
import { fileURLToPath, URL } from "node:url";
import { tanstackRouter } from "@tanstack/router-plugin/vite";

import { viteEnvSchema } from "./src/schemas/vite.ts";

const ALIASES = [
  "lib",
  "utils",
  "hooks",
  "stores",
  "schemas",
  "services",
  "providers",
  "constants",
  "components",
] as const;

export default defineConfig(({ mode }) => {
  const values = loadEnv(mode, process.cwd(), [
    "ATLAS_SERVER_PORT",
    "ATLAS_PREVIEW_PORT",
    "VITE_ATLAS_API_BASE_URL",
  ]);

  const environment = viteEnvSchema.safeParse({
    ATLAS_SERVER_PORT: values.ATLAS_SERVER_PORT,
    ATLAS_PREVIEW_PORT: values.ATLAS_PREVIEW_PORT,
    API_BASE_URL: values.VITE_ATLAS_API_BASE_URL,
  });

  if (!environment.success) {
    throw new Error(environment.error.issues[0].message);
  }

  return {
    plugins: [
      tanstackRouter({
        target: "react",
        autoCodeSplitting: true,
      }),
      react(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        ...Object.fromEntries(
          ALIASES.map((name) => [
            `@${name}`,
            fileURLToPath(new URL(`./src/${name}`, import.meta.url)),
          ]),
        ),
      },
    },
    server: {
      port: environment.data.ATLAS_SERVER_PORT,
      strictPort: true,
    },
    preview: {
      port: environment.data.ATLAS_PREVIEW_PORT,
      strictPort: true,
    },
  };
});
