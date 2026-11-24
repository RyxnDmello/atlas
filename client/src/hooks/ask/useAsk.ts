import { useEffect, useState, useSyncExternalStore } from "react";

import { createFileAskSession } from "@services/ask/fileSession";

type AskDenial = (status: number, code: string) => Promise<void>;

export default function useAsk(fileId: string, onDenied: AskDenial) {
  const [lifetime] = useState(() => createFileAskSession(fileId));

  const { session } = lifetime;

  const state = useSyncExternalStore(
    session.subscribe,
    session.getSnapshot,
    session.getSnapshot,
  );

  useEffect(() => {
    lifetime.activate();
    return lifetime.retire;
  }, [lifetime]);

  const onAsk = async (question: string) => {
    await session.submit(question);

    const failure = session.getSnapshot().httpFailure;

    if (failure) {
      await onDenied(failure.status, failure.code).catch(() => undefined);
    }
  };

  return {
    askState: state,
    askQuestion: onAsk,
  };
}
