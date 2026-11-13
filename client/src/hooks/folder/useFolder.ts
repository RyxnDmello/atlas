import { useQuery, type QueryFunctionContext } from "@tanstack/react-query";

import http from "@services/http/axios";
import {
  folderSession,
  checkFolderSession,
  currentFolderSession,
} from "@services/folder/session";

import { listingSchema } from "@schemas/folder/folder";

import {
  folderKey,
  folderError,
  validFolderId,
  FolderFailure,
  folderResponse,
} from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

export default function useFolder(id: string | null) {
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);
  const logout = useAuthStore((state) => state.logout);
  const accessToken = useAuthStore((state) => state.accessToken);

  const session = folderSession();

  const valid = id === null || validFolderId(id);
  const enabled =
    valid &&
    status === "authenticated" &&
    user?.id === session?.user &&
    !!accessToken &&
    logout === "none" &&
    currentFolderSession(session);

  const onFolder = async ({ signal }: QueryFunctionContext) => {
    checkFolderSession(session, signal);

    if (!valid) {
      throw new FolderFailure(422, "INVALID_FOLDER_ID");
    }

    try {
      const response = await http.get<unknown>(
        id === null ? "/folders" : `/folders/${id}`,
        {
          isProtected: true,
          signal,
        },
      );

      checkFolderSession(session, signal);

      const data = folderResponse(response, 200, listingSchema);

      if (
        (id === null && data.folder !== null) ||
        (id !== null && data.folder?.id !== id)
      ) {
        throw new FolderFailure(200, "INVALID_RESPONSE");
      }

      return data;
    } catch (error) {
      checkFolderSession(session, signal);

      throw folderError(error);
    }
  };

  const { data, error, isPending, isFetching, refetch } = useQuery({
    queryKey: folderKey(id),
    enabled,
    staleTime: 60_000,
    retry: false,
    retryOnMount: false,
    queryFn: onFolder,
  });

  const onRefresh = async () => {
    checkFolderSession(session);

    if (!valid) {
      throw new FolderFailure(422, "INVALID_FOLDER_ID");
    }

    const result = await refetch();

    checkFolderSession(session);

    if (result.error) {
      throw result.error;
    }

    return result.data;
  };

  const folderData = enabled ? data : undefined;

  const isFolderInvalid = !valid;

  return {
    folderData,
    isFolderInvalid,
    folderError: error,
    isFolderLoading: isPending,
    isFolderFetching: isFetching,
    refreshFolder: onRefresh,
  };
}
