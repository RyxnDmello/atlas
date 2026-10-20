"use client";

import { Controller, useForm } from "react-hook-form";

import { zodResolver } from "@hookform/resolvers/zod";

import { uploadFormSchema, type UploadForm } from "@schemas/upload/upload";

import { useUpload } from "@hooks/upload/useUpload";

import {
  Card,
  CardTitle,
  CardHeader,
  CardContent,
  CardDescription,
} from "@components/ui/card";
import { Label } from "@components/ui/label";
import { Input } from "@components/ui/input";
import { Button } from "@components/ui/button";

export function UploadPanel() {
  const form = useForm<UploadForm>({ resolver: zodResolver(uploadFormSchema) });
  const upload = useUpload();

  return (
    <Card className="w-full max-w-xl">
      <CardHeader>
        <CardTitle>Upload a file</CardTitle>
        <CardDescription>
          Select a supported file to prepare it for Atlas.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit(({ file }) => upload.submit(file))}
        >
          <div className="space-y-2">
            <Label htmlFor="file">File</Label>
            <Controller
              name="file"
              control={form.control}
              render={({ field }) => (
                <Input
                  id="file"
                  type="file"
                  name={field.name}
                  ref={field.ref}
                  onBlur={field.onBlur}
                  onChange={(event) => field.onChange(event.target.files?.[0])}
                  disabled={upload.pending}
                  aria-invalid={!!form.formState.errors.file}
                  aria-describedby="file-error"
                />
              )}
            />
            {form.formState.errors.file && (
              <p
                id="file-error"
                role="alert"
                className="text-sm text-destructive"
              >
                {form.formState.errors.file.message}
              </p>
            )}
          </div>
          <Button type="submit" disabled={upload.pending}>
            {upload.pending ? "Uploading…" : "Upload"}
          </Button>
          {upload.pending && (
            <p role="status" className="text-sm text-muted-foreground">
              Processing your file…
            </p>
          )}
          {upload.error && (
            <p role="alert" className="text-sm text-destructive">
              {upload.error.message}
            </p>
          )}
        </form>
        {upload.active && (
          <div
            role="status"
            className="space-y-2 rounded-lg border p-4 text-sm"
          >
            <p className="font-medium">Ready: {upload.active.name}</p>
            <p className="break-all text-muted-foreground">
              File ID:{" "}
              <span data-testid="active-file-id">{upload.active.fileId}</span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
