import { Link } from "@tanstack/react-router";

import FileDialog from "@components/File/FileDialog";
import DeleteFileDialog from "@components/File/DeleteFileDialog";

import type { FolderListing as Listing } from "@schemas/folder/folder";

interface FolderListingProps {
  data: Listing;
  refresh(): Promise<Listing | undefined>;
}

export default function FolderListing({ data, refresh }: FolderListingProps) {
  if (data.folders.length === 0 && data.files.length === 0) {
    return <p>This folder is empty.</p>;
  }

  return (
    <ul className="divide-y rounded-lg border">
      {data.folders.map((folder) => (
        <li key={folder.id} className="space-y-1 p-3">
          <Link
            className="font-medium underline"
            to="/drive/$id"
            params={{
              id: folder.id,
            }}
          >
            {folder.name}
          </Link>

          <p className="text-sm text-muted-foreground">Folder</p>

          {folder.description && (
            <p className="text-sm">{folder.description}</p>
          )}
        </li>
      ))}

      {data.files.map((file) => (
        <li key={file.id} className="space-y-1 p-3">
          <Link
            className="font-medium underline"
            to="/drive/file/$id"
            params={{
              id: file.id,
            }}
          >
            {file.name}
          </Link>

          <p className="text-sm text-muted-foreground">
            File · {file.extension} · {file.size_bytes.toLocaleString()} bytes ·{" "}
            {file.status}
          </p>

          {file.description && <p className="text-sm">{file.description}</p>}

          <div className="flex flex-wrap gap-2">
            {file.status === "ready" && (
              <FileDialog
                parent={file.folder_id}
                file={file}
                refresh={refresh}
              />
            )}

            {(file.status === "ready" || file.status === "deleting") && (
              <DeleteFileDialog file={file} refresh={refresh} />
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
