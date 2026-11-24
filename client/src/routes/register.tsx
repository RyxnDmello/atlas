import { createFileRoute } from "@tanstack/react-router";

import RegisterPanel from "@components/Auth/RegisterPanel";

export const Route = createFileRoute("/register")({
  component: RegisterPanel,
});
