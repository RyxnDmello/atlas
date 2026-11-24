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
  httpFailure?: AskHttpFailure;
  status: AskStatus;
  answer: string;
  citations: Citation[];
}

export interface AskHttpFailure {
  status: number;
  code: string;
}

interface AskSessionOptions {
  current?(): boolean;
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

export const createAskSession = (
  options: AskSessionOptions = {},
): AskSession => {
  let state = idle;
  let scope: string | undefined;
  let controller: AbortController | undefined;
  let activeReader: ReadableStreamDefaultReader<Uint8Array> | undefined;

  const listeners = new Set<AskListener>();

  const publish = (next: AskState): void => {
    state = next;
    listeners.forEach((listener) => listener());
  };

  const reset = (): void => {
    controller?.abort();
    controller = undefined;
    void activeReader?.cancel().catch(() => undefined);
    activeReader = undefined;

    publish(idle);
  };

  const submit = async (question: string): Promise<void> => {
    const form = askFormSchema.safeParse({
      question,
    });

    if (
      !scope ||
      !form.success ||
      controller ||
      options.current?.() === false
    ) {
      return;
    }

    const owner = new AbortController();
    controller = owner;

    const current = () =>
      controller === owner &&
      !owner.signal.aborted &&
      options.current?.() !== false;

    publish({
      ...idle,
      status: "streaming",
    });

    let complete = false;
    let message = failure;
    let httpFailure: AskHttpFailure | undefined;
    let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
    let responseBody: ReadableStream<Uint8Array> | null | undefined;

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
        isProtected: true,
        signal: owner.signal,
      });

      responseBody = response.body;

      if (!current()) {
        return;
      }

      if (!response.ok) {
        const payload: unknown = await response.json().catch(() => undefined);
        const result = atlasErrorSchema.safeParse(payload);

        if (result.success) {
          message = result.data.error;
          httpFailure = {
            status: response.status,
            code: result.data.code,
          };
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
      activeReader = reader;
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
          ...(httpFailure
            ? {
                httpFailure,
              }
            : {}),
        });
      }
    } finally {
      if (!complete) {
        owner.abort();
        await reader?.cancel().catch(() => undefined);

        if (!reader && !responseBody?.locked) {
          await responseBody?.cancel().catch(() => undefined);
        }
      }

      reader?.releaseLock();

      if (activeReader === reader) {
        activeReader = undefined;
      }

      if (controller === owner) {
        controller = undefined;
      }
    }
  };

  const subscribe = (listener: AskListener) => {
    listeners.add(listener);

    return () => {
      listeners.delete(listener);
    };
  };

  const getSnapshot = () => (options.current?.() === false ? idle : state);

  const setScope = (fileId: string | undefined) => {
    if (scope === fileId) {
      return;
    }

    scope = fileId;
    reset();
  };

  return {
    reset,
    submit,
    subscribe,
    getSnapshot,
    setScope,
  };
};
