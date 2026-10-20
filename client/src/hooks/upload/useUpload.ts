"use client";

import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { useRef, useState } from "react";
import { z } from "zod";

import {
  uploadResponseSchema,
  type UploadResponse,
} from "@schemas/upload/upload";
import { http } from "@services/http/client";

const errorSchema = z.object({ error: z.string().min(1), code: z.string() });

export async function uploadFile(file: File) {
  const body = new FormData();
  body.append("file", file);

  try {
    const response = await http.post<unknown>("/documents/upload", body);
    const result = uploadResponseSchema.safeParse(response.data);
    if (!result.success)
      throw new Error(
        "The server returned an invalid upload response. Try again.",
      );

    return result.data;
  } catch (error: unknown) {
    if (axios.isAxiosError<unknown>(error)) {
      const result = errorSchema.safeParse(error.response?.data);
      throw new Error(
        result.success
          ? result.data.error
          : "Upload failed. Check the API connection and try again.",
      );
    }

    throw error;
  }
}

export function useUpload() {
  const [active, setActive] = useState<
    Pick<UploadResponse, "name" | "type" | "total"> & { fileId: string }
  >();
  const locked = useRef(false);
  const mutation = useMutation({
    mutationFn: uploadFile,
    retry: false,
    gcTime: 0,
  });

  async function submit(file: File) {
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
      // Mutation state exposes failure while the last successful scope remains active.
    } finally {
      locked.current = false;
    }
  }

  return { active, submit, pending: mutation.isPending, error: mutation.error };
}
