"use client";

import { useRef } from "react";

import useAsk from "@hooks/ask/useAsk";
import useUpload from "@hooks/upload/useUpload";

import AskPanel from "@components/Ask/AskPanel";
import UploadPanel from "@components/Upload/UploadPanel";

export type WorkspaceAction = () => Promise<void>;

export default function RagWorkspace() {
  const upload = useUpload();

  const ask = useAsk(upload.active?.fileId);

  const locked = useRef(false);

  async function submit(action: WorkspaceAction) {
    if (locked.current) return;

    locked.current = true;

    try {
      await action();
    } finally {
      locked.current = false;
    }
  }

  return (
    <>
      <UploadPanel
        upload={{
          ...upload,
          submit: (file) => submit(() => upload.submit(file)),
        }}
        blocked={ask.status === "streaming"}
      />

      <AskPanel
        key={upload.active?.fileId ?? "empty"}
        ask={{
          ...ask,
          submit: (question) => submit(() => ask.submit(question)),
        }}
        disabled={!upload.active || upload.pending}
      />
    </>
  );
}
