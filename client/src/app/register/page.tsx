import RegisterPanel from "@components/Auth/RegisterPanel";

export default function Register() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-6">
      <h1 className="text-3xl font-semibold tracking-tight">Atlas</h1>

      <RegisterPanel />
    </main>
  );
}
