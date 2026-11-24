import { afterEach, expect, test } from "bun:test";

import "./environment";

import AuthGate from "@components/Auth/AuthGate";
import DrivePanel from "@components/Drive/DrivePanel";
import RegisterPanel from "@components/Auth/RegisterPanel";
import VerifyPanel from "@components/Auth/VerifyPanel";
import LoginPanel from "@components/Auth/LoginPanel";

import {
  authRoute,
  replaceAuthRoute,
  type AuthRouteMode,
  type AuthRouteState,
  type AuthDestination,
} from "@utils/auth/navigation";

import useAuthStore from "@stores/auth";

import { renderAuth } from "./render";

const initial = useAuthStore.getInitialState();

const original = {
  ...initial,
};

const user = {
  id: "00000000-0000-4000-8000-000000000005",
  name: "Canonical <script>profile</script>",
  email: "canonical@example.test",
};

const routes: [string, AuthRouteMode][] = [
  ["/", "entry"],
  ["/register", "anonymous"],
  ["/verify", "anonymous"],
  ["/login", "anonymous"],
  ["/drive", "protected"],
];

afterEach(() => {
  Object.assign(initial, original);
});

for (const [path, mode] of routes) {
  test.each([
    "restoring",
    "authenticated",
    "unauthenticated",
    "error",
  ] as const)(`${path}: %s policy and static visibility`, (status) => {
    const state: AuthRouteState = {
      status,
      user,
      logout: "none",
    };

    const decision = authRoute(mode, state);

    const expected =
      status === "restoring"
        ? "loading"
        : status === "error"
          ? "recovery"
          : status === "authenticated"
            ? mode === "protected"
              ? "content"
              : "redirect"
            : mode === "anonymous"
              ? "content"
              : "redirect";

    const destination =
      status === "authenticated" && mode !== "protected"
        ? "/drive"
        : status === "unauthenticated" && mode !== "anonymous"
          ? "/login"
          : null;

    Object.assign(initial, state);

    const html = renderAuth(
      <AuthGate mode={mode}>
        <span>guarded content</span>
      </AuthGate>,
      path,
    );

    expect(decision).toEqual({
      view: expected,
      destination,
    });
    expect(html.includes("guarded content")).toBe(expected === "content");
    expect(html).not.toContain(user.name);
    expect(html).not.toContain("Signed out");
  });

  test(`${path}: authenticated without canonical user stays private`, () => {
    const state: AuthRouteState = {
      status: "authenticated",
      user: null,
      logout: "none",
    };

    Object.assign(initial, state);

    expect(authRoute(mode, state).view).toBe("inconsistent");
    expect(
      renderAuth(<AuthGate mode={mode}>private</AuthGate>, path),
    ).toContain("Reload session");
    expect(
      renderAuth(<AuthGate mode={mode}>private</AuthGate>, path),
    ).not.toContain(">private<");
  });
}

test.each([RegisterPanel, VerifyPanel, LoginPanel])(
  "authenticated anonymous panel holds navigation without revealing forms/profile",
  (Panel) => {
    Object.assign(initial, {
      status: "authenticated",
      user,
    });

    const html = renderAuth(<Panel />, "/login");

    expect(html).toContain("Redirecting");
    expect(html).not.toContain("<form");
    expect(html).not.toContain("canonical@example.test");
  },
);

test("action errors preserve anonymous correction without weakening protected/entry gates", () => {
  const state: AuthRouteState = {
    status: "error",
    user: null,
    logout: "none",
  };

  Object.assign(initial, state);

  expect(authRoute("anonymous", state, true).view).toBe("content");
  expect(authRoute("anonymous", state, false).view).toBe("recovery");
  expect(authRoute("protected", state, true).view).toBe("recovery");
  expect(authRoute("entry", state, true).destination).toBeNull();
  expect(
    renderAuth(
      <AuthGate mode="anonymous" actionError>
        <input name="correction" />
      </AuthGate>,
      "/login",
    ),
  ).toContain('name="correction"');
});

test.each(["pending", "confirmed", "unconfirmed"] as const)(
  "logout %s cannot expose private identity or offer session recovery",
  (logout) => {
    Object.assign(initial, {
      status: "unauthenticated",
      logout,
      user,
    });

    const privateHtml = renderAuth(<DrivePanel />, "/drive");
    const loginHtml = renderAuth(<LoginPanel />, "/login");

    expect(privateHtml).toContain("Redirecting");
    expect(privateHtml).not.toContain("canonical@example.test");
    expect(loginHtml).not.toContain("Retry session check");
    expect(loginHtml).not.toContain("canonical@example.test");
  },
);

test("terminal refresh failure denies drive; uncertainty offers explicit recovery only", () => {
  Object.assign(initial, {
    status: "unauthenticated",
    user: null,
  });

  expect(renderAuth(<DrivePanel />, "/drive")).toContain("Redirecting");

  Object.assign(initial, {
    status: "error",
  });

  const html = renderAuth(<DrivePanel />, "/drive");

  expect(html).toContain("Retry session check");
  expect(html).not.toContain("Redirecting");
  expect(html).not.toContain("Signed out");
  expect(html).not.toContain("canonical@example.test");
});

test("redirect dispatch rechecks live state/path and suppresses duplicate effects", () => {
  const calls: AuthDestination[] = [];

  const replace = (destination: AuthDestination) => {
    calls.push(destination);
  };

  const authenticated: AuthRouteState = {
    status: "authenticated",
    user,
    logout: "none",
  };

  const signedOut: AuthRouteState = {
    status: "unauthenticated",
    user: null,
    logout: "confirmed",
  };

  const first = replaceAuthRoute(
    "anonymous",
    false,
    "/login",
    "/drive",
    authenticated,
    "/login/",
    null,
    replace,
  );

  expect(calls).toEqual(["/drive"]);
  expect(
    replaceAuthRoute(
      "anonymous",
      false,
      "/login",
      "/drive",
      authenticated,
      "/login",
      first,
      replace,
    ),
  ).toBe(first);
  replaceAuthRoute(
    "anonymous",
    false,
    "/login",
    "/drive",
    signedOut,
    "/login",
    null,
    replace,
  );
  replaceAuthRoute(
    "anonymous",
    false,
    "/login",
    "/drive",
    authenticated,
    "/drive",
    null,
    replace,
  );
  replaceAuthRoute(
    "protected",
    false,
    "/drive",
    "/login",
    authenticated,
    "/drive",
    null,
    replace,
  );

  expect(calls).toHaveLength(1);

  replaceAuthRoute(
    "protected",
    false,
    "/drive",
    "/login",
    signedOut,
    "/drive",
    null,
    replace,
  );

  expect(calls).toEqual(["/drive", "/login"]);
});

for (const [path, Panel] of [
  ["/verify", VerifyPanel],
  ["/register", RegisterPanel],
  ["/login", LoginPanel],
] as const) {
  test(`${path}: credential-action correction survives anonymous route handoff`, () => {
    Object.assign(initial, {
      status: "error",
      error: "credential_action",
      user: null,
      accessToken: null,
      logout: "none",
    });

    const html = renderAuth(<Panel />, path);

    expect(html).toContain("<form");
    expect(html).not.toContain("Retry session check");
    expect(authRoute("protected", initial).view).toBe("recovery");
    expect(authRoute("entry", initial).destination).toBeNull();
  });
}
