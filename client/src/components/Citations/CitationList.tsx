import type { Citation } from "@schemas/ask/ask";

interface CitationListProps {
  citations: Citation[];
}

export default function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <section className="space-y-2">
      <h2 className="font-medium">Sources</h2>

      <ul className="space-y-3">
        {citations.map((citation, position) => (
          <li
            key={position}
            className="space-y-2 rounded-lg border p-4 text-sm"
          >
            <h3 className="font-medium">Source {citation.index}</h3>

            <dl className="whitespace-pre-wrap wrap-anywhere">
              {citation.page !== null && (
                <div>
                  <dt className="inline font-medium">Page: </dt>
                  <dd className="inline">{citation.page}</dd>
                </div>
              )}

              {citation.heading !== null && (
                <div>
                  <dt className="inline font-medium">Heading: </dt>
                  <dd className="inline">{citation.heading}</dd>
                </div>
              )}

              {citation.section !== null && (
                <div>
                  <dt className="inline font-medium">Section: </dt>
                  <dd className="inline">{citation.section}</dd>
                </div>
              )}
            </dl>

            <p className="whitespace-pre-wrap wrap-anywhere">
              {citation.excerpt}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
