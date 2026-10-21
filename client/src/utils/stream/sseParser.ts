export interface SseRecord {
  data: string;
  event: string;
}

export interface SseParser {
  push(bytes: Uint8Array): SseRecord[];
  finish(): SseRecord[];
}

export function createSseParser(): SseParser {
  const decoder = new TextDecoder("utf-8", {
    fatal: true,
  });

  let event = "";
  let buffer = "";
  let data: string[] = [];
  let ended = false;

  function consume(text: string): SseRecord[] {
    buffer += text;

    const records: SseRecord[] = [];
    let boundary: number;

    while ((boundary = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, boundary).replace(/\r$/, "");
      buffer = buffer.slice(boundary + 1);

      if (line === "") {
        if (event || data.length)
          records.push({
            event: event || "message",
            data: data.join("\n"),
          });

        event = "";
        data = [];
      } else if (!line.startsWith(":")) {
        const colon = line.indexOf(":");
        const field = colon === -1 ? line : line.slice(0, colon);
        const value =
          colon === -1 ? "" : line.slice(colon + 1).replace(/^ /, "");

        if (field === "event") event = value;
        if (field === "data") data.push(value);
      }
    }

    return records;
  }

  return {
    push(bytes: Uint8Array) {
      if (ended) throw new Error("Stream already ended.");

      return consume(
        decoder.decode(bytes, {
          stream: true,
        }),
      );
    },

    finish() {
      if (ended) throw new Error("Stream already ended.");

      ended = true;
      const records = consume(decoder.decode());

      if (buffer || event || data.length)
        throw new Error("Incomplete SSE record.");

      return records;
    },
  };
}
