import { useEffect, useRef, type ReactNode } from "react";
import { useLocation, useNavigate } from "@tanstack/react-router";

import { Button } from "@components/ui/button";

import { retryAuth } from "@services/auth/auth";

import useAuthStore from "@stores/auth";

import {
  authRoute,
  replaceAuthRoute,
  type AuthRouteMode,
} from "@utils/auth/navigation";

interface AuthGateProps {
  mode: AuthRouteMode;
  actionError?: boolean;
  children?: ReactNode;
}

export default function AuthGate({
  mode,
  children,
  actionError = false,
}: AuthGateProps) {
  const navigate = useNavigate();

  const pathname = useLocation({
    select: (location) => location.pathname,
  });

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
        (destination) => {
          void navigate({
            to: destination,
            replace: true,
          });
        },
      );
    } else {
      previous.current = null;
    }
  }, [actionError, mode, decision.destination, pathname, navigate]);

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
  }

  if (decision.view === "inconsistent") {
    return (
      <div className="space-y-4">
        <p role="alert">
          The authenticated profile is unavailable. Please reload to check your
          session.
        </p>

        <Button onClick={() => window.location.reload()}>Reload session</Button>
      </div>
    );
  }

  if (decision.view === "recovery") {
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
  }

  return (
    <p role="status">
      {decision.view === "loading" ? "Checking session…" : "Redirecting…"}
    </p>
  );
}
