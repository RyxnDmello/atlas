import { z } from "zod";

export const uploadFormSchema = z.object({
  file: z.custom<File>(
    (value) => typeof File !== "undefined" && value instanceof File,
    "Choose a file to upload.",
  ),
});

export const uploadResponseSchema = z.object({
  id: z.uuid(),
  name: z.string(),
  type: z.string(),
  total: z.number().int().nonnegative(),
  chunks: z.array(
    z.object({
      text: z.string(),
      index: z.number().int(),
      count: z.number().int(),
      page: z.number().int().nullable().optional(),
      heading: z.string().nullable().optional(),
      section: z.string().nullable().optional(),
    }),
  ),
});

export type UploadForm = z.infer<typeof uploadFormSchema>;
export type UploadResponse = z.infer<typeof uploadResponseSchema>;
