import axios from "axios";
import type { z } from "zod";

import { authErrorSchema } from "@schemas/auth/auth";

import { env } from "@constants/env";

type HttpMethodType = "GET" | "POST";

interface ValidatedRequest<T> {
  url: string;
  status: number;
  method: HttpMethodType;
  schema: z.ZodType<T>;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

interface HttpResponse {
  data: unknown;
  status: number;
}

export class AuthFailure extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
  ) {
    super("Authentication request failed.");
    this.name = "AuthFailure";
  }
}

export const isAuthFailure = (error: unknown, code: string): boolean => {
  return (
    error instanceof AuthFailure && error.status === 401 && error.code === code
  );
};

export const safeAuthError = (error: unknown): AuthFailure => {
  if (error instanceof AuthFailure) {
    return error;
  }

  if (axios.isAxiosError<unknown>(error) && error.response) {
    const parsed = authErrorSchema.safeParse(error.response.data);

    return new AuthFailure(
      error.response.status,
      parsed.success ? parsed.data.code : "INVALID_RESPONSE",
    );
  }

  return new AuthFailure(0, "TRANSPORT_ERROR");
};

export const validatedResponse = <T>(
  response: HttpResponse,
  status: number,
  schema: z.ZodType<T>,
): T => {
  if (response.status === status) {
    const parsed = schema.safeParse(response.data);

    if (parsed.success) {
      return parsed.data;
    }

    throw new AuthFailure(status, "INVALID_RESPONSE");
  }

  const parsed = authErrorSchema.safeParse(response.data);

  throw new AuthFailure(
    response.status,
    parsed.success ? parsed.data.code : "INVALID_RESPONSE",
  );
};

export const validatedRequest = async <T>(
  options: ValidatedRequest<T>,
): Promise<T> => {
  try {
    const response = await globalThis.fetch(
      `${env.API_BASE_URL.replace(/\/+$/, "")}${options.url}`,
      {
        method: options.method,
        headers: options.headers,
        credentials: options.withCredentials ? "include" : "omit",
        redirect: "error",
      },
    );

    const data: unknown = await response.json().catch(() => undefined);

    return validatedResponse(
      {
        data,
        status: response.status,
      },
      options.status,
      options.schema,
    );
  } catch (error) {
    throw safeAuthError(error);
  }
};
