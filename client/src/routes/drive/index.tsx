import { createFileRoute } from "@tanstack/react-router";

import DrivePanel from "@components/Drive/DrivePanel";

export const Route = createFileRoute("/drive/")({
  component: DrivePanel,
});
