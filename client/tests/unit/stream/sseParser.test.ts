import { expect, test } from "bun:test";
import { createSseParser } from "@utils/stream/sseParser";
const encoder = new TextEncoder();
for (const newline of ["\n", "\r\n"]) {
  test(`ordered records and keepalives with ${JSON.stringify(newline)}`, () => {
    const parser = createSseParser();
    expect(
      parser.push(
        encoder.encode(
          [
            ": keepalive",
            "",
            "event: answer",
            'data: {"text":',
            'data: "hello"}',
            "",
            "event: citations",
            'data: {"citations":[]}',
            "",
            "event: done",
            'data: {"status":"completed"}',
            "",
            "",
          ].join(newline),
        ),
      ),
    ).toEqual([
      {
        event: "answer",
        data: '{"text":\n"hello"}',
      },
      {
        event: "citations",
        data: '{"citations":[]}',
      },
      {
        event: "done",
        data: '{"status":"completed"}',
      },
    ]);
    expect(parser.finish()).toEqual([]);
  });
}
test("every byte split preserves JSON, framing and multibyte UTF-8", () => {
  const bytes = encoder.encode(
    'event: answer\r\ndata: {"text":"café 🌍"}\r\n\r\nevent: error\ndata: {"error":"Generation failed.","code":"GENERATION_FAILED"}\n\n',
  );
  for (let offset = 1; offset < bytes.length; offset++) {
    const parser = createSseParser();
    const records = [
      ...parser.push(bytes.slice(0, offset)),
      ...parser.push(bytes.slice(offset)),
      ...parser.finish(),
    ];
    expect(records.map((record) => record.event)).toEqual(["answer", "error"]);
    expect(JSON.parse(records[0].data)).toEqual({
      text: "café 🌍",
    });
  }
});
test("releases each complete record without buffering the answer", () => {
  const parser = createSseParser();
  for (let index = 0; index < 100; index++)
    expect(
      parser.push(encoder.encode('event: answer\ndata: {"text":"x"}\n\n')),
    ).toHaveLength(1);
  expect(parser.finish()).toEqual([]);
});
for (const tail of [
  "event: done\n",
  "data: {}\n",
  "event: done\ndata: {}\n",
  ": unfinished",
]) {
  test(`rejects incomplete EOF ${JSON.stringify(tail)}`, () => {
    const parser = createSseParser();
    parser.push(encoder.encode(tail));
    expect(() => parser.finish()).toThrow("Incomplete");
  });
}
test("rejects incomplete and invalid UTF-8", () => {
  const parser = createSseParser();
  parser.push(new Uint8Array([0xf0, 0x9f]));
  expect(() => parser.finish()).toThrow();
  expect(() => createSseParser().push(new Uint8Array([0xff]))).toThrow();
});
