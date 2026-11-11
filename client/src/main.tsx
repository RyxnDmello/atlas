import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "@tanstack/react-router";

import QueryProvider from "@providers/query/queryProvider";

import { router } from "./router";

import "./styles.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Atlas root element is missing.");
}

createRoot(root).render(
  <StrictMode>
    <QueryProvider>
      <RouterProvider router={router} />
    </QueryProvider>
  </StrictMode>,
);
