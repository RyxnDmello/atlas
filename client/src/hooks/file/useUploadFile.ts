import { useMutation } from "@tanstack/react-query";

import useFileLifetime from "@hooks/file/useFileLifetime";

import http from "@services/http/axios";

import type { FileUpload } from "@schemas/file/file";

import { fileBody, fileResponse, FileFailure } from "@utils/file/file";

export default function useUploadFile(parent: string | null) {
  const lifetime = useFileLifetime();

  const onUpload = async (input: FileUpload) => {
    const body = fileBody(input, parent);
    const request = lifetime.begin();

    try {
      const response = await http.post<unknown>("/files", body, {
        isProtected: true,
        signal: request.controller.signal,
      });

      lifetime.check(request);

      const file = fileResponse(response, 201);

      if (file.status !== "ready" || file.folder_id !== parent) {
        throw new FileFailure(response.status, "INVALID_RESPONSE");
      }

      await lifetime.invalidate(request, true);

      return file;
    } catch (error) {
      return await lifetime.reject(request, error);
    } finally {
      lifetime.end(request);
    }
  };

  const { error, isPending, mutateAsync } = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onUpload,
  });

  return {
    uploadFileError: error,
    isUploadFileLoading: isPending,
    uploadFile: mutateAsync,
  };
}
