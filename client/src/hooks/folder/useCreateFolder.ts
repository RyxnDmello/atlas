import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import http from "@services/http/axios";
import { onAuthBoundary } from "@services/auth/auth";
import { folderSession, checkFolderSession } from "@services/folder/session";

import {
  folderSchema,
  folderCreateSchema,
  type FolderCreate,
} from "@schemas/folder/folder";

import {
  folderError,
  FolderFailure,
  folderResponse,
} from "@utils/folder/folder";

export default function useCreateFolder() {
  const pending = useRef(false);

  const session = folderSession();

  const cache = useQueryClient();

  const onCreate = async (input: FolderCreate) => {
    if (pending.current) {
      throw new FolderFailure(409, "REQUEST_PENDING");
    }

    checkFolderSession(session);

    const data = folderCreateSchema.parse(input);

    const controller = new AbortController();
    const unsubscribe = onAuthBoundary(() => controller.abort());

    pending.current = true;

    try {
      const response = await http.post<unknown>("/folders", data, {
        isProtected: true,
        signal: controller.signal,
      });

      checkFolderSession(session, controller.signal);

      const folder = folderResponse(response, 201, folderSchema);

      if (folder.parent_id !== data.parent_id) {
        throw new FolderFailure(201, "INVALID_RESPONSE");
      }

      await cache.invalidateQueries({
        queryKey: ["drive"],
      });

      checkFolderSession(session, controller.signal);

      return folder;
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
    mutationFn: onCreate,
  });

  return {
    createFolderError: error,
    isCreateFolderLoading: isPending,
    isCreateFolderSuccess: isSuccess,
    createFolder: mutateAsync,
  };
}
