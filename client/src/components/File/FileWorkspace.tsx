import { Link } from "@tanstack/react-router";

import useFile from "@hooks/file/useFile";

import AskPanel from "@components/Ask/AskPanel";
import { Button } from "@components/ui/button";
import NotFound from "@components/Common/NotFound";

import { FileFailure } from "@utils/file/file";

interface FileWorkspaceProps {
  fileId: string;
}

export default function FileWorkspace({ fileId }: FileWorkspaceProps) {
  const {
    fileData,
    fileError,
    isFileInvalid,
    isFileLoading,
    isFileFetching,
    refreshFile,
    reconcileFile,
  } = useFile(fileId);

  if (isFileInvalid) {
    return <NotFound />;
  }

  const refresh = (
    <Button
      disabled={isFileFetching}
      onClick={() => void refreshFile().catch(() => undefined)}
    >
      Refresh file
    </Button>
  );

  if (fileError) {
    const missing =
      fileError instanceof FileFailure && fileError.status === 404;

    return (
      <section className="space-y-3">
        <Link className="underline" to="/drive">
          Root
        </Link>

        <p role="alert">
          {missing
            ? "File not found."
            : "Unable to load this file. Refresh to check its current state."}
        </p>

        {refresh}
      </section>
    );
  }

  if (isFileLoading || !fileData) {
    return <p role="status">Loading file…</p>;
  }

  return (
    <section className="space-y-4">
      {fileData.folder_id ? (
        <Link
          className="underline"
          to="/drive/$id"
          params={{
            id: fileData.folder_id.toLowerCase(),
          }}
        >
          Back to Folder
        </Link>
      ) : (
        <Link className="underline" to="/drive">
          Back to Root
        </Link>
      )}

      <div>
        <h1 className="text-xl font-semibold">{fileData.name}</h1>

        {fileData.description && <p>{fileData.description}</p>}
      </div>

      <dl className="space-y-2 wrap-anywhere">
        <dt>Original name</dt>
        <dd>{fileData.original_name}</dd>
        <dt>Type</dt>
        <dd>{fileData.extension}</dd>
        <dt>Size</dt>
        <dd>{fileData.size_bytes.toLocaleString()} bytes</dd>
        <dt>Status</dt>
        <dd>{fileData.status}</dd>
      </dl>

      {refresh}

      {isFileFetching && <p role="status">Refreshing file…</p>}

      {fileData.status === "ready" ? (
        <AskPanel fileId={fileId} onDenied={reconcileFile} />
      ) : (
        <p role="status">
          Ask is unavailable while this file is {fileData.status}.
        </p>
      )}
    </section>
  );
}
