import RagWorkspace from "@components/Rag/RagWorkspace";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-start justify-center gap-6 p-6">
      <h1 className="text-3xl font-semibold tracking-tight">Atlas</h1>

      <RagWorkspace />
    </main>
  );
}
