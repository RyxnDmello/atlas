import type { AuthState } from "@stores/auth";

export type AuthRouteMode = "entry" | "anonymous" | "protected";
export type AuthRouteView =
  "content" | "loading" | "recovery" | "inconsistent" | "redirect";

export type AuthDestination = "/login" | "/drive";
export type AuthRouteState = Pick<AuthState, "status" | "user" | "logout"> &
  Partial<Pick<AuthState, "error">>;

export interface AuthRouteDecision {
  view: AuthRouteView;
  destination: AuthDestination | null;
}

export const authRoute = (
  mode: AuthRouteMode,
  state: AuthRouteState,
  actionError = false,
): AuthRouteDecision => {
  if (state.status === "authenticated") {
    if (!state.user) {
      return {
        view: "inconsistent",
        destination: null,
      };
    }

    return {
      view: mode === "protected" ? "content" : "redirect",
      destination: mode === "protected" ? null : "/drive",
    };
  }

  if (state.status === "restoring") {
    return {
      view: "loading",
      destination: null,
    };
  }

  if (
    state.status === "error" &&
    !(
      mode === "anonymous" &&
      (actionError ||
        state.error === "credential_action" ||
        state.logout !== "none")
    )
  ) {
    return {
      view: "recovery",
      destination: null,
    };
  }

  return {
    view: mode === "anonymous" ? "content" : "redirect",
    destination: mode === "anonymous" ? null : "/login",
  };
};

export const replaceAuthRoute = (
  mode: AuthRouteMode,
  actionError: boolean,
  pathname: string,
  destination: AuthDestination,
  current: AuthRouteState,
  location: string,
  previous: string | null,
  replace: (destination: AuthDestination) => void,
): string | null => {
  const key = `${pathname}:${destination}`;
  const decision = authRoute(mode, current, actionError);

  if (
    location.replace(/\/$/, "") === pathname.replace(/\/$/, "") &&
    decision.destination === destination &&
    previous !== key
  ) {
    replace(destination);

    return key;
  }

  return previous;
};
