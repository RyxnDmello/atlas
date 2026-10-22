import { expect, test } from "bun:test";
import { renderToStaticMarkup } from "react-dom/server";

import AskPanel from "@components/Ask/AskPanel";
import CitationList from "@components/Citations/CitationList";

import type { Citation } from "@schemas/ask/ask";

const citations: Citation[] = [
  {
    index: 7,
    page: 0,
    heading: "<Heading>",
    section: "",
    excerpt: "  <script>unsafe</script>\n& exact  spacing",
  },
  {
    index: 2,
    page: -2,
    heading: null,
    section: null,
    excerpt: "",
  },
];

test("preserves backend order, indexes, nullable values and escaped excerpt whitespace", () => {
  const html = renderToStaticMarkup(<CitationList citations={citations} />);

  expect(html.indexOf("Source 7")).toBeLessThan(html.indexOf("Source 2"));
  expect(html).toContain(
    "  &lt;script&gt;unsafe&lt;/script&gt;\n&amp; exact  spacing",
  );
  expect(html).not.toContain("<script>");
  expect(html).toContain("&lt;Heading&gt;");
  expect(html).toContain('class="inline">0</dd>');
  expect(html).toContain('class="inline">-2</dd>');
  expect(html.match(/Heading: /g)).toHaveLength(1);
  expect(html.match(/Section: /g)).toHaveLength(1);
  expect(html).toContain('Section: </dt><dd class="inline"></dd>');
  expect(html).not.toMatch(/confidence|score|unknown|file_id|href=/i);
});

test("null metadata is omitted and empty citations produce no markup", () => {
  expect(renderToStaticMarkup(<CitationList citations={[]} />)).toBe("");

  const html = renderToStaticMarkup(
    <CitationList
      citations={[
        {
          index: 0,
          page: null,
          heading: null,
          section: null,
          excerpt: "Exact excerpt",
        },
      ]}
    />,
  );

  expect(html).not.toMatch(/Page:|Heading:|Section:/);
  expect(html).toContain("Exact excerpt");
});

test("AskPanel presents citations only for successful completed state", () => {
  for (const status of ["idle", "streaming", "error", "success"] as const) {
    const html = renderToStaticMarkup(
      <AskPanel
        disabled={false}
        ask={{
          status,
          answer: "Synthetic answer",
          citations,
          submit: async () => {},
        }}
      />,
    );

    expect(html.includes("Sources</h2>")).toBe(status === "success");
  }
});
