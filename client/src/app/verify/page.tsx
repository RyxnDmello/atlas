import VerifyPanel from "@components/Auth/VerifyPanel";

export default function Verify() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-6">
      <h1 className="text-3xl font-semibold tracking-tight">Atlas</h1>

      <VerifyPanel />
    </main>
  );
}
