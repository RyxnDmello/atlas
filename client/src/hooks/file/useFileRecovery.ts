import { useEffect, useRef, useState } from "react";

import useReadFile from "@hooks/file/useReadFile";

import { folderSession, currentFolderSession } from "@services/folder/session";

import type { FileRecord } from "@schemas/file/file";
import type { FolderListing } from "@schemas/folder/folder";

import { fileError, fileFeedback } from "@utils/file/file";

export interface FileRecoveryProps {
  file?: FileRecord;
  refresh(): Promise<FolderListing | undefined>;
}

export default function useFileRecovery({ file, refresh }: FileRecoveryProps) {
  const active = useRef(true);
  const pending = useRef(false);

  const session = folderSession();

  const [blocked, setBlocked] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [record, setRecord] = useState<FileRecord | null | undefined>();

  const { readFile } = useReadFile();

  useEffect(() => {
    active.current = true;

    return () => {
      active.current = false;
    };
  }, []);

  const current = () => active.current && currentFolderSession(session);

  const onFailure = (error: unknown) => {
    if (!current()) {
      return;
    }

    setBlocked(fileError(error).reconcile);
    setFeedback(fileFeedback(error));
  };

  const onReset = () => {
    if (current()) {
      setBlocked(false);
      setFeedback(null);
      setRecord(undefined);
    }
  };

  const onRefresh = async () => {
    if (pending.current || !current()) {
      return undefined;
    }

    pending.current = true;
    setRefreshing(true);

    try {
      const updated = file ? await readFile(file.id) : undefined;

      if (!current()) {
        return undefined;
      }

      const listing = await refresh();

      if (!current() || !listing) {
        return undefined;
      }

      setBlocked(false);
      setRecord(updated);

      setFeedback(
        file
          ? updated
            ? `Current file status: ${updated.status}. Choose an action for this state.`
            : "The file is currently unavailable. This does not confirm the outcome of the earlier request."
          : "Folder refreshed. Check its contents before choosing another upload; a matching name alone does not confirm the earlier upload.",
      );

      return updated;
    } catch {
      if (current()) {
        setBlocked(true);

        setFeedback(
          "The current state could not be read. Refresh again before trying another operation.",
        );
      }
    } finally {
      pending.current = false;

      if (current()) {
        setRefreshing(false);
      }
    }
  };

  return {
    fileRecord: record === undefined ? file : record,
    isFileBlocked: blocked,
    fileFeedback: feedback,
    isFileRefreshing: refreshing,
    isFileCurrent: current,
    resetFile: onReset,
    failFile: onFailure,
    refreshFile: onRefresh,
  };
}
