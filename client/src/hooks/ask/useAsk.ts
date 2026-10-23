"use client";

import { useLayoutEffect, useState, useSyncExternalStore } from "react";

import {
  idle,
  createAskSession,
  type AskState,
} from "@services/ask/askSession";

export interface UseAskResult extends AskState {
  submit(question: string): Promise<void>;
}

export default function useAsk(fileId: string | undefined): UseAskResult {
  const [session] = useState(createAskSession);

  const state = useSyncExternalStore(
    session.subscribe,
    session.getSnapshot,
    () => idle,
  );

  useLayoutEffect(() => {
    session.setScope(fileId);

    return session.reset;
  }, [fileId, session]);

  return {
    ...state,
    submit: session.submit,
  };
}
