import { useMutation } from "@tanstack/react-query";

import useFileLifetime from "@hooks/file/useFileLifetime";

import http from "@services/http/axios";

import { validFolderId } from "@utils/folder/folder";
import { fileError, fileResponse, FileFailure } from "@utils/file/file";

export default function useReadFile() {
  const lifetime = useFileLifetime();

  const onRead = async (id: string) => {
    if (!validFolderId(id)) {
      throw new FileFailure(422, "INVALID_FILE_ID");
    }

    const request = lifetime.begin();

    try {
      const response = await http.get<unknown>(`/files/${id}`, {
        isProtected: true,
        signal: request.controller.signal,
      });

      lifetime.check(request);

      if (response.status === 404) {
        return null;
      }

      const file = fileResponse(response, 200);

      if (file.id !== id) {
        throw new FileFailure(200, "INVALID_RESPONSE");
      }

      return file;
    } catch (error) {
      lifetime.check(request);

      if (fileError(error).status === 404) {
        return null;
      }

      throw fileError(error);
    } finally {
      lifetime.end(request);
    }
  };

  const { error, isPending, mutateAsync } = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onRead,
  });

  return {
    readFileError: error,
    isReadFileLoading: isPending,
    readFile: mutateAsync,
  };
}
