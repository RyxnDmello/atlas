import { z } from "zod";
import { isAxiosError } from "axios";

import axios from "@services/http/axios";

import {
  uploadResponseSchema,
  type UploadResponse,
} from "@schemas/upload/upload";

const errorSchema = z.object({
  code: z.string(),
  error: z.string().min(1),
});

export default async function uploadFile(file: File): Promise<UploadResponse> {
  const body = new FormData();
  body.append("file", file);

  try {
    const response = await axios.post<unknown>("/documents/upload", body);
    const result = uploadResponseSchema.safeParse(response.data);
    if (!result.success)
      throw new Error(
        "The server returned an invalid upload response. Try again.",
      );

    return result.data;
  } catch (error: unknown) {
    if (isAxiosError<unknown>(error)) {
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
