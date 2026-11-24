import { createFileRoute } from "@tanstack/react-router";

import DrivePanel from "@components/Drive/DrivePanel";

function FolderPage() {
  const { id } = Route.useParams();

  return <DrivePanel folderId={id.toLowerCase()} />;
}

export const Route = createFileRoute("/drive/$id")({
  component: FolderPage,
});
