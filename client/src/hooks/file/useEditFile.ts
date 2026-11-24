import { useMutation } from "@tanstack/react-query";

import useFileLifetime from "@hooks/file/useFileLifetime";

import http from "@services/http/axios";

import {
  filePatchSchema,
  type FileRecord,
  type FilePatch,
} from "@schemas/file/file";

import { fileResponse, sameFile, FileFailure } from "@utils/file/file";

export default function useEditFile(file: FileRecord | null) {
  const lifetime = useFileLifetime();

  const onEdit = async (input: FilePatch) => {
    if (!file || file.status !== "ready") {
      throw new FileFailure(409, "FILE_NOT_READY");
    }

    const data = filePatchSchema.parse(input);

    const request = lifetime.begin();

    try {
      const response = await http.patch<unknown>(`/files/${file.id}`, data, {
        isProtected: true,
        signal: request.controller.signal,
      });

      lifetime.check(request);

      const updated = fileResponse(response, 200);

      if (!sameFile(file, updated) || updated.status !== "ready") {
        throw new FileFailure(response.status, "INVALID_RESPONSE");
      }

      await lifetime.invalidate(request, true);

      return updated;
    } catch (error) {
      return await lifetime.reject(request, error);
    } finally {
      lifetime.end(request);
    }
  };

  const { error, isPending, mutateAsync } = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onEdit,
  });

  return {
    editFileError: error,
    isEditFileLoading: isPending,
    editFile: mutateAsync,
  };
}
