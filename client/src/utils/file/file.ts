import { z } from "zod";
import axios from "axios";

import { fileSchema } from "@schemas/folder/folder";
import { authErrorSchema } from "@schemas/auth/auth";
import {
  uploadSchema,
  fileFormSchema,
  type FileForm,
  type FilePatch,
  type FileRecord,
  type FileUpload,
} from "@schemas/file/file";

interface FileResponse {
  data: unknown;
  status: number;
}

export class FileFailure extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
  ) {
    super("File operation could not be confirmed.");
    this.name = "FileFailure";
  }

  get uncertain() {
    return (
      this.status === 0 ||
      this.status >= 500 ||
      (this.status >= 200 && this.status < 300)
    );
  }

  get reconcile() {
    return (
      this.uncertain ||
      this.status === 404 ||
      this.status === 409 ||
      this.status === 401
    );
  }
}

export const fileKey = (id: string) => ["drive", "file", id] as const;

export const fileError = (error: unknown): FileFailure => {
  if (error instanceof FileFailure) {
    return error;
  }

  if (axios.isAxiosError<unknown>(error) && error.response) {
    const parsed = authErrorSchema.safeParse(error.response.data);

    return new FileFailure(
      error.response.status,
      parsed.success ? parsed.data.code : "INVALID_RESPONSE",
    );
  }

  return new FileFailure(0, "TRANSPORT_ERROR");
};

export const fileResponse = (
  response: FileResponse,
  status: number,
): FileRecord => {
  const parsed = fileSchema.safeParse(response.data);

  if (response.status !== status || !parsed.success) {
    throw new FileFailure(response.status, "INVALID_RESPONSE");
  }

  return parsed.data;
};

export const fileBody = (
  input: FileUpload,
  parent: string | null,
): FormData => {
  const data = uploadSchema.parse(input);

  if (parent !== null) {
    z.uuid().parse(parent);
  }

  const body = new FormData();

  body.append("file", data.file, data.file.name);
  body.append("name", data.name);

  if (data.description) {
    body.append("description", data.description);
  }

  if (parent !== null) {
    body.append("folder_id", parent);
  }

  return body;
};

export const fileChanges = (file: FileRecord, input: FileForm): FilePatch => {
  const data = fileFormSchema.parse(input);

  const patch: FilePatch = {};
  const description = data.description || null;

  if (data.name !== file.name) {
    patch.name = data.name;
  }

  if (description !== file.description) {
    patch.description = description;
  }

  return patch;
};

export const sameFile = (before: FileRecord, after: FileRecord): boolean => {
  return (
    before.id === after.id &&
    before.folder_id === after.folder_id &&
    before.original_name === after.original_name &&
    before.extension === after.extension &&
    before.size_bytes === after.size_bytes &&
    before.created_at === after.created_at
  );
};

export const fileFeedback = (error: unknown): string => {
  const failure = fileError(error);

  if (failure.uncertain) {
    return "The operation outcome is unknown. Refresh and check the current files before trying again. The server may have completed the operation.";
  }

  if (failure.status === 404) {
    return "The file or folder is unavailable. Refresh to check the current state.";
  }

  if (failure.status === 409) {
    return "The file state changed. Refresh before choosing another action.";
  }

  if (failure.status === 401) {
    return "Your session could not be confirmed. Refresh before trying again.";
  }

  if (
    failure.status === 422 ||
    failure.code === "INVALID_FILE_TYPE" ||
    failure.code === "INVALID_FILE_SIZE"
  ) {
    return "Check the selected file, name and description, then try again.";
  }

  return "The file operation was rejected. Check the file and try again.";
};
