import { z } from "zod";

const name = z.string().trim().min(1, "Enter a folder name.");

const description = z
  .string()
  .nullable()
  .transform((value) => value?.trim() || null);

const timestamp = z.iso.datetime({
  local: true,
  offset: true,
});

export const folderSchema = z.strictObject({
  id: z.uuid(),
  name: z.string(),
  parent_id: z.uuid().nullable(),
  description: z.string().nullable(),
  created_at: timestamp,
  updated_at: timestamp,
});

export const fileSchema = z.strictObject({
  id: z.uuid(),
  name: z.string(),
  extension: z.string(),
  original_name: z.string(),
  size_bytes: z.number().int(),
  folder_id: z.uuid().nullable(),
  description: z.string().nullable(),
  status: z.enum(["processing", "ready", "deleting"]),
  created_at: timestamp,
  updated_at: timestamp,
});

export const listingSchema = z.strictObject({
  folder: folderSchema.nullable(),
  files: z.array(fileSchema),
  folders: z.array(folderSchema),
});

export const folderFormSchema = z.strictObject({
  name,
  description: z.string(),
});

export const folderCreateSchema = z.strictObject({
  name,
  parent_id: z.uuid().nullable(),
  description: description.optional(),
});

export const folderPatchSchema = z
  .strictObject({
    name: name.optional(),
    description: description.optional(),
  })
  .refine(
    (value) => value.name !== undefined || value.description !== undefined,
    {
      message: "Change the name or description before saving.",
    },
  );

export type Folder = z.infer<typeof folderSchema>;

export type FolderForm = z.infer<typeof folderFormSchema>;
export type FolderListing = z.infer<typeof listingSchema>;

export type FolderPatch = z.input<typeof folderPatchSchema>;
export type FolderCreate = z.input<typeof folderCreateSchema>;
