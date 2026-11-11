import { createFileRoute } from "@tanstack/react-router";

import VerifyPanel from "@components/Auth/VerifyPanel";

export const Route = createFileRoute("/verify")({
  component: VerifyPanel,
});
