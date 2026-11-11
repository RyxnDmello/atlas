import js from "@eslint/js";
import globals from "globals";
import hooks from "eslint-plugin-react-hooks";
import parser from "@typescript-eslint/parser";
import typescript from "@typescript-eslint/eslint-plugin";

import { globalIgnores } from "eslint/config";

export default [
  globalIgnores([
    "dist/**",
    ".tanstack/**",
    "node_modules/**",
    "src/routeTree.gen.ts",
  ]),
  {
    files: ["**/*.{ts,tsx,mts}"],
    languageOptions: {
      parser,
      globals: {
        ...globals.node,
        ...globals.browser,
      },
    },
    plugins: {
      "react-hooks": {
        rules: hooks.rules,
      },
      "@typescript-eslint": {
        rules: typescript.rules,
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...hooks.configs.recommended.rules,
      ...typescript.configs.recommended.rules,
      ...typescript.configs["eslint-recommended"].overrides?.[0].rules,
      "no-empty": [
        "error",
        {
          allowEmptyCatch: true,
        },
      ],
    },
  },
];
