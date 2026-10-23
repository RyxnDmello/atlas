"use client";

import { useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import uploadFile from "@services/upload/uploadFile";

import type { UploadResponse } from "@schemas/upload/upload";

export interface ActiveFile extends Pick<
  UploadResponse,
  "name" | "type" | "total"
> {
  fileId: string;
}

export interface UseUploadResult {
  active: ActiveFile | undefined;
  pending: boolean;
  error: Error | null;
  submit(file: File): Promise<void>;
}

export default function useUpload(): UseUploadResult {
  const [active, setActive] = useState<ActiveFile>();

  const locked = useRef(false);

  const mutation = useMutation({
    mutationFn: uploadFile,
    retry: false,
    gcTime: 0,
  });

  async function submit(file: File): Promise<void> {
    if (locked.current) return;

    locked.current = true;

    try {
      const result = await mutation.mutateAsync(file);

      setActive({
        fileId: result.id,
        name: result.name,
        type: result.type,
        total: result.total,
      });
    } catch {
      return;
    } finally {
      locked.current = false;
    }
  }

  return {
    active,
    submit,
    error: mutation.error,
    pending: mutation.isPending,
  };
}
