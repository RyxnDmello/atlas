import { useForm } from "react-hook-form";
import { useId, useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";

import useEditFile from "@hooks/file/useEditFile";
import useUploadFile from "@hooks/file/useUploadFile";
import useFileRecovery, {
  type FileRecoveryProps,
} from "@hooks/file/useFileRecovery";

import { Input } from "@components/ui/input";
import { Label } from "@components/ui/label";
import { Button } from "@components/ui/button";
import { Textarea } from "@components/ui/textarea";
import {
  Dialog,
  DialogClose,
  DialogTitle,
  DialogTrigger,
  DialogContent,
  DialogDescription,
} from "@components/ui/dialog";

import {
  extensions,
  sourceSchema,
  fileFormSchema,
  type FileForm,
} from "@schemas/file/file";

import { fileChanges } from "@utils/file/file";

interface FileDialogProps extends FileRecoveryProps {
  parent: string | null;
}

export default function FileDialog({ parent, file, refresh }: FileDialogProps) {
  const id = useId();

  const pending = useRef(false);
  const input = useRef<HTMLInputElement | null>(null);

  const [open, setOpen] = useState(false);
  const [source, setSource] = useState<File | null>(null);
  const [sourceError, setSourceError] = useState<string | null>(null);

  const {
    fileRecord,
    fileFeedback,
    isFileBlocked,
    isFileRefreshing,
    isFileCurrent,
    failFile,
    resetFile,
    refreshFile,
  } = useFileRecovery({
    file,
    refresh,
  });

  const { uploadFile, isUploadFileLoading } = useUploadFile(parent);
  const { editFile, isEditFileLoading } = useEditFile(fileRecord ?? null);

  const form = useForm<FileForm>({
    resolver: zodResolver(fileFormSchema),
    defaultValues: {
      name: file?.name ?? "",
      description: file?.description ?? "",
    },
  });

  const label = file ? "Edit File" : "Upload File";

  const busy =
    isUploadFileLoading ||
    isEditFileLoading ||
    isFileRefreshing ||
    form.formState.isSubmitting;

  const editable = !file || fileRecord?.status === "ready";

  const onSource = (selected: File | null) => {
    setSource(selected);
    setSourceError(null);

    if (!form.getFieldState("name").isDirty) {
      form.setValue("name", selected?.name ?? "");
    }
  };

  const onSubmit = async (data: FileForm) => {
    try {
      if (!isFileCurrent() || isFileBlocked || !editable) {
        return;
      }

      if (file && fileRecord) {
        const patch = fileChanges(fileRecord, data);

        if (Object.keys(patch).length === 0) {
          form.setError("name", {
            message: "Change the name or description before saving.",
          });

          return;
        }

        await editFile(patch);
      } else {
        const parsed = sourceSchema.safeParse(source);

        if (!parsed.success) {
          setSourceError(parsed.error.issues[0]?.message ?? "Choose a file.");

          return;
        }

        await uploadFile({
          ...data,
          file: parsed.data,
        });
      }

      if (isFileCurrent()) {
        resetFile();
        setOpen(false);
        setSource(null);
        form.reset();
      }
    } catch (error) {
      failFile(error);
    } finally {
      pending.current = false;
    }
  };

  const onRefresh = async () => {
    const updated = await refreshFile();

    if (isFileCurrent() && updated) {
      form.reset({
        name: updated.name,
        description: updated.description ?? "",
      });
    }

    if (isFileCurrent() && !file) {
      setSource(null);

      if (input.current) {
        input.current.value = "";
      }
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (pending.current || busy) {
          return;
        }

        if (next && !isFileBlocked) {
          form.reset({
            name: fileRecord?.name ?? "",
            description: fileRecord?.description ?? "",
          });

          setSource(null);
          setSourceError(null);
        }

        setOpen(next);
      }}
    >
      <DialogTrigger render={<Button variant="outline" />}>
        {label}
      </DialogTrigger>

      <DialogContent>
        <DialogTitle>{label}</DialogTitle>

        <DialogDescription>
          {file
            ? "Update the display name and description. File content and location stay the same."
            : "Choose one file to upload to the current folder. Uploading may take a while."}
        </DialogDescription>

        <form
          className="mt-4 space-y-4"
          noValidate
          onSubmit={(event) => {
            event.preventDefault();

            if (pending.current || busy || isFileBlocked || !editable) {
              return;
            }

            pending.current = true;

            void form.handleSubmit(onSubmit, () => {
              pending.current = false;
            })(event);
          }}
        >
          <fieldset
            className="space-y-4"
            disabled={busy || isFileBlocked || !editable}
          >
            {!file && (
              <div className="space-y-2">
                <Label htmlFor={`${id}-source`}>Source file</Label>

                <Input
                  ref={input}
                  id={`${id}-source`}
                  type="file"
                  accept={extensions.join(",")}
                  onChange={(event) =>
                    onSource(event.target.files?.[0] ?? null)
                  }
                />

                {sourceError && <p role="alert">{sourceError}</p>}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor={`${id}-name`}>Display name</Label>

              <Input id={`${id}-name`} {...form.register("name")} />

              {form.formState.errors.name && (
                <p role="alert">{form.formState.errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor={`${id}-description`}>
                Description (optional)
              </Label>

              <Textarea
                id={`${id}-description`}
                {...form.register("description")}
              />

              {form.formState.errors.description && (
                <p role="alert">{form.formState.errors.description.message}</p>
              )}
            </div>

            <Button type="submit">
              {busy
                ? file
                  ? "Saving…"
                  : "Uploading…"
                : file
                  ? "Save"
                  : "Upload"}
            </Button>
          </fieldset>

          {fileFeedback && <p role="alert">{fileFeedback}</p>}

          {!editable && <p>Editing requires a ready file.</p>}

          {isFileBlocked && (
            <Button
              type="button"
              disabled={busy}
              onClick={() => void onRefresh()}
            >
              Refresh current state
            </Button>
          )}

          <DialogClose
            render={<Button type="button" variant="outline" disabled={busy} />}
          >
            Cancel
          </DialogClose>
        </form>
      </DialogContent>
    </Dialog>
  );
}
