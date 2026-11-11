import { afterEach, expect, test } from "bun:test";

import "./environment";

import DrivePanel from "@components/Drive/DrivePanel";
import LoginPanel from "@components/Auth/LoginPanel";

import { AuthFailure } from "@services/http/validate";

import { loginSchema } from "@schemas/auth/auth";

import { authFeedback } from "@utils/auth/feedback";

import useAuthStore from "@stores/auth";

import { renderAuth } from "./render";

const initial = useAuthStore.getInitialState();
const original = {
  ...initial,
};

const render = (drive = false) => {
  return renderAuth(
    drive ? <DrivePanel /> : <LoginPanel />,
    drive ? "/drive" : "/login",
  );
};

afterEach(() => {
  Object.assign(initial, original);
});

test("terminal unauthenticated login has labeled masked fields and a normal registration link", () => {
  Object.assign(initial, {
    status: "unauthenticated",
  });

  const html = render();

  expect(html).toContain('for="email"');
  expect(html).toContain('for="password"');
  expect(html).toContain('type="password"');
  expect(html).toContain('autoComplete="current-password"');
  expect(html).toContain('href="/register"');
  expect(html).not.toContain("Account authenticated");
  expect(html).not.toContain("/drive");
});

test("login schema normalizes email and preserves password exactly", () => {
  expect(
    loginSchema.parse({
      email: "USER@example.test",
      password: " synthetic-password ",
    }),
  ).toEqual({
    email: "user@example.test",
    password: " synthetic-password ",
  });

  for (const input of [
    {
      email: "bad",
      password: "synthetic-password",
    },
    {
      email: "user@example.test",
      password: "short",
    },
    {
      email: "user@example.test",
      password: "x".repeat(129),
    },
  ]) {
    expect(loginSchema.safeParse(input).success).toBe(false);
  }
});

test.each([
  "INVALID_CREDENTIALS",
  "VERIFICATION_REQUIRED",
  "UNPROCESSABLE_ENTITY",
  "INVALID_RESPONSE",
  "TRANSPORT_ERROR",
  "UNKNOWN_ERROR",
])("login feedback safely classifies %s", (code) => {
  const text = authFeedback(new AuthFailure(400, code));

  expect(text).not.toContain("ACCOUNT_NOT_FOUND");
  expect(text).not.toContain("400");
  expect(text).toContain(
    code === "INVALID_CREDENTIALS"
      ? "email or password is invalid"
      : code === "VERIFICATION_REQUIRED"
        ? "Verify your account"
        : code === "UNPROCESSABLE_ENTITY"
          ? "form values"
          : "could not be confirmed",
  );
  expect(authFeedback(new Error("private detail"))).not.toContain(
    "private detail",
  );
});

test.each(["pending", "available", "unavailable"] as const)(
  "authenticated and restored snapshots show only canonical profile with %s persistence",
  (persistence) => {
    Object.assign(initial, {
      status: "authenticated",
      persistence,
      accessToken: "private-token-fixture",
      user: {
        id: "00000000-0000-4000-8000-000000000001",
        name: "Canonical <script>name</script>",
        email: "canonical@example.test",
      },
    });

    const html = render(true);

    expect(html).toContain("Canonical &lt;script&gt;name&lt;/script&gt;");
    expect(html).toContain("canonical@example.test");
    expect(html).toContain("Logout");
    expect(html).not.toContain('name="password"');
    expect(html).not.toContain("private-token-fixture");
    expect(html).not.toContain("00000000-0000-4000-8000-000000000001");
    expect(html.includes("Session persistence is unavailable")).toBe(
      persistence === "unavailable",
    );
  },
);

test.each(["restoring", "error", "authenticated"] as const)(
  "%s without a validated user never fabricates profile or logged-out form",
  (status) => {
    Object.assign(initial, {
      status,
      user: null,
      error: status === "error" ? "session_uncertain" : null,
    });

    const html = render();

    expect(html).not.toContain('name="password"');
    expect(html).not.toContain("Account authenticated");
    expect(html).toContain(
      status === "restoring"
        ? "Checking session"
        : status === "error"
          ? "Retry session check"
          : "profile is unavailable",
    );
  },
);

test.each(["pending", "confirmed", "unconfirmed"] as const)(
  "logout %s remains visible after canonical identity is cleared",
  (logout) => {
    Object.assign(initial, {
      status: "unauthenticated",
      logout,
      user: null,
    });

    const html = render();

    expect(html).not.toContain("Account authenticated");
    expect(html).toContain(
      logout === "pending"
        ? "waiting for server confirmation"
        : logout === "confirmed"
          ? "Server logout confirmed"
          : "Server logout could not be confirmed",
    );
    expect(html.includes('name="password"')).toBe(logout !== "pending");
    expect(html).not.toContain("Retry session check");
  },
);

test("unconfirmed signout exposes storage and marker failures separately", () => {
  Object.assign(initial, {
    status: "unauthenticated",
    logout: "unconfirmed",
    persistence: "unavailable",
    signoutPersisted: false,
  });

  const html = render();

  expect(html).toContain("Signed out locally");
  expect(html).toContain("storage cleanup could not be confirmed");
  expect(html).toContain("Sign-out intent could not be saved");
  expect(html).not.toContain("Server logout confirmed.");
});
