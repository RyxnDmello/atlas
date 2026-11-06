import "./environment";

import { createAuthStore, initialAuth } from "@stores/auth";

import {
  initializeAuth,
  retryAuth,
  acquireAccess,
  createCoordination,
  onAuthBoundary,
  type Coordination,
  type RecoveryRequests,
  type AuthLease,
  acceptCredentials,
  startAuth,
  finishLogin,
  finishLogout,
  failCredentials,
  currentLease,
  refreshCredentials,
} from "@services/auth/auth";

import type { TokenStorage } from "@services/auth/token";

import type {
  Login,
  Registration,
  Resend,
  Verification,
  AuthenticatedResponse,
  VerificationRequired,
} from "@schemas/auth/auth";

interface AuthApi extends RecoveryRequests {
  register(data: Registration): Promise<VerificationRequired>;
  resend(data: Resend): Promise<VerificationRequired>;
  login(data: Login): Promise<AuthenticatedResponse>;
  verify(data: Verification): Promise<AuthenticatedResponse>;
  logout(): Promise<void>;
}

/** Test seeding bypasses HTTP; production login/verify always use ordered hooks. */
export const seedCredentials = async (
  response: AuthenticatedResponse,
  context: Coordination,
) => {
  context.sessionVersion++;
  context.refresh = undefined;
  context.initialization = Promise.resolve();

  void context.storage.clear();

  context.store.getState().update({
    ...initialAuth,
  });

  await acceptCredentials(response, context.sessionVersion, context);
};

/** Compatibility facade exists only in tests, retaining the old race assertions. */
export const fixtureAccess = (api: AuthApi, storage: TokenStorage) => {
  const context = createCoordination(createAuthStore(), storage);

  return {
    context,
    getSnapshot: context.store.getState,
    initialize: () => initializeAuth(context, api),
    retry: () => retryAuth(context, api),
    acquire: async () => {
      await initializeAuth(context, api);

      return acquireAccess(context);
    },
    current: (lease: AuthLease) => currentLease(lease, context),
    refresh: (lease: AuthLease) =>
      refreshCredentials(lease, context, api.refresh),
    adopt: (response: AuthenticatedResponse) =>
      seedCredentials(response, context),
    login: (data: Login) =>
      establishCredentials(() => api.login(data), context),
    verify: (data: Verification) =>
      establishCredentials(() => api.verify(data), context),
    logout: () => signOut(api.logout, context),
    registerCleanup: (cleanup: () => void) => onAuthBoundary(cleanup, context),
  };
};

export const user = {
  id: "25bca73f-3610-443c-9f74-8c2c2f91a54c",
  name: "Synthetic User",
  email: "fixture@example.test",
};

export const response = {
  access_token: "synthetic.access.fixture",
  user,
};

export const deferred = <T>() => {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;

  const promise = new Promise<T>((yes, no) => {
    resolve = yes;
    reject = no;
  });

  return {
    promise,
    resolve,
    reject,
  };
};

export const fixture = (
  overrides: Partial<AuthApi> = {},
  persistence: Partial<TokenStorage> = {},
) => {
  const calls: string[] = [];
  let saved: string | undefined;
  let signout = false;

  const storage: TokenStorage = {
    load: async () => {
      return saved;
    },

    save: async (token, current) => {
      if (!current()) {
        return false;
      }

      saved = token;

      return true;
    },

    clear: async () => {
      saved = undefined;
    },

    destroy: async () => {
      saved = undefined;

      return true;
    },

    signedOut: () => signout,

    signout: (value) => {
      signout = value;

      return true;
    },

    ...persistence,
  };

  const api: AuthApi = {
    register: async () => {
      calls.push("register");

      return {
        status: "verification_required",
      };
    },

    resend: async () => {
      calls.push("resend");

      return {
        status: "verification_required",
      };
    },

    current: async () => {
      calls.push("current");

      return user;
    },

    login: async () => {
      calls.push("login");

      return response;
    },

    verify: async () => {
      calls.push("verify");

      return response;
    },

    refresh: async () => {
      calls.push("refresh");

      return response;
    },

    logout: async () => {
      calls.push("logout");
    },

    ...overrides,
  };

  return {
    api,
    storage,
    calls,
    session: fixtureAccess(api, storage),
    saved: () => saved,
  };
};

/** Old session assertions use callbacks only in this test fixture. */
const establishCredentials = async (
  request: () => Promise<AuthenticatedResponse>,
  context: Coordination,
) => {
  const operation = startAuth("login", context);

  try {
    await operation.ready;

    return await finishLogin(operation, await request(), context);
  } catch (error) {
    await failCredentials(error, operation.sessionVersion, context);

    throw error;
  } finally {
    operation.release();
  }
};

const signOut = async (request: () => Promise<void>, context: Coordination) => {
  const operation = startAuth("logout", context);
  let confirmed = false;

  try {
    await operation.ready;
    await request();

    confirmed = true;
  } catch {
    confirmed = false;
  } finally {
    operation.release();
  }

  return finishLogout(operation, confirmed, context);
};
