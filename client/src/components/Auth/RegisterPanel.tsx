"use client";

import Link from "next/link";
import { useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import useRegister from "@hooks/auth/useRegister";

import { registrationSchema, type Registration } from "@schemas/auth/auth";

import { Label } from "@components/ui/label";
import { Input } from "@components/ui/input";
import { Button } from "@components/ui/button";
import AuthGate from "@components/Auth/AuthGate";
import { Card, CardTitle, CardHeader, CardContent } from "@components/ui/card";

import { authFeedback } from "@utils/auth/feedback";

export default function RegisterPanel() {
  const pending = useRef(false);

  const { register, isRegisterLoading, isRegisterSuccess, registerError } =
    useRegister();

  const form = useForm<Registration>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const onRegister = async (input: Registration) => {
    if (pending.current) {
      return;
    }

    pending.current = true;

    try {
      await register(input);

      form.resetField("password");
    } catch {
    } finally {
      pending.current = false;
    }
  };

  return (
    <AuthGate mode="anonymous" actionError={Boolean(registerError)}>
      <Card>
        <CardHeader>
          <CardTitle>Register account</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <form
            className="space-y-4"
            noValidate
            onSubmit={(event) => void form.handleSubmit(onRegister)(event)}
          >
            <fieldset
              className="space-y-4"
              disabled={isRegisterLoading || form.formState.isSubmitting}
            >
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>

                <Input
                  id="name"
                  autoComplete="name"
                  {...form.register("name")}
                />

                {form.formState.errors.name && (
                  <p role="alert">{form.formState.errors.name.message}</p>
                )}
              </div>

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
                  autoComplete="new-password"
                  {...form.register("password")}
                />

                {form.formState.errors.password && (
                  <p role="alert">{form.formState.errors.password.message}</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isRegisterLoading || form.formState.isSubmitting}
              >
                {isRegisterLoading ? "Registering…" : "Register"}
              </Button>
            </fieldset>

            {isRegisterLoading && <p role="status">Registering account…</p>}

            {registerError && <p role="alert">{authFeedback(registerError)}</p>}

            {isRegisterSuccess && (
              <p role="status">
                Verification required. Continue to Verify account and enter your
                email and code.
              </p>
            )}
          </form>

          <Link className="underline" href="/verify">
            Verify account
          </Link>
        </CardContent>
      </Card>
    </AuthGate>
  );
}
