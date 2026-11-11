import { createFileRoute } from "@tanstack/react-router";

import AuthGate from "@components/Auth/AuthGate";

function HomePage() {
  return <AuthGate mode="entry" />;
}

export const Route = createFileRoute("/")({
  component: HomePage,
});
