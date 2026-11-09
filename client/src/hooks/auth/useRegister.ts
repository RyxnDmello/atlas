"use client";

import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import http from "@services/http/axios";

import {
  AuthFailure,
  safeAuthError,
  validatedResponse,
} from "@/services/http/validate";

import {
  registrationSchema,
  verificationRequiredSchema,
  type Registration,
} from "@schemas/auth/auth";

import { AUTH_ENDPOINTS } from "@constants/auth";

export default function useRegister() {
  const pending = useRef(false);

  const onRegister = async (input: Registration) => {
    if (pending.current) {
      throw new AuthFailure(0, "REQUEST_PENDING");
    }

    const data = registrationSchema.parse(input);

    pending.current = true;

    try {
      const response = await http.post<unknown>(AUTH_ENDPOINTS.REGISTER, data, {
        isProtected: false,
        withCredentials: false,
        validateStatus: () => true,
      });

      return validatedResponse(response, 201, verificationRequiredSchema);
    } catch (error) {
      throw safeAuthError(error);
    } finally {
      pending.current = false;
    }
  };

  const mutation = useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onRegister,
  });

  return {
    registerError: mutation.error,
    isRegisterLoading: mutation.isPending,
    isRegisterSuccess: mutation.isSuccess,
    register: mutation.mutateAsync,
  };
}
