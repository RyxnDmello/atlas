import { createFileRoute } from "@tanstack/react-router";

import FilePanel from "@components/File/FilePanel";

function FilePage() {
  const { id } = Route.useParams();

  return <FilePanel fileId={id.toLowerCase()} />;
}

export const Route = createFileRoute("/drive_/file/$id")({
  component: FilePage,
});
