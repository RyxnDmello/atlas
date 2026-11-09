import useAuthStore, {
  initialAuth,
  type AuthLogoutResultType,
} from "@stores/auth";

import { tokenStorage, type TokenStorage } from "@services/auth/token";

import { isAuthFailure, validatedRequest } from "@/services/http/validate";

import {
  userSchema,
  authenticatedSchema,
  type AuthenticatedUser,
  type AuthenticatedResponse,
} from "@schemas/auth/auth";

import { AUTH_ENDPOINTS } from "@constants/auth";

export type AuthActionType = "login" | "logout";

export interface Coordination {
  store: typeof useAuthStore;
  tokenVersion: number;
  storage: TokenStorage;
  sessionVersion: number;
  refresh?: Promise<void>;
  cookieQueue: Promise<void>;
  initialization?: Promise<void>;
}

export interface AuthLease {
  readonly token: string;
  readonly tokenVersion: number;
  readonly sessionVersion: number;
}

export interface RecoveryRequests {
  refresh(): Promise<AuthenticatedResponse>;
  current(token: string): Promise<AuthenticatedUser>;
}

interface CookieSlot {
  ready: Promise<void>;
  check(): void;
  release(): void;
}

export const createCoordination = (
  store = useAuthStore,
  storage: TokenStorage = tokenStorage,
): Coordination => {
  return {
    store,
    storage,
    tokenVersion: 0,
    sessionVersion: 0,
    cookieQueue: Promise.resolve(),
  };
};

export const coordination = createCoordination();

const cookieOperation = <T>(
  context: Coordination,
  sessionVersion: number,
  operation: () => Promise<T>,
): Promise<T> => {
  const result = context.cookieQueue.then(() => {
    if (sessionVersion !== context.sessionVersion) {
      throw new Error("Session superseded.");
    } else {
      return operation();
    }
  });

  context.cookieQueue = result.then(
    () => undefined,
    () => undefined,
  );

  return result;
};

const reserveCookie = (
  sessionVersion: number,
  context: Coordination,
): CookieSlot => {
  const previous = context.cookieQueue;
  let release!: () => void;

  context.cookieQueue = new Promise<void>((resolve) => {
    release = resolve;
  });

  const check = () => {
    if (sessionVersion !== context.sessionVersion) {
      throw new Error("Session superseded.");
    }
  };

  const ready = previous.then(check);

  return {
    ready,
    check,
    release,
  };
};

export interface AuthOperation extends CookieSlot {
  persisted: boolean;
  sessionVersion: number;
  clearing: Promise<boolean>;
}

export const startAuth = (
  action: AuthActionType,
  context = coordination,
): AuthOperation => {
  const sessionVersion = ++context.sessionVersion;

  context.refresh = undefined;
  context.initialization = Promise.resolve();

  const persisted = action === "logout" ? context.storage.signout(true) : true;

  const clearing =
    action === "logout"
      ? context.storage.destroy()
      : context.storage.clear().then(() => true);

  context.store.getState().update({
    ...initialAuth,
    signoutPersisted: persisted,
    logout: action === "logout" ? "pending" : "none",
    status: action === "logout" ? "unauthenticated" : "restoring",
  });

  return {
    ...reserveCookie(sessionVersion, context),
    clearing,
    persisted,
    sessionVersion,
  };
};

export const finishLogin = async (
  operation: AuthOperation,
  response: AuthenticatedResponse,
  context = coordination,
) => {
  if (operation.sessionVersion !== context.sessionVersion) {
    throw new Error("Session superseded.");
  }

  context.store.getState().update({
    signoutPersisted: context.storage.signout(false),
  });

  await acceptCredentials(response, operation.sessionVersion, context);

  if (operation.sessionVersion === context.sessionVersion) {
    return response.user;
  } else {
    throw new Error("Session superseded.");
  }
};

export const finishLogout = async (
  operation: AuthOperation,
  confirmed: boolean,
  context = coordination,
): Promise<AuthLogoutResultType> => {
  const removed = await operation.clearing;
  const outcome = confirmed ? "confirmed" : "unconfirmed";

  if (operation.sessionVersion === context.sessionVersion) {
    context.store.getState().update({
      logout: outcome,
      persistence: removed ? "available" : "unavailable",
      signoutPersisted: confirmed
        ? context.storage.signout(false)
        : operation.persisted,
    });
  }

  return outcome;
};

export const onAuthBoundary = (
  cleanup: () => void,
  context: Coordination = coordination,
) => {
  let sessionVersion = context.sessionVersion;

  return context.store.subscribe(() => {
    if (sessionVersion !== context.sessionVersion) {
      sessionVersion = context.sessionVersion;

      try {
        cleanup();
      } catch {}
    }
  });
};

export const acceptCredentials = async (
  response: AuthenticatedResponse,
  sessionVersion: number,
  context: Coordination,
  persist = true,
) => {
  if (sessionVersion !== context.sessionVersion) {
    return;
  }

  const version = ++context.tokenVersion;

  context.store.getState().update({
    status: "authenticated",
    accessToken: response.access_token,
    user: Object.freeze({
      ...response.user,
    }),
    error: null,
    persistence: persist ? "pending" : "available",
    logout: "none",
  });

  if (persist) {
    const available = await context.storage.save(
      response.access_token,
      () =>
        sessionVersion === context.sessionVersion &&
        version === context.tokenVersion,
    );

    if (
      sessionVersion === context.sessionVersion &&
      version === context.tokenVersion
    ) {
      context.store.getState().update({
        persistence: available ? "available" : "unavailable",
      });
    }
  }
};

export const failCredentials = async (
  error: unknown,
  sessionVersion: number,
  context: Coordination = coordination,
  inconsistent = false,
  refreshFailure = false,
  actionFailure = false,
) => {
  if (sessionVersion !== context.sessionVersion) {
    return;
  }

  if (refreshFailure && isAuthFailure(error, "INVALID_REFRESH_TOKEN")) {
    context.sessionVersion++;
    context.refresh = undefined;

    const clearing = context.storage.clear();

    context.store.getState().update({
      status: "unauthenticated",
      accessToken: null,
      user: null,
      error: null,
      persistence: "unavailable",
    });

    await clearing;
  } else {
    context.store.getState().update({
      status: "error",
      accessToken: null,
      user: null,
      error: inconsistent
        ? "inconsistent_session"
        : actionFailure
          ? "credential_action"
          : "session_uncertain",
    });
  }
};

const validateCandidate = (token: string) => {
  return validatedRequest({
    url: AUTH_ENDPOINTS.AUTH,
    method: "GET",
    status: 200,
    schema: userSchema,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const restore = async (context: Coordination, request: RecoveryRequests) => {
  const sessionVersion = context.sessionVersion;

  if (context.storage.signedOut()) {
    context.store.getState().update({
      status: "unauthenticated",
      user: null,
      accessToken: null,
      persistence: "unavailable",
      logout: "unconfirmed",
    });
  } else {
    try {
      let token = await context.storage.load(
        () => sessionVersion === context.sessionVersion,
      );

      if (token && sessionVersion === context.sessionVersion) {
        try {
          const user = await request.current(token);

          await acceptCredentials(
            {
              access_token: token,
              user,
            },
            sessionVersion,
            context,
            false,
          );
        } catch (error) {
          if (sessionVersion !== context.sessionVersion) {
            token = undefined;
          } else if (isAuthFailure(error, "INVALID_ACCESS_TOKEN")) {
            await context.storage.clear();

            token = undefined;
          } else {
            throw error;
          }
        }
      }

      if (!token && sessionVersion === context.sessionVersion) {
        let response: AuthenticatedResponse | undefined;

        try {
          response = await cookieOperation(
            context,
            sessionVersion,
            request.refresh,
          );
        } catch (error) {
          await failCredentials(error, sessionVersion, context, false, true);
        }

        if (response && sessionVersion === context.sessionVersion) {
          try {
            const user = await request.current(response.access_token);

            if (user.id === response.user.id) {
              await acceptCredentials(
                {
                  ...response,
                  user,
                },
                sessionVersion,
                context,
              );
            } else {
              await failCredentials(new Error(), sessionVersion, context, true);
            }
          } catch (error) {
            await failCredentials(
              error,
              sessionVersion,
              context,
              isAuthFailure(error, "INVALID_ACCESS_TOKEN"),
            );
          }
        }
      }
    } catch (error) {
      await failCredentials(error, sessionVersion, context);
    }
  }
};

export const initializeAuth = (
  context = coordination,
  request = requests,
): Promise<void> => {
  if (context.initialization) {
    return context.initialization;
  }

  context.initialization = restore(context, request);

  return context.initialization;
};

export const retryAuth = (context = coordination, request = requests) => {
  if (
    context.store.getState().status !== "error" &&
    !context.storage.signedOut()
  ) {
    return initializeAuth(context, request);
  }

  context.sessionVersion++;
  context.refresh = undefined;
  context.initialization = undefined;

  context.storage.signout(false);
  context.store.getState().update({
    ...initialAuth,
  });

  return initializeAuth(context, request);
};

const requestRefresh = () => {
  return validatedRequest({
    url: AUTH_ENDPOINTS.REFRESH,
    method: "POST",
    status: 200,
    schema: authenticatedSchema,
    withCredentials: true,
  });
};

export const currentLease = (
  lease: AuthLease,
  context = coordination,
): boolean => {
  const state = context.store.getState();

  return (
    lease.sessionVersion === context.sessionVersion &&
    state.status === "authenticated" &&
    !!state.accessToken
  );
};

export const refreshCredentials = async (
  lease: AuthLease,
  context: Coordination = coordination,
  request: RecoveryRequests["refresh"] = requestRefresh,
) => {
  if (
    !currentLease(lease, context) ||
    lease.tokenVersion !== context.tokenVersion
  ) {
    return;
  }

  if (context.refresh) {
    await context.refresh;
  } else {
    const sessionVersion = context.sessionVersion;

    const result = (async () => {
      try {
        const response = await cookieOperation(
          context,
          sessionVersion,
          request,
        );

        if (
          sessionVersion === context.sessionVersion &&
          response.user.id !== context.store.getState().user?.id
        ) {
          await failCredentials(new Error(), sessionVersion, context, true);
        } else {
          await acceptCredentials(response, sessionVersion, context);
        }
      } catch (error) {
        await failCredentials(error, sessionVersion, context, false, true);
      }
    })();

    context.refresh = result;

    try {
      await result;
    } finally {
      if (context.refresh === result) {
        context.refresh = undefined;
      }
    }
  }
};

export interface AuthAccess {
  acquire(): Promise<AuthLease>;
  current(lease: AuthLease): boolean;
  refresh(lease: AuthLease): Promise<void>;
}

export const acquireAccess = async (
  context = coordination,
): Promise<AuthLease> => {
  await initializeAuth(context);

  const state = context.store.getState();

  if (state.status === "authenticated" && state.accessToken) {
    return {
      token: state.accessToken,
      sessionVersion: context.sessionVersion,
      tokenVersion: context.tokenVersion,
    };
  } else {
    throw new Error("Authenticated session unavailable.");
  }
};

const requests: RecoveryRequests = {
  current: validateCandidate,
  refresh: requestRefresh,
};

export const authAccess: AuthAccess = {
  acquire: acquireAccess,
  current: currentLease,
  refresh: refreshCredentials,
};
