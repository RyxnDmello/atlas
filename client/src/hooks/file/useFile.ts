import { useState } from "react";
import { useQuery, type QueryFunctionContext } from "@tanstack/react-query";

import http from "@services/http/axios";
import {
  folderSession,
  checkFolderSession,
  currentFolderSession,
} from "@services/folder/session";

import {
  fileKey,
  fileError,
  fileResponse,
  FileFailure,
} from "@utils/file/file";
import { validFolderId } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

export default function useFile(id: string) {
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);
  const logout = useAuthStore((state) => state.logout);
  const accessToken = useAuthStore((state) => state.accessToken);

  const [denial, setDenial] = useState<FileFailure>();
  const session = folderSession();
  const valid = validFolderId(id);
  const enabled =
    valid &&
    status === "authenticated" &&
    user?.id === session?.user &&
    !!accessToken &&
    logout === "none" &&
    currentFolderSession(session);

  const onFile = async ({ signal }: QueryFunctionContext) => {
    checkFolderSession(session, signal);

    if (!valid) {
      throw new FileFailure(422, "INVALID_FILE_ID");
    }

    try {
      const response = await http.get<unknown>(`/files/${id}`, {
        isProtected: true,
        signal,
      });

      checkFolderSession(session, signal);

      const file = fileResponse(response, 200);

      if (file.id.toLowerCase() !== id) {
        throw new FileFailure(200, "INVALID_RESPONSE");
      }

      return file;
    } catch (error) {
      checkFolderSession(session, signal);

      throw fileError(error);
    }
  };

  const { data, error, isPending, isFetching, refetch } = useQuery({
    queryKey: fileKey(id),
    enabled,
    staleTime: 60_000,
    retry: false,
    retryOnMount: false,
    queryFn: onFile,
  });

  const onRefresh = async () => {
    checkFolderSession(session);

    if (!valid) {
      throw new FileFailure(422, "INVALID_FILE_ID");
    }

    const result = await refetch();

    checkFolderSession(session);
    setDenial(undefined);

    if (result.error) {
      throw result.error;
    }

    return result.data;
  };

  const onDenied = async (status: number, code: string) => {
    checkFolderSession(session);

    if (status === 404 && code === "FILE_NOT_FOUND") {
      setDenial(new FileFailure(status, code));

      return;
    }

    if (status === 409 && code === "FILE_NOT_READY") {
      setDenial(new FileFailure(status, code));

      await onRefresh();
    }
  };

  return {
    fileData: enabled && !denial && !error ? data : undefined,
    fileError: denial ?? error,
    isFileInvalid: !valid,
    isFileLoading: isPending,
    isFileFetching: isFetching,
    refreshFile: onRefresh,
    reconcileFile: onDenied,
  };
}
