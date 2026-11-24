import { createFileRoute } from "@tanstack/react-router";

import LoginPanel from "@components/Auth/LoginPanel";

export const Route = createFileRoute("/login")({
  component: LoginPanel,
});
