import {
  doneSchema,
  answerSchema,
  citationsSchema,
  atlasErrorSchema,
  type Citation,
} from "@schemas/ask/ask";

import type { SseRecord } from "@utils/stream/sseParser";

type AnswerTerminal = "done" | "error";

export interface CompletedAnswer {
  answer: string;
  citations: Citation[];
}

export interface AnswerStreamOptions {
  onAnswer(answer: string): void;
  onError(): void;
}

export interface AnswerStream {
  accept(record: SseRecord): void;
  finish(): CompletedAnswer;
  failed(): boolean;
}

export const createAnswerStream = (
  options: AnswerStreamOptions,
): AnswerStream => {
  let answer = "";
  let pending = "";
  let citations: Citation[] | undefined;
  let terminal: AnswerTerminal | undefined;

  const accept = (record: SseRecord): void => {
    if (terminal) {
      throw new Error("Unexpected event after terminal.");
    }

    const payload: unknown = JSON.parse(record.data);

    switch (record.event) {
      case "answer": {
        if (citations) {
          throw new Error("Unexpected answer after citations.");
        }

        pending += answerSchema.parse(payload).text;

        if (/\[\[cite:\d+\]\]/.test(pending)) {
          throw new Error("Reserved citation marker.");
        }

        const prefix = /\[(?:\[cite(?::\d*\]?)?|\[cit?|\[c?)?$/.exec(pending);
        const length = prefix?.[0].length ?? 0;
        answer += pending.slice(0, pending.length - length);
        pending = length ? pending.slice(-length) : "";

        options.onAnswer(answer);

        break;
      }
      case "citations":
        if (citations) {
          throw new Error("Duplicate citations.");
        }

        citations = citationsSchema.parse(payload).citations;

        break;
      case "done":
        if (!citations) {
          throw new Error("Missing citations.");
        }

        doneSchema.parse(payload);
        terminal = "done";

        break;
      case "error":
        atlasErrorSchema.parse(payload);
        terminal = "error";
        options.onError();

        break;
      default:
        throw new Error("Unknown answer event.");
    }
  };

  return {
    accept,

    failed: () => terminal === "error",

    finish: () => {
      if (terminal !== "done" || !citations) {
        throw new Error("Incomplete answer stream.");
      }

      return {
        answer: answer + pending,
        citations,
      };
    },
  };
};
