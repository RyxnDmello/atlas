"use client";

import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import http from "@services/http/axios";
import { startAuth, finishLogin, failCredentials } from "@services/auth/auth";

import {
  AuthFailure,
  safeAuthError,
  validatedResponse,
} from "@/services/http/validate";

import {
  loginSchema,
  authenticatedSchema,
  type Login,
} from "@schemas/auth/auth";

import { AUTH_ENDPOINTS } from "@constants/auth";

export default function useLogin() {
  const pending = useRef(false);

  const onLogin = async (input: Login) => {
    if (pending.current) {
      throw new AuthFailure(0, "REQUEST_PENDING");
    }

    const data = loginSchema.parse(input);

    pending.current = true;

    const operation = startAuth("login");

    try {
      await operation.ready;

      operation.check();

      const response = await http.post<unknown>(AUTH_ENDPOINTS.LOGIN, data, {
        isProtected: false,
        withCredentials: true,
        validateStatus: () => true,
      });

      const result = validatedResponse(response, 200, authenticatedSchema);

      return await finishLogin(operation, result);
    } catch (error) {
      await failCredentials(error, operation.sessionVersion);
      throw safeAuthError(error);
    } finally {
      operation.release();
      pending.current = false;
    }
  };

  return useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onLogin,
  });
}
