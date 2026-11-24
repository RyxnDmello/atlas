import axios from "axios";
import { z } from "zod";

import { authErrorSchema } from "@schemas/auth/auth";
import type { Folder, FolderForm, FolderPatch } from "@schemas/folder/folder";

interface FolderHttpResponse {
  status: number;
  data: unknown;
}

export const folderKey = (id: string | null) =>
  ["drive", "folder", id ?? "root"] as const;

export const validFolderId = (id: string) => z.uuid().safeParse(id).success;

export class FolderFailure extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
  ) {
    super("Folder request could not be confirmed.");
    this.name = "FolderFailure";
  }

  get uncertain() {
    return (
      this.status === 0 ||
      this.status >= 500 ||
      (this.status >= 200 && this.status < 300)
    );
  }
}

export const folderError = (error: unknown): FolderFailure => {
  if (error instanceof FolderFailure) {
    return error;
  }

  if (axios.isAxiosError<unknown>(error) && error.response) {
    const parsed = authErrorSchema.safeParse(error.response.data);

    return new FolderFailure(
      error.response.status,
      parsed.success ? parsed.data.code : "INVALID_RESPONSE",
    );
  }

  return new FolderFailure(0, "TRANSPORT_ERROR");
};

export const folderResponse = <T>(
  response: FolderHttpResponse,
  status: number,
  schema: z.ZodType<T>,
): T => {
  if (response.status === status) {
    const parsed = schema.safeParse(response.data);

    if (parsed.success) {
      return parsed.data;
    }

    throw new FolderFailure(status, "INVALID_RESPONSE");
  }

  const parsed = authErrorSchema.safeParse(response.data);

  throw new FolderFailure(
    response.status,
    parsed.success ? parsed.data.code : "INVALID_RESPONSE",
  );
};

export const folderChanges = (
  folder: Folder,
  input: FolderForm,
): FolderPatch => {
  const patch: FolderPatch = {};
  const name = input.name.trim();
  const description = input.description.trim() || null;

  if (name !== folder.name) {
    patch.name = name;
  }

  if (description !== folder.description) {
    patch.description = description;
  }

  return patch;
};

export const folderFeedback = (error: unknown): string => {
  const failure = folderError(error);

  if (failure.code === "FOLDER_NOT_FOUND" && failure.status === 404) {
    return "Folder not found.";
  }

  if (failure.status === 401) {
    return "Your session could not be confirmed. Refresh the folder before trying again.";
  }

  if (failure.status === 422) {
    return "Check the folder name and description, then try again.";
  }

  return "The folder request could not be confirmed. Please refresh and check the current folder.";
};
