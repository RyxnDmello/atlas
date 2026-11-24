import { useMutation } from "@tanstack/react-query";

import useFileLifetime from "@hooks/file/useFileLifetime";

import http from "@services/http/axios";

import type { FileRecord } from "@schemas/file/file";

import { FileFailure } from "@utils/file/file";

export default function useDeleteFile(file: FileRecord) {
  const lifetime = useFileLifetime();

  const onDelete = async () => {
    if (file.status !== "ready" && file.status !== "deleting") {
      throw new FileFailure(409, "FILE_NOT_READY");
    }

    const request = lifetime.begin();

    try {
      const response = await http.delete<unknown>(`/files/${file.id}`, {
        isProtected: true,
        signal: request.controller.signal,
      });

      lifetime.check(request);

      if (response.status !== 204) {
        throw new FileFailure(response.status, "INVALID_RESPONSE");
      }

      await lifetime.invalidate(request, true);
    } catch (error) {
      await lifetime.reject(request, error);
    } finally {
      lifetime.end(request);
    }
  };

  const { error, isPending, mutateAsync } = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onDelete,
  });

  return {
    deleteFileError: error,
    isDeleteFileLoading: isPending,
    deleteFile: mutateAsync,
  };
}
