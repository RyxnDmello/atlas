import fetch from "@services/http/fetch";

import {
  askFormSchema,
  atlasErrorSchema,
  type Citation,
} from "@schemas/ask/ask";

import { createSseParser } from "@utils/stream/sseParser";
import { createAnswerStream } from "@utils/stream/answerStream";

export type AskStatus = "idle" | "streaming" | "success" | "error";

export interface AskState {
  error?: string;
  status: AskStatus;
  answer: string;
  citations: Citation[];
}

export type AskListener = () => void;

export interface AskSession {
  reset(): void;
  getSnapshot(): AskState;
  submit(question: string): Promise<void>;
  setScope(fileId: string | undefined): void;
  subscribe(listener: AskListener): AskListener;
}

export const idle: AskState = {
  error: undefined,
  status: "idle",
  answer: "",
  citations: [],
};

const failure =
  "Unable to complete the answer. Check the API connection and try again.";
const generationFailure = "Generation failed. Try again.";

export const createAskSession = (): AskSession => {
  let state = idle;
  let scope: string | undefined;
  let controller: AbortController | undefined;

  const listeners = new Set<AskListener>();

  const publish = (next: AskState): void => {
    state = next;
    listeners.forEach((listener) => listener());
  };

  const reset = (): void => {
    controller?.abort();
    controller = undefined;

    publish(idle);
  };

  const submit = async (question: string): Promise<void> => {
    const form = askFormSchema.safeParse({
      question,
    });

    if (!scope || !form.success || controller) {
      return;
    }

    const owner = new AbortController();
    controller = owner;

    const current = () => controller === owner && !owner.signal.aborted;

    publish({
      ...idle,
      status: "streaming",
    });

    let complete = false;
    let message = failure;
    let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;

    const stream = createAnswerStream({
      onAnswer: (answer) => {
        if (current()) {
          publish({
            status: "streaming",
            answer,
            citations: [],
          });
        }
      },

      onError: () => {
        if (current()) {
          publish({
            ...idle,
            status: "error",
            error: generationFailure,
          });
        }
      },
    });

    try {
      const response = await fetch.post(`/files/${scope}/ask`, form.data, {
        signal: owner.signal,
      });

      if (!current()) {
        return;
      }

      if (!response.ok) {
        const payload: unknown = await response.json().catch(() => undefined);
        const result = atlasErrorSchema.safeParse(payload);

        if (result.success) {
          message = result.data.error;
        }

        throw new Error(failure);
      }

      if (
        response.headers
          .get("Content-Type")
          ?.split(";")[0]
          .trim()
          .toLowerCase() !== "text/event-stream" ||
        !response.body
      ) {
        throw new Error(failure);
      }

      reader = response.body.getReader();
      const parser = createSseParser();

      while (current()) {
        const chunk = await reader.read();

        if (!current()) {
          return;
        }

        if (chunk.done) {
          break;
        }

        parser.push(chunk.value).forEach(stream.accept);
      }

      parser.finish().forEach(stream.accept);
      const result = stream.finish();
      complete = true;

      if (current()) {
        publish({
          status: "success",
          ...result,
        });
      }
    } catch {
      if (current()) {
        publish({
          ...idle,
          status: "error",
          error: stream.failed() ? generationFailure : message,
        });
      }
    } finally {
      if (!complete) {
        owner.abort();
        await reader?.cancel().catch(() => undefined);
      }

      reader?.releaseLock();

      if (controller === owner) {
        controller = undefined;
      }
    }
  };

  return {
    reset,
    submit,

    subscribe: (listener) => {
      listeners.add(listener);

      return () => {
        listeners.delete(listener);
      };
    },

    getSnapshot: () => state,

    setScope: (fileId) => {
      if (scope === fileId) {
        return;
      }

      scope = fileId;
      reset();
    },
  };
};
