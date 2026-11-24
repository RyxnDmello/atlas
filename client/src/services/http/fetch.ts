import { authAccess, type AuthLease } from "@services/auth/auth";

import {
  waitFor,
  recover,
  resolveUrl,
  requiresAuth,
  invalidAccess,
} from "@services/http/policy";

import { env } from "@constants/env";

export interface FetchOptions extends RequestInit {
  isProtected?: boolean;
}

export interface FetchClient {
  get(path: string, options?: FetchOptions): Promise<Response>;
  base(path: string, options?: FetchOptions): Promise<Response>;
  post(path: string, data: unknown, options?: FetchOptions): Promise<Response>;
}

interface AuthenticatedRequest {
  url: string;
  options: RequestInit;
  lease: AuthLease;
}

const recoverResponse = async (
  response: Response,
  request: AuthenticatedRequest,
): Promise<Response> => {
  if (response.status !== 401) {
    return response;
  }

  let body: unknown;

  try {
    body = await response.clone().json();
  } catch {}

  if (!invalidAccess(response.status, body)) {
    return response;
  }

  const { url, options, lease } = request;

  try {
    const replacement = await recover(authAccess, lease, options.signal);

    const replayable =
      (options.method ?? "GET").toUpperCase() === "GET" &&
      options.body == null &&
      !new URL(url).pathname.match(/\/auth(?:\/|$)/);

    if (!replacement || !replayable) {
      return response;
    }

    options.signal?.throwIfAborted();

    if (!authAccess.current(replacement)) {
      return response;
    }

    const headers = new Headers(options.headers);

    headers.set("Authorization", `Bearer ${replacement.token}`);

    return globalThis.fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    if (options.signal?.aborted) {
      throw error;
    }

    return response;
  }
};

const base = async (
  path: string,
  options?: FetchOptions,
): Promise<Response> => {
  const url = resolveUrl(path, env.API_BASE_URL);
  const { isProtected, ...native } = options ?? {};

  const settings: RequestInit = {
    credentials: "omit",
    ...native,
  };

  if (requiresAuth(url, isProtected)) {
    settings.signal?.throwIfAborted();

    const lease = await waitFor(authAccess.acquire(), settings.signal);

    if (authAccess.current(lease)) {
      const headers = new Headers(settings.headers);

      headers.set("Authorization", `Bearer ${lease.token}`);

      const response = await globalThis.fetch(url, {
        ...settings,
        headers,
      });

      return recoverResponse(response, {
        url,
        options: settings,
        lease,
      });
    }

    throw new Error("Session superseded.");
  }

  if (isProtected === false) {
    const headers = new Headers(settings.headers);

    headers.delete("Authorization");

    settings.headers = headers;
  }

  return globalThis.fetch(url, settings);
};

const client: FetchClient = {
  base,

  get: (path, options) => {
    return base(path, {
      ...options,
      method: "GET",
    });
  },

  post: (path, data, options) => {
    const headers = new Headers(options?.headers);

    if (!headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    return base(path, {
      ...options,
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },
};

export default client;
