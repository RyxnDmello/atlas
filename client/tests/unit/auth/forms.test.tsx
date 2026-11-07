import { afterEach, expect, test } from "bun:test";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "./environment";

import RegisterPanel from "@components/Auth/RegisterPanel";
import VerifyPanel from "@components/Auth/VerifyPanel";

import useAuthStore from "@stores/auth";
import {
  registrationSchema,
  verificationSchema,
  resendSchema,
} from "@schemas/auth/auth";
import { AuthFailure } from "@services/http/validate";
import { authFeedback } from "@utils/auth/feedback";

const initial = useAuthStore.getInitialState();
const original = {
  ...initial,
};

// SSR uses the store's server snapshot; no browser subscription is claimed here.
const render = (verification = false) => {
  const cache = new QueryClient();
  const html = renderToStaticMarkup(
    <QueryClientProvider client={cache}>
      {verification ? <VerifyPanel /> : <RegisterPanel />}
    </QueryClientProvider>,
  );

  cache.clear();

  return html;
};

afterEach(() => {
  Object.assign(initial, original);
});

test("registration presents masked inputs and a direct verification link without a profile", () => {
  const html = render();

  expect(html).toContain('name="name"');
  expect(html).toContain('name="email"');
  expect(html).toContain('type="password"');
  expect(html).toContain('autoComplete="new-password"');
  expect(html).toContain('href="/verify"');
  expect(html).not.toContain("Account authenticated");
  expect(html).not.toMatch(/href="\/(login|dashboard)"/);
});

test("direct verification entry has editable email and a string OTP with a separate resend control", () => {
  const html = render(true);

  expect(html).toContain('name="email"');
  expect(html).toContain('name="otp"');
  expect(html).toContain('inputMode="numeric"');
  expect(html).toContain('pattern="[0-9]{6}"');
  expect(html).toContain('maxLength="6"');
  expect(html).toContain('type="text"');
  expect(html).toContain('type="button"');
  expect(html).toContain("Resend code");
  expect(html).toContain('href="/register"');
  expect(html).not.toContain('type="number"');
});

test("shared form schemas validate registration, resend email and exact string OTP precision", () => {
  expect(
    registrationSchema.safeParse({
      name: " ",
      email: "invalid",
      password: "short",
    }).success,
  ).toBe(false);
  expect(
    registrationSchema.parse({
      name: " Canonical ",
      email: "FIXTURE@example.test",
      password: "synthetic-password",
    }),
  ).toEqual({
    name: "Canonical",
    email: "fixture@example.test",
    password: "synthetic-password",
  });
  expect(
    resendSchema.safeParse({
      email: "invalid",
    }).success,
  ).toBe(false);
  expect(
    verificationSchema.parse({
      email: "fixture@example.test",
      otp: "001234",
    }).otp,
  ).toBe("001234");

  for (const otp of ["12345", "1234567", "12a456", " 12345", 123456]) {
    expect(
      verificationSchema.safeParse({
        email: "fixture@example.test",
        otp,
      }).success,
    ).toBe(false);
  }
});

test.each([
  ["ACCOUNT_ALREADY_EXISTS", "already exists"],
  ["INVALID_VERIFICATION", "invalid"],
  ["VERIFICATION_EXPIRED", "expired"],
  ["VERIFICATION_NOT_REQUIRED", "does not require"],
  ["ACCOUNT_NOT_FOUND", "No account"],
  ["UNPROCESSABLE_ENTITY", "form values"],
  ["REQUEST_PENDING", "in progress"],
  ["TRANSPORT_ERROR", "could not be confirmed"],
  ["UNKNOWN_SERVER_ERROR", "could not be confirmed"],
])(
  "safe feedback maps %s without forwarding private details",
  (code, expected) => {
    expect(authFeedback(new AuthFailure(400, code))).toContain(expected);
    expect(
      authFeedback(new Error("private request credentials")),
    ).not.toContain("private");
  },
);

test("authenticated verification renders only canonical Zustand name/email as escaped text", () => {
  Object.assign(initial, {
    ...original,
    status: "authenticated",
    accessToken: "private-access-fixture",
    user: {
      id: "00000000-0000-4000-8000-000000000001",
      name: "Canonical <script>profile</script>",
      email: "canonical@example.test",
    },
  });

  const html = render(true);

  expect(html).toContain("Account authenticated");
  expect(html).toContain("Canonical &lt;script&gt;profile&lt;/script&gt;");
  expect(html).toContain("canonical@example.test");
  expect(html).not.toContain("private-access-fixture");
  expect(html).not.toContain("00000000-0000-4000-8000-000000000001");
  expect(html).not.toContain("<script>profile</script>");
  expect(html).not.toContain('name="otp"');
  expect(html).not.toContain('name="password"');
});

test("unvalidated and missing-user snapshots cannot fabricate authenticated profile output", () => {
  for (const status of [
    "restoring",
    "unauthenticated",
    "error",
    "authenticated",
  ] as const) {
    Object.assign(initial, {
      ...original,
      status,
      user: null,
    });

    expect(render(true)).not.toContain("Account authenticated");
  }
});
