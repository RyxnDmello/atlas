import axios, { CanceledError, type InternalAxiosRequestConfig } from "axios";

import { authAccess, type AuthLease } from "@services/auth/auth";

import {
  waitFor,
  recover,
  resolveUrl,
  requiresAuth,
  invalidAccess,
} from "@/services/http/policy";

import { env } from "@constants/env";

interface AuthConfig extends InternalAxiosRequestConfig {
  atlasLease?: AuthLease;
  atlasRetried?: boolean;
}

declare module "axios" {
  interface AxiosRequestConfig {
    isProtected?: boolean;
  }
}

const client = axios.create({
  baseURL: env.API_BASE_URL,
  withCredentials: false,
});

const checkCancellation = (config: AuthConfig): void => {
  if (config.signal?.aborted) {
    throw new CanceledError();
  }

  config.cancelToken?.throwIfRequested();
};

const waiting = <T>(operation: Promise<T>, config: AuthConfig): Promise<T> => {
  return new Promise((resolve, reject) => {
    const cancel = () => reject(new CanceledError());

    config.cancelToken?.subscribe(cancel);

    waitFor(operation, config.signal as AbortSignal | undefined)
      .then(resolve, reject)
      .finally(() => config.cancelToken?.unsubscribe(cancel));
  });
};

client.interceptors.request.use(async (config: AuthConfig) => {
  const url = resolveUrl(config.url ?? "", config.baseURL ?? env.API_BASE_URL);

  if (requiresAuth(url, config.isProtected)) {
    try {
      checkCancellation(config);

      const lease = await waiting(authAccess.acquire(), config);

      const sameSession =
        !config.atlasLease ||
        config.atlasLease.sessionVersion === lease.sessionVersion;

      if (authAccess.current(lease) && sameSession) {
        config.atlasLease = lease;
        config.auth = undefined;

        config.headers.set("Authorization", `Bearer ${lease.token}`);

        return config;
      } else {
        throw new Error("Session superseded.");
      }
    } catch (error) {
      checkCancellation(config);

      throw error;
    }
  } else {
    if (config.isProtected === false || config.atlasLease) {
      config.headers.delete("Authorization");
      config.auth = undefined;
    }

    delete config.atlasLease;

    return config;
  }
});

client.interceptors.response.use(undefined, async (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    throw error;
  }

  const config: AuthConfig | undefined = error.config;
  const lease = config?.atlasLease;

  const rejectedAccess = invalidAccess(
    error.response?.status ?? 0,
    error.response?.data,
  );

  if (config && lease && !config.atlasRetried && rejectedAccess) {
    try {
      checkCancellation(config);

      const replacement = await waiting(
        recover(authAccess, lease, config.signal as AbortSignal | undefined),
        config,
      );

      const replayable =
        config.method?.toUpperCase() === "GET" &&
        config.data == null &&
        !new URL(resolveUrl(config.url ?? "", config.baseURL)).pathname.match(
          /\/auth(?:\/|$)/,
        );

      if (replacement && replayable && authAccess.current(replacement)) {
        if (config.signal?.aborted) {
          throw new CanceledError();
        } else {
          config.atlasRetried = true;

          config.headers.set("Authorization", `Bearer ${replacement.token}`);

          return client.request(config);
        }
      } else {
        throw error;
      }
    } catch {
      checkCancellation(config);

      throw error;
    }
  } else {
    throw error;
  }
});

export default client;
