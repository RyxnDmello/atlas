"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, type ReactNode } from "react";

import { retryAuth } from "@services/auth/auth";

import { Button } from "@components/ui/button";

import {
  authRoute,
  replaceAuthRoute,
  type AuthRouteMode,
} from "@utils/auth/navigation";

import useAuthStore from "@stores/auth";

interface AuthGateProps {
  mode: AuthRouteMode;
  actionError?: boolean;
  children?: ReactNode;
}

export default function AuthGate({
  mode,
  actionError = false,
  children,
}: AuthGateProps) {
  const router = useRouter();
  const pathname = usePathname();

  const pending = useRef(false);
  const previous = useRef<string | null>(null);

  const user = useAuthStore((state) => state.user);
  const error = useAuthStore((state) => state.error);
  const status = useAuthStore((state) => state.status);
  const logout = useAuthStore((state) => state.logout);

  const decision = authRoute(
    mode,
    {
      user,
      status,
      logout,
      error,
    },
    actionError,
  );

  useEffect(() => {
    if (decision.destination) {
      previous.current = replaceAuthRoute(
        mode,
        actionError,
        pathname,
        decision.destination,
        useAuthStore.getState(),
        window.location.pathname,
        previous.current,
        (destination) => router.replace(destination),
      );
    } else {
      previous.current = null;
    }
  }, [actionError, mode, decision.destination, pathname, router]);

  const onRetry = async () => {
    if (
      pending.current ||
      useAuthStore.getState().logout !== "none" ||
      useAuthStore.getState().status !== "error"
    ) {
      return;
    }

    pending.current = true;

    try {
      await retryAuth();
    } catch {
    } finally {
      pending.current = false;
    }
  };

  if (decision.view === "content") {
    return children;
  } else if (decision.view === "inconsistent") {
    return (
      <div className="space-y-4">
        <p role="alert">
          The authenticated profile is unavailable. Please reload to check your
          session.
        </p>

        <Button onClick={() => window.location.reload()}>Reload session</Button>
      </div>
    );
  } else if (decision.view === "recovery") {
    return (
      <div className="space-y-4">
        <p role="alert">
          Your session could not be confirmed. Please retry the session check.
        </p>

        {logout === "none" && (
          <Button onClick={() => void onRetry()}>Retry session check</Button>
        )}
      </div>
    );
  } else {
    return (
      <p role="status">
        {decision.view === "loading" ? "Checking session…" : "Redirecting…"}
      </p>
    );
  }
}
