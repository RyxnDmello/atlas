import DashboardPanel from "@components/Auth/DashboardPanel";

export default function DashboardPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-6">
      <h1 className="text-2xl font-semibold">Atlas</h1>

      <DashboardPanel />
    </main>
  );
}
