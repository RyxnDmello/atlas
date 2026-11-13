import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import http from "@services/http/axios";
import { onAuthBoundary } from "@services/auth/auth";
import { folderSession, checkFolderSession } from "@services/folder/session";

import {
  folderSchema,
  folderPatchSchema,
  type Folder,
  type FolderPatch,
} from "@schemas/folder/folder";

import {
  folderError,
  validFolderId,
  FolderFailure,
  folderResponse,
} from "@utils/folder/folder";

export default function useEditFolder(folder: Folder | null) {
  const pending = useRef(false);

  const session = folderSession();

  const cache = useQueryClient();

  const onEdit = async (input: FolderPatch) => {
    if (pending.current) {
      throw new FolderFailure(409, "REQUEST_PENDING");
    }

    checkFolderSession(session);

    if (!folder || !validFolderId(folder.id)) {
      throw new FolderFailure(422, "INVALID_FOLDER_ID");
    }

    const data = folderPatchSchema.parse(input);

    const controller = new AbortController();
    const unsubscribe = onAuthBoundary(() => controller.abort());

    pending.current = true;

    try {
      const response = await http.patch<unknown>(
        `/folders/${folder.id}`,
        data,
        {
          isProtected: true,
          signal: controller.signal,
        },
      );

      checkFolderSession(session, controller.signal);

      const updated = folderResponse(response, 200, folderSchema);

      if (updated.id !== folder.id || updated.parent_id !== folder.parent_id) {
        throw new FolderFailure(200, "INVALID_RESPONSE");
      }

      await cache.invalidateQueries({
        queryKey: ["drive"],
      });

      checkFolderSession(session, controller.signal);

      return updated;
    } catch (error) {
      checkFolderSession(session, controller.signal);

      const failure = folderError(error);

      if (failure.uncertain) {
        await cache.invalidateQueries({
          queryKey: ["drive"],
          refetchType: "none",
        });
      }

      checkFolderSession(session, controller.signal);

      throw failure;
    } finally {
      unsubscribe();
      pending.current = false;
    }
  };

  const { error, isPending, isSuccess, mutateAsync } = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onEdit,
  });

  return {
    editFolderError: error,
    isEditFolderLoading: isPending,
    isEditFolderSuccess: isSuccess,
    editFolder: mutateAsync,
  };
}
