import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "src/api/gpm-api.ts"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "max-lines": ["error", { max: 300, skipBlankLines: true, skipComments: true }],
      "no-restricted-globals": [
        "error",
        {
          name: "fetch",
          message: "Use web/src/api/client.ts instead of fetch directly.",
        },
      ],
    },
  },
  {
    files: ["src/api/client.ts", "src/api/request.ts"],
    rules: {
      "no-restricted-globals": "off",
    },
  },
);
