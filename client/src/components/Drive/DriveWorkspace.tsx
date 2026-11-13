import { Link } from "@tanstack/react-router";

import useFolder from "@hooks/folder/useFolder";

import { Button } from "@components/ui/button";
import NotFound from "@components/Common/NotFound";
import FolderDialog from "@components/Folder/FolderDialog";
import FolderListing from "@components/Folder/FolderListing";

import { folderFeedback, FolderFailure } from "@utils/folder/folder";

interface DriveWorkspaceProps {
  folderId: string | null;
}

export default function DriveWorkspace({ folderId }: DriveWorkspaceProps) {
  const {
    folderData,
    folderError,
    isFolderLoading,
    isFolderFetching,
    isFolderInvalid,
    refreshFolder,
  } = useFolder(folderId);

  if (isFolderInvalid) {
    return <NotFound />;
  }

  if (folderError instanceof FolderFailure && folderError.status === 404) {
    return (
      <div className="space-y-3">
        <Link className="underline" to="/drive">
          Root
        </Link>
        <p role="alert">Folder not found.</p>
      </div>
    );
  }

  if (folderError) {
    return (
      <div className="space-y-3">
        <Link className="underline" to="/drive">
          Root
        </Link>

        <p role="alert">{folderFeedback(folderError)}</p>

        <Button
          disabled={isFolderFetching}
          onClick={() => void refreshFolder().catch(() => undefined)}
        >
          Retry
        </Button>
      </div>
    );
  }

  if (isFolderLoading || !folderData) {
    return <p role="status">Loading folder…</p>;
  }

  const folder = folderData.folder;

  return (
    <section className="space-y-4">
      <nav className="flex gap-4" aria-label="Folder navigation">
        <Link
          className="underline"
          to="/drive"
          activeOptions={{
            exact: true,
          }}
        >
          Root
        </Link>

        {folder &&
          (folder.parent_id ? (
            <Link
              className="underline"
              to="/drive/$id"
              params={{
                id: folder.parent_id,
              }}
            >
              Up
            </Link>
          ) : (
            <Link className="underline" to="/drive">
              Up
            </Link>
          ))}
      </nav>

      <div>
        <h2 className="text-xl font-semibold">{folder?.name ?? "My Drive"}</h2>

        {folder?.description && <p>{folder.description}</p>}
      </div>

      <div className="flex flex-wrap gap-2">
        <FolderDialog parent={folderId} refresh={refreshFolder} />

        {folder && (
          <FolderDialog
            parent={folderId}
            folder={folder}
            refresh={refreshFolder}
          />
        )}
      </div>

      {isFolderFetching && <p role="status">Refreshing folder…</p>}

      <FolderListing data={folderData} />
    </section>
  );
}
