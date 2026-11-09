import { type AuthLease, type AuthAccess } from "@services/auth/auth";

import { authErrorSchema } from "@schemas/auth/auth";

import { env } from "@constants/env";

export const trustedUrl = (
  url: string,
  configured = env.API_BASE_URL,
): boolean => {
  const base = new URL(configured);
  const target = new URL(url);
  const prefix = base.pathname.replace(/\/+$/, "");

  return (
    target.origin === base.origin &&
    !target.username &&
    !target.password &&
    (!prefix || target.pathname.startsWith(`${prefix}/`))
  );
};

export const requiresAuth = (url: string, isProtected?: boolean): boolean => {
  if (isProtected === true && !trustedUrl(url)) {
    throw new Error("Authenticated target is not trusted.");
  }

  return isProtected === true || (isProtected !== false && protectedUrl(url));
};

export const resolveUrl = (path: string, base = env.API_BASE_URL): string => {
  if (/^[a-z][a-z\d+.-]*:/i.test(path) || path.startsWith("//")) {
    return new URL(path, base).href;
  }

  return `${base.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`;
};

export const protectedUrl = (
  url: string,
  configured = env.API_BASE_URL,
): boolean => {
  const base = new URL(configured);
  const target = new URL(url);
  const prefix = base.pathname.replace(/\/+$/, "");

  const trusted =
    target.origin === base.origin && !target.username && !target.password;
  const withinBase = !prefix || target.pathname.startsWith(`${prefix}/`);

  if (trusted && withinBase) {
    const path = target.pathname.slice(prefix.length);

    return (
      path !== "/auth" &&
      !path.startsWith("/auth/") &&
      path !== "/system" &&
      !path.startsWith("/system/") &&
      path !== "/documents/upload"
    );
  } else {
    return false;
  }
};

export const invalidAccess = (status: number, body: unknown): boolean => {
  const parsed = authErrorSchema.safeParse(body);

  return (
    status === 401 &&
    parsed.success &&
    parsed.data.code === "INVALID_ACCESS_TOKEN"
  );
};

export const waitFor = <T>(
  operation: Promise<T>,
  signal?: AbortSignal | null,
): Promise<T> => {
  if (!signal) {
    return operation;
  }

  if (signal.aborted) {
    return Promise.reject(new DOMException("Aborted", "AbortError"));
  } else {
    return new Promise((resolve, reject) => {
      const abort = () => reject(new DOMException("Aborted", "AbortError"));

      signal.addEventListener("abort", abort, {
        once: true,
      });

      operation
        .then(resolve, reject)
        .finally(() => signal.removeEventListener("abort", abort));
    });
  }
};

export const recover = async (
  session: AuthAccess,
  lease: AuthLease,
  signal?: AbortSignal | null,
): Promise<AuthLease | undefined> => {
  await waitFor(session.refresh(lease), signal);

  if (session.current(lease)) {
    const replacement = await waitFor(session.acquire(), signal);

    return replacement.sessionVersion === lease.sessionVersion
      ? replacement
      : undefined;
  } else {
    return undefined;
  }
};
