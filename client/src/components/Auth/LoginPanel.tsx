"use client";

import Link from "next/link";
import { useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import useAuthStore from "@stores/auth";

import useLogin from "@hooks/auth/useLogin";
import useLogout from "@hooks/auth/useLogout";

import { loginSchema, type Login } from "@schemas/auth/auth";

import { Input } from "@components/ui/input";
import { Label } from "@components/ui/label";
import { Button } from "@components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@components/ui/card";

import { retryAuth } from "@services/auth/auth";
import { AuthFailure } from "@services/http/validate";

import { authFeedback } from "@utils/auth/feedback";

export default function LoginPanel() {
  const pending = useRef(false);

  const { logout, logoutError, isLogoutLoading } = useLogout();
  const { login, loginError, isLoginLoading, isLoginSuccess } = useLogin();

  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);
  const outcome = useAuthStore((state) => state.logout);
  const persistence = useAuthStore((state) => state.persistence);
  const signoutPersisted = useAuthStore((state) => state.signoutPersisted);

  const form = useForm<Login>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onLogin = async (input: Login) => {
    if (pending.current || useAuthStore.getState().logout === "pending") {
      return;
    }

    pending.current = true;

    try {
      await login(input);
      form.resetField("password");
    } catch {
    } finally {
      pending.current = false;
    }
  };

  const onLogout = async () => {
    if (pending.current) {
      return;
    }

    pending.current = true;

    try {
      await logout();
    } catch {
    } finally {
      pending.current = false;
    }
  };

  const onRetry = async () => {
    if (pending.current || useAuthStore.getState().logout !== "none") {
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

  const uncertain = status === "error" && !loginError;

  const busy = isLoginLoading || isLogoutLoading || form.formState.isSubmitting;

  const inconsistent =
    (status === "authenticated" && !user) ||
    (isLoginSuccess && status !== "authenticated" && outcome === "none");

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {status === "authenticated" && user
            ? "Account authenticated"
            : "Login"}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {outcome === "pending" ? (
          <p role="status">
            Signing out locally; waiting for server confirmation…
          </p>
        ) : status === "restoring" ? (
          <p role="status">
            {isLoginLoading ? "Signing in…" : "Checking session…"}
          </p>
        ) : inconsistent ? (
          <p role="alert">
            The authenticated profile is unavailable. Please reload to check
            your session.
          </p>
        ) : status === "authenticated" && user ? (
          <>
            <dl className="space-y-2">
              <dt>Name</dt>
              <dd>{user.name}</dd>
              <dt>Email</dt>
              <dd>{user.email}</dd>
            </dl>

            <Button disabled={busy} onClick={() => void onLogout()}>
              Logout
            </Button>
          </>
        ) : uncertain ? (
          <>
            <p role="alert">
              Your session could not be confirmed. Please retry the session
              check.
            </p>

            {outcome === "none" && (
              <Button disabled={busy} onClick={() => void onRetry()}>
                Retry session check
              </Button>
            )}
          </>
        ) : (
          <form
            className="space-y-4"
            noValidate
            onSubmit={(event) => void form.handleSubmit(onLogin)(event)}
          >
            <fieldset className="space-y-4" disabled={busy}>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>

                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  {...form.register("email")}
                />

                {form.formState.errors.email && (
                  <p role="alert">{form.formState.errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>

                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  {...form.register("password")}
                />

                {form.formState.errors.password && (
                  <p role="alert">{form.formState.errors.password.message}</p>
                )}
              </div>

              <Button type="submit" disabled={busy}>
                Login
              </Button>
            </fieldset>

            {loginError && <p role="alert">{authFeedback(loginError)}</p>}

            {loginError instanceof AuthFailure &&
              loginError.code === "VERIFICATION_REQUIRED" && (
                <Link className="underline" href="/verify">
                  Verify account
                </Link>
              )}

            <p>
              <Link className="underline" href="/register">
                Register account
              </Link>
            </p>
          </form>
        )}

        {outcome === "confirmed" && (
          <p role="status">Signed out. Server logout confirmed.</p>
        )}

        {outcome === "unconfirmed" && (
          <p role="alert">
            Signed out locally. Server logout could not be confirmed. Sign in
            explicitly to use this account again.
          </p>
        )}

        {logoutError && (
          <p role="alert">The logout request could not be confirmed.</p>
        )}

        {persistence === "unavailable" && (
          <p role="alert">
            {status === "authenticated"
              ? "Session persistence is unavailable. This session may not survive a reload."
              : "Local session storage cleanup could not be confirmed."}
          </p>
        )}

        {!signoutPersisted && (
          <p role="alert">
            Sign-out intent could not be saved. A reload may restore the server
            session.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
