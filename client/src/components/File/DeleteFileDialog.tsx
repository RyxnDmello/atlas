import { useRef, useState } from "react";

import useFileRecovery, {
  type FileRecoveryProps,
} from "@hooks/file/useFileRecovery";
import useDeleteFile from "@hooks/file/useDeleteFile";

import { Button } from "@components/ui/button";
import {
  Dialog,
  DialogTitle,
  DialogClose,
  DialogContent,
  DialogTrigger,
  DialogDescription,
} from "@components/ui/dialog";

import type { FileRecord } from "@schemas/file/file";

interface DeleteFileDialogProps extends FileRecoveryProps {
  file: FileRecord;
}

export default function DeleteFileDialog({
  file,
  refresh,
}: DeleteFileDialogProps) {
  const pending = useRef(false);

  const [open, setOpen] = useState(false);

  const {
    fileRecord,
    fileFeedback,
    isFileBlocked,
    isFileRefreshing,
    failFile,
    resetFile,
    refreshFile,
    isFileCurrent,
  } = useFileRecovery({
    file,
    refresh,
  });

  const { deleteFile, isDeleteFileLoading } = useDeleteFile(fileRecord ?? file);

  const busy = isDeleteFileLoading || isFileRefreshing;

  const allowed =
    fileRecord?.status === "ready" || fileRecord?.status === "deleting";

  const label =
    fileRecord?.status === "deleting" ? "Retry delete" : "Delete File";

  const onDelete = async () => {
    if (
      pending.current ||
      busy ||
      isFileBlocked ||
      !allowed ||
      !isFileCurrent()
    ) {
      return;
    }

    pending.current = true;

    try {
      await deleteFile();

      if (isFileCurrent()) {
        setOpen(false);
        resetFile();
      }
    } catch (error) {
      failFile(error);
    } finally {
      pending.current = false;
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!pending.current && !busy) {
          setOpen(next);
        }
      }}
    >
      <DialogTrigger render={<Button variant="outline" />}>
        {label}
      </DialogTrigger>

      <DialogContent>
        <DialogTitle>{label}</DialogTitle>

        <DialogDescription>
          Permanently delete “{fileRecord?.name ?? file.name}” and its indexed
          content? This cannot be undone.
        </DialogDescription>

        {fileRecord?.status === "deleting" && (
          <p>Deletion was started. Confirm to retry finishing it.</p>
        )}

        {!allowed && (
          <p>This file is unavailable or processing. Deletion is disabled.</p>
        )}

        {fileFeedback && <p role="alert">{fileFeedback}</p>}

        <div className="mt-4 flex flex-wrap gap-2">
          <Button
            disabled={busy || isFileBlocked || !allowed}
            onClick={() => void onDelete()}
          >
            {busy
              ? "Working…"
              : fileRecord?.status === "deleting"
                ? "Retry permanent delete"
                : "Permanently delete"}
          </Button>

          {isFileBlocked && (
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => void refreshFile()}
            >
              Refresh current state
            </Button>
          )}

          <DialogClose render={<Button variant="outline" disabled={busy} />}>
            Cancel
          </DialogClose>
        </div>
      </DialogContent>
    </Dialog>
  );
}
