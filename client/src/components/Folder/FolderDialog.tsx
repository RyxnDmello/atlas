import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useId, useRef, useState } from "react";

import useEditFolder from "@hooks/folder/useEditFolder";
import useCreateFolder from "@hooks/folder/useCreateFolder";

import { Input } from "@components/ui/input";
import { Label } from "@components/ui/label";
import { Button } from "@components/ui/button";
import { Textarea } from "@components/ui/textarea";
import {
  Dialog,
  DialogTitle,
  DialogClose,
  DialogContent,
  DialogTrigger,
  DialogDescription,
} from "@components/ui/dialog";

import { folderSession, currentFolderSession } from "@services/folder/session";

import {
  folderFormSchema,
  type Folder,
  type FolderForm,
  type FolderListing,
} from "@schemas/folder/folder";

import {
  folderChanges,
  folderError,
  folderFeedback,
} from "@utils/folder/folder";

interface FolderDialogProps {
  parent: string | null;
  folder?: Folder;
  refresh(): Promise<FolderListing | undefined>;
}

export default function FolderDialog({
  parent,
  folder,
  refresh,
}: FolderDialogProps) {
  const id = useId();

  const active = useRef(true);
  const pending = useRef(false);

  const [open, setOpen] = useState(false);
  const [uncertain, setUncertain] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const session = folderSession();
  const { createFolder, isCreateFolderLoading } = useCreateFolder();
  const { editFolder, isEditFolderLoading } = useEditFolder(folder ?? null);

  const label = folder ? "Edit Folder" : "New Folder";

  useEffect(() => {
    active.current = true;

    return () => {
      active.current = false;
    };
  }, []);

  const form = useForm<FolderForm>({
    resolver: zodResolver(folderFormSchema),
    defaultValues: {
      name: folder?.name ?? "",
      description: folder?.description ?? "",
    },
  });

  const current = () => active.current && currentFolderSession(session);

  const busy =
    isCreateFolderLoading ||
    isEditFolderLoading ||
    form.formState.isSubmitting ||
    refreshing;

  const onSubmit = async (input: FolderForm) => {
    try {
      if (!current() || uncertain) {
        return;
      }

      if (folder) {
        const patch = folderChanges(folder, input);

        if (Object.keys(patch).length === 0) {
          setFeedback("Change the name or description before saving.");

          return;
        }

        await editFolder(patch);
      } else {
        await createFolder({
          name: input.name,
          description: input.description,
          parent_id: parent,
        });
      }

      if (current()) {
        setOpen(false);
        form.reset();
      }
    } catch (error) {
      if (current()) {
        const failure = folderError(error);

        setUncertain(failure.uncertain);

        setFeedback(
          failure.uncertain
            ? "The save outcome is unknown. Refresh and check the folder before submitting again."
            : folderFeedback(failure),
        );
      }
    } finally {
      pending.current = false;
    }
  };

  const onRefresh = async () => {
    if (pending.current) {
      return;
    }

    pending.current = true;
    setRefreshing(true);

    try {
      const data = await refresh();

      if (current() && data) {
        if (folder && data.folder) {
          form.reset({
            name: data.folder.name,
            description: data.folder.description ?? "",
          });
        }

        setUncertain(false);

        setFeedback(
          "Folder refreshed. Check the current contents before saving again.",
        );
      }
    } catch {
      if (current()) {
        setFeedback(
          "The folder could not be refreshed. Please try refreshing again.",
        );
      }
    } finally {
      pending.current = false;

      if (current()) {
        setRefreshing(false);
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

        if (next) {
          form.reset({
            name: folder?.name ?? "",
            description: folder?.description ?? "",
          });

          if (!uncertain) {
            setFeedback(null);
          }
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
          {folder
            ? "Update this folder's name and description."
            : "Create a folder in the current location."}
        </DialogDescription>

        <form
          className="mt-4 space-y-4"
          noValidate
          onSubmit={(event) => {
            event.preventDefault();

            if (pending.current || uncertain || busy) {
              return;
            }

            pending.current = true;
            setFeedback(null);

            void form.handleSubmit(onSubmit, () => {
              pending.current = false;
            })(event);
          }}
        >
          <fieldset className="space-y-4" disabled={busy || uncertain}>
            <div className="space-y-2">
              <Label htmlFor={`${id}-name`}>Name</Label>

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
            </div>

            <Button type="submit">
              {busy ? "Saving…" : folder ? "Save" : "Create"}
            </Button>
          </fieldset>

          {feedback && <p role="alert">{feedback}</p>}

          {uncertain && (
            <Button
              type="button"
              disabled={busy}
              onClick={() => void onRefresh()}
            >
              Refresh folder
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
