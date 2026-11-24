import { useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "@tanstack/react-router";
import { zodResolver } from "@hookform/resolvers/zod";

import useVerify from "@hooks/auth/useVerify";
import useResend from "@hooks/auth/useResend";

import {
  resendSchema,
  verificationSchema,
  type Verification,
} from "@schemas/auth/auth";

import { Label } from "@components/ui/label";
import { Input } from "@components/ui/input";
import { Button } from "@components/ui/button";
import AuthGate from "@components/Auth/AuthGate";
import { Card, CardTitle, CardHeader, CardContent } from "@components/ui/card";

import { authFeedback } from "@utils/auth/feedback";

export default function VerifyPanel() {
  const pending = useRef(false);

  const [isResendValidating, setResendValidating] = useState(false);

  const { verify, isVerifyLoading, isVerifySuccess, verifyError } = useVerify();
  const { resend, isResendLoading, isResendSuccess, resendError } = useResend();

  const form = useForm<Verification>({
    resolver: zodResolver(verificationSchema),
    defaultValues: {
      email: "",
      otp: "",
    },
  });

  const blocked =
    isVerifyLoading ||
    isResendLoading ||
    isResendValidating ||
    form.formState.isSubmitting;

  const onVerify = async (input: Verification) => {
    if (pending.current) {
      return;
    }

    pending.current = true;

    try {
      await verify(input);

      form.resetField("otp");
    } catch {
    } finally {
      pending.current = false;
    }
  };

  const onResend = async () => {
    if (pending.current) {
      return;
    }

    pending.current = true;
    setResendValidating(true);

    const input = resendSchema.safeParse({
      email: form.getValues("email"),
    });

    try {
      if (input.success) {
        form.clearErrors("email");

        await resend(input.data);

        form.resetField("otp");
      } else {
        form.setError("email", {
          type: "validate",
          message: "Enter a valid email before requesting another code.",
        });
      }
    } catch {
    } finally {
      pending.current = false;
      setResendValidating(false);
    }
  };

  return (
    <AuthGate
      mode="anonymous"
      actionError={Boolean(verifyError || resendError)}
    >
      <Card>
        <CardHeader>
          <CardTitle>Verify account</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <form
            className="space-y-4"
            noValidate
            onSubmit={(event) => void form.handleSubmit(onVerify)(event)}
          >
            <fieldset disabled={blocked} className="space-y-4">
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
                <Label htmlFor="otp">Verification code</Label>

                <Input
                  id="otp"
                  type="text"
                  maxLength={6}
                  pattern="[0-9]{6}"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  {...form.register("otp")}
                />

                {form.formState.errors.otp && (
                  <p role="alert">Enter the six-digit verification code.</p>
                )}
              </div>

              <div className="flex gap-3">
                <Button type="submit" disabled={blocked}>
                  {isVerifyLoading ? "Verifying…" : "Verify"}
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  disabled={blocked}
                  onClick={onResend}
                >
                  {isResendLoading ? "Requesting…" : "Resend code"}
                </Button>
              </div>
            </fieldset>

            {isVerifyLoading && <p role="status">Verifying account…</p>}

            {verifyError && <p role="alert">{authFeedback(verifyError)}</p>}

            {isVerifySuccess && (
              <p role="alert">
                Verification completed, but the authenticated profile is
                unavailable. Reload to restore your session.
              </p>
            )}

            {isResendLoading && <p role="status">Requesting another code…</p>}

            {resendError && <p role="alert">{authFeedback(resendError)}</p>}

            {isResendSuccess && (
              <p role="status">
                Another code was requested. Use the latest code; the previous
                code no longer works.
              </p>
            )}
          </form>

          <Link className="underline" to="/register">
            Register account
          </Link>
        </CardContent>
      </Card>
    </AuthGate>
  );
}
