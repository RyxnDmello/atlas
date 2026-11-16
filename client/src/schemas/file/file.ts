import { z } from "zod";

import { fileSchema } from "@schemas/folder/folder";

const name = z
  .string()
  .trim()
  .refine(
    (value) =>
      Array.from(value).length >= 1 &&
      Array.from(value).length <= 100 &&
      /^[\p{L}\p{N} _\-.,()[\]&+@']+$/u.test(value),
    "Use 1-100 letters, numbers, spaces or supported punctuation.",
  );

const description = z
  .string()
  .trim()
  .refine(
    (value) => Array.from(value).length <= 250,
    "Use at most 250 characters.",
  );

export const extensions = [
  ".bmp",
  ".csv",
  ".docx",
  ".html",
  ".jpg",
  ".jpeg",
  ".md",
  ".png",
  ".pdf",
  ".pptx",
  ".tiff",
  ".txt",
  ".webp",
  ".xlsx",
];

export const fileFormSchema = z.strictObject({
  name,
  description,
});

export const sourceSchema = z.instanceof(File).superRefine((file, context) => {
  const dot = file.name.lastIndexOf(".");
  const suffix = dot > 0 ? file.name.slice(dot).toLowerCase() : "";

  if (!extensions.includes(suffix)) {
    context.addIssue({
      code: "custom",
      message: "Choose a supported file type.",
    });
  }

  if (file.size === 0) {
    context.addIssue({
      code: "custom",
      message: "Choose a file containing data.",
    });
  }
});

export const uploadSchema = fileFormSchema.extend({
  file: sourceSchema,
});

export const filePatchSchema = z
  .strictObject({
    name: name.optional(),
    description: description
      .nullable()
      .transform((value) => value || null)
      .optional(),
  })
  .refine(
    (value) => value.name !== undefined || value.description !== undefined,
    "Change the name or description before saving.",
  );

export type FileRecord = z.infer<typeof fileSchema>;
export type FileForm = z.infer<typeof fileFormSchema>;
export type FileUpload = z.infer<typeof uploadSchema>;
export type FilePatch = z.input<typeof filePatchSchema>;
