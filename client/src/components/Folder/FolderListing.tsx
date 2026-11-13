import { Link } from "@tanstack/react-router";

import type { FolderListing as Listing } from "@schemas/folder/folder";

interface FolderListingProps {
  data: Listing;
}

export default function FolderListing({ data }: FolderListingProps) {
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
          <p className="font-medium">{file.name}</p>
          <p className="text-sm text-muted-foreground">File · {file.status}</p>
          {file.description && <p className="text-sm">{file.description}</p>}
        </li>
      ))}
    </ul>
  );
}
